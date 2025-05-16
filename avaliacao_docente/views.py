from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import RegistroForm
from .models import DiarioProfessorDisciplina, Diario, RespostaAluno, Avaliacao, Aluno
from django.contrib.auth.models import User

from django.http import JsonResponse
from rolepermissions.roles import assign_role


#painel temporarios
def criar_usuario(request):
    # Cria um usuário temporário
    
    usuario = request.user
    
    """ usuario = User.objects.create_user(
        username="Cood",
        password="134679",
        first_name="Cood",
        last_name="Coordenador",
    ) """
    assign_role(usuario, "admin")
    return JsonResponse({"message": "Usuário criado com sucesso!"})




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
    aluno = get_aluno_from_user(request.user)
    if not aluno:
        return render(request, "avaliacoes_do_diario.html", {"avaliacoes": None})
    diario = get_object_or_404(Diario, id=diario_id)
    respostas = RespostaAluno.objects.filter(
        aluno=aluno,
        avaliacao_pergunta__avaliacao__professor_disciplina__diarios__diario=diario,
    )
    avaliacoes = set(r.avaliacao_pergunta.avaliacao for r in respostas)
    avaliacoes_list = [
        {
            "id": a.id,
            "professor_disciplina": str(a.professor_disciplina),
            "data_inicio": a.data_inicio,
            "data_fim": a.data_fim,
            "status": a.status_avaliacao,
        }
        for a in avaliacoes
    ]
    return render(
        request,
        "avaliacoes_do_diario.html",
        {"avaliacoes": avaliacoes_list, "diario": diario},
    )


@login_required
def avaliacoes_anteriores(request):
    aluno = get_aluno_from_user(request.user)
    if not aluno:
        return render(request, "avaliacoes.html", {"avaliacoes_recentes": None})
    diarios = Diario.objects.filter(entradas__aluno=aluno).distinct()
    return render(request, "avaliacoes.html", {"diarios": diarios})
