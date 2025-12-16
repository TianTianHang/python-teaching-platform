# backend/accounts/admin.py
from django.contrib import admin
from .models import MembershipType, Subscription, User

# admin.site.register(User, UserAdmin)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 指定自定义模板
    change_list_template = "admin/user_list.html"
    list_display = ('username', 'email','last_login','date_joined')
    list_filter = ('username', 'last_login','date_joined',"is_staff")
    search_fields = ('username',)

@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('membership_type', 'is_active')
    search_fields = ('user__username',)