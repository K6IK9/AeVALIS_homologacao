from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from avaliacao_docente import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("avaliacao_docente.urls")),
    path("registro/", views.RegistrarUsuarioView.as_view(), name="registro"),
    path("accounts/", include("django.contrib.auth.urls")),  # Para autenticação
]

