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
]