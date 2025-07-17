# Sistema de Avaliação Docente

## 📋 Sobre o Projeto

O **Sistema de Avaliação Docente** é uma aplicação web desenvolvida em Django que permite a gestão e avaliação de professores por alunos em instituições de ensino. O sistema oferece um ambiente completo para administração de cursos, disciplinas, turmas e avaliações docentes.

### ✨ Principais Funcionalidades

- **Gestão de Usuários**: Sistema de roles (Admin, Coordenador, Professor, Aluno) com permissões específicas
- **Administração Acadêmica**: Gerenciamento de cursos, disciplinas, períodos letivos e turmas
- **Sistema de Avaliações**: Criação e gestão de questionários de avaliação docente
- **Ciclos de Avaliação**: Controle de períodos específicos para realização das avaliações
- **Interface Responsiva**: Design moderno e adaptativo para diferentes dispositivos
- **Painel Administrativo**: Interface administrativa completa para gestão do sistema

### 🏗️ Arquitetura do Sistema

- **Backend**: Django 5.2.1 com Python
- **Frontend**: HTML, CSS, JavaScript com templates Django
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Autenticação**: Sistema de autenticação do Django com roles customizados
- **Deploy**: Configurado para Vercel

### 👥 Sistema de Permissões

O sistema utiliza 4 tipos de usuários com diferentes níveis de acesso:

- **Admin**: Acesso total ao sistema, incluindo gerenciamento de usuários e configurações
- **Coordenador**: Gestão de cursos, disciplinas e avaliações
- **Professor**: Visualização de suas avaliações e gerenciamento de perfil
- **Aluno**: Realização de avaliações dos professores

## 🚀 Como Executar o Projeto

### 📋 Pré-requisitos

- Python 3.9+
- pip (gerenciador de pacotes Python)
- Git

### 🔧 Instalação e Configuração

#### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd avaliacao_docente_novo
```

#### 2. Crie um ambiente virtual
```bash
# No Linux/Mac
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
```

**⚠️ Importante**: Gere uma SECRET_KEY segura para produção!

#### 5. Execute as migrações do banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Crie um superusuário (Admin)
```bash
python manage.py createsuperuser
```
Forneça as informações solicitadas:
- Username
- Email
- Password

#### 7. Execute o servidor de desenvolvimento
```bash
python manage.py runserver
```

O sistema estará disponível em: `http://127.0.0.1:8000/`

### 🔑 Acessando o Admin Hub

1. Acesse: `http://127.0.0.1:8000/admin/`
2. Faça login com as credenciais do superusuário criado
3. No painel administrativo você poderá:
   - Gerenciar usuários
   - Configurar cursos e disciplinas
   - Criar questionários de avaliação
   - Visualizar relatórios

### 📊 Configuração Inicial do Sistema

Após criar o superusuário e acessar o admin, siga estes passos para configurar o sistema:

1. **Criar Cursos**: Acesse "Cursos" e adicione os cursos da instituição
2. **Criar Disciplinas**: Adicione as disciplinas vinculadas aos cursos
3. **Definir Períodos Letivos**: Configure os semestres/períodos
4. **Criar Turmas**: Vincule disciplinas, professores e períodos
5. **Configurar Questionários**: Crie as perguntas para avaliação docente | **Em Desenvolvimento**
6. **Gerenciar Usuários**: Atribua roles aos usuários (Professor, Aluno, etc.) 


### 🔧 Desenvolvimento

#### Estrutura do Projeto
```
avaliacao_docente_novo/
├── avaliacao_docente/          # App principal
│   ├── models.py              # Modelos do banco de dados
│   ├── views.py               # Lógica das views
│   ├── forms.py               # Formulários
│   ├── urls.py                # URLs do app
│   └── templates/             # Templates HTML
├── setup/                     # Configurações do Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # URLs principais
│   └── roles.py               # Definição de roles
├── static/                    # Arquivos estáticos
├── templates/                 # Templates globais
└── requirements.txt           # Dependências
```

#### Comandos Úteis
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic
```

### 🛠️ Tecnologias Utilizadas

- **Django 5.2.1**: Framework web Python
- **django-role-permissions**: Gerenciamento de roles e permissões
- **psycopg2-binary**: Driver PostgreSQL
- **python-decouple**: Gerenciamento de configurações
- **SQLite**: Banco de dados para desenvolvimento
- **HTML/CSS/JavaScript**: Frontend

## 🔧 Troubleshooting

### 🖼️ Problemas com Carregamento de Imagens/Arquivos Estáticos

Se as imagens ou arquivos CSS/JS não estiverem carregando, siga estes passos:

#### 1. Verificar configurações de arquivos estáticos no settings.py
```python
# Certifique-se de que estas configurações estão no settings.py:
import os

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Para arquivos de mídia (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### 2. Coletar arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

#### 3. Verificar URLs principais
No arquivo `setup/urls.py`, certifique-se de que há:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # suas URLs aqui
]

# Adicionar estas linhas para servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 4. Verificar estrutura de pastas
Certifique-se de que a estrutura está assim:
```
avaliacao_docente_novo/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ...
├── media/              # Para uploads de usuários
└── staticfiles/        # Gerado pelo collectstatic
```


### 📝 Licença

Este projeto está sob a licença especificada no arquivo `LICENSE`.
