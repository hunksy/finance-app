from django.contrib import admin

# Register your models here.
from .models import Goal, Transaction

admin.site.register([Goal, Transaction])