from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Excluir la opción 'admin' del campo role
        self.fields['role'].choices = [choice for choice in User.ROLE_CHOICES if choice[0] != 'admin']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Excluir la opción 'admin' del campo role
        self.fields['role'].choices = [choice for choice in User.ROLE_CHOICES if choice[0] != 'admin']

class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)