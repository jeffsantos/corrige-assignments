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

    # Exemplo 1: Correção básica de assignment
    print("\n📝 Exemplo 1: Correção Básica de Assignment")
    print("-" * 50)
    print("Assignment: prog1-prova-av (Web Scraping + Streamlit)")
    print("Características:")
    print("  • Prompt personalizado em prompts/prog1-prova-av/prompt.txt")
    print("  • Avalia critérios específicos: scraping, dashboard, escolhas")
    print("  • Submissões em grupo")
    print("\nComando:")
    print("  python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025")
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 2: Correção com debug detalhado
    print("\n📝 Exemplo 2: Correção com Debug Detalhado")
    print("-" * 50)
    print("Características:")
    print("  • Mesmas funcionalidades do Exemplo 1")
    print("  • Logs detalhados com flag --verbose")
    print("  • Útil para troubleshooting e otimização")
    print("\nComando:")
    print("  python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose")
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])

    # Exemplo 3: Assignment HTML
    print("\n📝 Exemplo 3: Assignment HTML")
    print("-" * 50)
    print("Assignment: prog1-tarefa-html-curriculo")
    print("Características:")
    print("  • Prompt personalizado para avaliação HTML/CSS")
    print("  • Avalia estrutura de arquivos e elementos HTML obrigatórios")
    print("  • Submissões individuais")
    print("\nComando:")
    print("  python -m src.main correct --assignment prog1-tarefa-html-curriculo --turma ebape-prog-aplic-barra-2025")
    # cli(["correct", "--assignment", "prog1-tarefa-html-curriculo", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 4: Correção completa de turma
    print("\n📝 Exemplo 4: Correção Completa de Turma")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processa todos os assignments da turma")
    print("  • Usa prompts específicos quando disponíveis")
    print("  • Gera relatórios consolidados")
    print("\nComando:")
    print("  python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments")
    # cli(["correct", "--turma", "ebape-prog-aplic-barra-2025", "--all-assignments"])

    # Exemplo 5: Conversão de relatórios
    print("\n📝 Exemplo 5: Conversão de Relatórios")
    print("-" * 50)
    print("Características:")
    print("  • Converte JSON existente para HTML/Markdown")
    print("  • Não executa correção novamente")
    print("  • Economiza tempo e processamento")
    print("\nComandos:")
    print("  # Converter relatório específico")
    print("  python -m src.main convert-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --format html")
    print("\n  # Converter relatório mais recente")
    print("  python -m src.main convert-latest --format markdown")
    # cli(["convert-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--format", "html"])
    # cli(["convert-latest", "--format", "markdown"])

    # Exemplo 6: Exportação CSV
    print("\n📝 Exemplo 6: Exportação CSV")
    print("-" * 50)
    print("Características:")
    print("  • Exporta tabela de resultados para CSV")
    print("  • Compatível com Excel, Google Sheets, BI")
    print("  • Inclui notas de testes e IA separadamente")
    print("\nComandos:")
    print("  # Exportar um assignment")
    print("  python -m src.main export-results --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025")
    print("\n  # Exportar todos os assignments")
    print("  python -m src.main export-results --turma ebape-prog-aplic-barra-2025 --all-assignments")
    # cli(["export-results", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 7: Geração de thumbnails
    print("\n📝 Exemplo 7: Geração de Thumbnails")
    print("-" * 50)
    print("Características:")
    print("  • Gera relatório visual com screenshots")
    print("  • Suporta Streamlit dashboards e páginas HTML")
    print("  • Não executa testes ou análise de IA")
    print("  • Performance otimizada e captura completa")
    print("\nComandos:")
    print("  # Thumbnails Streamlit")
    print("  python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025")
    print("\n  # Thumbnails HTML")
    print("  python -m src.main generate-visual-report --assignment prog1-tarefa-html-curriculo --turma ebape-prog-aplic-barra-2025")
    print("\n  # Com logs detalhados")
    print("  python -m src.main generate-visual-report --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --verbose")
    # cli(["generate-visual-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 8: Relatório de execução Python
    print("\n📝 Exemplo 8: Relatório de Execução Python")
    print("-" * 50)
    print("Assignment: prog1-tarefa-scrap-yahoo")
    print("Características:")
    print("  • Gera relatório visual da execução de programas Python")
    print("  • Exibe saídas STDOUT e STDERR")
    print("  • Estatísticas de execução e status visual")
    print("  • Suporte a assignments interativos")
    print("\nComando:")
    print("  python -m src.main generate-execution-visual-report --assignment prog1-tarefa-scrap-yahoo --turma ebape-prog-aplic-barra-2025")
    # cli(["generate-execution-visual-report", "--assignment", "prog1-tarefa-scrap-yahoo", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 9: Correção com relatórios visuais
    print("\n📝 Exemplo 9: Correção com Relatórios Visuais")
    print("-" * 50)
    print("Características:")
    print("  • Executa correção completa (testes + IA)")
    print("  • Gera relatórios nos formatos solicitados")
    print("  • Gera relatório visual com thumbnails automaticamente")
    print("  • Tudo em uma única operação")
    print("\nComandos:")
    print("  # Um assignment")
    print("  python -m src.main correct --assignment prog1-prova-av --turma ebape-prog-aplic-barra-2025 --with-visual-reports")
    print("\n  # Todos os assignments")
    print("  python -m src.main correct --turma ebape-prog-aplic-barra-2025 --all-assignments --with-visual-reports")
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--with-visual-reports"])

    # Exemplo 10: Processamento completo de turma
    print("\n📝 Exemplo 10: Processamento Completo de Turma")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processamento em 4 etapas:")
    print("    1. Correção (testes + IA)")
    print("    2. Relatórios (HTML/Markdown/JSON)")
    print("    3. Thumbnails (relatórios visuais)")
    print("    4. Exportação CSV")
    print("  • Barra de progresso e resumo final")
    print("  • Tratamento robusto de erros")
    print("\nComandos:")
    print("  # Toda a turma")
    print("  python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025")
    print("\n  # Apenas um assignment")
    print("  python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog1-tarefa-scrap-simples")
    print("\n  # Com debug detalhado")
    print("  python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --verbose")
    # cli(["correct-all-with-visual", "--turma", "ebape-prog-aplic-barra-2025"])

    # Exemplo 11: Comandos de listagem
    print("\n📝 Exemplo 11: Comandos de Listagem")
    print("-" * 50)
    print("Características:")
    print("  • Lista assignments, turmas e submissões disponíveis")
    print("  • Útil para explorar o sistema")
    print("\nComandos:")
    print("  python -m src.main list-assignments")
    print("  python -m src.main list-turmas")
    print("  python -m src.main list-submissions --turma ebape-prog-aplic-barra-2025")
    # cli(["list-assignments"])

    print("\n✅ Exemplos demonstrados!")
    print("\n💡 Dicas:")
    print("  • Descomente as linhas cli([...]) para executar os exemplos")
    print("  • Use --help para ver todas as opções: python -m src.main --help")
    print("  • Use --verbose para debug detalhado em qualquer comando")
    print("  • Configure OPENAI_API_KEY para análise de IA")
    print("  • Instale Chrome/Chromium para geração de thumbnails")
    print("\n📚 Documentação:")
    print("  • README.md - Guia completo do sistema")
    print("  • CLAUDE.md - Guia para desenvolvimento")
    print("  • docs/sistema-notas.md - Sistema de cálculo de notas")
    print("  • docs/solucao-scraping-llm.md - Avaliação de assignments de scraping")


if __name__ == "__main__":
    run_example()
