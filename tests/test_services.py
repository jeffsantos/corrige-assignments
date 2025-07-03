"""Testes de integração para os serviços."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.services.prompt_manager import PromptManager
from src.services.test_executor import PytestExecutor
from src.services.ai_analyzer import AIAnalyzer
from src.services.correction_service import CorrectionService
from src.repositories.assignment_repository import AssignmentRepository
from src.repositories.submission_repository import SubmissionRepository
from src.domain.models import (
    AssignmentType, SubmissionType, IndividualSubmission, GroupSubmission,
    Assignment, Turma, CorrectionReport
)
from config import get_assignment_submission_type, is_assignment_configured


class TestConfiguration:
    """Testes para o sistema de configuração."""
    
    def test_get_assignment_submission_type(self):
        """Testa obtenção do tipo de submissão para assignments configurados."""
        # Assignment configurado como grupo
        submission_type = get_assignment_submission_type("prog1-prova-av")
        assert submission_type == SubmissionType.GROUP
        
        # Assignment configurado como individual
        submission_type = get_assignment_submission_type("prog1-tarefa-html-curriculo")
        assert submission_type == SubmissionType.INDIVIDUAL
    
    def test_get_assignment_submission_type_not_configured(self):
        """Testa erro para assignment não configurado."""
        with pytest.raises(KeyError, match="não configurado"):
            get_assignment_submission_type("assignment-inexistente")
    
    def test_is_assignment_configured(self):
        """Testa verificação se assignment está configurado."""
        assert is_assignment_configured("prog1-prova-av") is True
        assert is_assignment_configured("prog1-tarefa-html-curriculo") is True
        assert is_assignment_configured("assignment-inexistente") is False


class TestPromptManager:
    """Testes para PromptManager."""
    
    def test_load_prompt_from_prompts_folder(self):
        """Testa carregamento de prompt da pasta prompts/."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de pastas
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            # Cria prompt personalizado na pasta prompts (que é relativa ao projeto)
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"
            assignment_dir = prompts_dir / "prog1-prova-av"
            assignment_dir.mkdir(parents=True)
            
            # Cria prompt personalizado
            prompt_content = "Este é um prompt personalizado para prog1-prova-av"
            (assignment_dir / "prompt.txt").write_text(prompt_content)
            
            try:
                # Testa carregamento
                prompt_manager = PromptManager(enunciados_path=enunciados_dir)
                assignment = Assignment(
                    name="prog1-prova-av",
                    type=AssignmentType.PYTHON,
                    submission_type=SubmissionType.GROUP,
                    description="Test assignment"
                )
                prompt = prompt_manager.get_assignment_prompt(
                    assignment=assignment,
                    assignment_type="python",
                    student_code="def test(): pass"
                )
                
                assert "personalizado" in prompt
            finally:
                # Limpa o arquivo criado
                if (assignment_dir / "prompt.txt").exists():
                    (assignment_dir / "prompt.txt").unlink()
                if assignment_dir.exists():
                    assignment_dir.rmdir()
    
    def test_fallback_to_enunciados_folder(self):
        """Testa fallback para pasta enunciados/."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de pastas
            enunciados_dir = Path(temp_dir) / "enunciados"
            assignment_dir = enunciados_dir / "prog1-prova-av"
            assignment_dir.mkdir(parents=True)
            
            # Cria prompt no enunciado
            prompt_content = "Prompt do enunciado"
            (assignment_dir / "prompt.txt").write_text(prompt_content)
            
            # Testa carregamento com fallback
            prompt_manager = PromptManager(enunciados_path=enunciados_dir)
            assignment = Assignment(
                name="prog1-prova-av",
                type=AssignmentType.PYTHON,
                submission_type=SubmissionType.GROUP,
                description="Test assignment"
            )
            prompt = prompt_manager.get_assignment_prompt(
                assignment=assignment,
                assignment_type="python",
                student_code="def test(): pass"
            )
            
            assert "enunciado" in prompt
    
    def test_fallback_to_generic_prompt(self):
        """Testa fallback para prompt genérico."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Não cria nenhum prompt personalizado
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            prompt_manager = PromptManager(enunciados_path=enunciados_dir)
            assignment = Assignment(
                name="prog1-prova-av",
                type=AssignmentType.PYTHON,
                submission_type=SubmissionType.GROUP,
                description="Test assignment"
            )
            prompt = prompt_manager.get_assignment_prompt(
                assignment=assignment,
                assignment_type="python",
                student_code="def test(): pass"
            )
            
            # Deve retornar prompt genérico
            assert "assignment" in prompt.lower()
            assert "python" in prompt.lower()
    
    def test_read_readme_content(self):
        """Testa leitura do conteúdo do README.md."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria README.md
            readme_content = "# Assignment Title\n\nThis is the assignment description."
            assignment_dir = Path(temp_dir) / "enunciados" / "prog1-prova-av"
            assignment_dir.mkdir(parents=True)
            (assignment_dir / "README.md").write_text(readme_content)
            
            prompt_manager = PromptManager(enunciados_path=Path(temp_dir) / "enunciados")
            readme = prompt_manager._read_assignment_readme("prog1-prova-av")
            
            assert "Assignment Title" in readme
    
    def test_analyze_assignment_structure(self):
        """Testa análise da estrutura do assignment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de arquivos
            assignment_dir = Path(temp_dir) / "enunciados" / "prog1-prova-av"
            assignment_dir.mkdir(parents=True)
            
            # Cria alguns arquivos
            (assignment_dir / "main.py").write_text("# Main file")
            (assignment_dir / "utils.py").write_text("# Utils file")
            (assignment_dir / "data.csv").write_text("data")
            
            prompt_manager = PromptManager(enunciados_path=Path(temp_dir) / "enunciados")
            structure = prompt_manager._analyze_expected_structure("prog1-prova-av")
            
            assert "main.py" in structure
            assert "utils.py" in structure
            assert "data.csv" in structure


