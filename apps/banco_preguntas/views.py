import io
from decimal import Decimal
from django.db import transaction
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
import openpyxl

from .models import Categoria, Pregunta, OpcionRespuesta, Importacion
from .serializers import CategoriaSerializer, PreguntaDetalleSerializer, ImportacionSerializer
from authentication.permissions import require_permission


class CategoriaViewSet(viewsets.ModelViewSet):
    """CRUD de Categorías / Competencias de la prueba Saber TyT."""
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, require_permission('preguntas.gestionar')]


class PreguntaViewSet(viewsets.ModelViewSet):
    """
    CRUD completo del Banco Central de Preguntas (Sec 2.3).
    Permite registrar, consultar, editar, filtrar y desactivar reactivos.
    """
    queryset = Pregunta.objects.all().select_related('categoria').prefetch_related('opciones').order_by('-id')
    serializer_class = PreguntaDetalleSerializer
    permission_classes = [IsAuthenticated, require_permission('preguntas.gestionar')]

    def get_queryset(self):
        qs = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        tipo = self.request.query_params.get('tipo')
        search = self.request.query_params.get('search')
        activo = self.request.query_params.get('activo')

        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if search:
            qs = qs.filter(enunciado__icontains=search)
        if activo is not None:
            qs = qs.filter(activo=(activo.lower() in ['true', '1']))
        return qs

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        pregunta = self.get_object()
        pregunta.activo = not pregunta.activo
        pregunta.save()
        return Response({
            'detail': f"Pregunta {'activada' if pregunta.activo else 'desactivada'} correctamente.",
            'activo': pregunta.activo
        })


