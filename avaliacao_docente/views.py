from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.db.models import Q
from .forms import (
    RegistroForm,
    GerenciarRoleForm,
    CursoForm,
    DisciplinaForm,
    PeriodoLetivoForm,
    TurmaForm,
    QuestionarioAvaliacaoForm,
    PerguntaAvaliacaoForm,
    CicloAvaliacaoForm,
)
from .models import (
    Avaliacao,
    PerfilAluno,
    PerfilProfessor,
    Curso,
    Disciplina,
    PeriodoLetivo,
    Turma,
    MatriculaTurma,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    ComentarioAvaliacao,
)
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.db.models import Q, Avg
from django.utils import timezone
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role
from .utils import check_user_permission, get_user_role_name
from django.contrib import messages
from django.core.paginator import Paginator


@login_required
def gerenciar_roles(request):
    """
    View para gerenciar roles de usuários
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
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

            # Gerenciar perfis usando função utilitária
            mensagens_perfil = gerenciar_perfil_usuario(usuario, nova_role)

            # Adicionar mensagens informativas sobre mudanças de perfil
            for msg in mensagens_perfil:
                messages.info(request, msg)

            messages.success(
                request,
                f"Role de {usuario.username} alterada para {nova_role} com sucesso!",
            )
            return redirect("gerenciar_roles")
    else:
        form = GerenciarRoleForm()

    # Obter parâmetros de filtro da URL
    busca = request.GET.get("busca", "").strip()
    filtro_role = request.GET.get("role", "")

    # Iniciar com todos os usuários
    usuarios_queryset = User.objects.all()

    # Aplicar filtro de busca por nome ou matrícula
    if busca:
        usuarios_queryset = usuarios_queryset.filter(
            Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(username__icontains=busca)
        )

    # Lista todos os usuários com suas roles
    usuarios_com_roles = []
    for user in usuarios_queryset.order_by("username"):
        role_atual = get_user_role_name(user)

        # Aplicar filtro por role
        if filtro_role:
            # Mapeamento dos filtros para os nomes das roles
            filtros_map = {
                "admin": "Administrador",
                "coordenador": "Coordenador",
                "professor": "Professor",
                "aluno": "Aluno",
                "sem_role": "Sem role",
            }

            role_esperada = filtros_map.get(filtro_role, filtro_role)
            if role_atual != role_esperada:
                continue

        usuarios_com_roles.append({"usuario": user, "role": role_atual})

    context = {
        "form": form,
        "usuarios_com_roles": usuarios_com_roles,
        "filtro_busca": busca,
        "filtro_role": filtro_role,
    }

    return render(request, "gerenciar_roles.html", context)


@login_required
def gerenciar_cursos(request):
    """
    View para gerenciar cursos
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
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
def editar_curso(request, curso_id):
    """
    View para editar um curso existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar cursos.")
        return redirect("inicio")

    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == "POST":
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Curso '{curso.curso_nome}' atualizado com sucesso!"
            )
            return redirect("gerenciar_cursos")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = CursoForm(instance=curso)

    context = {"form": form, "curso": curso, "editing": True}
    return render(request, "gerenciar_cursos.html", context)


@login_required
def excluir_curso(request, curso_id):
    """
    View para excluir um curso
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method == "POST":
        try:
            curso = get_object_or_404(Curso, id=curso_id)

            # Verificar se há disciplinas relacionadas
            if curso.disciplinas.exists():
                return JsonResponse(
                    {
                        "error": f"Não é possível excluir o curso '{curso.curso_nome}' pois existem disciplinas vinculadas a ele."
                    },
                    status=400,
                )

            nome_curso = curso.curso_nome
            curso.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Curso '{nome_curso}' excluído com sucesso!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


@login_required
def gerenciar_disciplinas(request):
    """
    View para gerenciar disciplinas
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
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
def editar_disciplina(request, disciplina_id):
    """
    View para editar uma disciplina existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar disciplinas.")
        return redirect("inicio")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Disciplina '{disciplina.disciplina_nome}' atualizada com sucesso!",
            )
            return redirect("gerenciar_disciplinas")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = DisciplinaForm(instance=disciplina)

    context = {
        "form": form,
        "disciplina": disciplina,
        "editing": True,
    }
    return render(request, "gerenciar_disciplinas.html", context)


