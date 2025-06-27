from django.db import models
from django.contrib.auth.models import User


class PerfilAluno(models.Model):
    """
    Extensão do modelo User para dados específicos de alunos
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_aluno"
    )
    situacao = models.CharField(max_length=45, default="Ativo")

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

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registro_academico})"


class PerfilCoordenador(models.Model):
    """
    Extensão do modelo User para dados específicos de coordenadores
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil_coordenador"
    )
    registro_academico = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registro_academico})"


class Curso(models.Model):
    curso_nome = models.CharField(max_length=45)
    curso_sigla = models.CharField(max_length=10)
    coordenador_curso = models.ForeignKey(
        PerfilCoordenador, on_delete=models.CASCADE, related_name="cursos"
    )

    def __str__(self):
        return f"{self.curso_nome} ({self.curso_sigla})"


class Disciplina(models.Model):
    disciplina_nome = models.CharField(max_length=100)
    disciplina_sigla = models.CharField(max_length=45)
    disciplina_tipo = models.CharField(max_length=45)
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="disciplinas"
    )

    def __str__(self):
        return f"{self.disciplina_nome} ({self.disciplina_sigla})"


class ProfessorDisciplina(models.Model):
    professor = models.ForeignKey(
        PerfilProfessor, on_delete=models.CASCADE, related_name="disciplinas"
    )
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name="professores"
    )

    def __str__(self):
        return f"{self.professor} - {self.disciplina}"


class Diario(models.Model):
    diario_periodo = models.CharField(max_length=45)
    ano_letivo = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.diario_periodo}/{self.ano_letivo}"


class DiarioProfessorDisciplina(models.Model):
    """
    Agora usa PerfilAluno em vez da tabela Aluno
    """

    diario = models.ForeignKey(
        Diario, on_delete=models.CASCADE, related_name="entradas"
    )
    professor_disciplina = models.ForeignKey(
        ProfessorDisciplina, on_delete=models.CASCADE, related_name="diarios"
    )
    aluno = models.ForeignKey(
        PerfilAluno, on_delete=models.CASCADE, related_name="diarios"
    )

    def __str__(self):
        return f"{self.aluno} em {self.professor_disciplina}"


class Avaliacao(models.Model):
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status_avaliacao = models.CharField(max_length=15)
    professor_disciplina = models.ForeignKey(
        ProfessorDisciplina, on_delete=models.CASCADE, related_name="avaliacoes"
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
