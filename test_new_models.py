#!/usr/bin/env python3
"""
Teste para verificar se os novos modelos de submissão estão funcionando corretamente.
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.domain.models import Assignment, SubmissionType, IndividualSubmission, GroupSubmission
from src.repositories.assignment_repository import AssignmentRepository
from src.repositories.submission_repository import SubmissionRepository

def test_submission_parsing():
    """Testa o parsing de identificadores de submissão."""
    
    print("🧪 Testando parsing de identificadores de submissão")
    print("=" * 60)
    
    # Testes de submissões individuais
    individual_tests = [
        ("prog1-tarefa-html-curriculo", "prog1-tarefa-html-curriculo-anaclaravtoledo"),
        ("prog1-tarefa-scrap-simples", "prog1-tarefa-scrap-simples-joaosilva"),
        ("prog1-tarefa-html-tutorial", "prog1-tarefa-html-tutorial-maria123"),
    ]
    
    print("📝 Testes de submissões individuais:")
    for assignment_name, folder_name in individual_tests:
        try:
            submission_type, identifier = Assignment.parse_submission_identifier(assignment_name, folder_name)
            print(f"  ✅ {folder_name} -> {submission_type.value}: {identifier}")
        except Exception as e:
            print(f"  ❌ {folder_name} -> Erro: {e}")
    
    print()
    
    # Testes de submissões em grupo
    group_tests = [
        ("prog1-prova-av", "prog1-prova-av-ana-clara-e-isabella"),
        ("prog1-prova-av", "prog1-prova-av-joao-maria-pedro"),
        ("prog1-prova-av", "prog1-prova-av-grupo-final"),
    ]
    
    print("👥 Testes de submissões em grupo:")
    for assignment_name, folder_name in group_tests:
        try:
            submission_type, identifier = Assignment.parse_submission_identifier(assignment_name, folder_name)
            print(f"  ✅ {folder_name} -> {submission_type.value}: {identifier}")
        except Exception as e:
            print(f"  ❌ {folder_name} -> Erro: {e}")
    
    print()

def test_assignment_repository():
    """Testa o repositório de assignments com os novos tipos."""
    
    print("📚 Testando repositório de assignments")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    enunciados_path = base_path / "enunciados"
    
    if not enunciados_path.exists():
        print("⚠️  Pasta enunciados/ não encontrada")
        return
    
    assignment_repo = AssignmentRepository(enunciados_path)
    assignments = assignment_repo.get_all_assignments()
    
    for assignment in assignments:
        print(f"📋 {assignment.name}")
        print(f"  Tipo: {assignment.type.value}")
        print(f"  Submissão: {assignment.submission_type.value}")
        print(f"  Descrição: {assignment.description[:80]}...")
        print()

def test_submission_repository():
    """Testa o repositório de submissões com os novos tipos."""
    
    print("📁 Testando repositório de submissões")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    respostas_path = base_path / "respostas"
    
    if not respostas_path.exists():
        print("⚠️  Pasta respostas/ não encontrada")
        return
    
    submission_repo = SubmissionRepository(respostas_path)
    turmas = submission_repo.get_all_turmas()
    
    for turma in turmas:
        print(f"🏫 Turma: {turma.name}")
        print(f"  Assignments: {len(turma.assignments)}")
        print(f"  Submissões individuais: {len(turma.individual_submissions)}")
        print(f"  Submissões em grupo: {len(turma.group_submissions)}")
        
        if turma.individual_submissions:
            print(f"  Logins individuais: {', '.join(sorted(turma.individual_submissions)[:5])}{'...' if len(turma.individual_submissions) > 5 else ''}")
        
        if turma.group_submissions:
            print(f"  Grupos: {', '.join(sorted(turma.group_submissions)[:5])}{'...' if len(turma.group_submissions) > 5 else ''}")
        
        print()

def test_submission_loading():
    """Testa o carregamento de submissões específicas."""
    
    print("🔍 Testando carregamento de submissões específicas")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    respostas_path = base_path / "respostas"
    
    if not respostas_path.exists():
        print("⚠️  Pasta respostas/ não encontrada")
        return
    
    submission_repo = SubmissionRepository(respostas_path)
    
    # Testa algumas submissões conhecidas
    test_cases = [
        ("ebape-prog-aplic-barra-2025", "prog1-tarefa-html-curriculo", "anaclaravtoledo"),
        ("ebape-prog-aplic-barra-2025", "prog1-prova-av", "breno-e-matheus"),
    ]
    
    for turma_name, assignment_name, identifier in test_cases:
        try:
            submission = submission_repo.get_submission(turma_name, assignment_name, identifier)
            if submission:
                print(f"✅ {turma_name}/{assignment_name}/{identifier}")
                print(f"   Tipo: {type(submission).__name__}")
                print(f"   Display: {submission.display_name}")
                print(f"   Arquivos: {len(submission.files)}")
            else:
                print(f"❌ {turma_name}/{assignment_name}/{identifier} - Não encontrado")
        except Exception as e:
            print(f"❌ {turma_name}/{assignment_name}/{identifier} - Erro: {e}")
        print()

if __name__ == "__main__":
    test_submission_parsing()
    test_assignment_repository()
    test_submission_repository()
    test_submission_loading()
    
    print("✅ Testes concluídos!") 