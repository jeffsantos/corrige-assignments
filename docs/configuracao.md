# Guia de Configuração

Este documento detalha todas as configurações disponíveis no sistema.

## Configuração da API OpenAI

O sistema busca automaticamente a API key na seguinte ordem:

1. Variável de ambiente `OPENAI_API_KEY`
2. Arquivo `~/.secrets/open-ai-api-key.txt`
3. Arquivo `.secrets/open-ai-api-key.txt`

### Opção 1: Variável de Ambiente

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

### Opção 2: Arquivo de Segredos

```bash
mkdir -p ~/.secrets
echo "sua-chave-aqui" > ~/.secrets/open-ai-api-key.txt
```

### Configurações da API no config.py

```python
# config.py
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3
```

## Tipos de Submissão

Configure submissões individuais ou em grupo por assignment:

```python
# config.py
ASSIGNMENT_SUBMISSION_TYPES = {
    "prog1-tarefa-html-curriculo": SubmissionType.INDIVIDUAL,
    "prog1-prova-av": SubmissionType.GROUP,
}
```

### Padrões de Nomenclatura

- **Individuais**: `{assignment-name}-{login-do-aluno}`
- **Grupo**: `{assignment-name}-{nome-do-grupo}`

## Configuração de Thumbnails

### Para Streamlit

```python
# config.py
STREAMLIT_STARTUP_TIMEOUT = 30  # segundos para aguardar inicialização
STREAMLIT_PORT_RANGE = (8501, 8600)  # range de portas disponíveis
```

### Para Screenshots (Streamlit e HTML)

```python
# config.py
SCREENSHOT_WAIT_TIME = 3  # segundos para aguardar renderização
CHROME_WINDOW_SIZE = "1440,900"  # tamanho da janela do Chrome
```

### Assignments com Thumbnails

```python
# config.py
ASSIGNMENTS_WITH_THUMBNAILS = {
    "prog1-prova-av": "streamlit",
    "prog1-tarefa-html-curriculo": "html",
    "prog1-tarefa-html-tutorial": "html",
}
```

## Configuração de Execução Python

### Assignments Interativos

```python
# config.py
INTERACTIVE_ASSIGNMENTS = {
    "prog1-tarefa-scrap-yahoo": {
        "script": "main.py",
        "args": [],
        "inputs": ["PETR4.SA", "2024-01-01", "2024-12-31"],
        "expected_outputs": ["Dados salvos", "CSV gerado"]
    }
}
```

### Timeouts

```python
# config.py
TEST_TIMEOUT = 30  # segundos para testes
EXECUTION_TIMEOUT = 60  # segundos para execução Python
```

## Estrutura de Diretórios

### Diretórios Versionados

```
.
├── src/               # Código fonte
├── prompts/           # Prompts personalizados
├── docs/              # Documentação
├── specs/             # Especificações de implementações
└── tests/             # Testes do sistema
```

### Diretórios Não Versionados (gitignore)

```
.
├── enunciados/        # Enunciados dos assignments
├── respostas/         # Submissões dos alunos
├── reports/           # Relatórios gerados
└── logs/              # Logs de auditoria da IA
```

## Estrutura de Enunciados

Cada assignment deve ter a seguinte estrutura:

```
enunciados/
└── assignment-nome/
    ├── README.md          # Descrição e requisitos
    ├── arquivo-base.py    # Código fornecido ao aluno
    ├── tests/             # Testes da atividade
    │   └── test_*.py
    └── dados/             # Dados de exemplo (opcional)
```

## Estrutura de Prompts Personalizados

```
prompts/
└── assignment-nome/
    └── prompt.txt         # Prompt personalizado para IA
```

### Variáveis Disponíveis

- `{assignment_name}` - Nome do assignment
- `{assignment_description}` - Descrição do README.md
- `{assignment_requirements}` - Lista de requisitos
- `{student_code}` - Código do aluno formatado

## Estrutura de Respostas

```
respostas/
└── turma-nome/
    ├── assignment1-submissions/
    │   ├── assignment1-aluno1/          # Submissão individual
    │   ├── assignment1-grupo-abc/       # Submissão em grupo
    │   └── assignment1-outro-aluno/
    └── assignment2-submissions/
```

## Configuração de Pesos das Notas

Para alterar a ponderação entre testes e IA, edite `src/services/correction_service.py`:

```python
def _calculate_python_score(self, submission, assignment):
    # Configuração atual: 40% testes + 60% IA
    final_score = (test_score * 0.4) + (ai_score * 0.6)

    # Exemplo alternativo: 50% testes + 50% IA
    # final_score = (test_score * 0.5) + (ai_score * 0.5)

    return final_score
```

Para mais detalhes, consulte [Sistema de Cálculo de Notas](sistema-notas.md).

## Configuração de Testes

### Marcadores de Teste

```python
# pytest.ini ou pyproject.toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
    "thumbnails: marks tests that require Chrome/Selenium",
    "slow: marks tests as slow running"
]
```

### Execução Seletiva

```bash
# Apenas testes básicos
pytest tests/ -m "not integration and not thumbnails and not slow"

# Apenas testes de integração
pytest tests/ -m integration
```

## Dependências do Sistema

### Python Packages (Pipfile)

```toml
[packages]
pytest = "*"
pytest-json-report = "*"
openai = "*"
selenium = "*"
rich = "*"
pillow = "*"
psutil = "*"
click = "*"
```

### Sistema

- **Chrome/Chromium** - Para geração de thumbnails
- **ChromeDriver** - Compatível com versão do Chrome instalada

## Variáveis de Ambiente Úteis

```bash
# Caminho para ChromeDriver (se não estiver no PATH)
export CHROMEDRIVER_PATH="/path/to/chromedriver"

# Diretório de trabalho customizado
export TRABALHO_DIR="/path/to/trabalho"

# Nível de log
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## Ajustes de Performance

### Para Máquinas com Poucos Recursos

```python
# config.py
STREAMLIT_STARTUP_TIMEOUT = 60  # Aumentar timeout
SCREENSHOT_WAIT_TIME = 5  # Aguardar mais tempo
MAX_CONCURRENT_SUBMISSIONS = 1  # Processar uma de cada vez
```

### Para Máquinas Potentes

```python
# config.py
STREAMLIT_STARTUP_TIMEOUT = 15  # Reduzir timeout
SCREENSHOT_WAIT_TIME = 2  # Aguardar menos tempo
MAX_CONCURRENT_SUBMISSIONS = 5  # Processar em paralelo
```

## Solução de Problemas Comuns

### Erro: "ChromeDriver not found"

```bash
# Instalar ChromeDriver via sistema de pacotes
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Windows
# Baixar de https://chromedriver.chromium.org/
```

### Erro: "OPENAI_API_KEY not found"

```bash
# Verificar se a chave está configurada
echo $OPENAI_API_KEY

# Se vazio, configurar
export OPENAI_API_KEY="sua-chave-aqui"
```

### Thumbnails em Branco

```python
# Aumentar tempo de espera em config.py
SCREENSHOT_WAIT_TIME = 5  # ou mais
```

### Processos Streamlit Órfãos

```bash
# Verificar processos Streamlit
ps aux | grep streamlit

# Matar processos órfãos
pkill -f streamlit
```
