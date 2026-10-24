# 📘 Guía Rápida para el Compañero de Equipo
## ¿Qué es este proyecto, qué se hizo y cómo ponerlo a funcionar en tu máquina?

¡Hola compa! Esta guía está hecha para que puedas clonar el proyecto, configurarlo en 2 minutos y entender exactamente qué se implementó para el **Segundo Parcial Práctico de Electiva Profesional III (UniPutumayo)**.

---

## 1. ¿Qué es este sistema?
Es un **Simulador de Pruebas Saber TyT** desarrollado para la **Institución Universitaria del Putumayo (Ingeniería de Sistemas, 6.º Semestre)**.
El stack solicitado por el docente es:
* **Backend:** Python + Django + Django REST Framework + SimpleJWT.
* **Base de Datos:** MySQL Community Server (puerto `3306`).
* **Frontend:** Monolito Django con HTML5, Tailwind CSS y JavaScript interactivo (con consumo de API REST protegida por JWT).

---

## 2. ¿Qué se hizo? (Resumen de Módulos y Requerimientos)

| Módulo / Requerimiento | Descripción de lo que se implementó |
| :--- | :--- |
| **1. Seguridad JWT y Control de Cuentas (Sec 2.1)** | Login seguro con tokens JWT (`access` y `refresh`). Verificación de cuentas activas: si un usuario está desactivado (`is_active=False`), el backend rechaza el login de inmediato. Las autorizaciones se evalúan en Django (`403 Forbidden`). |
| **2. Roles y Permisos Configurables (Sec 2.2)** | Roles base: `Administrador` y `Estudiante`. Panel para crear roles dinámicos (ej. `Docente Evaluador`) con permisos atómicos asignables mediante checkboxes en base de datos. |
| **3. Banco de Preguntas y Carga Masiva (Sec 2.3 y R10)** | Reactivos organizados por competencias Saber TyT (Razonamiento Cuantitativo, Lectura Crítica, Ciudadanas, Inglés). Preguntas de Selección Múltiple (R05) y Verdadero/Falso (R06). Importador Excel que audita fila por fila, reporta la fila exacta con error y descarta filas malas sin romper la BD (Regla R10). |
| **4. Parametrización de Cuestionarios (Sec 2.4)** | Reglas R01 (`cierre > apertura`), R02 (`máxima > 0`), R03 (`aprobación <= máxima`), R04 (`tiempo > 0` e `intentos > 0`). Disponibilidad en servidor (R08): no deja presentar fuera de fecha. |
| **5. Blindaje de Evaluaciones (Nueva Regla)** | Solo usuarios con rol `Estudiante` pueden presentar exámenes oficiales. Si un docente o administrador intenta presentar, recibe **HTTP 403 Forbidden**. Se creó el **Modo Previsualización (Sandbox)** para que docentes revisen preguntas y claves sin generar intentos ni alterar notas. |
| **6. Examen Seguro y Calificación (Sec 2.5)** | Durante el examen, el backend **NO envía las respuestas correctas ni la retroalimentación** (imposible hacer trampa con F12). Al finalizar, Django calcula la nota con precisión `DECIMAL(5,2)`. Las preguntas en blanco se registran como omitidas con 0.00 pts (Regla R09). Aislamiento estricto: un estudiante no puede ver las notas de otro. |
| **7. Layout Maestro (Single Dashboard Shell)** | Barra de navegación lateral fija con colores institucionales (#0F172A, #8DBF21, #1B6C8C) y menú dinámico según el rol. Excepción de concentración: en la sala de examen se oculta el menú para evitar distracciones. |

---

## 3. Pasos para Hacerlo Funcionar en Tu Computador

### Paso 1: Clonar el Repositorio
Abre tu terminal en la carpeta donde guardas tus proyectos:
```bash
git clone https://github.com/MP-Daniel/Simulador_Tyt.git
cd Simulador_Tyt
```

### Paso 2: Crear el Entorno Virtual e Instalar Librerías
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En macOS / Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

> **Si usas Windows o tienes problemas con mysqlclient:**  
> Puedes instalar `pymysql` (`pip install pymysql`). El archivo `manage.py` y `core/__init__.py` ya están preparados para usar PyMySQL automáticamente si no tienes las librerías de C de MySQL.

---

### Paso 3: Configurar tu Contraseña de MySQL en `.env`
Copia la plantilla `.env.example` para crear tu `.env`:
```bash
cp .env.example .env
```

Abre `.env` y **solo debes cambiar la contraseña** por la de tu MySQL local:
```env
DB_ENGINE=mysql
DB_NAME=simulador_saber_tyt
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui    <--- PON TU CONTRASEÑA DE MYSQL AQUÍ
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

### Paso 4: Crear la Base de Datos y Cargar Datos Iniciales (1 solo comando)
Hemos creado un comando automatizado que crea la base de datos MySQL por ti, ejecuta todas las migraciones y siembra los roles, usuarios, preguntas y cuestionarios iniciales:

```bash
python3 manage.py setup_database
```

¡Listo! Verás mensajes en verde confirmando que la base de datos `simulador_saber_tyt` se creó y se poblaron todos los datos.

---

### Paso 5: Ejecutar el Servidor
Inicia el servidor local de Django:
```bash
python3 manage.py runserver 8000
```
O también puedes usar el script de arranque directo:
```bash
./run_server.sh
```

Abre en tu navegador web:
👉 **http://127.0.0.1:8000**

---

## 4. Cuentas de Acceso para Probar el Sistema

En la pantalla de inicio de sesión tienes botones que rellenan automáticamente las credenciales:

1. **`admin` / `admin123` (Rol: Administrador)**
   * Puedes ver el panel general, banco de preguntas, importar Excel, crear cuestionarios, previsualizar en modo Sandbox y administrar usuarios y roles configurables.
2. **`docente` / `docente123` (Rol: Docente Evaluador)**
   * Puedes gestionar reactivos, cargar Excel, configurar cuestionarios y previsualizar preguntas con sus claves correctas y retroalimentación pedagógica.
3. **`estudiante1` / `estudiante123` (Rol: Estudiante Activo)**
   * Ves los cuestionarios habilitados, presentas la evaluación con temporizador en vivo, finalizas y observas tu informe de resultados con calificación decimal y retroalimentación didáctica.
4. **`estudiante2` / `estudiante123` (Rol: Estudiante Activo)**
   * Sirve para demostrar que si intenta abrir la URL de un examen de `estudiante1`, el sistema lo bloquea con `403 Forbidden`.
5. **`inactivo` / `inactivo123` (Cuenta Desactivada)**
   * Sirve para demostrar que el backend JWT rechaza el login de cuentas inactivas.

---

## 5. ¿Cómo Verificar que Todo está Seguro?
Ejecuta la suite de pruebas automatizadas:
```bash
python3 test_jwt_security.py
```
Deben pasar las **14 pruebas automatizadas** en verde.

Cualquier duda, revisa también el archivo `INSTRUCCIONES_SUSTENTACION.md` donde está el guion detallado de qué decir en la presentación del parcial. ¡Éxitos compa! 🚀
