from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Nome Completo"})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Matrícula"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Senha"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme a senha"})
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class GerenciarRoleForm(forms.Form):
    """
    Form para gerenciar roles de usuários
    """

    usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Usuário",
    )

    role = forms.ChoiceField(
        choices=[
            ("aluno", "Aluno"),
            ("professor", "Professor"),
            ("coordenador", "Coordenador"),
            ("admin", "Administrador"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Role",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordena usuários por username
        self.fields["usuario"].queryset = User.objects.all().order_by("username")
