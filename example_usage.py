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

from src.main import cli

def run_example():
    """Executa exemplos de uso do sistema."""
    
    print("🚀 Sistema de Correção Automática - Exemplos de Uso")
    print("=" * 60)
    
    # Exemplo 1: Correção de um assignment específico com prompt personalizado
    print("\n📝 Exemplo 1: Assignment Python com prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-prova-av (Web Scraping + Streamlit)")
    print("Características:")
    print("  • Prompt personalizado em prompts/prog1-prova-av/prompt.txt")
    print("  • Considera estrutura específica do enunciado")
    print("  • Avalia critérios específicos: scraping (40%), dashboard (50%), escolhas (10%)")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 2: Assignment HTML com prompt personalizado
    print("\n📝 Exemplo 2: Assignment HTML com prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-tarefa-html-curriculo")
    print("Características:")
    print("  • Prompt personalizado em prompts/prog1-tarefa-html-curriculo/prompt.txt")
    print("  • Avalia estrutura de arquivos (20%), index.html (40%), contato.html (30%), CSS (10%)")
    print("  • Verifica elementos HTML obrigatórios: headings, lists, images, links, tables")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--assignment", "prog1-tarefa-html-curriculo", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 3: Assignment sem prompt personalizado (usa template padrão)
    print("\n📝 Exemplo 3: Assignment sem prompt personalizado")
    print("-" * 50)
    print("Assignment: prog1-tarefa-scrap-simples")
    print("Características:")
    print("  • Usa template padrão de prompt Python")
    print("  • Lê README.md do enunciado automaticamente")
    print("  • Analisa estrutura esperada dos arquivos fornecidos")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--assignment", "prog1-tarefa-scrap-simples", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 4: Correção de todos os assignments de uma turma
    print("\n📝 Exemplo 4: Correção completa de turma")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processa todos os assignments da turma")
    print("  • Usa prompts específicos quando disponíveis")
    print("  • Gera relatórios consolidados")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 5: Converter relatório JSON existente para HTML
    print("\n📝 Exemplo 5: Converter relatório JSON existente para HTML")
    print("-" * 50)
    print("Gera um relatório HTML a partir de um JSON já existente, sem rodar a correção novamente.")
    print("Comando:")
    print("  python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format html")
    # Comentar para não executar automaticamente
    # cli(["convert-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--format", "html"])

    # Exemplo 6: Converter o relatório JSON mais recente para Markdown
    print("\n📝 Exemplo 6: Converter o relatório JSON mais recente para Markdown")
    print("-" * 50)
    print("Gera um relatório Markdown a partir do JSON mais recente no diretório de relatórios.")
    print("Comando:")
    print("  python -m src.main convert-latest --format markdown")
    # Comentar para não executar automaticamente
    # cli(["convert-latest", "--format", "markdown"])
    
    # Exemplo 7: Verificar logs de auditoria da IA
    print("\n📝 Exemplo 7: Logs de Auditoria da IA")
    print("-" * 50)
    print("O sistema gera logs detalhados de todas as análises da IA.")
    print("Localização: logs/YYYY-MM-DD/assignment-name/")
    print("Conteúdo: Prompt, resposta raw da IA, resultado processado")
    print("Formato: JSON com metadados completos")
    
    # Exemplo 8: Gerar diagrama UML da arquitetura
    print("\n📝 Exemplo 8: Gerar Diagrama UML da Arquitetura")
    print("-" * 50)
    print("Gera um diagrama UML completo da arquitetura do sistema.")
    print("Comando:")
    print("  python tools/generate_mermaid_uml.py")
    print("Saída: diagrama_uml.md com diagrama Mermaid")
    
    # Exemplo 9: Geração de thumbnails Streamlit (apenas thumbnails)
    print("\n📝 Exemplo 9: Geração de Thumbnails Streamlit")
    print("-" * 50)
    print("Assignment: prog1-prova-av (apenas thumbnails)")
    print("Características:")
    print("  • Carrega todas as submissões do assignment")
    print("  • Inicia cada dashboard Streamlit em porta separada")
    print("  • Captura screenshot de cada dashboard")
    print("  • Gera relatório visual HTML com thumbnails")
    print("  • Não executa testes ou análise de IA")
    print("  • Mais rápido que correção completa")
    
    # Comentar para não executar automaticamente
    # cli(["generate-thumbnails-only", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 10: Relatório visual completo com correção
    print("\n📝 Exemplo 10: Relatório Visual Completo")
    print("-" * 50)
    print("Assignment: prog1-prova-av (correção + thumbnails)")
    print("Características:")
    print("  • Executa correção completa (testes + IA)")
    print("  • Gera thumbnails de todos os dashboards")
    print("  • Cria relatório visual com notas e thumbnails")
    print("  • Organiza por nota (melhores primeiro)")
    print("  • Inclui estatísticas de sucesso dos thumbnails")
    print("  • Grid de thumbnails com filtros por faixa de nota")
    
    # Comentar para não executar automaticamente
    # cli(["generate-visual-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    print("\n✅ Exemplos demonstrados!")
    print("\n💡 Para executar os exemplos, descomente as linhas correspondentes no código.")
    print("💡 Para mais opções, execute: python -m src.main --help")
    print("💡 Para ver a arquitetura: python tools/generate_mermaid_uml.py")
    print("\n🔧 Configurações para thumbnails:")
    print("  • Instale Chrome/Chromium para Selenium")
    print("  • Configure OPENAI_API_KEY para análise de IA")
    print("  • Verifique se pipenv está configurado")
    print("  • Ajuste timeouts em config.py se necessário")


if __name__ == "__main__":
    run_example() 