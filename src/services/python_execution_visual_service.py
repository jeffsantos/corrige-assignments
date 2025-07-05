"""
Serviço para gerar relatórios visuais da execução de programas Python.
"""
import html
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from ..domain.models import Submission, PythonExecutionResult


class PythonExecutionVisualService:
    """Serviço para gerar relatórios visuais de execução Python."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def generate_execution_visual_report(self, assignment_name: str, turma_name: str,
                                       submissions: List[Submission],
                                       output_dir: Path) -> Path:
        """Gera relatório visual HTML com saídas de execução Python."""
        
        # Filtra submissões que têm execução Python
        submissions_with_execution = []
        for i, submission in enumerate(submissions):
            if hasattr(submission, 'python_execution') and submission.python_execution:
                submissions_with_execution.append({
                    'submission': submission,
                    'execution': submission.python_execution,
                    'index': i + 1
                })
        
        if not submissions_with_execution:
            raise ValueError("Nenhuma submissão com execução Python encontrada")
        
        # Calcula estatísticas
        execution_stats = self._calculate_execution_stats(submissions_with_execution)
        
        # Gera HTML
        html_content = self._build_execution_visual_html(
            assignment_name, turma_name, submissions_with_execution, execution_stats
        )
        
        # Salva arquivo
        output_file = output_dir / f"{assignment_name}_{turma_name}_execution_visual.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _calculate_execution_stats(self, submissions_with_execution: List[Dict]) -> dict:
        """Calcula estatísticas das execuções."""
        total = len(submissions_with_execution)
        successful = sum(1 for item in submissions_with_execution 
                        if item['execution'].execution_status == "success")
        partial = sum(1 for item in submissions_with_execution 
                     if item['execution'].execution_status == "partial_success")
        failed = sum(1 for item in submissions_with_execution 
                    if item['execution'].execution_status == "error")
        
        avg_time = sum(item['execution'].execution_time for item in submissions_with_execution) / total if total > 0 else 0
        
        return {
            'total_executions': total,
            'successful_executions': successful,
            'partial_executions': partial,
            'failed_executions': failed,
            'success_rate': successful / total if total > 0 else 0,
            'avg_execution_time': avg_time
        }
    
    def _build_execution_visual_html(self, assignment_name: str, turma_name: str,
                                   submissions_with_execution: List[Dict],
                                   execution_stats: dict) -> str:
        """Constrói o HTML do relatório visual de execução."""
        
        # Gera cards de execução
        execution_cards_html = ""
        for item in submissions_with_execution:
            submission = item['submission']
            execution = item['execution']
            index = item['index']
            
            # Status da execução
            if execution.execution_status == "success":
                status_icon = "✅"
                status_text = "Sucesso"
                status_class = "success"
            elif execution.execution_status == "partial_success":
                status_icon = "⚠️"
                status_text = "Parcial"
                status_class = "partial"
            else:
                status_icon = "❌"
                status_text = "Erro"
                status_class = "error"
            
            # Formata saída para exibição
            stdout_formatted = self._format_output_for_display(execution.stdout_output)
            stderr_formatted = self._format_output_for_display(execution.stderr_output)
            
            execution_cards_html += f"""
            <div class="execution-card">
                <div class="execution-header">
                    <h3>#{index} - {submission.display_name}</h3>
                    <div class="execution-status {status_class}">
                        {status_icon} {status_text}
                    </div>
                </div>
                <div class="execution-info">
                    <div class="info-item">
                        <strong>Tempo:</strong> {execution.execution_time:.2f}s
                    </div>
                    <div class="info-item">
                        <strong>Código de retorno:</strong> {execution.return_code}
                    </div>
                    <div class="info-item">
                        <strong>Timestamp:</strong> {execution.execution_timestamp}
                    </div>
                </div>
                <div class="execution-output">
                    <div class="output-section">
                        <h4>📤 Saída Padrão (STDOUT)</h4>
                        <pre class="output-content">{stdout_formatted}</pre>
                    </div>
                    <div class="output-section">
                        <h4>📤 Saída de Erro (STDERR)</h4>
                        <pre class="output-content error-output">{stderr_formatted}</pre>
                    </div>
                </div>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Visual de Execução - {assignment_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .summary-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .summary-item h3 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 5px;
        }}
        
        .summary-item p {{
            color: #6c757d;
            font-weight: 500;
        }}
        
        .executions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
            gap: 25px;
            padding: 30px;
        }}
        
        .execution-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }}
        
        .execution-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .execution-header h3 {{
            color: #333;
            font-size: 1.2em;
        }}
        
        .execution-status {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .execution-status.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .execution-status.partial {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .execution-status.error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .execution-info {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .info-item {{
            margin-bottom: 5px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .execution-output {{
            padding: 20px;
        }}
        
        .output-section {{
            margin-bottom: 20px;
        }}
        
        .output-section h4 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 1em;
        }}
        
        .output-content {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.4;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .error-output {{
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            .executions-grid {{
                grid-template-columns: 1fr;
                padding: 15px;
            }}
            
            .execution-header {{
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐍 Relatório Visual de Execução Python</h1>
            <p>{assignment_name} - {turma_name}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Resumo das Execuções</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>{execution_stats['total_executions']}</h3>
                    <p>Total de Execuções</p>
                </div>
                <div class="summary-item">
                    <h3>{execution_stats['successful_executions']}</h3>
                    <p>Execuções Bem-sucedidas</p>
                </div>
                <div class="summary-item">
                    <h3>{execution_stats['partial_executions']}</h3>
                    <p>Execuções Parciais</p>
                </div>
                <div class="summary-item">
                    <h3>{execution_stats['failed_executions']}</h3>
                    <p>Execuções com Erro</p>
                </div>
                <div class="summary-item">
                    <h3>{execution_stats['success_rate']:.1%}</h3>
                    <p>Taxa de Sucesso</p>
                </div>
                <div class="summary-item">
                    <h3>{execution_stats['avg_execution_time']:.2f}s</h3>
                    <p>Tempo Médio</p>
                </div>
            </div>
        </div>
        
        <div class="executions-grid">
            {execution_cards_html}
        </div>
        
        <div class="footer">
            <p>Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _format_output_for_display(self, output: str) -> str:
        """Formata saída para exibição HTML."""
        if not output:
            return "Nenhuma saída"
        
        # Escapa caracteres HTML
        formatted = html.escape(output)
        
        # Limita tamanho se muito longo
        if len(formatted) > 2000:
            formatted = formatted[:2000] + "\n... (saída truncada)"
        
        return formatted 