# Sistema de Correção Automática de Assignments

Sistema inteligente para correção automática de assignments de programação usando IA (OpenAI GPT) e execução de testes automatizados.

## ✨ Funcionalidades Principais

- 🤖 **Análise de IA específica por assignment** - Prompts personalizados para cada atividade
- 📋 **Leitura automática de README.md** - Considera descrições e requisitos específicos
- 🏗️ **Análise de estrutura de enunciados** - Avalia se o aluno seguiu a estrutura fornecida
- 🧪 **Execução de testes detalhada** - Resultados por função com tempos de execução (PytestExecutor)
- 📊 **Relatórios em múltiplos formatos** - Console, HTML, Markdown e JSON
- 🔄 **Conversão de relatórios** - Converta JSON para HTML/Markdown sem re-execução
- 🔧 **Configuração flexível** - API key automática ou manual
- 🎯 **Critérios específicos** - Avaliação baseada nos requisitos de cada assignment
- 👥 **Suporte a submissões individuais e em grupo** - Configuração por assignment
- 📝 **Logs de auditoria da IA** - Registro completo das análises para transparência
- 🖼️ **Geração automática de thumbnails** - Screenshots de dashboards Streamlit e páginas HTML com captura completa
- 📈 **Relatórios visuais** - Interface HTML com thumbnails organizados por nota
- 🐍 **Relatórios visuais de execução Python** - Saídas de programas Python em interface visual organizada
- ⚡ **Performance otimizada** - Dependências instaladas uma única vez, limpeza automática de processos
- 🔍 **Debug opcional** - Flag --verbose para logs detalhados
- 🖥️ **Suporte a alta resolução** - Compatível com telas 2880x1620, 200% escala

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pipenv (recomendado) ou pip
- OpenAI API key (opcional, para análise de IA)
- Chrome/Chromium (para geração de thumbnails Streamlit)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/jeffersonsantos/corrige-assignments.git
cd corrige-assignments

# Instale as dependências
pipenv install

# Ative o ambiente virtual
pipenv shell
```

### Configuração da API OpenAI

O sistema busca automaticamente a API key na seguinte ordem:

1. Variável de ambiente `OPENAI_API_KEY`
2. Arquivo `~/.secrets/open-ai-api-key.txt`
3. Arquivo `.secrets/open-ai-api-key.txt`

```bash
# Opção 1: Variável de ambiente
export OPENAI_API_KEY="sua-chave-aqui"

