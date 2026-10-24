from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from .views import (
    LoginView,
    IndexView,
    StudentDashboardView,
    ExamView,
    ResultsView,
    AdminDashboardView,
    UserManagementView,
    QuestionBankView,
    CreateQuizView,
    ImportExcelView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/img/logo_uniputumayo.png', permanent=True)),

    # =========================================================================
    # ENDPOINTS DE API REST (Protegidos con JWT y Permisos)
    # =========================================================================
    path('api/auth/', include('authentication.urls')),
    path('api/banco/', include('banco_preguntas.urls')),
    path('api/cuestionarios/', include('cuestionarios.urls')),
    path('api/evaluaciones/', include('evaluaciones.urls')),

    # =========================================================================
    # VISTAS DE INTERFAZ WEB (HTML + Tailwind + JavaScript)
    # =========================================================================
    path('', LoginView.as_view(), name='web_login'),
    path('vistas/', IndexView.as_view(), name='web_index'),
    path('estudiante/', StudentDashboardView.as_view(), name='web_student_dashboard'),
    path('estudiante/examen/', ExamView.as_view(), name='web_exam'),
    path('estudiante/resultados/', ResultsView.as_view(), name='web_results'),
    path('admin-panel/', AdminDashboardView.as_view(), name='web_admin_dashboard'),
    path('admin-panel/usuarios/', UserManagementView.as_view(), name='web_user_management'),
    path('admin-panel/preguntas/', QuestionBankView.as_view(), name='web_question_bank'),
    path('admin-panel/cuestionarios/crear/', CreateQuizView.as_view(), name='web_create_quiz'),
    path('admin-panel/importar-excel/', ImportExcelView.as_view(), name='web_import_excel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
