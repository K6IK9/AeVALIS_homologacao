from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import (
    RegistroForm,
    GerenciarRoleForm,
    CursoForm,
    DisciplinaForm,
    PeriodoLetivoForm,
)
from .models import (
    Avaliacao,
    PerfilAluno,
    PerfilProfessor,
    Curso,
    Disciplina,
    PeriodoLetivo,
)
from django.contrib.auth.models import User

from django.http import JsonResponse
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role
from django.contrib import messages


@login_required
def gerenciar_roles(request):
    """
    View para gerenciar roles de usuários
    Apenas coordenadores e admins podem acessar
    """
    if not (has_role(request.user, "coordenador") or has_role(request.user, "admin")):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = GerenciarRoleForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data["usuario"]
            nova_role = form.cleaned_data["role"]

            # Remove todas as roles existentes
            for role in ["admin", "coordenador", "professor", "aluno"]:
                if has_role(usuario, role):
                    remove_role(usuario, role)

            # Atribui a nova role
            assign_role(usuario, nova_role)

            # Cria o perfil específico se necessário
            if nova_role == "aluno":
                PerfilAluno.objects.get_or_create(user=usuario)
            elif nova_role == "professor" or nova_role == "coordenador":
                PerfilProfessor.objects.get_or_create(
                    user=usuario, defaults={"registro_academico": usuario.username}
                )

            messages.success(
                request,
                f"Role de {usuario.username} alterada para {nova_role} com sucesso!",
            )
            return redirect("gerenciar_roles")
    else:
        form = GerenciarRoleForm()

    # Lista todos os usuários com suas roles
    usuarios_com_roles = []
    for user in User.objects.all().order_by("username"):
        role_atual = "Sem role"
        if has_role(user, "admin"):
            role_atual = "Administrador"
        elif has_role(user, "coordenador"):
            role_atual = "Coordenador"
        elif has_role(user, "professor"):
            role_atual = "Professor"
        elif has_role(user, "aluno"):
            role_atual = "Aluno"

        usuarios_com_roles.append({"usuario": user, "role": role_atual})

    context = {"form": form, "usuarios_com_roles": usuarios_com_roles}

    return render(request, "gerenciar_roles.html", context)


@login_required
def gerenciar_cursos(request):
    """
    View para gerenciar cursos
    Apenas coordenadores e admins podem acessar
    """
    if not (has_role(request.user, "coordenador") or has_role(request.user, "admin")):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            messages.success(
                request,
                f"Curso '{curso.curso_nome}' criado com sucesso!",
            )
            return redirect("gerenciar_cursos")
    else:
        form = CursoForm()

    # Lista todos os cursos
    cursos = Curso.objects.all().order_by("curso_nome")

    context = {"form": form, "cursos": cursos}

    return render(request, "gerenciar_cursos.html", context)


@login_required
def gerenciar_disciplinas(request):
    """
    View para gerenciar disciplinas
    Apenas coordenadores e admins podem acessar
    """
    if not (has_role(request.user, "coordenador") or has_role(request.user, "admin")):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(
                request,
                f"Disciplina '{disciplina.disciplina_nome}' criada com sucesso!",
            )
            return redirect("gerenciar_disciplinas")
        else:
            # Debug: Mostra os erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
            messages.error(request, "Verifique os dados do formulário.")
    else:
        form = DisciplinaForm()

    # Lista todas as disciplinas
    disciplinas = Disciplina.objects.all().order_by("disciplina_nome")

    context = {"form": form, "disciplinas": disciplinas}

    return render(request, "gerenciar_disciplinas.html", context)


@login_required
def gerenciar_periodos(request):
    """
    View para gerenciar períodos letivos
    Apenas coordenadores e admins podem acessar
    """
    if not (has_role(request.user, "coordenador") or has_role(request.user, "admin")):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            periodo = form.save()
            messages.success(
                request,
                f"Período '{periodo.nome}' criado com sucesso!",
            )
            return redirect("gerenciar_periodos")
    else:
        form = PeriodoLetivoForm()

    # Lista todos os períodos
    periodos = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    context = {"form": form, "periodos": periodos}

    return render(request, "gerenciar_periodos.html", context)


# Pagina admin_hub
class AdminHubView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_hub.html"


# Painel principal
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "inicial.html"
    context_object_name = "avaliacao_docente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Tela para registros de usuarios
class RegistrarUsuarioView(CreateView):
    form_class = RegistroForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("inicio")

    def form_valid(self, form):
        # Salva o usuário com todos os campos
        usuario = form.save(commit=False)
        usuario.first_name = form.cleaned_data["first_name"]
        usuario.last_name = form.cleaned_data["last_name"]
        usuario.email = form.cleaned_data["email"]
        usuario.save()

        # Atribui automaticamente a role "aluno" para novos usuários
        assign_role(usuario, "aluno")

        # Cria o perfil de aluno
        PerfilAluno.objects.create(user=usuario)

        login(self.request, usuario)
        return super().form_valid(form)


# Tela para avaliações, mas será apresentado por diario
class Avaliacoes(LoginRequiredMixin, TemplateView):
    template_name = "avaliacoes.html"
    context_object_name = "avaliacao_docente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["avaliacoes"] = Avaliacao.objects.all()
        return context


def get_perfil_aluno_from_user(user):
    """
    Função simplificada - agora usa o relacionamento OneToOne
    """
    try:
        return user.perfil_aluno
    except PerfilAluno.DoesNotExist:
        return None