class ImportarExcelView(APIView):
    """
    Procesamiento e importación masiva desde Excel (.xlsx) / CSV (Sec 2.3 y Regla R10).
    Valida campos obligatorios, tipos, opciones, respuesta correcta, puntaje y duplicados.
    Informa el número de fila exacto de cada error y no guarda registros inválidos.
    Opcionalmente asocia las preguntas válidas a un cuestionario de destino.
    """
    permission_classes = [IsAuthenticated, require_permission('preguntas.importar')]

    def post(self, request):
        file_obj = request.FILES.get('archivo')
        # También soporta recibir JSON pre-parseado desde el frontend si fue validado previamente
        json_rows = request.data.get('filas', None)
        cuestionario_id = request.data.get('cuestionario_id', None)

        rows_data = []
        archivo_nombre = "datos_importacion.json"

        if file_obj:
            archivo_nombre = file_obj.name
            try:
                wb = openpyxl.load_workbook(file_obj, data_only=True)
                sheet = wb.active
                headers = []
                for idx, cell in enumerate(sheet[1]):
                    headers.append(str(cell.value or '').strip().lower())

                for row_idx in range(2, sheet.max_row + 1):
                    row_vals = [sheet.cell(row=row_idx, column=col_idx).value for col_idx in range(1, len(headers) + 1)]
                    if all(v is None or str(v).strip() == '' for v in row_vals):
                        continue  # Fila vacía
                    row_dict = dict(zip(headers, row_vals))
                    row_dict['_excel_row'] = row_idx
                    rows_data.append(row_dict)
            except Exception as e:
                return Response(
                    {'detail': f'Error al leer el archivo Excel: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif json_rows and isinstance(json_rows, list):
            archivo_nombre = request.data.get('archivo_nombre', 'importacion_web.xlsx')
            for idx, item in enumerate(json_rows):
                item['_excel_row'] = item.get('rowNum', idx + 2)
                rows_data.append(item)
        else:
            return Response(
                {'detail': 'Se requiere un archivo Excel (.xlsx) en el campo "archivo" o un listado en "filas".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not rows_data:
            return Response(
                {'detail': 'El archivo o lote no contiene filas de datos para procesar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validación fila por fila (Reglas R05, R06, R10)
        valid_items = []
        duplicate_items = []
        error_items = []
        seen_enunciados_batch = set()

        # Cache de categorías existentes para no hacer consultas repetitivas
        categorias_cache = {c.nombre.lower().strip(): c for c in Categoria.objects.all()}

        for row in rows_data:
            row_num = row.get('_excel_row', 0)
            categoria_raw = str(row.get('categoria', '') or '').strip()
            tipo_raw = str(row.get('tipo', '') or '').strip().upper()
            texto_base_raw = str(row.get('texto_base', '') or '').strip()
            pregunta_raw = str(row.get('pregunta', '') or '').strip()
            opc_a = str(row.get('opcion_a', '') or '').strip()
            opc_b = str(row.get('opcion_b', '') or '').strip()
            opc_c = str(row.get('opcion_c', '') or '').strip()
            opc_d = str(row.get('opcion_d', '') or '').strip()
            resp_corr = str(row.get('respuesta_correcta', '') or '').strip().upper()
            puntaje_raw = row.get('puntaje', '2.50')
            retro_raw = str(row.get('retroalimentacion', '') or '').strip()

            # 1. Enunciado obligatorio
            if not pregunta_raw:
                error_items.append({
                    'fila': row_num,
                    'error': "El campo 'pregunta' (enunciado) es obligatorio y se encuentra vacío."
                })
                continue

            # 2. Tipo de pregunta
            if tipo_raw not in ['MULTIPLE', 'VERDADERO_FALSO']:
                error_items.append({
                    'fila': row_num,
                    'error': f"Tipo de pregunta inválido '{tipo_raw}'. Debe ser MULTIPLE o VERDADERO_FALSO."
                })
                continue

            # 3. Categoría obligatoria
            if not categoria_raw:
                error_items.append({
                    'fila': row_num,
                    'error': "El campo 'categoria' es obligatorio."
                })
                continue

            # 4. Validar opciones y respuesta correcta
            if tipo_raw == 'MULTIPLE':
                if not opc_a or not opc_b or not opc_c or not opc_d:
                    error_items.append({
                        'fila': row_num,
                        'error': "Para selección múltiple se requieren las 4 opciones (opcion_a, opcion_b, opcion_c, opcion_d)."
                    })
                    continue
                if resp_corr not in ['A', 'B', 'C', 'D']:
                    error_items.append({
                        'fila': row_num,
                        'error': f"Respuesta correcta inválida '{resp_corr}'. Para selección múltiple debe ser A, B, C o D (Regla R05)."
                    })
                    continue
            else:  # VERDADERO_FALSO
                if not opc_a or not opc_b:
                    # Rellenar con opciones predeterminadas si están vacías
                    opc_a = opc_a or "Verdadero"
                    opc_b = opc_b or "Falso"
                if resp_corr in ['VERDADERO', 'VERDADERA', 'V', 'TRUE']:
                    resp_corr = 'V'
                elif resp_corr in ['FALSO', 'FALSA', 'F', 'FALSE']:
                    resp_corr = 'F'
                else:
                    error_items.append({
                        'fila': row_num,
                        'error': f"Respuesta correcta inválida '{resp_corr}'. Para Verdadero o Falso debe ser V o F (Regla R06)."
                    })
                    continue

            # 5. Puntaje numérico mayor que cero (R02)
            try:
                puntaje_dec = Decimal(str(puntaje_raw).replace(',', '.'))
                if puntaje_dec <= Decimal('0.00'):
                    raise ValueError()
            except Exception:
                error_items.append({
                    'fila': row_num,
                    'error': f"Puntaje inválido '{puntaje_raw}'. Debe ser un número estrictamente mayor que cero (Regla R02)."
                })
                continue

            # 6. Detección de duplicados
            pregunta_clean = pregunta_raw.lower()
            if pregunta_clean in seen_enunciados_batch:
                duplicate_items.append({
                    'fila': row_num,
                    'motivo': "Ya existe una pregunta idéntica en este mismo archivo."
                })
                continue
            if Pregunta.objects.filter(enunciado__iexact=pregunta_raw).exists():
                duplicate_items.append({
                    'fila': row_num,
                    'motivo': "Ya existe una pregunta idéntica registrada previamente en el banco."
                })
                continue

            seen_enunciados_batch.add(pregunta_clean)
            valid_items.append({
                'fila': row_num,
                'categoria': categoria_raw,
                'tipo': tipo_raw,
                'texto_base': texto_base_raw,
                'enunciado': pregunta_raw,
                'opcion_a': opc_a,
                'opcion_b': opc_b,
                'opcion_c': opc_c,
                'opcion_d': opc_d,
                'respuesta_correcta': resp_corr,
                'puntaje': puntaje_dec,
                'retroalimentacion': retro_raw
            })

        # Guardado transaccional de las preguntas válidas
        preguntas_creadas = []
        with transaction.atomic():
            for item in valid_items:
                cat_name = item['categoria']
                cat_key = cat_name.lower().strip()
                if cat_key in categorias_cache:
                    categoria_obj = categorias_cache[cat_key]
                else:
                    categoria_obj = Categoria.objects.create(nombre=cat_name)
                    categorias_cache[cat_key] = categoria_obj

                pregunta = Pregunta.objects.create(
                    categoria=categoria_obj,
                    tipo=item['tipo'],
                    texto_base=item['texto_base'] or None,
                    enunciado=item['enunciado'],
                    retroalimentacion=item['retroalimentacion'],
                    puntaje=item['puntaje'],
                    activo=True
                )

                # Opciones
                if item['tipo'] == 'MULTIPLE':
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='A', texto=item['opcion_a'], es_correcta=(item['respuesta_correcta'] == 'A'), orden=1)
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='B', texto=item['opcion_b'], es_correcta=(item['respuesta_correcta'] == 'B'), orden=2)
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='C', texto=item['opcion_c'], es_correcta=(item['respuesta_correcta'] == 'C'), orden=3)
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='D', texto=item['opcion_d'], es_correcta=(item['respuesta_correcta'] == 'D'), orden=4)
                else:
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='V', texto=item['opcion_a'], es_correcta=(item['respuesta_correcta'] == 'V'), orden=1)
                    OpcionRespuesta.objects.create(pregunta=pregunta, letra='F', texto=item['opcion_b'], es_correcta=(item['respuesta_correcta'] == 'F'), orden=2)

                preguntas_creadas.append(pregunta)

            # Asociación opcional al cuestionario
            if cuestionario_id and cuestionario_id not in ['none', None, '']:
                try:
                    from cuestionarios.models import Cuestionario, CuestionarioPregunta
                    cuestionario = Cuestionario.objects.get(id=int(cuestionario_id))
                    orden_actual = cuestionario.cuestionario_preguntas.count() + 1
                    for p in preguntas_creadas:
                        CuestionarioPregunta.objects.get_or_create(
                            cuestionario=cuestionario,
                            pregunta=p,
                            defaults={'puntaje': p.puntaje, 'orden': orden_actual}
                        )
                        orden_actual += 1
                except Exception:
                    pass

            # Auditoría en tabla importaciones
            Importacion.objects.create(
                archivo_nombre=archivo_nombre,
                total_filas=len(rows_data),
                filas_validas=len(valid_items),
                filas_duplicadas=len(duplicate_items),
                filas_error=len(error_items),
                detalles_errores=error_items,
                usuario=request.user if request.user.is_authenticated else None
            )

        return Response({
            'detail': f"Procesamiento completado. Válidas importadas: {len(valid_items)}, Duplicadas: {len(duplicate_items)}, Errores: {len(error_items)}.",
            'resumen': {
                'total_filas': len(rows_data),
                'validas': len(valid_items),
                'duplicadas': len(duplicate_items),
                'errores': len(error_items)
            },
            'errores_detalle': error_items,
            'duplicadas_detalle': duplicate_items
        }, status=status.HTTP_200_OK if len(valid_items) > 0 else status.HTTP_400_BAD_REQUEST)


class DescargarPlantillaExcelView(APIView):
    """Genera y sirve para descarga la plantilla oficial de preguntas en formato Excel (.xlsx)."""
    permission_classes = [AllowAny]

    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Plantilla_Saber_TyT"

        headers = [
            "categoria", "tipo", "texto_base", "pregunta",
            "opcion_a", "opcion_b", "opcion_c", "opcion_d",
            "respuesta_correcta", "retroalimentacion", "puntaje"
        ]
        ws.append(headers)

        # Fila de ejemplo 1: Selección Múltiple
        ws.append([
            "Razonamiento Cuantitativo",
            "MULTIPLE",
            "En una empresa de software se requiere determinar el costo de producción para el despliegue en la nube.",
            "¿Si un servidor en la nube cuesta $100 al mes, cuánto se pagará en 6 meses con un 10% de descuento?",
            "$500", "$540", "$580", "$600",
            "B",
            "Costo sin descuento = 6 x 100 = 600. Descuento = 60. Total = $540.",
            2.50
        ])

        # Fila de ejemplo 2: Verdadero o Falso
        ws.append([
            "Lectura Crítica",
            "VERDADERO_FALSO",
            "",
            "La tesis de un texto argumentativo representa la postura o punto de vista que defiende el autor.",
            "Verdadero", "Falso", "", "",
            "V",
            "Correcto. La tesis es la proposición central que se defiende mediante argumentos.",
            2.50
        ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="plantilla_oficial_preguntas_saber_tyt.xlsx"'
        return response
