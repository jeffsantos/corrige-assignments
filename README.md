# Sistema de Correção Automática de Atividades

Sistema inteligente para correção automática de atividades de programação Python e HTML usando IA (OpenAI GPT) e testes automatizados com **detalhamento por função de teste**.

## 🎯 Funcionalidades

- **Análise Automática de Código Python**: Execução de testes com pytest e análise qualitativa usando IA
- **Detalhamento de Testes**: Resultados individuais por função de teste (ex: `test_parse_data_function_signature`)
- **Avaliação de Páginas HTML/CSS**: Verificação de elementos obrigatórios e análise de qualidade
- **Geração de Relatórios**: Múltiplos formatos (Console, HTML, Markdown, JSON)
- **Suporte a Múltiplas Turmas**: Gerenciamento de diferentes turmas e assignments
- **Integração com ChatGPT**: Análise qualitativa e feedback personalizado
- **Interface CLI**: Comando simples e intuitivo
- **Busca Automática da API OpenAI**: Configuração flexível da chave da API

## 🏗️ Arquitetura

O sistema segue uma arquitetura de **Domain-Driven Design (DDD)** com as seguintes camadas:

```
src/
├── domain/           # Modelos de domínio
│   └── models.py     # Entidades e objetos de valor
├── repositories/     # Acesso a dados
│   ├── assignment_repository.py
│   └── submission_repository.py
├── services/         # Lógica de negócio
│   ├── correction_service.py
│   ├── test_executor.py      # Execução direta na pasta do aluno
│   └── ai_analyzer.py        # Busca automática da API OpenAI
├── utils/            # Utilitários
│   └── report_generator.py   # Relatórios com detalhamento de testes
└── main.py          # Ponto de entrada CLI
```

## 📁 Estrutura do Projeto

```
corrige-assignments/
├── enunciados/           # Enunciados dos assignments
│   ├── prog1-prova-av/
│   ├── prog1-tarefa-html-curriculo/
│   └── ...
├── respostas/           # Submissões dos alunos por turma
│   ├── ebape-prog-aplic-barra-2025/
│   ├── ebape-prog-aplic-botafogo1-2025/
│   └── ...
├── src/                 # Código fonte do sistema
├── tests/               # Testes unitários
├── reports/             # Relatórios gerados
├── .secrets/            # Chaves de API (não versionado)
├── Pipfile              # Dependências do projeto
├── config.py            # Configurações
└── README.md            # Este arquivo
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos

- Python 3.13+
- pipenv
- Chave de API do OpenAI (opcional, mas recomendado)

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/jeffsantos/corrige-assignments.git
cd corrige-assignments

# Instale o pipenv (se não tiver)
pip install pipenv

# Instale as dependências
pipenv install

# Ative o ambiente virtual
pipenv shell
```

### 3. Configuração da API OpenAI

O sistema procura a chave da API OpenAI na seguinte ordem:

1. **Variável de ambiente** `OPENAI_API_KEY`
2. **Arquivo** `~/.secrets/open-ai-api-key.txt` (na home do usuário)
3. **Arquivo** `.secrets/open-ai-api-key.txt` (no diretório do projeto)

#### Opção 1: Variável de ambiente
```bash
# Linux/macOS
export OPENAI_API_KEY="sua-chave-api-aqui"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sua-chave-api-aqui"

# Windows (CMD)
set OPENAI_API_KEY=sua-chave-api-aqui
```

#### Opção 2: Arquivo na home do usuário
```bash
# Linux/macOS
mkdir -p ~/.secrets
echo "sua-chave-api-aqui" > ~/.secrets/open-ai-api-key.txt

# Windows
mkdir %USERPROFILE%\.secrets
echo sua-chave-api-aqui > %USERPROFILE%\.secrets\open-ai-api-key.txt
```

#### Opção 3: Arquivo no projeto
```bash
# Crie o diretório e arquivo
mkdir .secrets
echo "sua-chave-api-aqui" > .secrets/open-ai-api-key.txt
```

**Nota**: O arquivo `.secrets/` está no `.gitignore` para não ser versionado.

## 📖 Uso

### Interface de Linha de Comando (CLI)

#### Comandos Principais

```bash
# Listar assignments disponíveis
python -m src.main list-assignments

# Listar turmas disponíveis
python -m src.main list-turmas

# Listar alunos de uma turma
python -m src.main list-students --turma ebape-prog-aplic-barra-2025

# Corrigir um assignment específico
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Corrigir um aluno específico
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --aluno "nome-do-aluno"

# Corrigir todos os assignments de uma turma
python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments

# Gerar relatório em HTML
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-format html

# Gerar relatório em Markdown
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-format markdown
```

#### Opções de Saída

- `--output-format`: console, html, markdown, json
- `--output-dir`: diretório para salvar relatórios (padrão: reports/)
- `--all-assignments`: corrigir todos os assignments da turma

### Uso Programático

```python
from src.services.correction_service import CorrectionService
from src.utils.report_generator import ReportGenerator

# Inicializa serviços (API OpenAI será buscada automaticamente)
correction_service = CorrectionService(enunciados_path, respostas_path)
report_generator = ReportGenerator()

# Corrige um assignment
report = correction_service.correct_assignment(
    assignment_name="prog1-prova-av",
    turma_name="ebape-prog-aplic-barra-2025"
)

# Gera relatório com detalhamento de testes
report_generator.generate_console_report(report)
report.save_to_file("relatorio.json")
```

## 🔧 Configuração

### Arquivo `config.py`