class TestPytestExecutor:
    """Testes para PytestExecutor."""
    
    def test_execute_tests_with_pytest_json(self):
        """Testa execução de testes com pytest-json-report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria arquivo de teste simples
            test_file = Path(temp_dir) / "test_example.py"
            test_file.write_text("""
import pytest

def test_pass():
    assert True

def test_fail():
    assert False

def test_error():
    raise Exception("Test error")
""")
            
            test_executor = PytestExecutor()
            results = test_executor.run_tests(Path(temp_dir), ["test_example.py"])
            
            # Verifica se os resultados foram parseados corretamente
            assert len(results) >= 3
            
            # Encontra os testes específicos
            pass_test = next((r for r in results if "test_pass" in r.test_name), None)
            fail_test = next((r for r in results if "test_fail" in r.test_name), None)
            error_test = next((r for r in results if "test_error" in r.test_name), None)
            
            if pass_test:
                assert pass_test.result.value == "passed"
            if fail_test:
                assert fail_test.result.value == "failed"
            if error_test:
                # Pode ser "error" ou "failed" dependendo do pytest
                assert error_test.result.value in ["error", "failed"]
    
    def test_execute_tests_no_test_files(self):
        """Testa execução quando não há arquivos de teste."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_executor = PytestExecutor()
            results = test_executor.run_tests(Path(temp_dir), [])
            
            assert len(results) == 1
            assert results[0].result.value == "error"
    
    def test_execute_tests_invalid_python(self):
        """Testa execução com código Python inválido."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria arquivo com sintaxe inválida
            test_file = Path(temp_dir) / "test_invalid.py"
            test_file.write_text("""
def test_invalid():
    if True
        assert True
""")
            
            test_executor = PytestExecutor()
            results = test_executor.run_tests(Path(temp_dir), ["test_invalid.py"])
            
            # Deve capturar o erro de sintaxe
            assert len(results) >= 1
            assert results[0].result.value == "error"


class TestAIAnalyzer:
    """Testes para AIAnalyzer."""
    
    @patch('src.services.ai_analyzer.OpenAI')
    def test_analyze_code(self, mock_openai):
        """Testa análise de código com mock da OpenAI."""
        # Configura mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """NOTA: 8.5
COMENTARIOS: 
- Good structure
- Clear code

SUGESTOES: 
- Add comments
- Improve documentation

