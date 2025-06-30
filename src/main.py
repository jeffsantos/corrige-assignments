"""
Sistema de Correção Automática de Atividades

Este é o ponto de entrada principal do sistema.
"""
import os
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .services.correction_service import CorrectionService
from .utils.report_generator import ReportGenerator
from .repositories.assignment_repository import AssignmentRepository
from .repositories.submission_repository import SubmissionRepository


console = Console()


@click.group()
def cli():
    """Sistema de Correção Automática de Atividades"""
    pass


@cli.command()
@click.option('--assignment', '-a', help='Nome do assignment para corrigir')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--aluno', '-s', help='Nome específico do aluno (opcional)')
@click.option('--output-format', '-f', type=click.Choice(['console', 'html', 'markdown', 'json']), 
              default='console', help='Formato de saída do relatório')
@click.option('--output-dir', '-o', default='reports', help='Diretório para salvar relatórios')
@click.option('--all-assignments', is_flag=True, help='Corrigir todos os assignments da turma')
def correct(assignment, turma, aluno, output_format, output_dir, all_assignments):
    """Executa a correção de assignments."""
    try:
        # Configura caminhos
        base_path = Path(__file__).parent.parent
        enunciados_path = base_path / "enunciados"
        respostas_path = base_path / "respostas"
        output_path = Path(output_dir)
        
        # Verifica se os diretórios existem
        if not enunciados_path.exists():
            console.print(f"[red]Erro: Diretório 'enunciados' não encontrado em {enunciados_path}[/red]")
            sys.exit(1)
        
        if not respostas_path.exists():
            console.print(f"[red]Erro: Diretório 'respostas' não encontrado em {respostas_path}[/red]")
            sys.exit(1)
        
        # Cria diretório de saída se não existir
        output_path.mkdir(exist_ok=True)
        
        # Verifica API key do OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            console.print("[yellow]Aviso: OPENAI_API_KEY não configurada. A análise de IA será limitada.[/yellow]")
        
        # Inicializa serviços
        correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key)
        report_generator = ReportGenerator()
        
        if all_assignments:
            # Corrige todos os assignments da turma
            console.print(Panel(f"[bold blue]Corrigindo todos os assignments da turma {turma}[/bold blue]"))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processando assignments...", total=None)
                
                reports = correction_service.correct_all_assignments(turma)
                
                progress.update(task, description=f"Gerando relatórios...")
                
                for report in reports:
                    # Salva relatório JSON
                    json_path = output_path / f"{report.assignment_name}_{report.turma}.json"
                    report.save_to_file(json_path)
                    
                    # Gera relatórios nos formatos solicitados
                    if output_format == 'html':
                        html_path = output_path / f"{report.assignment_name}_{report.turma}.html"
                        report_generator.generate_html_report(report, html_path)
                        console.print(f"[green]Relatório HTML salvo: {html_path}[/green]")
                    
                    elif output_format == 'markdown':
                        md_path = output_path / f"{report.assignment_name}_{report.turma}.md"
                        report_generator.generate_markdown_report(report, md_path)
                        console.print(f"[green]Relatório Markdown salvo: {md_path}[/green]")
                    
                    else:  # console
                        report_generator.generate_console_report(report)
                    
                    console.print(f"[green]Relatório JSON salvo: {json_path}[/green]")
            
            console.print(f"[bold green]✅ Correção concluída! {len(reports)} assignments processados.[/bold green]")
            
        else:
            # Corrige um assignment específico
            if not assignment:
                console.print("[red]Erro: --assignment é obrigatório quando --all-assignments não é usado[/red]")
                sys.exit(1)
            
            console.print(Panel(f"[bold blue]Corrigindo assignment {assignment} da turma {turma}[/bold blue]"))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processando submissões...", total=None)
                
                report = correction_service.correct_assignment(assignment, turma, aluno)
                
                progress.update(task, description="Gerando relatório...")
                
                # Salva relatório JSON
                json_path = output_path / f"{report.assignment_name}_{report.turma}.json"
                report.save_to_file(json_path)
                
                # Gera relatório no formato solicitado
                if output_format == 'html':
                    html_path = output_path / f"{report.assignment_name}_{report.turma}.html"
                    report_generator.generate_html_report(report, html_path)
                    console.print(f"[green]Relatório HTML salvo: {html_path}[/green]")
                
                elif output_format == 'markdown':
                    md_path = output_path / f"{report.assignment_name}_{report.turma}.md"
                    report_generator.generate_markdown_report(report, md_path)
                    console.print(f"[green]Relatório Markdown salvo: {md_path}[/green]")
                
                else:  # console
                    report_generator.generate_console_report(report)
                
                console.print(f"[green]Relatório JSON salvo: {json_path}[/green]")
            
            console.print(f"[bold green]✅ Correção concluída! {len(report.submissions)} submissões processadas.[/bold green]")
    
    except Exception as e:
        console.print(f"[red]Erro durante a correção: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def list_assignments():
    """Lista todos os assignments disponíveis."""
    try:
        base_path = Path(__file__).parent.parent
        enunciados_path = base_path / "enunciados"
        
        if not enunciados_path.exists():
            console.print(f"[red]Erro: Diretório 'enunciados' não encontrado[/red]")
            sys.exit(1)
        
        assignment_repo = AssignmentRepository(enunciados_path)
        assignments = assignment_repo.get_all_assignments()
        
        console.print(Panel("[bold blue]Assignments Disponíveis[/bold blue]"))
        
        for assignment in assignments:
            console.print(f"[cyan]{assignment.name}[/cyan] - {assignment.type.value}")
            console.print(f"  Descrição: {assignment.description[:100]}...")
            console.print(f"  Testes: {len(assignment.test_files)} arquivos")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Erro ao listar assignments: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def list_turmas():
    """Lista todas as turmas disponíveis."""
    try:
        base_path = Path(__file__).parent.parent
        respostas_path = base_path / "respostas"
        
        if not respostas_path.exists():
            console.print(f"[red]Erro: Diretório 'respostas' não encontrado[/red]")
            sys.exit(1)
        
        submission_repo = SubmissionRepository(respostas_path)
        turmas = submission_repo.get_all_turmas()
        
        console.print(Panel("[bold blue]Turmas Disponíveis[/bold blue]"))
        
        for turma in turmas:
            console.print(f"[cyan]{turma.name}[/cyan]")
            console.print(f"  Assignments: {len(turma.assignments)}")
            console.print(f"  Alunos: {len(turma.students)}")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Erro ao listar turmas: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--turma', '-t', required=True, help='Nome da turma')
def list_students(turma):
    """Lista todos os alunos de uma turma."""
    try:
        base_path = Path(__file__).parent.parent
        respostas_path = base_path / "respostas"
        
        if not respostas_path.exists():
            console.print(f"[red]Erro: Diretório 'respostas' não encontrado[/red]")
            sys.exit(1)
        
        submission_repo = SubmissionRepository(respostas_path)
        turma_obj = submission_repo.get_turma(turma)
        
        if not turma_obj:
            console.print(f"[red]Turma '{turma}' não encontrada[/red]")
            sys.exit(1)
        
        console.print(Panel(f"[bold blue]Alunos da Turma {turma}[/bold blue]"))
        
        for student in sorted(turma_obj.students):
            console.print(f"  [cyan]{student}[/cyan]")
    
    except Exception as e:
        console.print(f"[red]Erro ao listar alunos: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli() 