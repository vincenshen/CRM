from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.
from utils import export_csv
from SCMC.models import MyUser, Course, Role, Menu, SubMenu, Customer, CustomerSource, Tag


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields, plus a repeated password.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ("username", "email", "password")

    def clean_password2(self):
        """Check that the two password entries math"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if all([password1, password2, password1 != password2]):
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Save the provided password in hashed format"""
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on the user,
    but replaces the password field with admin's password hash display field."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ("email", "password", "is_admin", "is_active")

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances.
    # form = UserChangeForm
    # add_form = UserCreationForm

    list_display = ("username", "email", "is_admin", "is_active", "role")
    list_filter = ("is_admin", "is_active", "role", "username")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_admin", "is_active", "role")})
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("username", "email", "password1", "password2")}),
    )
    ordering = ("email",)
    filter_horizontal = ()


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "qq", "consultant", "source", "status")
    list_filter = ("consultant", "source", "status")
    search_fields = ("name", "source__name")
    filter_horizontal = ["tags", "consult_courses"]
    actions = [export_csv.export_as_csv]

admin.site.register(MyUser, UserAdmin)
admin.site.register(Course)
admin.site.register(Role)
admin.site.register(Menu)
admin.site.register(SubMenu)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Tag)