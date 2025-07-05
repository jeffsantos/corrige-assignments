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
    
    # Exemplo 1b: Assignment Python com logs detalhados de debug
    print("\n📝 Exemplo 1b: Assignment Python com Debug Detalhado")
    print("-" * 50)
    print("Assignment: prog1-prova-av (Web Scraping + Streamlit)")
    print("Características:")
    print("  • Todas as funcionalidades do exemplo 1")
    print("  • Logs detalhados de debug com flag --verbose")
    print("  • Debug da geração de thumbnails (se aplicável)")
    print("  • Informações de performance e otimizações")
    print("  • Logs de instalação de dependências")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])
    
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
    
    # Exemplo 4b: Correção completa de turma com logs detalhados
    print("\n📝 Exemplo 4b: Correção Completa de Turma com Debug Detalhado")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Todas as funcionalidades do exemplo 4")
    print("  • Logs detalhados de debug com flag --verbose")
    print("  • Debug de todos os assignments processados")
    print("  • Informações de performance para cada assignment")
    print("  • Logs de geração de thumbnails (se aplicável)")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])
    
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
    
    # Exemplo 9: Relatório visual com thumbnails (sem correção)
    print("\n📝 Exemplo 9: Relatório Visual com Thumbnails")
    print("-" * 50)
    print("Assignment: prog1-prova-av (apenas thumbnails)")
    print("Características:")
    print("  • Carrega todas as submissões do assignment")
    print("  • Inicia cada dashboard Streamlit em porta separada")
    print("  • Captura screenshot de cada dashboard")
    print("  • Gera relatório visual HTML com thumbnails")
    print("  • Não executa testes ou análise de IA")
    print("  • Mais rápido que correção completa")
    print("  • Performance otimizada: dependências instaladas uma única vez")
    print("  • Captura completa: altura mínima de 1800px")
    print("  • Suporte a alta resolução: 2880x1620, 200% escala")
    
    # Comentar para não executar automaticamente
    # cli(["generate-visual-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 9b: Relatório visual com logs detalhados
    print("\n📝 Exemplo 9b: Relatório Visual com Debug Detalhado")
    print("-" * 50)
    print("Assignment: prog1-prova-av (thumbnails + verbose)")
    print("Características:")
    print("  • Todas as funcionalidades do exemplo 9")
    print("  • Logs detalhados de debug com flag --verbose")
    print("  • Mostra instalação de dependências")
    print("  • Exibe dimensões de páginas detectadas")
    print("  • Logs de captura de screenshots")
    print("  • Informações de processos e portas")
    
    # Comentar para não executar automaticamente
    # cli(["generate-visual-report", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])
    
    # Exemplo 10: Relatório visual com thumbnails HTML
    print("\n📝 Exemplo 10: Relatório Visual com Thumbnails HTML")
    print("-" * 50)
    print("Assignment: prog1-tarefa-html-curriculo (apenas thumbnails)")
    print("Características:")
    print("  • Carrega todas as submissões do assignment HTML")
    print("  • Acessa diretamente o arquivo index.html de cada submissão")
    print("  • Captura screenshot de cada página HTML")
    print("  • Gera relatório visual HTML com thumbnails")
    print("  • Não executa testes ou análise de IA")
    print("  • Mais rápido que correção completa")
    print("  • Não requer servidor (acesso direto ao arquivo)")
    print("  • Captura completa: altura mínima de 1200px")
    print("  • Suporte a alta resolução: 2880x1620, 200% escala")
    
    # Comentar para não executar automaticamente
    # cli(["generate-visual-report", "--assignment", "prog1-tarefa-html-curriculo", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 10b: Relatório visual HTML com logs detalhados
    print("\n📝 Exemplo 10b: Relatório Visual HTML com Debug Detalhado")
    print("-" * 50)
    print("Assignment: prog1-tarefa-html-curriculo (thumbnails + verbose)")
    print("Características:")
    print("  • Todas as funcionalidades do exemplo 10")
    print("  • Logs detalhados de debug com flag --verbose")
    print("  • Mostra caminhos dos arquivos HTML acessados")
    print("  • Exibe dimensões de páginas detectadas")
    print("  • Logs de captura de screenshots")
    print("  • Informações de renderização HTML")
    
    # Comentar para não executar automaticamente
    # cli(["generate-visual-report", "--assignment", "prog1-tarefa-html-curriculo", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])
    
    # Exemplo 11: Exportar tabela de resultados para CSV
    print("\n📝 Exemplo 11: Exportar Tabela de Resultados para CSV")
    print("-" * 50)
    print("Assignment: prog1-prova-av")
    print("Características:")
    print("  • Exporta tabela 'Resultados por Submissão' para CSV")
    print("  • Mostra notas de testes e IA separadamente")
    print("  • Inclui estatísticas: testes passados/total, status")
    print("  • Formato compatível com Excel, Google Sheets, BI")
    print("  • Encoding UTF-8 para caracteres especiais")
    print("  • Colunas: assignment, turma, aluno/grupo, notas, status, etc.")
    
    # Comentar para não executar automaticamente
    # cli(["export-results", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 12: Exportar todos os assignments de uma turma para CSV
    print("\n📝 Exemplo 12: Exportar Todos os Assignments para CSV")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Exporta todos os assignments da turma para CSV")
    print("  • Um arquivo CSV por assignment")
    print("  • Estatísticas consolidadas de todos os assignments")
    print("  • Tratamento de erros: continua mesmo se um assignment falhar")
    print("  • Diretório de saída: reports/csv/")
    print("  • Nomenclatura: {assignment}_{turma}_results.csv")
    
    # Comentar para não executar automaticamente
    # cli(["export-results", "--turma", "ebape-prog-aplic-barra-2025", "--all-assignments"])
    
    # Exemplo 13: Exportar CSV com diretório personalizado
    print("\n📝 Exemplo 13: Exportar CSV com Diretório Personalizado")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Exporta todos os assignments da turma")
    print("  • Diretório de saída personalizado: meus-csv/")
    print("  • Útil para organizar exportações por data ou projeto")
    print("  • Mantém estrutura de arquivos organizada")
    
    # Comentar para não executar automaticamente
    # cli(["export-results", "--turma", "ebape-prog-aplic-barra-2025", "--all-assignments", "--output-dir", "meus-csv"])
    
    # Exemplo 14: Correção com relatórios visuais
    print("\n📝 Exemplo 14: Correção com Relatórios Visuais")
    print("-" * 50)
    print("Assignment: prog1-prova-av")
    print("Características:")
    print("  • Executa correção completa (testes + IA)")
    print("  • Gera relatórios nos formatos solicitados")
    print("  • Gera relatório visual com thumbnails automaticamente")
    print("  • Tudo em uma única operação")
    print("  • Ideal para assignments que suportam thumbnails")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--assignment", "prog1-prova-av", "--turma", "ebape-prog-aplic-barra-2025", "--with-visual-reports"])
    
    # Exemplo 15: Correção completa de turma com visuais
    print("\n📝 Exemplo 15: Correção Completa de Turma com Visuais")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processa todos os assignments da turma")
    print("  • Executa correção completa (testes + IA)")
    print("  • Gera relatórios nos formatos solicitados")
    print("  • Gera relatórios visuais para assignments compatíveis")
    print("  • Tudo em uma única operação")
    print("  • Tratamento de erros robusto")
    
    # Comentar para não executar automaticamente
    # cli(["correct", "--turma", "ebape-prog-aplic-barra-2025", "--all-assignments", "--with-visual-reports"])
    
    # Exemplo 16: Processamento completo de turma
    print("\n📝 Exemplo 16: Processamento Completo de Turma")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Processamento completo em 4 etapas:")
    print("    1. Correção (testes + IA)")
    print("    2. Relatórios (HTML/Markdown/JSON)")
    print("    3. Thumbnails (relatórios visuais)")
    print("    4. Exportação CSV")
    print("  • Barra de progresso com etapas bem definidas")
    print("  • Resumo final com estatísticas completas")
    print("  • Estrutura organizada de saída")
    print("  • Ideal para processamento de turmas completas")
    print("  • Economia de tempo e esforço")
    
    # Comentar para não executar automaticamente
    # cli(["correct-all-with-visual", "--turma", "ebape-prog-aplic-barra-2025"])
    
    # Exemplo 17: Processamento completo com logs detalhados
    print("\n📝 Exemplo 17: Processamento Completo com Debug Detalhado")
    print("-" * 50)
    print("Turma: ebape-prog-aplic-barra-2025")
    print("Características:")
    print("  • Todas as funcionalidades do exemplo 16")
    print("  • Logs detalhados de debug com flag --verbose")
    print("  • Debug de todas as etapas do processamento")
    print("  • Informações de performance para cada etapa")
    print("  • Logs de geração de thumbnails")
    print("  • Debug de exportação CSV")
    print("  • Útil para troubleshooting e otimização")
    
    # Comentar para não executar automaticamente
    # cli(["correct-all-with-visual", "--turma", "ebape-prog-aplic-barra-2025", "--verbose"])
    
    print("\n✅ Exemplos demonstrados!")
    print("\n💡 Para executar os exemplos, descomente as linhas correspondentes no código.")
    print("💡 Para mais opções, execute: python -m src.main --help")
    print("💡 Para ver a arquitetura: python tools/generate_mermaid_uml.py")
    print("\n🔧 Configurações para thumbnails:")
    print("  • Instale Chrome/Chromium para Selenium")
    print("  • Configure OPENAI_API_KEY para análise de IA")
    print("  • Verifique se pipenv está configurado")
    print("  • Ajuste timeouts em config.py se necessário")
    print("  • Dependências otimizadas: psutil, pillow")
    print("  • Suporte a alta resolução: 2880x1620, 200% escala")
    print("  • Use --verbose para debug detalhado")


if __name__ == "__main__":
    run_example() 