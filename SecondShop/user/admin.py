from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import UserChangeForm,UserCreationForm,PasswordChangeForm

from .models import MyUser
# Register your models here.

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = PasswordChangeForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'nickname', 'telephone', 'avatar', 'address', 'major', 'is_admin','is_active')
    list_filter = ('is_admin','is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('nickname', 'telephone', 'avatar', 'address', 'major')}),
        ('Permissions', {'fields': ('is_admin','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nickname', 'telephone', 'avatar', 'address', 'major', 'password1', 'password2')
            }
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()

# Re-register UserAdmin
admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
