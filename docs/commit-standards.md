# Padrões de Commit - Sistema de Correção Automática

Este documento descreve os padrões de commit estabelecidos para o projeto, incluindo o template e hooks de validação.

## 🎯 **Conventional Commits**

O projeto segue a convenção [Conventional Commits](https://www.conventionalcommits.org/) com adaptações para português.

### **Formato Básico**
```bash
tipo(escopo): descrição

[corpo opcional]

[rodapé opcional]
```

### **Tipos Válidos**
- **`feat`**: Nova funcionalidade
- **`fix`**: Correção de bug
- **`docs`**: Mudanças na documentação
- **`style`**: Mudanças que não afetam o código (formatação, espaços, etc.)
- **`refactor`**: Refatoração de código (não adiciona funcionalidade nem corrige bug)
- **`test`**: Adição ou correção de testes
- **`chore`**: Mudanças em arquivos de build, config, etc.

### **Escopos Comuns**
- **`ai`**: Mudanças relacionadas à análise por IA
- **`cli`**: Mudanças na interface de linha de comando
- **`config`**: Mudanças em configurações
- **`models`**: Mudanças nos modelos de domínio
- **`tests`**: Mudanças nos testes
- **`docs`**: Mudanças na documentação
- **`prompts`**: Mudanças nos prompts personalizados
- **`services`**: Mudanças nos serviços
- **`utils`**: Mudanças nos utilitários

### **Regras Importantes**
1. **Descrição em português**
2. **Máximo 50 caracteres** na descrição
3. **Use imperativo**: "adiciona", "corrige", "remove", "atualiza"
4. **Escopo opcional**, mas recomendado para identificar área

## 📝 **Exemplos**

### **Commits Simples**
```bash
feat(ai): adiciona parsing robusto para elementos HTML
fix(tests): corrige timeout em execução de testes
docs: atualiza README com exemplos de uso
refactor(services): reorganiza AIAnalyzer para melhor separação
test(models): adiciona testes para serialização de relatórios
chore(config): adiciona configuração para novo assignment HTML
```

### **Commits com Corpo**
```bash
feat(ai): adiciona suporte a prompts personalizados por assignment

Permite que cada assignment tenha seu próprio prompt.txt na pasta prompts/.
O sistema carrega automaticamente o prompt personalizado ou usa o template padrão.

- Adiciona PromptManager para gerenciar prompts
- Implementa carregamento de prompts personalizados
- Mantém compatibilidade com prompts padrão
```

### **Breaking Changes**
```bash
feat(ai): adiciona configuração de temperatura da API OpenAI

BREAKING CHANGE: AIAnalyzer agora requer configuração explícita de temperatura

Closes #123
```

## 🔧 **Configuração do Ambiente**

### **1. Template de Commit**
O projeto inclui um template que aparece automaticamente quando você faz `git commit`:

```bash
# Configurar template (já configurado no projeto)
git config --local commit.template .gitmessage
```

### **2. Hook de Validação**
O projeto inclui um hook que valida automaticamente as mensagens de commit:

```bash
# Tornar hook executável (execute o script setup-commit-hooks.sh)
chmod +x .git/hooks/commit-msg
```

### **3. Script de Configuração**
Execute o script de configuração uma vez:

```bash
./setup-commit-hooks.sh
```

## 🚨 **Validações Automáticas**

O hook verifica automaticamente:

### **✅ Validações Obrigatórias**
- Formato Conventional Commits
- Tipo válido (feat, fix, docs, etc.)
- Descrição não vazia
- Máximo 50 caracteres na descrição

### **⚠️ Avisos**
- Escopo não está na lista de escopos comuns
- Descrição parece estar em inglês
- Segunda linha não está em branco (para commits com corpo)

### **❌ Erros (Bloqueiam o Commit)**
- Formato inválido
- Tipo inválido
- Descrição muito longa
- Mensagem vazia

## 🧪 **Testando os Hooks**

### **Teste de Mensagem Válida**
```bash
git commit -m "feat(ai): adiciona nova funcionalidade"
# ✅ Deve passar
```

### **Teste de Mensagem Inválida**
```bash
git commit -m "mensagem invalida"
# ❌ Deve falhar com erro explicativo
```

### **Teste de Tipo Inválido**
```bash
git commit -m "invalid(ai): adiciona funcionalidade"
# ❌ Deve falhar - tipo 'invalid' não é válido
```

### **Teste de Descrição Longa**
```bash
git commit -m "feat(ai): adiciona funcionalidade muito longa que excede cinquenta caracteres"
# ❌ Deve falhar - mais de 50 caracteres
```

## 📋 **Checklist para Commits**

Antes de fazer commit, verifique:

- [ ] Tipo correto (feat, fix, docs, etc.)
- [ ] Escopo apropriado (se aplicável)
- [ ] Descrição em português
- [ ] Máximo 50 caracteres
- [ ] Formato imperativo
- [ ] Corpo do commit (se necessário)
- [ ] Breaking changes documentados (se aplicável)

## 🔄 **Integração com Ferramentas**

### **Semantic Versioning**
Commits `feat` e `fix` geram novas versões automaticamente.

### **Changelog**
Geração automática de changelog baseado nos tipos de commit.

### **CI/CD**
Análise automática de tipos de commit para pipelines.

---

**Última atualização**: Janeiro 2025  
**Versão**: 1.0.0  
**Mantenedor**: Jefferson Santos (jefferson.santos@fgv.br) 