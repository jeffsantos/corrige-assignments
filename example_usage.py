"""
Exemplo de uso do sistema de correção automática.

Este script demonstra como usar o sistema programaticamente.
"""
import os
from pathlib import Path
from src.services.correction_service import CorrectionService
from src.utils.report_generator import ReportGenerator


def main():
    """Exemplo principal de uso do sistema."""
    
    # Configura caminhos
    base_path = Path(__file__).parent
    enunciados_path = base_path / "enunciados"
    respostas_path = base_path / "respostas"
    reports_path = base_path / "reports"
    
    # Cria diretório de relatórios se não existir
    reports_path.mkdir(exist_ok=True)
    
    # Verifica API key do OpenAI (agora com busca automática)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("ℹ️  OPENAI_API_KEY não configurada via variável de ambiente.")
        print("   O sistema tentará buscar automaticamente em:")
        print("   - ~/.secrets/open-ai-api-key.txt")
        print("   - .secrets/open-ai-api-key.txt")
    
    # Inicializa serviços
    correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key)
    report_generator = ReportGenerator()
    
    # Exemplo 1: Corrigir um assignment específico
    print("🔍 Exemplo 1: Corrigindo assignment específico")
    try:
        report = correction_service.correct_assignment(
            assignment_name="prog1-prova-av",
            turma_name="ebape-prog-aplic-barra-2025"
        )
        
        # Exibe relatório no console (agora com detalhamento de testes)
        report_generator.generate_console_report(report)
        
        # Salva relatório em diferentes formatos
        report.save_to_file(reports_path / "exemplo1.json")
        report_generator.generate_html_report(report, reports_path / "exemplo1.html")
        report_generator.generate_markdown_report(report, reports_path / "exemplo1.md")
        
        print(f"✅ Relatórios salvos em {reports_path}")
        print("   - exemplo1.json (formato JSON)")
        print("   - exemplo1.html (formato HTML)")
        print("   - exemplo1.md (formato Markdown)")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir assignment: {e}")
    
    # Exemplo 2: Corrigir um aluno específico
    print("\n👤 Exemplo 2: Corrigindo aluno específico")
    try:
        report = correction_service.correct_assignment(
            assignment_name="prog1-prova-av",
            turma_name="ebape-prog-aplic-barra-2025",
            student_name="prog1-prova-av-ana-clara-e-isabella"
        )
        
        report_generator.generate_console_report(report)
        report.save_to_file(reports_path / "exemplo2.json")
        
        print("✅ Relatório individual salvo em reports/exemplo2.json")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir aluno específico: {e}")
    
    # Exemplo 3: Listar assignments disponíveis
    print("\n📋 Exemplo 3: Listando assignments disponíveis")
    try:
        from src.repositories.assignment_repository import AssignmentRepository
        
        assignment_repo = AssignmentRepository(enunciados_path)
        assignments = assignment_repo.get_all_assignments()
        
        for assignment in assignments:
            print(f"  📝 {assignment.name} ({assignment.type.value})")
            print(f"     Descrição: {assignment.description[:80]}...")
            print(f"     Testes: {len(assignment.test_files)} arquivos")
            print(f"     Caminho: {assignment.path}")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar assignments: {e}")
    
    # Exemplo 4: Listar turmas disponíveis
    print("👥 Exemplo 4: Listando turmas disponíveis")
    try:
        from src.repositories.submission_repository import SubmissionRepository
        
        submission_repo = SubmissionRepository(respostas_path)
        turmas = submission_repo.get_all_turmas()
        
        for turma in turmas:
            print(f"  🏫 {turma.name}")
            print(f"     Assignments: {len(turma.assignments)}")
            print(f"     Alunos: {len(turma.students)}")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar turmas: {e}")


def exemplo_detalhamento_testes():
    """Exemplo de detalhamento de testes."""
    print("\n🧪 Exemplo de detalhamento de testes")
    
    try:
        from src.services.test_executor import TestExecutor
        
        base_path = Path(__file__).parent
        submission_path = base_path / "respostas" / "ebape-prog-aplic-barra-2025" / "prog1-prova-av-submissions" / "prog1-prova-av-ana-clara-e-isabella"
        test_files = ["test_scraping.py", "tests/test_app.py"]
        
        if submission_path.exists():
            test_executor = TestExecutor()
            results = test_executor.run_tests(submission_path, test_files)
            
            print(f"📊 Resultados dos testes para {submission_path.name}:")
            for test in results:
                status_icon = "✅" if test.result.value == "passed" else "❌" if test.result.value == "failed" else "⚠️"
                print(f"  {status_icon} {test.test_name}")
                if test.execution_time > 0:
                    print(f"     Tempo: {test.execution_time:.3f}s")
                if test.message and test.result.value != "passed":
                    print(f"     Erro: {test.message[:100]}...")
        else:
            print("⚠️  Caminho de submissão não encontrado para exemplo")
        
    except Exception as e:
        print(f"❌ Erro no exemplo de testes: {e}")


def exemplo_analise_individual():
    """Exemplo de análise individual de código."""
    print("\n🔬 Exemplo de análise individual de código")
    
    try:
        from src.services.ai_analyzer import AIAnalyzer
        from src.repositories.assignment_repository import AssignmentRepository
        
        base_path = Path(__file__).parent
        enunciados_path = base_path / "enunciados"
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Carrega assignment
        assignment_repo = AssignmentRepository(enunciados_path)
        assignment = assignment_repo.get_assignment("prog1-prova-av")
        
        if assignment and assignment.type.value == "python":
            # Exemplo de análise de código Python
            ai_analyzer = AIAnalyzer(openai_api_key)
            
            # Substitua pelo caminho real de uma submissão
            submission_path = base_path / "respostas" / "ebape-prog-aplic-barra-2025" / "prog1-prova-av-submissions" / "prog1-prova-av-ana-clara-e-isabella"
            
            if submission_path.exists():
                analysis = ai_analyzer.analyze_python_code(submission_path, assignment)
                print(f"📊 Análise de código:")
                print(f"   Nota: {analysis.score}/10")
                print(f"   Comentários: {len(analysis.comments)}")
                print(f"   Sugestões: {len(analysis.suggestions)}")
                print(f"   Problemas: {len(analysis.issues_found)}")
            else:
                print("⚠️  Caminho de submissão não encontrado para exemplo")
        
    except Exception as e:
        print(f"❌ Erro na análise individual: {e}")


if __name__ == "__main__":
    print("🚀 Sistema de Correção Automática - Exemplos de Uso")
    print("=" * 60)
    print("✨ Versão atualizada com:")
    print("   - Detalhamento de testes por função")
    print("   - Busca automática da API OpenAI")
    print("   - Relatórios em múltiplos formatos")
    print("   - Execução direta na pasta do aluno")
    print("=" * 60)
    
    main()
    exemplo_detalhamento_testes()
    exemplo_analise_individual()
    
    print("\n✨ Exemplos concluídos!")
    print("💡 Dica: Configure OPENAI_API_KEY para usar análise de IA completa")
    print("📚 Consulte o README.md para mais informações") 