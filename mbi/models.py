from django.db import models
from accounts.models import User
from teams.models import Team

class MBIQuestion(models.Model):
    text = models.CharField(max_length=255)
    dimension = models.CharField(
        max_length=30,
        choices=[
            ('agotamiento', 'Agotamiento emocional'),
            ('despersonalizacion', 'Despersonalización'),
            ('realizacion', 'Realización personal'),
        ]
    )

    def __str__(self):
        return self.text

class MBIResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    agotamiento = models.IntegerField()
    despersonalizacion = models.IntegerField()
    realizacion = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.date.date()})"

class MBIAnswer(models.Model):
    result = models.ForeignKey(MBIResult, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(MBIQuestion, on_delete=models.CASCADE)
    value = models.IntegerField()
