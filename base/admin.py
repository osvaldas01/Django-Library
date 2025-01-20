from django.contrib import admin
from .models import Books, Topic, Message

admin.site.register(Books)
admin.site.register(Topic)
admin.site.register(Message)