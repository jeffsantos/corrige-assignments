"""
Serviço para gerar thumbnails de dashboards Streamlit.
"""
import os
import time
import subprocess
import threading
import socket
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..domain.models import ThumbnailResult
from config import STREAMLIT_STARTUP_TIMEOUT, SCREENSHOT_WAIT_TIME, CHROME_WINDOW_SIZE, STREAMLIT_PORT_RANGE


class StreamlitThumbnailService:
    """Serviço para gerar thumbnails de dashboards Streamlit."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("reports/visual/thumbnails")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_thumbnails_for_assignment(self, assignment_name: str, turma_name: str, 
                                         submissions: List) -> List[ThumbnailResult]:
        """Gera thumbnails para todas as submissões de um assignment."""
        results = []
        
        for submission in submissions:
            try:
                print(f"Gerando thumbnail para {submission.display_name}...")
                result = self._capture_submission_thumbnail(submission, assignment_name, turma_name)
                results.append(result)
            except Exception as e:
                print(f"Erro ao gerar thumbnail para {submission.display_name}: {e}")
                # Identificador da submissão
                identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
                # Cria resultado de erro
                result = ThumbnailResult(
                    submission_identifier=identifier,
                    display_name=submission.display_name,
                    thumbnail_path=Path(),
                    capture_timestamp=datetime.now().isoformat(),
                    streamlit_status="error",
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    def _capture_submission_thumbnail(self, submission, assignment_name: str, 
                                    turma_name: str) -> ThumbnailResult:
        """Captura thumbnail de uma submissão específica."""
        # Encontra o arquivo main.py da submissão
        main_file = submission.submission_path / "main.py"
        if not main_file.exists():
            raise FileNotFoundError(f"Arquivo main.py não encontrado em {submission.submission_path}")
        
        # Identificador da submissão
        identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
        
        # Encontra porta disponível
        port = self._find_available_port()
        
        print(f"  [DEBUG] Iniciando Streamlit na porta {port} para {identifier}")
        
        # Executa Streamlit em background
        process = self._start_streamlit(main_file, port)
        
        try:
            # Aguarda Streamlit inicializar e verifica saúde
            if not self._wait_for_streamlit_ready(port, identifier):
                raise RuntimeError("Streamlit não inicializou corretamente")
            
            # Captura screenshot
            thumbnail_path = self.output_dir / f"{identifier}_{assignment_name}.png"
            try:
                self._capture_screenshot(port, thumbnail_path)
                print(f"  [DEBUG] Screenshot capturado com sucesso para {identifier}")
            except Exception as screenshot_exc:
                print(f"  [DEBUG] Erro na captura de screenshot para {identifier}: {screenshot_exc}")
                # Loga stdout/stderr do processo Streamlit
                self._log_process_output(process, identifier)
                raise screenshot_exc
            
            return ThumbnailResult(
                submission_identifier=identifier,
                display_name=submission.display_name,
                thumbnail_path=thumbnail_path,
                capture_timestamp=datetime.now().isoformat(),
                streamlit_status="success"
            )
            
        except Exception as e:
            print(f"  [DEBUG] Erro na captura de thumbnail: {e}")
            
            # Verifica se é erro de importação e tenta instalar dependências
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['module', 'import', 'no module named']):
                print(f"  [DEBUG] Detectado erro de importação, tentando instalar dependências...")
                self._install_common_dependencies(main_file.parent)
                
                # Tenta novamente após instalar dependências
                print(f"  [DEBUG] Tentando novamente após instalar dependências...")
                process = self._start_streamlit(main_file, port)
                
                if not self._wait_for_streamlit_ready(port, identifier):
                    print(f"  [DEBUG] Streamlit ainda falhou após instalar dependências")
                    raise RuntimeError("Streamlit falhou mesmo após instalar dependências")
                
                # Tenta capturar screenshot novamente
                try:
                    self._capture_screenshot(port, thumbnail_path)
                    print(f"  [DEBUG] Screenshot capturado com sucesso após instalar dependências")
                    return ThumbnailResult(
                        submission_identifier=identifier,
                        display_name=submission.display_name,
                        thumbnail_path=thumbnail_path,
                        capture_timestamp=datetime.now().isoformat(),
                        streamlit_status="success"
                    )
                except Exception as retry_exc:
                    print(f"  [DEBUG] Falha na segunda tentativa: {retry_exc}")
                    raise retry_exc
                finally:
                    self._stop_streamlit(process)
            
            raise e
            
        finally:
            # Para o processo Streamlit e aguarda um pouco para garantir que a porta seja liberada
            self._stop_streamlit(process)
            time.sleep(2)  # Aguarda 2 segundos para liberar a porta
    
    def _wait_for_streamlit_ready(self, port: int, identifier: str) -> bool:
        """Aguarda Streamlit inicializar e verifica se está funcionando."""
        max_attempts = STREAMLIT_STARTUP_TIMEOUT // 2  # Tenta a cada 2 segundos
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Verifica se a porta está respondendo
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    print(f"  [DEBUG] Streamlit está respondendo na porta {port} para {identifier}")
                    return True
            except requests.RequestException:
                pass
            
            attempt += 1
            time.sleep(2)
            print(f"  [DEBUG] Tentativa {attempt}/{max_attempts} - aguardando Streamlit para {identifier}")
        
        print(f"  [DEBUG] Timeout aguardando Streamlit para {identifier}")
        return False
    
    def _log_process_output(self, process: subprocess.Popen, identifier: str):
        """Loga a saída do processo Streamlit para debug."""
        try:
            if process.stdout:
                out = process.stdout.read().decode(errors='ignore')
                if out.strip():
                    print(f"  [DEBUG] Streamlit stdout para {identifier}:\n{out}")
            if process.stderr:
                err = process.stderr.read().decode(errors='ignore')
                if err.strip():
                    print(f"  [DEBUG] Streamlit stderr para {identifier}:\n{err}")
        except Exception as e:
            print(f"  [DEBUG] Erro ao ler saída do processo: {e}")
    
    def _find_available_port(self) -> int:
        """Encontra uma porta disponível para o Streamlit."""
        start_port, end_port = STREAMLIT_PORT_RANGE
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    s.close()
                    # Testa novamente para garantir que a porta está realmente livre
                    time.sleep(0.1)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                        s2.bind(('localhost', port))
                        s2.close()
                    return port
            except OSError:
                continue
        raise RuntimeError("Nenhuma porta disponível encontrada")
    
    def _start_streamlit(self, main_file: Path, port: int) -> subprocess.Popen:
        """Inicia o Streamlit em background."""
        cmd = [
            "pipenv", "run", "streamlit", "run", "main.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=main_file.parent
        )
        return process
    
    def _install_common_dependencies(self, submission_path: Path):
        """Instala dependências comuns que podem estar faltando."""
        common_deps = [
            "plotly",
            "altair", 
            "matplotlib",
            "seaborn",
            "numpy",
            "pandas",
            "requests",
            "beautifulsoup4",
            "lxml"
        ]
        
        print(f"  [DEBUG] Tentando instalar dependências comuns...")
        
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
                    print(f"  [DEBUG] Instalado: {dep}")
                else:
                    print(f"  [DEBUG] Falha ao instalar {dep}: {result.stderr.decode()}")
            except Exception as e:
                print(f"  [DEBUG] Falha ao instalar {dep}: {e}")
                continue
    
    def _stop_streamlit(self, process: subprocess.Popen):
        """Para o processo Streamlit."""
        try:
            if process.poll() is None:  # Processo ainda está rodando
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        except Exception as e:
            print(f"  [DEBUG] Erro ao parar processo Streamlit: {e}")
            try:
                process.kill()
            except:
                pass
    
    def _capture_screenshot(self, port: int, output_path: Path):
        """Captura screenshot da página Streamlit."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument(f"--window-size={CHROME_WINDOW_SIZE}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Acessa a página Streamlit
            url = f"http://localhost:{port}"
            print(f"  [DEBUG] Acessando {url}")
            driver.get(url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(driver, STREAMLIT_STARTUP_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Aguarda um pouco mais para o Streamlit renderizar completamente
            time.sleep(SCREENSHOT_WAIT_TIME)
            
            # Captura screenshot
            driver.save_screenshot(str(output_path))
            print(f"  [DEBUG] Screenshot salvo em {output_path}")
            
        except Exception as e:
            print(f"  [DEBUG] Erro na captura de screenshot: {e}")
            raise e
        finally:
            driver.quit() 