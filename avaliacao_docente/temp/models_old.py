from django.db import models

from django.db import models


class Curso(models.Model):
    curso_nome = models.CharField(max_length=45)

    def __str__(self):
        return self.curso_nome


class Professor(models.Model):
    professor_nome = models.CharField(max_length=150)
    registro_academico = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.professor_nome} ({self.registro_academico})"


class CoordenadorCurso(models.Model):
    professor = models.ForeignKey(
        Professor, on_delete=models.CASCADE, related_name="cursos_coordenados"
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="coordenadores"
    )

    def __str__(self):
        return f"{self.professor} coordena {self.curso}"


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
        Professor, on_delete=models.CASCADE, related_name="disciplinas"
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


class Aluno(models.Model):
    aluno_matricula = models.CharField(max_length=45)
    aluno_nome = models.CharField(max_length=100)
    aluno_email = models.CharField(max_length=100)
    aluno_situacao = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.aluno_nome} - {self.aluno_matricula}"


class DiarioProfessorDisciplina(models.Model):
    diario = models.ForeignKey(
        Diario, on_delete=models.CASCADE, related_name="entradas"
    )
    professor_disciplina = models.ForeignKey(
        ProfessorDisciplina, on_delete=models.CASCADE, related_name="diarios"
    )
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="diarios")

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
    resposta_pergunta = models.CharField(max_length=300)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="respostas")
    avaliacao_pergunta = models.ForeignKey(
        AvaliacaoPergunta, on_delete=models.CASCADE, related_name="respostas"
    )

    def __str__(self):
        return f"{self.aluno} respondeu '{self.resposta_pergunta[:30]}...'"
