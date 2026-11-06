"""
Servicio de Generación de Reportes Excel (.xlsx) con openpyxl.
Genera los 3 reportes obligatorios con formato profesional institucional:
- Reporte A: Consolidado general (con hoja 2 de promedios por estudiante)
- Reporte B: Desempeño por eje temático
- Reporte C: Historial individual
"""
import io
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportes.services.query_service import QueryService


class ExcelReportService:

    # Paleta institucional UniPutumayo
    COLOR_PRIMARY = "1B6C8C"      # Azul UniPutumayo
    COLOR_SECONDARY = "0F172A"    # Slate 900
    COLOR_ACCENT = "8DBF21"       # Verde institucional
    COLOR_BG_LIGHT = "F8FAFC"     # Slate 50
    COLOR_BORDER = "CBD5E1"       # Gris borde

    @classmethod
    def _crear_estilos_base(cls):
        """Retorna diccionario de fuentes, rellenos y bordes reutilizables."""
        thin_border = Border(
            left=Side(style='thin', color=cls.COLOR_BORDER),
            right=Side(style='thin', color=cls.COLOR_BORDER),
            top=Side(style='thin', color=cls.COLOR_BORDER),
            bottom=Side(style='thin', color=cls.COLOR_BORDER)
        )
        return {
            'font_title': Font(name='Calibri', size=14, bold=True, color='FFFFFF'),
            'font_subtitle': Font(name='Calibri', size=10, italic=True, color='E2E8F0'),
            'font_meta_label': Font(name='Calibri', size=9, bold=True, color='475569'),
            'font_meta_val': Font(name='Calibri', size=9, color='1E293B'),
            'font_header': Font(name='Calibri', size=11, bold=True, color='FFFFFF'),
            'font_data': Font(name='Calibri', size=10, color='0F172A'),
            'font_bold': Font(name='Calibri', size=10, bold=True, color='0F172A'),
            'fill_title': PatternFill(start_color=cls.COLOR_PRIMARY, end_color=cls.COLOR_PRIMARY, fill_type='solid'),
            'fill_header': PatternFill(start_color=cls.COLOR_PRIMARY, end_color=cls.COLOR_PRIMARY, fill_type='solid'),
            'fill_subtotal': PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid'),
            'border_thin': thin_border,
            'align_center': Alignment(horizontal='center', vertical='center'),
            'align_left': Alignment(horizontal='left', vertical='center'),
            'align_right': Alignment(horizontal='right', vertical='center'),
        }

    @classmethod
    def _agregar_encabezado_informe(cls, ws, titulo_reporte, filtros_activos, num_columnas):
        """Genera el bloque superior institucional con nombre, fecha y filtros aplicados."""
        estilos = cls._crear_estilos_base()
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Fila 1: Título de la Institución
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_columnas)
        cell_inst = ws.cell(row=1, column=1)
        cell_inst.value = "INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO — SIMULADOR SABER TyT"
        cell_inst.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        cell_inst.fill = PatternFill(start_color=cls.COLOR_SECONDARY, end_color=cls.COLOR_SECONDARY, fill_type='solid')
        cell_inst.alignment = estilos['align_center']
        ws.row_dimensions[1].height = 24

        # Fila 2: Título del Reporte
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_columnas)
        cell_tit = ws.cell(row=2, column=1)
        cell_tit.value = titulo_reporte.upper()
        cell_tit.font = estilos['font_title']
        cell_tit.fill = estilos['fill_title']
        cell_tit.alignment = estilos['align_center']
        ws.row_dimensions[2].height = 28

        # Fila 3: Metadatos (Fecha de generación y filtros)
        filtros_desc = []
        if filtros_activos.get('anio'):
            filtros_desc.append(f"Año: {filtros_activos['anio']}")
        if filtros_activos.get('periodo_nombre'):
            filtros_desc.append(f"Período: {filtros_activos['periodo_nombre']}")
        if filtros_activos.get('curso_nombre'):
            filtros_desc.append(f"Curso: {filtros_activos['curso_nombre']}")
        if filtros_activos.get('eje_nombre'):
            filtros_desc.append(f"Eje: {filtros_activos['eje_nombre']}")
        if filtros_activos.get('busqueda'):
            filtros_desc.append(f"Búsqueda: '{filtros_activos['busqueda']}'")

        txt_filtros = " | ".join(filtros_desc) if filtros_desc else "Filtros: Todos los registros permitidos"

        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=num_columnas)
        cell_meta = ws.cell(row=3, column=1)
        cell_meta.value = f"Generado: {fecha_str}  •  {txt_filtros}"
        cell_meta.font = Font(name='Calibri', size=9, italic=True, color='475569')
        cell_meta.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 18

        # Fila 4 en blanco de separación
        ws.row_dimensions[4].height = 10
        return 5  # La fila donde comienzan los encabezados de tabla

    @classmethod
    def _autoajustar_columnas(cls, ws):
        """Ajusta automáticamente el ancho de las columnas con margen de lectura."""
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                # Evitar filas combinadas 1 a 3 para no distorsionar anchos
                if cell.row > 4 and cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # =========================================================================
    # REPORTE A: CONSOLIDADO GENERAL (Multi-hoja con promedios por estudiante)
    # =========================================================================
    @classmethod
    def generar_reporte_a_consolidado(cls, filtros=None):
        """
        Genera el Reporte A: Consolidado general de evaluaciones.
        Hoja 1: Intentos detallados (año, período, curso, estudiante, identificación, simulacro, fecha, calificación, estado).
        Hoja 2: Promedio y estadísticas por estudiante.
        """
        filtros = filtros or {}
        wb = openpyxl.Workbook()
        estilos = cls._crear_estilos_base()

        # HOJA 1: DETALLE DE EVALUACIONES
        ws1 = wb.active
        ws1.title = "Consolidado General"
        ws1.views.sheetView[0].showGridLines = True

        columnas = [
            ("Año", 'center', None),
            ("Período", 'center', None),
            ("Curso / Grupo", 'left', None),
            ("Estudiante", 'left', None),
            ("Identificación", 'center', None),
            ("Simulacro Saber TyT", 'left', None),
            ("Fecha Presentación", 'center', None),
            ("Calificación (0.0 - 5.0)", 'right', '0.00'),
            ("Estado", 'center', None),
            ("Aciertos", 'right', '#,##0'),
            ("Errores", 'right', '#,##0'),
            ("Omitidas", 'right', '#,##0')
        ]

        start_row = cls._agregar_encabezado_informe(
            ws1, "Reporte A — Consolidado General de Evaluaciones Saber TyT", filtros, len(columnas)
        )

        # Encabezados de tabla
        for col_idx, (col_nombre, align, _) in enumerate(columnas, 1):
            cell = ws1.cell(row=start_row, column=col_idx)
            cell.value = col_nombre
            cell.font = estilos['font_header']
            cell.fill = estilos['fill_header']
            cell.alignment = estilos['align_center']
            cell.border = estilos['border_thin']
        ws1.row_dimensions[start_row].height = 22

        registros = QueryService.consulta_consolidado_general(filtros)
        current_row = start_row + 1

        if not registros:
            ws1.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=len(columnas))
            empty_cell = ws1.cell(row=current_row, column=1)
            empty_cell.value = "No se encontraron intentos finalizados con los filtros seleccionados."
            empty_cell.font = Font(name='Calibri', size=11, italic=True, color='64748B')
            empty_cell.alignment = estilos['align_center']
            ws1.row_dimensions[current_row].height = 24
        else:
            for item in registros:
                valores = [
                    item['anio'],
                    item['periodo'],
                    item['curso'],
                    item['estudiante_nombre'],
                    item['estudiante_codigo'],
                    item['simulacro'],
                    item['fecha'],
                    item['calificacion'],
                    item['estado'],
                    item['aciertos'],
                    item['errores'],
                    item['omitidas']
                ]
                for col_idx, (val, (_, align_type, num_fmt)) in enumerate(zip(valores, columnas), 1):
                    cell = ws1.cell(row=current_row, column=col_idx)
                    cell.value = val
                    cell.font = estilos['font_data']
                    cell.border = estilos['border_thin']

                    if align_type == 'center':
                        cell.alignment = estilos['align_center']
                    elif align_type == 'right':
                        cell.alignment = estilos['align_right']
                    else:
                        cell.alignment = estilos['align_left']

                    if num_fmt:
                        cell.number_format = num_fmt

                ws1.row_dimensions[current_row].height = 19
                current_row += 1

        cls._autoajustar_columnas(ws1)

        # HOJA 2: PROMEDIO POR ESTUDIANTE
        ws2 = wb.create_sheet(title="Promedios por Estudiante")
        ws2.views.sheetView[0].showGridLines = True

        cols_h2 = [
            ("Estudiante", 'left', None),
            ("Identificación", 'center', None),
            ("Curso", 'left', None),
            ("Intentos Realizados", 'right', '#,##0'),
            ("Nota Promedio", 'right', '0.00'),
            ("Nota Mínima", 'right', '0.00'),
            ("Nota Máxima", 'right', '0.00'),
            ("Estado Final", 'center', None)
        ]

        start_row_h2 = cls._agregar_encabezado_informe(
            ws2, "Resumen y Promedio de Desempeño por Estudiante", filtros, len(cols_h2)
        )

        for col_idx, (col_nombre, _, _) in enumerate(cols_h2, 1):
            cell = ws2.cell(row=start_row_h2, column=col_idx)
            cell.value = col_nombre
            cell.font = estilos['font_header']
            cell.fill = estilos['fill_header']
            cell.alignment = estilos['align_center']
            cell.border = estilos['border_thin']
        ws2.row_dimensions[start_row_h2].height = 22

        # Agrupar registros por estudiante
        estudiantes_map = {}
        for r in registros:
            eid = r['estudiante_id']
            if eid not in estudiantes_map:
                estudiantes_map[eid] = {
                    'nombre': r['estudiante_nombre'],
                    'codigo': r['estudiante_codigo'],
                    'curso': r['curso'],
                    'notas': []
                }
            estudiantes_map[eid]['notas'].append(r['calificacion'])

        current_row_h2 = start_row_h2 + 1
        for eid, edata in estudiantes_map.items():
            notas = edata['notas']
            prom = round(sum(notas) / len(notas), 2)
            mini = round(min(notas), 2)
            maxi = round(max(notas), 2)
            estado_prom = 'Aprobado' if prom >= 3.00 else 'Reprobado'

            row_vals = [
                edata['nombre'],
                edata['codigo'],
                edata['curso'],
                len(notas),
                prom,
                mini,
                maxi,
                estado_prom
            ]

            for col_idx, (val, (_, align_type, num_fmt)) in enumerate(zip(row_vals, cols_h2), 1):
                cell = ws2.cell(row=current_row_h2, column=col_idx)
                cell.value = val
                cell.font = estilos['font_data']
                cell.border = estilos['border_thin']
                if align_type == 'center':
                    cell.alignment = estilos['align_center']
                elif align_type == 'right':
                    cell.alignment = estilos['align_right']
                else:
                    cell.alignment = estilos['align_left']

                if num_fmt:
                    cell.number_format = num_fmt

            ws2.row_dimensions[current_row_h2].height = 19
            current_row_h2 += 1

        cls._autoajustar_columnas(ws2)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    # =========================================================================
    # REPORTE B: DESEMPEÑO POR EJE TEMÁTICO
    # =========================================================================
    @classmethod
    def generar_reporte_b_ejes(cls, filtros=None):
        """
        Genera el Reporte B: Desempeño por eje temático.
        Columnas: año, período, curso, eje, respuestas registradas, aciertos, errores, porcentaje de aciertos.
        """
        filtros = filtros or {}
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Desempeño por Eje"
        ws.views.sheetView[0].showGridLines = True
        estilos = cls._crear_estilos_base()

        columnas = [
            ("Año", 'center', None),
            ("Período", 'center', None),
            ("Curso / Grupo", 'left', None),
            ("Eje Temático (Saber TyT)", 'left', None),
            ("Respuestas Registradas", 'right', '#,##0'),
            ("Aciertos", 'right', '#,##0'),
            ("Errores", 'right', '#,##0'),
            ("Porcentaje de Aciertos", 'right', '0.00%')
        ]

        start_row = cls._agregar_encabezado_informe(
            ws, "Reporte B — Desempeño por Eje Temático Saber TyT", filtros, len(columnas)
        )

        for col_idx, (col_nombre, _, _) in enumerate(columnas, 1):
            cell = ws.cell(row=start_row, column=col_idx)
            cell.value = col_nombre
            cell.font = estilos['font_header']
            cell.fill = estilos['fill_header']
            cell.alignment = estilos['align_center']
            cell.border = estilos['border_thin']
        ws.row_dimensions[start_row].height = 22

        registros = QueryService.consulta_desempeno_ejes(filtros)
        current_row = start_row + 1

        anio_txt = filtros.get('anio') or 'Consolidado'
        periodo_txt = filtros.get('periodo_nombre') or 'Todos'
        curso_txt = filtros.get('curso_nombre') or 'Todos'

        if not registros:
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=len(columnas))
            empty_cell = ws.cell(row=current_row, column=1)
            empty_cell.value = "No se registraron respuestas en los ejes temáticos para los filtros seleccionados."
            empty_cell.font = Font(name='Calibri', size=11, italic=True, color='64748B')
            empty_cell.alignment = estilos['align_center']
            ws.row_dimensions[current_row].height = 24
        else:
            for item in registros:
                pct_dec = (item['porcentaje_acierto'] / 100.0)
                valores = [
                    anio_txt,
                    periodo_txt,
                    curso_txt,
                    item['eje_tematico'],
                    item['total_respondidas'],
                    item['aciertos'],
                    item['errores'],
                    pct_dec
                ]
                for col_idx, (val, (_, align_type, num_fmt)) in enumerate(zip(valores, columnas), 1):
                    cell = ws.cell(row=current_row, column=col_idx)
                    cell.value = val
                    cell.font = estilos['font_data']
                    cell.border = estilos['border_thin']

                    if align_type == 'center':
                        cell.alignment = estilos['align_center']
                    elif align_type == 'right':
                        cell.alignment = estilos['align_right']
                    else:
                        cell.alignment = estilos['align_left']

                    if num_fmt:
                        cell.number_format = num_fmt

                ws.row_dimensions[current_row].height = 19
                current_row += 1

        cls._autoajustar_columnas(ws)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    # =========================================================================
    # REPORTE C: HISTORIAL INDIVIDUAL
    # =========================================================================
    @classmethod
    def generar_reporte_c_historial(cls, filtros=None):
        """
        Genera el Reporte C: Historial individual de evaluaciones.
        Columnas: estudiante, curso, período, simulacro, fecha, preguntas respondidas, aciertos, errores y nota final.
        Orden cronológico y un intento por fila.
        """
        filtros = filtros or {}
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Historial Individual"
        ws.views.sheetView[0].showGridLines = True
        estilos = cls._crear_estilos_base()

        columnas = [
            ("Estudiante", 'left', None),
            ("Curso / Grupo", 'left', None),
            ("Período", 'center', None),
            ("Simulacro Saber TyT", 'left', None),
            ("Intento #", 'center', None),
            ("Fecha Presentación", 'center', None),
            ("Preguntas Respondidas", 'right', '#,##0'),
            ("Aciertos", 'right', '#,##0'),
            ("Errores", 'right', '#,##0'),
            ("Nota Final (0.0 - 5.0)", 'right', '0.00'),
            ("Estado", 'center', None)
        ]

        start_row = cls._agregar_encabezado_informe(
            ws, "Reporte C — Historial Individual de Intentos Saber TyT", filtros, len(columnas)
        )

        for col_idx, (col_nombre, _, _) in enumerate(columnas, 1):
            cell = ws.cell(row=start_row, column=col_idx)
            cell.value = col_nombre
            cell.font = estilos['font_header']
            cell.fill = estilos['fill_header']
            cell.alignment = estilos['align_center']
            cell.border = estilos['border_thin']
        ws.row_dimensions[start_row].height = 22

        registros = QueryService.consulta_historial_individual(filtros, filtros.get('estudiante_id'))
        current_row = start_row + 1

        if not registros:
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=len(columnas))
            empty_cell = ws.cell(row=current_row, column=1)
            empty_cell.value = "No se encontraron registros de historial para el estudiante o filtros especificados."
            empty_cell.font = Font(name='Calibri', size=11, italic=True, color='64748B')
            empty_cell.alignment = estilos['align_center']
            ws.row_dimensions[current_row].height = 24
        else:
            for item in registros:
                valores = [
                    item['estudiante_nombre'],
                    item['curso'],
                    item['periodo'],
                    item['simulacro'],
                    item['numero_intento'],
                    item['fecha'],
                    item['preguntas_respondidas'],
                    item['aciertos'],
                    item['errores'],
                    item['nota_final'],
                    item['estado']
                ]
                for col_idx, (val, (_, align_type, num_fmt)) in enumerate(zip(valores, columnas), 1):
                    cell = ws.cell(row=current_row, column=col_idx)
                    cell.value = val
                    cell.font = estilos['font_data']
                    cell.border = estilos['border_thin']

                    if align_type == 'center':
                        cell.alignment = estilos['align_center']
                    elif align_type == 'right':
                        cell.alignment = estilos['align_right']
                    else:
                        cell.alignment = estilos['align_left']

                    if num_fmt:
                        cell.number_format = num_fmt

                ws.row_dimensions[current_row].height = 19
                current_row += 1

        cls._autoajustar_columnas(ws)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
