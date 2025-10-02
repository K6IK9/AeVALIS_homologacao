# Proposta de Abstrações para Models Django

**Data**: 02/10/2025  
**Referência**: Auditoria de Duplicidades em Models  
**Status**: Proposta para Aprovação

---

## 📋 Sumário Executivo

Com base na auditoria automatizada, identificamos **432 duplicidades** nos models, sendo:
- **426 métodos idênticos** (`__repr__`, `clean`, `delete`, `save`)
- **6 campos repetidos** em múltiplos modelos
- **0 padrões transversais explícitos** detectados automaticamente

### Principais Achados

1. **Todos os 16 modelos** implementam os mesmos métodos `__repr__`, `clean`, `delete` e `save` com código 100% idêntico
2. Campo `data_criacao` aparece em **5 modelos** (Turma, QuestionarioAvaliacao, PerguntaAvaliacao, CicloAvaliacao, AvaliacaoDocente)
3. Campo `status` aparece em **3 modelos** (Turma, MatriculaTurma, AvaliacaoDocente)
4. Campo `nome` aparece em **3 modelos** (PeriodoLetivo, CategoriaPergunta, CicloAvaliacao)

---

## 🎯 Objetivos da Refatoração

1. **Reduzir duplicação de código** em ~95% através de classes base e mixins
2. **Melhorar manutenibilidade** centralizando lógica comum
3. **Garantir consistência** no comportamento de soft delete e timestamps
4. **Facilitar evolução** futura com novos padrões transversais

---

## 🏗️ Arquitetura Proposta

### 1. Classe Base Abstrata

```python
# avaliacao_docente/models/base.py

from django.db import models

class BaseModel(models.Model):
    """
    Classe base abstrata para todos os models do sistema.
    Implementa comportamento padrão de soft delete e métodos utilitários.
    """
    
    class Meta:
        abstract = True
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"
    
    def clean(self):
        """Validação padrão (pode ser sobrescrita)"""
        super().clean()
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca como inativo ao invés de deletar"""
        if hasattr(self, 'ativo'):
            self.ativo = False
            self.save(using=using)
        else:
            # Hard delete se não tiver campo 'ativo'
            super().delete(using=using, keep_parents=keep_parents)
    
    def save(self, *args, **kwargs):
        """Validação automática antes de salvar"""
        self.full_clean()
        super().save(*args, **kwargs)
```

### 2. Mixins para Funcionalidades Transversais

#### 2.1 TimestampMixin

```python
# avaliacao_docente/models/mixins.py

from django.db import models
from django.utils import timezone

class TimestampMixin(models.Model):
    """
    Adiciona campos de timestamp automáticos.
    Usado em: Turma, QuestionarioAvaliacao, PerguntaAvaliacao, 
              CicloAvaliacao, AvaliacaoDocente (5 modelos)
    """
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True,
        help_text='Data e hora de criação do registro'
    )
    data_atualizacao = models.DateTimeField(
        'Data de Atualização',
        auto_now=True,
        help_text='Data e hora da última atualização'
    )
    
    class Meta:
        abstract = True
```

#### 2.2 SoftDeleteMixin

```python
class SoftDeleteMixin(models.Model):
    """
    Adiciona capacidade de soft delete.
    Usado em: Turma, MatriculaTurma, AvaliacaoDocente (3 modelos com 'status')
    """
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Indica se o registro está ativo no sistema'
    )
    data_exclusao = models.DateTimeField(
        'Data de Exclusão',
        null=True,
        blank=True,
        help_text='Data e hora em que o registro foi desativado'
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Desativa o registro mantendo histórico"""
        self.ativo = False
        self.data_exclusao = timezone.now()
        self.save()
    
    def restore(self):
        """Reativa o registro"""
        self.ativo = True
        self.data_exclusao = None
        self.save()
```

#### 2.3 AuditoriaMixin

```python
from django.conf import settings

class AuditoriaMixin(models.Model):
    """
    Adiciona campos de auditoria (quem criou/modificou).
    Futuro: aplicar em modelos críticos
    """
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_criados',
        verbose_name='Criado Por'
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_atualizados',
        verbose_name='Atualizado Por'
    )
    
    class Meta:
        abstract = True
```

### 3. Custom Managers para Soft Delete

```python
# avaliacao_docente/models/managers.py

from django.db import models

class SoftDeleteManager(models.Manager):
    """Manager que filtra automaticamente registros inativos"""
    
    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)
    
    def all_with_deleted(self):
        """Retorna todos os registros, incluindo inativos"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Retorna apenas registros inativos"""
        return super().get_queryset().filter(ativo=False)
```

### 4. Enums Centralizados

