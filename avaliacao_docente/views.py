from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import RegistroForm, GerenciarRoleForm
from .models import DiarioProfessorDisciplina, Diario, RespostaAluno, Avaliacao, Aluno
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
    success_url = reverse_lazy("inicio")  # Altere para o nome correto

    def form_valid(self, form):
        usuario = form.save()
        # Atribui automaticamente a role "aluno" para novos usuários
        assign_role(usuario, "aluno")
        login(self.request, usuario)
        return super().form_valid(form)


# Tela para avaliações, mas será apresentado por diario
class Avaliacoes(LoginRequiredMixin, TemplateView):
    template_name = "avaliacoes.html"
    context_object_name = "avaliacao_docente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["avaliacoes"] = Avaliacao.objects.all()  # Altere para o modelo correto
        return context


def get_aluno_from_user(user):
    try:
        return Aluno.objects.get(aluno_nome=user.username)
    except Aluno.DoesNotExist:
        return None


@login_required
def diarios_usuario(request):
    aluno = get_aluno_from_user(request.user)
    if not aluno:
        return JsonResponse({"error": "Aluno não encontrado."}, status=404)
    diarios = Diario.objects.filter(entradas__aluno=aluno).distinct()
    diarios_list = [
        {"id": d.id, "periodo": d.diario_periodo, "ano": d.ano_letivo} for d in diarios
    ]
    return JsonResponse({"diarios": diarios_list})


@login_required
def avaliacoes_por_diario(request, diario_id):
    diario = get_object_or_404(Diario, id=diario_id)
    aluno = get_aluno_from_user(request.user)
    if not aluno:
        return JsonResponse({"error": "Aluno não encontrado."}, status=404)

    avaliacoes = Avaliacao.objects.filter(
        professor_disciplina__diarios__diario=diario,
        professor_disciplina__diarios__aluno=aluno,
    ).distinct()

    avaliacoes_list = [
        {
            "id": a.id,
            "professor": str(a.professor_disciplina.professor),
            "disciplina": str(a.professor_disciplina.disciplina),
            "data_inicio": a.data_inicio.strftime("%d/%m/%Y"),
            "data_fim": a.data_fim.strftime("%d/%m/%Y"),
            "status": a.status_avaliacao,
        }
        for a in avaliacoes
    ]

    return JsonResponse(
        {"avaliacoes": avaliacoes_list, "diario": diario},
    )


@login_required
def avaliacoes_anteriores(request):
    aluno = get_aluno_from_user(request.user)
    if not aluno:
        return render(request, "avaliacoes.html", {"avaliacoes_recentes": None})
    diarios = Diario.objects.filter(entradas__aluno=aluno).distinct()
    return render(request, "avaliacoes.html", {"diarios": diarios})
