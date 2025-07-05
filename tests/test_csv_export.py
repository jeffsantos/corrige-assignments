"""
Testes para o serviço de exportação CSV.
"""
import tempfile
import csv
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from src.services.csv_export_service import CSVExportService
from src.domain.models import (
    CorrectionReport, IndividualSubmission, GroupSubmission, 
    AssignmentTestExecution, AssignmentTestResult, CodeAnalysis
)


class TestCSVExportService:
    """Testes para CSVExportService."""
    
    def test_convert_submissions_to_csv_data_individual(self):
        """Testa conversão de submissão individual para dados CSV."""
        # Cria dados de teste
        submission = IndividualSubmission(
            github_login="joao-silva",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/test"),
            final_score=8.5
        )
        
        # Adiciona resultados de testes
        submission.test_results = [
            AssignmentTestExecution("test1", AssignmentTestResult.PASSED, "", 0.1),
            AssignmentTestExecution("test2", AssignmentTestResult.PASSED, "", 0.2),
            AssignmentTestExecution("test3", AssignmentTestResult.FAILED, "", 0.3),
        ]
        
        # Adiciona análise de código
        submission.code_analysis = CodeAnalysis(
            score=7.5,
            score_justification="Bom código",
            comments=["Bem estruturado"],
            suggestions=["Adicionar comentários"],
            issues_found=["Falta documentação"]
        )
        
        # Cria relatório
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission],
            generated_at="2025-01-15T10:30:14"
        )
        
        # Testa conversão
        service = CSVExportService(Path("/tmp"))
        csv_data = service._convert_submissions_to_csv_data(report)
        
        assert len(csv_data) == 1
        row = csv_data[0]
        
        assert row['assignment_name'] == "prog1-prova-av"
        assert row['turma'] == "ebape-prog-aplic-barra-2025"
        assert row['submission_identifier'] == "joao-silva"
        assert row['submission_type'] == "individual"
        assert row['test_score'] == 6.7  # 2/3 * 10
        assert row['ai_score'] == 7.5
        assert row['final_score'] == 8.5
        assert row['status'] == "🟡 Bom"
        assert row['tests_passed'] == 2
        assert row['tests_total'] == 3
        assert row['generated_at'] == "2025-01-15T10:30:14"
    
    def test_convert_submissions_to_csv_data_group(self):
        """Testa conversão de submissão em grupo para dados CSV."""
        # Cria dados de teste
        submission = GroupSubmission(
            group_name="grupo-abc",
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submission_path=Path("/tmp/test"),
            final_score=9.0
        )
        
        # Adiciona resultados de testes
        submission.test_results = [
            AssignmentTestExecution("test1", AssignmentTestResult.PASSED, "", 0.1),
            AssignmentTestExecution("test2", AssignmentTestExecution.PASSED, "", 0.2),
        ]
        
        # Adiciona análise de código
        submission.code_analysis = CodeAnalysis(
            score=9.0,
            score_justification="Excelente código",
            comments=["Muito bem estruturado"],
            suggestions=["Nenhuma sugestão"],
            issues_found=["Nenhum problema"]
        )
        
        # Cria relatório
        report = CorrectionReport(
            assignment_name="prog1-prova-av",
            turma="ebape-prog-aplic-barra-2025",
            submissions=[submission],
            generated_at="2025-01-15T10:30:14"
        )
        
        # Testa conversão
        service = CSVExportService(Path("/tmp"))
        csv_data = service._convert_submissions_to_csv_data(report)
        
        assert len(csv_data) == 1
        row = csv_data[0]
        
        assert row['assignment_name'] == "prog1-prova-av"
        assert row['turma'] == "ebape-prog-aplic-barra-2025"
        assert row['submission_identifier'] == "grupo-abc"
        assert row['submission_type'] == "group"
        assert row['test_score'] == 10.0  # 2/2 * 10
        assert row['ai_score'] == 9.0
        assert row['final_score'] == 9.0
        assert row['status'] == "🟢 Excelente"
        assert row['tests_passed'] == 2
        assert row['tests_total'] == 2
        assert row['generated_at'] == "2025-01-15T10:30:14"
    
    def test_write_csv_file(self):
        """Testa escrita de arquivo CSV."""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CSVExportService(Path("/tmp"))
            
            # Dados de teste
            csv_data = [
                {
                    'assignment_name': 'prog1-prova-av',
                    'turma': 'ebape-prog-aplic-barra-2025',
                    'submission_identifier': 'joao-silva',
                    'submission_type': 'individual',
                    'test_score': 8.0,
                    'ai_score': 7.5,
                    'final_score': 7.7,
                    'status': '🟡 Bom',
                    'tests_passed': 4,
                    'tests_total': 5,
                    'generated_at': '2025-01-15T10:30:14'
                }
            ]
            
            output_path = Path(temp_dir) / "test_results.csv"
            
            # Escreve arquivo CSV
            service._write_csv_file(csv_data, output_path)
            
            # Verifica se arquivo foi criado
            assert output_path.exists()
            
            # Verifica conteúdo
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                assert len(rows) == 1
                row = rows[0]
                
                assert row['assignment_name'] == 'prog1-prova-av'
                assert row['turma'] == 'ebape-prog-aplic-barra-2025'
                assert row['submission_identifier'] == 'joao-silva'
                assert row['submission_type'] == 'individual'
                assert float(row['test_score']) == 8.0
                assert float(row['ai_score']) == 7.5
                assert float(row['final_score']) == 7.7
                assert row['status'] == '🟡 Bom'
                assert int(row['tests_passed']) == 4
                assert int(row['tests_total']) == 5
                assert row['generated_at'] == '2025-01-15T10:30:14'
    
    def test_get_export_statistics(self):
        """Testa cálculo de estatísticas de exportação."""
        service = CSVExportService(Path("/tmp"))
        
        # Dados de teste
        csv_data = [
            {'test_score': 8.0, 'ai_score': 7.5, 'final_score': 7.7},
            {'test_score': 10.0, 'ai_score': 9.0, 'final_score': 9.4},
            {'test_score': 6.0, 'ai_score': 5.5, 'final_score': 5.7},
            {'test_score': 0.0, 'ai_score': 0.0, 'final_score': 0.0},  # Sem dados
        ]
        
        stats = service.get_export_statistics(csv_data)
        
        assert stats['total_submissions'] == 4
        assert stats['avg_test_score'] == 8.0  # (8+10+6)/3 (exclui 0.0)
        assert stats['avg_ai_score'] == 7.33  # (7.5+9+5.5)/3 (exclui 0.0)
        assert stats['avg_final_score'] == 5.7  # (7.7+9.4+5.7+0.0)/4
        assert stats['min_final_score'] == 0.0
        assert stats['max_final_score'] == 9.4
        assert stats['passing_rate'] == 75.0  # 3/4 >= 6.0
        assert stats['excellent_rate'] == 25.0  # 1/4 >= 9.0
    
    def test_export_statistics_empty_data(self):
        """Testa estatísticas com dados vazios."""
        service = CSVExportService(Path("/tmp"))
        
        stats = service.get_export_statistics([])
        
        assert stats == {}
    
    @patch('src.services.csv_export_service.CorrectionReport.load_from_file')
    def test_load_report_from_json_success(self, mock_load):
        """Testa carregamento bem-sucedido de relatório JSON."""
        # Mock do relatório
        mock_report = Mock()
        mock_load.return_value = mock_report
        
        service = CSVExportService(Path("/tmp"))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_path = Path(temp_dir)
            service.reports_path = reports_path
            
            # Cria arquivo JSON fake
            json_path = reports_path / "prog1-prova-av_ebape-prog-aplic-barra-2025.json"
            json_path.touch()
            
            # Testa carregamento
            result = service._load_report_from_json("prog1-prova-av", "ebape-prog-aplic-barra-2025")
            
            assert result == mock_report
            mock_load.assert_called_once_with(json_path)
    
    def test_load_report_from_json_not_found(self):
        """Testa carregamento quando arquivo não existe."""
        service = CSVExportService(Path("/tmp"))
        
        result = service._load_report_from_json("inexistente", "turma-inexistente")
        
        assert result is None
    
    def test_write_csv_file_empty_data(self):
        """Testa escrita de CSV com dados vazios."""
        service = CSVExportService(Path("/tmp"))
        
        with pytest.raises(ValueError, match="Nenhum dado para exportar"):
            service._write_csv_file([], Path("/tmp/test.csv")) 