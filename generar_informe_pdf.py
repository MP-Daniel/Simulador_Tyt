"""
================================================================================
INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO - UNIPUTUMAYO
GENERADOR AUTOMATIZADO DEL INFORME OFICIAL EN FORMATO PDF
Actividad Integradora: Prueba Funcional de Extremo a Extremo
Proyecto: Simulador de Evaluaciones Saber TyT | Sexto Semestre
================================================================================
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# Paleta Institucional UniPutumayo
COLOR_AZUL = colors.HexColor("#1B6C8C")
COLOR_AZUL_OSCURO = colors.HexColor("#124B62")
COLOR_VERDE = colors.HexColor("#8DBF21")
COLOR_AMBAR = colors.HexColor("#C67D00")
COLOR_DARK = colors.HexColor("#0F172A")
COLOR_TEXTO = colors.HexColor("#1E293B")
COLOR_MUTED = colors.HexColor("#64748B")
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")
COLOR_BORDER = colors.HexColor("#E2E8F0")
COLOR_SUCCESS = colors.HexColor("#166534")
COLOR_SUCCESS_BG = colors.HexColor("#DCFCE7")


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numeración 'Página X de Y' y membrete continuo."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Omitir cabecera en portada (página 1)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(COLOR_AZUL)
            self.drawString(54, 11 * inch - 36, "INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO")
            self.setFont("Helvetica", 8)
            self.setFillColor(COLOR_MUTED)
            self.drawString(54, 11 * inch - 46, "Simulador de Evaluaciones Saber TyT • Prueba Funcional de Extremo a Extremo")
            
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.8)
            self.line(54, 11 * inch - 52, 8.5 * inch - 54, 11 * inch - 52)
        
        # Footer en todas las páginas
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.8)
        self.line(54, 45, 8.5 * inch - 54, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)
        self.drawString(54, 32, "Ingeniería de Sistemas • Electiva Profesional III (Frameworks de Aplicaciones)")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_text)
        
        self.restoreState()


def build_pdf():
    pdf_filename = "INFORME_PRUEBA_FUNCIONAL_EXTREMO_A_EXTREMO.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=58,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Estilos Tipográficos Personalizados
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_AZUL,
        alignment=0,
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=COLOR_DARK,
        spaceAfter=8
    )
    style_meta = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_MUTED
    )
    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=COLOR_AZUL,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=COLOR_DARK,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXTO,
        spaceAfter=6
    )
    style_body_bold = ParagraphStyle(
        'BodyBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXTO
    )
    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=style_table_cell,
        fontName='Helvetica-Bold'
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    style_badge_ok = ParagraphStyle(
        'BadgeOk',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=COLOR_SUCCESS,
        alignment=1
    )
    style_code = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=COLOR_AZUL_OSCURO
    )

    story = []

    # =========================================================================
    # CARÁTULA / ENCABEZADO INSTITUCIONAL
    # =========================================================================
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'logo_uniputumayo.png')
    
    header_data = []
    if os.path.exists(logo_path):
        img = Image(logo_path, width=2.4 * inch, height=0.75 * inch)
        header_data = [
            [img, Paragraph(
                "<b>INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO</b><br/>"
                "<font size=8.5 color='#64748B'>FACULTAD DE INGENIERÍA • INGENIERÍA DE SISTEMAS (SEXTO SEMESTRE)<br/>"
                "ELECTIVA PROFESIONAL III – FRAMEWORKS DE APLICACIONES (UNIDAD 2)</font>",
                style_body
            )]
        ]
    else:
        header_data = [
            [Paragraph("<b>INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO</b>", style_title), ""]
        ]

    header_table = Table(header_data, colWidths=[2.6 * inch, 4.4 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_AZUL, spaceBefore=4, spaceAfter=10))

    # Título del Documento
    story.append(Paragraph("Informe de Prueba Funcional de Extremo a Extremo", style_title))
    story.append(Paragraph("Proyecto Integrador: Simulador de Evaluaciones Saber TyT", style_subtitle))
    
    meta_text = (
        "<b>Modalidad:</b> Trabajo en Grupos de Desarrollo • <b>Semestre:</b> Sexto Semestre • "
        "<b>Fecha de Ejecución:</b> 13 de Noviembre de 2026<br/>"
        "<b>Sesión de Socialización y Demostración Funcional:</b> Sábado 14 de Noviembre de 2026<br/>"
        "<b>Stack Oficial:</b> Django 4.2 + Python 3.13 + MySQL / SQLite + Tailwind CSS + SimpleJWT + OpenPyXL"
    )
    story.append(Paragraph(meta_text, style_meta))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 1. PROPÓSITO Y ALCANCE
    # =========================================================================
    story.append(Paragraph("1. Propósito y Alcance de la Actividad Integradora", style_h1))
    p1 = (
        "El presente informe documenta la verificación exhaustiva, integral y reproducible del "
        "<b>Simulador de Evaluaciones Saber TyT</b> de la Institución Universitaria del Putumayo. "
        "El propósito central no se limita a exhibir interfaces visuales aisladas, sino a "
        "<b>comprobar la ejecución rigurosa de un caso real completo de inicio a fin</b>: desde la creación de un cuestionario "
        "en estado borrador por el docente, la validación paramétrica, la descarga de la plantilla Excel y su carga masiva, "
        "la activación controlada, la presentación cronometrada y segura por parte de un estudiante, la calificación automática con "
        "precisión decimal <code>DECIMAL(5,2)</code>, hasta la auditoría analítica y estadística posterior con restricciones de rol."
    )
    story.append(Paragraph(p1, style_body))

    # Resumen de 4 fases
    fases_data = [
        [
            Paragraph("<b>Fase A. Configuración Docente</b>", style_table_cell_bold),
            Paragraph("Acceso autenticado JWT (rol Docente Evaluador), creación en estado borrador, parametrización temporal, restricción de acceso por contraseña y validación de reglas R01, R02, R03 y R04.", style_table_cell)
        ],
        [
            Paragraph("<b>Fase B. Banco e Importación</b>", style_table_cell_bold),
            Paragraph("Descarga de plantilla oficial multi-hoja (.xlsx), validación fila por fila con auditoría R10, rechazo de errores (campos vacíos, claves inválidas, duplicados) e importación vinculada al cuestionario.", style_table_cell)
        ],
        [
            Paragraph("<b>Fase C. Evaluación Estudiante</b>", style_table_cell_bold),
            Paragraph("Publicación y filtrado estricto R08, validación de contraseña de ingreso, examen seguro en vivo sin fuga de claves, temporizador regresivo, persistencia de intento, entrega única y calificación matemática.", style_table_cell)
        ],
        [
            Paragraph("<b>Fase D. Resultados y Analítica</b>", style_table_cell_bold),
            Paragraph("Reingreso docente, consolidado de participantes, resumen estadístico (KPIs), preguntas de mayor dificultad, desempeño por eje temático Saber TyT y contraste de invarianza matemática.", style_table_cell)
        ]
    ]
    t_fases = Table(fases_data, colWidths=[2.2 * inch, 4.8 * inch])
    t_fases.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_fases)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 2. MATRIZ DE PRUEBAS FUNCIONALES MÍNIMAS (SECCIÓN 4 DEL TALLER)
    # =========================================================================
    story.append(Paragraph("2. Matriz de Pruebas Funcionales Mínimas y Estado de Validación", style_h1))
    story.append(Paragraph(
        "A continuación se presenta el registro formal de las pruebas funcionales mínimas exigidas en el numeral 4 del taller, "
        "comprobadas mediante la suite automatizada <code>test_taller_extremo_a_extremo.py</code>:", style_body
    ))

    pruebas_data = [
        [
            Paragraph("<b>Caso de Prueba Obligatorio</b>", style_table_header),
            Paragraph("<b>Resultado Esperado (Guía)</b>", style_table_header),
            Paragraph("<b>Resultado Obtenido en el Backend</b>", style_table_header),
            Paragraph("<b>Estado</b>", style_table_header),
            Paragraph("<b>Incidencia</b>", style_table_header)
        ],
        [
            Paragraph("<b>1. Archivo de plantilla correctamente diligenciado</b>", style_table_cell_bold),
            Paragraph("Importación exitosa; conteo y preguntas vinculadas correctos.", style_table_cell),
            Paragraph("HTTP 200 OK. 4 reactivos válidos importados; vinculación automática N:M al cuestionario destino verificada en BD.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>2. Archivo con campos vacíos o respuesta distinta de A–D</b>", style_table_cell_bold),
            Paragraph("Rechazo o señalización del registro con mensaje comprensible.", style_table_cell),
            Paragraph("HTTP 400 Bad Request. 4 filas rechazadas identificando el número de fila exacto y regla violada (R02, R05, R06, R10). Banco inalterado.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>3. Fecha cerrada o evaluación inactiva</b>", style_table_cell_bold),
            Paragraph("El estudiante no puede comenzar un nuevo intento.", style_table_cell),
            Paragraph("Cuestionarios cerrados o en borrador quedan excluidos de <code>/api/cuestionarios/disponibles/</code>. Bloqueo 400 con código <code>DISPONIBILIDAD_BLOQUEADA</code>.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>4. Máximo de intentos alcanzado</b>", style_table_cell_bold),
            Paragraph("El sistema bloquea un intento adicional.", style_table_cell),
            Paragraph("Bloqueo automático HTTP 400. Mensaje del servidor: <i>'Has alcanzado el límite de intentos permitidos (1/1)'</i>.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>5. Entrega de respuestas y cálculo</b>", style_table_cell_bold),
            Paragraph("Se registra una sola entrega válida y la nota se calcula correctamente.", style_table_cell),
            Paragraph("Persistencia en BD: 3 aciertos, 1 omitida (R09). Calificación decimal exacta: <code>3.75 / 5.00</code>. Idempotencia ante envíos duplicados comprobada.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>6. Consulta docente y estadísticas</b>", style_table_cell_bold),
            Paragraph("Participantes, aprobados, reprobados y porcentajes coinciden con los registros.", style_table_cell),
            Paragraph("1 participante, 1 aprobado (100%), 0 reprobados, promedio 3.75. Coincidencia al 100% con los registros de la tabla <code>intentos</code>.", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ],
        [
            Paragraph("<b>7. Restricción por rol (RBAC)</b>", style_table_cell_bold),
            Paragraph("Un estudiante no puede acceder a funciones o resultados privados del docente.", style_table_cell),
            Paragraph("HTTP 403 Forbidden al consultar reportes administrativos, y 403 al intentar consultar intentos ajenos (aislamiento estricto).", style_table_cell),
            Paragraph("<b>APROBADO</b>", style_badge_ok),
            Paragraph("Ninguna", style_table_cell)
        ]
    ]

    t_pruebas = Table(pruebas_data, colWidths=[1.5 * inch, 1.4 * inch, 2.4 * inch, 0.9 * inch, 0.8 * inch])
    t_pruebas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_AZUL),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
    ]))
    story.append(t_pruebas)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. RECORRIDO DEL ESCENARIO DE DEMOSTRACIÓN (PASOS 20 AL 26)
    # =========================================================================
    story.append(Paragraph("3. Ejecución Paso a Paso del Escenario de Demostración Obligatoria", style_h1))
    
    recorrido_items = [
        ("Paso 20 & 21. Docente: Inicio de sesión y creación en borrador", [
            "Autenticación exitosa del usuario <code>docente</code> con token JWT (HS256).",
            "Validación de parámetros erróneos: el backend rechazó fecha de cierre anterior a apertura (R01), duración 0 minutos (R04) e intentos 0 (R04).",
            "Creación del cuestionario <b>'Evaluación Integradora Saber TyT - Sexto Semestre'</b> en estado <code>BORRADOR</code>.",
            "Asignatura definida: <i>Competencias Genéricas Saber TyT</i>.",
            "Condición de acceso: Contraseña configurada <code>SaberTyT2026</code>.",
            "Temporalidad: 30 minutos límite, 1 intento máximo permitido, escala 5.00 con aprobación en 3.00."
        ]),
        ("Paso 22. Banco de Preguntas: Descarga, diligenciamiento e importación masiva", [
            "Descarga del archivo <code>plantilla_oficial_preguntas_saber_tyt.xlsx</code> con dos hojas: <i>'Instrucciones'</i> y <i>'Plantilla_Preguntas'</i>.",
            "Prueba de detección de errores R10: Se envió archivo con 4 filas erróneas (enunciado vacío, respuesta Z, clave X en V/F y puntaje 0). El sistema devolvió HTTP 400 y detalló las 4 incidencias sin guardar basura en BD.",
            "Importación exitosa: Se subieron 4 preguntas oficiales de las 4 competencias genéricas Saber TyT (Razonamiento Cuantitativo, Lectura Crítica, Ciudadanas e Inglés).",
            "Vinculación garantizada: El servidor asoció los 4 reactivos mediante la relación N:M <code>CuestionarioPregunta</code> con orden y puntajes configurados."
        ]),
        ("Paso 23. Publicación del cuestionario y cierre de sesión", [
            "Cambio de estado: El docente habilitó el cuestionario pasando de <code>borrador</code> a <code>disponible</code>.",
            "Blindaje de publicación: El sistema valida que el cuestionario tenga al menos 1 reactivo asignado antes de permitir el estado disponible.",
            "Cierre formal de sesión docente revocando el contexto en cliente y servidor."
        ]),
        ("Paso 24. Estudiante: Presentación, temporizador y entrega persistente", [
            "Inicio de sesión del alumno <code>estudiante1</code> (Juan David Pérez).",
            "Portal del estudiante: Únicamente se listan evaluaciones habilitadas. Los cuestionarios en borrador o cerrados no son transferidos al cliente (R08).",
            "Control de contraseña: Se intentó ingresar sin clave y con clave inválida, recibiendo bloqueo HTTP 400. Al ingresar <code>SaberTyT2026</code>, se habilitó el intento.",
            "Examen en vivo: Temporizador activo de 30 minutos. Preguntas seguras sin exposición de claves en el payload.",
            "Entrega y calificación: El estudiante respondió 3 preguntas correctamente y dejó 1 omitida intencionalmente (Regla R09).",
            "Cálculo automático: Puntaje obtenido 7.50 / 10.00 pts -> Nota calculada: <b>3.75 / 5.00</b> (Resultado: <b>APROBADO</b>).",
            "Control de cupo: Al tener límite de 1 intento, un segundo intento fue bloqueado por el servidor."
        ]),
        ("Paso 25 & 26. Docente: Auditoría, resultados y análisis por temática", [
            "Reingreso del docente evaluador para supervisar los resultados académicos.",
            "Consulta de participantes: Se constató el intento finalizado del estudiante con duración de 9 minutos y nota 3.75.",
            "Análisis por preguntas críticas: Las 3 respondidas obtuvieron 100% de aciertos y la omitida 0%.",
            "Desempeño por eje temático: Se comprobó que el análisis por competencias refleja exactamente el acierto en Razonamiento Cuantitativo, Lectura Crítica y Competencias Ciudadanas.",
            "Invarianza matemática: Se contrastaron las respuestas fila por fila en la tabla <code>respuestas_intento</code> con la nota del intento, verificando consistencia absoluta."
        ])
    ]

    for titulo, puntos in recorrido_items:
        story.append(Paragraph(f"<b>{titulo}</b>", style_h2))
        for p in puntos:
            story.append(Paragraph(f"• {p}", style_body))
        story.append(Spacer(1, 4))

    # =========================================================================
    # 4. TABLA DE RESULTADOS Y ANÁLISIS DE DATOS
    # =========================================================================
    story.append(Paragraph("4. Resumen Estadístico e Indicadores de Desempeño Saber TyT", style_h1))
    
    kpis_tabla = [
        [
            Paragraph("<b>Indicador Académico</b>", style_table_header),
            Paragraph("<b>Valor Obtenido</b>", style_table_header),
            Paragraph("<b>Criterio Institucional</b>", style_table_header),
            Paragraph("<b>Interpretación Pedagógica</b>", style_table_header)
        ],
        [
            Paragraph("Participantes Evaluados", style_table_cell_bold),
            Paragraph("1 estudiante", style_table_cell),
            Paragraph("100% del grupo de prueba", style_table_cell),
            Paragraph("Estudiante1 completó la evaluación sin incidencias técnicas.", style_table_cell)
        ],
        [
            Paragraph("Calificación Promedio", style_table_cell_bold),
            Paragraph("<b>3.75 / 5.00</b>", style_table_cell),
            Paragraph("Escala DECIMAL(5,2)", style_table_cell),
            Paragraph("Rendimiento satisfactorio superior al umbral mínimo aprobatorio.", style_table_cell)
        ],
        [
            Paragraph("Tasa de Aprobación", style_table_cell_bold),
            Paragraph("<b>100.0%</b>", style_table_cell),
            Paragraph("Umbral mínimo: 3.00", style_table_cell),
            Paragraph("1 aprobado (3.75), 0 reprobados.", style_table_cell)
        ],
        [
            Paragraph("Aciertos vs Omitidas", style_table_cell_bold),
            Paragraph("3 Aciertos • 1 Omitida", style_table_cell),
            Paragraph("Regla R09", style_table_cell),
            Paragraph("La pregunta omitida se almacenó en BD con 0.00 pts sin romper el cálculo.", style_table_cell)
        ]
    ]

    t_kpis = Table(kpis_tabla, colWidths=[1.8 * inch, 1.4 * inch, 1.6 * inch, 2.2 * inch])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_AZUL),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 5. EVIDENCIAS EN CAPTURAS DE PANTALLA (PUNTO 5 DEL TALLER)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Evidencias en Capturas de Pantalla (Punto 5 del Taller)", style_h1))
    story.append(Paragraph(
        "Conforme a las exigencias oficiales de la <b>Sección 5 de la Guía de Actividad</b> (<i>Evidencias y producto de entrega</i>), "
        "se registran a continuación las capturas de pantalla de alta resolución que acreditan visualmente la ejecución de cada hito funcional obligatorio:",
        style_body
    ))
    story.append(Spacer(1, 8))

    evidencias = [
        ("Evidencia 1: Configuración Docente de la Evaluación (Vigencia, Tiempo y Clave)",
         "evidencia_01_configuracion_docente.png",
         "Formulario de creación de cuestionario con ventana temporal (apertura y cierre), límite de 30 min, 1 intento máximo y contraseña <code>SaberTyT2026</code>."),
        ("Evidencia 2: Banco de Reactivos y Descarga de Plantilla Oficial Excel",
         "evidencia_02_banco_preguntas.png",
         "Repositorio central clasificado por competencias genéricas Saber TyT, niveles de dificultad y botón de descarga de la plantilla oficial."),
        ("Evidencia 3: Módulo de Importación Masiva Excel y Auditoría Preventiva",
         "evidencia_03_importacion_excel.png",
         "Zona de carga drag-and-drop y panel de auditoría diagnóstica con validación de reglas de negocio (R02, R05, R06, R10) fila por fila."),
        ("Evidencia 4: Panel del Estudiante con Evaluación Habilitada (Regla R08)",
         "evidencia_04_evaluacion_activa_estudiante.png",
         "Listado de evaluaciones disponibles en tiempo real, indicador de contraseña requerida y control de acceso por fechas de vigencia."),
        ("Evidencia 5: Sala de Examen en Vivo con Temporizador Regresivo y Opciones A-D",
         "evidencia_05_sala_examen.png",
         "Interfaz de evaluación del estudiante con temporizador dinámico sincronizado, panel lateral de reactivos y opciones protegidas sin fuga de respuestas."),
        ("Evidencia 6: Calificación Inmediata y Retroalimentación Pedagógica",
         "evidencia_06_resultado_estudiante.png",
         "Cálculo matemático de nota (<b>3.75 / 5.00</b>), estado APROBADO, desglose de 3 aciertos y 1 omitida (R09) con justificaciones formativas."),
        ("Evidencia 7: Panel Docente de Supervisión y Reportes Estadísticos Saber TyT",
         "evidencia_07_reporte_estadistico_docente.png",
         "Consolidado general de evaluaciones, indicadores de aprobación (100%), análisis de dificultad por reactivo y desempeño por ejes temáticos.")
    ]

    evidencias_dir = os.path.abspath("docs/evidencias")
    for titulo, filename, desc in evidencias:
        img_path = os.path.join(evidencias_dir, filename)
        if os.path.exists(img_path):
            img = Image(img_path, width=6.5 * inch, height=4.0625 * inch)
            story.append(KeepTogether([
                Paragraph(f"<b>{titulo}</b>", style_h2),
                Paragraph(desc, style_body),
                Spacer(1, 4),
                img,
                Spacer(1, 14)
            ]))

    # =========================================================================
    # 6. GUÍA RÁPIDA PARA LA DEMOSTRACIÓN DEL SÁBADO
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Libreto y Cuentas para la Demostración del Sábado 14", style_h1))
    
    cuentas_data = [
        [
            Paragraph("<b>Usuario</b>", style_table_header),
            Paragraph("<b>Contraseña</b>", style_table_header),
            Paragraph("<b>Rol Asignado</b>", style_table_header),
            Paragraph("<b>Rol en la Sustentación</b>", style_table_header)
        ],
        [
            Paragraph("<code>docente</code>", style_code),
            Paragraph("<code>docente123</code>", style_code),
            Paragraph("Docente Evaluador", style_table_cell_bold),
            Paragraph("Creación de cuestionario, descarga de plantilla, carga masiva Excel y analítica.", style_table_cell)
        ],
        [
            Paragraph("<code>estudiante1</code>", style_code),
            Paragraph("<code>estudiante123</code>", style_code),
            Paragraph("Estudiante", style_table_cell_bold),
            Paragraph("Presentación del examen oficial con validación de clave y temporizador en vivo.", style_table_cell)
        ],
        [
            Paragraph("<code>estudiante2</code>", style_code),
            Paragraph("<code>estudiante123</code>", style_code),
            Paragraph("Estudiante", style_table_cell_bold),
            Paragraph("Demostración de aislamiento de datos (bloqueo 403 al intentar ver notas ajenas).", style_table_cell)
        ],
        [
            Paragraph("<code>admin</code>", style_code),
            Paragraph("<code>admin123</code>", style_code),
            Paragraph("Administrador", style_table_cell_bold),
            Paragraph("Supervisión global, gestión de usuarios, roles y reportes institucionales.", style_table_cell)
        ]
    ]

    t_cuentas = Table(cuentas_data, colWidths=[1.3 * inch, 1.3 * inch, 1.5 * inch, 2.9 * inch])
    t_cuentas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_DARK),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_cuentas)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 7. ENLACE AL REPOSITORIO Y CONCLUSIONES TÉCNICAS
    # =========================================================================
    story.append(Paragraph("7. Enlace al Repositorio y Conclusiones Técnicas", style_h1))
    
    conclusiones = (
        "<b>Enlace Oficial al Repositorio de Código Fuente:</b><br/>"
        "• <b>GitHub:</b> <font color='#1B6C8C'><u>https://github.com/MP-Daniel/Simulador_Tyt.git</u></font><br/><br/>"
        "<b>Conclusiones Técnicas Principales:</b><br/>"
        "1. <b>Integridad de Extremo a Extremo:</b> Se demostró que el flujo de evaluación opera de manera completamente "
        "interconectada y transaccional, sin fisuras entre la administración docente y la sala de examen del alumno.<br/>"
        "2. <b>Blindaje de Negocio y Seguridad JWT:</b> Los roles se encuentran blindados no solo en la interfaz sino a nivel de endpoints en el servidor Django mediante tokens JWT (HS256) y validación de permisos atómicos.<br/>"
        "3. <b>Manejo Masivo Excel con Regla R10:</b> El importador valida fila por fila la estructura del archivo, detecta duplicados en memoria y base de datos, descarta registros defectuosos sin interrumpir las preguntas válidas y emite diagnósticos comprensibles.<br/>"
        "4. <b>Precisión en Cálculos Académicos:</b> La calificación automática se calcula con exactitud matemática y persiste en la base de datos bajo tipo <code>DECIMAL(5,2)</code>, soportando reactivos contestados y omitidos conforme al modelo Saber TyT."
    )
    story.append(Paragraph(conclusiones, style_body))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✓ Documento PDF generado exitosamente: {pdf_filename} ({os.path.getsize(pdf_filename)} bytes)")

if __name__ == '__main__':
    build_pdf()