@login_required
def excluir_disciplina(request, disciplina_id):
    """
    View para excluir uma disciplina
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method == "POST":
        try:
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)

            # Verificar se há turmas relacionadas
            if disciplina.turmas.exists():
                return JsonResponse(
                    {
                        "error": f"Não é possível excluir a disciplina '{disciplina.disciplina_nome}' pois existem turmas vinculadas a ela."
                    },
                    status=400,
                )

            nome_disciplina = disciplina.disciplina_nome
            disciplina.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Disciplina '{nome_disciplina}' excluída com sucesso!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


@login_required
def gerenciar_periodos(request):
    """
    View para gerenciar períodos letivos
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
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


@login_required
def editar_periodo(request, periodo_id):
    """
    View para editar um período letivo existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar períodos.")
        return redirect("inicio")

    periodo = get_object_or_404(PeriodoLetivo, id=periodo_id)

    if request.method == "POST":
        form = PeriodoLetivoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Período '{periodo.nome}' atualizado com sucesso!"
            )
            return redirect("gerenciar_periodos")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = PeriodoLetivoForm(instance=periodo)

    context = {
        "form": form,
        "periodo": periodo,
        "periodos": PeriodoLetivo.objects.all().order_by("-ano", "-semestre"),
        "editing": True,
    }
    return render(request, "gerenciar_periodos.html", context)


@login_required
def excluir_periodo(request, periodo_id):
    """
    View para excluir um período letivo
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method == "POST":
        try:
            periodo = get_object_or_404(PeriodoLetivo, id=periodo_id)

            # Verificar se há turmas ou disciplinas relacionadas
            if periodo.turmas.exists():
                return JsonResponse(
                    {
                        "error": f"Não é possível excluir o período '{periodo.nome}' pois existem turmas vinculadas a ele."
                    },
                    status=400,
                )

            if periodo.disciplinas.exists():
                return JsonResponse(
                    {
                        "error": f"Não é possível excluir o período '{periodo.nome}' pois existem disciplinas vinculadas a ele."
                    },
                    status=400,
                )

            nome_periodo = periodo.nome
            periodo.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Período '{nome_periodo}' excluído com sucesso!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


@login_required
def gerenciar_turmas(request):
    """
    View para gerenciar turmas com filtros
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Filtros da requisição
    filtro_turno = request.GET.get("turno", "")
    filtro_periodo = request.GET.get("periodo", "")
    filtro_status = request.GET.get("status", "")

    if request.method == "POST":
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(
                request,
                f"Turma '{turma.codigo_turma}' criada com sucesso!",
            )
            return redirect("gerenciar_turmas")
        else:
            # Debug: Mostra os erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
            messages.error(request, "Verifique os dados do formulário.")
    else:
        form = TurmaForm()

    # Base queryset
    turmas = (
        Turma.objects.select_related("disciplina", "professor", "periodo_letivo")
        .prefetch_related("matriculas")
        .order_by(
            "-periodo_letivo__ano",
            "-periodo_letivo__semestre",
            "disciplina__disciplina_nome",
        )
    )

    # Aplicar filtros
    if filtro_turno:
        turmas = turmas.filter(turno=filtro_turno)
    if filtro_periodo:
        turmas = turmas.filter(periodo_letivo_id=filtro_periodo)
    if filtro_status:
        turmas = turmas.filter(status=filtro_status)

    # Períodos disponíveis para o filtro
    periodos_disponiveis = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    context = {
        "form": form,
        "turmas": turmas,
        "periodos_disponiveis": periodos_disponiveis,
        "filtro_turno": filtro_turno,
        "filtro_periodo": filtro_periodo,
        "filtro_status": filtro_status,
    }

    return render(request, "gerenciar_turmas.html", context)


@login_required
def editar_turma(request, turma_id):
    """
    View para editar uma turma existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar turmas.")
        return redirect("inicio")

    turma = get_object_or_404(Turma, id=turma_id)

    if request.method == "POST":
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Turma '{turma.codigo_turma}' atualizada com sucesso!"
            )
            return redirect("gerenciar_turmas")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        form = TurmaForm(instance=turma)

    # Períodos disponíveis para o filtro
    periodos_disponiveis = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    context = {
        "form": form,
        "turma": turma,
        "turmas": Turma.objects.select_related(
            "disciplina", "professor", "periodo_letivo"
        ).order_by(
            "-periodo_letivo__ano",
            "-periodo_letivo__semestre",
            "disciplina__disciplina_nome",
        ),
        "periodos_disponiveis": periodos_disponiveis,
        "editing": True,
    }
    return render(request, "gerenciar_turmas.html", context)


