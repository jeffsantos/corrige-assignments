# Sistema de Correção Automática de Assignments

Sistema inteligente para correção automática de assignments de programação usando IA (OpenAI GPT) e execução de testes automatizados.

## Funcionalidades

- Análise de IA específica por assignment com prompts personalizados
- Execução de testes automatizados com pytest
- Relatórios em múltiplos formatos (Console, HTML, Markdown, JSON, CSV)
- Suporte a submissões individuais e em grupo
- Geração automática de thumbnails para dashboards Streamlit e páginas HTML
- Relatórios visuais organizados por nota
- Logs de auditoria completos da IA
- Performance otimizada com limpeza automática de processos

## Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/jeffersonsantos/corrige-assignments.git
cd corrige-assignments

# Instale as dependências
pipenv install

# Ative o ambiente virtual
pipenv shell

# Configure a API OpenAI
export OPENAI_API_KEY="sua-chave-aqui"
```

## Uso Básico

### Comando Principal

**Processamento completo de uma turma:**

```bash
python -m src.main correct-all-with-visual --turma <turma-name>
```

Este comando executa:
1. Testes e análise de IA para todos os assignments
2. Geração de relatórios em todos os formatos
3. Criação de thumbnails visuais
4. Exportação para CSV

### Outros Comandos Úteis

```bash
# Correção básica
python -m src.main correct --assignment <assignment-name> --turma <turma-name>

# Listar assignments disponíveis
python -m src.main list-assignments

# Com logs detalhados
python -m src.main correct-all-with-visual --turma <turma-name> --verbose
```

## Documentação

### Para Usuários

- **[Guia de Uso](docs/guia-de-uso.md)** - Todos os comandos e exemplos detalhados
- **[Guia de Configuração](docs/configuracao.md)** - Configurações e personalização do sistema

### Para Desenvolvedores

- **[CLAUDE.md](CLAUDE.md)** - Guia para desenvolvimento com Claude Code
- **[Arquitetura](docs/arquitetura.md)** - Detalhes técnicos da implementação
- **[Sistema de Notas](docs/sistema-notas.md)** - Fórmulas e cálculo de notas
- **[Solução para Scraping](docs/solucao-scraping-llm.md)** - Avaliação de assignments de scraping
- **[Padrões de Commit](docs/commit-standards.md)** - Convenções de mensagens de commit

## Estrutura do Projeto

```
corrige-assignments/
├── docs/              # Documentação completa
├── specs/             # Especificações de implementações
├── src/               # Código fonte
│   ├── domain/        # Modelos de domínio
│   ├── repositories/  # Acesso a dados
│   ├── services/      # Lógica de aplicação
│   ├── utils/         # Utilitários
│   └── main.py        # Ponto de entrada CLI
├── prompts/           # Prompts personalizados por assignment
├── enunciados/        # Enunciados (não versionados)
├── respostas/         # Submissões (não versionadas)
├── reports/           # Relatórios gerados (não versionados)
└── logs/              # Logs de auditoria (não versionados)
```

## Pré-requisitos

- Python 3.8+
- pipenv
- OpenAI API key (para análise de IA)
- Chrome/Chromium (para geração de thumbnails)

## Exemplos de Uso

Veja `example_usage.py` para exemplos detalhados de todos os comandos.

```bash
python example_usage.py
```

## Contribuição

Este projeto segue a convenção [Conventional Commits](https://www.conventionalcommits.org/).

```bash
# Configure o ambiente
./setup-commit-hooks.sh

# Exemplos de commits
feat(ai): adiciona parsing robusto para elementos HTML
fix(tests): corrige timeout em execução de testes
docs: atualiza guia de uso com novos comandos
```

Consulte [Padrões de Commit](docs/commit-standards.md) para mais detalhes.

## Licença

MIT License - Veja o arquivo `LICENSE` para mais detalhes.

## Autor

**Jefferson Santos**
- GitHub: [@jeffersonsantos](https://github.com/jeffersonsantos)
- Email: jefferson.santos@fgv.br

## Agradecimentos

- OpenAI pela API GPT
- pytest pela framework de testes
- Comunidade Python pelos recursos utilizados
