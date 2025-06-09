from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from teams.models import Team
from .models import MBIQuestion, MBIResult, MBIAnswer
from .forms import MBIForm
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from deepface import DeepFace
from PIL import Image
import numpy as np
import io

@login_required
def take_mbi_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if not team.members.filter(id=request.user.id).exists():
        return render(request, 'mbi/not_member.html')

    if MBIResult.objects.filter(user=request.user, team=team).exists():
        return redirect('mbi_result', team_id=team.id)

    if request.method == 'POST':
        form = MBIForm(request.POST)
        if form.is_valid():
            # Calcular puntajes
            agotamiento = despersonalizacion = realizacion = 0
            answers = []
            for field, value in form.cleaned_data.items():
                qid = int(field.split('_')[1])
                question = MBIQuestion.objects.get(id=qid)
                val = int(value)
                if question.dimension == 'agotamiento':
                    agotamiento += val
                elif question.dimension == 'despersonalizacion':
                    despersonalizacion += val
                elif question.dimension == 'realizacion':
                    realizacion += val
                answers.append((question, val))
            result = MBIResult.objects.create(
                user=request.user,
                team=team,
                agotamiento=agotamiento,
                despersonalizacion=despersonalizacion,
                realizacion=realizacion
            )
            for question, val in answers:
                MBIAnswer.objects.create(result=result, question=question, value=val)
            return redirect('mbi_result', team_id=team.id)
    else:
        form = MBIForm()
    return render(request, 'mbi/take_mbi.html', {'form': form, 'team': team})

@login_required
def mbi_result_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    result = get_object_or_404(MBIResult, user=request.user, team=team)
    interpretacion = interpretar_mbi(result.agotamiento, result.despersonalizacion, result.realizacion)
    return render(request, 'mbi/mbi_result.html', {
        'team': team,
        'result': result,
        'interpretacion': interpretacion,
    })

