# Auditoria de Duplicidades em Models Django
**Data**: 02/10/2025 14:08
**Total de Modelos**: 16

---

## 📊 Resumo Executivo

**Total de Duplicidades Detectadas**: 432

| Categoria | Quantidade |
|-----------|------------|
| Campos Repetidos | 6 |
| Metodos Similares | 426 |
| Choices Duplicados | 0 |
| Constraints Sobrepostos | 0 |
| Relacionamentos Redundantes | 0 |
| Padroes Transversais | 0 |

## 📝 Campos Repetidos

### Campo: `id` (BigAutoField)
- **Aparece em 16 modelos**: PerfilAluno, PerfilProfessor, Curso, PeriodoLetivo, Disciplina, Turma, MatriculaTurma, HorarioTurma, QuestionarioAvaliacao, CategoriaPergunta, PerguntaAvaliacao, QuestionarioPergunta, CicloAvaliacao, AvaliacaoDocente, RespostaAvaliacao, ConfiguracaoSite

### Campo: `disciplinas` (ManyToOneRel)
- **Aparece em 3 modelos**: PerfilProfessor, Curso, PeriodoLetivo

### Campo: `nome` (CharField)
- **Aparece em 3 modelos**: PeriodoLetivo, CategoriaPergunta, CicloAvaliacao

### Campo: `status` (CharField)
- **Aparece em 3 modelos**: Turma, MatriculaTurma, AvaliacaoDocente

### Campo: `data_criacao` (DateTimeField)
- **Aparece em 5 modelos**: Turma, QuestionarioAvaliacao, PerguntaAvaliacao, CicloAvaliacao, AvaliacaoDocente

### Campo: `turma` (ForeignKey)
- **Aparece em 3 modelos**: MatriculaTurma, HorarioTurma, AvaliacaoDocente

## 🔧 Métodos Similares

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ PerfilProfessor
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ Curso
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ PeriodoLetivo
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ Disciplina
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ Turma
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ MatriculaTurma
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ HorarioTurma
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ QuestionarioAvaliacao
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ CategoriaPergunta
- **Recomendação**: Extrair para método utilitário ou mixin

### Método: `__repr__`
- **Similaridade**: 100.0%
- **Modelos**: PerfilAluno ↔️ PerguntaAvaliacao
- **Recomendação**: Extrair para método utilitário ou mixin

## 📈 Priorização de Refatorações

### Alta Prioridade
1. **Implementar Mixins para Padrões Transversais** (baixo risco, alto impacto)
   - TimestampMixin (created_at, updated_at)
   - SoftDeleteMixin (ativo, deletado)
   - AuditoriaMixin (criado_por, atualizado_por)

### Média Prioridade
2. **Centralizar Choices em Enums**
3. **Extrair Métodos Similares para Utils**

### Baixa Prioridade
4. **Revisar Relacionamentos Redundantes**
5. **Otimizar Constraints Sobrepostos**

## 🚀 Próximos Passos Recomendados

1. Criar `avaliacao_docente/mixins.py` com classes base
2. Criar `avaliacao_docente/enums.py` com choices centralizados
3. Implementar migrações para adicionar campos dos mixins
4. Migração de dados (popular novos campos)
5. Atualizar models para herdar de mixins
6. Remover campos antigos via migração
7. Executar suite de testes completa
8. Atualizar documentação
