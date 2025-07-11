from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from .models import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    Disciplina,
    Avaliacao,
    Pergunta,
    AvaliacaoPergunta,
    RespostaAluno,
    PeriodoLetivo,
    Turma,
    MatriculaTurma,
    HorarioTurma,
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
        "get_user_profile",
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

    def get_user_profile(self, obj):
        """Retorna o tipo de perfil do usuário"""
        # Admins não devem ter perfis específicos
        if has_role(obj, "admin"):
            return "Admin (sem perfil)"

        profiles = []
        if hasattr(obj, "perfil_aluno"):
            profiles.append("Aluno")
        if hasattr(obj, "perfil_professor"):
            profiles.append("Professor")

        if profiles:
            return " + ".join(profiles)
        return "Sem perfil"

    get_user_profile.short_description = "Perfil"

    def get_inlines(self, request, obj):
        """
        Mostra o inline apropriado baseado na role do usuário
        Admins não devem ter perfis específicos
        """
        if obj and has_role(obj, "admin"):
            return []  # Admins não têm perfis
        elif obj and has_role(obj, "aluno"):
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
admin.site.register(Disciplina)
admin.site.register(PeriodoLetivo)
admin.site.register(Turma)
admin.site.register(MatriculaTurma)
admin.site.register(HorarioTurma)
admin.site.register(Avaliacao)
admin.site.register(Pergunta)
admin.site.register(AvaliacaoPergunta)
admin.site.register(RespostaAluno)
