#!/usr/bin/env python3
"""
Teste para investigar problema de arredondamento nas notas.
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.models import IndividualSubmission, CorrectionReport
from services.correction_service import CorrectionService

def test_rounding_issue():
    """Testa o problema de arredondamento."""
    
    # Simula uma submissão com nota 9.1
    submission = IndividualSubmission(
        github_login="test-user",
        assignment_name="test-assignment",
        turma="test-turma",
        submission_path=Path("."),
        final_score=9.1
    )
    
    # Cria um relatório com essa submissão
    report = CorrectionReport(
        assignment_name="test-assignment",
        turma="test-turma",
        submissions=[submission],
        generated_at="2025-01-15T10:00:00"
    )
    
    # Calcula o summary
    service = CorrectionService(Path("."), Path("."))
    report.summary = service._calculate_summary([submission])
    
    print("=== TESTE DE ARREDONDAMENTO ===")
    print(f"Nota da submissão: {submission.final_score}")
    print(f"Tipo da nota: {type(submission.final_score)}")
    print(f"Nota média no summary: {report.summary['average_score']}")
    print(f"Tipo da média: {type(report.summary['average_score'])}")
    print(f"Nota mínima: {report.summary['min_score']}")
    print(f"Nota máxima: {report.summary['max_score']}")
    
    # Verifica se há diferença
    if abs(submission.final_score - report.summary['average_score']) > 0.001:
        print(f"❌ PROBLEMA ENCONTRADO: Diferença de {abs(submission.final_score - report.summary['average_score'])}")
    else:
        print("✅ Sem problemas de arredondamento detectados")
    
    # Testa formatação
    print(f"\n=== FORMATAÇÃO ===")
    print(f"Nota formatada com .1f: {submission.final_score:.1f}")
    print(f"Média formatada com .2f: {report.summary['average_score']:.2f}")
    print(f"Média formatada com .1f: {report.summary['average_score']:.1f}")

if __name__ == "__main__":
    test_rounding_issue() 