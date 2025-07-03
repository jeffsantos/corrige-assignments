"""
Serviço para gerar thumbnails de páginas HTML estáticas.
"""
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..domain.models import ThumbnailResult
from config import SCREENSHOT_WAIT_TIME, CHROME_WINDOW_SIZE


class HTMLThumbnailService:
    """Serviço para gerar thumbnails de páginas HTML estáticas."""
    
    def __init__(self, output_dir: Path = None, verbose: bool = False):
        self.output_dir = output_dir or Path("reports/visual/thumbnails")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
    
    def _debug_print(self, message: str):
        """Imprime mensagem de debug apenas se verbose estiver habilitado."""
        if self.verbose:
            print(message)
    
    def generate_thumbnails_for_assignment(self, assignment_name: str, turma_name: str, 
                                         submissions: List) -> List[ThumbnailResult]:
        """Gera thumbnails para todas as submissões de um assignment HTML."""
        print(f"Gerando thumbnails HTML para {assignment_name} da turma {turma_name}")
        
        results = []
        
        for submission in submissions:
            try:
                print(f"Gerando thumbnail HTML para {submission.display_name} ({'grupo' if hasattr(submission, 'group_name') else 'individual'})...")
                result = self._capture_submission_thumbnail(submission, assignment_name, turma_name)
                results.append(result)
            except Exception as e:
                print(f"Erro ao gerar thumbnail HTML para {submission.display_name}: {e}")
                # Identificador da submissão
                identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
                # Cria resultado de erro
                result = ThumbnailResult(
                    submission_identifier=identifier,
                    display_name=submission.display_name,
                    thumbnail_path=Path(),
                    capture_timestamp=datetime.now().isoformat(),
                    streamlit_status="error",  # Mantém compatibilidade com o modelo existente
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    def _capture_submission_thumbnail(self, submission, assignment_name: str, 
                                    turma_name: str) -> ThumbnailResult:
        """Captura thumbnail de uma submissão HTML específica."""
        # Encontra o arquivo index.html da submissão
        index_file = submission.submission_path / "index.html"
        if not index_file.exists():
            raise FileNotFoundError(f"Arquivo index.html não encontrado em {submission.submission_path}")
        
        # Identificador da submissão
        identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
        
        self._debug_print(f"  [DEBUG] Capturando thumbnail HTML para {identifier}")
        
        # Captura screenshot
        thumbnail_path = self.output_dir / f"{identifier}_{assignment_name}.png"
        try:
            self._capture_screenshot(index_file, thumbnail_path)
            self._debug_print(f"  [DEBUG] Screenshot HTML capturado com sucesso para {identifier}")
        except Exception as screenshot_exc:
            self._debug_print(f"  [DEBUG] Erro na captura de screenshot HTML para {identifier}: {screenshot_exc}")
            raise screenshot_exc
        
        return ThumbnailResult(
            submission_identifier=identifier,
            display_name=submission.display_name,
            thumbnail_path=thumbnail_path,
            capture_timestamp=datetime.now().isoformat(),
            streamlit_status="success"  # Mantém compatibilidade com o modelo existente
        )
    
    def _capture_screenshot(self, html_file: Path, output_path: Path):
        """Captura screenshot da página HTML completa."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--force-device-scale-factor=1")  # Força escala 1:1
        chrome_options.add_argument("--high-dpi-support=1")
        chrome_options.add_argument(f"--window-size={CHROME_WINDOW_SIZE}")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Converte caminho do arquivo para URL file://
            file_url = f"file:///{html_file.absolute().as_posix()}"
            self._debug_print(f"  [DEBUG] Acessando {file_url}")
            driver.get(file_url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Aguarda um pouco mais para a página renderizar completamente
            time.sleep(SCREENSHOT_WAIT_TIME)
            
            # Captura screenshot da página inteira
            self._capture_full_page_screenshot(driver, output_path)
            self._debug_print(f"  [DEBUG] Screenshot HTML completo salvo em {output_path}")
            
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na captura de screenshot HTML: {e}")
            raise e
        finally:
            driver.quit()
    
    def _capture_full_page_screenshot(self, driver, output_path: Path):
        """Captura screenshot da página HTML inteira, incluindo conteúdo rolável."""
        try:
            # Aguarda mais tempo para a página renderizar completamente
            time.sleep(3)
            
            # Usa método simples e robusto para captura completa
            self._capture_simple_full_screenshot(driver, output_path)
                
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na captura de página HTML completa: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path))
    
    def _capture_simple_full_screenshot(self, driver, output_path: Path):
        """Método simples e robusto para captura de página HTML completa."""
        try:
            # Obtém dimensões reais da página
            total_height = driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.clientHeight,
                    document.documentElement.scrollHeight,
                    document.documentElement.offsetHeight
                );
            """)
            
            total_width = driver.execute_script("""
                return Math.max(
                    document.body.scrollWidth,
                    document.body.offsetWidth,
                    document.documentElement.clientWidth,
                    document.documentElement.scrollWidth,
                    document.documentElement.offsetWidth
                );
            """)
            
            self._debug_print(f"  [DEBUG] Dimensões HTML detectadas: {total_width}x{total_height}")
            
            # Para HTML, vamos usar uma abordagem mais direta
            # Define uma altura mínima para garantir captura completa
            min_height = max(total_height + 200, 1200)  # Adiciona 200px de margem + mínimo 1200px
            
            # Redimensiona a janela para capturar mais conteúdo
            driver.set_window_size(total_width, min_height)
            time.sleep(2)
            
            # Força scroll para baixo para garantir que todo o conteúdo seja renderizado
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Aguarda mais tempo para renderização completa
            
            # Volta para o topo
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Captura screenshot
            driver.save_screenshot(str(output_path))
            self._debug_print(f"  [DEBUG] Screenshot HTML capturado com altura mínima de {min_height}px")
            
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro no método simples HTML: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path)) 