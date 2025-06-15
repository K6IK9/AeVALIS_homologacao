#!/usr/bin/env python
"""
Script de teste para verificar se o sistema de roles está funcionando corretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.auth.models import User
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role

def test_roles():
    print("=== Teste do Sistema de Roles ===")
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_role', 
        defaults={'email': 'teste@exemplo.com', 'first_name': 'Usuário', 'last_name': 'Teste'}
    )
    
    if created:
        print(f'✓ Usuário {user.username} criado com sucesso')
    else:
        print(f'ℹ Usuário {user.username} já existe')
        # Limpar roles existentes
        for role in ["admin", "coordenador", "professor", "aluno"]:
            if has_role(user, role):
                remove_role(user, role)
                print(f'  Removida role anterior: {role}')
    
    # Testar atribuição de role professor
    print("\n--- Testando role Professor ---")
    assign_role(user, 'professor')
    print(f'✓ Role professor atribuída')
    print(f'  Tem role professor: {has_role(user, "professor")}')
    print(f'  Tem role admin: {has_role(user, "admin")}')
    print(f'  Tem role coordenador: {has_role(user, "coordenador")}')
    print(f'  Tem role aluno: {has_role(user, "aluno")}')
    
    # Trocar para role coordenador
    print("\n--- Testando troca para Coordenador ---")
    remove_role(user, 'professor')
    assign_role(user, 'coordenador')
    print(f'✓ Role coordenador atribuída')
    print(f'  Tem role professor: {has_role(user, "professor")}')
    print(f'  Tem role coordenador: {has_role(user, "coordenador")}')
    
    # Testar o método get_user_role do admin
    print("\n--- Testando método get_user_role ---")
    from avaliacao_docente.admin_old import CustomUserAdmin
    admin_instance = CustomUserAdmin(User, None)
    role_display = admin_instance.get_user_role(user)
    print(f'✓ Display da role: {role_display}')
    
    print("\n=== Teste concluído com sucesso! ===")
    
    # Limpar usuário de teste
    user.delete()
    print("ℹ Usuário de teste removido")

if __name__ == '__main__':
    test_roles()
