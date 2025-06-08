from django import forms
from .models import Team

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class JoinTeamForm(forms.Form):
    code = forms.CharField(label="Código de invitación", max_length=6)