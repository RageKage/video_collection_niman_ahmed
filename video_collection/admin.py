from django.contrib import admin

# Register your models here.

from .models import Video

admin.site.register(Video) # this will register the Video model with the admin site
