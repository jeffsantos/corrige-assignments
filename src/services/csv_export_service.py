"""
Serviço para exportação de resultados de correção em formato CSV.
"""
import csv
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from ..domain.models import CorrectionReport, Submission, IndividualSubmission, GroupSubmission
from ..repositories.assignment_repository import AssignmentRepository


class CSVExportService:
    """Serviço para exportação de resultados em CSV."""
    
    def __init__(self, reports_path: Path):
        self.reports_path = reports_path
    
    def export_single_assignment(self, assignment_name: str, turma_name: str, output_dir: Path) -> Path:
        """Exporta resultados de um assignment específico para CSV."""
        # Carrega o relatório
        report = self._load_report_from_json(assignment_name, turma_name)
        if not report:
            raise ValueError(f"Relatório não encontrado para {assignment_name} da turma {turma_name}")
        
        # Converte dados para CSV
        csv_data = self._convert_submissions_to_csv_data(report)
        
        # Cria diretório de saída se não existir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Define nome do arquivo
        filename = f"{assignment_name}_{turma_name}_results.csv"
        output_path = output_dir / filename
        
        # Escreve arquivo CSV
        self._write_csv_file(csv_data, output_path)
        
        return output_path
    
    def export_all_assignments(self, turma_name: str, output_dir: Path) -> List[Path]:
        """Exporta resultados de todos os assignments de uma turma para CSV."""
        # Busca todos os relatórios JSON da turma
        json_files = list(self.reports_path.glob(f"*_{turma_name}.json"))
        
        if not json_files:
            raise ValueError(f"Nenhum relatório encontrado para a turma {turma_name}")
        
        exported_files = []
        
        for json_file in json_files:
            # Extrai nome do assignment do nome do arquivo
            assignment_name = json_file.stem.replace(f"_{turma_name}", "")
            
            try:
                output_path = self.export_single_assignment(assignment_name, turma_name, output_dir)
                exported_files.append(output_path)
            except Exception as e:
                print(f"⚠️  Erro ao exportar {assignment_name}: {e}")
                continue
        
        return exported_files
    
    def export_multiple_assignments(self, assignments: List[str], turma_name: str, output_dir: Path) -> List[Path]:
        """Exporta resultados de múltiplos assignments específicos."""
        exported_files = []
        
        for assignment_name in assignments:
            try:
                output_path = self.export_single_assignment(assignment_name, turma_name, output_dir)
                exported_files.append(output_path)
            except Exception as e:
                print(f"⚠️  Erro ao exportar {assignment_name}: {e}")
                continue
        
        return exported_files
    
    def _load_report_from_json(self, assignment_name: str, turma_name: str) -> Optional[CorrectionReport]:
        """Carrega relatório de um arquivo JSON."""
        json_filename = f"{assignment_name}_{turma_name}.json"
        json_path = self.reports_path / json_filename
        
        if not json_path.exists():
            return None
        
        try:
            return CorrectionReport.load_from_file(json_path)
        except Exception as e:
            print(f"⚠️  Erro ao carregar {json_filename}: {e}")
            return None
    
    def _convert_submissions_to_csv_data(self, report: CorrectionReport) -> List[Dict]:
        """Converte submissões do relatório para formato CSV."""
        csv_data = []
        
        for submission in report.submissions:
            # Calcula nota dos testes
            test_score = 0.0
            tests_passed = 0
            tests_total = 0
            if submission.test_results:
                tests_passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                tests_total = len(submission.test_results)
                if tests_total > 0:
                    test_score = (tests_passed / tests_total) * 10.0
            
            # Calcula nota da IA
            ai_score = 0.0
            if hasattr(submission, 'code_analysis') and submission.code_analysis:
                ai_score = submission.code_analysis.score
            elif hasattr(submission, 'html_analysis') and submission.html_analysis:
                ai_score = submission.html_analysis.score
            
            # Determina tipo de submissão e identificador
            if isinstance(submission, IndividualSubmission):
                submission_type = "individual"
                submission_identifier = submission.github_login
            else:  # GroupSubmission
                submission_type = "group"
                submission_identifier = submission.group_name
            
            # Determina status baseado na nota final
            if submission.final_score >= 9.0:
                status = "🟢 Excelente"
            elif submission.final_score >= 7.0:
                status = "🟡 Bom"
            elif submission.final_score >= 6.0:
                status = "🟠 Aprovado"
            else:
                status = "🔴 Reprovado"
            
            # Cria linha de dados
            row = {
                'assignment_name': report.assignment_name,
                'turma': report.turma,
                'submission_identifier': submission_identifier,
                'submission_type': submission_type,
                'test_score': round(test_score, 1),
                'ai_score': round(ai_score, 1),
                'final_score': round(submission.final_score, 1),
                'status': status,
                'tests_passed': tests_passed,
                'tests_total': tests_total,
                'generated_at': report.generated_at
            }
            
            csv_data.append(row)
        
        return csv_data
    
    def _write_csv_file(self, data: List[Dict], output_path: Path) -> None:
        """Escreve dados em arquivo CSV."""
        if not data:
            raise ValueError("Nenhum dado para exportar")
        
        # Define campos do CSV
        fieldnames = [
            'assignment_name', 'turma', 'submission_identifier', 'submission_type',
            'test_score', 'ai_score', 'final_score', 'status',
            'tests_passed', 'tests_total', 'generated_at'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Escreve cabeçalho
            writer.writeheader()
            
            # Escreve dados
            writer.writerows(data)
    
    def get_export_statistics(self, csv_data: List[Dict]) -> Dict:
        """Calcula estatísticas da exportação."""
        if not csv_data:
            return {}
        
        total_submissions = len(csv_data)
        test_scores = [row['test_score'] for row in csv_data if row['test_score'] > 0]
        ai_scores = [row['ai_score'] for row in csv_data if row['ai_score'] > 0]
        final_scores = [row['final_score'] for row in csv_data]
        
        return {
            'total_submissions': total_submissions,
            'avg_test_score': round(sum(test_scores) / len(test_scores), 2) if test_scores else 0,
            'avg_ai_score': round(sum(ai_scores) / len(ai_scores), 2) if ai_scores else 0,
            'avg_final_score': round(sum(final_scores) / len(final_scores), 2),
            'min_final_score': round(min(final_scores), 2),
            'max_final_score': round(max(final_scores), 2),
            'passing_rate': round(sum(1 for score in final_scores if score >= 6.0) / total_submissions * 100, 1),
            'excellent_rate': round(sum(1 for score in final_scores if score >= 9.0) / total_submissions * 100, 1)
        } 