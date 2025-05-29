from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Curso,
    Professor,
    CoordenadorCurso,
    Disciplina,
    ProfessorDisciplina,
    Diario,
    Aluno,
    DiarioProfessorDisciplina,
    Avaliacao,
    Pergunta,
    AvaliacaoPergunta,
    RespostaAluno,
)
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role


class CustomUserAdmin(UserAdmin):
    """
    Administrador customizado para usuários com gerenciamento de roles
    """

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_user_role",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")

    fieldsets = UserAdmin.fieldsets + (("Roles", {"fields": ("user_role",)}),)

    def get_user_role(self, obj):
        """Retorna a role atual do usuário"""
        if has_role(obj, "admin"):
            return "Administrador"
        elif has_role(obj, "coordenador"):
            return "Coordenador"
        elif has_role(obj, "professor"):
            return "Professor"
        elif has_role(obj, "aluno"):
            return "Aluno"
        else:
            return "Sem role definida"

    get_user_role.short_description = "Role"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Adiciona campo para seleção de role
        if obj:
            current_role = "aluno"  # padrão
            if has_role(obj, "admin"):
                current_role = "admin"
            elif has_role(obj, "coordenador"):
                current_role = "coordenador"
            elif has_role(obj, "professor"):
                current_role = "professor"
            elif has_role(obj, "aluno"):
                current_role = "aluno"

            from django import forms

            form.base_fields["user_role"] = forms.ChoiceField(
                choices=[
                    ("admin", "Administrador"),
                    ("coordenador", "Coordenador"),
                    ("professor", "Professor"),
                    ("aluno", "Aluno"),
                ],
                initial=current_role,
                required=True,
                help_text="Selecione a role do usuário no sistema",
            )

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Gerencia as roles
        if "user_role" in form.cleaned_data:
            new_role = form.cleaned_data["user_role"]

            # Remove todas as roles existentes
            for role in ["admin", "coordenador", "professor", "aluno"]:
                if has_role(obj, role):
                    remove_role(obj, role)

            # Atribui a nova role
            assign_role(obj, new_role)


# Registra o UserAdmin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Registra os models da aplicação
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("curso_nome",)
    search_fields = ("curso_nome",)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("professor_nome", "registro_academico")
    search_fields = ("professor_nome", "registro_academico")


@admin.register(CoordenadorCurso)
class CoordenadorCursoAdmin(admin.ModelAdmin):
    list_display = ("professor", "curso")
    list_filter = ("curso",)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("disciplina_nome", "disciplina_sigla", "disciplina_tipo", "curso")
    list_filter = ("disciplina_tipo", "curso")
    search_fields = ("disciplina_nome", "disciplina_sigla")


@admin.register(ProfessorDisciplina)
class ProfessorDisciplinaAdmin(admin.ModelAdmin):
    list_display = ("professor", "disciplina")
    list_filter = ("disciplina__curso",)


@admin.register(Diario)
class DiarioAdmin(admin.ModelAdmin):
    list_display = ("diario_periodo", "ano_letivo")
    list_filter = ("ano_letivo", "diario_periodo")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("aluno_nome", "aluno_matricula", "aluno_email", "aluno_situacao")
    search_fields = ("aluno_nome", "aluno_matricula", "aluno_email")
    list_filter = ("aluno_situacao",)


@admin.register(DiarioProfessorDisciplina)
class DiarioProfessorDisciplinaAdmin(admin.ModelAdmin):
    list_display = ("diario", "professor_disciplina", "aluno")
    list_filter = ("diario__ano_letivo", "professor_disciplina__disciplina__curso")


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "professor_disciplina",
        "data_inicio",
        "data_fim",
        "status_avaliacao",
    )
    list_filter = ("status_avaliacao", "data_inicio", "data_fim")
    date_hierarchy = "data_inicio"


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("enunciado_pergunta", "tipo_pergunta")
    list_filter = ("tipo_pergunta",)
    search_fields = ("enunciado_pergunta",)


@admin.register(AvaliacaoPergunta)
class AvaliacaoPerguntaAdmin(admin.ModelAdmin):
    list_display = ("avaliacao", "pergunta")
    list_filter = ("avaliacao__status_avaliacao",)


@admin.register(RespostaAluno)
class RespostaAlunoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "avaliacao_pergunta", "resposta_pergunta")
    list_filter = ("avaliacao_pergunta__avaliacao__status_avaliacao",)
    search_fields = ("resposta_pergunta",)
