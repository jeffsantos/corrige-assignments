"""
Serviço para executar código Python de terminal e capturar output.
"""
import os
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import psutil

from ..domain.models import PythonExecutionResult
from config import TEST_TIMEOUT, MAX_TEST_OUTPUT


class PythonExecutionService:
    """Serviço para executar código Python de terminal e capturar output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def _debug_print(self, message: str):
        """Imprime mensagem de debug apenas se verbose estiver habilitado."""
        if self.verbose:
            print(message)
    
    def execute_python_for_assignment(self, assignment_name: str, turma_name: str, 
                                    submissions: List) -> List[PythonExecutionResult]:
        """Executa código Python para todas as submissões de um assignment."""
        print(f"Executando código Python para {assignment_name} da turma {turma_name}")
        
        # Instala dependências fundamentais uma única vez para toda a execução
        if submissions:
            first_submission_path = submissions[0].submission_path.parent
            self._debug_print(f"Instalando dependências fundamentais uma única vez...")
            self._install_fundamental_dependencies(first_submission_path)
        
        results = []
        
        for submission in submissions:
            try:
                print(f"Executando código Python para {submission.display_name} ({'grupo' if hasattr(submission, 'group_name') else 'individual'})...")
                result = self._execute_submission_python(submission, assignment_name, turma_name)
                results.append(result)
            except Exception as e:
                print(f"Erro ao executar código Python para {submission.display_name}: {e}")
                # Identificador da submissão
                identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
                # Cria resultado de erro
                result = PythonExecutionResult(
                    submission_identifier=identifier,
                    display_name=submission.display_name,
                    execution_timestamp=datetime.now().isoformat(),
                    execution_status="error",
                    stdout_output="",
                    stderr_output="",
                    return_code=-1,
                    execution_time=0.0,
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    def _execute_submission_python(self, submission, assignment_name: str, 
                                 turma_name: str) -> PythonExecutionResult:
        """Executa código Python de uma submissão específica."""
        # Encontra o arquivo main.py da submissão
        main_file = submission.submission_path / "main.py"
        if not main_file.exists():
            raise FileNotFoundError(f"Arquivo main.py não encontrado em {submission.submission_path}")
        
        # Identificador da submissão
        identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
        
        self._debug_print(f"  [DEBUG] Executando main.py para {identifier}")
        
        # Executa o código Python
        start_time = time.time()
        
        try:
            # Limpa cache Python para garantir execução limpa
            self._clear_python_cache(submission.submission_path)
            
            # Executa o código Python
            result = self._run_python_code(main_file)
            
            execution_time = time.time() - start_time
            
            self._debug_print(f"  [DEBUG] Execução concluída para {identifier} em {execution_time:.2f}s")
            
            return PythonExecutionResult(
                submission_identifier=identifier,
                display_name=submission.display_name,
                execution_timestamp=datetime.now().isoformat(),
                execution_status="success",
                stdout_output=result['stdout'],
                stderr_output=result['stderr'],
                return_code=result['return_code'],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._debug_print(f"  [DEBUG] Erro na execução: {e}")
            
            # Verifica se é erro de importação e tenta instalar dependências
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['module', 'import', 'no module named']):
                self._debug_print(f"  [DEBUG] Detectado erro de importação, tentando instalar dependências...")
                self._install_common_dependencies(main_file.parent)
                
                # Tenta novamente após instalar dependências
                self._debug_print(f"  [DEBUG] Tentando novamente após instalar dependências...")
                try:
                    result = self._run_python_code(main_file)
                    execution_time = time.time() - start_time
                    
                    self._debug_print(f"  [DEBUG] Execução bem-sucedida após instalar dependências")
                    return PythonExecutionResult(
                        submission_identifier=identifier,
                        display_name=submission.display_name,
                        execution_timestamp=datetime.now().isoformat(),
                        execution_status="success",
                        stdout_output=result['stdout'],
                        stderr_output=result['stderr'],
                        return_code=result['return_code'],
                        execution_time=execution_time
                    )
                except Exception as retry_exc:
                    self._debug_print(f"  [DEBUG] Falha na segunda tentativa: {retry_exc}")
                    return PythonExecutionResult(
                        submission_identifier=identifier,
                        display_name=submission.display_name,
                        execution_timestamp=datetime.now().isoformat(),
                        execution_status="error",
                        stdout_output="",
                        stderr_output="",
                        return_code=-1,
                        execution_time=execution_time,
                        error_message=str(retry_exc)
                    )
            
            raise e
    
    def _run_python_code(self, main_file: Path) -> Dict[str, Any]:
        """Executa código Python e captura output."""
        cmd = [
            "pipenv", "run", "python", "main.py"
        ]
        
        self._debug_print(f"  [DEBUG] Executando comando: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=main_file.parent,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            # Aguarda execução com timeout
            stdout, stderr = process.communicate(timeout=TEST_TIMEOUT)
            
            # Limita tamanho do output para evitar problemas
            if len(stdout) > MAX_TEST_OUTPUT:
                stdout = stdout[:MAX_TEST_OUTPUT] + "\n... (output truncado)"
            if len(stderr) > MAX_TEST_OUTPUT:
                stderr = stderr[:MAX_TEST_OUTPUT] + "\n... (output truncado)"
            
            return {
                'stdout': stdout,
                'stderr': stderr,
                'return_code': process.returncode
            }
            
        except subprocess.TimeoutExpired:
            self._debug_print(f"  [DEBUG] Timeout na execução, terminando processo...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            
            return {
                'stdout': "",
                'stderr': f"Timeout: execução excedeu {TEST_TIMEOUT} segundos",
                'return_code': -1
            }
        
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na execução: {e}")
            # Tenta terminar o processo se ainda estiver rodando
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except:
                pass
            
            raise e
    
    def _clear_python_cache(self, submission_path: Path):
        """Limpa cache Python para garantir execução limpa."""
        try:
            # Remove diretórios de cache Python
            cache_dirs = [
                submission_path / "__pycache__",
                submission_path / ".pytest_cache"
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    import shutil
                    shutil.rmtree(cache_dir)
                    self._debug_print(f"  [DEBUG] Cache removido: {cache_dir}")
                    
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro ao limpar cache: {e}")
    
    def _install_fundamental_dependencies(self, submission_path: Path):
        """Instala dependências fundamentais necessárias para execução das submissões."""
        fundamental_deps = [
            "requests",
            "beautifulsoup4",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "lxml",
            "selenium",
            "webdriver-manager",
            "sqlalchemy",
            "psycopg2-binary",
            "python-dotenv"
        ]
        
        self._debug_print(f"  [DEBUG] Instalando dependências fundamentais...")
        
        for dep in fundamental_deps:
            try:
                # Usa pipenv run pip install para instalar no ambiente correto
                result = subprocess.run(
                    ["pipenv", "run", "pip", "install", dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60  # Timeout maior para instalações
                )
                if result.returncode == 0:
                    self._debug_print(f"  [DEBUG] Instalado: {dep}")
                else:
                    self._debug_print(f"  [DEBUG] Falha ao instalar {dep}: {result.stderr.decode()}")
            except Exception as e:
                self._debug_print(f"  [DEBUG] Falha ao instalar {dep}: {e}")
                continue
    
    def _install_common_dependencies(self, submission_path: Path):
        """Instala dependências comuns que podem estar faltando."""
        common_deps = [
            "requests",
            "beautifulsoup4",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "lxml",
            "selenium",
            "webdriver-manager",
            "sqlalchemy",
            "psycopg2-binary",
            "python-dotenv"
        ]
        
        self._debug_print(f"  [DEBUG] Tentando instalar dependências comuns...")
        
        for dep in common_deps:
            try:
                # Usa pipenv run pip install para instalar no ambiente correto
                result = subprocess.run(
                    ["pipenv", "run", "pip", "install", dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30
                )
                if result.returncode == 0:
                    self._debug_print(f"  [DEBUG] Instalado: {dep}")
                else:
                    self._debug_print(f"  [DEBUG] Falha ao instalar {dep}: {result.stderr.decode()}")
            except Exception as e:
                self._debug_print(f"  [DEBUG] Falha ao instalar {dep}: {e}")
                continue 