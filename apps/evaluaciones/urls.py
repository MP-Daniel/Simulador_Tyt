from django.urls import path
from .views import (
    IniciarIntentoView,
    FinalizarIntentoView,
    RevisionIntentoView,
    MisIntentosView,
    TodosLosIntentosView
)

urlpatterns = [
    path('iniciar/', IniciarIntentoView.as_view(), name='iniciar_intento'),
    path('intentos/<int:intento_id>/finalizar/', FinalizarIntentoView.as_view(), name='finalizar_intento'),
    path('intentos/<int:intento_id>/revision/', RevisionIntentoView.as_view(), name='revision_intento'),
    path('mis-intentos/', MisIntentosView.as_view(), name='mis_intentos'),
    path('todos-los-intentos/', TodosLosIntentosView.as_view(), name='todos_los_intentos'),
]
