# Guía Maestra para la Sustentación del Segundo Parcial
## Electiva Profesional III – Frameworks de Aplicaciones (6.º Semestre)
### Proyecto: Simulador de Pruebas Saber TyT – UniPutumayo

Este documento contiene la guía paso a paso para realizar una sustentación impecable frente al docente, cubriendo cada punto de la **Guía de Evaluación • Unidad 2**.

---

## 1. Puesta en Marcha Rápida

1. Abre tu terminal y dirígete a la carpeta en tu Escritorio:
   ```bash
   cd ~/Desktop/simulador_saber_tyt
   ```
2. Ejecuta el servidor:
   ```bash
   ./run_server.sh
   # O alternativamente:
   python3 manage.py runserver 8000
   ```
3. Abre tu navegador web en: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 2. Cuentas de Demostración Configuradas

En la pantalla de inicio de sesión dispones de botones de acceso rápido con las siguientes cuentas:

| Usuario | Contraseña | Rol Asignado | Propósito en la Sustentación |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Administrador** | Demostrar control total: administración de usuarios, roles configurables, banco de preguntas y cuestionarios. |
| `docente` | `docente123` | **Docente Evaluador** | Demostrar el ejemplo solicitado en la guía: rol con permisos para preguntas y cuestionarios, sin acceso a usuarios. |
| `estudiante1` | `estudiante123` | **Estudiante** (Activo) | Demostrar presentación de examen, visualización de cuestionarios habilitados y nota automática calculada. |
| `estudiante2` | `estudiante123` | **Estudiante** (Activo) | Demostrar que un estudiante **no puede consultar ni modificar** los intentos de otro estudiante (error 403). |
| `inactivo` | `inactivo123` | **Estudiante** (Desactivado) | Demostrar el **control de cuentas desactivadas**: el backend rechaza la generación de tokens JWT. |

---

## 3. Guion de Sustentación Paso a Paso (Metodología Exposición Virtual)

### Paso 1: Introducción y Arquitectura (1 minuto)
* **Qué decir**:
  > *"Profesor, nuestro proyecto está desarrollado sobre Django y MySQL con arquitectura monolítica institucional. La arquitectura se organiza en 4 módulos desacoplados: `authentication` (autenticación JWT, control de cuentas desactivadas y gestión de roles y permisos configurables), `banco_preguntas` (reactivos clasificados por competencias e importador Excel con validación fila por fila), `cuestionarios` (parametrización temporal R01-R04, modo previsualización sandbox para docentes y control de disponibilidad R08) y `evaluaciones` (flujo de examen seguro sin fuga de claves, aislamiento estricto de estudiantes, bloqueo de intentos no válidos y cálculo automático con precisión DECIMAL(5,2)). Además, cuenta con un layout maestro (Single Dashboard Shell) con menú lateral dinámico según el rol institucional."*

### Paso 2: Demostración como Administrador o Docente (3 minutos)
1. **Iniciar sesión como `admin` / `admin123` o `docente` / `docente123`**.
   * Muestra la barra de navegación lateral persistente con el badge de rol respectivo.
2. **Previsualización de Exámenes (Modo Sandbox)**:
   * En el Panel de Control (`/admin-panel/`), haz clic en el botón *"👁️ Previsualizar"* de cualquier cuestionario.
   * Explica:
     > *"Profesor, implementamos un modo Sandbox exclusivo para Docentes y Administradores: permite auditar las preguntas, claves correctas y retroalimentación pedagógica sin registrar intentos en la base de datos ni alterar las métricas de los estudiantes."*
3. **Demostración de Blindaje de Negocio (403 Forbidden para No-Estudiantes)**:
   * Demuestra que si un docente o administrador intenta llamar al endpoint de inicio de examen oficial (`POST /api/evaluaciones/iniciar/`), el backend responde con un **HTTP 403 Forbidden** y el mensaje:
     > *"Acceso denegado: Solo los usuarios con rol 'Estudiante' pueden presentar evaluaciones oficiales. Si es docente o administrador, utilice la opción de Previsualización."*
4. **Ir a "Usuarios y Roles" (`/admin-panel/usuarios/`)**:
   * **Demostrar control de cuentas**: Haz clic en *"Desactivar Cuenta"* de algún usuario y muestra cómo el estado cambia a `Desactivada`. Explica que Django valida este estado en el backend para rechazar logins JWT.
   * **Demostrar roles configurables**: Pasa a la pestaña *"Roles y Permisos"*. Muestra el rol `Docente Evaluador`.
   * **Crear nuevo rol configurable**: Haz clic en *"+ Crear Rol Personalizado"*, asígnale un nombre (ej. `Auditor Académico`) y marca checkboxes individuales de permisos (ej. solo `resultados.consultar_todos`). Explica:
     > *"Profesor, cumplimos el requerimiento de roles configurables: el administrador habilita o restringe individualmente las funcionalidades del sistema a nivel atómico en Django."*
5. **Ir al Banco de Preguntas (`/admin-panel/preguntas/`)**:
   * Muestra los reactivos clasificados por competencias (Razonamiento Cuantitativo, Lectura Crítica, etc.).
   * Abre *"+ Nueva Pregunta"* y muestra la validación de la Regla R05 (una sola respuesta correcta) y R06 (Verdadero/Falso con solo 2 opciones).
