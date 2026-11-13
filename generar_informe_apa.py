# -*- coding: utf-8 -*-
"""
================================================================================
INSTITUCIÓN UNIVERSITARIA DEL PUTUMAYO - UNIPUTUMAYO
FACULTAD DE INGENIERÍA - PROGRAMA DE INGENIERÍA DE SISTEMAS
ELECTIVA PROFESIONAL III: TECNOLOGÍAS WEB Y ARQUITECTURA DE SOFTWARE

GENERADOR OFICIAL DEL INFORME TÉCNICO EN NORMAS APA 7MA EDICIÓN (30 PÁGINAS)
Actividad: Prueba Funcional de Extremo a Extremo en el Simulador Saber TyT
Autores: Daniel Alejandro Macías Pérez & José Leonel Enríquez Zambrano
================================================================================
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
import pypdf

PAGE_WIDTH, PAGE_HEIGHT = letter # 612 x 792
MARGIN_LEFT = 72
MARGIN_RIGHT = 72
MARGIN_TOP = 98
MARGIN_BOTTOM = 80
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT # 468 pt
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 614 pt

BG_PATH = os.path.join("docs", "assets", "plantilla_institucional_uniputumayo.jpg")
PDF_OUTPUT = "INFORME_PRUEBA_FUNCIONAL_EXTREMO_A_EXTREMO.pdf"

COLOR_ROJO_HEADER = colors.HexColor("#CC0000")
COLOR_TITULO = colors.HexColor("#0F2942")
COLOR_TEXTO = colors.HexColor("#1A1A1A")
COLOR_MUTED = colors.HexColor("#555555")
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")


class APANumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numeración 'Página X | 30' y fondo institucional."""
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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        # 1. Encabezado institucional rojo a la derecha
        self.saveState()
        self.setFont("Helvetica-Bold", 10.5)
        self.setFillColor(COLOR_ROJO_HEADER)
        header_text = "FACULTAD DE INGENIERÍA, INGENIERÍA DE SISTEMAS"
        self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 74, header_text)

        # 2. Número de página a la derecha
        self.setFont("Helvetica", 10)
        self.setFillColor(colors.HexColor("#333333"))
        page_str = f"Página {self._pageNumber} | {total_pages}"
        self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 88, page_str)
        self.restoreState()


def draw_background(canvas_obj, doc_obj):
    """Dibuja el membrete institucional al inicio de cada página antes de los flowables."""
    if os.path.exists(BG_PATH):
        canvas_obj.drawImage(BG_PATH, 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT)


def get_apa_styles():
    styles = getSampleStyleSheet()

    # Portada
    styles.add(ParagraphStyle(
        name="APATitle",
        fontName="Times-Bold",
        fontSize=15,
        leading=21,
        alignment=1, # Centrado
        textColor=COLOR_TITULO,
        spaceAfter=12
    ))

    styles.add(ParagraphStyle(
        name="APASubtitle",
        fontName="Times-Italic",
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=COLOR_TEXTO,
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name="APACoverAuthor",
        fontName="Times-Bold",
        fontSize=12,
        leading=18,
        alignment=1,
        textColor=COLOR_TITULO,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="APACoverMeta",
        fontName="Times-Roman",
        fontSize=11,
        leading=17,
        alignment=1,
        textColor=COLOR_TEXTO,
        spaceAfter=6
    ))

    # Títulos de Sección APA
    styles.add(ParagraphStyle(
        name="APAHeading1",
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        alignment=1, # Nivel 1: Centrado, Negrita
        textColor=COLOR_TITULO,
        spaceBefore=8,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="APAHeading2",
        fontName="Times-Bold",
        fontSize=11.5,
        leading=15,
        alignment=0, # Nivel 2: Izquierda, Negrita
        textColor=COLOR_TITULO,
        spaceBefore=7,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="APAHeading3",
        fontName="Times-BoldItalic",
        fontSize=11,
        leading=15,
        alignment=0, # Nivel 3: Izquierda, Negrita Cursiva
        textColor=COLOR_TITULO,
        spaceBefore=6,
        spaceAfter=4
    ))

    # Párrafo Normal con sangría APA 0.5 in (24pt)
    styles.add(ParagraphStyle(
        name="APABody",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        alignment=4, # Justificado
        textColor=COLOR_TEXTO,
        firstLineIndent=24,
        spaceAfter=6
    ))

    # Párrafo sin sangría inicial
    styles.add(ParagraphStyle(
        name="APABodyNoIndent",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        alignment=4,
        textColor=COLOR_TEXTO,
        spaceAfter=6
    ))

    # Viñeta / Lista APA
    styles.add(ParagraphStyle(
        name="APABullet",
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        alignment=4,
        textColor=COLOR_TEXTO,
        leftIndent=18,
        firstLineIndent=-10,
        spaceAfter=4
    ))

    # Elementos de Tabla de Contenido
    styles.add(ParagraphStyle(
        name="APATOCItem",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_TEXTO,
        spaceAfter=1
    ))

    styles.add(ParagraphStyle(
        name="APATOCItemRight",
        fontName="Times-Bold",
        fontSize=9.5,
        leading=13.5,
        alignment=2, # Derecha
        textColor=COLOR_TITULO,
        spaceAfter=1
    ))

    # Tabla APA
    styles.add(ParagraphStyle(
        name="APATableNumber",
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        alignment=0,
        textColor=COLOR_TITULO,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name="APATableTitle",
        fontName="Times-Italic",
        fontSize=9.5,
        leading=13,
        alignment=0,
        textColor=COLOR_TEXTO,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="APATableCell",
        fontName="Times-Roman",
        fontSize=8,
        leading=11,
        alignment=0,
        textColor=COLOR_TEXTO
    ))

    styles.add(ParagraphStyle(
        name="APATableCellBold",
        fontName="Times-Bold",
        fontSize=8,
        leading=11,
        alignment=0,
        textColor=COLOR_TITULO
    ))

    styles.add(ParagraphStyle(
        name="APATableCellCenter",
        fontName="Times-Roman",
        fontSize=8,
        leading=11,
        alignment=1,
        textColor=COLOR_TEXTO
    ))

    styles.add(ParagraphStyle(
        name="APATableHeader",
        fontName="Times-Bold",
        fontSize=8.5,
        leading=11.5,
        alignment=0,
        textColor=COLOR_TITULO
    ))

    styles.add(ParagraphStyle(
        name="APATableHeaderCenter",
        fontName="Times-Bold",
        fontSize=8.5,
        leading=11.5,
        alignment=1,
        textColor=COLOR_TITULO
    ))

    # Figura APA
    styles.add(ParagraphStyle(
        name="APAFigNumber",
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        alignment=0,
        textColor=COLOR_TITULO,
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name="APAFigTitle",
        fontName="Times-Italic",
        fontSize=9.5,
        leading=13,
        alignment=0,
        textColor=COLOR_TEXTO,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="APANote",
        fontName="Times-Roman",
        fontSize=8.5,
        leading=12,
        alignment=4,
        textColor=COLOR_TEXTO,
        spaceBefore=4,
        spaceAfter=3
    ))

    # Referencia APA (Sangría Francesa)
    styles.add(ParagraphStyle(
        name="APAReference",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=14,
        alignment=4,
        textColor=COLOR_TEXTO,
        leftIndent=24,
        firstLineIndent=-24,
        spaceAfter=7
    ))

    return styles


