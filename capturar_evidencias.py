import os
import asyncio
from playwright.async_api import async_playwright

EVIDENCIAS_DIR = os.path.abspath("docs/evidencias")
os.makedirs(EVIDENCIAS_DIR, exist_ok=True)

async def capturar_todas_las_evidencias():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='msedge')
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # =====================================================================
        # 1. LOGIN DOCENTE & CONFIGURACIÓN
        # =====================================================================
        print("1. Capturando Configuración Docente...")
        await page.goto("http://127.0.0.1:8000/")
        await page.fill("#usernameInput", "docente")
        await page.fill("#passwordInput", "docente123")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/admin-panel/")
        await page.wait_for_timeout(1000)

        # 1.1 Ir a Crear Cuestionario
        await page.goto("http://127.0.0.1:8000/admin-panel/cuestionarios/crear/")
        await page.wait_for_timeout(1000)
        await page.fill("#quizName", "Evaluación Integradora Saber TyT - Sexto Semestre")
        await page.fill("#quizSubject", "Competencias Genéricas Saber TyT")
        await page.fill("#quizDesc", "Simulacro oficial de preparación con 4 competencias clave: Lectura Crítica, Razonamiento Cuantitativo, Competencias Ciudadanas e Inglés.")
        await page.fill("#timeLimit", "30")
        await page.fill("#attempts", "1")
        await page.fill("#quizPassword", "SaberTyT2026")
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_01_configuracion_docente.png"))
        print("  -> Guardado: evidencia_01_configuracion_docente.png")

        # =====================================================================
        # 2. BANCO DE PREGUNTAS Y PLANTILLA EXCEL
        # =====================================================================
        print("2. Capturando Banco de Preguntas...")
        await page.goto("http://127.0.0.1:8000/admin-panel/preguntas/")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_02_banco_preguntas.png"))
        print("  -> Guardado: evidencia_02_banco_preguntas.png")

        # =====================================================================
        # 3. IMPORTADOR EXCEL
        # =====================================================================
        print("3. Capturando Importador Excel...")
        await page.goto("http://127.0.0.1:8000/admin-panel/importar-excel/")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_03_importacion_excel.png"))
        print("  -> Guardado: evidencia_03_importacion_excel.png")

        # =====================================================================
        # 4. REPORTES Y ESTADÍSTICAS DOCENTE
        # =====================================================================
        print("4. Capturando Reporte Estadístico...")
        await page.goto("http://127.0.0.1:8000/admin-panel/reportes/")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_07_reporte_estadistico_docente.png"))
        print("  -> Guardado: evidencia_07_reporte_estadistico_docente.png")

        # =====================================================================
        # 5. ESTUDIANTE: EVALUACIÓN ACTIVA
        # =====================================================================
        print("5. Capturando Panel del Estudiante...")
        await page.evaluate("Auth.logout()")
        await page.wait_for_timeout(500)
        await page.goto("http://127.0.0.1:8000/")
        await page.fill("#usernameInput", "estudiante1")
        await page.fill("#passwordInput", "estudiante123")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/estudiante/")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_04_evaluacion_activa_estudiante.png"))
        print("  -> Guardado: evidencia_04_evaluacion_activa_estudiante.png")

        # =====================================================================
        # 6. ESTUDIANTE: RESULTADOS Y CALIFICACIÓN
        # =====================================================================
        print("6. Capturando Resultados del Estudiante...")
        await page.goto("http://127.0.0.1:8000/estudiante/resultados/")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_06_resultado_estudiante.png"))
        print("  -> Guardado: evidencia_06_resultado_estudiante.png")

        # =====================================================================
        # 7. SALA DE EXAMEN (CON ESTUDIANTE 2)
        # =====================================================================
        print("7. Capturando Sala de Examen en vivo...")
        await page.evaluate("Auth.logout()")
        await page.wait_for_timeout(500)
        await page.goto("http://127.0.0.1:8000/")
        await page.fill("#usernameInput", "estudiante2")
        await page.fill("#passwordInput", "estudiante123")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/estudiante/")
        await page.wait_for_timeout(1000)

        # Configurar variables de sesión e iniciar examen
        await page.evaluate("""() => {
            sessionStorage.setItem('active_cuestionario_id', '16');
            sessionStorage.setItem('active_quiz_pass_16', 'SaberTyT2026');
            window.location.href = '/estudiante/examen/?cuestionario_id=16';
        }""")
        await page.wait_for_url("**/estudiante/examen/**")
        await page.wait_for_timeout(2000)

        await page.screenshot(path=os.path.join(EVIDENCIAS_DIR, "evidencia_05_sala_examen.png"))
        print("  -> Guardado: evidencia_05_sala_examen.png")

        await browser.close()
        print("\n✓ ¡Todas las 7 capturas de pantalla de evidencias fueron generadas con éxito!")

if __name__ == '__main__':
    asyncio.run(capturar_todas_las_evidencias())