# Opção 2: Arquivo de segredos
mkdir -p ~/.secrets
echo "sua-chave-aqui" > ~/.secrets/open-ai-api-key.txt
```

### Configuração de Tipos de Submissão

O sistema suporta submissões individuais e em grupo, configuradas por assignment no arquivo `config.py`:

```python
# config.py
ASSIGNMENT_SUBMISSION_TYPES = {
    # Assignments individuais
    "prog1-tarefa-html-curriculo": SubmissionType.INDIVIDUAL,
    "prog1-tarefa-scrap-simples": SubmissionType.INDIVIDUAL,
    
    # Assignments em grupo
    "prog1-prova-av": SubmissionType.GROUP,
}
```

### Configuração para Thumbnails Streamlit

Para gerar thumbnails de dashboards Streamlit, configure as seguintes opções em `config.py`:

```python
# Configurações de thumbnails
STREAMLIT_STARTUP_TIMEOUT = 30  # segundos para aguardar Streamlit inicializar
SCREENSHOT_WAIT_TIME = 3  # segundos para aguardar renderização completa
CHROME_WINDOW_SIZE = "1440,900"  # tamanho da janela do Chrome (otimizado para alta resolução)
STREAMLIT_PORT_RANGE = (8501, 8600)  # range de portas para Streamlit
```

**Novas funcionalidades otimizadas:**
- **Performance**: Dependências instaladas uma única vez por execução
- **Captura completa**: Altura mínima de 1800px para dashboards
- **Suporte a alta resolução**: Compatível com telas 2880x1620, 200% escala
- **Logs opcionais**: Flag `--verbose` para debug detalhado
- **Limpeza automática**: Processos órfãos removidos automaticamente

## 📁 Estrutura do Projeto

```
corrige-assignments/
├── doc/                          # Documentação técnica
│   └── sistema-notas.md          # Sistema de cálculo de notas
├── enunciados/                    # Enunciados dos assignments (não versionados)
│   ├── prog1-prova-av/
│   │   ├── README.md             # Descrição da atividade
│   │   ├── scraper.py            # Código base fornecido
│   │   └── tests/                # Testes da atividade
│   └── prog1-tarefa-html-curriculo/
│       ├── README.md
│       └── ...
├── prompts/                       # Prompts personalizados (versionados)
│   ├── prog1-prova-av/
│   │   └── prompt.txt            # Prompt personalizado
│   └── prog1-tarefa-html-curriculo/
│       └── prompt.txt            # Prompt personalizado
├── respostas/                     # Submissões dos alunos
│   └── ebape-prog-aplic-barra-2025/
│       └── prog1-prova-av-submissions/
│           └── aluno-nome/
├── reports/                       # Relatórios gerados
│   └── visual/                   # Relatórios visuais com thumbnails
│       └── thumbnails/           # Screenshots dos dashboards
├── logs/                          # Logs de auditoria da IA (não versionados)
│   └── YYYY-MM-DD/               # Logs organizados por data
│       └── assignment-name/      # Logs por assignment
├── src/                          # Código fonte
│   ├── services/
│   │   ├── ai_analyzer.py        # Análise de IA
│   │   ├── prompt_manager.py     # Gerenciador de prompts
│   │   ├── correction_service.py # Serviço principal
│   │   ├── test_executor.py      # Execução de testes (PytestExecutor)
│   │   └── streamlit_thumbnail_service.py # Geração de thumbnails
│   └── ...
└── example_usage.py              # Exemplos de uso
```

## 🎯 Uso

### Comando Principal

```bash
python -m src.main correct [OPÇÕES]
```

### Opções Disponíveis

```bash
# Corrigir assignment específico
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Corrigir submissão específica (aluno individual ou grupo)
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --submissao nome-do-aluno

# Corrigir todos os assignments de uma turma
python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments

# Corrigir com relatórios visuais (thumbnails)
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --with-visual-reports

# Corrigir todos os assignments com relatórios visuais
python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments --with-visual-reports

# Processamento completo de turma (correção + visuais + CSV)
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025

# Especificar formato de saída
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-format html

# Especificar diretório de saída
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-dir meus-relatorios

# Mostrar logs detalhados de debug
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose
```

### Comandos de Listagem

```bash
# Listar assignments disponíveis
python -m src.main list-assignments

# Listar turmas disponíveis
python -m src.main list-turmas

# Listar submissões de uma turma
python -m src.main list-submissions --turma ebape-prog-aplic-barra-2025
```

### Comandos de Conversão de Relatórios

```bash
# Converter um relatório específico para HTML
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format html

# Converter um relatório específico para Markdown
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format markdown

# Converter o relatório JSON mais recente para HTML
python -m src.main convert-latest --format html

# Converter o relatório JSON mais recente para Markdown
python -m src.main convert-latest --format markdown
```

### Comandos de Exportação CSV

```bash
# Exportar tabela de resultados de um assignment para CSV
python -m src.main export-results --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Exportar tabela de resultados de todos os assignments de uma turma para CSV
python -m src.main export-results --turma ebape-prog-aplic-barra-2025 --all-assignments

# Especificar diretório de saída para arquivos CSV
python -m src.main export-results --turma ebape-prog-aplic-barra-2025 --all-assignments --output-dir reports/csv
```

### Comandos de Thumbnails

```bash
# Gerar relatório visual com thumbnails (sem correção)
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Gerar relatório visual com thumbnails HTML
python -m src.main generate-visual-report --assignment prog1-tarefa-html-curriculo --turma ebape-prog-aplic-barra-2025

