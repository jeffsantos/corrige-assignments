#!/usr/bin/env python3
"""
Exemplo de uso do sistema de correção automática de assignments.

Este script demonstra como usar o sistema para corrigir assignments
com análise de IA específica por assignment e prompts personalizados.
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import main

def run_example():
    """Executa exemplos de uso do sistema."""
    
    print("🚀 Sistema de Correção Automática - Exemplos de Uso")
    print("=" * 60)
    
    # Exemplo 1: Correção de um assignment específico com prompt personalizado
    print("\n📝 Exemplo 1: Assignment Python com prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-prova-av (Web Scraping + Streamlit)")
    print("Características:")
    print("  • Prompt personalizado em enunciados/prog1-prova-av/prompt.txt")
    print("  • Considera estrutura específica do enunciado")
    print("  • Avalia critérios específicos: scraping (40%), dashboard (50%), escolhas (10%)")
    
    # Comentar para não executar automaticamente
    # main(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 2: Assignment HTML com prompt personalizado
    print("\n📝 Exemplo 2: Assignment HTML com prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-tarefa-html-curriculo")
    print("Características:")
    print("  • Prompt personalizado em enunciados/prog1-tarefa-html-curriculo/prompt.txt")
    print("  • Avalia estrutura de arquivos (20%), index.html (40%), contato.html (30%), CSS (10%)")
    print("  • Verifica elementos HTML obrigatórios: headings, lists, images, links, tables")
    
    # Comentar para não executar automaticamente
    # main(["correct", "--assignment", "prog1-tarefa-html-curriculo", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 3: Assignment sem prompt personalizado (usa template padrão)
    print("\n📝 Exemplo 3: Assignment sem prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-tarefa-scrap-simples")
    print("Características:")
    print("  • Usa template padrão de prompt Python")
    print("  • Lê README.md do enunciado automaticamente")
    print("  • Analisa estrutura esperada dos arquivos fornecidos")
    
    # Comentar para não executar automaticamente
    # main(["correct", "--assignment", "prog1-tarefa-scrap-simples", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 4: Correção de todos os assignments de uma turma
    print("\n📝 Exemplo 4: Correção completa de turma")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processa todos os assignments da turma")
    print("  • Usa prompts específicos quando disponíveis")
    print("  • Gera relatórios consolidados")
    
    # Comentar para não executar automaticamente
    # main(["correct", "--turma", "ebape-prog-aplic-barra-2025"])
    
    print("\n✅ Exemplos demonstrados!")
    print("\n💡 Para executar os exemplos, descomente as linhas correspondentes no código.")
    print("💡 Para mais opções, execute: python -m src.main --help")

if __name__ == "__main__":
    run_example() 