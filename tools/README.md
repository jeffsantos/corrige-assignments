# Tools

Esta pasta contém ferramentas auxiliares para o projeto de correção automática.

## generate_mermaid_uml.py

Script para gerar diagramas UML da arquitetura do projeto em formato Markdown com Mermaid embutido.

### Como usar:

```bash
# Gerar diagrama com nome padrão (diagrama_uml.md)
python tools/generate_mermaid_uml.py

# Gerar diagrama com nome personalizado
python tools/generate_mermaid_uml.py meu_diagrama.md
```

### Saída:

O script gera um arquivo Markdown (.md) que contém:
- **Título e timestamp** de geração
- **Estatísticas** do projeto (total de classes, módulos)
- **Diagrama UML** em formato Mermaid
- **Tabela organizada** por módulos
- **Detalhes dos relacionamentos** (herança e composição)
- **Instruções de visualização**

### Visualização:

O arquivo Markdown gerado pode ser visualizado em:
- **GitHub**: Renderização automática do Mermaid
- **VS Code**: Use a extensão "Markdown Preview Mermaid Support"
- **Online**: Cole o conteúdo do bloco Mermaid em https://mermaid.live/

### O que o script faz:

1. Faz parse de todos os arquivos Python em `src/`
2. Identifica classes, heranças e composições
3. Gera um arquivo Markdown completo com diagrama Mermaid
4. Organiza informações por módulo e relacionamentos
5. Inclui estatísticas e documentação

### Dependências:

- Apenas bibliotecas padrão do Python (`ast`, `pathlib`, etc.)
- Não requer instalação de dependências externas

### Exemplo de uso:

```bash
# Gerar diagrama
python tools/generate_mermaid_uml.py

# Abrir no navegador (se disponível)
start diagrama_uml.md
``` 