PROBLEMAS: 
- Missing docstring
- No error handling"""
        mock_client.chat.completions.create.return_value = mock_response
        
        # Testa análise
        with tempfile.TemporaryDirectory() as temp_dir:
            submission_path = Path(temp_dir)
            (submission_path / "main.py").write_text("def hello(): pass")
            
            assignment = Assignment(
                name="prog1-prova-av",
                type=AssignmentType.PYTHON,
                submission_type=SubmissionType.GROUP,
                description="Test assignment"
            )
            
            analyzer = AIAnalyzer(api_key="fake-key")
            result = analyzer.analyze_python_code(submission_path, assignment)
            
            assert result.score == 8.5
            assert "Good structure" in result.comments
            assert "Add comments" in result.suggestions
            assert "Missing docstring" in result.issues_found
    
    @patch('src.services.ai_analyzer.OpenAI')
    def test_analyze_html(self, mock_openai):
        """Testa análise HTML com mock da OpenAI."""
        # Configura mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """NOTA: 7.0
ELEMENTOS: 
- h1: True
- h2: False
- p: True

COMENTARIOS: 
- Good CSS
- Clean structure

SUGESTOES: 
- Improve accessibility
- Add more content

PROBLEMAS: 
- Missing alt
- No navigation"""
        mock_client.chat.completions.create.return_value = mock_response
        
        # Testa análise
        with tempfile.TemporaryDirectory() as temp_dir:
            submission_path = Path(temp_dir)
            (submission_path / "index.html").write_text("<h1>Title</h1>")
            
            assignment = Assignment(
                name="prog1-tarefa-html-curriculo",
                type=AssignmentType.HTML,
                submission_type=SubmissionType.INDIVIDUAL,
                description="Test assignment"
            )
            
            analyzer = AIAnalyzer(api_key="fake-key")
            result = analyzer.analyze_html_code(submission_path, assignment)
            
            assert result.score == 7.0
            # Verifica se os elementos foram parseados corretamente
            assert "h1" in result.required_elements
            assert "h2" in result.required_elements
            assert "Good CSS" in result.comments
    
    def test_save_audit_log(self):
        """Testa salvamento do log de auditoria."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_dir = Path(temp_dir) / "logs"
            logs_dir.mkdir()
            
            analyzer = AIAnalyzer(api_key="fake-key", logs_path=logs_dir)
            
            # Simula uma análise
            analyzer._save_ai_log(
                assignment_name="prog1-prova-av",
                submission_identifier="joaosilva",
                analysis_type="python",
                prompt="Test prompt",
                response="Test response",
                parsed_result={"score": 8.0}
            )
            
            # Verifica se o arquivo foi criado
            log_files = list(logs_dir.glob("**/*.json"))
            assert len(log_files) == 1
            
            # Verifica conteúdo
            log_content = json.loads(log_files[0].read_text())
            assert log_content["metadata"]["assignment_name"] == "prog1-prova-av"
            assert log_content["metadata"]["submission_identifier"] == "joaosilva"
            assert log_content["prompt"] == "Test prompt"
            assert log_content["raw_response"] == "Test response"
            assert log_content["parsed_result"]["score"] == 8.0
    
    def test_parse_python_analysis_acento(self):
        """Testa o parsing da resposta da IA para análise Python com acentos."""
        analyzer = AIAnalyzer(api_key="fake-key")
        test_response = """NOTA: 9

COMENTÁRIOS:
- O código do aluno está bem estruturado, separando claramente as funções de scraping do dashboard Streamlit.
- As funções de scraping parecem estar funcionando corretamente, com a extração de dados da página HTML e a geração do arquivo CSV.
- O dashboard Streamlit possui um título personalizado, filtros na sidebar, exibição de tabela de dados e dois gráficos interativos relevantes.
- Os filtros escolhidos parecem adequados para os dados extraídos e os gráficos são informativos.

SUGESTÕES:
- Adicionar mais comentários explicativos ao código, principalmente em partes mais complexas ou que realizam operações específicas.
- Melhorar a apresentação do dashboard com mais formatação e estilos visuais para tornar a experiência do usuário mais agradável.
- Explorar mais funcionalidades do Streamlit, como widgets interativos e personalização de layout, para enriquecer o dashboard.

PROBLEMAS:
- Não foram identificados problemas significativos no código do aluno."""
        result = analyzer._parse_python_analysis(test_response)
        assert result.score == 9.0
        assert len(result.comments) == 4
        assert len(result.suggestions) == 3
        assert len(result.issues_found) == 1
        assert "O código do aluno está bem estruturado" in result.comments[0]
        assert "Adicionar mais comentários explicativos ao código" in result.suggestions[0]
        assert "Não foram identificados problemas" in result.issues_found[0]
    
    def test_parse_python_analysis_justification(self):
        """Testa se a justificativa da nota é capturada corretamente na análise Python."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 8.5
JUSTIFICATIVA: Código bem estruturado com implementação correta dos requisitos principais
COMENTARIOS:
- Boa organização do código
- Implementação correta das funcionalidades
SUGESTOES:
- Adicionar mais comentários
PROBLEMAS:
- Falta tratamento de erro em uma função
"""
        
        result = analyzer._parse_python_analysis(analysis_text)
        
        assert result.score == 8.5
        assert result.score_justification == "Código bem estruturado com implementação correta dos requisitos principais"
        assert "Boa organização do código" in result.comments
        assert "Adicionar mais comentários" in result.suggestions
        assert "Falta tratamento de erro em uma função" in result.issues_found
    
    def test_parse_html_analysis_justification(self):
        """Testa se a justificativa da nota é capturada corretamente na análise HTML."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 7.0
JUSTIFICATIVA: Estrutura HTML adequada mas CSS poderia ser melhorado
ELEMENTOS:
- h1: encontrado
- h2: encontrado
- img: encontrado
- a: encontrado
COMENTARIOS:
- Estrutura HTML correta
- Elementos obrigatórios presentes
SUGESTOES:
- Melhorar estilos CSS
PROBLEMAS:
- CSS muito básico
"""
        
        result = analyzer._parse_html_analysis(analysis_text)
        
        assert result.score == 7.0
        assert result.score_justification == "Estrutura HTML adequada mas CSS poderia ser melhorado"
        assert result.required_elements["h1"] == True
        assert result.required_elements["h2"] == True
        assert result.required_elements["img"] == True
        assert result.required_elements["a"] == True
        assert "Estrutura HTML correta" in result.comments
        assert "Melhorar estilos CSS" in result.suggestions
        assert "CSS muito básico" in result.issues_found


