from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg

from mbi.models import MBIResult

from .forms import TeamCreateForm, JoinTeamForm
from .models import Team, TeamInviteCode, TeamMembershipRequest

@login_required
def create_team_view(request):
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.save()
            # Generar código de invitación único
            code = TeamInviteCode.generate_code()
            while TeamInviteCode.objects.filter(code=code).exists():
                code = TeamInviteCode.generate_code()
            TeamInviteCode.objects.create(code=code, team=team)
            return redirect('team_detail', team_id=team.id)
    else:
        form = TeamCreateForm()
    return render(request, 'teams/create_team.html', {'form': form})

@login_required
def team_detail_view(request, team_id):
    team = get_object_or_404(Team, id=team_id, leader=request.user)
    invite_code = TeamInviteCode.objects.filter(team=team).first()
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'invite_code': invite_code,
    })

@login_required
def join_team_view(request):
    message = None
    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            invite = TeamInviteCode.objects.filter(code=code).first()
            if invite:
                # Verifica si ya existe una solicitud pendiente o aceptada
                existing = TeamMembershipRequest.objects.filter(team=invite.team, user=request.user).exclude(status='rechazada').first()
                if existing:
                    message = "Ya tienes una solicitud pendiente o eres miembro de este equipo."
                else:
                    TeamMembershipRequest.objects.create(team=invite.team, user=request.user)
                    message = "Solicitud enviada. Espera la aprobación del líder."
            else:
                message = "Código inválido."
    else:
        form = JoinTeamForm()
    return render(request, 'teams/join_team.html', {'form': form, 'message': message})

@login_required
def manage_requests_view(request, team_id):
    team = get_object_or_404(Team, id=team_id, leader=request.user)
    solicitudes = TeamMembershipRequest.objects.filter(team=team, status='pendiente')

    if request.method == 'POST':
        req_id = request.POST.get('req_id')
        action = request.POST.get('action')
        solicitud = TeamMembershipRequest.objects.get(id=req_id, team=team)
        if action == 'aceptar':
            solicitud.status = 'aceptada'
            solicitud.save()
            team.members.add(solicitud.user)
        elif action == 'rechazar':
            solicitud.status = 'rechazada'
            solicitud.save()
        return redirect('manage_requests', team_id=team.id)

    return render(request, 'teams/manage_requests.html', {
        'team': team,
        'solicitudes': solicitudes,
    })

@login_required
def my_requests_view(request):
    solicitudes = TeamMembershipRequest.objects.filter(user=request.user).select_related('team')
    return render(request, 'teams/my_requests.html', {'solicitudes': solicitudes})

@login_required
def my_teams_view(request):
    user = request.user
    es_lider = hasattr(user, 'role') and user.role == 'lider'
    if es_lider:
        equipos = Team.objects.filter(leader=user)
        # Para líderes, puedes pasar solicitudes pendientes por equipo si lo deseas
        context = {
            'es_lider': True,
            'equipos': equipos,
        }
    else:
        equipos = user.teams.all()
        solicitudes = TeamMembershipRequest.objects.filter(user=user).select_related('team')
        mbi_completados = {
            equipo.id: user.mbiresult_set.filter(team=equipo).exists()
            for equipo in equipos
        }
        context = {
            'es_lider': False,
            'equipos': equipos,
            'solicitudes': solicitudes,
            'mbi_completados': mbi_completados,
        }
    if request.method == 'POST' and not es_lider:
        solicitud_id = request.POST.get('solicitud_id')
        TeamMembershipRequest.objects.filter(id=solicitud_id, user=user, status='rechazada').delete()
        return redirect('my_teams')
    return render(request, 'teams/my_teams.html', context)

@login_required
def team_overview(request, team_id):
    team = get_object_or_404(Team, id=team_id, leader=request.user)
    solicitudes = TeamMembershipRequest.objects.filter(team=team, status='pendiente')
    miembros = team.members.all()
    resultados = MBIResult.objects.filter(team=team)
    respondieron_ids = resultados.values_list('user_id', flat=True)
    no_respondieron = miembros.exclude(id__in=respondieron_ids)
    promedios = resultados.aggregate(
        avg_agotamiento=Avg('agotamiento'),
        avg_despersonalizacion=Avg('despersonalizacion'),
        avg_realizacion=Avg('realizacion')
    )
    burnout = []
    for r in resultados:
        if r.agotamiento >= 27 and r.despersonalizacion >= 13 and r.realizacion <= 31:
            burnout.append(r.user)
    completaron = miembros.filter(id__in=respondieron_ids).exclude(id__in=[u.id for u in burnout])
    return render(request, 'teams/team_overview.html', {
        'team': team,
        'solicitudes': solicitudes,
        'completaron': completaron,
        'no_respondieron': no_respondieron,
        'promedios': promedios,
        'burnout': burnout,
    })

@login_required
def mbi_result_user(request, result_id):
    result = get_object_or_404(MBIResult, id=result_id, user=request.user, team__isnull=True)
    # ...otros cálculos...
    return render(request, 'mbi/mbi_result.html', {'result': result})