# Gerar relatório visual com logs detalhados
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose

# Especificar diretório de saída para relatórios visuais
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-dir reports/visual
```

### Comandos de Relatórios Visuais de Execução Python

```bash
# Gerar relatório visual de execução Python (sem correção)
python -m src.main generate-execution-visual-report --assignment prog1-tarefa-scrap-yahoo --turma ebape-prog-aplic-barra-2025

# Gerar relatório visual de execução com logs detalhados
python -m src.main generate-execution-visual-report --assignment prog1-tarefa-scrap-yahoo --turma ebape-prog-aplic-barra-2025 --verbose

# Especificar diretório de saída para relatórios de execução
python -m src.main generate-execution-visual-report --assignment prog1-tarefa-scrap-yahoo --turma ebape-prog-aplic-barra-2025 --output-dir reports/visual
```

### Comandos de Processamento Completo

```bash
# Processamento completo de turma (correção + visuais + CSV)
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025

# Processamento completo de apenas um assignment da turma
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog1-tarefa-scrap-simples

# Processamento completo de uma submissão específica
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog1-prova-av --submissao joao-silva

# Processamento completo com formato específico
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --output-format markdown

# Processamento completo com logs detalhados
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --verbose

# Processamento completo com diretório personalizado
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --output-dir meus-relatorios
```

### Exemplos de Uso

```bash
# Exemplo 1: Assignment com prompt personalizado
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Exemplo 2: Assignment HTML com critérios específicos
python -m src.main correct --assignment prog1-tarefa-html-curriculo --turma ebape-prog-aplic-barra-2025

# Exemplo 3: Correção de submissão específica
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --submissao joao-silva

# Exemplo 4: Correção completa de turma
python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments

# Exemplo 5: Relatório em HTML
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-format html

# Exemplo 5b: Correção com logs detalhados de debug
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose

# Exemplo 6: Converter relatório JSON existente para HTML
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format html

# Exemplo 7: Converter relatório JSON existente para Markdown
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format markdown

# Exemplo 8: Converter o relatório JSON mais recente para HTML
python -m src.main convert-latest --format html

# Exemplo 9: Converter o relatório JSON mais recente para Markdown
python -m src.main convert-latest --format markdown

# Exemplo 10: Ver assignments disponíveis
python -m src.main list-assignments

# Exemplo 11: Ver submissões de uma turma
python -m src.main list-submissions --turma ebape-prog-aplic-barra-2025

# Exemplo 12: Gerar relatório visual com thumbnails (Streamlit)
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Exemplo 13: Gerar relatório visual com thumbnails (HTML)
python -m src.main generate-visual-report --assignment prog1-tarefa-html-curriculo --turma ebape-prog-aplic-barra-2025

# Exemplo 14: Gerar relatório visual com logs detalhados
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose

# Exemplo 15: Exportar tabela de resultados para CSV
python -m src.main export-results --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Exemplo 16: Exportar todos os assignments de uma turma para CSV
python -m src.main export-results --turma ebape-prog-aplic-barra-2025 --all-assignments

# Exemplo 17: Correção com relatórios visuais
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --with-visual-reports

# Exemplo 18: Correção completa de turma com visuais
python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments --with-visual-reports

# Exemplo 19: Processamento completo de turma
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025

# Exemplo 19b: Processamento completo de apenas um assignment da turma
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog1-tarefa-scrap-simples

# Exemplo 19c: Processamento completo de uma submissão específica
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog1-prova-av --submissao joao-silva

# Exemplo 20: Relatório visual de execução Python
python -m src.main generate-execution-visual-report --assignment prog1-tarefa-scrap-yahoo --turma ebape-prog-aplic-barra-2025

## 🚀 Processamento Completo de Turmas

O sistema oferece funcionalidades avançadas para processamento completo de turmas, combinando correção, relatórios visuais e exportação de dados em uma única operação.

### Comando `correct-all-with-visual`

Este comando executa um processamento completo de turma em 4 etapas:

