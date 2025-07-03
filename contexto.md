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

## 📝 Padrões de Mensagens de Commit

### Convenção Conventional Commits

**Decisão**: Seguir a convenção [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit.

**Formato**:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Tipos de Commit

**Padrão**: Tipos específicos para categorizar mudanças.

- **`feat`**: Nova funcionalidade
- **`fix`**: Correção de bug
- **`docs`**: Mudanças na documentação
- **`style`**: Mudanças que não afetam o código (formatação, espaços, etc.)
- **`refactor`**: Refatoração de código (não adiciona funcionalidade nem corrige bug)
- **`test`**: Adição ou correção de testes
- **`chore`**: Mudanças em arquivos de build, config, etc.

### Escopo (Scope)

**Padrão**: Escopo opcional para especificar área afetada.

- **`ai`**: Mudanças relacionadas à análise por IA
- **`cli`**: Mudanças na interface de linha de comando
- **`config`**: Mudanças em configurações
- **`models`**: Mudanças nos modelos de domínio
- **`tests`**: Mudanças nos testes
- **`docs`**: Mudanças na documentação
- **`prompts`**: Mudanças nos prompts personalizados

### Descrição

**Padrão**: Descrição clara e concisa em português.

- **Imperativo**: "Adiciona", "Corrige", "Remove", "Atualiza"
- **Conciso**: Máximo 80 caracteres
- **Claro**: Deve explicar o que a mudança faz

### Exemplos de Mensagens

```bash
# Nova funcionalidade
feat(ai): adiciona sistema de logs de auditoria para análises da IA

# Correção de bug
fix(tests): corrige timeout em execução de testes longos

# Documentação
docs: atualiza README com exemplos de uso dos novos comandos

# Refatoração
refactor(services): reorganiza AIAnalyzer para melhor separação de responsabilidades

# Configuração
chore(config): adiciona configuração para novo assignment HTML

# Testes
test(models): adiciona testes para serialização de relatórios

# Estilo
style: corrige formatação de docstrings em todo o projeto
```

### Corpo da Mensagem (Body)

**Padrão**: Detalhes adicionais quando necessário.

```bash
feat(ai): adiciona suporte a prompts personalizados por assignment

Permite que cada assignment tenha seu próprio prompt.txt na pasta prompts/.
O sistema carrega automaticamente o prompt personalizado ou usa o template padrão.

- Adiciona PromptManager para gerenciar prompts
- Implementa carregamento de prompts personalizados
- Mantém compatibilidade com prompts padrão
```

### Rodapé (Footer)

**Padrão**: Para referências a issues ou breaking changes.

```bash
feat(ai): adiciona configuração de temperatura da API OpenAI

BREAKING CHANGE: AIAnalyzer agora requer configuração explícita de temperatura

Closes #123
```

### Regras Importantes

1. **Sempre use tipos convencionais** (`feat`, `fix`, `docs`, etc.)
2. **Use escopo quando relevante** para identificar área afetada
3. **Descrição em português** para facilitar entendimento da equipe
4. **Mantenha descrição concisa** (máximo 80 caracteres)
5. **Use corpo para detalhes** quando a descrição não for suficiente
6. **Referencie issues** quando aplicável
7. **Um commit por mudança lógica** - evite múltiplos tipos em uma mensagem
8. **Consistência na capitalização** - sempre minúsculo no tipo e escopo

### Lidando com Múltiplas Mudanças

**Padrão**: Quando um commit inclui múltiplas mudanças relacionadas.

**Opção 1 - Commit único com corpo detalhado**:
```bash
feat(ai): adiciona parsing robusto e testes para respostas da IA

- Implementa parsing robusto para comentários com acentos
- Adiciona testes específicos para validação de parsing
- Mantém compatibilidade com respostas sem acentos
```

**Opção 2 - Commits separados** (recomendado):
```bash
feat(ai): adiciona parsing robusto para respostas da IA com acentos
test(ai): adiciona testes para validação de parsing de respostas
```

**Decisão**: Preferir commits separados para melhor rastreabilidade e changelog mais preciso.

### Integração com Ferramentas

**Decisão**: Padrão compatível com ferramentas de automação.

- **Semantic Versioning**: Commits `feat` e `fix` geram novas versões
- **Changelog**: Geração automática de changelog baseado em commits
- **CI/CD**: Análise automática de tipos de commit para pipelines

## 📚 Padrões de Documentação e Atualização

### Atualização Obrigatória de Documentação

**Decisão**: Sempre verificar e atualizar a documentação após cada mudança funcional.

**Regra**: Após qualquer mudança que afete funcionalidade, interface ou comportamento do sistema, **sempre verificar** se é necessário atualizar:

1. **`README.md`**: 
   - Novos comandos ou opções
   - Mudanças em exemplos de uso
   - Novas funcionalidades
   - Mudanças em configurações
   - Atualizações de troubleshooting

2. **`example_usage.py`**:
   - Novos exemplos de uso
   - Atualização de exemplos existentes
   - Adição de casos de uso com novas flags (ex: `--verbose`)
   - Demonstração de novas funcionalidades

### Checklist de Verificação

**Padrão**: Sempre executar este checklist após mudanças:

- [ ] **README.md**: Novos comandos/opções documentados?
- [ ] **README.md**: Exemplos atualizados?
- [ ] **README.md**: Troubleshooting atualizado?
- [ ] **example_usage.py**: Novos exemplos adicionados?
- [ ] **example_usage.py**: Exemplos existentes atualizados?
- [ ] **example_usage.py**: Novas flags demonstradas?

### Exemplos de Atualizações Necessárias

**Cenário 1 - Nova flag `--verbose`**:
```bash
# Adicionar ao README.md
# Mostrar logs detalhados de debug
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose

# Adicionar ao example_usage.py
print("  • Logs detalhados de debug com flag --verbose")
```

**Cenário 2 - Novo comando**:
```bash
# Adicionar ao README.md
### Comandos de Thumbnails Streamlit
python -m src.main generate-thumbnails-only --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Adicionar ao example_usage.py
print("\n📝 Exemplo 9: Geração de Thumbnails Streamlit")
```

**Cenário 3 - Nova funcionalidade**:
```bash
# Adicionar ao README.md
- 🖼️ **Geração automática de thumbnails** - Screenshots de dashboards Streamlit

# Adicionar ao example_usage.py
print("  • Captura screenshot de cada dashboard")
```

### Padrão de Exemplos no example_usage.py

**Formato estabelecido**:
```python
print("\n📝 Exemplo X: Título Descritivo")
print("-" * 50)
print("Assignment: nome-do-assignment")
print("Características:")
print("  • Característica 1")
print("  • Característica 2")
print("  • Característica 3")

# Comentar para não executar automaticamente
# cli(["comando", "--opcao", "valor"])
```

### Padrão de Seções no README.md

**Formato estabelecido**:
```markdown
### Comandos de [Categoria]

```bash
# Descrição do comando
python -m src.main comando --opcao valor

# Descrição de variação
python -m src.main comando --opcao valor --flag
```

### Exemplos de Uso

```bash
# Exemplo X: Descrição
python -m src.main comando --opcao valor

# Exemplo Xb: Descrição com variação
python -m src.main comando --opcao valor --flag
```
```

### Justificativa

**Por que é importante**:
1. **Consistência**: Manter documentação sempre atualizada
2. **Usabilidade**: Usuários precisam de exemplos práticos
3. **Manutenção**: Facilita onboarding de novos desenvolvedores
4. **Qualidade**: Documentação desatualizada é pior que sem documentação
5. **Profissionalismo**: Projeto bem documentado demonstra qualidade

### Exceções

**Quando NÃO atualizar**:
- Mudanças apenas em testes
- Refatorações internas que não afetam interface
- Correções de bugs que não mudam comportamento visível
- Mudanças apenas em logs ou debug

**Quando SEMPRE atualizar**:
- Novos comandos ou opções
- Mudanças em interface CLI
- Novas funcionalidades
- Mudanças em configurações
- Correções que afetam exemplos existentes

## 🎯 Diretrizes para Futuras Implementações

### Princípio Fundamental: Consistência de Padrões

**Regra**: Sempre seguir o padrão já estabelecido ao editar qualquer arquivo existente.

**Justificativa**: Manter consistência facilita manutenção, reduz confusão e garante que o código siga as convenções já definidas no projeto.

**Exemplos de aplicação**:
- **Arquivos de exemplo**: Seguir o formato `📝 Exemplo X: Título` com `"-" * 50` e características usando `•`
- **Testes**: Usar asserções `assert` do pytest, não `unittest.TestCase`
- **Docstrings**: Manter o padrão simples estabelecido
- **Estrutura de comandos**: Seguir o padrão de opções e formatação já definido
- **Mensagens de commit**: Usar a convenção Conventional Commits estabelecida

### Novos Recursos

1. **Mantenha a arquitetura em camadas**
2. **Use os padrões de naming estabelecidos**
3. **Documente com docstrings no estilo Google**
4. **Configure novos assignments em `config.py`**
5. **Crie prompts personalizados quando necessário**
6. **Implemente logs de auditoria para operações críticas**
7. **Mantenha compatibilidade com formatos de relatório existentes**
8. **Siga sempre o padrão já estabelecido no arquivo que está editando**

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