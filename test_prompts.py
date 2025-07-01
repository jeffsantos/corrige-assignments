#!/usr/bin/env python3
"""
Teste para verificar se os prompts estão sendo carregados da nova localização.
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.prompt_manager import PromptManager
from src.domain.models import Assignment, AssignmentType

def test_prompt_loading():
    """Testa o carregamento de prompts da nova localização."""
    
    print("🧪 Testando carregamento de prompts da nova localização")
    print("=" * 60)
    
    # Configura caminhos
    base_path = Path(__file__).parent
    enunciados_path = base_path / "enunciados"
    prompts_path = base_path / "prompts"
    
    print(f"📁 Enunciados: {enunciados_path}")
    print(f"📁 Prompts: {prompts_path}")
    print()
    
    # Inicializa PromptManager
    prompt_manager = PromptManager(enunciados_path)
    
    # Lista de assignments para testar
    assignments_to_test = [
        "prog1-prova-av",
        "prog1-tarefa-html-curriculo", 
        "prog1-tarefa-scrap-simples",
        "prog1-tarefa-scrap-yahoo",
        "prog1-tarefa-html-tutorial"
    ]
    
    for assignment_name in assignments_to_test:
        print(f"🔍 Testando: {assignment_name}")
        
        # Cria assignment de teste
        assignment = Assignment(
            name=assignment_name,
            type=AssignmentType.PYTHON,
            description="Teste",
            requirements=["requisito1", "requisito2"],
            test_files=[]
        )
        
        # Tenta carregar prompt personalizado
        custom_prompt = prompt_manager._load_custom_prompt(assignment_name)
        
        if custom_prompt:
            print(f"  ✅ Prompt personalizado encontrado ({len(custom_prompt)} caracteres)")
            print(f"  📄 Primeiras linhas:")
            for i, line in enumerate(custom_prompt.split('\n')[:3]):
                print(f"     {i+1}: {line[:80]}{'...' if len(line) > 80 else ''}")
        else:
            print(f"  ⚠️  Nenhum prompt personalizado encontrado (usará template padrão)")
        
        print()
    
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_prompt_loading() 