"""
Testes para os modelos de domínio.
"""
import pytest
import json
import tempfile
from pathlib import Path
from src.domain.models import (
    AssignmentType, SubmissionType, TestResult, TestExecution, CodeAnalysis, 
    HTMLAnalysis, IndividualSubmission, GroupSubmission, Assignment, Turma, 
    CorrectionReport
)


class TestAssignmentType:
    """Testes para o enum AssignmentType."""
    
    def test_python_type(self):
        """Testa o tipo Python."""
        assert AssignmentType.PYTHON.value == "python"
    
    def test_html_type(self):
        """Testa o tipo HTML."""
        assert AssignmentType.HTML.value == "html"


class TestSubmissionType:
    """Testes para o enum SubmissionType."""
    
    def test_individual_type(self):
        """Testa o tipo individual."""
        assert SubmissionType.INDIVIDUAL.value == "individual"
    
    def test_group_type(self):
        """Testa o tipo grupo."""
        assert SubmissionType.GROUP.value == "group"


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


class TestIndividualSubmission:
    """Testes para IndividualSubmission."""
    
    def test_individual_submission_creation(self):
        """Testa a criação de um IndividualSubmission."""
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            files=["main.py", "scraper.py"],
            final_score=8.5,
            feedback="Good work overall"
        )
        
        assert submission.github_login == "joaosilva"
        assert submission.assignment_name == "prog1-prova-av"
        assert submission.turma == "ebape-prog-aplic-barra-2025"
        assert len(submission.files) == 2
        assert submission.final_score == 8.5
        assert submission.feedback == "Good work overall"
    
    def test_individual_submission_display_name(self):
        """Testa o display_name de IndividualSubmission."""
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission")
        )
        
        assert submission.display_name == "joaosilva (individual)"


class TestGroupSubmission:
    """Testes para GroupSubmission."""
    
    def test_group_submission_creation(self):
        """Testa a criação de um GroupSubmission."""
        submission = GroupSubmission(
            group_name="ana-clara-e-nadine",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            files=["main.py", "scraper.py"],
            final_score=9.0,
            feedback="Excellent teamwork"
        )
        
        assert submission.group_name == "ana-clara-e-nadine"
        assert submission.assignment_name == "prog1-prova-av"
        assert submission.turma == "ebape-prog-aplic-barra-2025"
        assert len(submission.files) == 2
        assert submission.final_score == 9.0
        assert submission.feedback == "Excellent teamwork"
    
    def test_group_submission_display_name(self):
        """Testa o display_name de GroupSubmission."""
        submission = GroupSubmission(
            group_name="ana-clara-e-nadine",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission")
        )
        
        assert submission.display_name == "ana-clara-e-nadine (grupo)"


class TestAssignment:
    """Testes para Assignment."""
    
    def test_assignment_creation(self):
        """Testa a criação de um Assignment."""
        assignment = Assignment(
            name="prog1-prova-av",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.GROUP,
            description="Web scraping with Streamlit dashboard",
            requirements=["Implement scraping functions", "Create dashboard"],
            test_files=["test_scraping.py"],
            rubric={"funcionamento": 0.4, "qualidade": 0.3},
            path=Path("/tmp/assignment")
        )
        
        assert assignment.name == "prog1-prova-av"
        assert assignment.type == AssignmentType.PYTHON
        assert assignment.submission_type == SubmissionType.GROUP
        assert "scraping" in assignment.description.lower()
        assert len(assignment.requirements) == 2
        assert len(assignment.test_files) == 1
        assert len(assignment.rubric) == 2
    
    def test_assignment_submission_type_configuration(self):
        """Testa que o tipo de submissão é configurado corretamente."""
        # Assignment configurado como grupo
        assignment = Assignment(
            name="prog1-prova-av",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.GROUP,
            description="Test assignment",
            path=Path("/tmp/assignment")
        )
        
        assert assignment.submission_type == SubmissionType.GROUP
        
        # Assignment configurado como individual
        assignment = Assignment(
            name="prog1-tarefa-html-curriculo",
            type=AssignmentType.HTML,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment",
            path=Path("/tmp/assignment")
        )
        
        assert assignment.submission_type == SubmissionType.INDIVIDUAL


class TestTurma:
    """Testes para Turma."""
    
    def test_turma_creation(self):
        """Testa a criação de uma Turma."""
        turma = Turma(
            name="ebape-prog-aplic-barra-2025",
            assignments=["prog1-prova-av", "prog1-tarefa-html-curriculo"],
            individual_submissions=["joaosilva", "mariasantos"],
            group_submissions=["ana-clara-e-nadine", "grupo-abc"]
        )
        
        assert turma.name == "ebape-prog-aplic-barra-2025"
        assert len(turma.assignments) == 2
        assert len(turma.individual_submissions) == 2
        assert len(turma.group_submissions) == 2