1. **Correção**: Executa testes e análise de IA para todos os assignments
2. **Relatórios**: Gera relatórios nos formatos solicitados (HTML/Markdown/JSON)
3. **Thumbnails**: Gera relatórios visuais com screenshots (quando aplicável)
4. **Exportação CSV**: Exporta tabela de resultados para análise

### Características

- **Processamento em lote**: Todos os assignments da turma em uma operação
- **Progress tracking**: Barra de progresso com 4 etapas bem definidas
- **Tratamento de erros**: Continua processamento mesmo se um assignment falhar
- **Relatórios consolidados**: Todos os formatos gerados automaticamente
- **Thumbnails automáticos**: Detecta assignments que suportam thumbnails
- **Exportação CSV**: Dados prontos para análise em planilhas/BI
- **Resumo final**: Estatísticas completas do processamento

### Estrutura de Saída

```
reports/
├── assignment1_turma.json          # Relatórios JSON
├── assignment1_turma.html          # Relatórios HTML
├── assignment2_turma.json
├── assignment2_turma.html
├── visual/                         # Relatórios visuais
│   ├── assignment1_turma.html
│   ├── assignment2_turma.html
│   └── thumbnails/                 # Screenshots
└── csv/                           # Exportação CSV
    ├── assignment1_turma_results.csv
    └── assignment2_turma_results.csv
```

## 🖼️ Funcionalidade de Thumbnails e Relatórios Visuais

O sistema inclui funcionalidade avançada para gerar thumbnails de dashboards Streamlit e páginas HTML, além de relatórios visuais da execução de programas Python, permitindo visualização rápida dos trabalhos dos alunos.

### Características

- **Geração automática**: Captura screenshots de cada dashboard Streamlit ou página HTML
- **Processamento paralelo**: Cada submissão roda em porta separada (Streamlit) ou arquivo separado (HTML)
- **Tratamento de erros**: Instala dependências automaticamente se necessário (Streamlit)
- **Relatórios visuais**: Interface HTML organizada por nota
- **Estatísticas**: Taxa de sucesso dos thumbnails gerados
- **Performance otimizada**: Dependências instaladas uma única vez por execução (Streamlit)
- **Captura completa**: Altura mínima de 1800px para dashboards, 1200px para HTML
- **Suporte a alta resolução**: Compatível com telas 2880x1620, 200% escala
- **Logs opcionais**: Flag `--verbose` para debug detalhado
- **Limpeza automática**: Processos órfãos removidos automaticamente (Streamlit)
- **Suporte a HTML estático**: Captura direta de arquivos index.html sem servidor

### Relatórios Visuais de Execução Python

- **Saídas organizadas**: Exibe STDOUT e STDERR de cada execução
- **Status visual**: Indicadores coloridos para sucesso, erro e execução parcial
- **Estatísticas detalhadas**: Tempo de execução, código de retorno, taxa de sucesso
- **Interface responsiva**: Layout adaptável para diferentes tamanhos de tela
- **Formatação preservada**: Mantém formatação original da saída do programa
- **Truncamento inteligente**: Limita saídas muito longas para melhor visualização

### Como Funciona

**Para Streamlit:**
1. **Detecção**: Identifica assignments que usam Streamlit
2. **Inicialização**: Inicia cada dashboard em porta separada
3. **Captura**: Usa Selenium para capturar screenshot
4. **Organização**: Cria relatório visual com thumbnails organizados

**Para HTML:**
1. **Detecção**: Identifica assignments que usam HTML estático
2. **Leitura**: Acessa diretamente o arquivo index.html de cada submissão
3. **Captura**: Usa Selenium para capturar screenshot da página HTML
4. **Organização**: Cria relatório visual com thumbnails organizados

**Para Execução Python:**
1. **Detecção**: Identifica assignments que têm execução Python
2. **Processamento**: Carrega dados de execução das submissões
3. **Formatação**: Organiza saídas STDOUT e STDERR
4. **Visualização**: Cria relatório HTML com cards de execução organizados

### Configurações

