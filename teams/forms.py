from django import forms
from .models import Team, Integrante, Proyecto, Rol, Equipo

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class JoinTeamForm(forms.Form):
    code = forms.CharField(label="Código de invitación", max_length=6)



class IntegranteForm(forms.ModelForm):
    class Meta:
        model = Integrante
        fields = '__all__'

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = '__all__'