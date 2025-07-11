#!/usr/bin/env python
"""
Script de teste para verificar se o sistema de roles está funcionando corretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role


def test_roles():
    print("=== Teste do Sistema de Roles ===")

    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username="teste_role",
        defaults={
            "email": "teste@exemplo.com",
            "first_name": "Usuário",
            "last_name": "Teste",
        },
    )

    if created:
        print(f"✓ Usuário {user.username} criado com sucesso")
    else:
        print(f"ℹ Usuário {user.username} já existe")
        # Limpar roles existentes
        for role in ["admin", "coordenador", "professor", "aluno"]:
            if has_role(user, role):
                remove_role(user, role)
                print(f"  Removida role anterior: {role}")

    # Testar atribuição de role professor
    print("\n--- Testando role Professor ---")
    assign_role(user, "professor")
    print(f"✓ Role professor atribuída")
    print(f'  Tem role professor: {has_role(user, "professor")}')
    print(f'  Tem role admin: {has_role(user, "admin")}')
    print(f'  Tem role coordenador: {has_role(user, "coordenador")}')
    print(f'  Tem role aluno: {has_role(user, "aluno")}')

    # Trocar para role coordenador
    print("\n--- Testando troca para Coordenador ---")
    remove_role(user, "professor")
    assign_role(user, "coordenador")
    print(f"✓ Role coordenador atribuída")
    print(f'  Tem role professor: {has_role(user, "professor")}')
    print(f'  Tem role coordenador: {has_role(user, "coordenador")}')

    # Testar o método get_user_role do admin
    print("\n--- Testando método get_user_role ---")
    from avaliacao_docente.admin import CustomUserAdmin

    admin_instance = CustomUserAdmin(User, None)
    role_display = admin_instance.get_user_role(user)
    print(f"✓ Display da role: {role_display}")

    # Testar troca de perfis
    print("\n--- Testando troca de perfis ---")
    from avaliacao_docente.models import PerfilAluno, PerfilProfessor
    from avaliacao_docente.views import gerenciar_perfil_usuario

    # Criar usuário como aluno inicialmente
    user2, created = User.objects.get_or_create(
        username="teste_perfil",
        defaults={
            "email": "teste2@exemplo.com",
            "first_name": "Teste",
            "last_name": "Perfil",
        },
    )

    if created:
        print(f"✓ Usuário {user2.username} criado")

    # Começar como aluno
    assign_role(user2, "aluno")
    gerenciar_perfil_usuario(user2, "aluno")
    print(f"  Iniciado como aluno")
    print(f"  Tem perfil aluno: {hasattr(user2, 'perfil_aluno')}")
    print(f"  Tem perfil professor: {hasattr(user2, 'perfil_professor')}")

    # Trocar para professor
    remove_role(user2, "aluno")
    assign_role(user2, "professor")
    mensagens = gerenciar_perfil_usuario(user2, "professor")
    print(f"  Trocado para professor:")
    for msg in mensagens:
        print(f"    - {msg}")

    # Verificar estado atual
    user2.refresh_from_db()  # Atualizar do banco
    print(f"  Tem perfil aluno: {hasattr(user2, 'perfil_aluno')}")
    print(f"  Tem perfil professor: {hasattr(user2, 'perfil_professor')}")

    # Trocar para coordenador (deve manter perfil professor)
    remove_role(user2, "professor")
    assign_role(user2, "coordenador")
    mensagens = gerenciar_perfil_usuario(user2, "coordenador")
    print(f"  Trocado para coordenador:")
    for msg in mensagens:
        print(f"    - {msg}")

    # Verificar estado final
    user2.refresh_from_db()
    print(f"  Tem perfil aluno: {hasattr(user2, 'perfil_aluno')}")
    print(f"  Tem perfil professor: {hasattr(user2, 'perfil_professor')}")

    # Testar que admin não recebe perfil
    print("\n--- Testando admin sem perfil ---")
    remove_role(user, "coordenador")
    assign_role(user, "admin")
    mensagens = gerenciar_perfil_usuario(user, "admin")
    print(f"  Trocado para admin:")
    for msg in mensagens:
        print(f"    - {msg}")

    # Verificar que admin não tem perfil
    user.refresh_from_db()
    print(f"  Admin tem perfil aluno: {hasattr(user, 'perfil_aluno')}")
    print(f"  Admin tem perfil professor: {hasattr(user, 'perfil_professor')}")

    # Limpar usuário de teste
    user2.delete()
    print(f"  ✓ Usuário {user2.username} removido")

    print("\n=== Teste concluído com sucesso! ===")

    # Limpar usuário de teste
    user.delete()
    print("ℹ Usuário de teste removido")


if __name__ == "__main__":
    test_roles()
