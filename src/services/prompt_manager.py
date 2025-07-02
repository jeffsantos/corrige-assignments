"""
Gerenciador de prompts específicos por assignment.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from ..domain.models import Assignment


class PromptManager:
    """Gerencia prompts específicos para cada assignment."""
    
    def __init__(self, enunciados_path: Path):
        self.enunciados_path = enunciados_path
        # Caminho para a pasta de prompts na raiz do projeto
        self.prompts_path = Path(__file__).parent.parent.parent / "prompts"
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Carrega templates de prompt padrão."""
        return {
            "python": self._get_default_python_prompt(),
            "html": self._get_default_html_prompt()
        }
    
    def _get_default_python_prompt(self) -> str:
        """Template padrão para análise de código Python."""
        return """Analise o código Python abaixo para o assignment "{assignment_name}".

DESCRIÇÃO DO ASSIGNMENT:
{assignment_description}

REQUISITOS ESPECÍFICOS:
{assignment_requirements}

ESTRUTURA ESPERADA (do enunciado):
{expected_structure}

ARQUIVOS FORNECIDOS NO ENUNCIADO:
{provided_files}

CÓDIGO DO ENUNCIADO:
{enunciado_code}

CÓDIGO DO ALUNO:
{student_code}

INSTRUÇÕES DE AVALIAÇÃO:
{assessment_criteria}

Por favor, analise o código considerando:
1. Se o aluno seguiu a estrutura e requisitos específicos do assignment
2. Se implementou corretamente as funcionalidades solicitadas
3. Se manteve a qualidade do código (quando não fornecido no enunciado)
4. Se adicionou valor além do que foi fornecido no enunciado

Formate sua resposta assim:
NOTA: [número de 0 a 10]
JUSTIFICATIVA: [justificativa resumida e clara da nota]
COMENTARIOS: [lista de comentários sobre pontos positivos]
SUGESTOES: [lista de sugestões de melhoria]
PROBLEMAS: [lista de problemas encontrados]"""

    def _get_default_html_prompt(self) -> str:
        """Template padrão para análise de código HTML."""
        return """Analise o código HTML/CSS abaixo para o assignment "{assignment_name}".

DESCRIÇÃO DO ASSIGNMENT:
{assignment_description}

REQUISITOS ESPECÍFICOS:
{assignment_requirements}

ESTRUTURA ESPERADA (do enunciado):
{expected_structure}

ARQUIVOS FORNECIDOS NO ENUNCIADO:
{provided_files}

CÓDIGO DO ENUNCIADO:
{enunciado_code}

CÓDIGO DO ALUNO:
{student_code}

INSTRUÇÕES DE AVALIAÇÃO:
{assessment_criteria}

Por favor, analise o código considerando:
1. Se o aluno seguiu a estrutura e requisitos específicos do assignment
2. Se implementou corretamente os elementos HTML/CSS solicitados
3. Se manteve a qualidade do código (quando não fornecido no enunciado)
4. Se adicionou valor além do que foi fornecido no enunciado

Formate sua resposta assim:
NOTA: [número de 0 a 10]
JUSTIFICATIVA: [justificativa resumida e clara da nota]
ELEMENTOS: [lista de elementos HTML encontrados/ausentes]
COMENTARIOS: [lista de comentários sobre pontos positivos]
SUGESTOES: [lista de sugestões de melhoria]
PROBLEMAS: [lista de problemas encontrados]"""

    def get_assignment_prompt(self, assignment: Assignment, assignment_type: str, 
                            student_code: str, assessment_criteria: str = "") -> str:
        """Gera o prompt específico para um assignment."""
        
        # Tenta carregar prompt personalizado do assignment
        custom_prompt = self._load_custom_prompt(assignment.name)
        
        if custom_prompt:
            # Usa prompt personalizado
            return self._format_custom_prompt(custom_prompt, assignment, student_code)
        else:
            # Usa template padrão
            return self._format_default_prompt(assignment, assignment_type, student_code, assessment_criteria)
    
    def _load_custom_prompt(self, assignment_name: str) -> Optional[str]:
        """Carrega prompt personalizado do assignment se existir."""
        # Primeiro tenta na pasta prompts/ (versionada)
        prompt_file = self.prompts_path / assignment_name / "prompt.txt"
        
        if prompt_file.exists():
            try:
                return prompt_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"⚠️  Erro ao ler prompt personalizado para {assignment_name}: {e}")
        
        # Fallback: tenta na pasta enunciados/ (não versionada)
        prompt_file = self.enunciados_path / assignment_name / "prompt.txt"
        
        if prompt_file.exists():
            try:
                return prompt_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"⚠️  Erro ao ler prompt personalizado para {assignment_name}: {e}")
        
        return None
    
    def _format_custom_prompt(self, prompt_template: str, assignment: Assignment, student_code: str) -> str:
        """Formata prompt personalizado."""
        return prompt_template.format(
            assignment_name=assignment.name,
            assignment_description=assignment.description,
            assignment_requirements="\n".join(f"- {req}" for req in assignment.requirements),
            enunciado_code=self._read_enunciado_code(assignment.name),
            student_code=student_code
        )
    
    def _format_default_prompt(self, assignment: Assignment, assignment_type: str, 
                              student_code: str, assessment_criteria: str) -> str:
        """Formata prompt usando template padrão."""
        
        # Lê README.md do enunciado
        readme_content = self._read_assignment_readme(assignment.name)
        
        # Analisa estrutura esperada
        expected_structure = self._analyze_expected_structure(assignment.name)
        
        # Lista arquivos fornecidos no enunciado
        provided_files = self._list_provided_files(assignment.name)
        
        template = self.prompt_templates.get(assignment_type, self.prompt_templates["python"])
        
        return template.format(
            assignment_name=assignment.name,
            assignment_description=assignment.description,
            assignment_requirements="\n".join(f"- {req}" for req in assignment.requirements),
            expected_structure=expected_structure,
            provided_files=provided_files,
            enunciado_code=self._read_enunciado_code(assignment.name),
            student_code=student_code,
            assessment_criteria=assessment_criteria or "Avalie se o aluno seguiu corretamente os requisitos e estrutura especificados."
        )
    
    def _read_assignment_readme(self, assignment_name: str) -> str:
        """Lê o README.md do enunciado do assignment."""
        readme_file = self.enunciados_path / assignment_name / "README.md"
        
        if readme_file.exists():
            try:
                content = readme_file.read_text(encoding="utf-8")
                # Remove seções de infraestrutura (GitHub Classroom, etc.)
                return self._clean_readme_content(content)
            except Exception as e:
                print(f"⚠️  Erro ao ler README.md para {assignment_name}: {e}")
        
        return "README.md não encontrado."
    
    def _clean_readme_content(self, content: str) -> str:
        """Remove seções de infraestrutura do README."""
        lines = content.split('\n')
        cleaned_lines = []
        skip_section = False
        
        for line in lines:
            # Pula seções de infraestrutura
            if any(keyword in line.lower() for keyword in ['.github', '.devcontainer', '.gitignore', 'codespace']):
                skip_section = True
                continue
            
            # Para de pular quando encontra nova seção
            if line.startswith('#') and skip_section:
                skip_section = False
            
            if not skip_section:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _analyze_expected_structure(self, assignment_name: str) -> str:
        """Analisa a estrutura esperada baseada nos arquivos do enunciado."""
        assignment_path = self.enunciados_path / assignment_name
        
        if not assignment_path.exists():
            return "Estrutura não encontrada."
        
        structure_info = []
        
        # Lista arquivos e pastas (excluindo infraestrutura)
        for item in assignment_path.iterdir():
            if item.name.startswith('.'):
                continue  # Pula arquivos ocultos
            
            if item.is_file():
                structure_info.append(f"- Arquivo: {item.name}")
            elif item.is_dir():
                structure_info.append(f"- Pasta: {item.name}/")
        
        if structure_info:
            return "Estrutura esperada:\n" + "\n".join(structure_info)
        else:
            return "Nenhuma estrutura específica definida."
    
    def _list_provided_files(self, assignment_name: str) -> str:
        """Lista arquivos fornecidos no enunciado (excluindo infraestrutura)."""
        assignment_path = self.enunciados_path / assignment_name
        
        if not assignment_path.exists():
            return "Arquivos não encontrados."
        
        provided_files = []
        
        for item in assignment_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                relative_path = item.relative_to(assignment_path)
                provided_files.append(f"- {relative_path}")
        
        if provided_files:
            return "Arquivos fornecidos no enunciado:\n" + "\n".join(provided_files)
        else:
            return "Nenhum arquivo fornecido no enunciado."
    
    def _read_enunciado_code(self, assignment_name: str) -> str:
        """Lê o código fornecido no enunciado do assignment."""
        assignment_dir = self.enunciados_path / assignment_name
        
        if not assignment_dir.exists():
            return "Diretório do assignment não encontrado."
        
        code_files = []
        
        # Lê arquivos Python
        for py_file in assignment_dir.rglob("*.py"):
            if py_file.is_file():
                try:
                    content = py_file.read_text(encoding="utf-8")
                    rel_path = py_file.relative_to(assignment_dir)
                    code_files.append(f"# {rel_path}\n{content}\n")
                except Exception as e:
                    code_files.append(f"# {rel_path} - Erro ao ler: {e}\n")
        
        # Lê arquivos HTML
        for html_file in assignment_dir.rglob("*.html"):
            if html_file.is_file():
                try:
                    content = html_file.read_text(encoding="utf-8")
                    rel_path = html_file.relative_to(assignment_dir)
                    code_files.append(f"<!-- {rel_path} -->\n{content}\n")
                except Exception as e:
                    code_files.append(f"<!-- {rel_path} - Erro ao ler: {e} -->\n")
        
        # Lê arquivos CSS
        for css_file in assignment_dir.rglob("*.css"):
            if css_file.is_file():
                try:
                    content = css_file.read_text(encoding="utf-8")
                    rel_path = css_file.relative_to(assignment_dir)
                    code_files.append(f"/* {rel_path} */\n{content}\n")
                except Exception as e:
                    code_files.append(f"/* {rel_path} - Erro ao ler: {e} */\n")
        
        if not code_files:
            return "Nenhum código fornecido no enunciado (arquivos vazios ou não encontrados)."
        
        return "\n".join(code_files) 