@login_required
def excluir_turma(request, turma_id):
    """
    View para excluir uma turma
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method == "POST":
        try:
            turma = get_object_or_404(Turma, id=turma_id)

            # Verificar se há matrículas ativas
            matriculas_ativas = turma.matriculas.filter(status="ativa").count()
            if matriculas_ativas > 0:
                return JsonResponse(
                    {
                        "error": f"Não é possível excluir a turma '{turma.codigo_turma}' pois existem {matriculas_ativas} aluno(s) matriculado(s)."
                    },
                    status=400,
                )

            codigo_turma = turma.codigo_turma
            turma.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Turma '{codigo_turma}' excluída com sucesso!",
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)


class AdminHubView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_hub.html"

    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário tem permissão para acessar o admin hub"""
        if not check_user_permission(request.user, ["coordenador", "admin"]):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estatísticas do sistema
        context["total_usuarios"] = User.objects.count()
        context["total_cursos"] = Curso.objects.count()
        context["total_disciplinas"] = Disciplina.objects.count()
        context["total_avaliacoes"] = Avaliacao.objects.count()
        context["total_turmas"] = Turma.objects.count()
        context["total_professores"] = PerfilProfessor.objects.count()
        context["total_alunos"] = PerfilAluno.objects.count()
        context["total_periodos"] = PeriodoLetivo.objects.count()

        return context


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


@login_required
def buscar_alunos_ajax(request):
    """
    View para buscar alunos via AJAX
    """
    if request.is_ajax and request.method == "GET":
        termo = request.GET.get("termo", "")
        alunos = (
            PerfilAluno.objects.filter(
                Q(user__first_name__icontains=termo)
                | Q(user__last_name__icontains=termo)
                | Q(user__username__icontains=termo)
            )
            .select_related("user")
            .distinct()
        )

        resultados = [
            {"id": aluno.user.id, "nome": aluno.user.get_full_name()}
            for aluno in alunos
        ]

        return JsonResponse({"resultados": resultados})

    return JsonResponse({"resultados": []})


def gerenciar_perfil_usuario(usuario, nova_role):
    """
    Função utilitária para gerenciar perfis de usuário baseado na role
    Remove perfis incompatíveis e cria os necessários
    """
    mensagens = []

    if nova_role == "aluno":
        # Se tinha perfil de professor, remover
        if hasattr(usuario, "perfil_professor"):
            usuario.perfil_professor.delete()
            mensagens.append(f"Perfil de professor removido de {usuario.username}")

        # Criar ou manter perfil de aluno
        perfil_aluno, created = PerfilAluno.objects.get_or_create(user=usuario)
        if created:
            mensagens.append(f"Perfil de aluno criado para {usuario.username}")

    elif nova_role in ["professor", "coordenador"]:
        # Se tinha perfil de aluno, remover
        if hasattr(usuario, "perfil_aluno"):
            usuario.perfil_aluno.delete()
            mensagens.append(f"Perfil de aluno removido de {usuario.username}")

        # Criar ou manter perfil de professor
        perfil_professor, created = PerfilProfessor.objects.get_or_create(
            user=usuario, defaults={"registro_academico": usuario.username}
        )
        if created:
            mensagens.append(f"Perfil de professor criado para {usuario.username}")

    elif nova_role == "admin":
        # Admin não deve ter nenhum perfil específico
        # Remover qualquer perfil existente
        if hasattr(usuario, "perfil_professor"):
            usuario.perfil_professor.delete()
            mensagens.append(
                f"Perfil de professor removido de admin {usuario.username}"
            )

        if hasattr(usuario, "perfil_aluno"):
            usuario.perfil_aluno.delete()
            mensagens.append(f"Perfil de aluno removido de admin {usuario.username}")

    return mensagens


