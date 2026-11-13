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
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

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

    @staticmethod
    def normalizar_columna(col_name):
        c = str(col_name or '').strip().lower().replace(' ', '_').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        if c in ['enunciado', 'pregunta', 'reactivo', 'texto_pregunta']:
            return 'pregunta'
        if c in ['tematica', 'eje', 'categoria', 'competencia', 'eje_tematico']:
            return 'categoria'
        if c in ['justificacion', 'retroalimentacion', 'explicacion', 'feedback']:
            return 'retroalimentacion'
        if c in ['dificultad', 'nivel_dificultad', 'nivel']:
            return 'dificultad'
        if c in ['respuesta_correcta', 'correcta', 'clave', 'opcion_correcta']:
            return 'respuesta_correcta'
        if c in ['opcion_a', 'opciona', 'a']:
            return 'opcion_a'
        if c in ['opcion_b', 'opcionb', 'b']:
            return 'opcion_b'
        if c in ['opcion_c', 'opcionc', 'c']:
            return 'opcion_c'
        if c in ['opcion_d', 'opciond', 'd']:
            return 'opcion_d'
        if c in ['puntaje', 'puntos', 'peso']:
            return 'puntaje'
        if c in ['texto_base', 'contexto', 'lectura']:
            return 'texto_base'
        return c

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
                
                # Selección inteligente de hoja (buscar hoja de preguntas o la que contenga encabezados válidos)
                sheet = None
                nombres_candidatos = ['plantilla_preguntas', 'preguntas', 'plantilla_saber_tyt', 'datos']
                for name in wb.sheetnames:
                    if name.lower().strip() in nombres_candidatos:
                        sheet = wb[name]
                        break

                if sheet is None:
                    # Inspeccionar hoja por hoja
                    for s in wb.worksheets:
                        first_row = [self.normalizar_columna(cell.value) for cell in s[1]]
                        if any(h in first_row for h in ['pregunta', 'categoria', 'opcion_a']):
                            sheet = s
                            break

                if sheet is None:
                    sheet = wb.active

                headers = []
                for idx, cell in enumerate(sheet[1]):
                    headers.append(self.normalizar_columna(cell.value))

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
                norm_item = {}
                for k, v in item.items():
                    norm_item[self.normalizar_columna(k)] = v
                norm_item['_excel_row'] = item.get('rowNum', idx + 2)
                rows_data.append(norm_item)
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
            dificultad_raw = str(row.get('dificultad', 'MEDIA') or 'MEDIA').strip().upper()
            opc_a = str(row.get('opcion_a', '') or '').strip()
            opc_b = str(row.get('opcion_b', '') or '').strip()
            opc_c = str(row.get('opcion_c', '') or '').strip()
            opc_d = str(row.get('opcion_d', '') or '').strip()
            resp_corr = str(row.get('respuesta_correcta', '') or '').strip().upper()
            puntaje_raw = row.get('puntaje', '2.50')
            retro_raw = str(row.get('retroalimentacion', '') or '').strip()

            if dificultad_raw not in ['BAJA', 'MEDIA', 'ALTA']:
                dificultad_raw = 'MEDIA'

            # 1. Enunciado obligatorio
            if not pregunta_raw:
                error_items.append({
                    'fila': row_num,
                    'error': "El campo 'enunciado' (pregunta) es obligatorio y se encuentra vacío."
                })
                continue

            # 2. Tipo de pregunta
            if tipo_raw not in ['MULTIPLE', 'VERDADERO_FALSO']:
                error_items.append({
                    'fila': row_num,
                    'error': f"Tipo de pregunta inválido '{tipo_raw}'. Debe ser MULTIPLE o VERDADERO_FALSO."
                })
                continue

            # 3. Categoría / Temática obligatoria
            if not categoria_raw:
                error_items.append({
                    'fila': row_num,
                    'error': "El campo 'temática / categoría' es obligatorio."
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
                    'motivo': "Ya existe una pregunta con este mismo enunciado en el archivo actual."
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
                'dificultad': dificultad_raw,
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
        cuestionario_asociado_nombre = None
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
                    nivel_dificultad=item['dificultad'],
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

            # Asociación al cuestionario destino si fue especificado
            if cuestionario_id and str(cuestionario_id).strip() not in ['none', 'null', '']:
                try:
                    from cuestionarios.models import Cuestionario, CuestionarioPregunta
                    cuestionario = Cuestionario.objects.get(id=int(cuestionario_id))
                    cuestionario_asociado_nombre = cuestionario.nombre
                    orden_actual = cuestionario.cuestionario_preguntas.count() + 1
                    for p in preguntas_creadas:
                        CuestionarioPregunta.objects.get_or_create(
                            cuestionario=cuestionario,
                            pregunta=p,
                            defaults={'puntaje': p.puntaje, 'orden': orden_actual}
                        )
                        orden_actual += 1
                except Exception as ex:
                    print(f"Error asociando al cuestionario: {ex}")

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
                'errores': len(error_items),
                'cuestionario_asociado': cuestionario_asociado_nombre
            },
            'errores_detalle': error_items,
            'duplicadas_detalle': duplicate_items
        }, status=status.HTTP_200_OK if len(valid_items) > 0 else status.HTTP_400_BAD_REQUEST)


