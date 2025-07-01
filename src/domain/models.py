"""
Modelos de domínio para o sistema de correção automática.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pathlib import Path
import json
import re


class AssignmentType(Enum):
    """Tipos de assignment suportados."""
    PYTHON = "python"
    HTML = "html"


class SubmissionType(Enum):
    """Tipos de submissão."""
    INDIVIDUAL = "individual"
    GROUP = "group"


class AssignmentTestResult(Enum):
    """Resultados possíveis de testes."""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class AssignmentTestExecution:
    """Resultado da execução de um teste."""
    test_name: str
    result: AssignmentTestResult
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
class IndividualSubmission:
    """Submissão individual de um aluno."""
    github_login: str  # Login do aluno no GitHub
    assignment_name: str
    turma: str
    submission_path: Path
    files: List[str] = field(default_factory=list)
    test_results: List[AssignmentTestExecution] = field(default_factory=list)
    code_analysis: Optional[CodeAnalysis] = None
    html_analysis: Optional[HTMLAnalysis] = None
    final_score: float = 0.0
    feedback: str = ""
    
    @property
    def display_name(self) -> str:
        """Nome para exibição da submissão."""
        return f"{self.github_login} (individual)"


@dataclass
class GroupSubmission:
    """Submissão em grupo."""
    group_name: str  # Nome do grupo no GitHub
    assignment_name: str
    turma: str
    submission_path: Path
    files: List[str] = field(default_factory=list)
    test_results: List[AssignmentTestExecution] = field(default_factory=list)
    code_analysis: Optional[CodeAnalysis] = None
    html_analysis: Optional[HTMLAnalysis] = None
    final_score: float = 0.0
    feedback: str = ""
    
    @property
    def display_name(self) -> str:
        """Nome para exibição da submissão."""
        return f"{self.group_name} (grupo)"


# Tipo união para representar qualquer tipo de submissão
Submission = Union[IndividualSubmission, GroupSubmission]


@dataclass
class Assignment:
    """Definição de um assignment."""
    name: str
    type: AssignmentType
    submission_type: SubmissionType  # Novo campo
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
    individual_submissions: List[str] = field(default_factory=list)  # Logins individuais
    group_submissions: List[str] = field(default_factory=list)  # Nomes de grupos


@dataclass
class CorrectionReport:
    """Relatório de correção."""
    assignment_name: str
    turma: str
    submissions: List[Submission] = field(default_factory=list)
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
                    "submission_type": "individual" if isinstance(sub, IndividualSubmission) else "group",
                    "identifier": sub.github_login if isinstance(sub, IndividualSubmission) else sub.group_name,
                    "display_name": sub.display_name,
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
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'CorrectionReport':
        """Carrega o relatório de um arquivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstrói as submissões
        submissions = []
        for sub_data in data.get('submissions', []):
            if sub_data['submission_type'] == 'individual':
                submission = IndividualSubmission(
                    github_login=sub_data['identifier'],
                    assignment_name=data['assignment_name'],
                    turma=data['turma'],
                    submission_path=Path(),  # Não é necessário para conversão
                    final_score=sub_data['final_score'],
                    feedback=sub_data['feedback']
                )
                
                # Reconstrói análise de código se existir
                if sub_data.get('code_analysis'):
                    code_analysis = CodeAnalysis(
                        score=sub_data['code_analysis']['score'],
                        comments=sub_data['code_analysis'].get('comments', []),
                        suggestions=sub_data['code_analysis'].get('suggestions', []),
                        issues_found=sub_data['code_analysis'].get('issues_found', [])
                    )
                    submission.code_analysis = code_analysis
                
                # Reconstrói análise HTML se existir
                if sub_data.get('html_analysis'):
                    html_analysis = HTMLAnalysis(
                        score=sub_data['html_analysis']['score'],
                        required_elements=sub_data['html_analysis'].get('required_elements', {}),
                        comments=sub_data['html_analysis'].get('comments', []),
                        suggestions=sub_data['html_analysis'].get('suggestions', []),
                        issues_found=sub_data['html_analysis'].get('issues_found', [])
                    )
                    submission.html_analysis = html_analysis
                
                # Reconstrói resultados de testes
                for test_data in sub_data.get('test_results', []):
                    test_result = AssignmentTestExecution(
                        test_name=test_data['test_name'],
                        result=AssignmentTestResult(test_data['result']),
                        message=test_data.get('message', '')
                    )
                    submission.test_results.append(test_result)
                
                submissions.append(submission)
            
            else:  # group submission
                submission = GroupSubmission(
                    group_name=sub_data['identifier'],
                    assignment_name=data['assignment_name'],
                    turma=data['turma'],
                    submission_path=Path(),  # Não é necessário para conversão
                    final_score=sub_data['final_score'],
                    feedback=sub_data['feedback']
                )
                
                # Reconstrói análise de código se existir
                if sub_data.get('code_analysis'):
                    code_analysis = CodeAnalysis(
                        score=sub_data['code_analysis']['score'],
                        comments=sub_data['code_analysis'].get('comments', []),
                        suggestions=sub_data['code_analysis'].get('suggestions', []),
                        issues_found=sub_data['code_analysis'].get('issues_found', [])
                    )
                    submission.code_analysis = code_analysis
                
                # Reconstrói análise HTML se existir
                if sub_data.get('html_analysis'):
                    html_analysis = HTMLAnalysis(
                        score=sub_data['html_analysis']['score'],
                        required_elements=sub_data['html_analysis'].get('required_elements', {}),
                        comments=sub_data['html_analysis'].get('comments', []),
                        suggestions=sub_data['html_analysis'].get('suggestions', []),
                        issues_found=sub_data['html_analysis'].get('issues_found', [])
                    )
                    submission.html_analysis = html_analysis
                
                # Reconstrói resultados de testes
                for test_data in sub_data.get('test_results', []):
                    test_result = AssignmentTestExecution(
                        test_name=test_data['test_name'],
                        result=AssignmentTestResult(test_data['result']),
                        message=test_data.get('message', '')
                    )
                    submission.test_results.append(test_result)
                
                submissions.append(submission)
        
        return cls(
            assignment_name=data['assignment_name'],
            turma=data['turma'],
            submissions=submissions,
            summary=data.get('summary', {}),
            generated_at=data.get('generated_at', '')
        ) 