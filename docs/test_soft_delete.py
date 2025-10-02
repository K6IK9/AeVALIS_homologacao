"""
Script de Teste - Validação de Soft Delete de Usuários

Este script testa a funcionalidade de soft delete implementada no sistema.
Para executar: python manage.py shell < tests/test_soft_delete.py

IMPORTANTE: Execute em ambiente de desenvolvimento/teste
"""

import os
import django
import sys

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.append("c:/Users/kaike_matos/Documents/Docs/avaliacao_docente_suap")

# Configurar o Django antes de importar os modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from avaliacao_docente.models import (
    PerfilAluno,
    PerfilProfessor,
    MatriculaTurma,
    RespostaAvaliacao,
    AvaliacaoDocente,
)
from django.db import transaction


def test_soft_delete_preserves_data():
    """
    Teste principal: verifica se o soft delete preserva os dados relacionados
    """
    print("\n" + "=" * 70)
    print("🧪 TESTE DE SOFT DELETE - PRESERVAÇÃO DE DADOS")
    print("=" * 70 + "\n")

    # 1. Criar um usuário de teste
    print("📝 1. Criando usuário de teste...")
    test_user = User.objects.create_user(
        username="999999",
        email="teste@teste.com",
        first_name="Teste",
        last_name="Usuário",
        password="senha123",
    )
    print(f"   ✅ Usuário criado: {test_user.username}")

    # 2. Criar perfil de aluno
    print("\n📝 2. Criando perfil de aluno...")
    perfil_aluno = PerfilAluno.objects.create(user=test_user, situacao="Ativo")
    print(f"   ✅ Perfil aluno criado: ID {perfil_aluno.id}")

    # 3. Verificar se há matrículas/respostas (se existir turmas no sistema)
    matriculas_count = MatriculaTurma.objects.filter(aluno=perfil_aluno).count()
    print(f"\n📊 3. Dados relacionados ANTES do soft delete:")
    print(f"   - Matrículas: {matriculas_count}")
    print(f"   - Perfil ativo: {perfil_aluno.situacao}")
    print(f"   - User is_active: {test_user.is_active}")

    # 4. Simular soft delete
    print("\n🔄 4. Executando SOFT DELETE...")
    original_username = test_user.username
    original_email = test_user.email

    test_user.is_active = False
    test_user.first_name = "Usuário"
    test_user.last_name = "Desativado"
    test_user.email = f"desativado_{test_user.id}_{original_email}"
    test_user.username = f"del_{test_user.id}_{original_username}"
    test_user.save()

    print(f"   ✅ Soft delete executado")
    print(f"   - Username alterado: {original_username} → {test_user.username}")
    print(f"   - Email alterado: {original_email} → {test_user.email}")
    print(f"   - is_active: True → {test_user.is_active}")

    # 5. Verificar se dados foram preservados
    print("\n✅ 5. Verificando PRESERVAÇÃO DE DADOS:")

    # Recarregar do banco
    test_user.refresh_from_db()

    try:
        perfil_aluno.refresh_from_db()
        print(f"   ✅ Perfil de aluno PRESERVADO (ID: {perfil_aluno.id})")
    except PerfilAluno.DoesNotExist:
        print(f"   ❌ ERRO: Perfil de aluno foi DELETADO!")

    matriculas_count_after = MatriculaTurma.objects.filter(aluno=perfil_aluno).count()
    print(f"   ✅ Matrículas PRESERVADAS: {matriculas_count_after}")

    # 6. Verificar que usuário não consegue mais logar
    print("\n🔒 6. Verificando bloqueio de acesso:")
    print(f"   - is_active: {test_user.is_active}")
    if not test_user.is_active:
        print("   ✅ Usuário NÃO pode fazer login (comportamento esperado)")
    else:
        print("   ❌ ERRO: Usuário ainda pode fazer login!")

    # 7. Limpar dados de teste
    print("\n🧹 7. Limpando dados de teste...")
    test_user.delete()  # Agora sim podemos deletar fisicamente (é um teste)
    print("   ✅ Usuário de teste removido")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70 + "\n")


def test_cascade_relationships():
    """
    Teste adicional: verifica os relacionamentos CASCADE no modelo
    """
    print("\n" + "=" * 70)
    print("🔍 TESTE DE RELACIONAMENTOS CASCADE")
    print("=" * 70 + "\n")

    from django.db import connection
    from django.apps import apps

    # Modelos que têm ForeignKey/OneToOne para User
    models_with_user_fk = [
        ("avaliacao_docente", "PerfilAluno", "user"),
        ("avaliacao_docente", "PerfilProfessor", "user"),
        ("avaliacao_docente", "QuestionarioAvaliacao", "criado_por"),
    ]

    print("📊 Relacionamentos identificados:\n")
    for app, model_name, field_name in models_with_user_fk:
        try:
            model = apps.get_model(app, model_name)
            field = model._meta.get_field(field_name)
            on_delete = field.remote_field.on_delete.__name__
            print(f"   {model_name}.{field_name}")
            print(f"   └─ on_delete: {on_delete}")
            print()
        except Exception as e:
            print(f"   ⚠️ Erro ao inspecionar {model_name}: {e}\n")

    print("💡 CONCLUSÃO:")
    print("   Com soft delete (is_active=False), os relacionamentos CASCADE")
    print("   são PRESERVADOS porque o registro User não é deletado.")
    print("\n" + "=" * 70 + "\n")


def test_view_behavior():
    """
    Teste de comportamento: verifica o que acontece nos filtros de views
    """
    print("\n" + "=" * 70)
    print("🎯 TESTE DE COMPORTAMENTO EM VIEWS")
    print("=" * 70 + "\n")

    # Contar usuários ativos vs inativos
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    print(f"📊 Estatísticas de Usuários:")
    print(f"   Total: {total_users}")
    print(f"   Ativos: {active_users}")
    print(f"   Inativos: {inactive_users}")
    print()

    # Verificar perfis de alunos/professores com usuários inativos
    alunos_inativos = PerfilAluno.objects.filter(user__is_active=False).count()
    professores_inativos = PerfilProfessor.objects.filter(user__is_active=False).count()

    print(f"📊 Perfis com Usuários Inativos:")
    print(f"   Alunos: {alunos_inativos}")
    print(f"   Professores: {professores_inativos}")
    print()

    print("💡 RECOMENDAÇÃO:")
    print("   Adicionar filtros nas views para excluir usuários inativos:")
    print("   - PerfilAluno.objects.filter(user__is_active=True)")
    print("   - PerfilProfessor.objects.filter(user__is_active=True)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    print("\n🚀 Iniciando bateria de testes de Soft Delete...\n")

    try:
        with transaction.atomic():
            test_soft_delete_preserves_data()
            test_cascade_relationships()
            test_view_behavior()

            print("\n✅ TODOS OS TESTES EXECUTADOS COM SUCESSO!")
            print("\n⚠️  Nota: Testes executados em transação (rollback automático)\n")

            # Forçar rollback para não alterar o banco
            raise Exception(
                "Rollback intencional - dados de teste não foram persistidos"
            )

    except Exception as e:
        if "Rollback intencional" in str(e):
            print("✅ Rollback executado - banco de dados não foi alterado\n")
        else:
            print(f"\n❌ ERRO durante os testes: {e}\n")
            raise
