"""
Serviço para executar testes Python usando pytest.
"""
import subprocess
import sys
import json
from pathlib import Path
from typing import List
from ..domain.models import AssignmentTestExecution, AssignmentTestResult


class PytestExecutor:
    """Serviço para executar testes Python."""
    
    def __init__(self):
        pass
    
    def run_tests(self, submission_path: Path, test_files: List[str]) -> List[AssignmentTestExecution]:
        """Executa testes em uma submissão diretamente na pasta do aluno, detalhando cada função de teste."""
        results = []
        
        # Remove .report.json antigo, se existir
        report_json = submission_path / ".report.json"
        if report_json.exists():
            report_json.unlink()
        
        # Executa pytest com --json-report usando caminhos relativos
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--tb=short", "--json-report"] + test_files,
                capture_output=True,
                text=True,
                cwd=submission_path,
                timeout=60
            )
        except Exception as e:
            return [AssignmentTestExecution(test_name="pytest", result=AssignmentTestResult.ERROR, message=f"Erro ao rodar pytest: {e}")]
        
        # Lê o .report.json (com ponto no início)
        if not report_json.exists():
            # Fallback: não gerou .report.json, retorna erro genérico
            return [AssignmentTestExecution(test_name="pytest", result=AssignmentTestResult.ERROR, message="pytest não gerou .report.json. STDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr)]
        
        with open(report_json, encoding="utf-8") as f:
            report = json.load(f)
        
        # Extrai resultados detalhados
        for test in report.get("tests", []):
            name = test.get("nodeid", "?")
            outcome = test.get("outcome", "error")
            duration = test.get("duration", 0.0)
            message = test.get("longrepr", "") or test.get("call", {}).get("crash", {}).get("message", "")
            if outcome == "passed":
                result_enum = AssignmentTestResult.PASSED
            elif outcome == "failed":
                result_enum = AssignmentTestResult.FAILED
            elif outcome == "skipped":
                result_enum = AssignmentTestResult.SKIPPED
            else:
                result_enum = AssignmentTestResult.ERROR
            results.append(AssignmentTestExecution(
                test_name=name,
                result=result_enum,
                message=message,
                execution_time=duration
            ))
        
        # Se não houver testes, retorna erro
        if not results:
            results.append(AssignmentTestExecution(test_name="pytest", result=AssignmentTestResult.ERROR, message="Nenhum teste encontrado ou erro na execução."))
        
        return results
    
    def run_specific_test(self, submission_path: Path, test_file: str) -> AssignmentTestExecution:
        """Executa um teste específico."""
        results = self.run_tests(submission_path, [test_file])
        return results[0] if results else AssignmentTestExecution(
            test_name=test_file,
            result=AssignmentTestResult.ERROR,
            message="Nenhum resultado obtido"
        ) 