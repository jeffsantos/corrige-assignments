#!/usr/bin/env python3
"""
Teste simples para o serviço de thumbnails.
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.streamlit_thumbnail_service import StreamlitThumbnailService
from src.domain.models import IndividualSubmission

def test_thumbnail_service():
    """Testa o serviço de thumbnails."""
    print("Testando StreamlitThumbnailService...")
    
    # Cria uma submissão mock
    submission = IndividualSubmission(
        github_login="test_user",
        assignment_name="prog1-prova-av",
        turma="test_turma",
        submission_path=Path("enunciados/prog1-prova-av"),
        final_score=8.5,
        feedback="Test feedback"
    )
    
    # Cria o serviço
    service = StreamlitThumbnailService()
    
    try:
        # Tenta gerar thumbnail
        results = service.generate_thumbnails_for_assignment(
            "prog1-prova-av", "test_turma", [submission]
        )
        
        print(f"Resultados: {len(results)} thumbnails gerados")
        for result in results:
            print(f"- {result.display_name}: {result.streamlit_status}")
            if result.error_message:
                print(f"  Erro: {result.error_message}")
            else:
                print(f"  Thumbnail: {result.thumbnail_path}")
        
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_thumbnail_service() 