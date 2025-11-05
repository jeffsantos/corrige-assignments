# Guia de Uso - Sistema de Correção Automática

Este guia documenta todos os comandos disponíveis no sistema de correção automática.

## Comando Principal - Processamento Completo

**Este é o comando mais importante do sistema:**

```bash
# Processamento completo de turma (correção + relatórios + thumbnails + CSV)
python -m src.main correct-all-with-visual --turma <turma-name>
```

**O que este comando faz:**
1. Executa testes e análise de IA para todos os assignments
2. Gera relatórios em todos os formatos (HTML/Markdown/JSON)
3. Cria relatórios visuais com thumbnails (quando aplicável)
4. Exporta resultados para CSV

**Variações comuns:**

```bash
# Processar apenas um assignment da turma
python -m src.main correct-all-with-visual --turma <turma-name> --assignment <assignment-name>

# Processar submissão específica
python -m src.main correct-all-with-visual --turma <turma-name> --assignment <assignment-name> --submissao <student-login>

# Com logs detalhados de debug
python -m src.main correct-all-with-visual --turma <turma-name> --verbose
```

## Outros Comandos de Correção

### Correção Básica

```bash
# Correção básica (apenas testes + IA)
python -m src.main correct --assignment <assignment-name> --turma <turma-name>

# Correção com relatórios visuais
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --with-visual-reports

# Correção de submissão específica
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --submissao <student-login>
```

## Comandos de Listagem

```bash
# Listar assignments disponíveis
python -m src.main list-assignments

# Listar turmas disponíveis
python -m src.main list-turmas

# Listar submissões de uma turma
python -m src.main list-submissions --turma <turma-name>
```

## Conversão de Relatórios

```bash
# Converter relatório específico para HTML
python -m src.main convert-report --assignment <assignment-name> --turma <turma-name> --format html

# Converter relatório específico para Markdown
python -m src.main convert-report --assignment <assignment-name> --turma <turma-name> --format markdown

# Converter o relatório JSON mais recente
python -m src.main convert-latest --format html
python -m src.main convert-latest --format markdown
```

## Exportação CSV

```bash
# Exportar resultados de um assignment
python -m src.main export-results --assignment <assignment-name> --turma <turma-name>

# Exportar todos os assignments de uma turma
python -m src.main export-results --turma <turma-name> --all-assignments

# Especificar diretório de saída personalizado
python -m src.main export-results --turma <turma-name> --all-assignments --output-dir reports/csv
```

### Estrutura do CSV

O arquivo CSV contém:
- assignment_name, turma, submission_identifier, submission_type
- test_score, ai_score, final_score, status
- tests_passed, tests_total, generated_at

## Geração de Thumbnails e Relatórios Visuais

```bash
# Gerar relatório visual com thumbnails (Streamlit/HTML)
python -m src.main generate-visual-report --assignment <assignment-name> --turma <turma-name>

# Gerar relatório visual de execução Python
python -m src.main generate-execution-visual-report --assignment <assignment-name> --turma <turma-name>

# Com logs detalhados
python -m src.main generate-visual-report --assignment <assignment-name> --turma <turma-name> --verbose
```

## Formatos de Relatório

### Formatos Disponíveis

- **Console**: Exibição colorida e formatada no terminal
- **HTML**: Relatório interativo com gráficos e navegação
- **Markdown**: Relatório em formato texto estruturado
- **JSON**: Dados estruturados para processamento posterior
- **CSV**: Tabela de resultados para análise em planilhas e BI

### Exemplo de Relatório Console

```
╭─────────────────────────────────────────────────────────────────╮
│ Relatório de Correção                                          │
│ Assignment: prog1-prova-av                                      │
│ Turma: ebape-prog-aplic-barra-2025                             │
│ Gerado em: 2025-07-01T10:30:14.095265                          │
╰─────────────────────────────────────────────────────────────────╯
     📈 Resumo Estatístico
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Métrica             ┃ Valor  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total de Submissões │ 1      │
│ Nota Média          │ 9.09   │
│ Taxa de Aprovação   │ 100.0% │
└─────────────────────┴────────┘
```

## Flags e Opções Comuns

### --verbose
Exibe logs detalhados de debug. Útil para troubleshooting e otimização.

```bash
python -m src.main <comando> --verbose
```

### --output-dir
Especifica diretório de saída personalizado para relatórios.

```bash
python -m src.main <comando> --output-dir <diretório>
```

### --output-format
Especifica formato de saída do relatório (html, markdown, json, console).

```bash
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --output-format html
```

## Testes

```bash
# Testes básicos (exclui integração, thumbnails, slow)
pipenv run pytest tests/ -m "not integration and not thumbnails and not slow"

# Todos os testes
pipenv run pytest tests/

# Apenas testes de integração
pipenv run pytest tests/ -m integration

# Apenas testes de thumbnails
pipenv run pytest tests/ -m thumbnails
```

## Solução de Problemas

### Para Streamlit

- **Thumbnails em branco**: Aumente `SCREENSHOT_WAIT_TIME` em config.py
- **Timeouts**: Aumente `STREAMLIT_STARTUP_TIMEOUT` em config.py
- **Conflitos de porta**: Ajuste `STREAMLIT_PORT_RANGE` em config.py

### Para HTML

- **Thumbnails em branco**: Aumente `SCREENSHOT_WAIT_TIME` em config.py
- **Arquivo não encontrado**: Verifique se index.html existe na submissão

### Para Assignments Interativos (Python)

- **Warnings do pipenv no STDERR**: Execute os comandos de correção **fora do terminal integrado do VS Code**
  - **Recomendado**: Use terminal externo (Windows Terminal, PowerShell, CMD, Git Bash)
  - **Alternativa 1**: `pipenv run python -m src.main correct-all-with-visual --turma <turma>`
  - **Alternativa 2**: Entre no shell primeiro: `pipenv shell` e depois `python -m src.main correct-all-with-visual --turma <turma>`
  - **Por quê**: O terminal integrado do VS Code pode carregar um ambiente virtual previamente, causando conflitos com o pipenv usado para executar código dos alunos
  - **Sintoma**: Mensagens de "Courtesy Notice: Pipenv found itself running within a virtual environment" aparecem no STDERR dos relatórios

### Geral

- **Debug detalhado**: Use flag `--verbose` para logs completos
- **Telas de alta resolução**: Suporte nativo para 2880x1620, 200% escala