class TestCorrectionService:
    """Testes para CorrectionService."""
    
    @pytest.mark.integration
    @pytest.mark.thumbnails
    @pytest.mark.slow
    def test_correct_assignment_integration(self):
        """Testa integração completa da correção."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de dados de teste
            enunciados_dir = Path(temp_dir) / "enunciados"
            respostas_dir = Path(temp_dir) / "respostas"
            reports_dir = Path(temp_dir) / "reports"
            
            for dir_path in [enunciados_dir, respostas_dir, reports_dir]:
                dir_path.mkdir(parents=True)
            
            # Cria assignment
            assignment_dir = enunciados_dir / "prog1-prova-av"
            assignment_dir.mkdir()
            (assignment_dir / "README.md").write_text("# Assignment")
            
            # Cria submissão na estrutura correta
            turma_dir = respostas_dir / "ebape-prog-aplic-barra-2025"
            assignment_submissions_dir = turma_dir / "prog1-prova-av-submissions"
            assignment_submissions_dir.mkdir(parents=True)
            submission_dir = assignment_submissions_dir / "prog1-prova-av-joaosilva"
            submission_dir.mkdir()
            (submission_dir / "main.py").write_text("def hello(): return 'world'")
            
            # Mock dos serviços
            with patch('src.services.ai_analyzer.AIAnalyzer') as mock_analyzer_class, \
                 patch('src.services.test_executor.PytestExecutor') as mock_executor_class:
                
                # Configura mocks
                mock_analyzer = Mock()
                mock_analyzer_class.return_value = mock_analyzer
                mock_analyzer.analyze_python_code.return_value = Mock(score=8.5)
                
                mock_executor = Mock()
                mock_executor_class.return_value = mock_executor
                mock_executor.run_tests.return_value = []
                
                # Executa correção
                service = CorrectionService(
                    enunciados_path=enunciados_dir,
                    respostas_path=respostas_dir,
                    verbose=False
                )
                
                report = service.correct_assignment(
                    assignment_name="prog1-prova-av",
                    turma_name="ebape-prog-aplic-barra-2025"
                )
                
                # Verifica resultado
                assert report.assignment_name == "prog1-prova-av"
                assert report.turma == "ebape-prog-aplic-barra-2025"
                assert len(report.submissions) == 1
                submission = report.submissions[0]
                from src.domain.models import GroupSubmission
                assert isinstance(submission, GroupSubmission)
                assert submission.group_name == "joaosilva"
                assert isinstance(submission.final_score, float)

    def test_summary_rounding_consistency(self):
        """Testa se as estatísticas de nota no summary são arredondadas para uma casa decimal."""
        from src.domain.models import IndividualSubmission, CorrectionReport
        submissions = [
            IndividualSubmission(
                github_login=f"aluno{i}",
                assignment_name="test-assignment",
                turma="test-turma",
                submission_path=Path("."),
                final_score=nota
            )
            for i, nota in enumerate([9.1, 7.7, 6.4, 8.8, 9.9])
        ]
        service = CorrectionService(Path("."), Path("."), verbose=False)
        summary = service._calculate_summary(submissions)
        # Todos devem ter apenas uma casa decimal
        for key in ["average_score", "min_score", "max_score"]:
            value = summary[key]
            # Deve ser float
            assert isinstance(value, float)
            # Deve ter apenas uma casa decimal
            value_str = f"{value:.1f}"
            assert float(value_str) == value, f"{key} não está arredondado corretamente: {value}"
        # Checagem visual
        print("Resumo arredondado:", summary)


class TestRepositories:
    """Testes para os repositórios."""
    
    def test_assignment_repository_load_assignments(self):
        """Testa carregamento de assignments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria assignments
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            # Assignment Python
            python_assignment = enunciados_dir / "prog1-prova-av"
            python_assignment.mkdir()
            (python_assignment / "README.md").write_text("# Python Assignment")
            
            # Assignment HTML
            html_assignment = enunciados_dir / "prog1-tarefa-html-curriculo"
            html_assignment.mkdir()
            (html_assignment / "README.md").write_text("# HTML Assignment")
            
            # Testa carregamento
            repo = AssignmentRepository(enunciados_path=enunciados_dir)
            assignments = repo.get_all_assignments()
            
            assert len(assignments) == 2
            assert any(a.name == "prog1-prova-av" for a in assignments)
            assert any(a.name == "prog1-tarefa-html-curriculo" for a in assignments)
    
    def test_assignment_repository_submission_type_configuration(self):
        """Testa que o tipo de submissão é carregado da configuração."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria assignment configurado
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            assignment_dir = enunciados_dir / "prog1-prova-av"
            assignment_dir.mkdir()
            (assignment_dir / "README.md").write_text("# Assignment")
            
            # Testa carregamento
            repo = AssignmentRepository(enunciados_path=enunciados_dir)
            assignment = repo.get_assignment("prog1-prova-av")
            
            # Deve usar a configuração do config.py
            assert assignment.submission_type == SubmissionType.GROUP
    
    def test_submission_repository_load_submissions(self):
        """Testa carregamento de submissões."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de submissões (estrutura esperada pelo SubmissionRepository)
            respostas_dir = Path(temp_dir) / "respostas"
            turma_dir = respostas_dir / "ebape-prog-aplic-barra-2025"
            turma_dir.mkdir(parents=True)
            
            # Cria pasta de submissões do assignment
            assignment_submissions_dir = turma_dir / "prog1-prova-av-submissions"
            assignment_submissions_dir.mkdir()
            
            # Submissão individual
            individual_dir = assignment_submissions_dir / "prog1-prova-av-joaosilva"
            individual_dir.mkdir()
            (individual_dir / "main.py").write_text("# Individual submission")
            
            # Submissão em grupo
            group_dir = assignment_submissions_dir / "prog1-prova-av-ana-clara-e-nadine"
            group_dir.mkdir()
            (group_dir / "main.py").write_text("# Group submission")
            
            # Testa carregamento
            repo = SubmissionRepository(respostas_path=respostas_dir)
            submissions = repo.get_submissions_for_assignment(
                turma_name="ebape-prog-aplic-barra-2025",
                assignment_name="prog1-prova-av"
            )
            
            assert len(submissions) == 2
            
            # Verifica tipos - deve usar configuração do config.py
            # prog1-prova-av é configurado como GROUP, então ambas devem ser GroupSubmission
            group_subs = [s for s in submissions if isinstance(s, GroupSubmission)]
            individual_subs = [s for s in submissions if isinstance(s, IndividualSubmission)]
            
            assert len(group_subs) == 2  # Ambas são grupos devido à configuração
            assert len(individual_subs) == 0
            # Verifica se ambos os identificadores estão presentes (ordem pode variar)
            group_names = [sub.group_name for sub in group_subs]
            assert "joaosilva" in group_names
            assert "ana-clara-e-nadine" in group_names
    
    def test_submission_repository_parse_identifier_with_config(self):
        """Testa que o parse de identificador usa a configuração."""
        with tempfile.TemporaryDirectory() as temp_dir:
            respostas_dir = Path(temp_dir) / "respostas"
            repo = SubmissionRepository(respostas_path=respostas_dir)
            
            # Testa com assignment configurado como grupo
            submission_type, identifier = repo._parse_submission_identifier(
                "prog1-prova-av", 
                "prog1-prova-av-joaosilva"
            )
            
            # Deve usar configuração do config.py (GROUP)
            assert submission_type == SubmissionType.GROUP
            assert identifier == "joaosilva"
            
            # Testa com assignment configurado como individual
            submission_type, identifier = repo._parse_submission_identifier(
                "prog1-tarefa-html-curriculo", 
                "prog1-tarefa-html-curriculo-joaosilva"
            )
            
            # Deve usar configuração do config.py (INDIVIDUAL)
            assert submission_type == SubmissionType.INDIVIDUAL
            assert identifier == "joaosilva"


