from django.urls import path
from . import views

urlpatterns = [
    path('equipo/<int:team_id>/test/', views.take_mbi_view, name='take_mbi'),
    path('equipo/<int:team_id>/resultado/', views.mbi_result_view, name='mbi_result'),
    path('equipo/<int:team_id>/resumen/', views.team_mbi_overview, name='team_mbi_overview'),
    path('mbi/personal/', views.take_mbi_user, name='take_mbi_user'),
    # ...otras rutas...
]