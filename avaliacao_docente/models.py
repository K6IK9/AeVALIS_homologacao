from django.db import models
from django.contrib.auth.models import User


class PerfilProfessorManager(models.Manager):
    """Manager customizado para excluir usuários admin"""

    def get_queryset(self):
        from rolepermissions.checkers import has_role

        return (
            super()
            .get_queryset()
            .exclude(
                user__id__in=[
                    user.id for user in User.objects.all() if has_role(user, "admin")
                ]
            )
        )

    def non_admin(self):
        """Retorna apenas professores que não são admin"""
        return self.get_queryset()


class PerfilAlunoManager(models.Manager):
    """Manager customizado para excluir usuários admin"""

    def get_queryset(self):
        from rolepermissions.checkers import has_role

        return (
            super()
            .get_queryset()
            .exclude(
                user__id__in=[
                    user.id for user in User.objects.all() if has_role(user, "admin")
                ]
            )
        )

    def non_admin(self):
        """Retorna apenas alunos que não são admin"""
        return self.get_queryset()


class PerfilAluno(models.Model):
    """
    Extensão do modelo User para dados específicos de alunos
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_aluno"
    )
    situacao = models.CharField(max_length=45, default="Ativo")

    objects = models.Manager()  # Manager padrão
    non_admin = PerfilAlunoManager()  # Manager que exclui admins

    objects = PerfilAlunoManager()

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.username}"

    @property
    def matricula(self):
        return self.user.username

    @property
    def nome_completo(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def email(self):
        return self.user.email


class PerfilProfessor(models.Model):
    """
    Extensão do modelo User para dados específicos de professores
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_professor"
    )
    registro_academico = models.CharField(max_length=45)

    objects = models.Manager()  # Manager padrão
    non_admin = PerfilProfessorManager()  # Manager que exclui admins

    objects = PerfilProfessorManager()

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registro_academico})"


class Curso(models.Model):
    curso_nome = models.CharField(max_length=45)
    curso_sigla = models.CharField(max_length=10)
    coordenador_curso = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="cursos"
    )

    def __str__(self):
        return f"{self.curso_nome} ({self.curso_sigla})"


class PeriodoLetivo(models.Model):
    SEMESTRE_CHOICES = [
        (1, "1º Semestre"),
        (2, "2º Semestre"),
        (3, "3º Semestre"),
        (4, "4º Semestre"),
        (5, "5º Semestre"),
        (6, "6º Semestre"),
        (7, "7º Semestre"),
        (8, "8º Semestre"),
        (9, "9º Semestre"),
        (10, "10º Semestre"),
    ]

    nome = models.CharField(max_length=50)
    ano = models.IntegerField()
    semestre = models.IntegerField(choices=SEMESTRE_CHOICES)

    class Meta:
        unique_together = ["ano", "semestre"]
        ordering = ["-ano", "-semestre"]

    def __str__(self):
        return f"{self.nome} - {self.ano}.{self.semestre}"


class Disciplina(models.Model):
    TIPO_CHOICES = [
        ("Obrigatória", "Obrigatória"),
        ("Optativa", "Optativa"),
    ]

    disciplina_nome = models.CharField(max_length=100)
    disciplina_sigla = models.CharField(max_length=45)
    disciplina_tipo = models.CharField(max_length=45, choices=TIPO_CHOICES)
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="disciplinas"
    )
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="disciplinas"
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo, on_delete=models.CASCADE, related_name="disciplinas"
    )

    def __str__(self):
        return f"{self.disciplina_nome} ({self.disciplina_sigla})"


class Avaliacao(models.Model):
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status_avaliacao = models.CharField(max_length=15)
    professor_disciplina = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="avaliacoes"
    )

    def __str__(self):
        return f"Avaliação de {self.professor_disciplina} [{self.status_avaliacao}]"


class Pergunta(models.Model):
    enunciado_pergunta = models.CharField(max_length=150)
    tipo_pergunta = models.CharField(max_length=20)

    def __str__(self):
        return self.enunciado_pergunta


class AvaliacaoPergunta(models.Model):
    avaliacao = models.ForeignKey(
        Avaliacao, on_delete=models.CASCADE, related_name="perguntas"
    )
    pergunta = models.ForeignKey(
        Pergunta, on_delete=models.CASCADE, related_name="avaliacoes"
    )

    def __str__(self):
        return f"{self.pergunta} na {self.avaliacao}"


class RespostaAluno(models.Model):
    """
    Agora usa PerfilAluno em vez da tabela Aluno
    """

    resposta_pergunta = models.CharField(max_length=300)
    aluno = models.ForeignKey(
        PerfilAluno, on_delete=models.CASCADE, related_name="respostas"
    )
    avaliacao_pergunta = models.ForeignKey(
        AvaliacaoPergunta, on_delete=models.CASCADE, related_name="respostas"
    )

    def __str__(self):
        return f"{self.aluno} respondeu '{self.resposta_pergunta[:30]}...'"


class Turma(models.Model):
    """
    Modelo principal para gerenciar turmas
    """

    TURNO_CHOICES = [
        ("matutino", "Matutino"),
        ("vespertino", "Vespertino"),
        ("noturno", "Noturno"),
    ]

    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("finalizada", "Finalizada"),
    ]

    codigo_turma = models.CharField(max_length=20, unique=True)  # Ex: "INFO3A-2024.1"
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name="turmas"
    )
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="turmas"
    )
    periodo_letivo = models.ForeignKey(
        PeriodoLetivo, on_delete=models.CASCADE, related_name="turmas"
    )

    turno = models.CharField(max_length=15, choices=TURNO_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="ativa")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["disciplina", "periodo_letivo", "turno"]
        ordering = ["periodo_letivo", "disciplina__disciplina_nome"]

    def save(self, *args, **kwargs):
        # Auto-gera código da turma se não existir
        if not self.codigo_turma:
            self.codigo_turma = f"{self.disciplina.disciplina_sigla}-{self.periodo_letivo.ano}.{self.periodo_letivo.semestre}-{self.turno[:3].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_turma} - {self.disciplina.disciplina_nome}"

    def count_alunos_matriculados(self):
        """
        Conta apenas alunos matriculados (exclui admins)
        """
        from rolepermissions.checkers import has_role

        count = 0
        for matricula in self.matriculas.filter(status="ativa"):
            if not has_role(matricula.aluno.user, "admin"):
                count += 1
        return count


class MatriculaTurma(models.Model):
    """
    Relacionamento entre alunos e turmas (matrícula)
    """

    STATUS_MATRICULA_CHOICES = [
        ("ativa", "Ativa"),
        ("trancada", "Trancada"),
        ("cancelada", "Cancelada"),
        ("concluida", "Concluída"),
    ]

    aluno = models.ForeignKey(
        PerfilAluno, on_delete=models.CASCADE, related_name="matriculas"
    )
    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name="matriculas"
    )

    data_matricula = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15, choices=STATUS_MATRICULA_CHOICES, default="ativa"
    )

    class Meta:
        unique_together = ["aluno", "turma"]
        ordering = ["data_matricula"]

    def __str__(self):
        return f"{self.aluno.user.get_full_name()} em {self.turma.codigo_turma}"


class HorarioTurma(models.Model):
    """
    Horários das aulas da turma
    """

    DIAS_SEMANA_CHOICES = [
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
    ]

    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="horarios")
    dia_semana = models.IntegerField(choices=DIAS_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        unique_together = ["turma", "dia_semana", "hora_inicio"]
        ordering = ["dia_semana", "hora_inicio"]

    def __str__(self):
        return f"{self.turma.codigo_turma} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"