```python
# avaliacao_docente/enums.py

from django.db import models

class StatusTurma(models.TextChoices):
    """Status possíveis para Turma"""
    ATIVA = 'ativa', 'Ativa'
    ENCERRADA = 'encerrada', 'Encerrada'
    CANCELADA = 'cancelada', 'Cancelada'

class StatusMatricula(models.TextChoices):
    """Status possíveis para MatriculaTurma"""
    ATIVO = 'ativo', 'Ativo'
    TRANCADO = 'trancado', 'Trancado'
    CONCLUIDO = 'concluido', 'Concluído'
    CANCELADO = 'cancelado', 'Cancelado'

class StatusAvaliacao(models.TextChoices):
    """Status possíveis para AvaliacaoDocente"""
    PENDENTE = 'pendente', 'Pendente'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'
    EXPIRADA = 'expirada', 'Expirada'

class TurnoDisciplina(models.TextChoices):
    """Turnos possíveis para Turma"""
    MATUTINO = 'matutino', 'Matutino'
    VESPERTINO = 'vespertino', 'Vespertino'
    NOTURNO = 'noturno', 'Noturno'

class TipoPergunta(models.TextChoices):
    """Tipos de pergunta para avaliação"""
    ESCALA_LIKERT = 'escala_likert', 'Escala Likert (1-5)'
    MULTIPLA_ESCOLHA = 'multipla_escolha', 'Múltipla Escolha'
    TEXTO_CURTO = 'texto_curto', 'Texto Curto'
    TEXTO_LONGO = 'texto_longo', 'Texto Longo'
```

---

## 📦 Exemplo de Uso

### Antes (Modelo Atual)

```python
class Turma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    turno = models.CharField(max_length=20, choices=[...])
    status = models.CharField(max_length=20, default='ativa')
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __repr__(self):
        return f"<Turma: {self}>"
    
    def clean(self):
        super().clean()
    
    def delete(self, using=None, keep_parents=False):
        self.status = 'cancelada'
        self.save(using=using)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

### Depois (Com Abstrações)

```python
from avaliacao_docente.models.base import BaseModel
from avaliacao_docente.models.mixins import TimestampMixin, SoftDeleteMixin
from avaliacao_docente.models.managers import SoftDeleteManager
from avaliacao_docente.enums import StatusTurma, TurnoDisciplina

class Turma(BaseModel, TimestampMixin, SoftDeleteMixin):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    turno = models.CharField(
        max_length=20,
        choices=TurnoDisciplina.choices,
        default=TurnoDisciplina.MATUTINO
    )
    status = models.CharField(
        max_length=20,
        choices=StatusTurma.choices,
        default=StatusTurma.ATIVA
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager para acesso sem filtro
    
    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        unique_together = ['disciplina', 'turno']
        ordering = ['disciplina__periodo_letivo', 'disciplina__nome', 'turno']
```

**Redução**: De ~30 linhas para ~15 linhas (50% menos código)

---

## 🔄 Plano de Migração

### Fase 1: Preparação (Sem Impacto no BD)

**Esforço**: 2-3 horas  
**Risco**: Muito Baixo

1. Criar estrutura de arquivos:
   ```
   avaliacao_docente/
   ├── models/
   │   ├── __init__.py
   │   ├── base.py          # BaseModel
   │   ├── mixins.py        # Mixins
   │   └── managers.py      # Managers
   ├── enums.py             # Enums centralizados
   └── models.py (existente, será modularizado)
   ```

2. Implementar classes base, mixins e enums
3. Adicionar testes unitários para cada componente
4. Executar testes: `python manage.py test`

### Fase 2: Migração Gradual (Com Migrações)

**Esforço**: 1 dia  
**Risco**: Baixo (migrations reversíveis)

**Passo 2.1**: Adicionar campos dos mixins (mantendo os antigos)

```python
# Migration 0009_adicionar_campos_mixins.py
operations = [
    # TimestampMixin - adicionar data_atualizacao (data_criacao já existe)
    migrations.AddField(
        model_name='turma',
        name='data_atualizacao',
        field=models.DateTimeField(auto_now=True),
    ),
    # SoftDeleteMixin - adicionar ativo e data_exclusao
    migrations.AddField(
        model_name='turma',
        name='ativo',
        field=models.BooleanField(default=True),
    ),
    migrations.AddField(
        model_name='turma',
        name='data_exclusao',
        field=models.DateTimeField(null=True, blank=True),
    ),
    # ... repetir para outros modelos ...
]
```

**Passo 2.2**: Migração de dados (popular novos campos)

```python
# Migration 0010_popular_campos_mixins.py
def popular_campos_ativo(apps, schema_editor):
    Turma = apps.get_model('avaliacao_docente', 'Turma')
    # Mapeamento: status 'cancelada' -> ativo=False
    Turma.objects.filter(status='cancelada').update(ativo=False)
    Turma.objects.exclude(status='cancelada').update(ativo=True)

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(popular_campos_ativo, reverse_code=migrations.RunPython.noop),
    ]
