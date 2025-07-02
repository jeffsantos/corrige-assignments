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
- 🖼️ **Geração automática de thumbnails** - Screenshots de dashboards Streamlit
- 📈 **Relatórios visuais** - Interface HTML com thumbnails organizados por nota

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
CHROME_WINDOW_SIZE = "1200,800"  # tamanho da janela do Chrome
STREAMLIT_PORT_RANGE = (8501, 8600)  # range de portas para Streamlit
```

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

# Especificar formato de saída
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-format html

# Especificar diretório de saída
python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-dir meus-relatorios
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

### Comandos de Thumbnails Streamlit

```bash
# Gerar apenas thumbnails (sem correção)
python -m src.main generate-thumbnails-only --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Gerar relatório visual completo (correção + thumbnails)
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Especificar diretório de saída para relatórios visuais
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --output-dir reports/visual
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

# Exemplo 12: Gerar apenas thumbnails de dashboards
python -m src.main generate-thumbnails-only --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025

# Exemplo 13: Gerar relatório visual completo
python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025
```

## 🖼️ Funcionalidade de Thumbnails Streamlit

O sistema inclui funcionalidade avançada para gerar thumbnails de dashboards Streamlit, permitindo visualização rápida dos trabalhos dos alunos.

### Características

- **Geração automática**: Captura screenshots de cada dashboard Streamlit
- **Processamento paralelo**: Cada submissão roda em porta separada
- **Tratamento de erros**: Instala dependências automaticamente se necessário
- **Relatórios visuais**: Interface HTML organizada por nota
- **Estatísticas**: Taxa de sucesso dos thumbnails gerados

### Como Funciona

1. **Detecção**: Identifica assignments que usam Streamlit
2. **Inicialização**: Inicia cada dashboard em porta separada
3. **Captura**: Usa Selenium para capturar screenshot
4. **Organização**: Cria relatório visual com thumbnails organizados

### Configurações

```python
# config.py
STREAMLIT_STARTUP_TIMEOUT = 30  # Tempo para inicializar
SCREENSHOT_WAIT_TIME = 3        # Tempo para renderizar
CHROME_WINDOW_SIZE = "1200,800" # Tamanho da janela
STREAMLIT_PORT_RANGE = (8501, 8600) # Range de portas
```

### Solução de Problemas

- **Thumbnails em branco**: Aumente `SCREENSHOT_WAIT_TIME`
- **Timeouts**: Aumente `STREAMLIT_STARTUP_TIMEOUT`
- **Erros de dependência**: O sistema tenta instalar automaticamente
- **Conflitos de porta**: Ajuste `STREAMLIT_PORT_RANGE`

## 📊 Relatórios

### Formatos Disponíveis

- **Console**: Exibição colorida e formatada no terminal
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

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
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