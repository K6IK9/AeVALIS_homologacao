"""
Script de Validação - Consistência de Dados Turma

⚠️ OBSOLETO - Este script foi utilizado antes da migração 0008 que removeu
os campos redundantes 'professor' e 'periodo_letivo' de Turma.

HISTÓRICO:
- Validava se turma.professor == disciplina.professor
- Validava se turma.periodo_letivo == disciplina.periodo_letivo
- Utilizado antes da migration 0008_remover_campos_redundantes_turma

STATUS ATUAL (pós-migração 0008):
- Os campos professor e periodo_letivo foram REMOVIDOS de Turma
- Agora Turma possui apenas @property que delega para disciplina
- Este script não é mais necessário e está mantido apenas para referência histórica

Para executar validações atuais, use os testes em avaliacao_docente/tests.py
"""

import sys

print("=" * 80)
print("⚠️  ESTE SCRIPT ESTÁ OBSOLETO")
print("=" * 80)
print("\nOs campos 'professor' e 'periodo_letivo' foram removidos de Turma")
print("na migração 0008_remover_campos_redundantes_turma.")
print("\nAgora esses dados são acessados via properties:")
print("  • turma.professor → turma.disciplina.professor")
print("  • turma.periodo_letivo → turma.disciplina.periodo_letivo")
print("\nEste arquivo está mantido apenas para referência histórica.")
print("Para testes atuais, veja: avaliacao_docente/tests.py")
print("=" * 80)
sys.exit(0)