```python
# config.py
# Configurações para Streamlit
STREAMLIT_STARTUP_TIMEOUT = 30  # Tempo para inicializar
STREAMLIT_PORT_RANGE = (8501, 8600) # Range de portas

# Configurações para captura de screenshots (Streamlit e HTML)
SCREENSHOT_WAIT_TIME = 3        # Tempo para renderizar
CHROME_WINDOW_SIZE = "1440,900" # Tamanho da janela (otimizado para alta resolução)

# Configuração de assignments que geram thumbnails
ASSIGNMENTS_WITH_THUMBNAILS = {
    "prog1-prova-av": "streamlit",           # Dashboard Streamlit
    "prog1-tarefa-html-curriculo": "html",   # Página HTML
    "prog1-tarefa-html-tutorial": "html",    # Página HTML
}
```

### Dependências Adicionais

O sistema agora inclui dependências otimizadas para thumbnails:

```python
# Pipfile
psutil = "*"    # Gerenciamento de processos órfãos
pillow = "*"    # Manipulação de imagens para captura completa
```

### Solução de Problemas

**Para Streamlit:**
- **Thumbnails em branco**: Aumente `SCREENSHOT_WAIT_TIME`
- **Timeouts**: Aumente `STREAMLIT_STARTUP_TIMEOUT`
- **Erros de dependência**: O sistema tenta instalar automaticamente
- **Conflitos de porta**: Ajuste `STREAMLIT_PORT_RANGE`
- **Thumbnails cortados**: Sistema usa altura mínima de 1800px automaticamente
- **Performance lenta**: Dependências instaladas uma única vez por execução
- **Processos órfãos**: Limpeza automática implementada

**Para HTML:**
- **Thumbnails em branco**: Aumente `SCREENSHOT_WAIT_TIME`
- **Arquivo não encontrado**: Verifique se index.html existe na submissão
- **Thumbnails cortados**: Sistema usa altura mínima de 1200px automaticamente
- **Erros de renderização**: Verifique se o HTML é válido

**Geral:**
- **Telas de alta resolução**: Suporte nativo para 2880x1620, 200% escala
- **Debug detalhado**: Use flag `--verbose` para logs completos

## 📊 Relatórios

### Formatos Disponíveis

- **Console**: Exibição colorida e formatada no terminal
- **HTML**: Relatório interativo com gráficos e navegação
- **Markdown**: Relatório em formato texto estruturado
- **JSON**: Dados estruturados para processamento posterior
- **CSV**: Tabela de resultados para análise em planilhas e BI

### Exportação CSV

O sistema permite exportar a tabela "Resultados por Submissão" em formato CSV para análise em planilhas, ferramentas de BI e outras aplicações.

#### Estrutura do CSV

O arquivo CSV contém as seguintes colunas:

- **assignment_name**: Nome do assignment
- **turma**: Nome da turma
- **submission_identifier**: Login do aluno ou nome do grupo
- **submission_type**: Tipo de submissão (individual/group)
- **test_score**: Nota dos testes (0-10)
- **ai_score**: Nota da análise de IA (0-10)
- **final_score**: Nota final (0-10)
- **status**: Status da submissão (🟢 Excelente, 🟡 Bom, 🟠 Aprovado, 🔴 Reprovado)
- **tests_passed**: Número de testes que passaram
- **tests_total**: Número total de testes
- **generated_at**: Data/hora de geração do relatório

#### Características

- **Notas separadas**: Mostra nota dos testes e nota da IA separadamente
- **Suporte a múltiplos assignments**: Exporta todos os assignments de uma turma
- **Encoding UTF-8**: Suporte completo a caracteres especiais
- **Estatísticas**: Calcula estatísticas de exportação (média, taxa de aprovação, etc.)
- **Tratamento de erros**: Continua exportação mesmo se um assignment falhar
- **HTML**: Relatório interativo com gráficos e navegação
- **Markdown**: Relatório em formato texto estruturado
- **JSON**: Dados estruturados para processamento posterior

### Conversão de Relatórios

