"""
Configurações do sistema de correção automática.
"""
import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).parent
ENUNCIADOS_DIR = BASE_DIR / "enunciados"
RESPOSTAS_DIR = BASE_DIR / "respostas"
REPORTS_DIR = BASE_DIR / "reports"

# Configurações da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3

# Configurações de teste
TEST_TIMEOUT = 30  # segundos
MAX_TEST_OUTPUT = 1000  # caracteres

# Configurações de relatório
DEFAULT_OUTPUT_FORMAT = "console"
DEFAULT_OUTPUT_DIR = "reports"

# Rubricas padrão
PYTHON_RUBRIC = {
    "funcionamento_correto": 0.4,
    "qualidade_codigo": 0.3,
    "documentacao": 0.2,
    "criatividade": 0.1
}

HTML_RUBRIC = {
    "estrutura_html": 0.4,
    "estilizacao_css": 0.3,
    "responsividade": 0.2,
    "criatividade": 0.1
}

# Elementos HTML obrigatórios
REQUIRED_HTML_ELEMENTS = [
    "h1", "h2", "h3", "lists", "images", "links", "tables"
]

# Padrões de arquivo
PYTHON_FILE_PATTERNS = ["*.py"]
HTML_FILE_PATTERNS = ["*.html", "*.htm"]
CSS_FILE_PATTERNS = ["*.css"]
TEST_FILE_PATTERNS = ["test_*.py", "*_test.py", "tests/"]

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 