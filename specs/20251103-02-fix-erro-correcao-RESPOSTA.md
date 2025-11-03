# Resposta à Spec 20251103-02: Corrigir erro ao executar a correção automática

## Análise do Problema

Durante a execução do comando completo de correção para a atividade `prog2-as`, o sistema estava gerando erros consistentes para todas as submissões:

```
Processando submissão de Brenoall (individual)...
  ⚠️  Erro na análise de IA para Brenoall (individual): 'cityName'
Processando submissão de deresaw2010 (individual)...
  ⚠️  Erro na análise de IA para deresaw2010 (individual): 'cityName'
```

### Causa Raiz Identificada

O erro `KeyError: 'cityName'` ocorria no `PromptManager` ao processar o prompt personalizado do `prog2-as`.

**Raiz do problema:**
- O prompt continha exemplos de endpoints da API CPTEC com placeholders: `{cityName}` e `{cityCode}`
- Esses exemplos eram usados para documentar a API de previsão do tempo
- O método `_format_custom_prompt()` usava `.format()` para substituir placeholders
- O `.format()` tentava substituir **todas** as chaves `{...}`, incluindo os exemplos da API
- Como `cityName` e `cityCode` não eram variáveis fornecidas ao `.format()`, ocorria `KeyError`

**Placeholders legítimos do sistema:**
- `{assignment_name}`
- `{assignment_description}`
- `{assignment_requirements}`
- `{enunciado_code}`
- `{student_code}`

**Placeholders problemáticos (exemplos de API no prompt):**
- `{cityName}` - exemplo de endpoint da API
- `{cityCode}` - exemplo de endpoint da API

## Solução Implementada

### Abordagem Técnica

Implementação de escape seletivo de chaves no template do prompt **antes** da formatação com `.format()`.

**Estratégia:**
1. Identificar todos os placeholders no template usando regex
2. Verificar se cada placeholder pertence à lista de placeholders conhecidos
3. Escapar apenas placeholders desconhecidos (duplicando as chaves: `{x}` → `{{x}}`)
4. Preservar placeholders conhecidos para substituição pelo `.format()`

### Código Implementado

**Novo método adicionado:**

```python
def _escape_non_placeholder_braces(self, template: str) -> str:
    """Escapa chaves no template que não são placeholders conhecidos."""
    # Lista de placeholders conhecidos que devem ser preservados
    known_placeholders = [
        'assignment_name',
        'assignment_description',
        'assignment_requirements',
        'enunciado_code',
        'student_code'
    ]

    # Padrão para encontrar todas as ocorrências de {algo}
    pattern = r'\{([^}]+)\}'

    def replace_brace(match):
        """Substitui a chave por chave escapada se não for placeholder conhecido."""
        placeholder_name = match.group(1)
        if placeholder_name in known_placeholders:
            # Preserva placeholders conhecidos
            return match.group(0)
        else:
            # Escapa placeholders desconhecidos (duplica as chaves)
            return '{{' + placeholder_name + '}}'

    # Substitui todas as ocorrências
    return re.sub(pattern, replace_brace, template)
```

**Modificação no `_format_custom_prompt()`:**

```python
def _format_custom_prompt(self, prompt_template: str, ...):
    # ... código existente ...

    # Escapa chaves no template que não são placeholders conhecidos
    escaped_template = self._escape_non_placeholder_braces(prompt_template)

    # Agora usa o template com escape seletivo
    formatted_prompt = escaped_template.format(
        assignment_name=assignment.name,
        assignment_description=assignment.description,
        # ... outros placeholders ...
    )
```

### Arquivos Modificados

**Commit:** 1b740a13c3c7d794c2a3b4cee3e5fc83c49ab255

| Arquivo | Linhas | Modificações |
|---------|--------|--------------|
| `src/services/prompt_manager.py` | 2 | Adiciona `import re` |
| `src/services/prompt_manager.py` | 224-250 | Adiciona método `_escape_non_placeholder_braces()` (27 linhas) |
| `src/services/prompt_manager.py` | 256-260 | Modifica `_format_custom_prompt()` para usar escape seletivo (5 linhas) |
| `specs/20251103-02-fix-erro-correcao.md` | - | Criação da spec original |

**Total:** +35 linhas adicionadas, -2 linhas modificadas

### Decisões Técnicas

1. **Uso de Regex para identificação de placeholders**
   - Pattern `r'\{([^}]+)\}'` captura qualquer `{conteúdo}`
   - Abordagem robusta que funciona com qualquer placeholder

2. **Lista explícita de placeholders conhecidos**
   - Mantém clareza sobre quais são os placeholders legítimos do sistema
   - Facilita manutenção futura (adicionar novos placeholders conhecidos)
   - Previne erros se novos placeholders forem adicionados

3. **Escape via duplicação de chaves**
   - `{cityName}` → `{{cityName}}`
   - Método padrão do Python para escapar chaves em strings com `.format()`
   - Após `.format()`, `{{cityName}}` volta a ser `{cityName}` no resultado

4. **Processamento antes do `.format()`**
   - Garante que placeholders desconhecidos não causem KeyError
   - Permite que código de exemplo com chaves seja incluído em prompts
   - Mantém retrocompatibilidade com prompts existentes

## Resultados e Validações

✅ **Erro corrigido**
- Nenhum `KeyError` mais ocorre durante correção do prog2-as
- Sistema processa todas as submissões sem erros

✅ **Exemplos de API preservados nos prompts**
- `{cityName}` e `{cityCode}` aparecem corretamente no prompt final
- Documentação da API CPTEC permanece legível para o modelo

✅ **Placeholders do sistema funcionando**
- `{assignment_name}`, `{student_code}`, etc. continuam sendo substituídos
- Sistema de prompts personalizados totalmente funcional

✅ **Solução genérica e robusta**
- Funciona para qualquer prompt com exemplos de API ou código
- Não quebra prompts existentes
- Permite adicionar novos placeholders facilmente

## Teste de Validação

Após a implementação, o comando completo executa sem erros:

```bash
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog2-as --verbose
```

**Resultado:** Todas as submissões processadas com sucesso, análise de IA funcionando corretamente.
