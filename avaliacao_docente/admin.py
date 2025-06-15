from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from .models import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    CoordenadorCurso,
    Disciplina,
    ProfessorDisciplina,
    Diario,
    DiarioProfessorDisciplina,
    Avaliacao,
    Pergunta,
    AvaliacaoPergunta,
    RespostaAluno,
)


class PerfilAlunoInline(admin.StackedInline):
    model = PerfilAluno
    can_delete = False
    verbose_name_plural = "Perfil de Aluno"


class PerfilProfessorInline(admin.StackedInline):
    model = PerfilProfessor
    can_delete = False
    verbose_name_plural = "Perfil de Professor"


class CustomUserAdmin(DefaultUserAdmin):
    """
    Admin customizado que mostra as roles dos usuários
    """

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "get_user_role",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")

    def get_user_role(self, obj):
        """Retorna a role do usuário"""
        if has_role(obj, "admin"):
            return "Administrador"
        elif has_role(obj, "coordenador"):
            return "Coordenador"
        elif has_role(obj, "professor"):
            return "Professor"
        elif has_role(obj, "aluno"):
            return "Aluno"
        return "Sem role"

    get_user_role.short_description = "Role"

    def get_inlines(self, request, obj):
        """
        Mostra o inline apropriado baseado na role do usuário
        """
        if obj and has_role(obj, "aluno"):
            return [PerfilAlunoInline]
        elif obj and (has_role(obj, "professor") or has_role(obj, "coordenador")):
            return [PerfilProfessorInline]
        return []


# Re-registra o User com o admin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registra os modelos
admin.site.register(PerfilAluno)
admin.site.register(PerfilProfessor)
admin.site.register(Curso)
admin.site.register(CoordenadorCurso)
admin.site.register(Disciplina)
admin.site.register(ProfessorDisciplina)
admin.site.register(Diario)
admin.site.register(DiarioProfessorDisciplina)
admin.site.register(Avaliacao)
admin.site.register(Pergunta)
admin.site.register(AvaliacaoPergunta)
admin.site.register(RespostaAluno)
