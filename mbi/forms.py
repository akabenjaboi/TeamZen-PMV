from django import forms
from .models import MBIQuestion

class MBIForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (1, "Nunca"),
            (2, "Algunas veces al año"),
            (3, "Algunas veces al mes"),
            (4, "Algunas veces a la semana"),
            (5, "Diariamente"),
        ]
        for question in MBIQuestion.objects.all():
            self.fields[f"q_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )