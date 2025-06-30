"""
Testes para os modelos de domínio.
"""
import pytest
from pathlib import Path
from src.domain.models import (
    AssignmentType, TestResult, TestExecution, CodeAnalysis, 
    HTMLAnalysis, StudentSubmission, Assignment, Turma, CorrectionReport
)


class TestAssignmentType:
    """Testes para o enum AssignmentType."""
    
    def test_python_type(self):
        """Testa o tipo Python."""
        assert AssignmentType.PYTHON.value == "python"
    
    def test_html_type(self):
        """Testa o tipo HTML."""
        assert AssignmentType.HTML.value == "html"


class TestTestResult:
    """Testes para o enum TestResult."""
    
    def test_passed_result(self):
        """Testa o resultado passed."""
        assert TestResult.PASSED.value == "passed"
    
    def test_failed_result(self):
        """Testa o resultado failed."""
        assert TestResult.FAILED.value == "failed"
    
    def test_error_result(self):
        """Testa o resultado error."""
        assert TestResult.ERROR.value == "error"
    
    def test_skipped_result(self):
        """Testa o resultado skipped."""
        assert TestResult.SKIPPED.value == "skipped"


class TestTestExecution:
    """Testes para TestExecution."""
    
    def test_test_execution_creation(self):
        """Testa a criação de um TestExecution."""
        test_exec = TestExecution(
            test_name="test_example",
            result=TestResult.PASSED,
            message="Test passed successfully",
            execution_time=1.5
        )
        
        assert test_exec.test_name == "test_example"
        assert test_exec.result == TestResult.PASSED
        assert test_exec.message == "Test passed successfully"
        assert test_exec.execution_time == 1.5


class TestCodeAnalysis:
    """Testes para CodeAnalysis."""
    
    def test_code_analysis_creation(self):
        """Testa a criação de um CodeAnalysis."""
        analysis = CodeAnalysis(
            score=8.5,
            comments=["Good code structure", "Clear variable names"],
            suggestions=["Add more comments", "Consider error handling"],
            issues_found=["Missing docstring", "Unused import"]
        )
        
        assert analysis.score == 8.5
        assert len(analysis.comments) == 2
        assert len(analysis.suggestions) == 2
        assert len(analysis.issues_found) == 2


class TestHTMLAnalysis:
    """Testes para HTMLAnalysis."""
    
    def test_html_analysis_creation(self):
        """Testa a criação de um HTMLAnalysis."""
        analysis = HTMLAnalysis(
            score=7.0,
            required_elements={"h1": True, "h2": False, "table": True},
            comments=["Good use of CSS", "Responsive design"],
            suggestions=["Add more semantic HTML", "Improve accessibility"],
            issues_found=["Missing alt attributes", "No form validation"]
        )
        
        assert analysis.score == 7.0
        assert analysis.required_elements["h1"] is True
        assert analysis.required_elements["h2"] is False
        assert len(analysis.comments) == 2
        assert len(analysis.suggestions) == 2
        assert len(analysis.issues_found) == 2


class TestStudentSubmission:
    """Testes para StudentSubmission."""
    
    def test_student_submission_creation(self):
        """Testa a criação de um StudentSubmission."""
        submission = StudentSubmission(
            student_name="João Silva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            files=["main.py", "scraper.py"],
            final_score=8.5,
            feedback="Good work overall"
        )
        
        assert submission.student_name == "João Silva"
        assert submission.assignment_name == "prog1-prova-av"
        assert submission.turma == "ebape-prog-aplic-barra-2025"
        assert len(submission.files) == 2
        assert submission.final_score == 8.5
        assert submission.feedback == "Good work overall"


class TestAssignment:
    """Testes para Assignment."""
    
    def test_assignment_creation(self):
        """Testa a criação de um Assignment."""
        assignment = Assignment(
            name="prog1-prova-av",
            type=AssignmentType.PYTHON,
            description="Web scraping with Streamlit dashboard",
            requirements=["Implement scraping functions", "Create dashboard"],
            test_files=["test_scraping.py"],
            rubric={"funcionamento": 0.4, "qualidade": 0.3},
            path=Path("/tmp/assignment")
        )
        
        assert assignment.name == "prog1-prova-av"
        assert assignment.type == AssignmentType.PYTHON
        assert "scraping" in assignment.description.lower()
        assert len(assignment.requirements) == 2
        assert len(assignment.test_files) == 1
        assert len(assignment.rubric) == 2


class TestTurma:
    """Testes para Turma."""
    
    def test_turma_creation(self):
        """Testa a criação de uma Turma."""
        turma = Turma(
            name="ebape-prog-aplic-barra-2025",
            assignments=["prog1-prova-av", "prog1-tarefa-html-curriculo"],
            students=["João Silva", "Maria Santos"]
        )
        
        assert turma.name == "ebape-prog-aplic-barra-2025"
        assert len(turma.assignments) == 2
        assert len(turma.students) == 2


class TestCorrectionReport:
    """Testes para CorrectionReport."""
    
    def test_correction_report_creation(self):
        """Testa a criação de um CorrectionReport."""
        submissions = [
            StudentSubmission(
                student_name="João Silva",
                assignment_name="prog1-prova-av",
                turma="ebape-prog-aplic-barra-2025",
                submission_path=Path("/tmp/submission1"),
                final_score=8.5
            ),
            StudentSubmission(
                student_name="Maria Santos",
                assignment_name="prog1-prova-av",
                turma="ebape-prog-aplic-barra-2025",
                submission_path=Path("/tmp/submission2"),
                final_score=7.0
            )
        ]
        
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=submissions,
            summary={"total_submissions": 2, "average_score": 7.75},
            generated_at="2024-01-01T10:00:00"
        )
        
        assert report.assignment_name == "prog1-prova-av"
        assert report.turma == "ebape-prog-aplic-barra-2025"
        assert len(report.submissions) == 2
        assert report.summary["total_submissions"] == 2
        assert report.summary["average_score"] == 7.75
    
    def test_correction_report_to_dict(self):
        """Testa a conversão para dicionário."""
        submission = StudentSubmission(
            student_name="João Silva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            final_score=8.5,
            feedback="Good work"
        )
        
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission],
            summary={"total_submissions": 1},
            generated_at="2024-01-01T10:00:00"
        )
        
        report_dict = report.to_dict()
        
        assert report_dict["assignment_name"] == "prog1-prova-av"
        assert report_dict["turma"] == "ebape-prog-aplic-barra-2025"
        assert len(report_dict["submissions"]) == 1
        assert report_dict["submissions"][0]["student_name"] == "João Silva"
        assert report_dict["submissions"][0]["final_score"] == 8.5 