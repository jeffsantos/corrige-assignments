"""
Utilitário para gerar relatórios em diferentes formatos.
"""
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from ..domain.models import CorrectionReport, Submission


class ReportGenerator:
    """Gerador de relatórios em diferentes formatos."""
    
    def __init__(self):
        self.console = Console()
    
    def generate_console_report(self, report: CorrectionReport):
        """Gera relatório para console usando Rich."""
        # Título
        self.console.print(Panel(
            f"[bold blue]Relatório de Correção[/bold blue]\n"
            f"Assignment: {report.assignment_name}\n"
            f"Turma: {report.turma}\n"
            f"Gerado em: {report.generated_at}",
            title="📊 Sistema de Correção Automática"
        ))
        
        # Resumo estatístico
        if report.summary:
            summary_table = Table(title="📈 Resumo Estatístico")
            summary_table.add_column("Métrica", style="cyan")
            summary_table.add_column("Valor", style="magenta")
            
            summary_table.add_row("Total de Submissões", str(report.summary["total_submissions"]))
            summary_table.add_row("Nota Média", f"{report.summary['average_score']:.2f}")
            summary_table.add_row("Nota Mínima", f"{report.summary['min_score']:.2f}")
            summary_table.add_row("Nota Máxima", f"{report.summary['max_score']:.2f}")
            summary_table.add_row("Taxa de Aprovação", f"{report.summary['passing_rate']:.1%}")
            summary_table.add_row("Taxa de Excelência", f"{report.summary['excellent_rate']:.1%}")
            
            self.console.print(summary_table)
        
        # Tabela de resultados
        results_table = Table(title="📋 Resultados por Submissão")
        results_table.add_column("Submissão", style="cyan")
        results_table.add_column("Nota Final", style="green")
        results_table.add_column("Status", style="yellow")
        results_table.add_column("Testes", style="blue")
        
        for submission in sorted(report.submissions, key=lambda x: x.final_score, reverse=True):
            # Determina status baseado na nota
            if submission.final_score >= 9.0:
                status = "🟢 Excelente"
            elif submission.final_score >= 7.0:
                status = "🟡 Bom"
            elif submission.final_score >= 6.0:
                status = "🟠 Aprovado"
            else:
                status = "🔴 Reprovado"
            
            # Informações dos testes
            test_info = "N/A"
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                test_info = f"{passed}/{total}"
            
            results_table.add_row(
                submission.display_name,
                f"{submission.final_score:.1f}",
                status,
                test_info
            )
        
        self.console.print(results_table)
        
        # Detalhes por submissão
        self.console.print("\n[bold]📝 Detalhes por Submissão:[/bold]")
        for submission in report.submissions:
            # Constrói detalhes dos testes
            test_details = self._build_test_details(submission.test_results)
            
            self.console.print(Panel(
                f"[bold]{submission.display_name}[/bold]\n"
                f"Nota: {submission.final_score:.1f}/10\n\n"
                f"[bold cyan]🧪 Resultados dos Testes:[/bold cyan]\n{test_details}\n\n"
                f"[dim]{submission.feedback}[/dim]",
                title=f"👤 {submission.display_name}",
                border_style="green" if submission.final_score >= 7.0 else "red"
            ))
    
    def generate_html_report(self, report: CorrectionReport, output_path: Path):
        """Gera relatório em HTML."""
        html_content = self._build_html_content(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_markdown_report(self, report: CorrectionReport, output_path: Path):
        """Gera relatório em Markdown."""
        md_content = self._build_markdown_content(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def generate_csv_export(self, reports: List[CorrectionReport], output_path: Path) -> None:
        """Gera arquivo CSV com dados de múltiplos relatórios."""
        import csv
        
        # Converte todos os relatórios para dados CSV
        all_csv_data = []
        for report in reports:
            csv_data = self._convert_report_to_csv_data(report)
            all_csv_data.extend(csv_data)
        
        if not all_csv_data:
            raise ValueError("Nenhum dado para exportar")
        
        # Define campos do CSV
        fieldnames = [
            'assignment_name', 'turma', 'submission_identifier', 'submission_type',
            'test_score', 'ai_score', 'final_score', 'status',
            'tests_passed', 'tests_total', 'generated_at'
        ]
        
        # Cria diretório de saída se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escreve arquivo CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Escreve cabeçalho
            writer.writeheader()
            
            # Escreve dados
            writer.writerows(all_csv_data)
    
    def _convert_report_to_csv_data(self, report: CorrectionReport) -> List[Dict]:
        """Converte um relatório para dados CSV."""
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
            from ..domain.models import IndividualSubmission, GroupSubmission
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
    
    def _build_html_content(self, report: CorrectionReport) -> str:
        """Constrói conteúdo HTML do relatório."""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Correção - {report.assignment_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .results-table th {{ background-color: #f2f2f2; }}
        .excellent {{ background-color: #d4edda; }}
        .good {{ background-color: #d1ecf1; }}
        .pass {{ background-color: #fff3cd; }}
        .fail {{ background-color: #f8d7da; }}
        .student-detail {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .test-passed {{ color: #155724; background-color: #d4edda; padding: 5px; margin: 2px 0; border-radius: 3px; }}
        .test-failed {{ color: #721c24; background-color: #f8d7da; padding: 5px; margin: 2px 0; border-radius: 3px; }}
        .test-error {{ color: #856404; background-color: #fff3cd; padding: 5px; margin: 2px 0; border-radius: 3px; }}
        .test-skipped {{ color: #0c5460; background-color: #d1ecf1; padding: 5px; margin: 2px 0; border-radius: 3px; }}
        .feedback-pre {{ 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            overflow-wrap: break-word; 
            max-width: 100%; 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-radius: 5px; 
            border: 1px solid #dee2e6; 
            font-family: monospace; 
            font-size: 12px; 
            line-height: 1.4; 
        }}
        .score-breakdown {{ 
            display: flex; 
            gap: 20px; 
            margin: 10px 0; 
            flex-wrap: wrap; 
        }}
        .score-item {{ 
            background-color: #e9ecef; 
            padding: 8px 12px; 
            border-radius: 4px; 
            font-weight: bold; 
        }}
        .test-score {{ color: #0066cc; }}
        .ai-score {{ color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Relatório de Correção Automática</h1>
        <p><strong>Assignment:</strong> {report.assignment_name}</p>
        <p><strong>Turma:</strong> {report.turma}</p>
        <p><strong>Gerado em:</strong> {report.generated_at}</p>
    </div>
    
    <div class="summary">
        <h2>📈 Resumo Estatístico</h2>
        <p><strong>Total de Submissões:</strong> {report.summary.get('total_submissions', 0)}</p>
        <p><strong>Nota Média:</strong> {report.summary.get('average_score', 0):.2f}</p>
        <p><strong>Nota Mínima:</strong> {report.summary.get('min_score', 0):.2f}</p>
        <p><strong>Nota Máxima:</strong> {report.summary.get('max_score', 0):.2f}</p>
        <p><strong>Taxa de Aprovação:</strong> {report.summary.get('passing_rate', 0):.1%}</p>
        <p><strong>Taxa de Excelência:</strong> {report.summary.get('excellent_rate', 0):.1%}</p>
    </div>
    
    <h2>📋 Resultados por Submissão</h2>
    <table class="results-table">
        <thead>
            <tr>
                <th>Submissão</th>
                <th>Nota Testes</th>
                <th>Nota IA</th>
                <th>Status</th>
                <th>Testes</th>
            </tr>
        </thead>
        <tbody>
            {self._build_html_table_rows(report.submissions)}
        </tbody>
    </table>
    
    <h2>📝 Detalhes por Submissão</h2>
    {self._build_html_student_details(report.submissions)}
</body>
</html>
"""
    
    def _build_html_table_rows(self, submissions: List[Submission]) -> str:
        """Constrói linhas da tabela HTML."""
        rows = []
        for submission in sorted(submissions, key=lambda x: x.final_score, reverse=True):
            if submission.final_score >= 9.0:
                status = "🟢 Excelente"
                css_class = "excellent"
            elif submission.final_score >= 7.0:
                status = "🟡 Bom"
                css_class = "good"
            elif submission.final_score >= 6.0:
                status = "🟠 Aprovado"
                css_class = "pass"
            else:
                status = "🔴 Reprovado"
                css_class = "fail"
            
            # Calcula nota dos testes
            test_score = 0.0
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                if total > 0:
                    test_score = (passed / total) * 10.0
            
            # Calcula nota da IA
            ai_score = 0.0
            if hasattr(submission, 'code_analysis') and submission.code_analysis:
                ai_score = submission.code_analysis.score
            elif hasattr(submission, 'html_analysis') and submission.html_analysis:
                ai_score = submission.html_analysis.score
            
            # Simplifica o nome da submissão (remove "(individual)" e "(grupo)")
            display_name = submission.display_name
            if " (individual)" in display_name:
                display_name = display_name.replace(" (individual)", "")
            elif " (grupo)" in display_name:
                display_name = display_name.replace(" (grupo)", "")
            
            test_info = "N/A"
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                test_info = f"{passed}/{total}"
            
            rows.append(f"""
            <tr class="{css_class}">
                <td>{display_name}</td>
                <td>{test_score:.1f}</td>
                <td>{ai_score:.1f}</td>
                <td>{status}</td>
                <td>{test_info}</td>
            </tr>
            """)
        
        return "".join(rows)
    
    def _build_html_student_details(self, submissions: List[Submission]) -> str:
        """Constrói detalhes dos alunos em HTML."""
        details = []
        for submission in submissions:
            # Constrói detalhes dos testes
            test_details_html = self._build_html_test_details(submission.test_results)
            
            # Calcula nota dos testes
            test_score = 0.0
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                if total > 0:
                    test_score = (passed / total) * 10.0
            
            # Calcula nota da IA
            ai_score = 0.0
            if hasattr(submission, 'code_analysis') and submission.code_analysis:
                ai_score = submission.code_analysis.score
            elif hasattr(submission, 'html_analysis') and submission.html_analysis:
                ai_score = submission.html_analysis.score
            
            # Simplifica o nome da submissão (remove "(individual)" e "(grupo)")
            display_name = submission.display_name
            if " (individual)" in display_name:
                display_name = display_name.replace(" (individual)", "")
            elif " (grupo)" in display_name:
                display_name = display_name.replace(" (grupo)", "")
            
            details.append(f"""
            <div class="student-detail">
                <h3>👤 {display_name}</h3>
                
                <div class="score-breakdown">
                    <div class="score-item test-score">🧪 Nota Testes: {test_score:.1f}/10</div>
                    <div class="score-item ai-score">🤖 Nota IA: {ai_score:.1f}/10</div>
                </div>
                
                <h4>🧪 Resultados dos Testes:</h4>
                {test_details_html}
                
                <h4>📝 Feedback:</h4>
                <pre class="feedback-pre">{submission.feedback}</pre>
            </div>
            """)
        
        return "".join(details)
    
    def _build_html_test_details(self, test_results: List) -> str:
        """Constrói detalhes dos testes em HTML."""
        if not test_results:
            return "<p>Nenhum teste executado</p>"
        
        details = []
        for test in test_results:
            if test.result.value == "passed":
                status_icon = "✅"
                status_class = "test-passed"
            elif test.result.value == "failed":
                status_icon = "❌"
                status_class = "test-failed"
            elif test.result.value == "error":
                status_icon = "⚠️"
                status_class = "test-error"
            else:
                status_icon = "⏭️"
                status_class = "test-skipped"
            
            time_info = ""
            if hasattr(test, 'execution_time') and test.execution_time > 0:
                time_info = f" ({test.execution_time:.2f}s)"
            
            details.append(f'<p class="{status_class}">{status_icon} <strong>{test.test_name}</strong>{time_info}</p>')
        
        return "".join(details)
    
    def _build_markdown_content(self, report: CorrectionReport) -> str:
        """Constrói conteúdo Markdown do relatório."""
        content = f"""# 📊 Relatório de Correção Automática

**Assignment:** {report.assignment_name}  
**Turma:** {report.turma}  
**Gerado em:** {report.generated_at}

## 📈 Resumo Estatístico

- **Total de Submissões:** {report.summary.get('total_submissions', 0)}
- **Nota Média:** {report.summary.get('average_score', 0):.2f}
- **Nota Mínima:** {report.summary.get('min_score', 0):.2f}
- **Nota Máxima:** {report.summary.get('max_score', 0):.2f}
- **Taxa de Aprovação:** {report.summary.get('passing_rate', 0):.1%}
- **Taxa de Excelência:** {report.summary.get('excellent_rate', 0):.1%}

## 📋 Resultados por Submissão

| Submissão | Nota Testes | Nota IA | Status | Testes |
|-------|------------|--------|--------|--------|
"""
        
        # Adiciona linhas da tabela
        for submission in sorted(report.submissions, key=lambda x: x.final_score, reverse=True):
            if submission.final_score >= 9.0:
                status = "🟢 Excelente"
            elif submission.final_score >= 7.0:
                status = "🟡 Bom"
            elif submission.final_score >= 6.0:
                status = "🟠 Aprovado"
            else:
                status = "🔴 Reprovado"
            
            # Calcula nota dos testes
            test_score = 0.0
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                if total > 0:
                    test_score = (passed / total) * 10.0
            
            # Calcula nota da IA
            ai_score = 0.0
            if hasattr(submission, 'code_analysis') and submission.code_analysis:
                ai_score = submission.code_analysis.score
            elif hasattr(submission, 'html_analysis') and submission.html_analysis:
                ai_score = submission.html_analysis.score
            
            # Simplifica o nome da submissão (remove "(individual)" e "(grupo)")
            display_name = submission.display_name
            if " (individual)" in display_name:
                display_name = display_name.replace(" (individual)", "")
            elif " (grupo)" in display_name:
                display_name = display_name.replace(" (grupo)", "")
            
            test_info = "N/A"
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                test_info = f"{passed}/{total}"
            
            content += f"| {display_name} | {test_score:.1f} | {ai_score:.1f} | {status} | {test_info} |\n"
        
        content += "\n## 📝 Detalhes por Submissão\n\n"
        
        # Adiciona detalhes dos alunos
        for submission in report.submissions:
            # Constrói detalhes dos testes
            test_details_md = self._build_markdown_test_details(submission.test_results)
            
            # Calcula nota dos testes
            test_score = 0.0
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                if total > 0:
                    test_score = (passed / total) * 10.0
            
            # Calcula nota da IA
            ai_score = 0.0
            if hasattr(submission, 'code_analysis') and submission.code_analysis:
                ai_score = submission.code_analysis.score
            elif hasattr(submission, 'html_analysis') and submission.html_analysis:
                ai_score = submission.html_analysis.score
            
            # Simplifica o nome da submissão (remove "(individual)" e "(grupo)")
            display_name = submission.display_name
            if " (individual)" in display_name:
                display_name = display_name.replace(" (individual)", "")
            elif " (grupo)" in display_name:
                display_name = display_name.replace(" (grupo)", "")
            
            content += f"""### 👤 {display_name}

**🧪 Nota Testes:** {test_score:.1f}/10  
**🤖 Nota IA:** {ai_score:.1f}/10

#### 🧪 Resultados dos Testes

{test_details_md}

#### 📝 Feedback

```
{submission.feedback}
```

---
"""
        
        return content
    
    def _build_markdown_test_details(self, test_results: List) -> str:
        """Constrói detalhes dos testes em Markdown."""
        if not test_results:
            return "Nenhum teste executado"
        
        details = []
        for test in test_results:
            if test.result.value == "passed":
                status_icon = "✅"
            elif test.result.value == "failed":
                status_icon = "❌"
            elif test.result.value == "error":
                status_icon = "⚠️"
            else:
                status_icon = "⏭️"
            
            time_info = ""
            if hasattr(test, 'execution_time') and test.execution_time > 0:
                time_info = f" ({test.execution_time:.2f}s)"
            
            details.append(f"- {status_icon} **{test.test_name}**{time_info}")
        
        return "\n".join(details)
    
    def _build_test_details(self, test_results: List) -> str:
        """Constrói detalhes dos testes para exibição."""
        if not test_results:
            return "Nenhum teste executado"
        
        details = []
        for test in test_results:
            if test.result.value == "passed":
                status_icon = "✅"
                status_color = "green"
            elif test.result.value == "failed":
                status_icon = "❌"
                status_color = "red"
            elif test.result.value == "error":
                status_icon = "⚠️"
                status_color = "yellow"
            else:
                status_icon = "⏭️"
                status_color = "blue"
            
            details.append(f"{status_icon} [bold {status_color}]{test.test_name}[/bold {status_color}]")
            
            # Adiciona tempo de execução se disponível
            if hasattr(test, 'execution_time') and test.execution_time > 0:
                details[-1] += f" ({test.execution_time:.2f}s)"
        
        return "\n".join(details) 