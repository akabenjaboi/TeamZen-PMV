from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.create_team_view, name='create_team'),
    path('<int:team_id>/', views.team_detail_view, name='team_detail'),
    path('unirse/', views.join_team_view, name='join_team'),
    path('<int:team_id>/solicitudes/', views.manage_requests_view, name='manage_requests'),
    path('mis-solicitudes/', views.my_requests_view, name='my_requests'),
    path('mis-equipos/', views.my_teams_view, name='my_teams'),
    path('mbi/personal/result/<int:result_id>/', views.mbi_result_user, name='mbi_result_user'),
    path('crud/', views.crud_menu_view, name='crud'),
      # Integrante
    path('crud/integrantes/create/', views.integrante_create_view, name='integrante_create'),
    path('crud/integrantes/<int:pk>/edit/', views.integrante_update_view, name='integrante_update'),
    path('crud/integrantes/<int:pk>/delete/', views.integrante_delete_view, name='integrante_delete'),

    # Equipo
    path('crud/equipos/create/', views.equipo_create_view, name='equipo_create'),
    path('crud/equipos/<int:pk>/edit/', views.equipo_update_view, name='equipo_update'),
    path('crud/equipos/<int:pk>/delete/', views.equipo_delete_view, name='equipo_delete'),

    # Proyecto
    path('crud/proyectos/create/', views.proyecto_create_view, name='proyecto_create'),
    path('crud/proyectos/<int:pk>/edit/', views.proyecto_update_view, name='proyecto_update'),
    path('crud/proyectos/<int:pk>/delete/', views.proyecto_delete_view, name='proyecto_delete'),

    # Rol
    path('crud/roles/create/', views.rol_create_view, name='rol_create'),
    path('crud/roles/<int:pk>/edit/', views.rol_update_view, name='rol_update'),
    path('crud/roles/<int:pk>/delete/', views.rol_delete_view, name='rol_delete'),
]
