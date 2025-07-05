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
from src.services.python_execution_visual_service import PythonExecutionVisualService
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
    
    def test_get_assignment_thumbnail_type(self):
        """Testa obtenção do tipo de thumbnail para assignments."""
        from config import get_assignment_thumbnail_type
        
        # Testa assignments com thumbnails
        assert get_assignment_thumbnail_type("prog1-prova-av") == "streamlit"
        assert get_assignment_thumbnail_type("prog1-tarefa-html-curriculo") == "html"
        assert get_assignment_thumbnail_type("prog1-tarefa-html-tutorial") == "html"
        
        # Testa assignment sem thumbnails
        assert get_assignment_thumbnail_type("prog1-tarefa-scrap-simples") is None
    
    def test_assignment_has_thumbnails(self):
        """Testa verificação se assignment gera thumbnails."""
        from config import assignment_has_thumbnails
        
        # Testa assignments com thumbnails
        assert assignment_has_thumbnails("prog1-prova-av") == True
        assert assignment_has_thumbnails("prog1-tarefa-html-curriculo") == True
        assert assignment_has_thumbnails("prog1-tarefa-html-tutorial") == True
        
        # Testa assignment sem thumbnails
        assert assignment_has_thumbnails("prog1-tarefa-scrap-simples") == False


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
- Headings (h1, h2): Presente
- Lists (ul/ol): Presente
- Images (img): Presente
- Links (a): Presente
- Tables (table): Presente
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
        assert result.required_elements["headings"] == True
        assert result.required_elements["lists"] == True
        assert result.required_elements["img"] == True
        assert result.required_elements["a"] == True
        assert result.required_elements["table"] == True
    
    def test_parse_html_analysis_elements_inline_format(self):
        """Testa parsing de elementos HTML quando vêm na mesma linha após ELEMENTOS:."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 8.0
JUSTIFICATIVA: Boa implementação dos elementos HTML obrigatórios
ELEMENTOS: headings (h1, h2), lists (ul), images (img), links (a), tables (table)
COMENTARIOS:
- Todos os elementos obrigatórios presentes
SUGESTOES:
- Melhorar responsividade
PROBLEMAS:
- Nenhum problema encontrado
"""
        
        result = analyzer._parse_html_analysis(analysis_text)
        
        assert result.score == 8.0
        assert result.score_justification == "Boa implementação dos elementos HTML obrigatórios"
        assert result.required_elements["headings"] == True
        assert result.required_elements["lists"] == True
        assert result.required_elements["img"] == True
        assert result.required_elements["a"] == True
        assert result.required_elements["table"] == True
    
    def test_parse_html_analysis_elements_mixed_format(self):
        """Testa parsing de elementos HTML em formato misto (alguns com hífen, outros não)."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 6.0
JUSTIFICATIVA: Implementação parcial dos elementos HTML
ELEMENTOS:
- Headings (h1, h2): Presente
- Lists (ul/ol): Ausente
Images (img): Presente
Links (a): Presente
- Tables (table): Ausente
COMENTARIOS:
- Alguns elementos implementados corretamente
SUGESTOES:
- Adicionar listas e tabelas
PROBLEMAS:
- Elementos obrigatórios ausentes
"""
        
        result = analyzer._parse_html_analysis(analysis_text)
        
        assert result.score == 6.0
        assert result.score_justification == "Implementação parcial dos elementos HTML"
        assert result.required_elements["headings"] == True
        assert result.required_elements["lists"] == False
        assert result.required_elements["img"] == True
        assert result.required_elements["a"] == True
        assert result.required_elements["table"] == False
    
    def test_parse_html_analysis_elements_with_parentheses(self):
        """Testa parsing de elementos HTML com informações adicionais em parênteses."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 9.0
JUSTIFICATIVA: Excelente implementação com todos os elementos
ELEMENTOS:
- Headings (h1, h2): Presente (bem estruturados)
- Lists (ul/ol): Presente (organizadas)
- Images (img): Presente (com alt text)
- Links (a): Presente (funcionais)
- Tables (table): Presente (bem formatadas)
COMENTARIOS:
- Implementação completa
SUGESTOES:
- Nenhuma sugestão
PROBLEMAS:
- Nenhum problema
"""
        
        result = analyzer._parse_html_analysis(analysis_text)
        
        assert result.score == 9.0
        assert result.score_justification == "Excelente implementação com todos os elementos"
        assert result.required_elements["headings"] == True
        assert result.required_elements["lists"] == True
        assert result.required_elements["img"] == True
        assert result.required_elements["a"] == True
        assert result.required_elements["table"] == True
    
    def test_parse_html_analysis_justification_multiline(self):
        """Testa se justificativa multilinha é capturada corretamente."""
        analyzer = AIAnalyzer(api_key="fake-key")
        analysis_text = """
NOTA: 7.5
JUSTIFICATIVA: O aluno implementou corretamente a estrutura básica do site de currículo, 
incluindo as duas páginas HTML solicitadas e o arquivo CSS. A organização dos arquivos 
está adequada e os elementos HTML obrigatórios foram utilizados.
ELEMENTOS:
- Headings (h1, h2): Presente
- Lists (ul/ol): Presente
- Images (img): Presente
- Links (a): Presente
- Tables (table): Presente
COMENTARIOS:
- Estrutura correta
SUGESTOES:
- Melhorar CSS
PROBLEMAS:
- Nenhum
"""
        
        result = analyzer._parse_html_analysis(analysis_text)
        
        expected_justification = "O aluno implementou corretamente a estrutura básica do site de currículo, incluindo as duas páginas HTML solicitadas e o arquivo CSS. A organização dos arquivos está adequada e os elementos HTML obrigatórios foram utilizados."
        assert result.score == 7.5
        assert result.score_justification == expected_justification
    
    def test_parse_html_analysis_real_log_examples(self):
        """Testa parsing com exemplos reais dos logs problemáticos."""
        analyzer = AIAnalyzer(api_key="fake-key")
        
        # Exemplo do log tarefa-html-curriculo-anaclaravtoledo_html_08-06-46.json
        analysis_text_1 = """
NOTA: 8
JUSTIFICATIVA: O aluno atendeu à maioria dos requisitos do assignment, mas há alguns pontos que podem ser melhorados.
ELEMENTOS:
- Headings (h1, h2): Presentes
- Lists (ul): Presente
- Images (img): Presente
- Links (a): Presente
- Tables (table): Presente

COMENTÁRIOS:
- A estrutura de arquivos está correta, seguindo a organização solicitada.
- A página index.html contém todas as seções obrigatórias e os elementos HTML necessários.
- A página contato.html possui o formulário de contato com os campos solicitados.
- O CSS está bem organizado e contribui para uma apresentação visual agradável.
- Os estilos são consistentes e responsivos, tornando a página legível em diferentes dispositivos.

SUGESTÕES:
- Seria interessante adicionar mais detalhes às seções do currículo, como descrições mais elaboradas sobre a formação acadêmica e experiências.
- Considerar a adição de mais informações pessoais, como habilidades, certificações ou projetos relevantes.
- Melhorar a acessibilidade do formulário de contato, adicionando rótulos visíveis para os campos de entrada.

PROBLEMAS:
- O uso do atributo "method" no formulário de contato não é necessário, pois o envio por e-mail não é suportado em todos os navegadores. Recomenda-se utilizar uma solução de backend para processar os dados do formulário.
- Não foi encontrado um h3 na página index.html, o que poderia ser adicionado para melhorar a hierarquia de títulos.
"""
        
        result_1 = analyzer._parse_html_analysis(analysis_text_1)
        
        assert result_1.score == 8.0
        assert result_1.score_justification == "O aluno atendeu à maioria dos requisitos do assignment, mas há alguns pontos que podem ser melhorados."
        assert result_1.required_elements["headings"] == True
        assert result_1.required_elements["lists"] == True
        assert result_1.required_elements["img"] == True
        assert result_1.required_elements["a"] == True
        assert result_1.required_elements["table"] == True
        
        # Exemplo do log tarefa-html-curriculo-arthurrrangel_html_08-06-53.json
        analysis_text_2 = """
NOTA: 6
JUSTIFICATIVA: O aluno seguiu a estrutura de arquivos corretamente e implementou as seções obrigatórias nas páginas index.html e contato.html. No entanto, faltam alguns elementos HTML obrigatórios e a qualidade do CSS poderia ser melhorada.
ELEMENTOS: headings (h1, h2), lists (ul), images (img), links (a), tables (table)
COMENTÁRIOS:
- A estrutura de arquivos está correta, com os arquivos organizados conforme especificado.
- As seções obrigatórias estão presentes nas páginas index.html e contato.html.
- O link "Fale Comigo" para a página contato.html está funcionando corretamente.

SUGESTÕES:
- Adicionar mais elementos HTML obrigatórios, como headings (h3), lists (ol), e talvez uma tabela para organizar informações de forma mais estruturada.
- Melhorar a qualidade do CSS, tornando-o mais organizado e aplicando estilos de forma mais consistente e esteticamente agradável.
- Verificar a responsividade do site para garantir uma boa experiência em diferentes dispositivos.

PROBLEMAS:
- Faltam alguns elementos HTML obrigatórios, como headings (h3), lists (ol), e tables para melhorar a estrutura e organização do conteúdo.
- O CSS poderia ser mais elaborado para melhorar a apresentação visual do site.
"""
        
        result_2 = analyzer._parse_html_analysis(analysis_text_2)
        
        assert result_2.score == 6.0
        assert result_2.score_justification == "O aluno seguiu a estrutura de arquivos corretamente e implementou as seções obrigatórias nas páginas index.html e contato.html. No entanto, faltam alguns elementos HTML obrigatórios e a qualidade do CSS poderia ser melhorada."
        assert result_2.required_elements["headings"] == True
        assert result_2.required_elements["lists"] == True
        assert result_2.required_elements["img"] == True
        assert result_2.required_elements["a"] == True
        assert result_2.required_elements["table"] == True
    
    def test_prompt_contains_evaluation_criteria(self):
        """Testa se os prompts contêm o critério fundamental de avaliação."""
        analyzer = AIAnalyzer(api_key="fake-key")

        # Testa prompt genérico de Python
        python_files = {"main.py": "def hello(): pass"}
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment",
            requirements=["Requirement 1"]
        )
        
        python_prompt = analyzer._build_python_analysis_prompt(python_files, assignment)
        assert "CRITÉRIOS FUNDAMENTAIS DE AVALIAÇÃO" in python_prompt
        assert "DEFINIÇÃO DE PROBLEMAS vs SUGESTÕES" in python_prompt
        assert "NOTA 10" in python_prompt
        assert "REGRAS CRÍTICAS" in python_prompt
        assert "requisitos obrigatórios" in python_prompt
        
        # Testa prompt genérico de HTML
        html_files = {"index.html": "<h1>Title</h1>"}
        css_files = {"style.css": "body { margin: 0; }"}
        html_assignment = Assignment(
            name="test-html-assignment",
            type=AssignmentType.HTML,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test HTML assignment",
            requirements=["Requirement 1"]
        )
        
        html_prompt = analyzer._build_html_analysis_prompt(html_files, css_files, html_assignment)
        assert "CRITÉRIOS FUNDAMENTAIS DE AVALIAÇÃO" in html_prompt
        assert "DEFINIÇÃO DE PROBLEMAS vs SUGESTÕES" in html_prompt
        assert "NOTA 10" in html_prompt
        assert "REGRAS CRÍTICAS" in html_prompt
        assert "requisitos obrigatórios" in html_prompt


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

    def test_generate_feedback_python_assignment(self):
        """Testa geração de feedback para assignment Python com campos padronizados."""
        from src.domain.models import IndividualSubmission, CodeAnalysis, AssignmentTestExecution, AssignmentTestResult
        
        # Cria submissão com análise de código
        submission = IndividualSubmission(
            github_login="test_user",
            assignment_name="test-assignment",
            turma="test-turma",
            submission_path=Path("."),
            code_analysis=CodeAnalysis(
                score=8.5,
                score_justification="Código bem estruturado com implementação correta",
                comments=["Boa organização", "Implementação correta"],
                suggestions=["Adicionar mais comentários"],
                issues_found=["Falta tratamento de erro", "Variável não utilizada"]
            ),
            test_results=[
                AssignmentTestExecution(
                    test_name="test_function",
                    result=AssignmentTestResult.PASSED,
                    execution_time=0.1,
                    message="Test passed"
                ),
                AssignmentTestExecution(
                    test_name="test_another_function",
                    result=AssignmentTestResult.FAILED,
                    execution_time=0.2,
                    message="Test failed"
                )
            ]
        )
        
        # Cria assignment Python
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment"
        )
        
        # Gera feedback
        service = CorrectionService(Path("."), Path("."), verbose=False)
        feedback = service._generate_feedback(submission, assignment)
        
        # Verifica estrutura do feedback
        lines = feedback.split('\n')
        
        # Deve conter informações dos testes
        assert any("Testes: 1/2 passaram" in line for line in lines)
        assert any("Testes que falharam:" in line for line in lines)
        assert any("test_another_function" in line for line in lines)
        
        # Deve conter análise de código
        assert any("Análise de código: 8.5/10" in line for line in lines)
        
        # Deve conter JUSTIFICATIVA (novo campo padronizado)
        assert any("Justificativa:" in line for line in lines)
        assert any("Código bem estruturado com implementação correta" in line for line in lines)
        
        # Deve conter PROBLEMAS (novo campo padronizado)
        assert any("Problemas:" in line for line in lines)
        assert any("Falta tratamento de erro" in line for line in lines)
        assert any("Variável não utilizada" in line for line in lines)
        
        # NÃO deve conter "Pontos positivos" (campo antigo removido)
        assert not any("Pontos positivos:" in line for line in lines)
        assert not any("Problemas encontrados:" in line for line in lines)

    def test_generate_feedback_html_assignment(self):
        """Testa geração de feedback para assignment HTML com campos padronizados."""
        from src.domain.models import IndividualSubmission, HTMLAnalysis
        
        # Cria submissão com análise HTML
        submission = IndividualSubmission(
            github_login="test_user",
            assignment_name="test-assignment",
            turma="test-turma",
            submission_path=Path("."),
            html_analysis=HTMLAnalysis(
                score=7.0,
                score_justification="Estrutura HTML adequada mas CSS poderia ser melhorado",
                required_elements={
                    "headings": True,
                    "lists": True,
                    "img": True,
                    "a": True,
                    "table": False
                },
                comments=["Estrutura HTML correta"],
                suggestions=["Melhorar estilos CSS"],
                issues_found=["CSS muito básico", "Falta responsividade"]
            )
        )
        
        # Cria assignment HTML
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.HTML,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment"
        )
        
        # Gera feedback
        service = CorrectionService(Path("."), Path("."), verbose=False)
        feedback = service._generate_feedback(submission, assignment)
        
        # Verifica estrutura do feedback
        lines = feedback.split('\n')
        
        # Deve conter análise HTML/CSS
        assert any("Análise HTML/CSS: 7.0/10" in line for line in lines)
        
        # Deve manter apresentação dos elementos HTML (conforme solicitado)
        assert any("Elementos HTML:" in line for line in lines)
        assert any("- headings: ✓" in line for line in lines)
        assert any("- lists: ✓" in line for line in lines)
        assert any("- img: ✓" in line for line in lines)
        assert any("- a: ✓" in line for line in lines)
        assert any("- table: ✗" in line for line in lines)
        
        # Deve conter JUSTIFICATIVA (novo campo padronizado)
        assert any("Justificativa:" in line for line in lines)
        assert any("Estrutura HTML adequada mas CSS poderia ser melhorado" in line for line in lines)
        
        # Deve conter PROBLEMAS (novo campo padronizado)
        assert any("Problemas:" in line for line in lines)
        assert any("CSS muito básico" in line for line in lines)
        assert any("Falta responsividade" in line for line in lines)

    def test_generate_feedback_without_analysis(self):
        """Testa geração de feedback quando não há análise de IA."""
        from src.domain.models import IndividualSubmission
        
        # Cria submissão sem análise
        submission = IndividualSubmission(
            github_login="test_user",
            assignment_name="test-assignment",
            turma="test-turma",
            submission_path=Path(".")
        )
        
        # Cria assignment Python
        assignment = Assignment(
            name="test-assignment",
            type=AssignmentType.PYTHON,
            submission_type=SubmissionType.INDIVIDUAL,
            description="Test assignment"
        )
        
        # Gera feedback
        service = CorrectionService(Path("."), Path("."), verbose=False)
        feedback = service._generate_feedback(submission, assignment)
        
        # Deve retornar string vazia ou apenas informações básicas
        assert isinstance(feedback, str)
        # Não deve conter campos de análise
        assert "Análise de código:" not in feedback
        assert "Análise HTML/CSS:" not in feedback
        assert "Justificativa:" not in feedback
        assert "Problemas:" not in feedback


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


