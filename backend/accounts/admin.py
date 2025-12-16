# backend/accounts/admin.py
from django.contrib import admin
from .models import User

# admin.site.register(User, UserAdmin)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 指定自定义模板
    change_list_template = "admin/user_list.html"
    list_display = ('username', 'email','last_login','date_joined')
    list_filter = ('username', 'last_login','date_joined',"is_staff")
    search_fields = ('username',)
