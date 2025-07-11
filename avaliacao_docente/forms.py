from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Curso,
    PerfilProfessor,
    Disciplina,
    PeriodoLetivo,
    Turma,
    PerfilAluno,
)


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
    Form para gerenciar permissões de usuários
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
        queryset=PerfilProfessor.non_admin.all(),
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


class DisciplinaForm(forms.ModelForm):
    """
    Form para criação e edição de disciplinas
    """

    disciplina_nome = forms.CharField(
        max_length=100,
        required=True,
        label="Nome da Disciplina",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite o nome da disciplina",
            }
        ),
    )
    disciplina_sigla = forms.CharField(
        max_length=45,
        required=True,
        label="Sigla da Disciplina",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite a sigla da disciplina",
            }
        ),
    )
    disciplina_tipo = forms.ChoiceField(
        required=True,
        label="Tipo da Disciplina",
        choices=Disciplina.TIPO_CHOICES,
        widget=forms.Select(
            attrs={"class": "form-control"},
        ),
    )
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Curso",
    )
    professor = forms.ModelChoiceField(
        queryset=PerfilProfessor.non_admin.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Professor Responsável",
    )
    periodo_letivo = forms.ModelChoiceField(
        queryset=PeriodoLetivo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Período Letivo",
        required=True,
    )

    class Meta:
        model = Disciplina
        fields = [
            "disciplina_nome",
            "disciplina_sigla",
            "disciplina_tipo",
            "curso",
            "professor",
            "periodo_letivo",
        ]

    def clean_disciplina_nome(self):
        disciplina_nome = self.cleaned_data.get("disciplina_nome")
        curso = self.cleaned_data.get("curso")
        if disciplina_nome and curso:
            # Verifica se a disciplina já existe no mesmo curso
            if Disciplina.objects.filter(
                disciplina_nome__iexact=disciplina_nome, curso=curso
            ).exists():
                raise forms.ValidationError("Esta disciplina já existe neste curso.")
        return disciplina_nome


class PeriodoLetivoForm(forms.ModelForm):

    nome = forms.CharField(
        max_length=50,
        required=True,
        label="Nome do Período",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ex: Período Letivo 2024.1"}
        ),
    )
    ano = forms.IntegerField(
        required=True,
        label="Ano",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "2024",
                "min": "2020",
                "max": "2030",
            }
        ),
    )
    semestre = forms.ChoiceField(
        required=True,
        label="Semestre",
        choices=PeriodoLetivo.SEMESTRE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = PeriodoLetivo
        fields = ["nome", "ano", "semestre"]

    def clean(self):
        cleaned_data = super().clean()
        ano = cleaned_data.get("ano")
        semestre = cleaned_data.get("semestre")

        if ano and semestre:
            # Verifica se já existe um período para o mesmo ano e semestre
            if PeriodoLetivo.objects.filter(ano=ano, semestre=semestre).exists():
                raise forms.ValidationError(
                    f"Já existe um período cadastrado para {ano}.{semestre}"
                )

        return cleaned_data


class TurmaForm(forms.ModelForm):
    """
    Form para criação e edição de turmas
    """

    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Disciplina",
    )
    professor = forms.ModelChoiceField(
        queryset=PerfilProfessor.non_admin.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Professor",
    )
    periodo_letivo = forms.ModelChoiceField(
        queryset=PeriodoLetivo.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Período Letivo",
    )
    turno = forms.ChoiceField(
        choices=[("", "--- Selecione ---")] + Turma.TURNO_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Turno",
    )

    class Meta:
        model = Turma
        fields = [
            "disciplina",
            "professor",
            "periodo_letivo",
            "turno",
        ]

    def clean(self):
        cleaned_data = super().clean()
        disciplina = cleaned_data.get("disciplina")
        periodo_letivo = cleaned_data.get("periodo_letivo")
        turno = cleaned_data.get("turno")

        if disciplina and periodo_letivo and turno:
            # Verifica se já existe uma turma para essa disciplina no mesmo período e turno
            if Turma.objects.filter(
                disciplina=disciplina,
                periodo_letivo=periodo_letivo,
                turno=turno,
            ).exists():
                raise forms.ValidationError(
                    f"Já existe uma turma de {disciplina.disciplina_nome} "
                    f"no período {periodo_letivo} no turno {turno}."
                )

        return cleaned_data