@login_required
def buscar_alunos_turma(request):
    """
    View para buscar alunos para gerenciamento de turmas via AJAX
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    turma_id = request.GET.get("turma_id")
    busca = request.GET.get("busca", "")

    try:
        turma = get_object_or_404(Turma, id=turma_id)

        # Buscar todos os alunos
        alunos_query = PerfilAluno.objects.select_related("user").all()

        if busca:
            alunos_query = alunos_query.filter(
                Q(user__first_name__icontains=busca)
                | Q(user__last_name__icontains=busca)
                | Q(user__username__icontains=busca)
                | Q(user__email__icontains=busca)
            )

        # Verificar quais alunos estão matriculados na turma
        matriculas_ativas = MatriculaTurma.objects.filter(
            turma=turma, status="ativa"
        ).values_list("aluno_id", flat=True)

        alunos_data = []
        for aluno in alunos_query.order_by("user__first_name", "user__last_name"):
            alunos_data.append(
                {
                    "id": aluno.user.id,
                    "nome": aluno.user.get_full_name() or aluno.user.username,
                    "username": aluno.user.username,
                    "email": aluno.user.email or "Não informado",
                    "matriculado": aluno.id in matriculas_ativas,
                }
            )

        turma_data = {
            "codigo": turma.codigo_turma,
            "disciplina": turma.disciplina.disciplina_nome,
            "professor": turma.professor.user.get_full_name(),
        }

        return JsonResponse(
            {
                "success": True,
                "alunos": alunos_data,
                "turma": turma_data,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def matricular_alunos_massa(request):
    """
    View para matricular/desmatricular alunos em massa via AJAX
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        turma_id = request.POST.get("turma_id")
        acao = request.POST.get("acao")  # 'matricular' ou 'desmatricular'
        alunos_ids = request.POST.getlist("alunos_ids[]")

        if not turma_id or not acao or not alunos_ids:
            return JsonResponse({"error": "Dados incompletos"}, status=400)

        turma = get_object_or_404(Turma, id=turma_id)

        # Buscar os perfis de aluno pelos IDs dos usuários
        usuarios = User.objects.filter(id__in=alunos_ids)
        alunos = PerfilAluno.objects.filter(user__in=usuarios)

        sucesso_count = 0
        erro_count = 0

        for aluno in alunos:
            try:
                if acao == "matricular":
                    matricula, created = MatriculaTurma.objects.get_or_create(
                        aluno=aluno, turma=turma, defaults={"status": "ativa"}
                    )
                    if created:
                        sucesso_count += 1
                    else:
                        # Se já existe, ativar se estiver inativa
                        if matricula.status != "ativa":
                            matricula.status = "ativa"
                            matricula.save()
                            sucesso_count += 1

                elif acao == "desmatricular":
                    matriculas = MatriculaTurma.objects.filter(
                        aluno=aluno, turma=turma, status="ativa"
                    )
                    if matriculas.exists():
                        matriculas.update(status="cancelada")
                        sucesso_count += 1

            except Exception as e:
                erro_count += 1
                print(f"Erro ao processar aluno {aluno.user.username}: {e}")

        if acao == "matricular":
            message = f"{sucesso_count} aluno(s) matriculado(s) com sucesso"
        else:
            message = f"{sucesso_count} aluno(s) desmatriculado(s) com sucesso"

        if erro_count > 0:
            message += f" ({erro_count} erro(s))"

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "sucesso_count": sucesso_count,
                "erro_count": erro_count,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============= VIEWS PARA AVALIAÇÃO DOCENTE =============


