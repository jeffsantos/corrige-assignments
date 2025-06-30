"""
Repositório para gerenciar assignments e suas definições.
"""
from pathlib import Path
from typing import List, Optional
import re
from ..domain.models import Assignment, AssignmentType


class AssignmentRepository:
    """Repositório para gerenciar assignments."""
    
    def __init__(self, enunciados_path: Path):
        self.enunciados_path = enunciados_path
    
    def get_all_assignments(self) -> List[Assignment]:
        """Retorna todos os assignments disponíveis."""
        assignments = []
        
        for assignment_dir in self.enunciados_path.iterdir():
            if assignment_dir.is_dir():
                assignment = self._load_assignment(assignment_dir)
                if assignment:
                    assignments.append(assignment)
        
        return assignments
    
    def get_assignment(self, name: str) -> Optional[Assignment]:
        """Retorna um assignment específico pelo nome."""
        assignment_path = self.enunciados_path / name
        if assignment_path.exists() and assignment_path.is_dir():
            return self._load_assignment(assignment_path)
        return None
    
    def _load_assignment(self, assignment_path: Path) -> Optional[Assignment]:
        """Carrega um assignment a partir do diretório."""
        readme_path = assignment_path / "README.md"
        
        if not readme_path.exists():
            return None
        
        # Determina o tipo do assignment baseado no nome
        assignment_type = self._determine_assignment_type(assignment_path.name)
        
        # Lê o README para extrair informações
        description, requirements = self._parse_readme(readme_path)
        
        # Encontra arquivos de teste
        test_files = self._find_test_files(assignment_path)
        
        # Define rubrica padrão baseada no tipo
        rubric = self._get_default_rubric(assignment_type)
        
        return Assignment(
            name=assignment_path.name,
            type=assignment_type,
            description=description,
            requirements=requirements,
            test_files=test_files,
            rubric=rubric,
            path=assignment_path
        )
    
    def _determine_assignment_type(self, assignment_name: str) -> AssignmentType:
        """Determina o tipo do assignment baseado no nome."""
        if "html" in assignment_name.lower():
            return AssignmentType.HTML
        else:
            return AssignmentType.PYTHON
    
    def _parse_readme(self, readme_path: Path) -> tuple[str, List[str]]:
        """Extrai descrição e requisitos do README."""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrai descrição (primeiras linhas até encontrar seção de requisitos)
            lines = content.split('\n')
            description_lines = []
            requirements = []
            
            in_requirements = False
            for line in lines:
                if any(keyword in line.lower() for keyword in ['requisitos', 'critérios', 'avaliação']):
                    in_requirements = True
                    continue
                
                if in_requirements:
                    if line.strip().startswith('-') or line.strip().startswith('*'):
                        requirements.append(line.strip()[1:].strip())
                else:
                    if line.strip() and not line.startswith('#'):
                        description_lines.append(line.strip())
            
            description = ' '.join(description_lines[:5])  # Primeiras 5 linhas como descrição
            return description, requirements
            
        except Exception as e:
            return f"Erro ao ler README: {e}", []
    
    def _find_test_files(self, assignment_path: Path) -> List[str]:
        """Encontra arquivos de teste no assignment."""
        test_files = []
        
        # Procura por arquivos de teste comuns
        test_patterns = ['test_*.py', '*_test.py', 'tests/']
        
        for pattern in test_patterns:
            if pattern.endswith('/'):
                test_dir = assignment_path / pattern[:-1]
                if test_dir.exists() and test_dir.is_dir():
                    for test_file in test_dir.glob('*.py'):
                        test_files.append(str(test_file.relative_to(assignment_path)))
            else:
                for test_file in assignment_path.glob(pattern):
                    test_files.append(str(test_file.relative_to(assignment_path)))
        
        return test_files
    
    def _get_default_rubric(self, assignment_type: AssignmentType) -> dict:
        """Retorna rubrica padrão baseada no tipo de assignment."""
        if assignment_type == AssignmentType.PYTHON:
            return {
                "funcionamento_correto": 0.4,
                "qualidade_codigo": 0.3,
                "documentacao": 0.2,
                "criatividade": 0.1
            }
        else:  # HTML
            return {
                "estrutura_html": 0.4,
                "estilizacao_css": 0.3,
                "responsividade": 0.2,
                "criatividade": 0.1
            } 