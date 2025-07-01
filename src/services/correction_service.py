"""
Serviço principal de correção que orquestra todo o processo.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from ..domain.models import (
    IndividualSubmission, GroupSubmission, Submission, Assignment, CorrectionReport, 
    AssignmentType, AssignmentTestResult
)
from ..repositories.assignment_repository import AssignmentRepository
from ..repositories.submission_repository import SubmissionRepository
from .test_executor import PytestExecutor
from .ai_analyzer import AIAnalyzer


class CorrectionService:
    """Serviço principal de correção."""
    
    def __init__(self, enunciados_path: Path, respostas_path: Path, openai_api_key: str = None, logs_path: Path = None):
        self.assignment_repo = AssignmentRepository(enunciados_path)
        self.submission_repo = SubmissionRepository(respostas_path)
        self.test_executor = PytestExecutor()
        self.ai_analyzer = AIAnalyzer(openai_api_key, enunciados_path, logs_path)
    
    def correct_assignment(self, assignment_name: str, turma_name: str, 
                          submission_identifier: Optional[str] = None) -> CorrectionReport:
        """Corrige um assignment específico."""
        # Carrega o assignment
        assignment = self.assignment_repo.get_assignment(assignment_name)
        if not assignment:
            raise ValueError(f"Assignment '{assignment_name}' não encontrado")
        
        # Carrega as submissões
        if submission_identifier:
            submissions = [self.submission_repo.get_submission(turma_name, assignment_name, submission_identifier)]
            submissions = [s for s in submissions if s is not None]
        else:
            submissions = self.submission_repo.get_submissions_for_assignment(turma_name, assignment_name)
        
        if not submissions:
            raise ValueError(f"Nenhuma submissão encontrada para {assignment_name} na turma {turma_name}")
        
        # Processa cada submissão
        for submission in submissions:
            self._process_submission(submission, assignment)
        
        # Cria o relatório
        report = CorrectionReport(
            assignment_name=assignment_name,
            turma=turma_name,
            submissions=submissions,
            generated_at=datetime.now().isoformat()
        )
        
        # Calcula estatísticas do relatório
        report.summary = self._calculate_summary(submissions)
        
        return report
    
    def correct_all_assignments(self, turma_name: str) -> List[CorrectionReport]:
        """Corrige todos os assignments de uma turma."""
        turma = self.submission_repo.get_turma(turma_name)
        if not turma:
            raise ValueError(f"Turma '{turma_name}' não encontrada")
        
        reports = []
        
        for assignment_name in turma.assignments:
            try:
                report = self.correct_assignment(assignment_name, turma_name)
                reports.append(report)
            except Exception as e:
                print(f"Erro ao corrigir {assignment_name}: {e}")
                continue
        
        return reports
    
    def _process_submission(self, submission: Submission, assignment: Assignment):
        """Processa uma submissão."""
        print(f"Processando submissão de {submission.display_name}...")
        
        # Executa testes se for assignment Python
        if assignment.type == AssignmentType.PYTHON and assignment.test_files:
            submission.test_results = self.test_executor.run_tests(
                submission.submission_path, 
                assignment.test_files
            )
        
        # Analisa código usando IA
        if assignment.type == AssignmentType.PYTHON:
            submission.code_analysis = self.ai_analyzer.analyze_python_code(
                submission.submission_path, 
                assignment
            )
        else:  # HTML
            submission.html_analysis = self.ai_analyzer.analyze_html_code(
                submission.submission_path, 
                assignment
            )
        
        # Calcula nota final
        submission.final_score = self._calculate_final_score(submission, assignment)
        
        # Gera feedback
        submission.feedback = self._generate_feedback(submission, assignment)
    
    def _calculate_final_score(self, submission: Submission, assignment: Assignment) -> float:
        """Calcula a nota final baseada nos critérios da rubrica."""
        if assignment.type == AssignmentType.PYTHON:
            return self._calculate_python_score(submission, assignment)
        else:
            return self._calculate_html_score(submission, assignment)
    
    def _calculate_python_score(self, submission: Submission, assignment: Assignment) -> float:
        """Calcula nota para assignments Python."""
        rubric = assignment.rubric
        
        # Nota dos testes (40% do peso total)
        test_score = 0.0
        if submission.test_results:
            passed_tests = sum(1 for test in submission.test_results if test.result == AssignmentTestResult.PASSED)
            total_tests = len(submission.test_results)
            if total_tests > 0:
                test_score = (passed_tests / total_tests) * 10.0
        
        # Nota da análise de IA (60% do peso total)
        ai_score = 0.0
        if submission.code_analysis:
            ai_score = submission.code_analysis.score
        
        # Calcula nota final ponderada
        final_score = (test_score * 0.4) + (ai_score * 0.6)
        
        return min(10.0, max(0.0, final_score))
    
    def _calculate_html_score(self, submission: Submission, assignment: Assignment) -> float:
        """Calcula nota para assignments HTML."""
        if submission.html_analysis:
            return submission.html_analysis.score
        return 0.0
    
    def _generate_feedback(self, submission: Submission, assignment: Assignment) -> str:
        """Gera feedback personalizado para o aluno."""
        feedback_parts = []
        
        # Feedback dos testes
        if submission.test_results:
            passed_tests = sum(1 for test in submission.test_results if test.result == AssignmentTestResult.PASSED)
            total_tests = len(submission.test_results)
            feedback_parts.append(f"Testes: {passed_tests}/{total_tests} passaram")
            
            # Adiciona detalhes dos testes que falharam
            failed_tests = [test for test in submission.test_results if test.result == AssignmentTestResult.FAILED]
            if failed_tests:
                feedback_parts.append("Testes que falharam:")
                for test in failed_tests[:3]:  # Limita a 3 testes para não ficar muito longo
                    feedback_parts.append(f"- {test.test_name}: {test.message[:100]}...")
        
        # Feedback da análise de IA
        if assignment.type == AssignmentType.PYTHON and submission.code_analysis:
            feedback_parts.append(f"Análise de código: {submission.code_analysis.score:.1f}/10")
            if submission.code_analysis.comments:
                feedback_parts.append("Pontos positivos:")
                for comment in submission.code_analysis.comments[:2]:
                    feedback_parts.append(f"- {comment}")
            if submission.code_analysis.issues_found:
                feedback_parts.append("Problemas encontrados:")
                for issue in submission.code_analysis.issues_found[:2]:
                    feedback_parts.append(f"- {issue}")
        
        elif assignment.type == AssignmentType.HTML and submission.html_analysis:
            feedback_parts.append(f"Análise HTML/CSS: {submission.html_analysis.score:.1f}/10")
            if submission.html_analysis.required_elements:
                feedback_parts.append("Elementos HTML:")
                for element, found in submission.html_analysis.required_elements.items():
                    status = "✓" if found else "✗"
                    feedback_parts.append(f"- {element}: {status}")
        
        return "\n".join(feedback_parts)
    
    def _calculate_summary(self, submissions: List[Submission]) -> dict:
        """Calcula estatísticas resumidas das submissões."""
        if not submissions:
            return {}
        
        scores = [sub.final_score for sub in submissions]
        
        return {
            "total_submissions": len(submissions),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "passing_rate": sum(1 for score in scores if score >= 6.0) / len(scores),
            "excellent_rate": sum(1 for score in scores if score >= 9.0) / len(scores)
        } 