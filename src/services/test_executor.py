"""
Serviço para executar testes Python usando pytest.
"""
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List
from ..domain.models import TestExecution, TestResult


class TestExecutor:
    """Serviço para executar testes Python."""
    
    def __init__(self):
        pass
    
    def run_tests(self, submission_path: Path, test_files: List[str]) -> List[TestExecution]:
        """Executa testes em uma submissão."""
        results = []
        
        # Cria um diretório temporário para executar os testes
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copia os arquivos da submissão para o diretório temporário
            self._copy_submission_files(submission_path, temp_path)
            
            # Executa cada arquivo de teste
            for test_file in test_files:
                test_result = self._run_single_test(temp_path, test_file)
                if test_result:
                    results.append(test_result)
        
        return results
    
    def _copy_submission_files(self, source_path: Path, dest_path: Path):
        """Copia arquivos da submissão para o diretório temporário."""
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, dest_path)
            elif item.is_dir():
                shutil.copytree(item, dest_path / item.name)
    
    def _run_single_test(self, test_path: Path, test_file: str) -> TestExecution:
        """Executa um arquivo de teste específico."""
        test_file_path = test_path / test_file
        
        if not test_file_path.exists():
            return TestExecution(
                test_name=test_file,
                result=TestResult.ERROR,
                message=f"Arquivo de teste não encontrado: {test_file}"
            )
        
        try:
            # Executa o teste usando pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=test_path,
                timeout=30  # Timeout de 30 segundos
            )
            
            # Analisa o resultado
            if result.returncode == 0:
                return TestExecution(
                    test_name=test_file,
                    result=TestResult.PASSED,
                    message="Todos os testes passaram"
                )
            else:
                return TestExecution(
                    test_name=test_file,
                    result=TestResult.FAILED,
                    message=result.stdout + result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return TestExecution(
                test_name=test_file,
                result=TestResult.ERROR,
                message="Timeout na execução do teste"
            )
        except Exception as e:
            return TestExecution(
                test_name=test_file,
                result=TestResult.ERROR,
                message=f"Erro na execução: {str(e)}"
            )
    
    def run_specific_test(self, submission_path: Path, test_file: str) -> TestExecution:
        """Executa um teste específico."""
        results = self.run_tests(submission_path, [test_file])
        return results[0] if results else TestExecution(
            test_name=test_file,
            result=TestResult.ERROR,
            message="Nenhum resultado obtido"
        ) 