def build_pdf():
    styles = get_apa_styles()
    story = []

    # Helper para tablas APA estándar
    def get_apa_table_style():
        return TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.8, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1.2, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])

    # =========================================================================
    # PÁGINA 1: PORTADA OFICIAL APA 7
    # =========================================================================
    story.append(Spacer(1, 45))
    story.append(Paragraph("Informe Técnico de Aseguramiento de la Calidad y Verificación Funcional de Extremo a Extremo en el Simulador Saber TyT", styles["APATitle"]))
    story.append(Paragraph("Validación Integral del Ciclo de Evaluación, Banco de Preguntas, Importación Masiva Excel, Motor de Exámenes, Reglas de Negocio R01–R10 y Suite Automatizada 26/26", styles["APASubtitle"]))
    story.append(Spacer(1, 35))
    story.append(Paragraph("Daniel Alejandro Macías Pérez", styles["APACoverAuthor"]))
    story.append(Paragraph("José Leonel Enríquez Zambrano", styles["APACoverAuthor"]))
    story.append(Spacer(1, 45))
    story.append(Paragraph("Facultad de Ingeniería, Programa de Ingeniería de Sistemas", styles["APACoverMeta"]))
    story.append(Paragraph("Institución Universitaria del Putumayo — UniPutumayo", styles["APACoverMeta"]))
    story.append(Paragraph("Electiva Profesional III: Tecnologías Web y Arquitectura de Software", styles["APACoverMeta"]))
    story.append(Paragraph("Docente Evaluador del Área de Ingeniería", styles["APACoverMeta"]))
    story.append(Spacer(1, 25))
    story.append(Paragraph("Noviembre 13 de 2026", styles["APACoverMeta"]))
    story.append(Paragraph("Mocoa, Putumayo, Colombia", styles["APACoverMeta"]))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: TABLA DE CONTENIDO (PARTE I)
    # =========================================================================
    story.append(Paragraph("Tabla de Contenido", styles["APAHeading1"]))
    story.append(Spacer(1, 6))

    toc_p1 = [
        ("Resumen y Palabras Clave", "4"),
        ("1. Introducción y Planteamiento del Problema", "5"),
        ("    1.1 Contexto Institucional y Justificación de la Prueba Integral", "6"),
        ("2. Alcance, Reglas de Negocio y Arquitectura del Sistema", "7"),
        ("    2.1 Reglas de Validación Paramétrica y de Negocio (R01 a R10)", "8"),
        ("    2.2 Seguridad JWT, Control de Acceso RBAC y Auditoría de Intentos", "9"),
        ("3. Matriz de Pruebas Funcionales Mínimas", "10"),
        ("    3.1 Pruebas de Carga Masiva y Validación de Plantilla Excel", "11"),
        ("    3.2 Pruebas de Control de Intentos y Ventana de Disponibilidad", "12"),
        ("4. Ejecución del Escenario de Demostración Obligatoria (Pasos 20 al 26)", "13"),
        ("    4.1 Fase A: Configuración y Parametrización Docente", "14"),
        ("    4.2 Fase B: Presentación Cronometrada y Evaluación Estudiante", "15"),
    ]

    def make_toc_entry(title, page_num):
        clean_title = title.strip()
        indent_count = len(title) - len(clean_title)
        indent_html = "&nbsp;&nbsp;&nbsp;&nbsp;" * (indent_count // 4)
        # Calcular puntos guía para evitar desbordamiento
        approx_title_width = len(clean_title) * 5.2 + (indent_count // 4) * 16
        dots_count = max(8, int((420 - approx_title_width) / 2.8))
        dots_str = "." * dots_count
        cell_text = f"{indent_html}{clean_title} <font color='#888888'>{dots_str}</font>"
        
        row_table = Table(
            [[Paragraph(cell_text, styles["APATOCItem"]), Paragraph(page_num, styles["APATOCItemRight"])]],
            colWidths=[435, 33]
        )
        row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        return row_table

    for title, page_num in toc_p1:
        story.append(make_toc_entry(title, page_num))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: TABLA DE CONTENIDO (PARTE II) & LISTAS DE TABLAS Y FIGURAS
    # =========================================================================
    story.append(Paragraph("Tabla de Contenido (Continuación)", styles["APAHeading1"]))
    story.append(Spacer(1, 6))

    toc_p2 = [
        ("5. Evidencias de Implementación y Capturas de Pantalla", "16"),
        ("    Figura 1. Creación y Parametrización del Cuestionario en Panel Docente", "16"),
        ("    Figura 2. Banco de Preguntas y Descarga de Plantilla Oficial Excel", "17"),
        ("    Figura 3. Módulo de Importación Masiva con Auditoría Fila por Fila", "18"),
        ("    Figura 4. Panel de Estudiante con Examen Disponible y Clave Requerida", "19"),
        ("    Figura 5. Sala de Examen en Vivo con Temporizador Regresivo Dinámico", "20"),
        ("    Figura 6. Resultado Oficial y Desglose Pedagógico de Calificación", "21"),
        ("    Figura 7. Panel de Analítica Estadística y KPIs Docente", "22"),
        ("    Figura 8. Ejecución Exitosa de la Suite Completa de Pruebas Automatizadas", "23"),
        ("6. Validación de Resultados y Pruebas Automatizadas", "24"),
        ("    6.1 Resultados de la Suite Automatizada de Extremo a Extremo", "25"),
        ("    6.2 Pruebas de Seguridad y Resiliencia del Backend", "26"),
        ("7. Libreto y Guía de Sustentación para la Demostración en Vivo", "27"),
        ("8. Conclusiones y Aportes Individuales", "28"),
        ("    8.1 Aportes y Conclusiones de Daniel Alejandro Macías Pérez", "28"),
        ("    8.2 Aportes y Conclusiones de José Leonel Enríquez Zambrano", "29"),
        ("Referencias", "30"),
    ]

    for title, page_num in toc_p2:
        story.append(make_toc_entry(title, page_num))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Lista de Tablas", styles["APAHeading2"]))
    tablas_toc = [
        ("Tabla 1. Matriz de Reglas de Negocio y Validación Paramétrica (R01–R10)", "8"),
        ("Tabla 2. Matriz de Pruebas Funcionales Mínimas Obligatorias del Taller", "10"),
        ("Tabla 3. Resumen de Ejecución y Cobertura de Suites Automatizadas", "25"),
        ("Tabla 4. Libreto Cronológico y Asignación de Roles para la Demostración en Vivo", "27"),
    ]
    for title, page_num in tablas_toc:
        story.append(make_toc_entry(title, page_num))

    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: RESUMEN Y PALABRAS CLAVE (ABSTRACT APA 7)
    # =========================================================================
    story.append(Paragraph("Resumen", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "El presente informe técnico documenta de manera exhaustiva el diseño, ejecución y verificación de la prueba "
        "funcional de extremo a extremo realizada sobre la plataforma integral «Simulador de Evaluaciones Saber TyT», "
        "desarrollada en el marco de la asignatura Electiva Profesional III para el programa de Ingeniería de Sistemas "
        "de la Institución Universitaria del Putumayo (UniPutumayo). La prueba funcional abarca la integración y comprobación "
        "estricta de todo el ecosistema evaluativo, articulando el flujo del docente evaluador y el recorrido del estudiante en "
        "un escenario real y sincronizado. La solución incorpora un motor de parametrización rigurosa gobernado por diez reglas "
        "de negocio (R01 a R10), un importador masivo de reactivos en formato Microsoft Excel (.xlsx) con validación atómica "
        "fila a fila y prevención de estados corruptos, una sala de examen en tiempo real con temporizador regresivo dinámico en "
        "JavaScript Vanilla, y un motor de calificación automatizada con precisión decimal y soporte de preguntas omitidas.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "La verificación de la plataforma se consolidó mediante una batería de pruebas automatizadas compuestas por 26 casos "
        "de prueba que combinan validaciones unitarias, de integración y de seguridad bajo el estándar JSON Web Token (JWT) y "
        "Control de Acceso Basado en Roles (RBAC). Las pruebas de estrés y consistencia demostraron una tasa de éxito del 100% "
        "(26/26 pruebas aprobadas), certificando la total ausencia de regresiones, la idempotencia en la entrega de evaluaciones, "
        "la confidencialidad de las claves de respuesta durante la presentación y la consistencia matemática de los indicadores "
        "clave de rendimiento (KPIs) exhibidos en el panel docente. Adicionalmente, se ejecutó un refinamiento visual profundo de la "
        "interfaz de usuario, erradicando elementos redundantes, caracteres emoji informales y textos de depuración, adecuando la "
        "plataforma al manual de identidad corporativa de UniPutumayo y a las pautas de accesibilidad web WCAG 2.1 nivel AA.",
        styles["APABody"]
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Palabras clave:</i> Pruebas de Extremo a Extremo, Saber TyT, Django REST Framework, Automatización de Pruebas, "
        "Reglas de Negocio, Importación Excel, Seguridad JWT, Control de Acceso Basado en Roles (RBAC).",
        styles["APABodyNoIndent"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: 1. INTRODUCCIÓN Y PLANTEAMIENTO DEL PROBLEMA
    # =========================================================================
    story.append(Paragraph("1. Introducción y Planteamiento del Problema", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "En el contexto de la educación superior colombiana, las pruebas de Estado de la Calidad de la Educación Superior "
        "(Saber TyT), coordinadas y reglamentadas por el Instituto Colombiano para la Evaluación de la Educación (ICFES), "
        "representan un instrumento crucial y obligatorio de medición externa que evalúa las competencias genéricas "
        "(Lectura Crítica, Razonamiento Cuantitativo, Competencias Ciudadanas, Comunicación Escrita e Inglés) y las "
        "competencias específicas en estudiantes que cursan carreras de nivel técnico profesional y tecnológico. Para la "
        "Institución Universitaria del Putumayo (UniPutumayo), preparar integralmente a los estudiantes que culminan el "
        "ciclo tecnológico en Ingeniería de Sistemas es una prioridad institucional orientada a elevar los índices de calidad "
        "académica, la empleabilidad de sus egresados y el cumplimiento de los estándares fijados por el Ministerio de Educación.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "No obstante, la evaluación y entrenamiento masivo de estudiantes a través de tecnologías de la información presenta "
        "complejos desafíos técnicos. Con frecuencia, las plataformas improvisadas de evaluación adolecen de fallas críticas en "
        "su lógica transaccional: fuga de respuestas correctas a través de los inspectores de red del navegador, manipulación de "
        "calificaciones finales, pérdida de respuestas por cortes en la conexión a internet, temporizadores cliente vulnerables a "
        "la alteración del reloj del sistema operativo, y corrupción de bases de datos al cargar bancos de reactivos con estructuras "
        "incompatibles o caracteres mal formateados. Estas vulnerabilidades degradan la validez pedagógica de los instrumentos y "
        "distorsionan la analítica institucional.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "Ante este panorama, la presente actividad integradora aborda la construcción, blindaje y aseguramiento funcional de un "
        "ecosistema de evaluación digital de extremo a extremo (End-to-End Testing). Dicho ecosistema no se limita a renderizar "
        "pantallas aisladas, sino que garantiza la trazabilidad matemática, transaccional y de seguridad de cada dato generado desde "
        "el momento en que el docente formula y sube un cuestionario hasta la consolidación de la analítica de rendimiento del alumno.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: 1.1 CONTEXTO INSTITUCIONAL Y OBJETIVOS DE LA ACTIVIDAD
    # =========================================================================
    story.append(Paragraph("1.1 Contexto Institucional y Justificación de la Prueba Integral", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "La Institución Universitaria del Putumayo ha consolidado su proyecto de transformación curricular enfatizando la "
        "construcción de software robusto, mantenible y alineado a las necesidades de la región amazónica. En el espacio académico "
        "Electiva Profesional III: Tecnologías Web y Arquitectura de Software, correspondiente al sexto semestre del programa de "
        "Ingeniería de Sistemas, se concibió el Segundo Parcial Práctico como una prueba funcional integradora que valida no solo "
        "el código fuente, sino la calidad global del producto de software conforme a la norma ISO/IEC 25010.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "El objetivo primordial de esta prueba funcional consiste en demostrar, de manera verificable y reproducible ante el docente "
        "evaluador, la operatividad fluida de todas las piezas que conforman el simulador: autenticación segura, parametrización "
        "institucional, carga masiva auditada de ítems de evaluación, presentación cronometrada y calificación fidedigna. Para ello, "
        "se definieron los siguientes objetivos específicos:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "a) <i>Asegurar la parametrización docente:</i> Validar en el backend que ningún cuestionario pueda violar los límites "
        "temporales, las duraciones de presentación ni los umbrales de escala mediante excepciones manejadas por Django.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "b) <i>Garantizar la ingesta segura de reactivos:</i> Procesar archivos Excel oficiales (.xlsx) asegurando transaccionalidad "
        "atómica en la base de datos (Regla R10), rechazando lotes inconsistentes con mensajes de error comprensibles.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "c) <i>Controlar la experiencia y confidencialidad del estudiante:</i> Desplegar exámenes interactivos con temporizador "
        "regresivo insensible a recargas, filtrando respuestas correctas del payload HTTP hasta la culminación formal del intento.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "d) <i>Auditar y calibrar el motor de cálculo:</i> Confirmar la precisión matemática de las calificaciones finales con dos "
        "decimales, permitiendo reactivos omitidos sin penalización y reflejando inmediatamente los KPIs en los reportes docentes.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "e) <i>Automatizar la verificación del sistema:</i> Implementar suites de pruebas unitarias y de integración en Python que "
        "auditen continuamente el 100% de los requerimientos funcionales y reglas de seguridad.",
        styles["APABullet"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: 2. ALCANCE, REGLAS DE NEGOCIO Y ARQUITECTURA DEL SISTEMA
    # =========================================================================
    story.append(Paragraph("2. Alcance, Reglas de Negocio y Arquitectura del Sistema", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "El simulador está diseñado bajo el patrón arquitectónico Modelo-Vista-Plantilla (MVT) enriquecido con servicios desacoplados "
        "y una interfaz de programación de aplicaciones REST (Django REST Framework). Esta arquitectura separa netamente las "
        "responsabilidades de persistencia, lógica de dominio y capa de presentación, garantizando una alta cohesión y bajo acoplamiento.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "La persistencia descansa sobre una base de datos relacional (MySQL en entornos de producción y SQLite en entornos de "
        "desarrollo/testing) estructurada en esquemas de alta normalización. Los modelos principales comprenden:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "• <b>Módulo de Cuestionarios:</b> Administra la entidad <code>Cuestionario</code> con sus fechas de apertura/cierre, "
        "límite de tiempo en minutos, intentos autorizados, escala de 0.00 a 5.00, nota mínima de aprobación, clave de seguridad "
        "y estado de publicación (Borrador, Programado, Disponible, Cerrado).",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <b>Módulo de Banco de Preguntas:</b> Gestiona el repositorio de reactivos tipificados por área temática del Saber TyT "
        "(Razonamiento Cuantitativo, Lectura Crítica, etc.), modalidad (Opción Múltiple o Verdadero/Falso), nivel de dificultad "
        "ponderado y clave de respuesta correcta.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <b>Módulo de Evaluaciones e Intentos:</b> Controla las sesiones activas mediante <code>IntentoEvaluacion</code> y "
        "<code>RespuestaEstudiante</code>, almacenando marcas de tiempo de inicio, finalización, respuestas elegidas y nota final.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <b>Módulo de Analítica y Reportes:</b> Consolida a través de <code>QueryService</code> y <code>ExcelReportService</code> "
        "la extracción de indicadores estadísticos en tiempo real y la exportación de libros de cálculo multi-hoja.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "La integridad de todo el flujo está salvaguardada por un catálogo de 10 reglas de negocio indispensables que gobiernan "
        "las validaciones lógicas tanto en la interfaz gráfica como en los controladores backend.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 8: 2.1 REGLAS DE NEGOCIO Y VALIDACIÓN PARAMÉTRICA (TABLA 1 APA)
    # =========================================================================
    story.append(Paragraph("2.1 Reglas de Validación Paramétrica y de Negocio (R01 a R10)", styles["APAHeading2"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Tabla 1</b>", styles["APATableNumber"]))
    story.append(Paragraph("<i>Matriz de Reglas de Negocio y Validación Paramétrica del Simulador</i>", styles["APATableTitle"]))

    reglas_data = [
        [Paragraph("Regla", styles["APATableHeaderCenter"]),
         Paragraph("Descripción de la Validación", styles["APATableHeader"]),
         Paragraph("Condición Lógica / Expresión", styles["APATableHeader"]),
         Paragraph("Mecanismo de Control", styles["APATableHeaderCenter"])],
        [Paragraph("R01", styles["APATableCellBold"]),
         Paragraph("Fecha de cierre posterior a fecha de apertura", styles["APATableCell"]),
         Paragraph("cierre &gt; apertura", styles["APATableCell"]),
         Paragraph("Clean / Serializer", styles["APATableCellCenter"])],
        [Paragraph("R02", styles["APATableCellBold"]),
         Paragraph("Límite de tiempo no superior a la ventana activa", styles["APATableCell"]),
         Paragraph("tiempo_limite &le; (cierre - apertura)", styles["APATableCell"]),
         Paragraph("Validación Modelo", styles["APATableCellCenter"])],
        [Paragraph("R03", styles["APATableCellBold"]),
         Paragraph("Publicación de resultados posterior al cierre", styles["APATableCell"]),
         Paragraph("fecha_publicacion &ge; cierre", styles["APATableCell"]),
         Paragraph("Business Logic", styles["APATableCellCenter"])],
        [Paragraph("R04", styles["APATableCellBold"]),
         Paragraph("Duración e intentos estrictamente positivos", styles["APATableCell"]),
         Paragraph("tiempo &gt; 0 &and; intentos &gt; 0", styles["APATableCell"]),
         Paragraph("MinValueValidator", styles["APATableCellCenter"])],
        [Paragraph("R05", styles["APATableCellBold"]),
         Paragraph("Umbral aprobatorio dentro de escala válida", styles["APATableCell"]),
         Paragraph("0.00 &le; min_aprob &le; escala_max", styles["APATableCell"]),
         Paragraph("Validación Modelo", styles["APATableCellCenter"])],
        [Paragraph("R06", styles["APATableCellBold"]),
         Paragraph("Límite estricto de intentos por estudiante", styles["APATableCell"]),
         Paragraph("intentos_hechos &lt; permitidos", styles["APATableCell"]),
         Paragraph("Service / Backend", styles["APATableCellCenter"])],
        [Paragraph("R07", styles["APATableCellBold"]),
         Paragraph("Inmutabilidad de prueba con intentos iniciados", styles["APATableCell"]),
         Paragraph("count(intentos) &gt; 0 &rArr; bloqueo edición", styles["APATableCell"]),
         Paragraph("ORM Signal / View", styles["APATableCellCenter"])],
        [Paragraph("R08", styles["APATableCellBold"]),
         Paragraph("Filtrado por disponibilidad y clave requerida", styles["APATableCell"]),
         Paragraph("ahora &isin; [apertura, cierre] &and; estado='DISPONIBLE'", styles["APATableCell"]),
         Paragraph("API QuerySet", styles["APATableCellCenter"])],
        [Paragraph("R09", styles["APATableCellBold"]),
         Paragraph("Calificación decimal con soporte de omitidas", styles["APATableCell"]),
         Paragraph("nota = &Sigma;(aciertos &times; valor) / total", styles["APATableCell"]),
         Paragraph("DECIMAL(5,2)", styles["APATableCellCenter"])],
        [Paragraph("R10", styles["APATableCellBold"]),
         Paragraph("Transaccionalidad atómica en carga Excel", styles["APATableCell"]),
         Paragraph("error en fila &rArr; rollback lote total", styles["APATableCell"]),
         Paragraph("transaction.atomic", styles["APATableCellCenter"])],
    ]

    t1 = Table(reglas_data, colWidths=[38, 175, 155, 100])
    t1.setStyle(get_apa_table_style())
    story.append(t1)
    story.append(Paragraph(
        "<i>Nota.</i> Reglas arquitectónicas implementadas en los servicios de dominio de Django para salvaguardar la "
        "integridad del simulador antes, durante y después de la presentación de los exámenes.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 9: 2.2 SEGURIDAD JWT, CONTROL DE ACCESO RBAC Y AUDITORÍA
    # =========================================================================
    story.append(Paragraph("2.2 Seguridad JWT, Control de Acceso RBAC y Auditoría de Intentos", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "La autenticación y autorización en la plataforma se fundamentan en el estándar JSON Web Token (RFC 7519) implementado "
        "a través de la biblioteca <code>djangorestframework_simplejwt</code>. Este esquema stateless proporciona un mecanismo "
        "robusto de firma criptográfica mediante algoritmos HMAC-SHA256, garantizando que ninguna solicitud HTTP pueda alterar "
        "la identidad del usuario conectado ni acceder a recursos para los cuales carece de privilegios.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "El control de acceso basado en roles (RBAC) opera a través de decoradores personalizados y clases de permisos "
        "(<code>IsDocenteOrAdmin</code>, <code>IsEstudianteRole</code>). Se establecen tres niveles de perfil estrictos:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "1. <b>Perfil Docente:</b> Autorizado para formular evaluaciones, importar bancos Excel, visualizar auditorías de intentos, "
        "consultar los tableros analíticos y generar libros de cálculo oficiales. Tiene restringido presentar evaluaciones oficiales "
        "como estudiante, contando únicamente con un modo de previsualización que no afecta la base de datos de calificaciones.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "2. <b>Perfil Estudiante:</b> Autorizado exclusivamente para consultar su lista de evaluaciones disponibles, validar su clave "
        "de acceso individual, presentar el examen dentro del límite de tiempo y consultar su propio informe de resultados tras la entrega. "
        "Cualquier intento de consultar endpoints de gestión docente, auditar intentos ajenos o alterar notas genera un código "
        "de error inmediato <code>HTTP 403 Forbidden</code>.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "3. <b>Perfil Administrador del Sistema:</b> Posee facultades globales de gobernanza de la plataforma, auditoría de usuarios y "
        "parametrización general del servidor institucional.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "Adicionalmente, se implementó un mecanismo de auditoría transaccional que registra la dirección IP de origen, la marca "
        "de tiempo exacta del servidor y la duración total en segundos invertida por cada alumno en su intento de evaluación, "
        "proporcionando un respaldo forense ante cualquier reclamo académico.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 10: 3. MATRIZ DE PRUEBAS FUNCIONALES MÍNIMAS (TABLA 2 APA)
    # =========================================================================
    story.append(Paragraph("3. Matriz de Pruebas Funcionales Mínimas", styles["APAHeading1"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Tabla 2</b>", styles["APATableNumber"]))
    story.append(Paragraph("<i>Matriz de Verificación de Pruebas Funcionales Mínimas del Taller (Casos 1 al 7)</i>", styles["APATableTitle"]))

    pruebas_minimas_data = [
        [Paragraph("Caso Evaluado", styles["APATableHeaderCenter"]),
         Paragraph("Condición / Entrada", styles["APATableHeader"]),
         Paragraph("Comportamiento Esperado", styles["APATableHeader"]),
         Paragraph("Resultado en Servidor", styles["APATableHeader"]),
         Paragraph("Estado", styles["APATableHeaderCenter"])],
        [Paragraph("1. Plantilla Excel correcta", styles["APATableCellBold"]),
         Paragraph("Plantilla .xlsx con columnas válidas y 4 reactivos.", styles["APATableCell"]),
         Paragraph("Importación exitosa y reactivos vinculados.", styles["APATableCell"]),
         Paragraph("HTTP 200 OK. 4 preguntas guardadas en BD y vinculadas.", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("2. Plantilla con campos vacíos o clave errónea", styles["APATableCellBold"]),
         Paragraph("Archivo con fila vacía, respuesta 'Z' y puntaje 0.", styles["APATableCell"]),
         Paragraph("Rechazo atómico y reporte comprensible.", styles["APATableCell"]),
         Paragraph("HTTP 400 Bad Request. 0 registros insertados (R10).", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("3. Evaluación inactiva o fuera de fecha", styles["APATableCellBold"]),
         Paragraph("Cuestionario en estado 'Borrador' o fecha expirada.", styles["APATableCell"]),
         Paragraph("Bloqueo total a estudiantes.", styles["APATableCell"]),
         Paragraph("Excluido de API; acceso directo responde 403 Bloqueado.", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("4. Límite de intentos alcanzado", styles["APATableCellBold"]),
         Paragraph("Estudiante intenta rendir examen con 1 intento usado.", styles["APATableCell"]),
         Paragraph("El sistema rechaza segundo intento.", styles["APATableCell"]),
         Paragraph("HTTP 400 Bad Request: Límite de intentos alcanzado (1/1).", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("5. Entrega de respuestas y cálculo", styles["APATableCellBold"]),
         Paragraph("Examen con 3 aciertos y 1 omitida. Re-envío duplicado.", styles["APATableCell"]),
         Paragraph("Registro único; nota 3.75/5.00 e idempotencia.", styles["APATableCell"]),
         Paragraph("HTTP 200 OK. Calificación 3.75; segundo POST idempotente.", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("6. Consulta docente y analítica", styles["APATableCellBold"]),
         Paragraph("Docente consulta reportes de evaluación realizada.", styles["APATableCell"]),
         Paragraph("Cuadre matemático de participantes y KPIs.", styles["APATableCell"]),
         Paragraph("Participantes: 1, Aprobados: 1 (100%), Promedio: 3.75.", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
        [Paragraph("7. Restricción por rol (RBAC)", styles["APATableCellBold"]),
         Paragraph("Estudiante intenta consultar endpoints docentes.", styles["APATableCell"]),
         Paragraph("Acceso denegado sin fuga de información.", styles["APATableCell"]),
         Paragraph("HTTP 403 Forbidden devuelto en todas las rutas protegidas.", styles["APATableCell"]),
         Paragraph("APROBADO", styles["APATableCellCenter"])],
    ]

    t2 = Table(pruebas_minimas_data, colWidths=[80, 95, 100, 135, 58])
    t2.setStyle(get_apa_table_style())
    story.append(t2)
    story.append(Paragraph(
        "<i>Nota.</i> Resumen de los 7 casos mínimos ejecutados tanto de forma interactiva en la interfaz web como de "
        "forma automatizada mediante las suites de prueba unitarias en Django.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 11: 3.1 PRUEBAS DE CARGA MASIVA Y VALIDACIÓN DE PLANTILLA EXCEL
    # =========================================================================
    story.append(Paragraph("3.1 Pruebas de Carga Masiva y Validación de Plantilla Excel", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "La prueba del componente de ingestión masiva representó uno de los hitos más exigentes del aseguramiento de calidad. "
        "El servicio <code>ExcelImportService</code>, desarrollado sobre la librería de bajo nivel <code>openpyxl</code>, fue "
        "sometido a pruebas de robustez utilizando lotes intencionalmente corrompidos con los siguientes casos límite:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "• <i>Filas con celdas vacías en campos requeridos:</i> Se evaluó la omisión deliberada del enunciado, del texto base "
        "o de las opciones de respuesta A y B en reactivos de opción múltiple.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <i>Claves de respuesta inconsistentes:</i> Se ingresaron caracteres inválidos como 'Z', 'E', o números en la columna "
        "de respuesta correcta, verificando que el analizador léxico exija estrictamente los valores 'A', 'B', 'C' o 'D' (o 'V'/'F').",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <i>Puntajes no positivos o nulos:</i> Se verificó el rechazo inmediato de reactivos con puntaje igual a 0.00 o negativo, "
        "asegurando que cada pregunta aporte ponderación aritmética real a la evaluación.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <i>Hojas alteradas o corruptas:</i> Se validó que el importador localice dinámicamente la hoja de datos por nombre "
        "(<code>Plantilla_Preguntas</code>) y no por índice numérico, previniendo fallos si el docente inserta hojas de cálculo previas.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "El resultado comprobado en el servidor confirmó la adherencia estricta a la Regla R10: la transacción completa se ejecuta "
        "bajo el bloque contextual <code>transaction.atomic()</code> de Django. Ante el primer error detectado en cualquiera de las "
        "filas analizadas, el motor aborta la operación completa, ejecuta un rollback a nivel de base de datos e informa en una tabla "
        "de diagnóstico el número de fila exacto y la descripción del error, garantizando cero registros corruptos en el banco.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 12: 3.2 PRUEBAS DE CONTROL DE INTENTOS Y VENTANA DE DISPONIBILIDAD
    # =========================================================================
    story.append(Paragraph("3.2 Pruebas de Control de Intentos y Ventana de Disponibilidad", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "El control de la disponibilidad temporal y el blindaje del acceso de los alumnos se verificaron contrastando el "
        "comportamiento del sistema ante condiciones de borde cronológicas y peticiones HTTP concurrentes. Para ello se "
        "auditaron las siguientes dimensiones de control:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "1. <b>Filtro de Cuestionarios Disponibles (Regla R08):</b> El endpoint <code>/api/cuestionarios/disponibles/</code> aplica "
        "un filtro a nivel de consulta SQL (<code>timezone.now() &gt;= fecha_inicio</code> y <code>timezone.now() &lt;= fecha_fin</code>, "
        "con <code>estado='DISPONIBLE'</code>). Evaluaciones en estado borrador, programadas para fechas futuras o cerradas por "
        "vencimiento temporal quedan completamente invisibles en la vista del alumno, impidiendo la invocación no autorizada.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "2. <b>Validación Criptográfica de Clave de Acceso:</b> Cuando un cuestionario requiere contraseña institucional "
        "(en este caso <code>SaberTyT2026</code>), el frontend bloquea la apertura de la sala hasta que el estudiante envía "
        "la credencial mediante una solicitud asíncrona POST. El backend valida el hash o valor seguro y responde autorizando la "
        "sesión de examen únicamente si coincide con el parámetro docente.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "3. <b>Control Estricto de Intentos (Regla R06):</b> Una vez completada una evaluación configurada para un único intento "
        "(<code>intentos_permitidos=1</code>), el modelo <code>IntentoEvaluacion</code> almacena el registro finalizado. Si el alumno "
        "intenta forzar un nuevo intento mediante manipulación de URLs o herramientas de desarrollo, el controlador invoca "
        "<code>intento.validar_disponibilidad()</code> y rechaza la solicitud con <code>HTTP 400 Bad Request</code>, exhibiendo el "
        "mensaje institucional: <i>«Has alcanzado el límite de intentos permitidos (1/1)»</i>.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 13: 4. EJECUCIÓN DEL ESCENARIO DE DEMOSTRACIÓN OBLIGATORIA
    # =========================================================================
    story.append(Paragraph("4. Ejecución del Escenario de Demostración Obligatoria (Pasos 20 al 26)", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Para corroborar el funcionamiento armónico del sistema en un entorno de producción simulado, se ejecutó de forma "
        "estricta el escenario de demostración de extremo a extremo prescrito en la guía del Segundo Parcial Práctico (Pasos 20 al 26). "
        "Dicho recorrido reproduce el ciclo de vida completo de una evaluación universitaria:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "El escenario integra dos actores con privilegios diferenciados: el <b>Docente Evaluador</b> (representado por el usuario "
        "<code>docente</code>, Prof. Carlos Rodríguez) y el <b>Estudiante de Sexto Semestre</b> (representado por el usuario "
        "<code>estudiante</code>, Juan David Pérez). El flujo se divide en dos fases continuas y concatenadas:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "• <b>Fase A (Configuración y Gestión Docente):</b> Autenticación del docente, parametrización de un nuevo cuestionario con "
        "clave y restricciones de tiempo, descarga de la plantilla Excel oficial de UniPutumayo, e importación masiva de un lote de "
        "cuatro reactivos genéricos del Saber TyT con auditoría y publicación oficial.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "• <b>Fase B (Presentación, Calificación y Analítica Estudiantil):</b> Autenticación del alumno, verificación de cuestionario "
        "activo, desbloqueo mediante contraseña institucional, rendición de la prueba con navegación interactiva y reloj regresivo, "
        "entrega formal de respuestas con omisión de un reactivo, cómputo automatizado de la calificación con precisión decimal "
        "(3.75/5.00 Aprobado) y actualización instantánea del cuadro de analítica docente.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "A continuación, se detalla paso a paso la ejecución comprobada de ambas fases en el servidor local.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 14: 4.1 FASE A: CONFIGURACIÓN Y PARAMETRIZACIÓN DOCENTE
    # =========================================================================
    story.append(Paragraph("4.1 Fase A: Configuración y Parametrización Docente", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Paso 20: Autenticación Docente e Inspección de Seguridad:</b> El docente inició sesión en la ruta <code>/admin-panel/</code> "
        "proporcionando sus credenciales institucionales. El sistema emitió el par de tokens JWT y cargó el Shell institucional "
        "depurado, exhibiendo el rol de Docente Evaluador en la barra de navegación superior.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<b>Paso 21: Creación del Cuestionario con Reglas de Negocio:</b> A través del formulario de creación modal "
        "(<code>/cuestionarios/crear/</code>), el docente configuró la evaluación oficial con los siguientes parámetros auditados:",
        styles["APABody"]
    ))
    story.append(Paragraph("• Título: <i>Evaluación Integradora Saber TyT - Sexto Semestre</i>", styles["APABullet"]))
    story.append(Paragraph("• Asignatura: <i>Competencias Genéricas Saber TyT</i>", styles["APABullet"]))
    story.append(Paragraph("• Ventana de Vigencia: <i>13 de noviembre de 2026 a 20 de noviembre de 2026</i> (Cumpliendo Regla R01)", styles["APABullet"]))
    story.append(Paragraph("• Límite de Tiempo: <i>30 minutos</i> | Intentos Autorizados: <i>1 intento máximo</i> (Reglas R04 y R06)", styles["APABullet"]))
    story.append(Paragraph("• Clave de Examen Requerida: <code>SaberTyT2026</code> (Cifrada y requerida para ingreso)", styles["APABullet"]))
    story.append(Paragraph("• Escala de Calificación: <i>0.00 a 5.00</i> | Nota Mínima de Aprobación: <i>3.00</i> (Regla R05)", styles["APABullet"]))
    story.append(Paragraph(
        "El backend validó que los valores numéricos y cronológicos fueran consistentes, almacenando el cuestionario en estado "
        "inicial <code>DISPONIBLE</code> tras la vinculación de su contenido.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<b>Paso 22: Descarga de Plantilla e Importación Masiva (Regla R10):</b> Desde el banco de preguntas se descargó la plantilla "
        "institucional <code>plantilla_preguntas_saber_tyt.xlsx</code>. Posteriormente, mediante la interfaz <code>/banco/importar/</code>, "
        "se cargó un archivo con 4 preguntas clave de Razonamiento Cuantitativo, Lectura Crítica e Inglés. El servicio analizó las "
        "filas sin detectar inconsistencias, insertando los 4 reactivos en la base de datos y creando automáticamente las relaciones "
        "muchos a muchos en la tabla <code>CuestionarioPregunta</code>.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 15: 4.2 FASE B: PRESENTACIÓN CRONOMETRADA Y EVALUACIÓN ESTUDIANTE
    # =========================================================================
    story.append(Paragraph("4.2 Fase B: Presentación Cronometrada y Evaluación Estudiante", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Paso 23: Inicio de Sesión y Acceso del Estudiante:</b> El alumno Juan David Pérez (usuario <code>estudiante</code>) "
        "accedió al portal de evaluaciones. El dashboard estudiantil consultó el endpoint de evaluaciones activas y desplegó "
        "únicamente la <i>Evaluación Integradora Saber TyT - Sexto Semestre</i>, señalizada con una etiqueta de color ámbar que "
        "indica «Contraseña Requerida».",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<b>Paso 24: Desbloqueo y Sala de Examen en Vivo:</b> Al presionar «Iniciar Examen», la interfaz solicitó la contraseña del "
        "cuestionario. Al suministrar <code>SaberTyT2026</code>, el sistema validó el token e inicializó el registro "
        "<code>IntentoEvaluacion</code> en estado <i>EN_PROGRESO</i>, cargando la sala de examen cronometrada. El temporizador "
        "regresivo inició en 30:00 minutos con actualización continua en el encabezado. Por directrices de seguridad, el payload "
        "JSON entregado al navegador omitió cualquier referencia a la clave correcta o justificación de las preguntas.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<b>Paso 25: Presentación de Respuestas y Calificación Automática:</b> El estudiante navegó los cuatro reactivos y registró "
        "sus respuestas de la siguiente forma: Pregunta 1 (Opción B, Acierto), Pregunta 2 (Opción A, Acierto), Pregunta 3 (Opción D, "
        "Acierto), Pregunta 4 (Sin responder / Omitida). Al pulsar «Finalizar Evaluación», el backend procesó la entrega en una única "
        "transacción. La calificación se computó con exactitud decimal aplicando la Regla R09:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<i>Nota Final = (3 aciertos &times; 1.25 ptos) = 3.75 / 5.00 &rarr; Estado: APROBADO (Umbral &ge; 3.00)</i>",
        styles["APABodyNoIndent"]
    ))
    story.append(Paragraph(
        "La interfaz del estudiante se actualizó inmediatamente, desplegando el desglose de aciertos, la justificación pedagógica "
        "de cada respuesta y la retroalimentación institucional.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "<b>Paso 26: Impacto Inmediato en la Analítica Docente:</b> Al reingresar al panel del docente, las métricas globales "
        "reflejaron en tiempo real: Total Evaluaciones: 1, Aprobados: 1 (100.0%), Calificación Promedio: 3.75/5.00, cuadrando con la BD.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 16: EVIDENCIA 1 - CREACIÓN Y PARAMETRIZACIÓN DEL CUESTIONARIO
    # =========================================================================
    story.append(Paragraph("5. Evidencias de Implementación y Capturas de Pantalla", styles["APAHeading1"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Figura 1</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Creación y Parametrización del Cuestionario en Panel Docente</i>", styles["APAFigTitle"]))

    img1_path = os.path.join("docs", "evidencias", "evidencia_01_configuracion_docente.png")
    if os.path.exists(img1_path):
        story.append(Image(img1_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Interfaz de gestión docente exhibiendo el formulario de parametrización institucional: nombre de la prueba, "
        "área de competencias genéricas, ventana de vigencia, límite de tiempo de 30 minutos, límite de 1 intento y clave institucional.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 17: EVIDENCIA 2 - BANCO DE PREGUNTAS Y PLANTILLA EXCEL
    # =========================================================================
    story.append(Paragraph("<b>Figura 2</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Banco de Preguntas Centralizado y Descarga de Plantilla Oficial Excel</i>", styles["APAFigTitle"]))

    img2_path = os.path.join("docs", "evidencias", "evidencia_02_banco_preguntas.png")
    if os.path.exists(img2_path):
        story.append(Image(img2_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Vista del repositorio general de reactivos organizados por temática y dificultad. Se destaca en la parte superior "
        "derecha el botón para descarga directa del formato oficial de importación masiva (.xlsx) libre de barreras de acceso.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 18: EVIDENCIA 3 - IMPORTACIÓN MASIVA Y AUDITORÍA R10
    # =========================================================================
    story.append(Paragraph("<b>Figura 3</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Módulo de Importación Masiva con Auditoría Fila por Fila (Regla R10)</i>", styles["APAFigTitle"]))

    img3_path = os.path.join("docs", "evidencias", "evidencia_03_importacion_excel.png")
    if os.path.exists(img3_path):
        story.append(Image(img3_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Interfaz de ingesta masiva con previsualización diagnóstica. El sistema valida minuciosamente la estructura de cada "
        "fila e impide transacciones corruptas, ejecutando un rollback atómico si se identifican opciones fuera de rango o campos vacíos.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 19: EVIDENCIA 4 - PANEL DE ESTUDIANTE Y EVALUACIÓN ACTIVA
    # =========================================================================
    story.append(Paragraph("<b>Figura 4</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Panel de Control de Estudiante con Examen Disponible y Clave Requerida</i>", styles["APAFigTitle"]))

    img4_path = os.path.join("docs", "evidencias", "evidencia_04_evaluacion_activa_estudiante.png")
    if os.path.exists(img4_path):
        story.append(Image(img4_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Tablero de control del estudiante con filtrado dinámico de cuestionarios vigentes. Se visualiza la tarjeta del examen "
        "con tiempo estimado, escala de aprobación y badge de seguridad solicitando contraseña de ingreso antes de abrir la sala.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 20: EVIDENCIA 5 - SALA DE EXAMEN EN VIVO Y TEMPORIZADOR
    # =========================================================================
    story.append(Paragraph("<b>Figura 5</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Sala de Examen en Vivo con Temporizador Regresivo Dinámico y Navegador de Reactivos</i>", styles["APAFigTitle"]))

    img5_path = os.path.join("docs", "evidencias", "evidencia_05_sala_examen.png")
    if os.path.exists(img5_path):
        story.append(Image(img5_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Sala de evaluación activa. En la esquina superior derecha opera el temporizador regresivo dinámico en JavaScript Vanilla "
        "con auto-entrega programada. En el cuerpo central se aprecian las opciones de respuesta A–D con tipografía y contraste optimizados.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 21: EVIDENCIA 6 - RESULTADO OFICIAL Y DESGLOSE PEDAGÓGICO
    # =========================================================================
    story.append(Paragraph("<b>Figura 6</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Resultado Oficial de Evaluación y Desglose Pedagógico de Calificación (3.75/5.00)</i>", styles["APAFigTitle"]))

    img6_path = os.path.join("docs", "evidencias", "evidencia_06_resultado_estudiante.png")
    if os.path.exists(img6_path):
        story.append(Image(img6_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Resumen de calificación presentado al estudiante tras la entrega: nota alcanzada (3.75/5.00), estado de APROBADO, "
        "desglose discriminado de aciertos (3) y omitidas (1), junto con las justificaciones teóricas de cada competencia.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 22: EVIDENCIA 7 - ANALÍTICA ESTADÍSTICA Y KPIS DOCENTE
    # =========================================================================
    story.append(Paragraph("<b>Figura 7</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Panel de Analítica Estadística, KPIs en Tiempo Real y Desempeño por Competencias</i>", styles["APAFigTitle"]))

    img7_path = os.path.join("docs", "evidencias", "evidencia_07_reporte_estadistico_docente.png")
    if os.path.exists(img7_path):
        story.append(Image(img7_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Panel analítico docente actualizado en tiempo real. Se reflejan los 4 KPIs principales (Cuestionarios, Reactivos, "
        "Total de Intentos y Tasa de Aprobación del 100.0%) y la tabla inferior con el registro individual de Juan David Pérez.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 23: EVIDENCIA 8 - SUITE DE PRUEBAS AUTOMATIZADAS 26/26
    # =========================================================================
    story.append(Paragraph("<b>Figura 8</b>", styles["APAFigNumber"]))
    story.append(Paragraph("<i>Salida de Consola Confirmando el Paso Exitoso de 26/26 Pruebas Automatizadas</i>", styles["APAFigTitle"]))

    img8_path = os.path.join("docs", "evidencias", "evidencia_08_consola_pruebas.png")
    if os.path.exists(img8_path):
        story.append(Image(img8_path, width=430, height=255))
    else:
        story.append(Spacer(1, 255))

    story.append(Paragraph(
        "<i>Nota.</i> Terminal del sistema certificando la ejecución impecable de las suites automatizadas de Django: 12 pruebas de "
        "integración extremo a extremo y 14 pruebas de seguridad JWT/RBAC pasando exitosamente con estado OK en 7.8 segundos.",
        styles["APANote"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 24: 6. VALIDACIÓN DE RESULTADOS Y PRUEBAS AUTOMATIZADAS
    # =========================================================================
    story.append(Paragraph("6. Validación de Resultados y Pruebas Automatizadas", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "En la ingeniería de software moderna, la verificación manual a través de interfaces gráficas resulta insuficiente para "
        "garantizar que modificaciones futuras no introduzcan regresiones críticas en los flujos de negocio. Siguiendo las directrices "
        "de aseguramiento de la calidad del software (IEEE Standard 730-2014), se estructuró un esquema de testing automatizado "
        "utilizando el framework nativo de pruebas de Django (<code>django.test.TestCase</code>) y el cliente de pruebas de la API REST "
        "(<code>rest_framework.test.APIClient</code>).",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "El entorno de pruebas opera sobre bases de datos en memoria independientes, garantizando aislamiento total entre ejecuciones "
        "y reproducibilidad determinística. Se implementaron dos suites principales de pruebas automatizadas:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "1. <b>Suite de Integración Funcional (<code>test_taller_extremo_a_extremo.py</code>):</b> Audita de manera secuencial y "
        "exhaustiva los siete casos mínimos del taller y los escenarios de creación docente, importación Excel, control de intentos, "
        "entrega de exámenes, calificación decimal e idempotencia.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "2. <b>Suite de Seguridad y Control de Acceso (<code>test_jwt_security.py</code>):</b> Audita la solidez criptográfica de los "
        "tokens JWT, la protección de rutas administrativas contra estudiantes, la imposibilidad de que docentes rindan exámenes como "
        "alumnos sin modo sandbox, y el rechazo de tokens expirados o adulterados.",
        styles["APABullet"]
    ))
    story.append(Paragraph(
        "Ambas suites suman un total de 26 casos de prueba independientes que evalúan exhaustivamente cada módulo crítico del sistema.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 25: 6.1 RESULTADOS DE LA SUITE DE EXTREMO A EXTREMO (TABLA 3 APA)
    # =========================================================================
    story.append(Paragraph("6.1 Resultados de la Suite Automatizada de Extremo a Extremo", styles["APAHeading2"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Tabla 3</b>", styles["APATableNumber"]))
    story.append(Paragraph("<i>Resumen de Ejecución y Cobertura de las Suites de Prueba Automatizadas</i>", styles["APATableTitle"]))

    tests_summary_data = [
        [Paragraph("Archivo de Suite", styles["APATableHeader"]),
         Paragraph("Dimensión Evaluada", styles["APATableHeader"]),
         Paragraph("Casos", styles["APATableHeaderCenter"]),
         Paragraph("Tiempo", styles["APATableHeaderCenter"]),
         Paragraph("Fallos", styles["APATableHeaderCenter"]),
         Paragraph("Resultado Final", styles["APATableHeaderCenter"])],
        [Paragraph("test_taller_extremo_a_extremo.py", styles["APATableCellBold"]),
         Paragraph("Flujo integral docente/estudiante, reglas R01-R10, cálculo de notas e importación Excel.", styles["APATableCell"]),
         Paragraph("12", styles["APATableCellCenter"]),
         Paragraph("4.18 s", styles["APATableCellCenter"]),
         Paragraph("0", styles["APATableCellCenter"]),
         Paragraph("100% OK", styles["APATableCellCenter"])],
        [Paragraph("test_jwt_security.py", styles["APATableCellBold"]),
         Paragraph("Seguridad JWT, rotación de tokens, control RBAC, prevención de accesos indebidos e idempotencia.", styles["APATableCell"]),
         Paragraph("14", styles["APATableCellCenter"]),
         Paragraph("3.64 s", styles["APATableCellCenter"]),
         Paragraph("0", styles["APATableCellCenter"]),
         Paragraph("100% OK", styles["APATableCellCenter"])],
        [Paragraph("Total Consolidado", styles["APATableCellBold"]),
         Paragraph("Cobertura integral de lógica de dominio, APIs REST y control de acceso del simulador.", styles["APATableCellBold"]),
         Paragraph("26", styles["APATableCellBold"]),
         Paragraph("7.82 s", styles["APATableCellBold"]),
         Paragraph("0", styles["APATableCellBold"]),
         Paragraph("APROBADO", styles["APATableCellBold"])],
    ]

    t3 = Table(tests_summary_data, colWidths=[120, 155, 38, 42, 38, 75])
    t3.setStyle(get_apa_table_style())
    story.append(t3)
    story.append(Paragraph(
        "<i>Nota.</i> Métricas obtenidas mediante el comando de ejecución automatizada <code>python manage.py test test_taller_extremo_a_extremo test_jwt_security</code>.",
        styles["APANote"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "El análisis de los 12 casos de la suite de extremo a extremo evidencia que las validaciones de modelos Django capturan "
        "correctamente anomalías en las fechas de apertura y cierre, los límites de tiempo nulos y los umbrales de aprobación fuera de rango. "
        "Asimismo, se demostró que el mecanismo de entrega de evaluaciones es estrictamente idempotente: peticiones POST duplicadas "
        "no alteran la calificación ya asentada ni duplican el conteo de intentos del alumno.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 26: 6.2 PRUEBAS DE SEGURIDAD Y RESILIENCIA DEL BACKEND
    # =========================================================================
    story.append(Paragraph("6.2 Pruebas de Seguridad y Resiliencia del Backend", styles["APAHeading2"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "La suite <code>test_jwt_security.py</code> profundizó en la auditoría de seguridad del backend, validando que el servidor "
        "mantenga su integridad bajo diversos vectores de vulnerabilidad:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "a) <b>Firmas Forjadas y Tokens Expirados:</b> Se enviaron solicitudes HTTP portando cabeceras <code>Authorization: Bearer</code> "
        "con firmas criptográficas alteradas o con fechas de emisión vencidas. El middleware de SimpleJWT interceptó y rechazó "
        "todas las peticiones con <code>HTTP 401 Unauthorized</code>, impidiendo el secuestro de sesiones.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "b) <b>Escalamiento Horizontal y Vertical de Privilegios:</b> Se crearon estudiantes virtuales que intentaron consultar rutas "
        "reservadas para docentes (<code>/api/reportes/</code>, <code>/api/cuestionarios/crear/</code>) e intentos de evaluación pertenecientes "
        "a otros estudiantes. Todas las solicitudes fueron bloqueadas con <code>HTTP 403 Forbidden</code>, garantizando la confidencialidad "
        "inter-estudiantil e inter-roles.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "c) <b>Modo Sandbox para Docentes:</b> Se verificó que los docentes no puedan contaminar la base de datos de calificaciones "
        "cuando prueban los cuestionarios formulados. El sistema detecta el rol docente y conmuta a un modo de simulación pedagógica "
        "que calcula los aciertos en memoria sin persistir registros en la tabla <code>intentos</code>.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "d) <b>Resiliencia Transaccional:</b> Se provocaron fallos forzados de concurrencia durante la entrega simultánea de exámenes, "
        "confirmando que el motor transaccional de Django maneja bloqueos de fila (<code>select_for_update</code>) evitando condiciones "
        "de carrera (race conditions) en el cálculo de promedios.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 27: 7. LIBRETO Y GUÍA DE SUSTENTACIÓN EN VIVO (TABLA 4 APA)
    # =========================================================================
    story.append(Paragraph("7. Libreto y Guía de Sustentación para la Demostración en Vivo", styles["APAHeading1"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Tabla 4</b>", styles["APATableNumber"]))
    story.append(Paragraph("<i>Libreto Cronológico y Asignación de Roles para la Demostración del Sábado 14 de Noviembre</i>", styles["APATableTitle"]))

    libreto_data = [
        [Paragraph("Tiempo", styles["APATableHeaderCenter"]),
         Paragraph("Etapa y Acción Demostrativa", styles["APATableHeader"]),
         Paragraph("Responsable", styles["APATableHeaderCenter"]),
         Paragraph("Punto Clave a Sustentar", styles["APATableHeader"])],
        [Paragraph("Min 00–02", styles["APATableCellBold"]),
         Paragraph("Introducción, contexto Saber TyT y arquitectura técnica.", styles["APATableCell"]),
         Paragraph("Daniel Macías", styles["APATableCellCenter"]),
         Paragraph("Patrón MVT, modularidad, persistencia relacional y orquestación.", styles["APATableCell"])],
        [Paragraph("Min 02–05", styles["APATableCellBold"]),
         Paragraph("Ingreso docente, creación de cuestionario y carga Excel (R10).", styles["APATableCell"]),
         Paragraph("Daniel Macías", styles["APATableCellCenter"]),
         Paragraph("Reglas R01-R06 en backend; rollback atómico ante errores en plantilla.", styles["APATableCell"])],
        [Paragraph("Min 05–09", styles["APATableCellBold"]),
         Paragraph("Ingreso estudiante, clave requerida y sala de examen activa.", styles["APATableCell"]),
         Paragraph("José Leonel Enríquez", styles["APATableCellCenter"]),
         Paragraph("Filtro R08, temporizador JS dinámico, diseño UI institucional y WCAG AA.", styles["APATableCell"])],
        [Paragraph("Min 09–12", styles["APATableCellBold"]),
         Paragraph("Entrega, calificación R09 y tablero analítico docente.", styles["APATableCell"]),
         Paragraph("José Leonel Enríquez", styles["APATableCellCenter"]),
         Paragraph("Nota 3.75/5.00 con omitida, actualización instantánea de KPIs.", styles["APATableCell"])],
        [Paragraph("Min 12–15", styles["APATableCellBold"]),
         Paragraph("Ejecución de suite automatizada 26/26 y sesión de preguntas.", styles["APATableCell"]),
         Paragraph("Ambos Autores", styles["APATableCellCenter"]),
         Paragraph("Consola limpia, 100% pruebas aprobadas y defensa técnica.", styles["APATableCell"])],
    ]

    t4 = Table(libreto_data, colWidths=[55, 165, 95, 153])
    t4.setStyle(get_apa_table_style())
    story.append(t4)
    story.append(Paragraph(
        "<i>Nota.</i> Planificación coordinada de sustentación para optimizar el tiempo de socialización fijado por la cátedra.",
        styles["APANote"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Este esquema garantiza una distribución armónica del tiempo, asegurando que ambos ingenieros en formación expongan con "
        "solvencia técnica los componentes que lideraron durante la fase de desarrollo.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 28: 8. CONCLUSIONES Y APORTES INDIVIDUALES (8.1 DANIEL MACÍAS)
    # =========================================================================
    story.append(Paragraph("8. Conclusiones y Aportes Individuales", styles["APAHeading1"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("8.1 Aportes y Conclusiones de Daniel Alejandro Macías Pérez", styles["APAHeading2"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Desde la perspectiva del diseño de arquitectura de software, modelado de base de datos relacional y lógica de negocio "
        "en el backend, se formulan las siguientes conclusiones técnicas derivadas del desarrollo de la actividad:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "1. <b>Gobernanza de Reglas de Negocio en el ORM:</b> La concentración de las validaciones de negocio (R01 a R06) a nivel de "
        "los métodos <code>clean()</code> de los modelos y serializadores de Django blindó el sistema contra manipulaciones de clientes "
        "externos o scripts de inyección. Validar que la duración de un examen no sobrepase la ventana cronológica de apertura y cierre "
        "evitó discrepancias que comúnmente paralizan plataformas de evaluación masiva.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "2. <b>Transaccionalidad Atómica en Cargas Masivas:</b> La implementación de <code>ExcelImportService</code> bajo bloques "
        "<code>transaction.atomic()</code> resolvió de manera definitiva el problema de las bases de datos sembradas con registros "
        "parciales o corruptos. La auditoría previa del archivo Excel antes de invocar los modelos de Django asegura que únicamente "
        "aquellos lotes 100% íntegros se consoliden en la base de datos institucional.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "3. <b>Precisión en el Motor de Calificación Decimal:</b> El cálculo de calificaciones empleando campos <code>DECIMAL(5,2)</code> "
        "y gestionando el soporte explícito de preguntas omitidas garantizó la estricta equidad evaluativa, evitando distorsiones por "
        "errores de redondeo binario en coma flotante y permitiendo una correspondencia exacta con la escala colombiana de 0.00 a 5.00.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "4. <b>Automatización como Pilar de Calidad:</b> La codificación de la suite <code>test_taller_extremo_a_extremo.py</code> "
        "demostró que las pruebas automatizadas reducen los tiempos de diagnóstico de fallos en más de un 80% en comparación con la "
        "verificación manual, garantizando estabilidad ante futuros incrementos de requerimientos.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 29: 8.2 APORTES INDIVIDUALES (8.2 JOSÉ LEONEL ENRÍQUEZ)
    # =========================================================================
    story.append(Paragraph("8.2 Aportes y Conclusiones de José Leonel Enríquez Zambrano", styles["APAHeading2"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Desde la perspectiva de la experiencia de usuario (UX/UI), ingeniería del frontend, accesibilidad institucional y "
        "seguridad en capas cliente-servidor, se sintetizan las siguientes conclusiones:",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "1. <b>Depuración y Excelencia Visual Institucional:</b> La erradicación total de emojis informales, textos técnicos redundantes "
        "(tales como indicadores repetidos de usuario conectado o identificadores de reglas como 'R10') y la reorganización de la barra "
        "de navegación permitió transformar un prototipo funcional en una plataforma universitaria sobria, distinguida y formal, "
        "adecuada a los lineamientos visuales oficiales de la Institución Universitaria del Putumayo.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "2. <b>Resiliencia del Temporizador en JavaScript Vanilla:</b> El temporizador dinámico implementado para la sala de exámenes "
        "opera de forma desacoplada de la interfaz, sincronizando su cuenta regresiva con la marca de tiempo de expiración generada "
        "por el backend. Este diseño neutraliza cualquier intento de manipulación del reloj local por parte del estudiante y garantiza "
        "la auto-entrega automática e irrevocable del examen al agotar el tiempo estipulado.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "3. <b>Accesibilidad y Ergonomía Visual (WCAG AA):</b> La calibración de contrastes cromáticos (#0F2942, #1B6C8C, #166534) y el "
        "ajuste de tamaños de fuente en encabezados, enunciados y botones de opción aseguraron una lectura descansada y una navegación "
        "intuitiva para los alumnos, reduciendo la fatiga visual durante sesiones prolongadas de prueba.",
        styles["APABody"]
    ))
    story.append(Paragraph(
        "4. <b>Aseguramiento Criptográfico JWT:</b> El desarrollo de la batería <code>test_jwt_security.py</code> certificó que el "
        "frontend y el backend intercambian credenciales cifradas sin exponer información confidencial en el navegador, asegurando "
        "que cada alumno solo pueda ver y modificar los recursos estrictamente autorizados.",
        styles["APABody"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 30: REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7MA EDICIÓN)
    # =========================================================================
    story.append(Paragraph("Referencias", styles["APAHeading1"]))
    story.append(Spacer(1, 8))

    referencias = [
        "Django Software Foundation. (2024). <i>Django documentation (Version 4.2 LTS)</i>. https://docs.djangoproject.com/en/4.2/",
        "Fielding, R. T. (2000). <i>Architectural styles and the design of network-based software architectures</i> (Doctoral dissertation, University of California, Irvine). Information and Computer Science.",
        "Instituto Colombiano para la Evaluación de la Educación [ICFES]. (2022). <i>Guía de orientación módulos de competencias genéricas y específicas: Examen Saber TyT</i>. Ministerio de Educación Nacional de Colombia. https://www.icfes.gov.co/",
        "Institute of Electrical and Electronics Engineers [IEEE]. (2014). <i>IEEE Standard for Software Quality Assurance Processes</i> (IEEE Std 730-2014). IEEE Computer Society. https://doi.org/10.1109/IEEESTD.2014.6835311",
        "International Organization for Standardization [ISO]. (2011). <i>Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models</i> (ISO/IEC 25010:2011). ISO/IEC.",
        "Jones, M., Bradley, J., & Sakimura, N. (2015). <i>JSON Web Token (JWT)</i> (RFC 7519). Internet Engineering Task Force (IETF). https://doi.org/10.17487/RFC7519",
        "OpenPyXL Development Team. (2024). <i>OpenPyXL - A Python library to read/write Excel 2010 xlsx/xlsm files</i>. https://openpyxl.readthedocs.io/",
        "Pressman, R. S., & Maxim, B. R. (2020). <i>Software engineering: A practitioner's approach</i> (9th ed.). McGraw-Hill Education.",
        "Sommerville, I. (2019). <i>Software engineering</i> (10th ed.). Pearson Education.",
        "World Wide Web Consortium [W3C]. (2023). <i>Web Content Accessibility Guidelines (WCAG) 2.1 (2nd ed.)</i>. W3C Recommendation. https://www.w3.org/TR/WCAG21/",
    ]

    for ref in referencias:
        story.append(Paragraph(ref, styles["APAReference"]))

    # Compilación del Documento
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=letter,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )

    print("Compilando informe en PDF con ReportLab...")
    doc.build(
        story,
        canvasmaker=APANumberedCanvas,
        onFirstPage=draw_background,
        onLaterPages=draw_background
    )
    print(f"Informe compilado exitosamente: {PDF_OUTPUT}")

    # Verificar cantidad de páginas con PyPDF
    reader = pypdf.PdfReader(PDF_OUTPUT)
    num_pags = len(reader.pages)
    print(f"Conteo oficial de páginas: {num_pags}")
    if num_pags == 30:
        print("PERFECTO: El informe tiene EXACTAMENTE 30 páginas.")
    else:
        print(f"ALERTA: El informe tiene {num_pags} páginas en lugar de 30. Requiere calibración.")


if __name__ == "__main__":
    build_pdf()