Após gerar um relatório JSON com o comando `correct`, você pode convertê-lo para HTML ou Markdown sem precisar rodar a correção novamente:

```bash
# Converter um relatório específico para HTML
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format html

# Converter um relatório específico para Markdown
python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format markdown

# Converter o relatório JSON mais recente para HTML
python -m src.main convert-latest --format html

# Converter o relatório JSON mais recente para Markdown
python -m src.main convert-latest --format markdown
```

Os arquivos convertidos serão salvos no diretório de relatórios (`reports/` por padrão).

### Exemplo de Relatório

```
╭───────────────────────────────────────────────────────────────────────────────────────────────────╮
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
│ Relatório de Correção                                                                             │
│ Assignment: prog1-prova-av                                                                        │
│ Turma: ebape-prog-aplic-barra-2025                                                                │
│ Gerado em: 2025-07-01T10:30:14.095265                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
     📈 Resumo Estatístico      
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Métrica             ┃ Valor  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total de Submissões │ 1      │
│ Nota Média          │ 9.09   │
│ Nota Mínima         │ 9.09   │
│ Nota Máxima         │ 9.09   │
│ Taxa de Aprovação   │ 100.0% │
│ Taxa de Excelência  │ 100.0% │
└─────────────────────┴────────┘
```

## 📝 Prompts Personalizados

### Sistema de Prompts Específicos

O sistema suporta prompts personalizados para cada assignment:

1. **Prompt Personalizado**: Crie um arquivo `prompt.txt` na pasta `prompts/{assignment-name}/`
2. **Template Padrão**: Se não existir prompt personalizado, usa template baseado no tipo (Python/HTML)
3. **Leitura Automática**: Lê README.md e estrutura de arquivos do enunciado
4. **Versionamento**: Os prompts ficam na pasta `prompts/` (versionada) separada dos enunciados

### Instruções Especiais para Scraping

O sistema inclui **instruções específicas para assignments de scraping** que garantem que o LLM avalie apenas o **resultado final**, nunca o método usado:

- **Proíbe avaliação de seletores CSS** baseada no conhecimento do LLM sobre páginas
- **Foca apenas em**: código roda? extrai dados? formato correto? passa testes?
- **Aplica automaticamente** a todos os assignments de scraping
- **Garante avaliações justas** independente do método de implementação

Para mais detalhes, consulte [Solução para Avaliação de Scraping](docs/solucao-scraping-llm.md).

### Exemplo de Prompt Personalizado

```txt
# prompts/prog1-prova-av/prompt.txt
Analise o código Python abaixo para o assignment "{assignment_name}".

DESCRIÇÃO DO ASSIGNMENT:
{assignment_description}

REQUISITOS ESPECÍFICOS:
{assignment_requirements}

CÓDIGO DO ALUNO:
{student_code}

INSTRUÇÕES DE AVALIAÇÃO ESPECÍFICAS PARA ESTE ASSIGNMENT:

Este é um assignment de Web Scraping + Streamlit Dashboard. Avalie considerando:

1. **Funcionamento do Scraping (40% do peso)**:
   - A função `fetch_page()` deve fazer requisições HTTP corretas
   - A função `parse_data()` deve extrair dados da página HTML
   - A função `generate_csv()` deve gerar o arquivo CSV corretamente

2. **Dashboard Streamlit (50% do peso)**:
   - Deve ter título personalizado do projeto
   - Deve ter 3 filtros na sidebar
   - Deve exibir tabela de dados
   - Deve ter 2 gráficos interativos relevantes

3. **Escolha dos Filtros e Gráficos (10% do peso)**:
   - Os filtros devem fazer sentido para os dados
   - Os gráficos devem ser apropriados e informativos

Formate sua resposta assim:
NOTA: [número de 0 a 10]
COMENTARIOS: [lista de comentários sobre pontos positivos]
SUGESTOES: [lista de sugestões de melhoria]
PROBLEMAS: [lista de problemas encontrados]
```

### Variáveis Disponíveis no Prompt

