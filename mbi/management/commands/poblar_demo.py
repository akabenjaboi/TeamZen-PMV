from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from teams.models import Team
from mbi.models import MBIResult

class Command(BaseCommand):
    help = 'Pobla la base de datos con un líder, dos equipos, trabajadores y resultados MBI de ejemplo'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Crear líder
        lider, _ = User.objects.get_or_create(username='lider', email='lider@demo.com')
        lider.set_password('demo123')
        lider.save()

        # Crear equipos
        equipo1, _ = Team.objects.get_or_create(name='Equipo Burnout', leader=lider)
        equipo2, _ = Team.objects.get_or_create(name='Equipo Zen', leader=lider)

        # Crear trabajadores para equipo 1 (burnout)
        burnout_workers = []
        for i in range(1, 5):
            user, _ = User.objects.get_or_create(username=f'burnout{i}', email=f'burnout{i}@demo.com')
            user.set_password('demo123')
            user.save()
            burnout_workers.append(user)
        equipo1.members.add(*burnout_workers)

        # Crear trabajadores para equipo 2 (bienestar)
        zen_workers = []
        for i in range(1, 5):
            user, _ = User.objects.get_or_create(username=f'zen{i}', email=f'zen{i}@demo.com')
            user.set_password('demo123')
            user.save()
            zen_workers.append(user)
        equipo2.members.add(*zen_workers)

        # Resultados MBI para equipo 1 (burnout notorio)
        MBIResult.objects.get_or_create(user=burnout_workers[0], team=equipo1, defaults={
            'agotamiento': 32, 'despersonalizacion': 16, 'realizacion': 25
        })
        MBIResult.objects.get_or_create(user=burnout_workers[1], team=equipo1, defaults={
            'agotamiento': 29, 'despersonalizacion': 14, 'realizacion': 28
        })
        MBIResult.objects.get_or_create(user=burnout_workers[2], team=equipo1, defaults={
            'agotamiento': 31, 'despersonalizacion': 15, 'realizacion': 27
        })
        # burnout_workers[3] no responde (sin resultado)

        # Resultados MBI para equipo 2 (bienestar)
        MBIResult.objects.get_or_create(user=zen_workers[0], team=equipo2, defaults={
            'agotamiento': 10, 'despersonalizacion': 3, 'realizacion': 42
        })
        MBIResult.objects.get_or_create(user=zen_workers[1], team=equipo2, defaults={
            'agotamiento': 12, 'despersonalizacion': 2, 'realizacion': 40
        })
        MBIResult.objects.get_or_create(user=zen_workers[2], team=equipo2, defaults={
            'agotamiento': 9, 'despersonalizacion': 4, 'realizacion': 41
        })
        # zen_workers[3] no responde (sin resultado)

        self.stdout.write(self.style.SUCCESS('Datos demo creados correctamente.'))