# Diagrama UML - Sistema de Correção Automática

> Gerado automaticamente em 01/07/2025 às 12:27:51

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
        class AssignmentType
        class CodeAnalysis
        class CorrectionReport
        class GroupSubmission
        class HTMLAnalysis
        class IndividualSubmission
        class SubmissionType
        class TestExecution
        class TestResult
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
        class TestExecutor
    }
    namespace utils {
        class ReportGenerator
    }
    TestExecution --> TestResult : has-a
    Assignment --> AssignmentType : has-a
    Assignment --> SubmissionType : has-a
    AssignmentRepository ..> Assignment
    AssignmentRepository ..> SubmissionType
    AssignmentRepository ..> AssignmentType
    SubmissionRepository ..> Turma
    SubmissionRepository ..> Assignment
    SubmissionRepository ..> IndividualSubmission
    SubmissionRepository ..> SubmissionType
    SubmissionRepository ..> GroupSubmission
    AIAnalyzer ..> HTMLAnalysis
    AIAnalyzer ..> CodeAnalysis
    AIAnalyzer ..> PromptManager
    AIAnalyzer ..> Assignment
    CorrectionService ..> AssignmentRepository
    CorrectionService ..> TestExecutor
    CorrectionService ..> AIAnalyzer
    CorrectionService ..> Assignment
    CorrectionService ..> CorrectionReport
    CorrectionService ..> SubmissionRepository
    CorrectionService ..> TestResult
    CorrectionService ..> AssignmentType
    PromptManager ..> Assignment
    TestExecutor ..> TestExecution
    TestExecutor ..> TestResult
    ReportGenerator ..> CorrectionReport
```

## Estrutura por Pacote

| Pacote | Classes | Quantidade |
|--------|---------|------------|
| `domain` | Assignment, AssignmentType, CodeAnalysis, CorrectionReport, GroupSubmission, HTMLAnalysis, IndividualSubmission, SubmissionType, TestExecution, TestResult, Turma | 11 |
| `repositories` | AssignmentRepository, SubmissionRepository | 2 |
| `services` | AIAnalyzer, CorrectionService, PromptManager, TestExecutor | 4 |
| `utils` | ReportGenerator | 1 |


## Estrutura por Módulo

| Módulo | Classes | Quantidade |
|--------|---------|------------|
| `domain/models.py` | Assignment, AssignmentType, CodeAnalysis, CorrectionReport, GroupSubmission, HTMLAnalysis, IndividualSubmission, SubmissionType, TestExecution, TestResult, Turma | 11 |
| `repositories/assignment_repository.py` | AssignmentRepository | 1 |
| `repositories/submission_repository.py` | SubmissionRepository | 1 |
| `services/ai_analyzer.py` | AIAnalyzer | 1 |
| `services/correction_service.py` | CorrectionService | 1 |
| `services/prompt_manager.py` | PromptManager | 1 |
| `services/test_executor.py` | TestExecutor | 1 |
| `utils/report_generator.py` | ReportGenerator | 1 |


## Detalhes dos Relacionamentos

### Herança
- Nenhuma herança encontrada

### Composição
- `TestExecution` contém `TestResult`
- `Assignment` contém `AssignmentType`
- `Assignment` contém `SubmissionType`

### Dependências
- `AssignmentRepository` depende de `Assignment`
- `AssignmentRepository` depende de `SubmissionType`
- `AssignmentRepository` depende de `AssignmentType`
- `SubmissionRepository` depende de `Turma`
- `SubmissionRepository` depende de `Assignment`
- `SubmissionRepository` depende de `IndividualSubmission`
- `SubmissionRepository` depende de `SubmissionType`
- `SubmissionRepository` depende de `GroupSubmission`
- `AIAnalyzer` depende de `HTMLAnalysis`
- `AIAnalyzer` depende de `CodeAnalysis`
- `AIAnalyzer` depende de `PromptManager`
- `AIAnalyzer` depende de `Assignment`
- `CorrectionService` depende de `AssignmentRepository`
- `CorrectionService` depende de `TestExecutor`
- `CorrectionService` depende de `AIAnalyzer`
- `CorrectionService` depende de `Assignment`
- `CorrectionService` depende de `CorrectionReport`
- `CorrectionService` depende de `SubmissionRepository`
- `CorrectionService` depende de `TestResult`
- `CorrectionService` depende de `AssignmentType`
- `PromptManager` depende de `Assignment`
- `TestExecutor` depende de `TestExecution`
- `TestExecutor` depende de `TestResult`
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
