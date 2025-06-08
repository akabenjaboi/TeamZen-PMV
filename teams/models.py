from django.db import models
from accounts.models import User
import string
import random

class Team(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams', blank=True)

    def __str__(self):
        return self.name

class TeamInviteCode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_code():
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=6))

    def __str__(self):
        return f"{self.code} ({self.team.name})"

class TeamMembershipRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')],
        default='pendiente'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.team.name} ({self.status})"
