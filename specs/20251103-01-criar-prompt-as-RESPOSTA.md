# Resposta à Spec 20251103-01: Criar prompt.txt para atividade da AS

## Análise e Implementação

Esta spec solicitou a criação de um prompt especializado para a atividade `prog2-as` (prova substitutiva), baseando-se no prompt já existente para `prog2-prova`.

### Contexto da Atividade

A atividade `prog2-as` é uma variação da prova regular (`prog2-prova`) com as seguintes diferenças principais:

| Aspecto | prog2-prova | prog2-as |
|---------|------------|----------|
| **API utilizada** | Brasil API - Câmbio (cotações de moedas) | Brasil API - CPTEC (previsão do tempo) |
| **Tabela obrigatória** | Não especificada | Cidades (com campo VARCHAR obrigatório) |
| **App Terminal** | Busca cotação de moedas | Busca previsão do tempo para cidade |
| **Dashboard** | Adiciona coluna com cotações usando .apply() | Adiciona coluna com previsão usando .apply() |
| **Campo exibido** | Valores de cotação | `condicao_desc` da previsão |

### Decisões Técnicas

1. **Baseado no prompt existente de prog2-prova**
   - Mantém estrutura e formatação consistentes
   - Preserva critérios de avaliação e pontuação
   - Adapta contexto específico para previsão do tempo

2. **Adaptações específicas para API CPTEC**
   - Requisito obrigatório: tabela Cidades com campo VARCHAR
   - Endpoints específicos da API de previsão do tempo
   - Exemplos de uso com {cityName} e {cityCode}
   - Campo condicao_desc como saída esperada

3. **Commits obrigatórios atualizados**
   - Adaptados do contexto de câmbio para previsão do tempo
   - Mensagens refletem implementação de API CPTEC
   - Mantém estrutura em 3 partes (PROVA_PARTE1, PARTE2, PARTE3)

4. **Critérios de avaliação**
   - Mesma estrutura de pontuação do prog2-prova
   - Adaptados para verificar integração com API de previsão
   - Ênfase na tabela Cidades e uso correto de .apply()

### Arquivos Criados/Modificados

**Commit:** c1200ab0a6a13f4771d8cc1ad83fcb236fdc19d8

| Arquivo | Modificações | Descrição |
|---------|-------------|-----------|
| `prompts/prog2-as/prompt.txt` | +109 linhas (novo) | Prompt especializado para avaliação do prog2-as |
| `specs/20251103-01-criar-prompt-as.md` | +7 linhas (novo) | A própria spec |
| `CLAUDE.md` | +1 linha | Adiciona regra de commit da spec após implementação |

### Resultados e Validações

✅ **Prompt criado com sucesso**
- Arquivo `prompts/prog2-as/prompt.txt` criado com 109 linhas
- Estrutura consistente com outros prompts do sistema
- Adaptações específicas para API CPTEC implementadas

✅ **Consistência com prog2-prova mantida**
- Mesma estrutura de avaliação e pontuação
- Formatação e delimitadores padronizados
- Critérios adaptados ao novo contexto

✅ **Requisitos específicos documentados**
- Tabela Cidades como obrigatória
- Campo VARCHAR destacado nos requisitos
- Uso de .apply() para integração com API
- Exibição do campo condicao_desc especificado

✅ **Workflow de specs atualizado**
- CLAUDE.md atualizado com regra de commit após implementação
- Estabelece padrão para futuras specs

### Conteúdo Principal do Prompt

O prompt criado inclui:

1. **Contexto da atividade** - Descrição da prova substitutiva prog2-as
2. **Estrutura da prova** - 3 partes (PROVA_PARTE1, PARTE2, PARTE3)
3. **Requisitos técnicos** - Tabela Cidades, API CPTEC, campo VARCHAR
4. **Commits obrigatórios** - Mensagens esperadas adaptadas para previsão do tempo
5. **Critérios de avaliação** - Pontuação detalhada por requisito
6. **Exemplos de integração** - Uso correto de .apply() e API
7. **Campos esperados** - Foco em condicao_desc da previsão

O prompt está pronto para uso no sistema de correção automática e garantirá avaliações consistentes para as submissões do prog2-as.
