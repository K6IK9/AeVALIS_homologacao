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
    path("admin-hub/", views.AdminHubView.as_view(), name="admin_hub"),
    path("", IndexView.as_view(), name="inicio"),
]
