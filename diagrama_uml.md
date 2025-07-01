# Diagrama UML - Sistema de Correção Automática

> Gerado automaticamente em 01/07/2025 às 16:36:39

## Visão Geral

Este diagrama representa a arquitetura e relacionamentos entre as classes do sistema de correção automática de assignments.

**Estatísticas:**
- **Total de classes:** 18
- **Módulos:** 8
- **Pacotes:** 4
- **Heranças:** 0
- **Composições:** 3
- **Dependências:** 24

## Diagrama de Classes

```mermaid
classDiagram
    namespace domain {
        class Assignment
        class AssignmentTestExecution
        class AssignmentTestResult
        class AssignmentType
        class CodeAnalysis
        class CorrectionReport
        class GroupSubmission
        class HTMLAnalysis
        class IndividualSubmission
        class SubmissionType
        class Turma
    }
    namespace repositories {
        class AssignmentRepository
        class SubmissionRepository
    }
    namespace services {
        class AIAnalyzer
        class CorrectionService
        class PromptManager
        class PytestExecutor
    }
    namespace utils {
        class ReportGenerator
    }
    AssignmentTestExecution --> AssignmentTestResult : has-a
    Assignment --> SubmissionType : has-a
    Assignment --> AssignmentType : has-a
    CorrectionReport ..> CorrectionReport
    AssignmentRepository ..> SubmissionType
    AssignmentRepository ..> AssignmentType
    AssignmentRepository ..> Assignment
    SubmissionRepository ..> SubmissionType
    SubmissionRepository ..> GroupSubmission
    SubmissionRepository ..> Turma
    SubmissionRepository ..> IndividualSubmission
    AIAnalyzer ..> CodeAnalysis
    AIAnalyzer ..> HTMLAnalysis
    AIAnalyzer ..> PromptManager
    AIAnalyzer ..> Assignment
    CorrectionService ..> AssignmentType
    CorrectionService ..> CorrectionReport
    CorrectionService ..> SubmissionRepository
    CorrectionService ..> PytestExecutor
    CorrectionService ..> AIAnalyzer
    CorrectionService ..> AssignmentTestResult
    CorrectionService ..> Assignment
    CorrectionService ..> AssignmentRepository
    PromptManager ..> Assignment
    PytestExecutor ..> AssignmentTestExecution
    PytestExecutor ..> AssignmentTestResult
    ReportGenerator ..> CorrectionReport
```

## Estrutura por Pacote

| Pacote | Classes | Quantidade |
|--------|---------|------------|
| `domain` | Assignment, AssignmentTestExecution, AssignmentTestResult, AssignmentType, CodeAnalysis, CorrectionReport, GroupSubmission, HTMLAnalysis, IndividualSubmission, SubmissionType, Turma | 11 |
| `repositories` | AssignmentRepository, SubmissionRepository | 2 |
| `services` | AIAnalyzer, CorrectionService, PromptManager, PytestExecutor | 4 |
| `utils` | ReportGenerator | 1 |


## Estrutura por Módulo

| Módulo | Classes | Quantidade |
|--------|---------|------------|
| `domain/models.py` | Assignment, AssignmentTestExecution, AssignmentTestResult, AssignmentType, CodeAnalysis, CorrectionReport, GroupSubmission, HTMLAnalysis, IndividualSubmission, SubmissionType, Turma | 11 |
| `repositories/assignment_repository.py` | AssignmentRepository | 1 |
| `repositories/submission_repository.py` | SubmissionRepository | 1 |
| `services/ai_analyzer.py` | AIAnalyzer | 1 |
| `services/correction_service.py` | CorrectionService | 1 |
| `services/prompt_manager.py` | PromptManager | 1 |
| `services/test_executor.py` | PytestExecutor | 1 |
| `utils/report_generator.py` | ReportGenerator | 1 |


## Detalhes dos Relacionamentos

### Herança
- Nenhuma herança encontrada

### Composição
- `AssignmentTestExecution` contém `AssignmentTestResult`
- `Assignment` contém `SubmissionType`
- `Assignment` contém `AssignmentType`

### Dependências
- `CorrectionReport` depende de `CorrectionReport`
- `AssignmentRepository` depende de `SubmissionType`
- `AssignmentRepository` depende de `AssignmentType`
- `AssignmentRepository` depende de `Assignment`
- `SubmissionRepository` depende de `SubmissionType`
- `SubmissionRepository` depende de `GroupSubmission`
- `SubmissionRepository` depende de `Turma`
- `SubmissionRepository` depende de `IndividualSubmission`
- `AIAnalyzer` depende de `CodeAnalysis`
- `AIAnalyzer` depende de `HTMLAnalysis`
- `AIAnalyzer` depende de `PromptManager`
- `AIAnalyzer` depende de `Assignment`
- `CorrectionService` depende de `AssignmentType`
- `CorrectionService` depende de `CorrectionReport`
- `CorrectionService` depende de `SubmissionRepository`
- `CorrectionService` depende de `PytestExecutor`
- `CorrectionService` depende de `AIAnalyzer`
- `CorrectionService` depende de `AssignmentTestResult`
- `CorrectionService` depende de `Assignment`
- `CorrectionService` depende de `AssignmentRepository`
- `PromptManager` depende de `Assignment`
- `PytestExecutor` depende de `AssignmentTestExecution`
- `PytestExecutor` depende de `AssignmentTestResult`
- `ReportGenerator` depende de `CorrectionReport`

## Legenda do Diagrama

- **<|--** : Herança (is-a)
- **-->** : Composição (has-a)
- **..>** : Dependência (depends-on)
- **package** : Agrupamento de classes por pacote/módulo

## Como Visualizar

1. **GitHub**: Este arquivo Markdown será renderizado automaticamente com o diagrama Mermaid
2. **VS Code**: Use a extensão "Markdown Preview Mermaid Support"
3. **Online**: Cole o conteúdo do bloco Mermaid em https://mermaid.live/

## Gerado por

Script: `tools/generate_mermaid_uml.py`
