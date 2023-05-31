from django.contrib.auth.forms import BaseUserCreationForm

from messaging.models import CustomUser


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name")
