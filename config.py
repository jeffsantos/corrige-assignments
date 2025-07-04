"""
Configurações do sistema de correção automática.
"""
import os
from pathlib import Path
from typing import Dict, Optional
from src.domain.models import SubmissionType

# Caminhos base
BASE_DIR = Path(__file__).parent
ENUNCIADOS_DIR = BASE_DIR / "enunciados"
RESPOSTAS_DIR = BASE_DIR / "respostas"
REPORTS_DIR = BASE_DIR / "reports"

# Configurações da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#OPENAI_MODEL = "gpt-3.5-turbo"
#OPENAI_MODEL = "gpt-4.1-nano"
OPENAI_MODEL = "gpt-4.1-mini"
#OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3

# Configurações de teste
TEST_TIMEOUT = 30  # segundos
MAX_TEST_OUTPUT = 1000  # caracteres

# Configurações de thumbnails
STREAMLIT_STARTUP_TIMEOUT = 30  # segundos para aguardar Streamlit inicializar
SCREENSHOT_WAIT_TIME = 3  # segundos para aguardar renderização completa
CHROME_WINDOW_SIZE = "1440,900"  # tamanho da janela do Chrome (maior para alta resolução)
STREAMLIT_PORT_RANGE = (8501, 8600)  # range de portas para Streamlit

# Configuração do tipo de submissão para cada assignment
ASSIGNMENT_SUBMISSION_TYPES: Dict[str, SubmissionType] = {
    # Assignments individuais
    "prog1-tarefa-html-curriculo": SubmissionType.INDIVIDUAL,
    "prog1-tarefa-html-tutorial": SubmissionType.INDIVIDUAL,
    "prog1-tarefa-scrap-simples": SubmissionType.INDIVIDUAL,
    "prog1-tarefa-scrap-yahoo": SubmissionType.INDIVIDUAL,
    
    # Assignments em grupo
    "prog1-prova-av": SubmissionType.GROUP,
}

# Configuração de assignments que geram thumbnails
ASSIGNMENTS_WITH_THUMBNAILS = {
    # Assignments Streamlit
    "prog1-prova-av": "streamlit",
    
    # Assignments HTML
    "prog1-tarefa-html-curriculo": "html",
    "prog1-tarefa-html-tutorial": "html",
}

def get_assignment_submission_type(assignment_name: str) -> SubmissionType:
    """
    Retorna o tipo de submissão para um assignment específico.
    
    Args:
        assignment_name: Nome do assignment
        
    Returns:
        SubmissionType.INDIVIDUAL ou SubmissionType.GROUP
        
    Raises:
        KeyError: Se o assignment não estiver configurado
    """
    if assignment_name not in ASSIGNMENT_SUBMISSION_TYPES:
        raise KeyError(f"Assignment '{assignment_name}' não configurado em ASSIGNMENT_SUBMISSION_TYPES")
    
    return ASSIGNMENT_SUBMISSION_TYPES[assignment_name]

def is_assignment_configured(assignment_name: str) -> bool:
    """
    Verifica se um assignment está configurado.
    
    Args:
        assignment_name: Nome do assignment
        
    Returns:
        True se o assignment estiver configurado, False caso contrário
    """
    return assignment_name in ASSIGNMENT_SUBMISSION_TYPES

def get_assignment_thumbnail_type(assignment_name: str) -> Optional[str]:
    """
    Retorna o tipo de thumbnail para um assignment específico.
    
    Args:
        assignment_name: Nome do assignment
        
    Returns:
        "streamlit", "html" ou None se não gerar thumbnails
    """
    return ASSIGNMENTS_WITH_THUMBNAILS.get(assignment_name)

def assignment_has_thumbnails(assignment_name: str) -> bool:
    """
    Verifica se um assignment gera thumbnails.
    
    Args:
        assignment_name: Nome do assignment
        
    Returns:
        True se o assignment gerar thumbnails, False caso contrário
    """
    return assignment_name in ASSIGNMENTS_WITH_THUMBNAILS 