- `{assignment_name}` - Nome do assignment
- `{assignment_description}` - Descrição do assignment
- `{assignment_requirements}` - Lista de requisitos
- `{student_code}` - Código do aluno formatado

## 📝 Sistema de Logs de Auditoria

### Características

- **Logs automáticos**: Todas as análises da IA são salvas automaticamente
- **Estrutura organizada**: `logs/YYYY-MM-DD/assignment-name/submission_analysis_timestamp.json`
- **Dados completos**: Prompt enviado, resposta raw da IA e resultado processado
- **Auditoria completa**: Permite revisar como a IA chegou às suas avaliações
- **Não versionados**: Os logs ficam na pasta `logs/` (ignorada pelo git)

### Estrutura dos Logs

```json
{
  "metadata": {
    "assignment_name": "prog1-prova-av",
    "submission_identifier": "joao-silva",
    "analysis_type": "python",
    "timestamp": "2025-01-15T10:30:14.095265",
    "ai_model": "gpt-3.5-turbo"
  },
  "prompt": "Analise o código Python abaixo...",
  "raw_response": "NOTA: 8.5\nCOMENTARIOS: ...",
  "parsed_result": {
    "score": 8.5,
    "comments": ["Código bem estruturado"],
    "suggestions": ["Adicionar mais comentários"],
    "issues_found": ["Falta tratamento de erro"]
  }
}
```

### Localização dos Logs

```
logs/
├── 2025-01-15/
│   ├── prog1-prova-av/
│   │   ├── joao-silva_python_10-30-14.json
│   │   ├── maria-santos_python_10-35-22.json
│   │   └── grupo-abc_python_10-40-15.json
│   └── prog1-tarefa-html-curriculo/
│       ├── ana-clara_html_11-15-30.json
│       └── ...
└── 2025-01-16/
    └── ...
```

## 🧪 Execução de Testes

### Características

- **Execução direta**: Testes rodam na pasta do aluno (sem cópia)
- **Resultados detalhados**: Status, tempo de execução e mensagens de erro
- **Suporte a pytest**: Usa pytest-json-report para resultados estruturados
- **Múltiplos arquivos**: Suporta múltiplos arquivos de teste por assignment

### Exemplo de Resultado

```
🧪 Resultados dos Testes:
✅ test_fetch_page_function_signature (0.123s)
✅ test_generate_csv_function_existence (0.045s)
❌ test_parse_data_function_signature (0.234s)
   Erro: SystemExit: 1
```

## 📚 Documentação Técnica

### Sistema de Cálculo de Notas

Para entender como o sistema calcula as notas finais dos alunos, consulte:
- **[Sistema de Cálculo de Notas](doc/sistema-notas.md)** - Explicação detalhada das fórmulas e ponderações

### Outros Documentos

- **[Contexto do Projeto](contexto.md)** - Decisões de design e padrões estabelecidos

## 🔧 Configuração Avançada

### Estrutura de Enunciados

```
enunciados/
├── assignment-nome/
│   ├── README.md          # Descrição e requisitos
│   ├── prompt.txt         # Prompt personalizado (opcional)
│   ├── arquivo-base.py    # Código fornecido ao aluno
│   ├── tests/             # Testes da atividade
│   └── dados/             # Dados de exemplo
```

### Estrutura de Respostas

```
respostas/
├── turma-nome/
│   ├── assignment1-submissions/
│   │   ├── assignment1-aluno1/          # Submissão individual
│   │   │   ├── main.py
│   │   │   └── ...
│   │   ├── assignment1-grupo-abc/       # Submissão em grupo
│   │   │   ├── main.py
│   │   │   └── ...
│   │   └── assignment1-outro-aluno/
│   └── assignment2-submissions/
```

### Tipos de Submissão

O sistema suporta dois tipos de submissão:

1. **Submissões Individuais**: 
   - Padrão: `{assignment-name}-{login-do-aluno}`
   - Exemplo: `prog1-prova-av-joaosilva`

