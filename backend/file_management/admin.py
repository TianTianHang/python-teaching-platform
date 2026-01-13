from django.contrib import admin

from file_management.models import FileEntry, Folder

# Register your models here.
admin.site.register(FileEntry)
admin.site.register(Folder)