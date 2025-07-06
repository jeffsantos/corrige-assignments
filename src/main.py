"""
Sistema de Correção Automática de Atividades

Este é o ponto de entrada principal do sistema.
"""
import os
import sys
from datetime import datetime
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .services.correction_service import CorrectionService
from .services.streamlit_thumbnail_service import StreamlitThumbnailService
from .services.html_thumbnail_service import HTMLThumbnailService
from .services.python_execution_visual_service import PythonExecutionVisualService
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
@click.option('--with-visual-reports', is_flag=True, help='Gerar relatórios visuais com thumbnails após correção')
@click.option('--force-recapture', is_flag=True, help='Força recaptura de thumbnails mesmo se já existirem (usado com --with-visual-reports)')
@click.option('--verbose', '-v', is_flag=True, help='Mostra logs detalhados de debug')
def correct(assignment, turma, submissao, output_format, output_dir, all_assignments, with_visual_reports, force_recapture, verbose):
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
        correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key, logs_path, verbose=verbose)
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
                
                # Gera relatórios visuais se solicitado
                if with_visual_reports:
                    progress.update(task, description="Gerando relatórios visuais...")
                    
                    # Inicializa serviços de relatórios visuais
                    visual_generator = VisualReportGenerator()
                    python_execution_visual_service = PythonExecutionVisualService(verbose=verbose)
                    
                    for report in reports:
                        # Verifica se o assignment suporta thumbnails
                        from config import assignment_has_thumbnails, get_assignment_thumbnail_type
                        
                        if assignment_has_thumbnails(report.assignment_name):
                            thumbnail_type = get_assignment_thumbnail_type(report.assignment_name)
                            
                            # Inicializa serviço de thumbnails apropriado
                            if thumbnail_type == "streamlit":
                                thumbnail_service = StreamlitThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                            elif thumbnail_type == "html":
                                thumbnail_service = HTMLThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                            else:
                                console.print(f"[yellow]⚠️  Tipo de thumbnail '{thumbnail_type}' não suportado para {report.assignment_name}[/yellow]")
                                continue
                            
                            try:
                                # Gera thumbnails
                                thumbnails = thumbnail_service.generate_thumbnails_for_assignment(
                                    report.assignment_name, report.turma, report.submissions
                                )
                                
                                # Cria relatório visual
                                visual_report_path = visual_generator.generate_visual_report(
                                    report.assignment_name, report.turma, thumbnails, report, 
                                    output_path / "visual"
                                )
                                
                                console.print(f"[green]Relatório visual salvo: {visual_report_path}[/green]")
                                console.print(f"[yellow]Thumbnails gerados: {len(thumbnails)}[/yellow]")
                                
                            except Exception as e:
                                console.print(f"[red]Erro ao gerar relatório visual para {report.assignment_name}: {str(e)}[/red]")
                                continue
                        else:
                            console.print(f"[yellow]⚠️  Assignment '{report.assignment_name}' não suporta thumbnails[/yellow]")
                        
                        # Gera relatório visual de execução Python se for assignment Python
                        from config import assignment_has_python_execution
                        if assignment_has_python_execution(report.assignment_name):
                            try:
                                # Cria diretório para relatórios de execução
                                execution_visual_dir = output_path / "visual"
                                execution_visual_dir.mkdir(exist_ok=True)
                                
                                # Gera relatório visual de execução
                                execution_visual_path = python_execution_visual_service.generate_execution_visual_report(
                                    report.assignment_name, report.turma, report.submissions, execution_visual_dir
                                )
                                
                                console.print(f"[green]Relatório visual de execução salvo: {execution_visual_path}[/green]")
                                
                            except Exception as e:
                                console.print(f"[red]Erro ao gerar relatório visual de execução para {report.assignment_name}: {str(e)}[/red]")
                                continue
            
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
                
                # Gera relatório visual se solicitado
                if with_visual_reports:
                    progress.update(task, description="Gerando relatório visual...")
                    
                    # Inicializa serviços de relatórios visuais
                    visual_generator = VisualReportGenerator()
                    python_execution_visual_service = PythonExecutionVisualService(verbose=verbose)
                    
                    # Verifica se o assignment suporta thumbnails
                    from config import assignment_has_thumbnails, get_assignment_thumbnail_type
                    
                    if assignment_has_thumbnails(assignment):
                        thumbnail_type = get_assignment_thumbnail_type(assignment)
                        
                        # Inicializa serviços
                        visual_generator = VisualReportGenerator()
                        
                        if thumbnail_type == "streamlit":
                            thumbnail_service = StreamlitThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                        elif thumbnail_type == "html":
                            thumbnail_service = HTMLThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                        else:
                            console.print(f"[red]Tipo de thumbnail '{thumbnail_type}' não suportado[/red]")
                            sys.exit(1)
                        
                        # Gera thumbnails
                        thumbnails = thumbnail_service.generate_thumbnails_for_assignment(
                            assignment, turma, report.submissions
                        )
                        
                        # Cria relatório visual
                        visual_report_path = visual_generator.generate_visual_report(
                            assignment, turma, thumbnails, report, output_path / "visual"
                        )
                        
                        console.print(f"[green]Relatório visual salvo: {visual_report_path}[/green]")
                        console.print(f"[yellow]Thumbnails gerados: {len(thumbnails)}[/yellow]")
                    else:
                        console.print(f"[yellow]⚠️  Assignment '{assignment}' não suporta thumbnails[/yellow]")
                    
                    # Gera relatório visual de execução Python se for assignment Python
                    from config import assignment_has_python_execution
                    if assignment_has_python_execution(assignment):
                        try:
                            # Cria diretório para relatórios de execução
                            execution_visual_dir = output_path / "visual"
                            execution_visual_dir.mkdir(exist_ok=True)
                            
                            # Gera relatório visual de execução
                            execution_visual_path = python_execution_visual_service.generate_execution_visual_report(
                                assignment, turma, report.submissions, execution_visual_dir
                            )
                            
                            console.print(f"[green]Relatório visual de execução salvo: {execution_visual_path}[/green]")
                            
                        except Exception as e:
                            console.print(f"[red]Erro ao gerar relatório visual de execução para {assignment}: {str(e)}[/red]")
            
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
@click.option('--verbose', '-v', is_flag=True, help='Mostra logs detalhados de debug')
def generate_visual_report(assignment, turma, output_dir, force_recapture, verbose):
    """Gera relatório visual com thumbnails (sem correção)."""
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
        
        console.print(Panel(f"[bold blue]Gerando relatório visual para {assignment} da turma {turma}[/bold blue]"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Carregando submissões...", total=None)
            
            # Carrega submissões sem fazer correção
            submission_repo = SubmissionRepository(respostas_path)
            submissions = submission_repo.get_submissions_for_assignment(turma, assignment)
            
            if not submissions:
                console.print(f"[red]Nenhuma submissão encontrada para {assignment} na turma {turma}[/red]")
                sys.exit(1)
            
            progress.update(task, description="Gerando thumbnails...")
            
            # Verifica tipo de thumbnail e inicializa serviço apropriado
            from config import assignment_has_thumbnails, get_assignment_thumbnail_type
            
            if not assignment_has_thumbnails(assignment):
                console.print(f"[red]Assignment '{assignment}' não suporta geração de thumbnails[/red]")
                sys.exit(1)
            
            thumbnail_type = get_assignment_thumbnail_type(assignment)
            visual_generator = VisualReportGenerator()
            
            # Inicializa serviço de thumbnails apropriado
            if thumbnail_type == "streamlit":
                thumbnail_service = StreamlitThumbnailService(output_path / "thumbnails", verbose=verbose)
            elif thumbnail_type == "html":
                thumbnail_service = HTMLThumbnailService(output_path / "thumbnails", verbose=verbose)
            else:
                console.print(f"[red]Tipo de thumbnail '{thumbnail_type}' não suportado[/red]")
                sys.exit(1)
            
            # Gera thumbnails
            thumbnails = thumbnail_service.generate_thumbnails_for_assignment(
                assignment, turma, submissions
            )
            
            # Cria relatório básico apenas com thumbnails
            from src.domain.models import CorrectionReport
            report = CorrectionReport(
                assignment_name=assignment,
                turma=turma,
                submissions=submissions,
                thumbnails=thumbnails,
                generated_at=datetime.now().isoformat()
            )
            
            progress.update(task, description="Gerando relatório visual...")
            
            # Gera relatório visual
            visual_report_path = visual_generator.generate_visual_report(
                assignment, turma, thumbnails, report, output_path
            )
            
            console.print(f"[green]Relatório visual salvo: {visual_report_path}[/green]")
        
        console.print(f"[bold green]✅ Relatório visual gerado com sucesso![/bold green]")
        console.print(f"[yellow]Thumbnails gerados: {len(thumbnails)}[/yellow]")
        console.print(f"[blue]💡 Use 'correct' para executar correção completa (testes + IA)[/blue]")
        
    except Exception as e:
        console.print(f"[red]Erro durante a geração do relatório visual: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', help='Nome do assignment para exportar')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--all-assignments', is_flag=True, help='Exportar todos os assignments da turma')
@click.option('--format', '-f', type=click.Choice(['csv']), default='csv', help='Formato de exportação')
@click.option('--output-dir', '-o', default='reports/csv', help='Diretório para salvar arquivos CSV')
def export_results(assignment, turma, all_assignments, format, output_dir):
    """Exporta tabela de resultados para CSV."""
    try:
        # Configura caminhos
        base_path = Path(__file__).parent.parent
        reports_path = Path("reports")  # Diretório padrão dos relatórios JSON
        output_path = Path(output_dir)
        
        # Verifica se o diretório de relatórios existe
        if not reports_path.exists():
            console.print(f"[red]Erro: Diretório 'reports' não encontrado[/red]")
            console.print(f"[yellow]Dica: Execute primeiro o comando 'correct' para gerar relatórios JSON[/yellow]")
            sys.exit(1)
        
        # Cria diretório de saída se não existir
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializa serviço de exportação CSV
        from .services.csv_export_service import CSVExportService
        csv_service = CSVExportService(reports_path)
        
        if all_assignments:
            # Exporta todos os assignments da turma
            console.print(Panel(f"[bold blue]Exportando todos os assignments da turma {turma} para CSV[/bold blue]"))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Buscando relatórios...", total=None)
                
                exported_files = csv_service.export_all_assignments(turma, output_path)
                
                progress.update(task, description="Exportando dados...")
                
                if not exported_files:
                    console.print(f"[red]Nenhum relatório encontrado para a turma {turma}[/red]")
                    sys.exit(1)
                
                # Calcula estatísticas totais
                total_submissions = 0
                for csv_file in exported_files:
                    # Carrega dados do CSV para estatísticas
                    import csv
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        submissions_count = sum(1 for row in reader)
                        total_submissions += submissions_count
                    
                    assignment_name = csv_file.stem.replace(f"_{turma}_results", "")
                    console.print(f"[green]✅ {assignment_name}: {submissions_count} submissões exportadas[/green]")
                
                console.print(f"\n[bold green]📁 Arquivos gerados em: {output_path}[/bold green]")
                for csv_file in exported_files:
                    console.print(f"   - {csv_file.name}")
                
                console.print(f"\n[bold green]📊 Total: {total_submissions} submissões exportadas[/bold green]")
            
        else:
            # Exporta um assignment específico
            if not assignment:
                console.print("[red]Erro: --assignment é obrigatório quando --all-assignments não é usado[/red]")
                sys.exit(1)
            
            console.print(Panel(f"[bold blue]Exportando assignment {assignment} da turma {turma} para CSV[/bold blue]"))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Carregando relatório...", total=None)
                
                csv_file = csv_service.export_single_assignment(assignment, turma, output_path)
                
                progress.update(task, description="Exportando dados...")
                
                # Calcula estatísticas
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    submissions_count = sum(1 for row in reader)
                
                console.print(f"[green]✅ Arquivo CSV salvo: {csv_file}[/green]")
                console.print(f"[green]📊 {submissions_count} submissões exportadas[/green]")
        
        console.print(f"[bold green]✅ Exportação concluída![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Erro durante a exportação: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--assignment', '-a', required=True, help='Nome do assignment')
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--output-dir', '-o', default='reports/visual', help='Diretório para salvar relatório visual')
@click.option('--verbose', '-v', is_flag=True, help='Mostra logs detalhados de debug')
def generate_execution_visual_report(assignment, turma, output_dir, verbose):
    """Gera relatório visual da execução de programas Python."""
    try:
        # Configura caminhos
        base_path = Path(__file__).parent.parent
        output_path = Path(output_dir)
        
        # Cria diretório de saída se não existir
        output_path.mkdir(parents=True, exist_ok=True)
        
        console.print(Panel(f"[bold blue]Gerando relatório visual de execução Python[/bold blue]"))
        console.print(f"[blue]Assignment: {assignment}[/blue]")
        console.print(f"[blue]Turma: {turma}[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Carregando relatório...", total=None)
            
            # Carrega relatório JSON existente
            reports_path = base_path / "reports"
            json_path = reports_path / f"{assignment}_{turma}.json"
            
            if not json_path.exists():
                console.print(f"[red]Erro: Relatório JSON não encontrado: {json_path}[/red]")
                console.print(f"[yellow]Dica: Execute primeiro o comando 'correct' para gerar o relatório JSON[/yellow]")
                sys.exit(1)
            
            # Carrega o relatório
            from src.domain.models import CorrectionReport
            report = CorrectionReport.load_from_file(json_path)
            
            progress.update(task, description="Gerando relatório visual...")
            
            # Inicializa serviço de relatório visual de execução
            python_execution_visual_service = PythonExecutionVisualService(verbose=verbose)
            
            # Gera relatório visual de execução
            execution_visual_path = python_execution_visual_service.generate_execution_visual_report(
                assignment, turma, report.submissions, output_path
            )
            
            progress.update(task, description="Relatório visual gerado")
        
        console.print(f"[green]✅ Relatório visual de execução salvo: {execution_visual_path}[/green]")
        console.print(f"[blue]📊 Submissões processadas: {len(report.submissions)}[/blue]")
        
        # Calcula estatísticas
        submissions_with_execution = [s for s in report.submissions 
                                    if hasattr(s, 'python_execution') and s.python_execution]
        
        if submissions_with_execution:
            successful = sum(1 for s in submissions_with_execution 
                           if s.python_execution.execution_status == "success")
            console.print(f"[blue]✅ Execuções bem-sucedidas: {successful}/{len(submissions_with_execution)}[/blue]")
        else:
            console.print(f"[yellow]⚠️  Nenhuma submissão com execução Python encontrada[/yellow]")
        
        console.print(f"[bold green]✅ Relatório visual de execução concluído![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Erro ao gerar relatório visual de execução: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--turma', '-t', required=True, help='Nome da turma')
@click.option('--assignment', '-a', help='Nome do assignment específico (opcional - se não fornecido, processa todos)')
@click.option('--output-format', '-f', type=click.Choice(['console', 'html', 'markdown', 'json']), 
              default='html', help='Formato de saída do relatório')
@click.option('--output-dir', '-o', default='reports', help='Diretório para salvar relatórios')
@click.option('--force-recapture', is_flag=True, help='Força recaptura de thumbnails mesmo se já existirem')
@click.option('--verbose', '-v', is_flag=True, help='Mostra logs detalhados de debug')
def correct_all_with_visual(turma, assignment, output_format, output_dir, force_recapture, verbose):
    """Executa correção completa de turma com relatórios visuais."""
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
        correction_service = CorrectionService(enunciados_path, respostas_path, openai_api_key, logs_path, verbose=verbose)
        report_generator = ReportGenerator()
        visual_generator = VisualReportGenerator()
        
        # Determina o escopo do processamento
        if assignment:
            console.print(Panel(f"[bold blue]Processamento completo do assignment {assignment} da turma {turma}[/bold blue]"))
            console.print("[yellow]📋 Inclui: Correção + Relatórios + Thumbnails + Exportação CSV[/yellow]")
        else:
            console.print(Panel(f"[bold blue]Processamento completo da turma {turma}[/bold blue]"))
            console.print("[yellow]📋 Inclui: Correção + Relatórios + Thumbnails + Exportação CSV[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Etapa 1: Correção de assignments
            task = progress.add_task("1/4 - Corrigindo assignments...", total=None)
            
            if assignment:
                # Processa apenas o assignment específico
                reports = [correction_service.correct_assignment(assignment, turma)]
            else:
                # Processa todos os assignments da turma
                reports = correction_service.correct_all_assignments(turma)
            
            progress.update(task, description="1/4 - Correção concluída")
            
            # Etapa 2: Geração de relatórios
            task = progress.add_task("2/4 - Gerando relatórios...", total=None)
            
            for report in reports:
                # Salva relatório JSON
                json_path = output_path / f"{report.assignment_name}_{report.turma}.json"
                report.save_to_file(json_path)
                
                # Gera relatórios no formato solicitado
                if output_format == 'html':
                    html_path = output_path / f"{report.assignment_name}_{report.turma}.html"
                    report_generator.generate_html_report(report, html_path)
                    console.print(f"[green]✅ Relatório HTML: {html_path}[/green]")
                
                elif output_format == 'markdown':
                    md_path = output_path / f"{report.assignment_name}_{report.turma}.md"
                    report_generator.generate_markdown_report(report, md_path)
                    console.print(f"[green]✅ Relatório Markdown: {md_path}[/green]")
                
                else:  # console
                    report_generator.generate_console_report(report)
                
                console.print(f"[green]✅ Relatório JSON: {json_path}[/green]")
            
            progress.update(task, description="2/4 - Relatórios concluídos")
            
            # Etapa 3: Geração de relatórios visuais
            task = progress.add_task("3/4 - Gerando relatórios visuais...", total=None)
            
            visual_reports_generated = 0
            execution_visual_reports_generated = 0
            
            for report in reports:
                # Verifica se o assignment suporta thumbnails
                from config import assignment_has_thumbnails, get_assignment_thumbnail_type
                
                if assignment_has_thumbnails(report.assignment_name):
                    thumbnail_type = get_assignment_thumbnail_type(report.assignment_name)
                    
                    # Inicializa serviço de thumbnails apropriado
                    if thumbnail_type == "streamlit":
                        thumbnail_service = StreamlitThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                    elif thumbnail_type == "html":
                        thumbnail_service = HTMLThumbnailService(output_path / "visual" / "thumbnails", verbose=verbose)
                    else:
                        console.print(f"[yellow]⚠️  Tipo de thumbnail '{thumbnail_type}' não suportado para {report.assignment_name}[/yellow]")
                        continue
                    
                    try:
                        # Gera thumbnails
                        thumbnails = thumbnail_service.generate_thumbnails_for_assignment(
                            report.assignment_name, report.turma, report.submissions
                        )
                        
                        # Cria relatório visual
                        visual_report_path = visual_generator.generate_visual_report(
                            report.assignment_name, report.turma, thumbnails, report, 
                            output_path / "visual"
                        )
                        
                        console.print(f"[green]✅ Relatório visual: {visual_report_path}[/green]")
                        console.print(f"[yellow]📸 Thumbnails: {len(thumbnails)}[/yellow]")
                        visual_reports_generated += 1
                        
                    except Exception as e:
                        console.print(f"[red]❌ Erro no relatório visual para {report.assignment_name}: {str(e)}[/red]")
                        continue
                else:
                    console.print(f"[yellow]⚠️  Assignment '{report.assignment_name}' não suporta thumbnails[/yellow]")
                
                # Gera relatório visual de execução Python se for assignment Python
                from config import assignment_has_python_execution
                if assignment_has_python_execution(report.assignment_name):
                    try:
                        # Inicializa serviço de relatório visual de execução
                        python_execution_visual_service = PythonExecutionVisualService(verbose=verbose)
                        
                        # Gera relatório visual de execução
                        execution_visual_path = python_execution_visual_service.generate_execution_visual_report(
                            report.assignment_name, report.turma, report.submissions, output_path / "visual"
                        )
                        
                        console.print(f"[green]✅ Relatório visual de execução: {execution_visual_path}[/green]")
                        execution_visual_reports_generated += 1
                        
                    except Exception as e:
                        console.print(f"[red]❌ Erro no relatório visual de execução para {report.assignment_name}: {str(e)}[/red]")
                        continue
            
            progress.update(task, description="3/4 - Relatórios visuais concluídos")
            
            # Etapa 4: Exportação CSV
            task = progress.add_task("4/4 - Exportando CSV...", total=None)
            
            try:
                # Inicializa serviço de exportação CSV
                from .services.csv_export_service import CSVExportService
                csv_service = CSVExportService(output_path)
                
                if assignment:
                    # Exporta apenas o assignment específico
                    csv_file = csv_service.export_single_assignment(assignment, turma, output_path / "csv")
                    console.print(f"[green]✅ CSV exportado: {csv_file.name}[/green]")
                else:
                    # Exporta todos os assignments da turma
                    exported_files = csv_service.export_all_assignments(turma, output_path / "csv")
                    
                    for csv_file in exported_files:
                        assignment_name = csv_file.stem.replace(f"_{turma}_results", "")
                        console.print(f"[green]✅ CSV exportado: {csv_file.name}[/green]")
                
                progress.update(task, description="4/4 - Exportação CSV concluída")
                
            except Exception as e:
                console.print(f"[red]❌ Erro na exportação CSV: {str(e)}[/red]")
                progress.update(task, description="4/4 - Exportação CSV falhou")
        
        # Resumo final
        console.print(f"\n[bold green]🎉 Processamento completo concluído![/bold green]")
        console.print(f"[blue]📊 Assignments processados: {len(reports)}[/blue]")
        console.print(f"[blue]📸 Relatórios visuais gerados: {visual_reports_generated}[/blue]")
        console.print(f"[blue]🐍 Relatórios visuais de execução: {execution_visual_reports_generated}[/blue]")
        console.print(f"[blue]📁 Diretório de saída: {output_path}[/blue]")
        console.print(f"[blue]📋 Relatórios: {output_path}[/blue]")
        console.print(f"[blue]🖼️  Visuais: {output_path}/visual[/blue]")
        console.print(f"[blue]📊 CSV: {output_path}/csv[/blue]")
        
    except Exception as e:
        console.print(f"[red]Erro durante o processamento completo: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli() 