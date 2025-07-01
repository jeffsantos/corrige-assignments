"""
Repositório para gerenciar submissões dos alunos.
"""
from pathlib import Path
from typing import List, Optional
from ..domain.models import IndividualSubmission, GroupSubmission, Submission, Turma, SubmissionType, Assignment


class SubmissionRepository:
    """Repositório para gerenciar submissões dos alunos."""
    
    def __init__(self, respostas_path: Path):
        self.respostas_path = respostas_path
    
    def get_all_turmas(self) -> List[Turma]:
        """Retorna todas as turmas disponíveis."""
        turmas = []
        
        for turma_dir in self.respostas_path.iterdir():
            if turma_dir.is_dir():
                turma = self._load_turma(turma_dir)
                if turma:
                    turmas.append(turma)
        
        return turmas
    
    def get_turma(self, name: str) -> Optional[Turma]:
        """Retorna uma turma específica pelo nome."""
        turma_path = self.respostas_path / name
        if turma_path.exists() and turma_path.is_dir():
            return self._load_turma(turma_path)
        return None
    
    def get_submissions_for_assignment(self, turma_name: str, assignment_name: str) -> List[Submission]:
        """Retorna todas as submissões de um assignment específico de uma turma."""
        submissions = []
        turma_path = self.respostas_path / turma_name
        assignment_submissions_path = turma_path / f"{assignment_name}-submissions"
        
        if not assignment_submissions_path.exists():
            return submissions
        
        for submission_dir in assignment_submissions_path.iterdir():
            if submission_dir.is_dir():
                submission = self._load_submission(submission_dir, turma_name, assignment_name)
                if submission:
                    submissions.append(submission)
        
        return submissions
    
    def get_submission(self, turma_name: str, assignment_name: str, submission_identifier: str) -> Optional[Submission]:
        """Retorna uma submissão específica."""
        turma_path = self.respostas_path / turma_name
        assignment_submissions_path = turma_path / f"{assignment_name}-submissions"
        submission_path = assignment_submissions_path / f"{assignment_name}-{submission_identifier}"
        
        if submission_path.exists() and submission_path.is_dir():
            return self._load_submission(submission_path, turma_name, assignment_name)
        return None
    
    def _load_turma(self, turma_path: Path) -> Optional[Turma]:
        """Carrega uma turma a partir do diretório."""
        assignments = []
        individual_submissions = set()
        group_submissions = set()
        
        for assignment_dir in turma_path.iterdir():
            if assignment_dir.is_dir() and assignment_dir.name.endswith('-submissions'):
                # Remove o sufixo '-submissions' para obter o nome do assignment
                assignment_name = assignment_dir.name[:-12]  # Remove '-submissions'
                assignments.append(assignment_name)
                
                # Coleta identificadores de submissões
                for submission_dir in assignment_dir.iterdir():
                    if submission_dir.is_dir():
                        try:
                            submission_type, identifier = Assignment.parse_submission_identifier(
                                assignment_name, submission_dir.name
                            )
                            if submission_type == SubmissionType.INDIVIDUAL:
                                individual_submissions.add(identifier)
                            else:
                                group_submissions.add(identifier)
                        except ValueError:
                            # Se não conseguir parsear, assume individual
                            individual_submissions.add(submission_dir.name)
        
        return Turma(
            name=turma_path.name,
            assignments=assignments,
            individual_submissions=list(individual_submissions),
            group_submissions=list(group_submissions)
        )
    
    def _load_submission(self, submission_path: Path, turma_name: str, assignment_name: str) -> Optional[Submission]:
        """Carrega uma submissão a partir do diretório."""
        submission_folder_name = submission_path.name
        
        # Determina o tipo de submissão e extrai o identificador
        try:
            submission_type, identifier = Assignment.parse_submission_identifier(
                assignment_name, submission_folder_name
            )
        except ValueError:
            # Se não conseguir parsear, assume individual
            submission_type = SubmissionType.INDIVIDUAL
            identifier = submission_folder_name
        
        # Lista arquivos na submissão
        files = []
        for file_path in submission_path.rglob('*'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(submission_path)))
        
        # Cria o objeto de submissão apropriado
        if submission_type == SubmissionType.INDIVIDUAL:
            return IndividualSubmission(
                github_login=identifier,
                assignment_name=assignment_name,
                turma=turma_name,
                submission_path=submission_path,
                files=files
            )
        else:
            return GroupSubmission(
                group_name=identifier,
                assignment_name=assignment_name,
                turma=turma_name,
                submission_path=submission_path,
                files=files
            )
    
    def get_submissions_by_identifier(self, turma_name: str, identifier: str) -> List[Submission]:
        """Retorna todas as submissões de um identificador específico (aluno ou grupo)."""
        submissions = []
        turma_path = self.respostas_path / turma_name
        
        if not turma_path.exists():
            return submissions
        
        for assignment_dir in turma_path.iterdir():
            if assignment_dir.is_dir() and assignment_dir.name.endswith('-submissions'):
                assignment_name = assignment_dir.name[:-12]
                submission_path = assignment_dir / f"{assignment_name}-{identifier}"
                
                if submission_path.exists() and submission_path.is_dir():
                    submission = self._load_submission(submission_path, turma_name, assignment_name)
                    if submission:
                        submissions.append(submission)
        
        return submissions 