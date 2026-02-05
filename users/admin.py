from django.contrib import admin
from .models import UserAccount, RealtorProfile

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff')
    search_fields = ('email', 'name')

admin.site.register(RealtorProfile)



