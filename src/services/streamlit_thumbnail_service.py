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
from config import STREAMLIT_STARTUP_TIMEOUT, SCREENSHOT_WAIT_TIME, CHROME_WINDOW_SIZE, STREAMLIT_PORT_RANGE, STREAMLIT_FILE_CONFIG


class StreamlitThumbnailService:
    """Serviço para gerar thumbnails de dashboards Streamlit."""
    
    def __init__(self, output_dir: Path = None, verbose: bool = False):
        self.output_dir = output_dir or Path("reports/visual/thumbnails")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.current_assignment = None  # Para rastrear o assignment atual
    
    def _debug_print(self, message: str):
        """Imprime mensagem de debug apenas se verbose estiver habilitado."""
        if self.verbose:
            print(message)
        
    def generate_thumbnails_for_assignment(self, assignment_name: str, turma_name: str,
                                         submissions: List) -> List[ThumbnailResult]:
        """Gera thumbnails para todas as submissões de um assignment."""
        print(f"Gerando thumbnails para {assignment_name} da turma {turma_name}")

        # Armazena o assignment atual para uso posterior
        self.current_assignment = assignment_name

        # Instala dependências fundamentais uma única vez para toda a execução
        if submissions:
            first_submission_path = submissions[0].submission_path.parent
            self._debug_print(f"Instalando dependências fundamentais uma única vez...")
            self._install_fundamental_dependencies(first_submission_path)

        results = []
        
        for submission in submissions:
            try:
                print(f"Gerando thumbnail para {submission.display_name} ({'grupo' if hasattr(submission, 'group_name') else 'individual'})...")
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
        # Determina o arquivo Streamlit a ser usado
        streamlit_filename = STREAMLIT_FILE_CONFIG.get(assignment_name, "main.py")
        main_file = submission.submission_path / streamlit_filename
        if not main_file.exists():
            raise FileNotFoundError(f"Arquivo {streamlit_filename} não encontrado em {submission.submission_path}")
        
        # Identificador da submissão
        identifier = getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None)
        
        # Encontra porta disponível
        port = self._find_available_port()
        
        self._debug_print(f"  [DEBUG] Iniciando Streamlit na porta {port} para {identifier}")
        
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
                self._debug_print(f"  [DEBUG] Screenshot capturado com sucesso para {identifier}")
            except Exception as screenshot_exc:
                self._debug_print(f"  [DEBUG] Erro na captura de screenshot para {identifier}: {screenshot_exc}")
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
            self._debug_print(f"  [DEBUG] Erro na captura de thumbnail: {e}")
            
            # Verifica se é erro de importação e tenta instalar dependências
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['module', 'import', 'no module named']):
                self._debug_print(f"  [DEBUG] Detectado erro de importação, tentando instalar dependências...")
                self._install_common_dependencies(main_file.parent)
                
                # Tenta novamente após instalar dependências
                self._debug_print(f"  [DEBUG] Tentando novamente após instalar dependências...")
                process = self._start_streamlit(main_file, port)
                
                if not self._wait_for_streamlit_ready(port, identifier):
                    self._debug_print(f"  [DEBUG] Streamlit ainda falhou após instalar dependências")
                    raise RuntimeError("Streamlit falhou mesmo após instalar dependências")
                
                # Tenta capturar screenshot novamente
                try:
                    self._capture_screenshot(port, thumbnail_path)
                    self._debug_print(f"  [DEBUG] Screenshot capturado com sucesso após instalar dependências")
                    return ThumbnailResult(
                        submission_identifier=identifier,
                        display_name=submission.display_name,
                        thumbnail_path=thumbnail_path,
                        capture_timestamp=datetime.now().isoformat(),
                        streamlit_status="success"
                    )
                except Exception as retry_exc:
                    self._debug_print(f"  [DEBUG] Falha na segunda tentativa: {retry_exc}")
                    raise retry_exc
                finally:
                    self._stop_streamlit(process)
            
            raise e
            
        finally:
            # Para o processo Streamlit e aguarda um pouco para garantir que a porta seja liberada
            self._stop_streamlit(process)
            time.sleep(5)  # Aguarda 5 segundos para liberar a porta completamente
    
    def _wait_for_streamlit_ready(self, port: int, identifier: str) -> bool:
        """Aguarda Streamlit inicializar e verifica se está funcionando."""
        max_attempts = STREAMLIT_STARTUP_TIMEOUT // 2  # Tenta a cada 2 segundos
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Verifica se a porta está respondendo
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    # Aguarda um pouco mais para garantir que o Streamlit carregou completamente
                    time.sleep(3)
                    self._debug_print(f"  [DEBUG] Streamlit está respondendo na porta {port} para {identifier}")
                    return True
            except requests.RequestException:
                pass
            
            attempt += 1
            time.sleep(2)
            self._debug_print(f"  [DEBUG] Tentativa {attempt}/{max_attempts} - aguardando Streamlit para {identifier}")
        
        self._debug_print(f"  [DEBUG] Timeout aguardando Streamlit para {identifier}")
        return False
    
    def _log_process_output(self, process: subprocess.Popen, identifier: str):
        """Loga a saída do processo Streamlit para debug."""
        try:
            if process.stdout:
                out = process.stdout.read().decode(errors='ignore')
                if out.strip():
                    self._debug_print(f"  [DEBUG] Streamlit stdout para {identifier}:\n{out}")
            if process.stderr:
                err = process.stderr.read().decode(errors='ignore')
                if err.strip():
                    self._debug_print(f"  [DEBUG] Streamlit stderr para {identifier}:\n{err}")
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro ao ler saída do processo: {e}")
    
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
        # Limpa cache do Streamlit para garantir execução limpa
        self._clear_streamlit_cache(main_file.parent)

        # Usa o nome do arquivo correto
        streamlit_filename = main_file.name

        cmd = [
            "pipenv", "run", "streamlit", "run", streamlit_filename,
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.runOnSave", "false",
            "--browser.gatherUsageStats", "false",
            "--server.maxUploadSize", "200"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=main_file.parent
        )
        return process
    
    def _clear_streamlit_cache(self, submission_path: Path):
        """Limpa cache do Streamlit para garantir execução limpa."""
        try:
            # Remove diretórios de cache do Streamlit
            cache_dirs = [
                submission_path / ".streamlit",
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
            "streamlit",
            "plotly",
            "pandas",
            "requests",
            "beautifulsoup4",
            "numpy",
            "matplotlib",
            "seaborn",
            "altair",
            "lxml",
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
            "plotly",
            "altair",
            "matplotlib",
            "seaborn",
            "numpy",
            "pandas",
            "requests",
            "beautifulsoup4",
            "lxml",
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
    
    def _stop_streamlit(self, process: subprocess.Popen):
        """Para o processo Streamlit."""
        try:
            if process.poll() is None:  # Processo ainda está rodando
                self._debug_print(f"  [DEBUG] Terminando processo Streamlit...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                    self._debug_print(f"  [DEBUG] Processo Streamlit terminado com sucesso")
                except subprocess.TimeoutExpired:
                    self._debug_print(f"  [DEBUG] Forçando kill do processo Streamlit...")
                    process.kill()
                    process.wait(timeout=5)
                    self._debug_print(f"  [DEBUG] Processo Streamlit forçadamente finalizado")
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro ao parar processo Streamlit: {e}")
            try:
                process.kill()
                process.wait(timeout=5)
            except:
                pass
        
        # Mata processos órfãos do Streamlit que possam estar rodando
        self._kill_orphan_streamlit_processes()
    
    def _kill_orphan_streamlit_processes(self):
        """Mata processos órfãos do Streamlit que possam estar rodando."""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('streamlit' in arg.lower() for arg in cmdline):
                        self._debug_print(f"  [DEBUG] Matando processo órfão do Streamlit: PID {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
        except ImportError:
            self._debug_print(f"  [DEBUG] psutil não disponível, pulando limpeza de processos órfãos")
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro ao matar processos órfãos: {e}")
    
    def _capture_screenshot(self, port: int, output_path: Path):
        """Captura screenshot da página Streamlit completa."""
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
        # Suprime warnings e erros do Chrome
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--log-level=3")  # Somente erros fatais
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Acessa a página Streamlit
            url = f"http://localhost:{port}"
            self._debug_print(f"  [DEBUG] Acessando {url}")
            driver.get(url)

            # Aguarda a página carregar
            wait = WebDriverWait(driver, STREAMLIT_STARTUP_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Aguarda o Streamlit renderizar completamente
            time.sleep(SCREENSHOT_WAIT_TIME)

            # Captura screenshot da página inteira
            self._capture_full_page_screenshot(driver, output_path)
            self._debug_print(f"  [DEBUG] Screenshot completo salvo em {output_path}")

        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na captura de screenshot: {e}")
            raise e
        finally:
            driver.quit()

    def _capture_full_page_screenshot(self, driver, output_path: Path):
        """Captura screenshot da página inteira, incluindo conteúdo rolável."""
        try:
            # Aguarda mais tempo para o Streamlit renderizar completamente
            time.sleep(3)
            
            # Usa método mais simples e robusto para captura completa
            self._capture_simple_full_screenshot(driver, output_path)
                
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na captura de página completa: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path))
    
    def _capture_simple_full_screenshot(self, driver, output_path: Path):
        """Método simples e robusto para captura de página completa."""
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
            
            self._debug_print(f"  [DEBUG] Dimensões detectadas: {total_width}x{total_height}")
            
            # Para Streamlit, vamos usar uma abordagem mais direta
            # Define uma altura mínima para garantir captura completa
            min_height = max(total_height + 200, 1800)  # Adiciona 200px de margem + mínimo 1800px
            
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
            self._debug_print(f"  [DEBUG] Screenshot capturado com altura mínima de {min_height}px")
            
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro no método simples: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path))
    
    def _get_page_height(self, driver) -> int:
        """Obtém altura da página com múltiplas tentativas."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Aguarda um pouco entre tentativas
                time.sleep(1)
                
                # Múltiplas formas de obter altura
                heights = [
                    driver.execute_script("return document.body.scrollHeight"),
                    driver.execute_script("return document.body.offsetHeight"),
                    driver.execute_script("return document.documentElement.scrollHeight"),
                    driver.execute_script("return document.documentElement.offsetHeight"),
                    driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight)"),
                    # Força scroll para baixo e verifica altura
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;"),
                ]
                
                # Retorna o maior valor
                max_height = max(heights)
                self._debug_print(f"  [DEBUG] Tentativa {attempt+1}: altura máxima = {max_height}")
                return max_height
                
            except Exception as e:
                self._debug_print(f"  [DEBUG] Erro na tentativa {attempt+1}: {e}")
                continue
        
        # Fallback
        return driver.execute_script("return document.body.scrollHeight")
    
    def _get_page_width(self, driver) -> int:
        """Obtém largura da página com múltiplas tentativas."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Aguarda um pouco entre tentativas
                time.sleep(1)
                
                # Múltiplas formas de obter largura
                widths = [
                    driver.execute_script("return document.body.scrollWidth"),
                    driver.execute_script("return document.body.offsetWidth"),
                    driver.execute_script("return document.documentElement.scrollWidth"),
                    driver.execute_script("return document.documentElement.offsetWidth"),
                    driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth)"),
                ]
                
                # Retorna o maior valor
                max_width = max(widths)
                self._debug_print(f"  [DEBUG] Tentativa {attempt+1}: largura máxima = {max_width}")
                return max_width
                
            except Exception as e:
                self._debug_print(f"  [DEBUG] Erro na tentativa {attempt+1}: {e}")
                continue
        
        # Fallback
        return driver.execute_script("return document.body.scrollWidth")
    
    def _capture_scrolling_screenshot(self, driver, output_path: Path, total_width: int, total_height: int, viewport_width: int, viewport_height: int):
        """Captura screenshot da página inteira usando técnica de scroll e composição."""
        try:
            from PIL import Image
            import io
            
            # Define tamanho da janela para viewport
            driver.set_window_size(viewport_width, viewport_height)
            time.sleep(2)  # Aguarda redimensionamento
            
            # Para Streamlit, vamos usar uma abordagem mais simples: capturar em seções verticais
            # Calcula quantas seções verticais precisamos
            sections = max(1, (total_height + viewport_height - 1) // viewport_height)
            
            self._debug_print(f"  [DEBUG] Capturando {sections} seções verticais da página...")
            
            # Cria imagem final
            final_image = Image.new('RGB', (total_width, total_height))
            
            for section in range(sections):
                # Calcula posição de scroll vertical
                scroll_y = section * viewport_height
                
                # Faz scroll para a posição
                driver.execute_script(f"window.scrollTo(0, {scroll_y})")
                time.sleep(1)  # Aguarda renderização do Streamlit
                
                # Captura screenshot da seção visível
                screenshot = driver.get_screenshot_as_png()
                section_image = Image.open(io.BytesIO(screenshot))
                
                # Calcula posição na imagem final
                y = scroll_y
                
                # Calcula dimensões da seção atual
                section_height = min(viewport_height, total_height - scroll_y)
                
                # Corta a parte relevante da captura
                section_image = section_image.crop((0, 0, total_width, section_height))
                
                # Cola na imagem final
                final_image.paste(section_image, (0, y))
                
                self._debug_print(f"  [DEBUG] Seção {section+1}/{sections} capturada (y={y}, altura={section_height})")
            
            # Salva imagem final
            final_image.save(str(output_path))
            self._debug_print(f"  [DEBUG] Screenshot completo salvo com {sections} seções")
            
        except ImportError:
            self._debug_print(f"  [DEBUG] PIL não disponível, usando método alternativo...")
            self._capture_alternative_full_screenshot(driver, output_path, total_width, total_height)
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro na captura por partes: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path))
    
    def _capture_alternative_full_screenshot(self, driver, output_path: Path, total_width: int, total_height: int):
        """Método alternativo para captura de página completa sem PIL."""
        try:
            # Define tamanho da janela para capturar toda a página
            driver.set_window_size(total_width, total_height)
            time.sleep(2)  # Aguarda redimensionamento e renderização
            
            # Força reflow da página
            driver.execute_script("document.body.style.zoom = '1'")
            time.sleep(1)
            
            # Captura screenshot da página inteira
            driver.save_screenshot(str(output_path))
            self._debug_print(f"  [DEBUG] Screenshot alternativo de página completa capturado")
            
        except Exception as e:
            self._debug_print(f"  [DEBUG] Erro no método alternativo: {e}")
            # Fallback para screenshot normal
            driver.save_screenshot(str(output_path)) 