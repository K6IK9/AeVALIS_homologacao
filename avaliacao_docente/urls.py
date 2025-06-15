from django.urls import path

from . import views
from .views import IndexView

urlpatterns = [

    path("gerenciar-roles/", views.gerenciar_roles, name="gerenciar_roles"),
    path("gerenciar-cursos/", views.gerenciar_cursos, name="gerenciar_cursos"),
    path("", IndexView.as_view(), name="inicio"),
    path("avaliacoes/", views.avaliacoes_anteriores, name="avaliacoes"),
    path("meus-diarios/", views.diarios_usuario, name="meus_diarios"),
    path(
        "avaliacoes-por-diario/<int:diario_id>/",
        views.avaliacoes_por_diario,
        name="avaliacoes_por_diario",
    ),
]
