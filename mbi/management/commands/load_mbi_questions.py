from django.core.management.base import BaseCommand
from mbi.models import MBIQuestion

QUESTIONS = [
    ("Me siento emocionalmente defraudado en mi trabajo", "agotamiento"),
    ("Cuando termino mi jornada de trabajo me siento agotado", "agotamiento"),
    ("Cuando me levanto por la mañana y me enfrento a otra jornada de trabajo me siento agotado", "agotamiento"),
    ("Siento que puedo entender fácilmente a las personas que tengo que atender", "realizacion"),
    ("Siento que estoy tratando a algunos beneficiados de mí, como si fuesen objetos impersonales", "despersonalizacion"),
    ("Siento que trabajar todo el día con la gente me cansa", "agotamiento"),
    ("Siento que trato con mucha efectividad los problemas de las personas a las que tengo que atender", "realizacion"),
    ("Siento que mi trabajo me está desgastando", "agotamiento"),
    ("Siento que estoy influyendo positivamente en las vidas de otras personas a través de mi trabajo", "realizacion"),
    ("Siento que me he hecho más duro con la gente", "despersonalizacion"),
    ("Me preocupa que este trabajo me está endureciendo emocionalmente", "despersonalizacion"),
    ("Me siento muy enérgico en mi trabajo", "realizacion"),
    ("Me siento frustrado por el trabajo", "agotamiento"),
    ("Siento que estoy demasiado tiempo en mi trabajo", "agotamiento"),
    ("Siento que realmente no me importa lo que les ocurra a las personas a las que tengo que atender profesionalmente", "despersonalizacion"),
    ("Siento que trabajar en contacto directo con la gente me cansa", "agotamiento"),
    ("Siento que puedo crear con facilidad un clima agradable en mi trabajo", "realizacion"),
    ("Me siento estimulado después de haber trabajado íntimamente con quienes tengo que atender", "realizacion"),
    ("Creo que consigo muchas cosas valiosas en este trabajo", "realizacion"),
    ("Me siento como si estuviera al límite de mis posibilidades", "agotamiento"),
    ("Siento que en mi trabajo los problemas emocionales son tratados de forma adecuada", "realizacion"),
    ("Me parece que los beneficiarios de mi trabajo me culpan de algunos problemas", "despersonalizacion"),
]

class Command(BaseCommand):
    help = 'Carga las preguntas del test MBI'

    def handle(self, *args, **kwargs):
        for text, dimension in QUESTIONS:
            MBIQuestion.objects.get_or_create(text=text, dimension=dimension)
        self.stdout.write(self.style.SUCCESS('Preguntas MBI cargadas correctamente.'))