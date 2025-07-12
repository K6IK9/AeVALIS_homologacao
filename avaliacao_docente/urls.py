from django.urls import path

from . import views
from .views import IndexView

urlpatterns = [
    path("gerenciar-roles/", views.gerenciar_roles, name="gerenciar_roles"),
    path("gerenciar-cursos/", views.gerenciar_cursos, name="gerenciar_cursos"),
    path(
        "gerenciar-disciplinas/",
        views.gerenciar_disciplinas,
        name="gerenciar_disciplinas",
    ),
    path("gerenciar-periodos/", views.gerenciar_periodos, name="gerenciar_periodos"),
    path("gerenciar-turmas/", views.gerenciar_turmas, name="gerenciar_turmas"),
    path("buscar-alunos-turma/", views.buscar_alunos_turma, name="buscar_alunos_turma"),
    path(
        "matricular-alunos-massa/",
        views.matricular_alunos_massa,
        name="matricular_alunos_massa",
    ),
    path("admin-hub/", views.AdminHubView.as_view(), name="admin_hub"),
    # URLs para Avaliação Docente
    path("avaliacoes/", views.listar_avaliacoes, name="listar_avaliacoes"),
    path(
        "avaliacoes/criar-questionario/",
        views.criar_questionario_avaliacao,
        name="criar_questionario_avaliacao",
    ),
    path(
        "avaliacoes/questionario/<int:questionario_id>/perguntas/",
        views.editar_questionario_perguntas,
        name="editar_questionario_perguntas",
    ),
    path(
        "avaliacoes/criar-ciclo/",
        views.criar_ciclo_avaliacao,
        name="criar_ciclo_avaliacao",
    ),
    path(
        "avaliacoes/ciclo/<int:ciclo_id>/",
        views.detalhe_ciclo_avaliacao,
        name="detalhe_ciclo_avaliacao",
    ),
    path(
        "avaliacoes/responder/<int:avaliacao_id>/",
        views.responder_avaliacao,
        name="responder_avaliacao",
    ),
    path(
        "avaliacoes/visualizar/<int:avaliacao_id>/",
        views.visualizar_avaliacao,
        name="visualizar_avaliacao",
    ),
    path(
        "avaliacoes/relatorios/",
        views.relatorio_avaliacoes,
        name="relatorio_avaliacoes",
    ),
    path("", IndexView.as_view(), name="inicio"),
]
