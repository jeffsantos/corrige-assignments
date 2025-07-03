# Sistema de Cálculo de Notas

Este documento explica como o sistema calcula a nota final dos alunos/grupos, combinando resultados de testes automatizados e análise de IA.

## 📋 Visão Geral

O sistema utiliza uma abordagem híbrida que combina:
- **Testes automatizados** (critérios objetivos)
- **Análise de IA** (critérios subjetivos e qualitativos)

A ponderação varia conforme o tipo de assignment (Python vs HTML).

## 🔄 Fluxo de Cálculo

### Métodos Envolvidos

1. **`CorrectionService._process_submission()`** - Orquestra o processo completo
2. **`CorrectionService._calculate_final_score()`** - Determina o método de cálculo
3. **`CorrectionService._calculate_python_score()`** - Calcula nota para assignments Python
4. **`CorrectionService._calculate_html_score()`** - Calcula nota para assignments HTML

### Sequência de Execução

```python
# 1. Executa testes (se aplicável)
if assignment.type == AssignmentType.PYTHON and assignment.test_files:
    submission.test_results = self.test_executor.run_tests(...)

# 2. Analisa código com IA
if assignment.type == AssignmentType.PYTHON:
    submission.code_analysis = self.ai_analyzer.analyze_python_code(...)
else:  # HTML
    submission.html_analysis = self.ai_analyzer.analyze_html_code(...)

# 3. Calcula nota final
submission.final_score = self._calculate_final_score(submission, assignment)
```

## 🧮 Fórmulas de Cálculo

### Assignments Python

**Fórmula:**
```
Nota Final = (Nota dos Testes × 0.4) + (Nota da IA × 0.6)
```

**Detalhamento:**

#### 1. Nota dos Testes (40% do peso)
```python
test_score = 0.0
if submission.test_results:
    passed_tests = sum(1 for test in submission.test_results 
                      if test.result == AssignmentTestResult.PASSED)
    total_tests = len(submission.test_results)
    if total_tests > 0:
        test_score = (passed_tests / total_tests) * 10.0
```

- Calcula a porcentagem de testes que passaram
- Converte para escala de 0-10
- Exemplo: 8/10 testes passaram = 8.0 pontos

#### 2. Nota da IA (60% do peso)
```python
ai_score = 0.0
if submission.code_analysis:
    ai_score = submission.code_analysis.score
```

- Nota direta retornada pela IA (0-10)
- Baseada na análise qualitativa do código
- Considera estrutura, legibilidade, boas práticas, etc.

#### 3. Ponderação Final
```python
final_score = (test_score * 0.4) + (ai_score * 0.6)
return min(10.0, max(0.0, final_score))
```

### Assignments HTML

**Fórmula:**
```
Nota Final = Nota da IA (100%)
```

**Detalhamento:**
```python
def _calculate_html_score(self, submission: Submission, assignment: Assignment) -> float:
    if submission.html_analysis:
        return submission.html_analysis.score
    return 0.0
```

- Usa apenas a análise de IA
- Não há testes automatizados para HTML
- Avalia elementos HTML, CSS, estrutura, etc.

## 📊 Exemplos Práticos

### Exemplo 1: Assignment Python

**Cenário:**
- **Testes**: 7/10 passaram (7.0 pontos)
- **IA**: 8.5/10 pontos

**Cálculo:**
```
Nota Final = (7.0 × 0.4) + (8.5 × 0.6)
Nota Final = 2.8 + 5.1
Nota Final = 7.9
```

### Exemplo 2: Assignment Python (Todos os testes passaram)

**Cenário:**
- **Testes**: 10/10 passaram (10.0 pontos)
- **IA**: 7.0/10 pontos

**Cálculo:**
```
Nota Final = (10.0 × 0.4) + (7.0 × 0.6)
Nota Final = 4.0 + 4.2
Nota Final = 8.2
```

### Exemplo 3: Assignment HTML

**Cenário:**
- **IA**: 9.0/10 pontos

**Cálculo:**
```
Nota Final = 9.0 (100% da nota da IA)
```

## 🎯 Justificativa da Ponderação

### Por que 40% Testes + 60% IA?

1. **Testes (40%)**: Critérios objetivos e mensuráveis
   - Funcionalidade básica
   - Conformidade com especificações
   - Execução correta do código

2. **IA (60%)**: Critérios qualitativos e educacionais
   - Qualidade do código
   - Boas práticas
   - Estrutura e organização
   - Criatividade e escolhas de design

### Vantagens desta Abordagem

- **Equilibra objetividade e subjetividade**
- **Reconhece tanto funcionalidade quanto qualidade**
- **Permite avaliação de aspectos não testáveis automaticamente**
- **Mantém foco educacional**

## 🔧 Configuração e Personalização

### Alterando a Ponderação

Para modificar os pesos, edite o método `_calculate_python_score()`:

```python
# Exemplo: 50% testes + 50% IA
final_score = (test_score * 0.5) + (ai_score * 0.5)

# Exemplo: 30% testes + 70% IA
final_score = (test_score * 0.3) + (ai_score * 0.7)
```

### Adicionando Novos Critérios

Para incluir novos critérios de avaliação:

1. Adicione o cálculo no método apropriado
2. Ajuste os pesos para somar 100%
3. Atualize a documentação

## 📝 Logs e Auditoria

### Rastreamento das Notas

O sistema mantém logs detalhados em `logs/YYYY-MM-DD/assignment-name/`:

```json
{
  "metadata": {
    "assignment_name": "prog1-prova-av",
    "submission_identifier": "joao-silva",
    "analysis_type": "python"
  },
  "parsed_result": {
    "score": 8.5,  // Nota da IA
    "comments": [...],
    "suggestions": [...],
    "issues_found": [...]
  }
}
```

### Feedback para o Aluno

O sistema gera feedback detalhado incluindo:

```python
def _generate_feedback(self, submission: Submission, assignment: Assignment) -> str:
    # Feedback dos testes
    feedback_parts.append(f"Testes: {passed_tests}/{total_tests} passaram")
    
    # Feedback da análise de IA
    feedback_parts.append(f"Análise de código: {submission.code_analysis.score:.1f}/10")
```

## ⚠️ Considerações Importantes

### Limitações

1. **Testes**: Dependem da qualidade dos testes fornecidos
2. **IA**: Pode variar conforme o prompt e modelo usado
3. **Ponderação**: Fixa para todos os assignments do mesmo tipo

### Recomendações

1. **Revise os pesos** conforme a natureza do assignment
2. **Monitore os logs** para verificar consistência da IA
3. **Ajuste os prompts** para melhorar a qualidade da análise
4. **Teste a ponderação** com diferentes cenários

## 🔄 Histórico de Mudanças

- **v1.0**: Implementação inicial com 40% testes + 60% IA para Python
- **v1.0**: 100% IA para assignments HTML
- **Futuro**: Possibilidade de ponderação configurável por assignment

---

**Última atualização**: Janeiro 2025  
**Responsável**: Jefferson Santos  
**Arquivo**: `src/services/correction_service.py` 