@login_required
def team_mbi_overview(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    miembros = team.members.all()
    resultados = MBIResult.objects.filter(team=team)

    # Agrupa resultados por año-mes
    resultados_por_mes = defaultdict(list)
    for r in resultados:
        key = r.date.strftime('%Y-%m')
        resultados_por_mes[key].append(r)

    # Determina el rango de meses (desde el primer resultado hasta un mes a futuro)
    if resultados.exists():
        fecha_inicio = resultados.order_by('date').first().date
    else:
        fecha_inicio = timezone.now()
    fecha_inicio = datetime(fecha_inicio.year, fecha_inicio.month, 1)
    fecha_fin = datetime(timezone.now().year, timezone.now().month, 1) + relativedelta(months=1)

    meses_disponibles = []
    actual = fecha_inicio
    while actual <= fecha_fin:
        meses_disponibles.append(actual.strftime('%Y-%m'))
        actual += relativedelta(months=1)

    # Selecciona el mes actual por defecto, o el que venga por GET
    mes_actual = request.GET.get('mes') or timezone.now().strftime('%Y-%m')
    resultados_mes = resultados_por_mes.get(mes_actual, [])

    # Calcula los datos del dashboard solo para ese mes
    completaron = []
    burnout_resultados = []
    respondieron_ids = []
    for r in resultados_mes:
        respondieron_ids.append(r.user.id)
        if r.agotamiento >= 27 and r.despersonalizacion >= 13 and r.realizacion <= 31:
            burnout_resultados.append(r)
        else:
            completaron.append(r.user)
    no_respondieron = miembros.exclude(id__in=respondieron_ids)
    total_miembros = len(completaron) + no_respondieron.count()

    promedios = {
        'avg_agotamiento': sum(r.agotamiento for r in resultados_mes) / len(resultados_mes) if resultados_mes else 0,
        'avg_despersonalizacion': sum(r.despersonalizacion for r in resultados_mes) / len(resultados_mes) if resultados_mes else 0,
        'avg_realizacion': sum(r.realizacion for r in resultados_mes) / len(resultados_mes) if resultados_mes else 0,
    }

    mes_siguiente = (timezone.now() + relativedelta(months=1)).strftime('%Y-%m')

    return render(request, 'mbi/team_mbi_overview.html', {
        'team': team,
        'meses_disponibles': meses_disponibles,
        'mes_actual': mes_actual,
        'completaron': completaron,
        'no_respondieron': no_respondieron,
        'burnout_resultados': burnout_resultados,
        'total_miembros': total_miembros,
        'promedios': promedios,
        'resultados': resultados_mes,
        'mes_siguiente': mes_siguiente,
    })

def take_mbi_user(request):
    if request.method == 'POST':
        form = MBIForm(request.POST)
        if form.is_valid():
            # Procesa y guarda igual que en take_mbi_view, pero sin team
            agotamiento = despersonalizacion = realizacion = 0
            answers = []
            for field, value in form.cleaned_data.items():
                qid = int(field.split('_')[1])
                question = MBIQuestion.objects.get(id=qid)
                val = int(value)
                if question.dimension == 'agotamiento':
                    agotamiento += val
                elif question.dimension == 'despersonalizacion':
                    despersonalizacion += val
                elif question.dimension == 'realizacion':
                    realizacion += val
                answers.append((question, val))
            result = MBIResult.objects.create(
                user=request.user,
                team=None,  # No hay equipo
                agotamiento=agotamiento,
                despersonalizacion=despersonalizacion,
                realizacion=realizacion
            )
            for question, val in answers:
                MBIAnswer.objects.create(result=result, question=question, value=val)
            return redirect('profile')
    else:
        form = MBIForm()
    return render(request, 'mbi/take_mbi.html', {'form': form, 'team': None})

def interpretar_mbi(agotamiento, despersonalizacion, realizacion):
    interpretacion = []

    # Agotamiento emocional
    if agotamiento >= 27:
        interpretacion.append("😫 Presentas un nivel ALTO de agotamiento emocional. Esto significa que podrías estar sintiendo un cansancio importante relacionado con tu trabajo o actividades. ¡Recuerda que pedir ayuda y tomarte un respiro está bien!")
    elif agotamiento >= 17:
        interpretacion.append("😌 Tu nivel de agotamiento emocional es MEDIO. Es un buen momento para cuidar tu bienestar y buscar pequeños cambios que te ayuden a relajarte y recargar energías.")
    else:
        interpretacion.append("🎉 ¡Felicidades! Tu nivel de agotamiento emocional es BAJO. Estás manejando muy bien el estrés y el cansancio diario.")

    # Despersonalización
    if despersonalizacion >= 13:
        interpretacion.append("🧊 Tu nivel de despersonalización es ALTO. Esto puede indicar que te estás distanciando o sintiendo menos conexión con las personas o tu entorno laboral. Conversar con alguien de confianza puede ayudarte a reconectar.")
    elif despersonalizacion >= 7:
        interpretacion.append("🤔 Tu nivel de despersonalización es MEDIO. Es importante que sigas atento a cómo te relacionas con los demás y busques espacios de apoyo si lo necesitas.")
    else:
        interpretacion.append("🤝 ¡Muy bien! Tu nivel de despersonalización es BAJO. Mantienes una buena relación y conexión con tu entorno.")

    # Realización personal
    if realizacion <= 31:
        interpretacion.append("😕 Tu nivel de realización personal es BAJO. Quizás sientes que no estás logrando tus metas o que tu trabajo no te resulta tan satisfactorio. Recuerda que siempre puedes buscar nuevas motivaciones o hablar con alguien sobre tus inquietudes.")
    elif realizacion <= 38:
        interpretacion.append("🙂 Tu nivel de realización personal es MEDIO. Hay espacio para que te sientas aún más satisfecho con tus logros. ¡Sigue avanzando y reconoce tus éxitos!")
    else:
        interpretacion.append("🏆 ¡Excelente! Tu nivel de realización personal es ALTO. Te sientes realizado y satisfecho con lo que haces. ¡Sigue así!")

    # Diagnóstico general SIEMPRE presente
    if agotamiento >= 27 and despersonalizacion >= 13 and realizacion <= 31:
        interpretacion.append("⚠️ Diagnóstico general: Tus resultados sugieren un riesgo ALTO de burnout. Es importante que te cuides, busques apoyo y converses con alguien de confianza o un profesional si lo necesitas. ¡Tu bienestar es lo más importante!")
    elif agotamiento < 17 and despersonalizacion < 7 and realizacion > 38:
        interpretacion.append("🌟 Diagnóstico general: ¡Felicitaciones! Tus resultados muestran un muy buen estado de bienestar. Sigue cuidándote y manteniendo esos hábitos positivos.")
    else:
        interpretacion.append("📝 Diagnóstico general: Tus resultados no indican un riesgo alto de burnout, pero recuerda siempre cuidar tu salud mental y buscar apoyo si lo necesitas. ¡Sigue atento a tu bienestar!")

    return interpretacion

def faceapi_emotion_view(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if not photo:
            return JsonResponse({'error': 'No se recibió la imagen.'})

        try:
            # Leer la imagen y convertir a formato compatible con DeepFace
            img = Image.open(photo)
            img = img.convert('RGB')
            img_np = np.array(img)

            # Analizar emociones
            result = DeepFace.analyze(img_path=img_np, actions=['emotion'], enforce_detection=False)
            # DeepFace.analyze devuelve una lista de dicts si hay más de un rostro
            if isinstance(result, list):
                result = result[0]
            emotions = result['emotion']
            emotions_str = "<br>".join([f"{k.capitalize()}: {round(v, 2)}%" for k, v in emotions.items()])
            return JsonResponse({'emotions': emotions_str})
        except Exception as e:
            return JsonResponse({'error': f'Error al analizar la imagen: {str(e)}'})

    return render(request, 'mbi/faceapi_emotion.html')