class TestHTMLThumbnails:
    """Testes para a funcionalidade de thumbnails HTML."""
    
    @pytest.mark.thumbnails
    def test_html_thumbnail_service_initialization(self):
        """Testa inicialização do serviço de thumbnails HTML."""
        from src.services.html_thumbnail_service import HTMLThumbnailService
        
        # Testa com diretório padrão
        service = HTMLThumbnailService()
        assert service.output_dir == Path("reports/visual/thumbnails")
        
        # Testa com diretório customizado
        custom_dir = Path("test_html_thumbnails")
        service = HTMLThumbnailService(custom_dir)
        assert service.output_dir == custom_dir
        
        # Verifica se o diretório foi criado
        assert custom_dir.exists()
        
        # Limpa após o teste
        import shutil
        shutil.rmtree(custom_dir)
    
    @pytest.mark.thumbnails
    def test_html_thumbnail_service_debug_print(self):
        """Testa funcionalidade de debug do serviço HTML."""
        from src.services.html_thumbnail_service import HTMLThumbnailService
        
        # Testa sem verbose
        service = HTMLThumbnailService(verbose=False)
        # Não deve gerar erro
        service._debug_print("Test message")
        
        # Testa com verbose
        service_verbose = HTMLThumbnailService(verbose=True)
        # Não deve gerar erro
        service_verbose._debug_print("Test message")
    
    @pytest.mark.thumbnails
    def test_html_thumbnail_service_file_not_found(self):
        """Testa tratamento de erro quando index.html não existe."""
        from src.services.html_thumbnail_service import HTMLThumbnailService
        from src.domain.models import IndividualSubmission
        
        service = HTMLThumbnailService()
        
        # Cria submissão mock sem index.html
        with tempfile.TemporaryDirectory() as temp_dir:
            submission_path = Path(temp_dir) / "test_submission"
            submission_path.mkdir()
            
            submission = IndividualSubmission(
                github_login="test_user",
                assignment_name="test_assignment",
                turma="test_turma",
                submission_path=submission_path
            )
            
            # Deve gerar erro quando index.html não existe
            with pytest.raises(FileNotFoundError, match="index.html não encontrado"):
                service._capture_submission_thumbnail(submission, "test_assignment", "test_turma")
    
    @pytest.mark.thumbnails
    def test_html_thumbnail_service_with_valid_html(self):
        """Testa serviço com HTML válido (sem captura real)."""
        from src.services.html_thumbnail_service import HTMLThumbnailService
        from src.domain.models import IndividualSubmission
        
        service = HTMLThumbnailService()
        
        # Cria submissão mock com index.html
        with tempfile.TemporaryDirectory() as temp_dir:
            submission_path = Path(temp_dir) / "test_submission"
            submission_path.mkdir()
            
            # Cria index.html básico
            index_html = submission_path / "index.html"
            index_html.write_text("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <h1>Test Content</h1>
                <p>This is a test page.</p>
            </body>
            </html>
            """)
            
            submission = IndividualSubmission(
                github_login="test_user",
                assignment_name="test_assignment",
                turma="test_turma",
                submission_path=submission_path
            )
            
            # Testa que o método não falha na validação inicial
            # (não testamos captura real pois requer Chrome/Selenium)
            try:
                service._capture_submission_thumbnail(submission, "test_assignment", "test_turma")
            except Exception as e:
                # Esperamos erro de Selenium/Chrome, mas não de validação
                assert "index.html não encontrado" not in str(e)
    
    @pytest.mark.thumbnails
    def test_html_thumbnail_service_error_handling(self):
        """Testa tratamento de erros no serviço HTML."""
        from src.services.html_thumbnail_service import HTMLThumbnailService
        from src.domain.models import IndividualSubmission
        
        service = HTMLThumbnailService()
        
        # Cria submissão mock
        with tempfile.TemporaryDirectory() as temp_dir:
            submission_path = Path(temp_dir) / "test_submission"
            submission_path.mkdir()
            
            submission = IndividualSubmission(
                github_login="test_user",
                assignment_name="test_assignment",
                turma="test_turma",
                submission_path=submission_path
            )
            
            # Testa geração de thumbnails com erro
            results = service.generate_thumbnails_for_assignment("test_assignment", "test_turma", [submission])
            
            # Deve retornar um resultado com erro
            assert len(results) == 1
            assert results[0].streamlit_status == "error"
            assert "index.html não encontrado" in results[0].error_message
            assert results[0].submission_identifier == "test_user"
            assert results[0].display_name == "test_user (individual)"


class TestPythonExecutionVisualService:
    """Testes para PythonExecutionVisualService."""
    
    def setup_method(self):
        """Configuração para cada teste."""
        self.service = PythonExecutionVisualService(verbose=False)
        self.temp_dir = Path("tests/temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Remove arquivos temporários
        for file in self.temp_dir.glob("*"):
            if file.is_file():
                file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()
    
    def test_generate_execution_visual_report_success(self):
        """Testa geração bem-sucedida de relatório visual."""
        from src.domain.models import PythonExecutionResult
        from datetime import datetime
        
        # Cria submissões de teste
        submissions = []
        for i in range(2):
            submission = Mock(spec=IndividualSubmission)
            submission.display_name = f"aluno-{i+1}"
            submission.github_login = f"aluno{i+1}"
            
            # Cria execução Python de teste
            execution = PythonExecutionResult(
                submission_identifier=f"aluno{i+1}",
                display_name=f"aluno-{i+1}",
                execution_status="success" if i == 0 else "error",
                stdout_output=f"Saída padrão do aluno {i+1}\nLinha 2\nLinha 3",
                stderr_output=f"Erro do aluno {i+1}" if i == 1 else "",
                execution_time=1.5 + i,
                return_code=0 if i == 0 else 1,
                execution_timestamp=datetime.now().isoformat()
            )
            submission.python_execution = execution
            submissions.append(submission)
        
        # Gera relatório
        result_path = self.service.generate_execution_visual_report(
            "test-assignment", "test-turma", submissions, self.temp_dir
        )
        
        # Verifica se o arquivo foi criado
        assert result_path.exists()
        assert result_path.name == "test-assignment_test-turma_execution_visual.html"
        
        # Verifica conteúdo do HTML
        content = result_path.read_text(encoding='utf-8')
        assert "Relatório Visual de Execução Python" in content
        assert "test-assignment" in content
        assert "test-turma" in content
        assert "aluno-1" in content
        assert "aluno-2" in content
        assert "Saída padrão do aluno 1" in content
        assert "Erro do aluno 2" in content
    
    def test_generate_execution_visual_report_no_executions(self):
        """Testa erro quando não há execuções Python."""
        # Cria submissões sem execução Python
        submissions = []
        for i in range(2):
            submission = Mock(spec=IndividualSubmission)
            submission.display_name = f"aluno-{i+1}"
            submission.python_execution = None
            submissions.append(submission)
        
        # Deve gerar erro
        with pytest.raises(ValueError, match="Nenhuma submissão com execução Python encontrada"):
            self.service.generate_execution_visual_report(
                "test-assignment", "test-turma", submissions, self.temp_dir
            )
    
    def test_calculate_execution_stats(self):
        """Testa cálculo de estatísticas de execução."""
        # Cria dados de teste
        submissions_with_execution = []
        for i in range(3):
            execution = Mock()
            if i == 0:
                execution.execution_status = "success"
                execution.execution_time = 1.0
            elif i == 1:
                execution.execution_status = "partial_success"
                execution.execution_time = 2.0
            else:
                execution.execution_status = "error"
                execution.execution_time = 3.0
            
            submissions_with_execution.append({'execution': execution})
        
        # Calcula estatísticas
        stats = self.service._calculate_execution_stats(submissions_with_execution)
        
        # Verifica resultados
        assert stats['total_executions'] == 3
        assert stats['successful_executions'] == 1
        assert stats['partial_executions'] == 1
        assert stats['failed_executions'] == 1
        assert stats['success_rate'] == 1/3
        assert stats['avg_execution_time'] == 2.0
    
    def test_format_output_for_display(self):
        """Testa formatação de saída para exibição."""
        # Teste com saída normal
        output = "Linha 1\nLinha 2\nLinha 3"
        formatted = self.service._format_output_for_display(output)
        assert formatted == "Linha 1\nLinha 2\nLinha 3"
        
        # Teste com saída vazia
        formatted = self.service._format_output_for_display("")
        assert formatted == "Nenhuma saída"
        
        # Teste com saída muito longa (deve truncar)
        long_output = "x" * 3000
        formatted = self.service._format_output_for_display(long_output)
        assert len(formatted) < 2100  # Deve ser truncado
        assert "... (saída truncada)" in formatted
        
        # Teste com caracteres especiais (deve escapar HTML)
        special_output = "<script>alert('test')</script>"
        formatted = self.service._format_output_for_display(special_output)
        assert "&lt;script&gt;" in formatted
        assert "&lt;/script&gt;" in formatted
    
    def test_build_execution_visual_html(self):
        """Testa construção do HTML do relatório visual."""
        # Cria dados de teste
        submissions_with_execution = []
        for i in range(1):
            submission = Mock()
            submission.display_name = f"aluno-{i+1}"
            
            execution = Mock()
            execution.execution_status = "success"
            execution.stdout_output = "Saída teste"
            execution.stderr_output = ""
            execution.execution_time = 1.5
            execution.return_code = 0
            execution.execution_timestamp = "2025-01-15T10:30:00"
            
            submissions_with_execution.append({
                'submission': submission,
                'execution': execution,
                'index': 1
            })
        
        execution_stats = {
            'total_executions': 1,
            'successful_executions': 1,
            'partial_executions': 0,
            'failed_executions': 0,
            'success_rate': 1.0,
            'avg_execution_time': 1.5
        }
        
        # Gera HTML
        html = self.service._build_execution_visual_html(
            "test-assignment", "test-turma", submissions_with_execution, execution_stats
        )
        
        # Verifica elementos do HTML
        assert "Relatório Visual de Execução Python" in html
        assert "test-assignment" in html
        assert "test-turma" in html
        assert "aluno-1" in html
        assert "Saída teste" in html
        assert "1.50s" in html
        assert "100.0%" in html  # Taxa de sucesso