@login_required
def listar_avaliacoes(request):
    """
    View para listar todas as avaliações disponíveis
    """
    avaliacoes = QuestionarioAvaliacao.objects.filter(ativo=True).order_by(
        "-data_criacao"
    )
    ciclos = CicloAvaliacao.objects.filter(ativo=True).order_by("-data_inicio")

    # Paginação
    paginator = Paginator(avaliacoes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "avaliacoes": page_obj,
        "ciclos": ciclos,
        "titulo": "Avaliações Docentes",
    }
    return render(request, "avaliacoes/listar_avaliacoes.html", context)


@login_required
def criar_questionario_avaliacao(request):
    """
    View para criar um novo questionário de avaliação
    Apenas coordenadores e admins podem criar
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para criar questionários.")
        return redirect("listar_avaliacoes")

    if request.method == "POST":
        form = QuestionarioAvaliacaoForm(request.POST)
        if form.is_valid():
            questionario = form.save(commit=False)
            questionario.criado_por = request.user
            questionario.save()
            messages.success(request, "Questionário criado com sucesso!")
            return redirect(
                "editar_questionario_perguntas", questionario_id=questionario.id
            )
    else:
        form = QuestionarioAvaliacaoForm()

    return render(
        request,
        "avaliacoes/criar_questionario.html",
        {"form": form, "titulo": "Criar Questionário de Avaliação"},
    )


@login_required
def editar_questionario_perguntas(request, questionario_id):
    """
    View para editar as perguntas de um questionário
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para editar questionários.")
        return redirect("listar_avaliacoes")

    questionario = get_object_or_404(QuestionarioAvaliacao, id=questionario_id)
    perguntas_existentes = QuestionarioPergunta.objects.filter(
        questionario=questionario
    ).order_by("ordem_no_questionario")

    categorias = CategoriaPergunta.objects.all()

    if request.method == "POST":
        if "adicionar_pergunta" in request.POST:
            form = PerguntaAvaliacaoForm(request.POST)
            if form.is_valid():
                pergunta = form.save()
                # Adicionar ao questionário
                ordem = perguntas_existentes.count() + 1
                QuestionarioPergunta.objects.create(
                    questionario=questionario,
                    pergunta=pergunta,
                    ordem_no_questionario=ordem,
                )
                messages.success(request, "Pergunta adicionada com sucesso!")
                return redirect(
                    "editar_questionario_perguntas", questionario_id=questionario.id
                )

        elif "remover_pergunta" in request.POST:
            pergunta_id = request.POST.get("pergunta_id")
            QuestionarioPergunta.objects.filter(
                questionario=questionario, pergunta_id=pergunta_id
            ).delete()
            # Reordenar perguntas
            perguntas_restantes = QuestionarioPergunta.objects.filter(
                questionario=questionario
            ).order_by("ordem_no_questionario")
            for i, qp in enumerate(perguntas_restantes, 1):
                qp.ordem_no_questionario = i
                qp.save()
            messages.success(request, "Pergunta removida com sucesso!")
            return redirect(
                "editar_questionario_perguntas", questionario_id=questionario.id
            )
    else:
        form = PerguntaAvaliacaoForm()

    context = {
        "questionario": questionario,
        "perguntas_existentes": perguntas_existentes,
        "form": form,
        "categorias": categorias,
        "titulo": f"Editar Perguntas - {questionario.nome}",
    }
    return render(request, "avaliacoes/editar_questionario_perguntas.html", context)