class DescargarPlantillaExcelView(APIView):
    """
    Genera y sirve para descarga la plantilla oficial de preguntas en formato Excel (.xlsx) (Fase B, Items 5 y 6).
    Incluye 2 hojas:
      1. 'Instrucciones': Guía visual de diligenciamiento, tipos, reglas de negocio y columnas identificadas.
      2. 'Plantilla_Preguntas': Encabezados requeridos y 5 ejemplos representativos de competencias Saber TyT.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        wb = openpyxl.Workbook()

        # Paleta institucional
        azul_primario = "1B6C8C"
        verde_secundario = "8DBF21"
        gris_oscuro = "0F172A"
        gris_claro = "F8FAFC"
        borde_fino = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # -------------------------------------------------------------
        # HOJA 1: INSTRUCCIONES
        # -------------------------------------------------------------
        ws_inst = wb.active
        ws_inst.title = "Instrucciones"
        ws_inst.views.sheetView[0].showGridLines = True

        # Título principal
        ws_inst.merge_cells("A1:G1")
        c1 = ws_inst["A1"]
        c1.value = "INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO - SIMULADOR SABER TyT"
        c1.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
        c1.fill = PatternFill(start_color=azul_primario, end_color=azul_primario, fill_type="solid")
        c1.alignment = Alignment(horizontal="center", vertical="center")
        ws_inst.row_dimensions[1].height = 36

        # Subtítulo
        ws_inst.merge_cells("A2:G2")
        c2 = ws_inst["A2"]
        c2.value = "GUÍA DE DILIGENCIAMIENTO PARA IMPORTACIÓN MASIVA DE PREGUNTAS (R02, R05, R06, R10)"
        c2.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        c2.fill = PatternFill(start_color=gris_oscuro, end_color=gris_oscuro, fill_type="solid")
        c2.alignment = Alignment(horizontal="center", vertical="center")
        ws_inst.row_dimensions[2].height = 24

        ws_inst.append([])  # Fila 3 vacía

        # Encabezados de tabla de instrucciones
        headers_inst = ["Columna", "Campo BD", "Obligatorio", "Valores Permitidos", "Descripción Pedagógica / Regla de Negocio"]
        ws_inst.append(headers_inst)
        ws_inst.row_dimensions[4].height = 24
        for col_num in range(1, len(headers_inst) + 1):
            cell = ws_inst.cell(row=4, column=col_num)
            cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color=azul_primario, end_color=azul_primario, fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = borde_fino

        filas_inst = [
            ("tematica", "categoria", "SÍ", "Razonamiento Cuantitativo, Lectura Crítica, Competencias Ciudadanas, Inglés", "Competencia Saber TyT evaluada. Si la categoría no existe en el sistema, se crea automáticamente."),
            ("tipo", "tipo", "SÍ", "MULTIPLE o VERDADERO_FALSO", "MULTIPLE = Selección con 4 alternativas (A–D). VERDADERO_FALSO = Reactivo binario (V o F)."),
            ("dificultad", "nivel_dificultad", "NO", "Baja, Media, Alta", "Nivel de complejidad cognitiva estimado del reactivo. Si se omite, se asigna Media."),
            ("texto_base", "texto_base", "NO", "Texto libre", "Contexto narrativo, caso o lectura introductoria que antecede a la pregunta."),
            ("enunciado", "enunciado", "SÍ", "Texto libre no vacío", "Pregunta o planteamiento central que debe responder el estudiante."),
            ("opcion_a", "opcion_a", "SÍ", "Texto libre", "Texto de la opción A (para selección múltiple) o 'Verdadero' (para V/F)."),
            ("opcion_b", "opcion_b", "SÍ", "Texto libre", "Texto de la opción B (para selección múltiple) o 'Falso' (para V/F)."),
            ("opcion_c", "opcion_c", "CONDICIONAL", "Texto libre", "Obligatorio para tipo MULTIPLE. Omitir para tipo VERDADERO_FALSO."),
            ("opcion_d", "opcion_d", "CONDICIONAL", "Texto libre", "Obligatorio para tipo MULTIPLE. Omitir para tipo VERDADERO_FALSO."),
            ("respuesta_correcta", "respuesta_correcta", "SÍ", "A, B, C, D (si MULTIPLE) | V, F (si V/F)", "Regla R05: Debe existir exactamente una clave correcta. Cualquier otro valor genera rechazo de la fila."),
            ("justificacion", "retroalimentacion", "NO", "Texto libre", "Explicación formativa mostrada al estudiante al revisar su intento finalizado."),
            ("puntaje", "puntaje", "SÍ", "Número decimal > 0.00 (ej. 2.50)", "Regla R02: El puntaje base debe ser estrictamente mayor que cero. Valores menores o cero son rechazados.")
        ]

        for r_idx, fila in enumerate(filas_inst, 5):
            ws_inst.append(list(fila))
            ws_inst.row_dimensions[r_idx].height = 22
            for c_idx in range(1, len(fila) + 1):
                cell = ws_inst.cell(row=r_idx, column=c_idx)
                cell.font = Font(name="Segoe UI", size=9)
                cell.border = borde_fino
                if c_idx == 3 and fila[2] == "SÍ":
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color="B91C1C")
                if r_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

        # Ajuste de anchos en hoja de instrucciones
        anchos_inst = [18, 16, 14, 30, 55]
        for idx, w in enumerate(anchos_inst, 1):
            ws_inst.column_dimensions[get_column_letter(idx)].width = w

        # -------------------------------------------------------------
        # HOJA 2: PLANTILLA_PREGUNTAS (DATOS)
        # -------------------------------------------------------------
        ws_data = wb.create_sheet(title="Plantilla_Preguntas")
        ws_data.views.sheetView[0].showGridLines = True

        headers_data = [
            "tematica", "tipo", "dificultad", "texto_base", "enunciado",
            "opcion_a", "opcion_b", "opcion_c", "opcion_d",
            "respuesta_correcta", "justificacion", "puntaje"
        ]
        ws_data.append(headers_data)
        ws_data.row_dimensions[1].height = 26

        for col_num in range(1, len(headers_data) + 1):
            cell = ws_data.cell(row=1, column=col_num)
            cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color=azul_primario, end_color=azul_primario, fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = borde_fino

        # Reactivos de demostración Saber TyT
        ejemplos = [
            [
                "Razonamiento Cuantitativo",
                "MULTIPLE",
                "Media",
                "En una empresa de software se requiere determinar el costo para el despliegue de infraestructura en la nube.",
                "¿Si un servidor en la nube cuesta $100 al mes, cuánto se pagará en 6 meses con un 10% de descuento?",
                "$500", "$540", "$580", "$600",
                "B",
                "Costo sin descuento = 6 x 100 = $600. Descuento del 10% = $60. Total a pagar = $540.",
                2.50
            ],
            [
                "Lectura Crítica",
                "MULTIPLE",
                "Alta",
                "El software libre y de código abierto fomenta la innovación colaborativa y la soberanía tecnológica en instituciones públicas.",
                "De acuerdo con el texto, ¿cuál es uno de los principales impactos positivos del software libre?",
                "Fomentar la innovación colaborativa y soberanía tecnológica",
                "Impedir la modificación y estudio del código fuente",
                "Incrementar los costos de licenciamiento corporativo",
                "Restringir el acceso comunitario a herramientas digitales",
                "A",
                "El texto destaca explícitamente la innovación colaborativa y la soberanía tecnológica.",
                2.50
            ],
            [
                "Competencias Ciudadanas",
                "MULTIPLE",
                "Media",
                "Un ciudadano evidencia presuntas irregularidades en la contratación pública municipal y desea que se investigue disciplinariamente.",
                "¿Ante cuál de los siguientes organismos de control disciplinario debe presentarse la queja?",
                "Fiscalía General de la Nación",
                "Procuraduría General de la Nación",
                "Defensoría del Pueblo",
                "Registraduría Nacional del Estado Civil",
                "B",
                "La Procuraduría General de la Nación ejerce la vigilancia disciplinaria de los servidores públicos.",
                2.50
            ],
            [
                "Inglés",
                "MULTIPLE",
                "Baja",
                "Software engineers write comprehensive documentation to support system longevity.",
                "What is the main goal of technical documentation in a software project?",
                "To confuse future developers",
                "To support system maintenance and team collaboration",
                "To erase source code history",
                "To increase runtime latency",
                "B",
                "Technical documentation supports long-term software maintainability and collaboration.",
                2.50
            ],
            [
                "Lectura Crítica",
                "VERDADERO_FALSO",
                "Media",
                "",
                "La tesis en un texto argumentativo constituye la proposición o postura central defendida por el autor.",
                "Verdadero",
                "Falso",
                "",
                "",
                "V",
                "Verdadero. La tesis es la afirmación cardinal sustentada mediante premisas y argumentos.",
                2.50
            ]
        ]

        for r_idx, ej in enumerate(ejemplos, 2):
            ws_data.append(ej)
            ws_data.row_dimensions[r_idx].height = 20
            for c_idx in range(1, len(ej) + 1):
                cell = ws_data.cell(row=r_idx, column=c_idx)
                cell.font = Font(name="Segoe UI", size=9)
                cell.border = borde_fino
                if c_idx == 10:  # respuesta_correcta
                    cell.alignment = Alignment(horizontal="center")
                    cell.font = Font(name="Segoe UI", size=9, bold=True, color=azul_primario)
                if c_idx == 12:  # puntaje
                    cell.alignment = Alignment(horizontal="right")
                    cell.number_format = '0.00'

        # Ajuste automático de anchos en hoja de preguntas
        anchos_data = [24, 18, 12, 35, 45, 20, 20, 20, 20, 18, 40, 10]
        for idx, w in enumerate(anchos_data, 1):
            ws_data.column_dimensions[get_column_letter(idx)].width = w

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="plantilla_oficial_preguntas_saber_tyt.xlsx"'
        return response
