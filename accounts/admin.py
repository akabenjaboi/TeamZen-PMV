from django.contrib import admin
from .models import User  # Si tienes un modelo User personalizado

admin.site.register(User)
