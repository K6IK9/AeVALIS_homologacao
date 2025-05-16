
from django.contrib import admin
from django.urls import path
from django.urls import include
from avaliacao_docente import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('avaliacao_docente.urls')),
    path('registro/', views.RegistrarUsuarioView.as_view(), name='registro'),
    path('accounts/', include('django.contrib.auth.urls')),  # Para autenticação
]


