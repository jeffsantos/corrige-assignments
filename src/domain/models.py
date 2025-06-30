"""
Modelos de domínio para o sistema de correção automática.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
import json


class AssignmentType(Enum):
    """Tipos de assignment suportados."""
    PYTHON = "python"
    HTML = "html"


class TestResult(Enum):
    """Resultados possíveis de testes."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestExecution:
    """Resultado da execução de um teste."""
    test_name: str
    result: TestResult
    message: str = ""
    execution_time: float = 0.0


@dataclass
class CodeAnalysis:
    """Análise de código usando IA."""
    score: float  # Nota de 0 a 10
    comments: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    issues_found: List[str] = field(default_factory=list)


@dataclass
class HTMLAnalysis:
    """Análise de páginas HTML."""
    score: float  # Nota de 0 a 10
    required_elements: Dict[str, bool] = field(default_factory=dict)
    comments: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    issues_found: List[str] = field(default_factory=list)


@dataclass
class StudentSubmission:
    """Submissão de um aluno."""
    student_name: str
    assignment_name: str
    turma: str
    submission_path: Path
    files: List[str] = field(default_factory=list)
    test_results: List[TestExecution] = field(default_factory=list)
    code_analysis: Optional[CodeAnalysis] = None
    html_analysis: Optional[HTMLAnalysis] = None
    final_score: float = 0.0
    feedback: str = ""


@dataclass
class Assignment:
    """Definição de um assignment."""
    name: str
    type: AssignmentType
    description: str
    requirements: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    rubric: Dict[str, float] = field(default_factory=dict)
    path: Path = field(default_factory=Path)


@dataclass
class Turma:
    """Representa uma turma."""
    name: str
    assignments: List[str] = field(default_factory=list)
    students: List[str] = field(default_factory=list)


@dataclass
class CorrectionReport:
    """Relatório de correção."""
    assignment_name: str
    turma: str
    submissions: List[StudentSubmission] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o relatório para dicionário."""
        return {
            "assignment_name": self.assignment_name,
            "turma": self.turma,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "submissions": [
                {
                    "student_name": sub.student_name,
                    "final_score": sub.final_score,
                    "feedback": sub.feedback,
                    "test_results": [
                        {
                            "test_name": test.test_name,
                            "result": test.result.value,
                            "message": test.message
                        }
                        for test in sub.test_results
                    ],
                    "code_analysis": {
                        "score": sub.code_analysis.score,
                        "comments": sub.code_analysis.comments,
                        "suggestions": sub.code_analysis.suggestions,
                        "issues_found": sub.code_analysis.issues_found
                    } if sub.code_analysis else None,
                    "html_analysis": {
                        "score": sub.html_analysis.score,
                        "required_elements": sub.html_analysis.required_elements,
                        "comments": sub.html_analysis.comments,
                        "suggestions": sub.html_analysis.suggestions,
                        "issues_found": sub.html_analysis.issues_found
                    } if sub.html_analysis else None
                }
                for sub in self.submissions
            ]
        }
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva o relatório em arquivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False) 