class TestCorrectionReport:
    """Testes para CorrectionReport."""
    
    def test_correction_report_creation(self):
        """Testa a criação de um CorrectionReport."""
        submissions = [
            IndividualSubmission(
                github_login="joaosilva",
                assignment_name="prog1-prova-av",
                turma="ebape-prog-aplic-barra-2025",
                submission_path=Path("/tmp/submission1"),
                final_score=8.5
            ),
            GroupSubmission(
                group_name="ana-clara-e-nadine",
                assignment_name="prog1-prova-av",
                turma="ebape-prog-aplic-barra-2025",
                submission_path=Path("/tmp/submission2"),
                final_score=9.0
            )
        ]
        
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=submissions,
            summary={"total_submissions": 2, "average_score": 8.75},
            generated_at="2024-01-01T10:00:00"
        )
        
        assert report.assignment_name == "prog1-prova-av"
        assert report.turma == "ebape-prog-aplic-barra-2025"
        assert len(report.submissions) == 2
        assert report.summary["total_submissions"] == 2
        assert report.summary["average_score"] == 8.75
    
    def test_correction_report_to_dict(self):
        """Testa a conversão para dicionário."""
        submission = IndividualSubmission(
            github_login="joaosilva",
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
        assert report_dict["submissions"][0]["submission_type"] == "individual"
        assert report_dict["submissions"][0]["identifier"] == "joaosilva"
        assert report_dict["submissions"][0]["final_score"] == 8.5
    
    def test_correction_report_save_and_load(self):
        """Testa salvar e carregar um relatório."""
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            final_score=8.5,
            feedback="Good work"
        )
        
        original_report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission],
            summary={"total_submissions": 1},
            generated_at="2024-01-01T10:00:00"
        )
        
        # Salva o relatório
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            original_report.save_to_file(temp_file)
            
            # Carrega o relatório
            loaded_report = CorrectionReport.load_from_file(temp_file)
            
            # Verifica se os dados foram preservados
            assert loaded_report.assignment_name == original_report.assignment_name
            assert loaded_report.turma == original_report.turma
            assert len(loaded_report.submissions) == len(original_report.submissions)
            assert loaded_report.submissions[0].github_login == "joaosilva"
            assert loaded_report.submissions[0].final_score == 8.5
            assert loaded_report.summary["total_submissions"] == 1
            
        finally:
            # Limpa o arquivo temporário
            temp_file.unlink(missing_ok=True)
    
    def test_correction_report_with_code_analysis(self):
        """Testa relatório com análise de código."""
        code_analysis = CodeAnalysis(
            score=8.5,
            comments=["Good structure"],
            suggestions=["Add comments"],
            issues_found=["Missing docstring"]
        )
        
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            code_analysis=code_analysis
        )
        
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission]
        )
        
        report_dict = report.to_dict()
        code_analysis_dict = report_dict["submissions"][0]["code_analysis"]
        
        assert code_analysis_dict["score"] == 8.5
        assert code_analysis_dict["comments"] == ["Good structure"]
        assert code_analysis_dict["suggestions"] == ["Add comments"]
        assert code_analysis_dict["issues_found"] == ["Missing docstring"]
    
    def test_correction_report_with_html_analysis(self):
        """Testa relatório com análise HTML."""
        html_analysis = HTMLAnalysis(
            score=7.0,
            required_elements={"h1": True, "h2": False},
            comments=["Good CSS"],
            suggestions=["Improve accessibility"],
            issues_found=["Missing alt"]
        )
        
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-tarefa-html-curriculo",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            html_analysis=html_analysis
        )
        
        report = CorrectionReport(
            assignment_name="prog1-tarefa-html-curriculo",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission]
        )
        
        report_dict = report.to_dict()
        html_analysis_dict = report_dict["submissions"][0]["html_analysis"]
        
        assert html_analysis_dict["score"] == 7.0
        assert html_analysis_dict["required_elements"]["h1"] is True
        assert html_analysis_dict["required_elements"]["h2"] is False
        assert html_analysis_dict["comments"] == ["Good CSS"]
        assert html_analysis_dict["suggestions"] == ["Improve accessibility"]
        assert html_analysis_dict["issues_found"] == ["Missing alt"]
    
    def test_correction_report_with_test_results(self):
        """Testa relatório com resultados de testes."""
        test_results = [
            TestExecution(
                test_name="test_function",
                result=TestResult.PASSED,
                message="Test passed",
                execution_time=0.5
            ),
            TestExecution(
                test_name="test_another_function",
                result=TestResult.FAILED,
                message="Test failed",
                execution_time=0.3
            )
        ]
        
        submission = IndividualSubmission(
            github_login="joaosilva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/submission"),
            test_results=test_results
        )
        
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission]
        )
        
        report_dict = report.to_dict()
        test_results_dict = report_dict["submissions"][0]["test_results"]
        
        assert len(test_results_dict) == 2
        assert test_results_dict[0]["test_name"] == "test_function"
        assert test_results_dict[0]["result"] == "passed"
        assert test_results_dict[0]["message"] == "Test passed"
        assert test_results_dict[1]["test_name"] == "test_another_function"
        assert test_results_dict[1]["result"] == "failed"
        assert test_results_dict[1]["message"] == "Test failed"