class TestPromptConsistency:
    """Testes para garantir consistência entre prompts personalizados e fallback."""
    
    def test_python_prompt_consistency(self):
        """Testa se prompts Python (personalizado e fallback) têm campos obrigatórios."""
        # Testa prompt fallback
        analyzer = AIAnalyzer(api_key="fake-key")
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment",
            requirements=["Requirement 1", "Requirement 2"]
        )
        
        python_files = {"main.py": "def hello(): pass"}
        fallback_prompt = analyzer._build_python_analysis_prompt(python_files, assignment)
        
        # Verifica campos obrigatórios no prompt fallback
        assert "CÓDIGO DO ENUNCIADO:" in fallback_prompt
        assert "CÓDIGO DO ALUNO:" in fallback_prompt
        assert "JUSTIFICATIVA:" in fallback_prompt
        assert "NOTA:" in fallback_prompt
        assert "COMENTARIOS:" in fallback_prompt
        assert "SUGESTOES:" in fallback_prompt
        assert "PROBLEMAS:" in fallback_prompt
    
    def test_html_prompt_consistency(self):
        """Testa se prompts HTML (personalizado e fallback) têm campos obrigatórios."""
        # Testa prompt fallback
        analyzer = AIAnalyzer(api_key="fake-key")
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.HTML,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment",
            requirements=["Requirement 1", "Requirement 2"]
        )
        
        html_files = {"index.html": "<h1>Title</h1>"}
        css_files = {"style.css": "body { margin: 0; }"}
        fallback_prompt = analyzer._build_html_analysis_prompt(html_files, css_files, assignment)
        
        # Verifica campos obrigatórios no prompt fallback
        assert "CÓDIGO DO ENUNCIADO:" in fallback_prompt
        assert "CÓDIGO DO ALUNO:" in fallback_prompt
        assert "JUSTIFICATIVA:" in fallback_prompt
        assert "NOTA:" in fallback_prompt
        assert "ELEMENTOS:" in fallback_prompt
        assert "COMENTARIOS:" in fallback_prompt
        assert "SUGESTOES:" in fallback_prompt
        assert "PROBLEMAS:" in fallback_prompt
    
    def test_custom_prompt_consistency(self):
        """Testa se prompts personalizados têm campos obrigatórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria estrutura de enunciados
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            # Cria assignment de teste
            assignment_dir = enunciados_dir / "test-assignment"
            assignment_dir.mkdir()
            (assignment_dir / "main.py").write_text("# Código fornecido no enunciado")
            
            # Cria prompt personalizado
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()
            custom_prompt_dir = prompts_dir / "test-assignment"
            custom_prompt_dir.mkdir()
            
            custom_prompt_content = """Analise o código Python abaixo para o assignment "{assignment_name}".

