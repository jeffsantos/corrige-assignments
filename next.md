### Miscelânea

- readme muito grande + docs + contexto.md
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
### Erro deecução do Streamlit não está sendo considerada ao enviar para IA

Durante minha última execução de correção dos assingments prog2-prova, notei o seguinte caso: na turma da barra, a aluna mariclaraluz recebeu nota 10 na correção da IA, embora a aplicação streamlit que ela entregou (app_streamlit.py) execute com erros. O teste correspondente passa 100% porque só analisa os elementos estáticos do programa (presentes no caso dessa aluna), mas não levou em consideração o resultado da execução, mas deveria, já que o programa que envia a correção para ser feita pela IA embute os resultados dos testes e da execução para ela. Eu renomeei os logs e reports dessa correção para facilitar minha avaliação. Os logs salvos com a situação dessa aluna podem ser encontrados nas pastas logs/2025-10-06-prog2-prova e os reports estão em reports/2025-10-06-prog2-prova. Isso parece ser um problema da correção de tarefas streamlit. Qualquer solução deve ser integrada à estrutura atual do código, mantendo a consistência com o que já foi feito e com os padrões de programação estabelecidos no contexto.md e em docs/*.md. Os arquivos README.md e CLAUDE.md tratam dos propósitos gerais e funcionamento do projeto. Alguns erros de execução streamlit não são exibidos no terminal, mas podem ser capturados, pois são exibidos no browser em uma div com class stException. 

Pode-se testar o caso acima com o comando abaixo: 

python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog2-prova --submissao mariclaraluz.


--------------------------------------------------
### Sintaxes não tratadas no teste de bd

Quando o CREATE TABLE no bd.sql usa a sintaxe CREATE TABLE IF NOT EXISTS (como o do aluno arthurrrangel em prog2-prova) a expressão regular do test_bd não está reconhecendo. O mesmo ocorre quando o CREATE
  TABLE usa o schema para determinar a tabela como em CREATE TABLE esquema.tabela.