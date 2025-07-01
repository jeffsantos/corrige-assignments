# Contexto do Projeto: Sistema de Correção Automática de Assignments

## 📋 Visão Geral

Este documento registra o contexto, decisões de design e padrões estabelecidos durante o desenvolvimento do **Sistema de Correção Automática de Assignments**. O projeto é uma ferramenta educacional que combina análise de IA (OpenAI GPT) com execução de testes automatizados para avaliar trabalhos de programação.

## 🏗️ Arquitetura e Decisões de Design

### Estrutura de Camadas (Clean Architecture)

O projeto segue uma arquitetura em camadas bem definida:

```
src/
├── domain/           # Camada de domínio (entidades e regras de negócio)
├── repositories/     # Camada de acesso a dados
├── services/         # Camada de serviços (lógica de aplicação)
├── utils/            # Utilitários e helpers
└── main.py          # Ponto de entrada (CLI)
```

**Decisão**: Separação clara de responsabilidades usando Clean Architecture para facilitar manutenção e testes.

### Padrões de Naming

#### Classes e Módulos
- **Classes de Serviço**: Sufixo `Service` (ex: `CorrectionService`, `AIAnalyzer`)
- **Classes de Repositório**: Sufixo `Repository` (ex: `AssignmentRepository`, `SubmissionRepository`)
- **Classes de Utilitário**: Sufixo `Generator` ou `Manager` (ex: `ReportGenerator`, `PromptManager`)
- **Classes de Teste**: Sufixo `Test` (ex: `PytestExecutor`)

#### Variáveis e Métodos
- **Variáveis**: snake_case (ex: `assignment_name`, `submission_path`)
- **Métodos**: snake_case (ex: `correct_assignment`, `calculate_final_score`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `OPENAI_API_KEY`, `TEST_TIMEOUT`)
- **Enums**: PascalCase (ex: `AssignmentType`, `SubmissionType`)

#### Arquivos e Diretórios
- **Módulos Python**: snake_case (ex: `correction_service.py`, `ai_analyzer.py`)
- **Diretórios**: snake_case (ex: `enunciados/`, `respostas/`, `reports/`)
- **Configurações**: `config.py` (centralizado)

## 🎯 Decisões de Design Principais

### 1. Suporte a Submissões Individuais e em Grupo

**Decisão**: Sistema flexível que suporta tanto submissões individuais quanto em grupo, configurado por assignment.

**Implementação**:
```python
# config.py
ASSIGNMENT_SUBMISSION_TYPES = {
    "prog1-tarefa-html-curriculo": SubmissionType.INDIVIDUAL,
    "prog1-prova-av": SubmissionType.GROUP,
}
```

**Padrão**: Configuração centralizada em `config.py` para facilitar manutenção.

### 2. Sistema de Prompts Personalizados

**Decisão**: Prompts específicos por assignment para análise mais precisa da IA.

**Estrutura**:
```
prompts/
├── assignment-name/
│   └── prompt.txt    # Prompt personalizado
```

**Padrão**: Prompts versionados separadamente dos enunciados para controle de versão.

### 3. Sistema de Logs de Auditoria

**Decisão**: Logs completos de todas as análises da IA para transparência e auditoria.

**Estrutura**:
```
logs/
├── YYYY-MM-DD/
│   └── assignment-name/
│       └── submission_analysis_timestamp.json
```

**Padrão**: Logs não versionados (`.gitignore`) mas estruturados para fácil consulta.

### 4. Múltiplos Formatos de Relatório

**Decisão**: Suporte a múltiplos formatos de saída (console, HTML, Markdown, JSON).

**Padrão**: 
- JSON como formato base (dados estruturados)
- Conversão para outros formatos sem re-execução
- Comandos separados para conversão (`convert-report`, `convert-latest`)

## 📝 Padrões de Documentação e Comentários

### Docstrings

**Padrão**: Docstrings simples e concisas, preferencialmente apenas com descrição. Campos adicionais (Args, Returns, Raises) apenas quando necessário para esclarecimento.

