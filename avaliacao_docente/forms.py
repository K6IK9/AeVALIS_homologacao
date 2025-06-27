from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Curso, PerfilCoordenador


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nome",
        widget=forms.TextInput(attrs={"placeholder": "Nome"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Sobrenome",
        widget=forms.TextInput(attrs={"placeholder": "Sobrenome"}),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email Institucional",
        widget=forms.EmailInput(attrs={"placeholder": "Email institucional"}),
    )
    username = forms.CharField(
        required=True,
        label="Matrícula",
        widget=forms.TextInput(attrs={"placeholder": "Matrícula"}),
    )
    password1 = forms.CharField(
        required=True,
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Senha"}),
    )
    password2 = forms.CharField(
        required=True,
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirme a senha"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Verifica se o email já existe
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Este email já está sendo usado por outro usuário."
                )

        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Validação para formato de matrícula (opcional - pode ser personalizada)
            if not username.isdigit():
                raise forms.ValidationError("A matrícula deve conter apenas números.")
            if len(username) < 6:
                raise forms.ValidationError(
                    "A matrícula deve ter pelo menos 6 dígitos."
                )

        return username


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


class CursoForm(forms.ModelForm):
    """
    Form para criação e edição de cursos
    """

    curso_nome = forms.CharField(
        max_length=45,
        required=True,
        label="Nome do Curso",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite o nome do curso"}
        ),
    )
    curso_sigla = forms.CharField(
        max_length=10,
        required=True,
        label="Sigla do Curso",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Digite a sigla do curso"}
        ),
    )
    coordenador_curso = forms.ModelChoiceField(
        queryset=PerfilCoordenador.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Coordenador do Curso",
    )

    class Meta:
        model = Curso
        fields = ["curso_nome", "curso_sigla", "coordenador_curso"]

    def clean_curso_nome(self):
        curso_nome = self.cleaned_data.get("curso_nome")
        if curso_nome:
            # Verifica se o curso já existe
            if Curso.objects.filter(curso_nome__iexact=curso_nome).exists():
                raise forms.ValidationError("Este curso já existe no sistema.")
        return curso_nome
