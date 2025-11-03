### Miscelânea

- warnings de slow tests
- uma pasta prompts está surgindo dentro de tools
- ver ambientes pipenv criados para testes e não apagados
- dar minha nota pelo painel de cada execução.

--------------------------------------------------
### Rever chamada da API da OpenAI

https://platform.openai.com/docs/api-reference/chat/create

**max_tokens**

The maximum number of tokens that can be generated in the chat completion. This value can be used to control costs for text generated via API.

This value is now deprecated in favor of max_completion_tokens, and is not compatible with o-series models.

**max_completion_tokens**

An upper bound for the number of tokens that can be generated for a completion, including visible output tokens and reasoning tokens.

--------------------------------------------------
### Sobre assignments específicos

- rever todos os gabaritos com os testes. 

- yahoo 
	- desconsiderar teste --> erro no teste que forneci. rever depois. 
	- if content is not "" --> if content != ""

--------------------------------------------------
### Assignment interativo precisa ser setado em dois lugares

Além de ser setado no `config.py`, também precisa ser incluído hardcoded no `correction_service.py`, como pode ser visto abaixo. 

**src\services\correction_service.py - linha 113:**

```python
from config import assignment_has_python_execution

# Verifica se é um assignment interativo
if assignment.name in ["prog1-tarefa-scrap-yahoo", "prog1-prova-as", "prog2-prova"]:
	print(f"  🔄 Executando programa interativo para {submission.display_name}...")
	submission.python_execution = self.interactive_execution_service.execute_interactive_program(
		assignment.name, submission.submission_path
	)
```                       

--------------------------------------------------
### Sintaxes não tratadas no teste de bd

Quando o CREATE TABLE no bd.sql usa a sintaxe CREATE TABLE IF NOT EXISTS (como o do aluno arthurrrangel em prog2-prova) a expressão regular do test_bd não está reconhecendo. O mesmo ocorre quando o CREATE
  TABLE usa o schema para determinar a tabela como em CREATE TABLE esquema.tabela.