**Exemplo de docstring simples**:
```python
def correct_assignment(self, assignment_name: str, turma_name: str, 
                      submission_identifier: Optional[str] = None) -> CorrectionReport:
    """Corrige um assignment específico."""
```

**Exemplo de docstring com campos adicionais** (apenas quando necessário):
```python
def _save_ai_log(self, assignment_name: str, submission_identifier: str, 
                 analysis_type: str, prompt: str, raw_response: str, 
                 parsed_result: dict) -> None:
    """Salva log de auditoria da análise de IA.
    
    Args:
        assignment_name: Nome do assignment sendo analisado
        submission_identifier: Identificador da submissão (login ou grupo)
        analysis_type: Tipo de análise (python, html)
        prompt: Prompt enviado para a IA
        raw_response: Resposta raw da IA
        parsed_result: Resultado processado da análise
    """
```

**Princípio**: Manter documentação simples e adicionar detalhes apenas quando o método/parâmetro não for autoexplicativo.

### Comentários Inline

**Padrão**: Comentários explicativos para lógica complexa, não para código óbvio.

```python
# Calcula nota final ponderada
final_score = (test_score * 0.4) + (ai_score * 0.6)
```

### README.md

**Padrão**: Documentação completa com exemplos práticos, incluindo:
- Instalação e configuração
- Exemplos de uso para cada comando
- Explicação da estrutura do projeto
- Troubleshooting comum

## 🔧 Padrões de Configuração

### Configuração Centralizada

**Decisão**: Todas as configurações em `config.py` para facilitar manutenção.

```python
# Configurações da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3

# Configurações de teste
TEST_TIMEOUT = 30  # segundos
MAX_TEST_OUTPUT = 1000  # caracteres
```

### Configuração de API Keys

**Padrão**: Busca automática da API key em ordem de prioridade:
1. Variável de ambiente `OPENAI_API_KEY`
2. Arquivo `~/.secrets/open-ai-api-key.txt`
3. Arquivo `.secrets/open-ai-api-key.txt`

## 🧪 Padrões de Teste

### Estrutura de Testes

**Padrão**: Testes organizados por módulo com prefixo `test_`.

```
tests/
├── test_models.py      # Testes dos modelos de domínio
├── test_services.py    # Testes dos serviços
└── logs/              # Logs de teste (não versionados)
```

### Naming de Testes

**Padrão**: `test_{method_name}_{scenario}`

```python
def test_correct_assignment_single_submission(self):
    """Testa correção de assignment com submissão única."""

def test_correct_assignment_all_submissions(self):
    """Testa correção de assignment com todas as submissões."""
```

## 🎨 Padrões de UI/UX (CLI)

### Uso do Rich para Interface

**Decisão**: Biblioteca Rich para interface CLI rica e colorida.

**Padrão**:
- Painéis para títulos de seções
- Cores consistentes (azul para títulos, verde para sucesso, vermelho para erro)
- Barras de progresso para operações longas

```python
console.print(Panel(f"[bold blue]Corrigindo assignment {assignment} da turma {turma}[/bold blue]"))

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    task = progress.add_task("Processando submissões...", total=None)
```

### Comandos CLI

**Padrão**: Comandos verbosos e descritivos com opções bem documentadas.

```python
@cli.command()
@click.option('--assignment', '-a', help='Nome do assignment para corrigir')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--submissao', '-s', help='Identificador da submissão')
```

## 🔄 Padrões de Processamento

### Tratamento de Erros

**Padrão**: Exceções específicas com mensagens claras e logging apropriado.

```python
try:
    report = correction_service.correct_assignment(assignment, turma, submissao)
except ValueError as e:
    console.print(f"[red]Erro: {str(e)}[/red]")
    sys.exit(1)
except Exception as e:
    console.print(f"[red]Erro inesperado: {str(e)}[/red]")
    sys.exit(1)
```

### Processamento Assíncrono

**Decisão**: Processamento sequencial com feedback visual para operações longas.

**Padrão**: Uso de Progress bars e spinners para manter o usuário informado.

## 📊 Padrões de Dados

### Modelos de Domínio

**Padrão**: Dataclasses para representar entidades do domínio.

