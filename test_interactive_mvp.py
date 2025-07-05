#!/usr/bin/env python3
"""
Teste simples para validar o MVP da execução interativa.
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.interactive_execution_service import InteractiveExecutionService


def test_interactive_execution():
    """Testa a execução interativa do MVP."""
    
    print("🧪 Testando MVP da Execução Interativa")
    print("=" * 50)
    
    # Inicializa o serviço
    service = InteractiveExecutionService(verbose=True)
    
    # Testa com uma submissão real (se existir)
    test_path = Path("respostas/ebape-prog-aplic-barra-2025/prog1-tarefa-scrap-yahoo-submissions")
    
    if not test_path.exists():
        print(f"❌ Diretório de teste não encontrado: {test_path}")
        print("💡 Certifique-se de que existe uma submissão para prog1-tarefa-scrap-yahoo")
        return
    
    # Lista submissões disponíveis
    submissions = [d for d in test_path.iterdir() if d.is_dir()]
    
    if not submissions:
        print(f"❌ Nenhuma submissão encontrada em: {test_path}")
        return
    
    print(f"📁 Encontradas {len(submissions)} submissões")
    
    # Testa com a primeira submissão
    test_submission = submissions[0]
    print(f"🧪 Testando com submissão: {test_submission.name}")
    
    try:
        # Executa o programa interativo
        result = service.execute_interactive_program("prog1-tarefa-scrap-yahoo", test_submission)
        
        print(f"\n📊 Resultado da Execução Interativa:")
        print(f"  Status: {result.execution_status}")
        print(f"  Tempo: {result.execution_time:.2f}s")
        print(f"  Código de retorno: {result.return_code}")
        print(f"  Erro: {result.error_message}")
        
        print(f"\n📤 STDOUT (primeiros 500 chars):")
        print("-" * 40)
        print(result.stdout_output[:500])
        if len(result.stdout_output) > 500:
            print("... (truncado)")
        
        print(f"\n📤 STDERR (primeiros 200 chars):")
        print("-" * 40)
        print(result.stderr_output[:200])
        if len(result.stderr_output) > 200:
            print("... (truncado)")
        
        # Avalia o resultado
        if result.execution_status == "success":
            print(f"\n✅ SUCESSO: Programa executou corretamente!")
        elif result.execution_status == "partial_success":
            print(f"\n⚠️  PARCIAL: Programa executou mas não produziu resultado esperado")
        else:
            print(f"\n❌ FALHA: Programa não executou corretamente")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_interactive_execution() 