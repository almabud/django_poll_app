from django.contrib import admin

# Register your models here.
from poll.models import Question

admin.site.register(Question)