DESCRIÇÃO DO ASSIGNMENT:
{assignment_description}

REQUISITOS ESPECÍFICOS:
{assignment_requirements}

CÓDIGO DO ENUNCIADO:
{enunciado_code}

CÓDIGO DO ALUNO:
{student_code}

Formate sua resposta assim:
NOTA: [número de 0 a 10]
JUSTIFICATIVA: [justificativa resumida e clara da nota]
COMENTARIOS: [lista de comentários sobre pontos positivos]
SUGESTOES: [lista de sugestões de melhoria]
PROBLEMAS: [lista de problemas encontrados]"""
            
            (custom_prompt_dir / "prompt.txt").write_text(custom_prompt_content)
            
            # Testa com PromptManager
            prompt_manager = PromptManager(enunciados_dir)
            assignment = Assignment(
                name="test-assignment",
                type=AssignmentType.PYTHON,
                submission_type=SubmissionType.INDIVIDUAL,
                description="Test assignment",
                requirements=["Requirement 1"]
            )
            
            custom_prompt = prompt_manager.get_assignment_prompt(
                assignment=assignment,
                assignment_type="python",
                student_code="def student_code(): pass"
            )
            
            # Verifica campos obrigatórios no prompt personalizado
            assert "CÓDIGO DO ENUNCIADO:" in custom_prompt
            assert "CÓDIGO DO ALUNO:" in custom_prompt
            assert "JUSTIFICATIVA:" in custom_prompt
            assert "NOTA:" in custom_prompt
            assert "COMENTARIOS:" in custom_prompt
            assert "SUGESTOES:" in custom_prompt
            assert "PROBLEMAS:" in custom_prompt
    
    def test_prompt_manager_template_consistency(self):
        """Testa se templates padrão do PromptManager têm campos obrigatórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            enunciados_dir = Path(temp_dir) / "enunciados"
            enunciados_dir.mkdir()
            
            prompt_manager = PromptManager(enunciados_dir)
            
            # Testa template Python
            python_template = prompt_manager._get_default_python_prompt()
            assert "CÓDIGO DO ENUNCIADO:" in python_template
            assert "CÓDIGO DO ALUNO:" in python_template
            assert "JUSTIFICATIVA:" in python_template
            assert "NOTA:" in python_template
            assert "COMENTARIOS:" in python_template
            assert "SUGESTOES:" in python_template
            assert "PROBLEMAS:" in python_template
            
            # Testa template HTML
            html_template = prompt_manager._get_default_html_prompt()
            assert "CÓDIGO DO ENUNCIADO:" in html_template
            assert "CÓDIGO DO ALUNO:" in html_template
            assert "JUSTIFICATIVA:" in html_template
            assert "NOTA:" in html_template
            assert "ELEMENTOS:" in html_template
            assert "COMENTARIOS:" in html_template
            assert "SUGESTOES:" in html_template
            assert "PROBLEMAS:" in html_template
    
    def test_all_custom_prompts_have_required_fields(self):
        """Testa se todos os prompts personalizados existentes têm campos obrigatórios."""
        # Lista de prompts personalizados conhecidos
        known_prompts = [
            "prompts/prog1-tarefa-html-curriculo/prompt.txt",
            "prompts/prog1-tarefa-html-tutorial/prompt.txt",
            "prompts/prog1-tarefa-scrap-simples/prompt.txt",
            "prompts/prog1-tarefa-scrap-yahoo/prompt.txt",
            "prompts/prog1-prova-av/prompt.txt"
        ]
        
        required_fields = [
            "CÓDIGO DO ENUNCIADO:",
            "CÓDIGO DO ALUNO:",
            "JUSTIFICATIVA:",
            "NOTA:"
        ]
        
        for prompt_path in known_prompts:
            if Path(prompt_path).exists():
                prompt_content = Path(prompt_path).read_text(encoding="utf-8")
                
                # Verifica se todos os campos obrigatórios estão presentes
                for field in required_fields:
                    assert field in prompt_content, f"Campo '{field}' não encontrado em {prompt_path}"
                
                # Verifica se é um prompt Python ou HTML
                if "ELEMENTOS:" in prompt_content:
                    # É um prompt HTML
                    assert "COMENTARIOS:" in prompt_content
                    assert "SUGESTOES:" in prompt_content
                    assert "PROBLEMAS:" in prompt_content
                else:
                    # É um prompt Python
                    assert "COMENTARIOS:" in prompt_content
                    assert "SUGESTOES:" in prompt_content
                    assert "PROBLEMAS:" in prompt_content