```python
# Configurações da API OpenAI
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3

# Configurações de teste
TEST_TIMEOUT = 60  # segundos (aumentado para testes complexos)

# Rubricas padrão
PYTHON_RUBRIC = {
    "funcionamento_correto": 0.4,
    "qualidade_codigo": 0.3,
    "documentacao": 0.2,
    "criatividade": 0.1
}
```

## 📊 Relatórios

O sistema gera relatórios detalhados incluindo:

### Estatísticas Gerais
- Total de submissões
- Nota média, mínima e máxima
- Taxa de aprovação e excelência

### Análise por Aluno
- Nota final calculada
- **Detalhamento de testes por função** (ex: `test_parse_data_function_signature`)
- Status individual de cada teste (✅ passou, ❌ falhou, ⚠️ erro)
- Tempo de execução de cada teste
- Feedback da análise de IA
- Comentários e sugestões

### Exemplo de Relatório de Testes
```
🧪 Resultados dos Testes:
✅ test_scraping.py::test_fetch_page_function_signature (0.023s)
❌ test_scraping.py::test_parse_data_function_signature (0.045s)
✅ test_scraping.py::test_generate_csv_function_existence (0.012s)
✅ tests/test_app.py::test_streamlit_import (0.001s)
...
```

### Formatos de Saída
- **Console**: Exibição colorida e formatada com detalhamento de testes
- **HTML**: Relatório web interativo com estilos para diferentes status de teste
- **Markdown**: Documento estruturado com listas de testes
- **JSON**: Dados estruturados para processamento

## 🧪 Testes

### Execução de Testes
O sistema executa testes **diretamente na pasta da submissão do aluno**, garantindo:
- Fidelidade total ao ambiente do aluno
- Detecção de dependências e imports
- Execução em contexto real

### Detalhamento de Testes
- **pytest-json-report**: Gera relatórios JSON detalhados
- **Análise por função**: Cada teste individual é reportado
- **Tempo de execução**: Medição precisa do tempo de cada teste
- **Mensagens de erro**: Captura de tracebacks e erros específicos

```bash
# Executar todos os testes
pipenv run pytest

# Executar com cobertura
pipenv run pytest --cov=src

# Executar testes específicos
pipenv run pytest tests/test_models.py
```

## 🔍 Exemplos de Uso

### Exemplo 1: Correção de Assignment Python com Detalhamento

```bash
python -m src.main correct \
  --assignment prog1-prova-av \
  --turma ebape-prog-aplic-barra-2025 \
  --output-format html
```

**Saída esperada:**
```
📊 Sistema de Correção Automática
📈 Resumo Estatístico
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Métrica             ┃ Valor  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total de Submissões │ 1      │
│ Nota Média          │ 9.1    │
│ Taxa de Aprovação   │ 100.0% │
└─────────────────────┴────────┘

🧪 Resultados dos Testes:
✅ test_scraping.py::test_fetch_page_function_signature (0.023s)
❌ test_scraping.py::test_parse_data_function_signature (0.045s)
✅ test_scraping.py::test_generate_csv_function_existence (0.012s)
...
```

### Exemplo 2: Correção de Assignment HTML

```bash
python -m src.main correct \
  --assignment prog1-tarefa-html-curriculo \
  --turma ebape-prog-aplic-barra-2025 \
  --output-format markdown
```

### Exemplo 3: Análise de Aluno Específico

```bash
python -m src.main correct \
  --assignment prog1-prova-av \
  --turma ebape-prog-aplic-barra-2025 \
  --aluno "prog1-prova-av-ana-clara-e-isabella"
```

## 🤖 Análise de IA

O sistema usa a API do OpenAI para:

### Análise de Código Python
- Avaliação de qualidade do código
- Verificação de boas práticas
- Identificação de problemas
- Sugestões de melhoria

### Análise de HTML/CSS
- Verificação de elementos obrigatórios
- Avaliação de estrutura semântica
- Análise de estilização
- Feedback sobre responsividade

### Busca Automática da API
- Configuração flexível sem necessidade de variáveis de ambiente
- Suporte multiplataforma (Linux, macOS, Windows)
- Fallback para análise básica quando API não está disponível

## 📝 Critérios de Avaliação

### Assignments Python
- **40%**: Funcionamento correto (testes automatizados)
- **30%**: Qualidade do código (análise de IA)
- **20%**: Documentação
- **10%**: Criatividade

### Assignments HTML
- **40%**: Estrutura HTML
- **30%**: Estilização CSS
- **20%**: Responsividade
- **10%**: Criatividade

## 🛠️ Desenvolvimento

### Estrutura de Contribuição

1. **Domain Models**: Defina entidades e objetos de valor
2. **Repositories**: Implemente acesso a dados
3. **Services**: Adicione lógica de negócio
4. **Tests**: Escreva testes unitários
5. **Documentation**: Atualize documentação

### Padrões de Código

- **Type Hints**: Use tipagem estática
- **Docstrings**: Documente todas as funções
- **Error Handling**: Trate exceções adequadamente
- **Testing**: Mantenha cobertura de testes alta

### Melhorias Recentes

- ✅ **Detalhamento de testes por função**
- ✅ **Execução direta na pasta do aluno**
- ✅ **Busca automática da API OpenAI**
- ✅ **Relatórios aprimorados em múltiplos formatos**
- ✅ **Integração com pytest-json-report**

## 📄 Licença

Este projeto é desenvolvido para uso acadêmico na FGV.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Consulte a documentação
- Execute `python -m src.main --help` para ajuda
- Execute `python example_usage.py` para exemplos práticos

---

**Desenvolvido para o curso de Programação Aplicada da FGV** 