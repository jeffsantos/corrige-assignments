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
from .utils.visual_report_generator import VisualReportGenerator


console = Console()


@click.group()
def cli():
    """Sistema de Correção Automática de Atividades"""
    pass


@cli.command()
@click.option('--assignment', '-a', help='Nome do assignment para corrigir')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--submissao', '-s', help='Identificador da submissão (login do aluno ou nome do grupo)')
@click.option('--output-format', '-f', type=click.Choice(['console', 'html', 'markdown', 'json']), 
              default='console', help='Formato de saída do relatório')
@click.option('--output-dir', '-o', default='reports', help='Diretório para salvar relatórios')
@click.option('--all-assignments', is_flag=True, help='Corrigir todos os assignments da turma')
def correct(assignment, turma, submissao, output_format, output_dir, all_assignments):
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

        # Configura caminho dos logs
        logs_path = base_path / "logs"
        
        # Inicializa serviços
        correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key, logs_path)
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
                
                report = correction_service.correct_assignment(assignment, turma, submissao)
                
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
            total_submissions = len(turma.individual_submissions) + len(turma.group_submissions)
            console.print(f"[cyan]{turma.name}[/cyan]")
            console.print(f"  Assignments: {len(turma.assignments)}")
            console.print(f"  Submissões individuais: {len(turma.individual_submissions)}")
            console.print(f"  Submissões em grupo: {len(turma.group_submissions)}")
            console.print(f"  Total de submissões: {total_submissions}")
            console.print()
    
    except Exception as e:
        console.print(f"[red]Erro ao listar turmas: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--turma', '-t', required=True, help='Nome da turma')
def list_submissions(turma):
    """Lista todas as submissões de uma turma."""
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
        
        console.print(Panel(f"[bold blue]Submissões da Turma {turma}[/bold blue]"))
        
        if turma_obj.individual_submissions:
            console.print(f"[yellow]Submissões Individuais ({len(turma_obj.individual_submissions)}):[/yellow]")
            for login in sorted(turma_obj.individual_submissions):
                console.print(f"  [cyan]{login}[/cyan] (individual)")
        
        if turma_obj.group_submissions:
            console.print(f"[yellow]Submissões em Grupo ({len(turma_obj.group_submissions)}):[/yellow]")
            for group in sorted(turma_obj.group_submissions):
                console.print(f"  [cyan]{group}[/cyan] (grupo)")
    
    except Exception as e:
        console.print(f"[red]Erro ao listar submissões: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', required=True, help='Nome do assignment')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--format', '-f', type=click.Choice(['html', 'markdown']), required=True, 
              help='Formato de saída (html ou markdown)')
@click.option('--input-dir', '-i', default='reports', help='Diretório com os relatórios JSON')
@click.option('--output-dir', '-o', default='reports', help='Diretório para salvar relatórios convertidos')
def convert_report(assignment, turma, format, input_dir, output_dir):
    """Converte um relatório JSON existente para HTML ou Markdown."""
    try:
        base_path = Path(__file__).parent.parent
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Verifica se o diretório de entrada existe
        if not input_path.exists():
            console.print(f"[red]Erro: Diretório de entrada '{input_dir}' não encontrado[/red]")
            sys.exit(1)
        
        # Cria diretório de saída se não existir
        output_path.mkdir(exist_ok=True)
        
        # Nome do arquivo JSON
        json_filename = f"{assignment}_{turma}.json"
        json_path = input_path / json_filename
        
        if not json_path.exists():
            console.print(f"[red]Erro: Relatório JSON não encontrado: {json_path}[/red]")
            console.print(f"[yellow]Dica: Execute primeiro o comando 'correct' para gerar o relatório JSON[/yellow]")
            sys.exit(1)
        
        # Carrega o relatório JSON
        console.print(Panel(f"[bold blue]Convertendo relatório {assignment} da turma {turma}[/bold blue]"))
        
        from src.domain.models import CorrectionReport
        report = CorrectionReport.load_from_file(json_path)
        
        # Inicializa o gerador de relatórios
        from src.utils.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        
        # Converte para o formato solicitado
        if format == 'html':
            output_filename = f"{assignment}_{turma}.html"
            output_file = output_path / output_filename
            report_generator.generate_html_report(report, output_file)
            console.print(f"[green]Relatório HTML salvo: {output_file}[/green]")
        
        elif format == 'markdown':
            output_filename = f"{assignment}_{turma}.md"
            output_file = output_path / output_filename
            report_generator.generate_markdown_report(report, output_file)
            console.print(f"[green]Relatório Markdown salvo: {output_file}[/green]")
        
        console.print(f"[bold green]✅ Conversão concluída![/bold green]")
    
    except Exception as e:
        console.print(f"[red]Erro durante a conversão: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['html', 'markdown']), required=True, 
              help='Formato de saída (html ou markdown)')
@click.option('--input-dir', '-i', default='reports', help='Diretório com os relatórios JSON')
@click.option('--output-dir', '-o', default='reports', help='Diretório para salvar relatórios convertidos')
def convert_latest(format, input_dir, output_dir):
    """Converte o relatório JSON mais recente para HTML ou Markdown."""
    try:
        base_path = Path(__file__).parent.parent
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Verifica se o diretório de entrada existe
        if not input_path.exists():
            console.print(f"[red]Erro: Diretório de entrada '{input_dir}' não encontrado[/red]")
            sys.exit(1)
        
        # Cria diretório de saída se não existir
        output_path.mkdir(exist_ok=True)
        
        # Encontra o arquivo JSON mais recente
        json_files = list(input_path.glob("*.json"))
        
        if not json_files:
            console.print(f"[red]Erro: Nenhum relatório JSON encontrado em '{input_dir}'[/red]")
            console.print(f"[yellow]Dica: Execute primeiro o comando 'correct' para gerar relatórios JSON[/yellow]")
            sys.exit(1)
        
        # Ordena por data de modificação (mais recente primeiro)
        latest_json = max(json_files, key=lambda f: f.stat().st_mtime)
        
        console.print(Panel(f"[bold blue]Convertendo relatório mais recente: {latest_json.name}[/bold blue]"))
        
        # Carrega o relatório JSON
        from src.domain.models import CorrectionReport
        report = CorrectionReport.load_from_file(latest_json)
        
        # Inicializa o gerador de relatórios
        from src.utils.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        
        # Extrai nome base do arquivo (sem extensão)
        base_name = latest_json.stem
        
        # Converte para o formato solicitado
        if format == 'html':
            output_filename = f"{base_name}.html"
            output_file = output_path / output_filename
            report_generator.generate_html_report(report, output_file)
            console.print(f"[green]Relatório HTML salvo: {output_file}[/green]")
        
        elif format == 'markdown':
            output_filename = f"{base_name}.md"
            output_file = output_path / output_filename
            report_generator.generate_markdown_report(report, output_file)
            console.print(f"[green]Relatório Markdown salvo: {output_file}[/green]")
        
        console.print(f"[bold green]✅ Conversão concluída![/bold green]")
    
    except Exception as e:
        console.print(f"[red]Erro durante a conversão: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', required=True, help='Nome do assignment')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--output-dir', '-o', default='reports/visual', help='Diretório para salvar relatório visual')
@click.option('--force-recapture', is_flag=True, help='Força recaptura de thumbnails mesmo se já existirem')
def generate_visual_report(assignment, turma, output_dir, force_recapture):
    """Gera relatório visual com thumbnails de dashboards Streamlit."""
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
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Verifica API key do OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Configura caminho dos logs
        logs_path = base_path / "logs"
        
        console.print(Panel(f"[bold blue]Gerando relatório visual para {assignment} da turma {turma}[/bold blue]"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processando submissões...", total=None)
            
            # Inicializa serviços
            correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key, logs_path)
            visual_generator = VisualReportGenerator()
            
            # Executa correção (que inclui geração de thumbnails para assignments Streamlit)
            report = correction_service.correct_assignment(assignment, turma)
            
            progress.update(task, description="Gerando relatório visual...")
            
            # Gera relatório visual
            visual_report_path = visual_generator.generate_visual_report(
                assignment, turma, report.thumbnails, report, output_path
            )
            
            console.print(f"[green]Relatório visual salvo: {visual_report_path}[/green]")
        
        console.print(f"[bold green]✅ Relatório visual gerado com sucesso![/bold green]")
        console.print(f"[yellow]Thumbnails gerados: {len(report.thumbnails)}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Erro durante a geração do relatório visual: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli() 