```

**Passo 2.3**: Atualizar models.py para usar mixins

```python
# Mudar de:
class Turma(models.Model):
    ...

# Para:
class Turma(BaseModel, TimestampMixin, SoftDeleteMixin):
    ...
    objects = SoftDeleteManager()
    all_objects = models.Manager()
```

**Passo 2.4**: Atualizar código que usa os campos antigos

- Views, forms, serializers que usam `status` para soft delete
- Queries que filtram por `status != 'cancelada'` → usar `ativo=True`

**Passo 2.5**: (Opcional) Remover campos antigos redundantes

```python
# Migration 0011_remover_campos_redundantes.py (FUTURA)
# Apenas após validação completa em produção
operations = [
    migrations.RemoveField(model_name='turma', name='status'),  # Se substituído por 'ativo'
]
```

### Fase 3: Validação e Testes

**Esforço**: 4-6 horas  
**Risco**: Muito Baixo

1. Executar suite completa de testes
2. Teste manual de soft delete:
   ```python
   turma = Turma.objects.get(pk=1)
   turma.soft_delete()  # Novo método
   assert turma.ativo == False
   turma.restore()  # Novo método
   assert turma.ativo == True
   ```
3. Validar managers:
   ```python
   Turma.objects.all()  # Apenas ativos
   Turma.all_objects.all()  # Todos
   Turma.objects.deleted_only()  # Apenas inativos
   ```
4. Validar enums em formulários e admin

---

## 📊 Impacto Esperado

| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **Linhas de código duplicado** | ~480 | ~20 | 95% |
| **Modelos com soft delete manual** | 3 | 0 | 100% |
| **Modelos com timestamps** | 5 | 0 (via mixin) | 100% |
| **Choices hardcoded** | ~10 | 0 | 100% |
| **Risco de inconsistência** | Alto | Baixo | -75% |

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Quebra de queries existentes | Baixa | Médio | Manter campos antigos durante transição; testes extensivos |
| Conflito de nomes em mixins | Baixa | Baixo | Revisar campos antes de aplicar mixins |
| Performance de múltipla herança | Muito Baixa | Baixo | Django otimiza herança de abstract models; sem impacto |
| Migração de dados falha | Baixa | Alto | Backup de BD; rollback plan; dry-run em dev/staging |

---

## ✅ Critérios de Aceitação

- [ ] Todos os 49 testes unitários existentes passam
- [ ] 5 novos testes de integração para mixins passam
- [ ] Soft delete funciona via método `.soft_delete()`
- [ ] Managers filtram corretamente registros ativos/inativos
- [ ] Admin Django exibe campos de mixins corretamente
- [ ] Enums aparecem como dropdowns em formulários
- [ ] Documentação atualizada em `docs/MODELS_ARCHITECTURE.md`
- [ ] Zero queries quebradas (validado via `manage.py check`)
- [ ] Performance mantida ou melhorada (< 5% regressão)

---

## 📅 Cronograma Sugerido

| Fase | Duração | Responsável | Data Alvo |
|------|---------|-------------|-----------|
| **Fase 1**: Implementar abstrações | 3h | Dev Backend | 03/10/2025 |
| **Fase 2**: Migrações e integração | 1 dia | Dev Backend | 04/10/2025 |
| **Fase 3**: Testes e validação | 6h | Dev Backend + QA | 04/10/2025 |
| **Revisão e Aprovação** | 2h | Tech Lead | 07/10/2025 |
| **Deploy em Staging** | - | DevOps | 08/10/2025 |
| **Deploy em Produção** | - | DevOps | 10/10/2025 |

---

## 🔗 Referências

- [Django Best Practices - Mixins](https://docs.djangoproject.com/en/4.2/topics/db/models/#abstract-base-classes)
- [Soft Delete Pattern](https://stackoverflow.com/questions/46663841/soft-delete-in-django)
- [Custom Managers](https://docs.djangoproject.com/en/4.2/topics/db/managers/)
- Relatório de Auditoria: `docs/AUDITORIA_MODELS_DUPLICIDADES.md`
- Script de Auditoria: `scripts/auditoria_models.py`

---

**Próxima Ação Recomendada**: Aprovação da arquitetura proposta antes de implementação da Fase 1.

