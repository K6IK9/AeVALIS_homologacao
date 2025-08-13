# Ajuste a fazer

1. input de matricula e senha muito grande em computador, sugerido um max width

2. aluno conseguiu responder mais de uma vez uma qestão marcada como unica erro: ntegrityError at /avaliacoes/responder/1/
```bash
duplicate key value violates unique constraint "avaliacao_docente_coment_avaliacao_id_aluno_id_se_49f0a80d_uniq"
DETAIL:  Key (avaliacao_id, aluno_id, session_key)=(1, 1, ) already exists.

Request Method: 	POST
Request URL: 	https://avaliacao-docente-novo.vercel.app/avaliacoes/responder/1/
Django Version: 	5.2.1
Exception Type: 	IntegrityError
Exception Value: 	

duplicate key value violates unique constraint "avaliacao_docente_coment_avaliacao_id_aluno_id_se_49f0a80d_uniq"
DETAIL:  Key (avaliacao_id, aluno_id, session_key)=(1, 1, ) already exists.

Exception Location: 	/var/task/django/db/backends/utils.py, line 105, in _execute
Raised during: 	avaliacao_docente.views.responder_avaliacao
Python Executable: 	/var/lang/bin/python
Python Version: 	3.12.11
Python Path: 	

['/var/task',
 '/var/lang/lib/python312.zip',
 '/var/lang/lib/python3.12',
 '/var/lang/lib/python3.12/lib-dynload',
 '/var/lang/lib/python3.12/site-packages']

Server time: 	Tue, 12 Aug 2025 21:23:21 -0400

```
3. 