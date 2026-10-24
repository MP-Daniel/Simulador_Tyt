# 🎓 Simulador de Pruebas Saber TyT – UniPutumayo
## Sistema Web Monolítico con Django, MySQL y Seguridad JWT
### Institución Universitaria del Putumayo • Ingeniería de Sistemas (6.º Semestre)
**Electiva Profesional III – Frameworks de Aplicaciones (Segundo Parcial Práctico • Unidad 2)**

---

## 📋 Descripción del Proyecto
Plataforma integral de simulación y evaluación para las pruebas de Estado **Saber TyT**, desarrollada con el stack oficial solicitado: **Django + Python + MySQL + Tailwind CSS + JavaScript**. 

El sistema implementa una arquitectura segura y modularizada en 4 componentes desacoplados (`authentication`, `banco_preguntas`, `cuestionarios`, `evaluaciones`), con control de acceso basado en tokens JWT (HS256), roles y permisos configurables a nivel atómico en Django, importador masivo con validación fila por fila (Regla R10), modo previsualización Sandbox para docentes, calificación automática con precisión `DECIMAL(5,2)` y un layout institucional unificado (*Single Dashboard Shell*) con menú dinámico por rol.

---

## 🚀 Guía de Instalación Rápida para Compañeros

Cualquier compañero que clone este repositorio puede poner a funcionar el proyecto en **3 sencillos pasos**:

### Paso 1: Clonar el Repositorio e Instalar Dependencias
```bash
# 1. Clonar el repositorio
git clone https://github.com/MP-Daniel/Simulador_Tyt.git
cd Simulador_Tyt

# 2. (Opcional pero recomendado) Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows

# 3. Instalar librerías
pip install -r requirements.txt
```

> **Nota para macOS / Linux:** Asegúrate de tener instalado el cliente de MySQL (`brew install mysql-client` en Mac o `sudo apt install default-libmysqlclient-dev` en Ubuntu).

---

### Paso 2: Configurar las Credenciales de tu Base de Datos Local
Copia el archivo de plantilla `.env.example` y crea tu archivo `.env`:

```bash
cp .env.example .env
```

Abre `.env` con tu editor y coloca la contraseña de tu usuario `root` de MySQL local:

```env
SECRET_KEY=django-insecure-uniputumayo-saber-tyt-2026-jwt-secure-key-xyz
DEBUG=True

# Configuración de tu base de datos local
DB_ENGINE=mysql
DB_NAME=simulador_saber_tyt
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui   <--- COLOCA TU CONTRASEÑA DE MYSQL AQUÍ
DB_HOST=127.0.0.1
DB_PORT=3306

JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

---

### Paso 3: Inicializar la Base de Datos Automáticamente (Estilo Hibernate)
No necesitas crear la base de datos a mano en MySQL Workbench o phpMyAdmin. Hemos programado un comando maestro que hace todo por ti:

```bash
python3 manage.py setup_database
```

Este comando ejecuta en secuencia:
1. Conecta con MySQL en tu puerto local.
2. Crea automáticamente la base de datos `simulador_saber_tyt` con encoding `utf8mb4` (si no existía).
3. Aplica todas las migraciones del esquema relacional.
4. Siembra los datos iniciales necesarios: roles (`Administrador`, `Estudiante`, `Docente Evaluador`), permisos atómicos, categorías Saber TyT, banco de reactivos con claves pedagógicas, cuestionarios habilitados y usuarios de prueba.

---

### Paso 4: Iniciar el Servidor Web
Ejecuta el servidor de desarrollo:

```bash
python3 manage.py runserver 8000
# O también mediante el script directo:
./run_server.sh
```

Abre tu navegador en:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Verificación Automatizada (14 Pruebas Unitarias e Integradas)
Para comprobar que la seguridad JWT, las autorizaciones en Django y el blindaje de evaluaciones están al 100%, ejecuta en la terminal:

```bash
python3 test_jwt_security.py
```

El script valida automáticamente:
1. Emisión de tokens JWT (`access` y `refresh`) para Administradores.
2. Control de cuentas desactivadas (usuario inactivo rechazado por JWT).
3. Emisión de tokens para Estudiantes.
4. Validación de claims y permisos en `/api/auth/me/`.
5. Bloqueo 403 Forbidden cuando un estudiante intenta administrar usuarios.
6. **Blindaje de negocio**: Administrador bloqueado (403) al intentar presentar examen oficial.
7. **Blindaje de negocio**: Docente bloqueado (403) al intentar presentar examen oficial.
8. **Modo Previsualización (Sandbox)**: Docentes y Administradores auditan preguntas con claves sin registrar intentos en la base de datos.
9. **Seguridad Sandbox**: Estudiante bloqueado (403) al intentar acceder a la previsualización docente.
10. **Seguridad en examen en vivo**: El frontend recibe preguntas seguras sin fuga de claves correctas ni retroalimentación.
11. **Cálculo automático de calificación**: Calificación decimal exacta `DECIMAL(5,2)` y registro de omitidas (Regla R09).
12. **Aislamiento estricto**: Un estudiante recibe 403 Forbidden al intentar consultar las notas o revisiones de otro estudiante.
13. Consulta autorizada de revisión pedagógica propia.
14. Creación dinámica de roles configurables con permisos atómicos.

---

## 👥 Cuentas de Acceso Rápido para Pruebas y Sustentación

En la pantalla de inicio de sesión (`/`) dispones de botones de acceso rápido precargados con estas cuentas:

| Usuario | Contraseña | Rol Asignado | Alcance y Capacidades |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Administrador** | Control total: gestión de usuarios, roles configurables, banco de reactivos, creación de cuestionarios y previsualización Sandbox. |
| `docente` | `docente123` | **Docente Evaluador** | Gestión académica: preguntas, carga masiva Excel, configuración de cuestionarios y previsualización pedagógica sin alterar notas. |
| `estudiante1` | `estudiante123` | **Estudiante** (Activo) | Presentación de exámenes oficiales disponibles, temporizador en vivo, entrega y consulta de historial de calificaciones. |
| `estudiante2` | `estudiante123` | **Estudiante** (Activo) | Demostración de aislamiento de datos: no puede acceder a las revisiones ni calificaciones de `estudiante1` (403). |
| `inactivo` | `inactivo123` | **Estudiante** (Desactivado) | Demostración de control de cuentas: rechazado por el backend JWT (`is_active = False`). |

---

## 🏛️ Estructura del Proyecto

```text
Simulador_Tyt/
├── apps/
│   ├── authentication/       # Modelos Usuario, Rol, Permiso, JWT serializers y endpoints
│   ├── banco_preguntas/      # Categorías Saber TyT, Preguntas, Opciones e Importador Excel
│   ├── cuestionarios/        # Parametrización R01-R04, Disponibilidad R08 y Previsualización Sandbox
│   └── evaluaciones/         # Examen en vivo, cálculo decimal de nota, Regla R09 y auditoría
├── core/
│   ├── settings.py           # Configuración Django, SimpleJWT y conexión MySQL
│   ├── urls.py               # Enrutamiento principal de vistas web y API REST
│   └── views.py              # Controladores de plantillas HTML
├── static/
│   ├── img/
│   │   └── logo_uniputumayo.png  # Logo oficial institucional transparente
│   └── js/
│       └── auth.js           # Cliente central de autenticación JWT y manejo de sesiones
├── templates/
│   ├── base.html             # Master Shell: navegación lateral dinámica según el rol institucional
│   ├── login.html            # Pantalla de inicio de sesión segura con tokens JWT
│   ├── student_dashboard.html# Panel del estudiante: cuestionarios disponibles e historial
│   ├── exam.html             # Sala de examen en vivo (entorno de concentración sin sidebar)
│   ├── results.html          # Auditoría pedagógica e informe de resultados DECIMAL(5,2)
│   ├── admin_dashboard.html  # Panel de control, métricas, previsualización Sandbox y resultados
│   ├── user_management.html  # Administración de usuarios y roles configurables
│   ├── question_bank.html    # Banco central de reactivos por competencias Saber TyT
│   ├── create_quiz.html      # Formulario de parametrización de cuestionarios
│   ├── import_excel.html     # Carga masiva con auditoría fila por fila (Regla R10)
│   └── index.html            # Mapa y directorio de pantallas del sistema
├── INSTRUCCIONES_SUSTENTACION.md # Libreto detallado paso a paso para la sustentación
├── requirements.txt          # Dependencias y librerías Python
├── run_server.sh             # Script de arranque rápido
├── test_jwt_security.py      # Suite de 14 pruebas automatizadas
└── .env.example              # Plantilla segura de variables de entorno (sin credenciales)
```

---

## 🎨 Identidad Institucional UniPutumayo
El diseño gráfico respeta las directrices visuales de la Institución Universitaria del Putumayo:
* **Verde Institucional**: `#8DBF21`
* **Azul Institucional**: `#1B6C8C`
* **Acento Dorado / Ámbar**: `#C67D00`
* **Fondo Maestro Oscuro**: `#0F172A` (Slate 900)
* **Logo Oficial**: Renderizado con canal alfa transparente y anti-aliasing de bordes en alta definición.