2. **Submissões em Grupo**:
   - Padrão: `{assignment-name}-{nome-do-grupo}`
   - Exemplo: `prog1-prova-av-ana-clara-e-isabella`

O tipo de submissão é configurado por assignment no arquivo `config.py`:

```python
ASSIGNMENT_SUBMISSION_TYPES = {
    "prog1-tarefa-html-curriculo": SubmissionType.INDIVIDUAL,
    "prog1-prova-av": SubmissionType.GROUP,
    # ...
}
```

## 🧪 Testes

### Execução de Testes

O projeto usa pytest para testes automatizados. Os testes estão organizados em diferentes categorias para permitir execução seletiva:

#### Testes Básicos (Execução Padrão)

```bash
# Executa todos os testes básicos (exclui testes de integração e thumbnails)
pipenv run pytest tests/ -m "not integration and not thumbnails and not slow"

# Ou simplesmente (padrão)
pipenv run pytest tests/
```

#### Testes de Integração

```bash
# Executa apenas testes de integração
pipenv run pytest tests/ -m integration

# Executa todos os testes EXCETO os de integração
pipenv run pytest tests/ -m "not integration"
```

#### Testes de Thumbnails

```bash
# Executa apenas testes relacionados a thumbnails
pipenv run pytest tests/ -m thumbnails

# Executa todos os testes EXCETO os de thumbnails
pipenv run pytest tests/ -m "not thumbnails"
```

#### Testes Lentos

```bash
# Executa apenas testes marcados como lentos
pipenv run pytest tests/ -m slow

# Executa todos os testes EXCETO os lentos
pipenv run pytest tests/ -m "not slow"
```

#### Combinações

```bash
# Executa testes de integração E thumbnails
pipenv run pytest tests/ -m "integration and thumbnails"

# Executa testes que são de integração OU thumbnails
pipenv run pytest tests/ -m "integration or thumbnails"

# Executa todos os testes exceto os lentos
pipenv run pytest tests/ -m "not slow"
```

### Categorias de Testes

- **`integration`**: Testes que executam integração completa do sistema (incluem geração de thumbnails)
- **`thumbnails`**: Testes relacionados à funcionalidade de thumbnails Streamlit
- **`slow`**: Testes que são mais lentos (geralmente incluem processos externos como Chrome/Selenium)

### Por que Testes Opcionais?

Alguns testes são marcados como opcionais porque:

1. **Testes de Integração**: Executam o sistema completo, incluindo geração de thumbnails que requer Chrome/Selenium
2. **Testes de Thumbnails**: Requerem ambiente com Chrome/Chromium instalado
3. **Testes Lentos**: Podem levar mais tempo devido a processos externos

Para desenvolvimento rápido, execute apenas os testes básicos. Para validação completa, execute todos os testes.

## 🤝 Contribuição

### Padrões de Commit

O projeto segue a convenção [Conventional Commits](https://www.conventionalcommits.org/) com adaptações para português. Para garantir consistência, o projeto inclui:

- **Template de commit** (`.gitmessage`) - Guia visual para mensagens
- **Hook de validação** (`.git/hooks/commit-msg`) - Validação automática
- **Documentação completa** (`docs/commit-standards.md`) - Padrões detalhados

#### Configuração Inicial
```bash
# Execute uma vez para configurar o ambiente
./setup-commit-hooks.sh
```

#### Exemplos de Commits Válidos
```bash
feat(ai): adiciona parsing robusto para elementos HTML
fix(tests): corrige timeout em execução de testes
docs: atualiza README com exemplos de uso
refactor(services): reorganiza AIAnalyzer para melhor separação
```

Para mais detalhes, consulte [Padrões de Commit](docs/commit-standards.md).

### Processo de Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças seguindo os padrões estabelecidos
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Jefferson Santos**
- GitHub: [@jeffersonsantos](https://github.com/jeffersonsantos)
- Email: jefferson.santos@fgv.br

## 🙏 Agradecimentos

- OpenAI pela API GPT
- pytest pela framework de testes
- Comunidade Python pelos recursos utilizados 