6. **Ir a Importación Excel (`/admin-panel/importar-excel/`)**:
   * Haz clic en *"⚡ Cargar Datos Demo con Regla R10"*.
   * Muestra cómo el sistema audita fila por fila, reporta el número de fila exacto donde se encuentra el error y descarta filas erróneas sin afectar la base de datos (Regla R10).
7. **Ir a Crear Cuestionario (`/admin-panel/cuestionarios/crear/`)**:
   * Muestra las validaciones de las Reglas R01 (`cierre > apertura`), R02 (`nota máxima > 0`), R03 (`aprobación <= máxima`) y R04 (`tiempo > 0` e `intentos > 0`).

### Paso 3: Demostración como Estudiante (3 minutos)
1. Cierra sesión y entra como **`estudiante1` / `estudiante123`**.
2. **Dashboard del Estudiante (`/estudiante/`)**:
   * Muestra la barra lateral del estudiante: *Mis Cuestionarios Disponibles*, *Mi Historial de Resultados* y *Cerrar Sesión*.
   * Explica que el backend solo entrega los cuestionarios **disponibles** (activos y dentro de las fechas de apertura/cierre, cumpliendo la Sec 2.5 y Regla R08).
3. **Presentar Examen (`/estudiante/examen/`)**:
   * Muestra la **excepción de concentración**: la barra lateral se oculta durante la evaluación para evitar distracciones y clics accidentales, manteniendo únicamente el temporizador regresivo.
   * **Punto clave de seguridad técnica**: Abre las herramientas de desarrollador (`F12` -> Inspeccionar red o consola) y demuestra que:
     > *"Profesor, las preguntas recibidas por el frontend NO contienen el campo `es_correcta` ni la retroalimentación. El estudiante no tiene forma de hacer trampa inspeccionando el código."*
   * Responde algunas preguntas y deja 1 o 2 en blanco.
   * Haz clic en *"Finalizar y Enviar Intento"*.
4. **Pantalla de Resultados (`/estudiante/resultados/`)**:
   * Muestra la nota calculada con precisión `DECIMAL(5,2)` según la fórmula oficial:
     $$\text{Calificación} = \left(\frac{\text{puntaje\_obtenido}}{\text{puntaje\_total\_posible}}\right) \times \text{calificacion\_maxima}$$
   * Muestra que las preguntas no respondidas quedaron guardadas como **Omitidas** con 0.00 pts (Regla R09).
   * Muestra la retroalimentación didáctica y las respuestas correctas ahora que el examen ha concluido.
   * Muestra la barra lateral activa para regresar inmediatamente a Mis Cuestionarios o Historial sin quedar atrapado.
5. **Demostración de Aislamiento de Seguridad (Sec 2.5)**:
   * Copia la URL del resultado (ej. `/estudiante/resultados/?intento_id=1`).
   * Cierra sesión e ingresa como **`estudiante2`**.
   * Intenta pegar la URL del intento del estudiante 1.
   * El sistema y la API responden con **403 Forbidden / Acceso Denegado**, demostrando que un estudiante no puede espiar ni alterar evaluaciones ajenas.

---

## 4. Archivos Clave para Explicar en el Código

Si el docente pide abrir archivos de código específicos:

| Archivo | Qué demostrar / Explicar |
| :--- | :--- |
| `apps/authentication/models.py` | Modelos `Permiso`, `Rol` (con ManyToMany a permisos y método `tiene_permiso`) y `Usuario` (hereda de `AbstractUser` con FK a `Rol`). |
| `apps/authentication/serializers.py` | `CustomTokenObtainPairSerializer`: personalización del payload JWT con claims de usuario y control de cuentas desactivadas (`is_active`). |
| `apps/authentication/permissions.py` | `HasCustomPermission` y `require_permission`: clases de permisos que validan en Django que el usuario tenga el código de permiso requerido. |
| `apps/cuestionarios/models.py` | Validaciones `clean()` de las reglas R01, R02, R03, R04 y método `esta_disponible_ahora()` para la regla R08. |
| `apps/cuestionarios/views.py` | `previsualizar`: Endpoint Sandbox exclusivo para docentes que expone claves pedagógicas sin alterar la BD. |
| `apps/evaluaciones/views.py` | Lógica de `IniciarIntentoView` (blindaje 403 a no-estudiantes y exclusión de claves en vivo), `FinalizarIntentoView` (evaluación atómica, cálculo de nota decimal, manejo de omitidas R09) y `RevisionIntentoView` (aislamiento estricto por usuario). |
| `templates/base.html` | Single Dashboard Shell unificado con sidebar dinámico según rol e institucional UniPutumayo. |
| `core/settings.py` | Conexión con MySQL (`mysqlclient`), configuración de `SIMPLE_JWT` y modelo de usuario personalizado. |

---

## 5. Ejecución del Test Automatizado de Seguridad

Para demostrar la solidez del sistema ante el docente con un solo comando:
```bash
python3 test_jwt_security.py
```
Este script ejecuta automáticamente **14 pruebas unitarias e integradas** verificando tokens JWT, rechazo de cuentas inactivas, blindaje 403 a no-estudiantes, previsualización Sandbox docente, examen seguro sin fuga de claves, cálculo de nota con omitidas R09, aislamiento entre estudiantes y creación de roles dinámicos.
