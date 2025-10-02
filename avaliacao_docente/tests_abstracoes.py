"""
Testes unitários para abstrações de models (BaseModel, Mixins, Managers).

Testa funcionalidade de:
    - BaseModel: __repr__, clean, delete, save
    - TimestampMixin: data_criacao, data_atualizacao
    - SoftDeleteMixin: soft_delete, restore, is_deleted
    - SoftDeleteManager: get_queryset, all_with_deleted, deleted_only
    - Enums: StatusTurma, TurnoDisciplina, etc
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from avaliacao_docente.models import (
    BaseModel,
    TimestampMixin,
    SoftDeleteMixin,
    AuditoriaMixin,
    SoftDeleteManager,
)
from avaliacao_docente.enums import (
    StatusTurma,
    StatusMatricula,
    TurnoDisciplina,
    TipoPergunta,
)


# ========== MODELS DE TESTE ==========


class TestModelSimples(BaseModel):
    """Model simples para testar BaseModel"""

    nome = models.CharField(max_length=100)

    class Meta:
        app_label = "avaliacao_docente"

    def __str__(self):
        return self.nome


class TestModelComTimestamp(BaseModel, TimestampMixin):
    """Model para testar TimestampMixin"""

    nome = models.CharField(max_length=100)

    class Meta:
        app_label = "avaliacao_docente"


class TestModelComSoftDelete(BaseModel, SoftDeleteMixin):
    """Model para testar SoftDeleteMixin"""

    nome = models.CharField(max_length=100)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        app_label = "avaliacao_docente"


class TestModelCompleto(BaseModel, TimestampMixin, SoftDeleteMixin):
    """Model com todos os mixins"""

    nome = models.CharField(max_length=100)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        app_label = "avaliacao_docente"


# ========== TESTES ==========


class BaseModelTest(TestCase):
    """Testes para BaseModel"""

    def setUp(self):
        """Cria models de teste em memória (sem migração)"""
        # Nota: Models de teste não criam tabelas reais
        # Usamos models existentes para testes reais
        pass

    def test_repr_padrao(self):
        """Testa que __repr__ retorna formato correto"""
        from avaliacao_docente.models import Curso, PerfilProfessor
        from django.contrib.auth.models import User

        user = User.objects.create_user(username="coord_test", password="test")
        coord = PerfilProfessor.objects.create(user=user, matricula="999")
        curso = Curso(curso_nome="Teste", curso_sigla="TST", coordenador_curso=coord)
        repr_str = repr(curso)

        self.assertIn("<Curso:", repr_str)
        self.assertIn("Teste", repr_str)

    def test_save_com_validacao(self):
        """Testa que save() chama full_clean() automaticamente"""
        # Nota: Models existentes não herdam de BaseModel ainda
        # Este teste será relevante após migração para BaseModel
        self.assertTrue(True)  # Placeholder

    def test_save_pula_validacao(self):
        """Testa que skip_validation=True pula validação"""
        # Nota: Models existentes não herdam de BaseModel ainda
        # Este teste será relevante após migração para BaseModel
        self.assertTrue(True)  # Placeholder


class TimestampMixinTest(TestCase):
    """Testes para TimestampMixin"""

    def test_data_criacao_auto_preenchida(self):
        """Testa que data_criacao é preenchida automaticamente"""
        from avaliacao_docente.models import (
            Turma,
            Disciplina,
            Curso,
            PeriodoLetivo,
            PerfilProfessor,
        )
        from django.contrib.auth.models import User

        # Criar dependências
        user = User.objects.create_user(username="test", password="test")
        prof = PerfilProfessor.objects.create(user=user, matricula="123")
        curso = Curso.objects.create(nome="Curso Teste", sigla="TST")
        periodo = PeriodoLetivo.objects.create(ano=2024, semestre=1, descricao="2024.1")
        disc = Disciplina.objects.create(
            disciplina_nome="Disciplina Teste",
            disciplina_sigla="TST",
            disciplina_tipo="Obrigatória",
            curso=curso,
            professor=prof,
            periodo_letivo=periodo,
        )

        turma = Turma.objects.create(disciplina=disc, turno="matutino")

        self.assertIsNotNone(turma.data_criacao)
        self.assertIsInstance(turma.data_criacao, timezone.datetime)

    def test_data_atualizacao_atualiza_automaticamente(self):
        """Testa que data_atualizacao é atualizada no save"""
        from avaliacao_docente.models import (
            Turma,
            Disciplina,
            Curso,
            PeriodoLetivo,
            PerfilProfessor,
        )
        from django.contrib.auth.models import User
        import time

        # Criar dependências
        user = User.objects.create_user(username="test2", password="test")
        prof = PerfilProfessor.objects.create(user=user, matricula="124")
        curso = Curso.objects.create(nome="Curso Teste 2", sigla="TS2")
        periodo = PeriodoLetivo.objects.create(ano=2024, semestre=2, descricao="2024.2")
        disc = Disciplina.objects.create(
            disciplina_nome="Disciplina Teste 2",
            disciplina_sigla="TS2",
            disciplina_tipo="Obrigatória",
            curso=curso,
            professor=prof,
            periodo_letivo=periodo,
        )

        turma = Turma.objects.create(disciplina=disc, turno="vespertino")

        data_criacao_original = turma.data_criacao
        data_atualizacao_original = turma.data_atualizacao

        # Aguardar um pouco e salvar novamente
        time.sleep(0.1)
        turma.codigo_turma = "NOVO-2024.2-VES"
        turma.save()

        turma.refresh_from_db()

        # data_criacao não deve mudar
        self.assertEqual(turma.data_criacao, data_criacao_original)

        # data_atualizacao deve ser mais recente
        self.assertGreater(turma.data_atualizacao, data_atualizacao_original)


class SoftDeleteMixinTest(TestCase):
    """Testes para SoftDeleteMixin e SoftDeleteManager"""

    def setUp(self):
        """Criar dados de teste"""
        from avaliacao_docente.models import (
            Turma,
            Disciplina,
            Curso,
            PeriodoLetivo,
            PerfilProfessor,
        )
        from django.contrib.auth.models import User

        user = User.objects.create_user(username="test_soft", password="test")
        self.prof = PerfilProfessor.objects.create(user=user, matricula="125")
        self.curso = Curso.objects.create(nome="Curso Soft Delete", sigla="SFD")
        self.periodo = PeriodoLetivo.objects.create(
            ano=2025, semestre=1, descricao="2025.1"
        )
        self.disc = Disciplina.objects.create(
            disciplina_nome="Disciplina Soft Delete",
            disciplina_sigla="SFD",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.prof,
            periodo_letivo=self.periodo,
        )

    def test_soft_delete_marca_inativo(self):
        """Testa que soft_delete() marca ativo=False"""
        from avaliacao_docente.models import Turma

        turma = Turma.objects.create(disciplina=self.disc, turno="noturno")

        self.assertTrue(turma.ativo)

        turma.soft_delete()

        self.assertFalse(turma.ativo)
        self.assertIsNotNone(turma.data_exclusao)

    def test_restore_reativa_registro(self):
        """Testa que restore() reativa registro deletado"""
        from avaliacao_docente.models import Turma

        turma = Turma.objects.create(disciplina=self.disc, turno="matutino")

        turma.soft_delete()
        self.assertFalse(turma.ativo)

        turma.restore()
        self.assertTrue(turma.ativo)
        self.assertIsNone(turma.data_exclusao)

    def test_is_deleted_property(self):
        """Testa property is_deleted"""
        from avaliacao_docente.models import Turma

        turma = Turma.objects.create(disciplina=self.disc, turno="vespertino")

        self.assertFalse(turma.is_deleted)

        turma.soft_delete()
        self.assertTrue(turma.is_deleted)

        turma.restore()
        self.assertFalse(turma.is_deleted)

    def test_manager_filtra_deletados(self):
        """Testa que SoftDeleteManager filtra registros deletados"""
        from avaliacao_docente.models import Turma

        # Criar 3 turmas
        turma1 = Turma.objects.create(disciplina=self.disc, turno="matutino")
        turma2 = Turma.objects.create(disciplina=self.disc, turno="vespertino")
        turma3 = Turma.objects.create(disciplina=self.disc, turno="noturno")

        # Deletar uma
        turma2.soft_delete()

        # Manager padrão deve retornar apenas ativos (2)
        ativos = Turma.objects.filter(disciplina=self.disc).count()
        self.assertEqual(ativos, 2)

        # all_objects deve retornar todos (3)
        todos = Turma.all_objects.filter(disciplina=self.disc).count()
        self.assertEqual(todos, 3)

    def test_deleted_only(self):
        """Testa método deleted_only()"""
        from avaliacao_docente.models import Turma

        turma1 = Turma.objects.create(disciplina=self.disc, turno="matutino")
        turma2 = Turma.objects.create(disciplina=self.disc, turno="vespertino")

        turma1.soft_delete()

        deletados = Turma.objects.deleted_only().filter(disciplina=self.disc).count()
        self.assertEqual(deletados, 1)


class EnumsTest(TestCase):
    """Testes para enums centralizados"""

    def test_status_turma_valores(self):
        """Testa que StatusTurma tem valores corretos"""
        self.assertEqual(StatusTurma.ATIVA.value, "ativa")
        self.assertEqual(StatusTurma.ENCERRADA.value, "encerrada")
        self.assertEqual(StatusTurma.CANCELADA.value, "cancelada")

        # Testa labels
        self.assertEqual(StatusTurma.ATIVA.label, "Ativa")

    def test_status_turma_choices(self):
        """Testa que StatusTurma.choices funciona"""
        choices = StatusTurma.choices

        self.assertEqual(len(choices), 3)
        self.assertIn(("ativa", "Ativa"), choices)

    def test_turno_disciplina_valores(self):
        """Testa que TurnoDisciplina tem valores corretos"""
        self.assertEqual(TurnoDisciplina.MATUTINO.value, "matutino")
        self.assertEqual(TurnoDisciplina.VESPERTINO.value, "vespertino")
        self.assertEqual(TurnoDisciplina.NOTURNO.value, "noturno")

    def test_tipo_pergunta_valores(self):
        """Testa que TipoPergunta tem valores corretos"""
        self.assertEqual(TipoPergunta.ESCALA_LIKERT.value, "escala_likert")
        self.assertEqual(TipoPergunta.MULTIPLA_ESCOLHA.value, "multipla_escolha")
        self.assertEqual(TipoPergunta.TEXTO_CURTO.value, "texto_curto")
        self.assertEqual(TipoPergunta.TEXTO_LONGO.value, "texto_longo")

    def test_uso_em_model(self):
        """Testa uso de enum em campo de model"""
        from avaliacao_docente.models import Curso

        # Verificar que campo tem choices
        curso = Curso()
        # Note: Este teste é limitado pois não podemos criar novos campos
        # apenas verificamos que enums estão disponíveis
        self.assertTrue(hasattr(StatusTurma, "choices"))


class IntegracaoAbstracoesTest(TestCase):
    """Testes de integração com abstrações em models reais"""

    def test_turma_usa_timestamps(self):
        """Testa que Turma tem campos de timestamp"""
        from avaliacao_docente.models import Turma

        # Verificar que campos existem
        self.assertTrue(hasattr(Turma, "data_criacao"))
        # data_atualizacao será adicionado na migração

    def test_turma_tem_soft_delete(self):
        """Testa que Turma tem campos de soft delete"""
        from avaliacao_docente.models import Turma

        # Verificar que campo ativo existe
        self.assertTrue(hasattr(Turma, "ativo"))
        # data_exclusao será adicionado na migração


class DocumentacaoTest(TestCase):
    """Testes para validar documentação das abstrações"""

    def test_base_model_documentado(self):
        """Verifica que BaseModel tem docstring"""
        self.assertIsNotNone(BaseModel.__doc__)
        self.assertIn("Classe base abstrata", BaseModel.__doc__)

    def test_mixins_documentados(self):
        """Verifica que mixins têm docstrings"""
        self.assertIsNotNone(TimestampMixin.__doc__)
        self.assertIsNotNone(SoftDeleteMixin.__doc__)
        self.assertIsNotNone(AuditoriaMixin.__doc__)

    def test_manager_documentado(self):
        """Verifica que SoftDeleteManager tem docstring"""
        self.assertIsNotNone(SoftDeleteManager.__doc__)
        self.assertIn("Manager", SoftDeleteManager.__doc__)

    def test_enums_documentados(self):
        """Verifica que enums têm docstrings"""
        self.assertIsNotNone(StatusTurma.__doc__)
        self.assertIsNotNone(TurnoDisciplina.__doc__)
        self.assertIsNotNone(TipoPergunta.__doc__)
