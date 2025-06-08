from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, EditProfileForm, EmailLoginForm
from django.contrib import messages
from .models import User
from teams.models import Team
from mbi.models import MBIResult
from mbi.views import interpretar_mbi

def home_view(request):
    return render(request, 'base/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})  # Cambiado

def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    return redirect('home')
                else:
                    return render(request, 'accounts/login.html', {'form': form, 'error': 'Credenciales inválidas'})
            except User.DoesNotExist:
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Credenciales inválidas'})
    else:
        form = EmailLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    # Solo tests personales (no asociados a equipo)
    mbi_history = MBIResult.objects.filter(user=request.user, team__isnull=True).order_by('-date')
    return render(request, 'accounts/profile.html', {
        'mbi_history': mbi_history,
        
        # ...otros contextos que ya uses...
    })

@login_required
def edit_profile_view(request):
    user = request.user
    old_role = user.role
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            new_role = form.cleaned_data['role']
            if old_role == 'lider' and new_role == 'empleado':
                # Eliminar equipos donde el usuario es líder
                Team.objects.filter(leader=user).delete()
            elif old_role == 'empleado' and new_role == 'lider':
                # Salir de todos los equipos
                user.teams.clear()
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