@login_required
def criar_ciclo_avaliacao(request):
    """
    View para criar um novo ciclo de avaliação
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(
            request, "Você não tem permissão para criar ciclos de avaliação."
        )
        return redirect("listar_avaliacoes")

    if request.method == "POST":
        form = CicloAvaliacaoForm(request.POST)
        if form.is_valid():
            ciclo = form.save(commit=False)
            ciclo.criado_por = request.user
            ciclo.save()
            messages.success(request, "Ciclo de avaliação criado com sucesso!")
            return redirect("detalhe_ciclo_avaliacao", ciclo_id=ciclo.id)
    else:
        form = CicloAvaliacaoForm()

    return render(
        request,
        "avaliacoes/criar_ciclo.html",
        {"form": form, "titulo": "Criar Ciclo de Avaliação"},
    )


@login_required
def detalhe_ciclo_avaliacao(request, ciclo_id):
    """
    View para visualizar detalhes de um ciclo de avaliação
    """
    ciclo = get_object_or_404(CicloAvaliacao, id=ciclo_id)
    avaliacoes_docentes = AvaliacaoDocente.objects.filter(ciclo=ciclo)

    # Estatísticas do ciclo
    total_avaliacoes = avaliacoes_docentes.count()

    # Contar avaliações que têm pelo menos uma resposta
    avaliacoes_com_respostas = (
        avaliacoes_docentes.filter(respostas__isnull=False).distinct().count()
    )

    context = {
        "ciclo": ciclo,
        "avaliacoes_docentes": avaliacoes_docentes,
        "total_avaliacoes": total_avaliacoes,
        "avaliacoes_respondidas": avaliacoes_com_respostas,
        "percentual_respondidas": (
            (avaliacoes_com_respostas / total_avaliacoes * 100)
            if total_avaliacoes > 0
            else 0
        ),
        "titulo": f"Ciclo: {ciclo.nome}",
    }
    return render(request, "avaliacoes/detalhe_ciclo.html", context)


@login_required
def responder_avaliacao(request, avaliacao_id):
    """
    View para um aluno responder uma avaliação docente
    """
    avaliacao = get_object_or_404(AvaliacaoDocente, id=avaliacao_id)

    # Verificar se o usuário pode responder esta avaliação
    if not hasattr(request.user, "perfil_aluno"):
        messages.error(request, "Apenas alunos podem responder avaliações.")
        return redirect("listar_avaliacoes")

    # Verificar se a avaliação já foi respondida
    respostas_existentes = RespostaAvaliacao.objects.filter(
        avaliacao=avaliacao, aluno=request.user.perfil_aluno
    ).exists()

    if respostas_existentes:
        messages.warning(request, "Esta avaliação já foi respondida.")
        return redirect("visualizar_avaliacao", avaliacao_id=avaliacao.id)

    # Verificar se o ciclo está ativo
    if not avaliacao.ciclo.ativo:
        messages.error(request, "Este ciclo de avaliação não está mais ativo.")
        return redirect("listar_avaliacoes")

    # Pegar perguntas do questionário
    perguntas_questionario = QuestionarioPergunta.objects.filter(
        questionario=avaliacao.ciclo.questionario
    ).order_by("ordem_no_questionario")

    if request.method == "POST":
        # Processar respostas
        respostas_validas = True

        for qp in perguntas_questionario:
            campo_resposta = f"pergunta_{qp.pergunta.id}"
            valor_resposta = request.POST.get(campo_resposta)

            if not valor_resposta and qp.pergunta.obrigatoria:
                messages.error(
                    request, f'A pergunta "{qp.pergunta.enunciado}" é obrigatória.'
                )
                respostas_validas = False
                continue

            if valor_resposta:
                # Criar resposta baseada no tipo
                resposta_data = {
                    "avaliacao": avaliacao,
                    "aluno": request.user.perfil_aluno,
                    "pergunta": qp.pergunta,
                    "anonima": avaliacao.ciclo.permite_avaliacao_anonima,
                }

                if qp.pergunta.tipo in ["likert", "nps"]:
                    resposta_data["valor_numerico"] = int(valor_resposta)
                elif qp.pergunta.tipo == "sim_nao":
                    resposta_data["valor_boolean"] = valor_resposta.lower() == "sim"
                else:
                    resposta_data["valor_texto"] = valor_resposta

                RespostaAvaliacao.objects.create(**resposta_data)

        # Processar comentário geral se houver
        comentario_geral = request.POST.get("comentario_geral", "").strip()
        if comentario_geral:
            ComentarioAvaliacao.objects.create(
                avaliacao=avaliacao,
                aluno=request.user.perfil_aluno,
                elogios=comentario_geral,
                anonimo=avaliacao.ciclo.permite_avaliacao_anonima,
            )

        if respostas_validas:
            messages.success(request, "Avaliação respondida com sucesso!")
            return redirect("visualizar_avaliacao", avaliacao_id=avaliacao.id)

    context = {
        "avaliacao": avaliacao,
        "perguntas_questionario": perguntas_questionario,
        "titulo": f"Responder Avaliação - {avaliacao.professor.user.get_full_name()}",
    }
    return render(request, "avaliacoes/responder_avaliacao.html", context)


@login_required
def visualizar_avaliacao(request, avaliacao_id):
    """
    View para visualizar uma avaliação respondida
    """
    avaliacao = get_object_or_404(AvaliacaoDocente, id=avaliacao_id)

    # Verificar permissões
    pode_visualizar = False
    if hasattr(request.user, "perfil_aluno"):
        # Verificar se há respostas do aluno para esta avaliação
        respostas_aluno = RespostaAvaliacao.objects.filter(
            avaliacao=avaliacao, aluno=request.user.perfil_aluno
        ).exists()
        if respostas_aluno:
            pode_visualizar = True
    elif (
        hasattr(request.user, "perfil_professor")
        and avaliacao.professor == request.user.perfil_professor
    ):
        pode_visualizar = True
    elif check_user_permission(request.user, ["coordenador", "admin"]):
        pode_visualizar = True

    if not pode_visualizar:
        messages.error(
            request, "Você não tem permissão para visualizar esta avaliação."
        )
        return redirect("listar_avaliacoes")

    # Pegar respostas ordenadas pela ordem das perguntas no questionário
    respostas = RespostaAvaliacao.objects.filter(avaliacao=avaliacao).select_related(
        "pergunta"
    )
    comentarios = ComentarioAvaliacao.objects.filter(avaliacao=avaliacao)

    context = {
        "avaliacao": avaliacao,
        "respostas": respostas,
        "comentarios": comentarios,
        "titulo": f"Avaliação - {avaliacao.professor.user.get_full_name()}",
    }
    return render(request, "avaliacoes/visualizar_avaliacao.html", context)


@login_required
def relatorio_avaliacoes(request):
    """
    View para gerar relatórios de avaliações
    Apenas coordenadores e admins podem acessar
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para acessar relatórios.")
        return redirect("listar_avaliacoes")

    ciclos = CicloAvaliacao.objects.all().order_by("-data_inicio")
    professores = PerfilProfessor.objects.all().order_by("user__first_name")

    # Filtros
    ciclo_selecionado = request.GET.get("ciclo")
    professor_selecionado = request.GET.get("professor")

    # Buscar avaliações que têm respostas
    avaliacoes = AvaliacaoDocente.objects.filter(respostas__isnull=False).distinct()

    if ciclo_selecionado:
        avaliacoes = avaliacoes.filter(ciclo_id=ciclo_selecionado)

    if professor_selecionado:
        avaliacoes = avaliacoes.filter(professor_id=professor_selecionado)

    # Estatísticas
    total_avaliacoes = avaliacoes.count()

    # Calcular média simples das respostas numéricas
    media_geral = 0
    if total_avaliacoes > 0:
        respostas_numericas = RespostaAvaliacao.objects.filter(
            avaliacao__in=avaliacoes, valor_numerico__isnull=False
        )
        if respostas_numericas.exists():
            media_geral = (
                respostas_numericas.aggregate(media=Avg("valor_numerico"))["media"] or 0
            )

    context = {
        "ciclos": ciclos,
        "professores": professores,
        "avaliacoes": avaliacoes,
        "total_avaliacoes": total_avaliacoes,
        "media_geral": round(media_geral, 2),
        "ciclo_selecionado": ciclo_selecionado,
        "professor_selecionado": professor_selecionado,
        "titulo": "Relatórios de Avaliação",
    }
    return render(request, "avaliacoes/relatorio_avaliacoes.html", context)
