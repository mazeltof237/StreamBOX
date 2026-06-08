from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()


class StreamBoxLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email ou nom d'utilisateur",
        widget=forms.TextInput(attrs={"placeholder": "Email or phone number"}),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("name", "avatar_preset", "is_kid", "avatar", "pin")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nom du profil"}),
            "pin": forms.TextInput(attrs={"placeholder": "PIN 4 chiffres (optionnel)", "maxlength": "4", "inputmode": "numeric"}),
        }
