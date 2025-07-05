"""
Serviço para executar programas Python interativos com entrada simulada.
MVP: Implementação específica para prog1-tarefa-scrap-yahoo
"""
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..domain.models import PythonExecutionResult


class InteractiveExecutionService:
    """Serviço para executar programas Python interativos."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
        # Configuração hardcoded para MVP (prog1-tarefa-scrap-yahoo)
        self.interactive_config = {
            "prog1-tarefa-scrap-yahoo": {
                "command_args": ["VALE"],
                "inputs": [
                    "2024-01-01",  # Data inicial
                    "2024-01-31"   # Data final
                ],
                "timeout": 30,
                "expected_outputs": ["vale", "ações", "data", "início", "fim"]
            }
        }
    
    def _debug_print(self, message: str):
        """Imprime mensagem de debug apenas se verbose estiver habilitado."""
        if self.verbose:
            print(f"  [DEBUG] {message}")
    
    def execute_interactive_program(self, assignment_name: str, submission_path: Path) -> PythonExecutionResult:
        """Executa programa interativo com entrada simulada."""
        
        # Verifica se é um assignment interativo
        if assignment_name not in self.interactive_config:
            raise ValueError(f"Assignment '{assignment_name}' não configurado para execução interativa")
        
        config = self.interactive_config[assignment_name]
        
        # Encontra o arquivo main.py
        main_file = submission_path / "main.py"
        if not main_file.exists():
            raise FileNotFoundError(f"Arquivo main.py não encontrado em {submission_path}")
        
        self._debug_print(f"Executando programa interativo: {assignment_name}")
        self._debug_print(f"Argumentos: {config['command_args']}")
        self._debug_print(f"Inputs: {config['inputs']}")
        
        # Executa o programa interativo
        start_time = time.time()
        
        try:
            result = self._run_interactive_program(
                main_file, 
                config['command_args'], 
                config['inputs'], 
                config['timeout']
            )
            
            execution_time = time.time() - start_time
            
            # Analisa o resultado
            success = self._analyze_execution_result(result, config)
            
            return PythonExecutionResult(
                submission_identifier="interactive_test",
                display_name=f"{assignment_name}_interactive",
                execution_timestamp=datetime.now().isoformat(),
                execution_status="success" if success else "partial_success",
                stdout_output=result['stdout'],
                stderr_output=result['stderr'],
                return_code=result['return_code'],
                execution_time=execution_time,
                error_message="" if success else "Execução interativa não produziu resultado esperado"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._debug_print(f"Erro na execução interativa: {e}")
            
            return PythonExecutionResult(
                submission_identifier="interactive_test",
                display_name=f"{assignment_name}_interactive",
                execution_timestamp=datetime.now().isoformat(),
                execution_status="error",
                stdout_output="",
                stderr_output="",
                return_code=-1,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _run_interactive_program(self, main_file: Path, args: List[str], inputs: List[str], timeout: int) -> Dict:
        """Executa programa interativo com entrada simulada."""
        
        # Monta comando com argumentos
        cmd = ["pipenv", "run", "python", "main.py"] + args
        
        self._debug_print(f"Executando comando: {' '.join(cmd)}")
        self._debug_print(f"Diretório: {main_file.parent}")
        
        # Inicia processo
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=main_file.parent,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            # Envia inputs com delay para simular usuário real
            self._send_inputs(process, inputs)
            
            # Captura saída com timeout
            stdout, stderr = process.communicate(timeout=timeout)
            
            self._debug_print(f"Processo finalizado com código: {process.returncode}")
            self._debug_print(f"STDOUT: {stdout[:200]}...")
            self._debug_print(f"STDERR: {stderr[:200]}...")
            
            return {
                'stdout': stdout,
                'stderr': stderr,
                'return_code': process.returncode
            }
            
        except subprocess.TimeoutExpired:
            self._debug_print(f"Timeout na execução ({timeout}s), terminando processo...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            
            return {
                'stdout': "",
                'stderr': f"Timeout: execução excedeu {timeout} segundos",
                'return_code': -1
            }
        
        except Exception as e:
            self._debug_print(f"Erro na execução: {e}")
            # Tenta terminar o processo se ainda estiver rodando
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except:
                pass
            
            raise e
    
    def _send_inputs(self, process: subprocess.Popen, inputs: List[str]):
        """Envia inputs para o processo com delay realista."""
        
        for i, input_text in enumerate(inputs):
            # Aguarda um pouco para simular usuário real
            time.sleep(0.5)
            
            self._debug_print(f"Enviando input {i+1}: '{input_text}'")
            
            try:
                # Envia input com quebra de linha
                process.stdin.write(input_text + "\n")
                process.stdin.flush()
            except Exception as e:
                self._debug_print(f"Erro ao enviar input {i+1}: {e}")
                break
    
    def _analyze_execution_result(self, result: Dict, config: Dict) -> bool:
        """Analisa se a execução foi bem-sucedida."""
        
        stdout = result['stdout'].lower()
        stderr = result['stderr'].lower()
        
        # Verifica se há saída
        if not stdout.strip():
            self._debug_print("Nenhuma saída detectada")
            return False
        
        # Verifica se há erros críticos
        error_keywords = ['error', 'exception', 'traceback', 'failed']
        if any(keyword in stderr for keyword in error_keywords):
            self._debug_print(f"Erros detectados: {stderr}")
            return False
        
        # Verifica se contém outputs esperados
        expected_outputs = [output.lower() for output in config['expected_outputs']]
        found_outputs = sum(1 for expected in expected_outputs if expected in stdout)
        
        self._debug_print(f"Outputs esperados encontrados: {found_outputs}/{len(expected_outputs)}")
        
        # Considera sucesso se pelo menos 50% dos outputs esperados foram encontrados
        success_rate = found_outputs / len(expected_outputs)
        success = success_rate >= 0.5
        
        self._debug_print(f"Taxa de sucesso: {success_rate:.2f} ({'SUCESSO' if success else 'FALHA'})")
        
        return success 