```python
@dataclass
class IndividualSubmission:
    """Submissão individual de um aluno."""
    github_login: str
    assignment_name: str
    turma: str
    submission_path: Path
    files: List[str] = field(default_factory=list)
    test_results: List[AssignmentTestExecution] = field(default_factory=list)
    code_analysis: Optional[CodeAnalysis] = None
    html_analysis: Optional[HTMLAnalysis] = None
    final_score: float = 0.0
    feedback: str = ""
```

### Serialização JSON

**Padrão**: Métodos `to_dict()` e `load_from_file()` para persistência.

```python
def to_dict(self) -> Dict[str, Any]:
    """Converte o relatório para dicionário."""
    return {
        "assignment_name": self.assignment_name,
        "turma": self.turma,
        "generated_at": self.generated_at,
        # ...
    }
```

## 🚀 Padrões de Deploy e Distribuição

### Estrutura de Dependências

**Decisão**: Pipenv para gerenciamento de dependências e ambiente virtual.

**Padrão**: 
- `Pipfile` para dependências principais
- `Pipfile.lock` para versões fixas
- `setup.py` para instalação como pacote

### Estrutura de Diretórios

**Padrão**: Separação clara entre código versionado e dados não versionados.

```
corrige-assignments/
├── src/              # Código fonte (versionado)
├── enunciados/       # Enunciados (não versionado)
├── respostas/        # Submissões (não versionado)
├── reports/          # Relatórios (não versionado)
├── logs/             # Logs (não versionado)
└── prompts/          # Prompts (versionado)
```

## 🔍 Padrões de Debugging e Monitoramento

### Logging Estruturado

**Padrão**: Logs JSON estruturados com metadados completos.

```json
{
  "metadata": {
    "assignment_name": "prog1-prova-av",
    "submission_identifier": "joao-silva",
    "analysis_type": "python",
    "timestamp": "2025-01-15T10:30:14.095265",
    "ai_model": "gpt-3.5-turbo"
  },
  "prompt": "...",
  "raw_response": "...",
  "parsed_result": {...}
}
```

### Tratamento de Warnings

**Decisão**: Eliminação de warnings do pytest para manter código limpo.

**Padrão**: Renomeação de classes que conflitam com pytest (ex: `TestResult` → `AssignmentTestResult`).

## 📈 Padrões de Performance

### Execução de Testes

**Decisão**: Execução direta na pasta do aluno sem cópia para performance.

**Padrão**: Timeout configurável e limitação de output para evitar travamentos.

```python
TEST_TIMEOUT = 30  # segundos
MAX_TEST_OUTPUT = 1000  # caracteres
```

### Análise de IA

**Decisão**: Configurações otimizadas para balancear qualidade e custo.

**Padrão**: 
- Modelo: `gpt-3.5-turbo` (bom custo-benefício)
- Max tokens: 1000 (suficiente para análise)
- Temperature: 0.3 (consistente mas não muito rígido)

## 🎯 Diretrizes para Futuras Implementações

### Novos Recursos

1. **Mantenha a arquitetura em camadas**
2. **Use os padrões de naming estabelecidos**
3. **Documente com docstrings no estilo Google**
4. **Configure novos assignments em `config.py`**
5. **Crie prompts personalizados quando necessário**
6. **Implemente logs de auditoria para operações críticas**
7. **Mantenha compatibilidade com formatos de relatório existentes**

### Refatorações

1. **Preserve a interface pública dos serviços**
2. **Mantenha compatibilidade com relatórios JSON existentes**
3. **Atualize documentação quando necessário**
4. **Execute testes após mudanças**
5. **Verifique se não há warnings do pytest**

### Manutenção

1. **Revise logs de auditoria periodicamente**
2. **Atualize prompts baseado no feedback**
3. **Monitore performance de testes**
4. **Mantenha dependências atualizadas**
5. **Verifique configurações de API keys**

---

**Última atualização**: Janeiro 2025  
**Versão do projeto**: 1.0.0  
**Mantenedor**: Jefferson Santos (jefferson.santos@fgv.br) 