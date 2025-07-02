"""
Serviço para gerar thumbnails de dashboards Streamlit.
"""
import os
import time
import subprocess
import threading
import socket
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
        
        # Executa Streamlit em background
        process = self._start_streamlit(main_file, port)
        
        try:
            # Aguarda Streamlit inicializar
            time.sleep(STREAMLIT_STARTUP_TIMEOUT)
            
            # Captura screenshot
            thumbnail_path = self.output_dir / f"{identifier}_{assignment_name}.png"
            self._capture_screenshot(port, thumbnail_path)
            
            return ThumbnailResult(
                submission_identifier=identifier,
                display_name=submission.display_name,
                thumbnail_path=thumbnail_path,
                capture_timestamp=datetime.now().isoformat(),
                streamlit_status="success"
            )
            
        finally:
            # Para o processo Streamlit
            self._stop_streamlit(process)
    
    def _find_available_port(self) -> int:
        """Encontra uma porta disponível para o Streamlit."""
        start_port, end_port = STREAMLIT_PORT_RANGE
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("Nenhuma porta disponível encontrada")
    
    def _start_streamlit(self, main_file: Path, port: int) -> subprocess.Popen:
        """Inicia o Streamlit em background."""
        cmd = [
            "streamlit", "run", "main.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=main_file.parent
        )
        return process
    
    def _stop_streamlit(self, process: subprocess.Popen):
        """Para o processo Streamlit."""
        try:
            process.terminate()
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
    
    def _capture_screenshot(self, port: int, output_path: Path):
        """Captura screenshot da página Streamlit."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={CHROME_WINDOW_SIZE}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Acessa a página Streamlit
            url = f"http://localhost:{port}"
            driver.get(url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(driver, STREAMLIT_STARTUP_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Aguarda um pouco mais para o Streamlit renderizar completamente
            time.sleep(SCREENSHOT_WAIT_TIME)
            
            # Captura screenshot
            driver.save_screenshot(str(output_path))
            
        finally:
            driver.quit() 