class TestStreamlitThumbnails:
    """Testes para a funcionalidade de thumbnails Streamlit."""
    
    @pytest.mark.thumbnails
    def test_streamlit_thumbnail_service_initialization(self):
        """Testa inicialização do serviço de thumbnails."""
        from src.services.streamlit_thumbnail_service import StreamlitThumbnailService
        
        # Testa com diretório padrão
        service = StreamlitThumbnailService()
        assert service.output_dir == Path("reports/visual/thumbnails")
        
        # Testa com diretório customizado
        custom_dir = Path("test_thumbnails")
        service = StreamlitThumbnailService(custom_dir)
        assert service.output_dir == custom_dir
        
        # Verifica se o diretório foi criado
        assert custom_dir.exists()
        
        # Limpa após o teste
        import shutil
        shutil.rmtree(custom_dir)
    
    @pytest.mark.thumbnails
    def test_find_available_port(self):
        """Testa busca de porta disponível."""
        from src.services.streamlit_thumbnail_service import StreamlitThumbnailService
        
        service = StreamlitThumbnailService()
        port = service._find_available_port()
        
        # Verifica se a porta está no range configurado
        start_port, end_port = (8501, 8600)  # STREAMLIT_PORT_RANGE
        assert port >= start_port
        assert port < end_port
        
        # Verifica se a porta é um número válido
        assert isinstance(port, int)
        assert port > 0
    
    @pytest.mark.thumbnails
    def test_calculate_thumbnail_stats(self):
        """Testa cálculo de estatísticas de thumbnails."""
        from src.utils.visual_report_generator import VisualReportGenerator
        from src.domain.models import ThumbnailResult
        
        generator = VisualReportGenerator()
        
        # Cria thumbnails de teste
        thumbnails = [
            ThumbnailResult(
                submission_identifier="user1",
                display_name="User 1",
                thumbnail_path=Path("test1.png"),
                capture_timestamp="2024-01-01T10:00:00",
                streamlit_status="success"
            ),
            ThumbnailResult(
                submission_identifier="user2",
                display_name="User 2",
                thumbnail_path=Path("test2.png"),
                capture_timestamp="2024-01-01T10:01:00",
                streamlit_status="error",
                error_message="Test error"
            ),
            ThumbnailResult(
                submission_identifier="user3",
                display_name="User 3",
                thumbnail_path=Path("test3.png"),
                capture_timestamp="2024-01-01T10:02:00",
                streamlit_status="success"
            )
        ]
        
        stats = generator._calculate_thumbnail_stats(thumbnails)
        
        assert stats['total_thumbnails'] == 3
        assert stats['successful_thumbnails'] == 2
        assert stats['failed_thumbnails'] == 1
        assert stats['success_rate'] == 2/3
    
    @pytest.mark.thumbnails
    def test_thumbnail_result_creation(self):
        """Testa criação de ThumbnailResult."""
        from src.domain.models import ThumbnailResult
        
        # Testa criação com sucesso
        result = ThumbnailResult(
            submission_identifier="test_user",
            display_name="Test User",
            thumbnail_path=Path("test.png"),
            capture_timestamp="2024-01-01T10:00:00",
            streamlit_status="success"
        )
        
        assert result.submission_identifier == "test_user"
        assert result.display_name == "Test User"
        assert result.streamlit_status == "success"
        assert result.error_message is None
        
        # Testa criação com erro
        error_result = ThumbnailResult(
            submission_identifier="error_user",
            display_name="Error User",
            thumbnail_path=Path(),
            capture_timestamp="2024-01-01T10:00:00",
            streamlit_status="error",
            error_message="Test error message"
        )
        
        assert error_result.streamlit_status == "error"
        assert error_result.error_message == "Test error message"


