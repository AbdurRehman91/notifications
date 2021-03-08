from django.contrib import admin
from .models import User,UserDevices

class UsersAdmin(admin.ModelAdmin):
    exclude = ('user_permissions',)

#registering User model to django admin
admin.site.register(UserDevices, UsersAdmin)
admin.site.register(User, UsersAdmin)