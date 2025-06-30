"""
Serviço para análise de código usando IA (OpenAI).
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import openai
from ..domain.models import CodeAnalysis, HTMLAnalysis, Assignment


class AIAnalyzer:
    """Serviço para análise de código usando IA."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Busca na home do usuário
            secrets_path = Path.home() / ".secrets" / "open-ai-api-key.txt"
            if secrets_path.exists():
                try:
                    self.api_key = secrets_path.read_text(encoding="utf-8").strip()
                except Exception as e:
                    print(f"⚠️  Erro ao ler chave da OpenAI em {secrets_path}: {e}")
        self.ai_available = bool(self.api_key)
        
        if self.ai_available:
            openai.api_key = self.api_key
        else:
            print("⚠️  OpenAI API key não configurada. A análise de IA será limitada.")
    
    def analyze_python_code(self, submission_path: Path, assignment: Assignment) -> CodeAnalysis:
        """Analisa código Python usando IA."""
        if not self.ai_available:
            return self._analyze_python_code_basic(submission_path, assignment)
        
        # Lê os arquivos Python da submissão
        python_files = self._read_python_files(submission_path)
        
        if not python_files:
            return CodeAnalysis(
                score=0.0,
                comments=["Nenhum arquivo Python encontrado"],
                issues_found=["Arquivos Python ausentes"]
            )
        
        # Constrói o prompt para análise
        prompt = self._build_python_analysis_prompt(python_files, assignment)
        
        try:
            # Chama a API do OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um professor experiente de Python analisando código de alunos. Seja construtivo e específico."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Processa a resposta
            analysis_text = response.choices[0].message.content
            return self._parse_python_analysis(analysis_text)
            
        except Exception as e:
            return CodeAnalysis(
                score=0.0,
                comments=[f"Erro na análise de IA: {str(e)}"],
                issues_found=["Falha na análise automática"]
            )
    
    def analyze_html_code(self, submission_path: Path, assignment: Assignment) -> HTMLAnalysis:
        """Analisa código HTML usando IA."""
        if not self.ai_available:
            return self._analyze_html_code_basic(submission_path, assignment)
        
        # Lê os arquivos HTML e CSS da submissão
        html_files = self._read_html_files(submission_path)
        css_files = self._read_css_files(submission_path)
        
        if not html_files:
            return HTMLAnalysis(
                score=0.0,
                comments=["Nenhum arquivo HTML encontrado"],
                issues_found=["Arquivos HTML ausentes"]
            )
        
        # Constrói o prompt para análise
        prompt = self._build_html_analysis_prompt(html_files, css_files, assignment)
        
        try:
            # Chama a API do OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um professor experiente de HTML/CSS analisando páginas web de alunos. Seja construtivo e específico."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Processa a resposta
            analysis_text = response.choices[0].message.content
            return self._parse_html_analysis(analysis_text)
            
        except Exception as e:
            return HTMLAnalysis(
                score=0.0,
                comments=[f"Erro na análise de IA: {str(e)}"],
                issues_found=["Falha na análise automática"]
            )
    
    def _analyze_python_code_basic(self, submission_path: Path, assignment: Assignment) -> CodeAnalysis:
        """Análise básica de código Python sem IA."""
        python_files = self._read_python_files(submission_path)
        
        if not python_files:
            return CodeAnalysis(
                score=0.0,
                comments=["Nenhum arquivo Python encontrado"],
                issues_found=["Arquivos Python ausentes"]
            )
        
        # Análise básica baseada em heurísticas
        score = 5.0  # Nota base
        comments = []
        suggestions = []
        issues = []
        
        # Verifica se há arquivos principais
        if any("main.py" in f for f in python_files):
            score += 1.0
            comments.append("Arquivo main.py encontrado")
        else:
            issues.append("Arquivo main.py não encontrado")
        
        # Verifica se há documentação
        for filename, content in python_files.items():
            if '"""' in content or "'''" in content:
                score += 0.5
                comments.append(f"Documentação encontrada em {filename}")
                break
        else:
            suggestions.append("Adicionar docstrings ao código")
        
        # Verifica se há imports
        for filename, content in python_files.items():
            if "import " in content or "from " in content:
                score += 0.5
                comments.append(f"Imports encontrados em {filename}")
                break
        
        return CodeAnalysis(
            score=min(10.0, score),
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        )
    
    def _analyze_html_code_basic(self, submission_path: Path, assignment: Assignment) -> HTMLAnalysis:
        """Análise básica de código HTML sem IA."""
        html_files = self._read_html_files(submission_path)
        css_files = self._read_css_files(submission_path)
        
        if not html_files:
            return HTMLAnalysis(
                score=0.0,
                comments=["Nenhum arquivo HTML encontrado"],
                issues_found=["Arquivos HTML ausentes"]
            )
        
        # Análise básica baseada em heurísticas
        score = 5.0  # Nota base
        comments = []
        suggestions = []
        issues = []
        required_elements = {}
        
        # Verifica elementos HTML obrigatórios
        for filename, content in html_files.items():
            if "<h1" in content:
                required_elements["h1"] = True
                score += 0.5
            if "<h2" in content:
                required_elements["h2"] = True
                score += 0.5
            if "<h3" in content:
                required_elements["h3"] = True
                score += 0.5
            if "<ul>" in content or "<ol>" in content:
                required_elements["lists"] = True
                score += 0.5
            if "<img" in content:
                required_elements["images"] = True
                score += 0.5
            if "<a " in content:
                required_elements["links"] = True
                score += 0.5
            if "<table" in content:
                required_elements["tables"] = True
                score += 0.5
        
        # Verifica se há CSS
        if css_files:
            score += 1.0
            comments.append("Arquivos CSS encontrados")
        else:
            suggestions.append("Adicionar arquivos CSS para estilização")
        
        # Verifica se há index.html
        if any("index.html" in f for f in html_files):
            score += 0.5
            comments.append("Arquivo index.html encontrado")
        else:
            issues.append("Arquivo index.html não encontrado")
        
        return HTMLAnalysis(
            score=min(10.0, score),
            required_elements=required_elements,
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        )
    
    def _read_python_files(self, submission_path: Path) -> Dict[str, str]:
        """Lê todos os arquivos Python da submissão."""
        python_files = {}
        
        for file_path in submission_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                python_files[str(file_path.relative_to(submission_path))] = content
            except Exception as e:
                python_files[str(file_path.relative_to(submission_path))] = f"Erro ao ler arquivo: {str(e)}"
        
        return python_files
    
    def _read_html_files(self, submission_path: Path) -> Dict[str, str]:
        """Lê todos os arquivos HTML da submissão."""
        html_files = {}
        
        for file_path in submission_path.rglob("*.html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                html_files[str(file_path.relative_to(submission_path))] = content
            except Exception as e:
                html_files[str(file_path.relative_to(submission_path))] = f"Erro ao ler arquivo: {str(e)}"
        
        return html_files
    
    def _read_css_files(self, submission_path: Path) -> Dict[str, str]:
        """Lê todos os arquivos CSS da submissão."""
        css_files = {}
        
        for file_path in submission_path.rglob("*.css"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                css_files[str(file_path.relative_to(submission_path))] = content
            except Exception as e:
                css_files[str(file_path.relative_to(submission_path))] = f"Erro ao ler arquivo: {str(e)}"
        
        return css_files
    
    def _build_python_analysis_prompt(self, python_files: Dict[str, str], assignment: Assignment) -> str:
        """Constrói o prompt para análise de código Python."""
        prompt = f"""
Analise o código Python abaixo para o assignment "{assignment.name}".

Descrição do assignment:
{assignment.description}

Requisitos:
{chr(10).join(f"- {req}" for req in assignment.requirements)}

Código do aluno:
"""
        
        for filename, content in python_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += """
Por favor, analise o código e forneça:

1. Uma nota de 0 a 10 (apenas o número)
2. Comentários sobre pontos positivos
3. Sugestões de melhoria
4. Problemas encontrados

Formate sua resposta assim:
NOTA: [número]
COMENTARIOS: [lista de comentários]
SUGESTOES: [lista de sugestões]
PROBLEMAS: [lista de problemas]
"""
        
        return prompt
    
    def _build_html_analysis_prompt(self, html_files: Dict[str, str], css_files: Dict[str, str], assignment: Assignment) -> str:
        """Constrói o prompt para análise de código HTML."""
        prompt = f"""
Analise o código HTML/CSS abaixo para o assignment "{assignment.name}".

Descrição do assignment:
{assignment.description}

Requisitos:
{chr(10).join(f"- {req}" for req in assignment.requirements)}

Arquivos HTML:
"""
        
        for filename, content in html_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        if css_files:
            prompt += "\nArquivos CSS:\n"
            for filename, content in css_files.items():
                prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += """
Por favor, analise o código e forneça:

1. Uma nota de 0 a 10 (apenas o número)
2. Verificação dos elementos HTML obrigatórios (h1, h2, h3, lists, images, links, tables)
3. Comentários sobre pontos positivos
4. Sugestões de melhoria
5. Problemas encontrados

Formate sua resposta assim:
NOTA: [número]
ELEMENTOS: [lista de elementos encontrados/ausentes]
COMENTARIOS: [lista de comentários]
SUGESTOES: [lista de sugestões]
PROBLEMAS: [lista de problemas]
"""
        
        return prompt
    
    def _parse_python_analysis(self, analysis_text: str) -> CodeAnalysis:
        """Processa a resposta da IA para análise Python."""
        lines = analysis_text.split('\n')
        score = 0.0
        comments = []
        suggestions = []
        issues = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('NOTA:'):
                try:
                    score = float(line.split(':')[1].strip())
                except:
                    score = 0.0
            elif line.startswith('COMENTARIOS:'):
                current_section = 'comments'
            elif line.startswith('SUGESTOES:'):
                current_section = 'suggestions'
            elif line.startswith('PROBLEMAS:'):
                current_section = 'issues'
            elif line and current_section and line.startswith('-'):
                item = line[1:].strip()
                if current_section == 'comments':
                    comments.append(item)
                elif current_section == 'suggestions':
                    suggestions.append(item)
                elif current_section == 'issues':
                    issues.append(item)
        
        return CodeAnalysis(
            score=score,
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        )
    
    def _parse_html_analysis(self, analysis_text: str) -> HTMLAnalysis:
        """Processa a resposta da IA para análise HTML."""
        lines = analysis_text.split('\n')
        score = 0.0
        required_elements = {}
        comments = []
        suggestions = []
        issues = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('NOTA:'):
                try:
                    score = float(line.split(':')[1].strip())
                except:
                    score = 0.0
            elif line.startswith('ELEMENTOS:'):
                current_section = 'elements'
            elif line.startswith('COMENTARIOS:'):
                current_section = 'comments'
            elif line.startswith('SUGESTOES:'):
                current_section = 'suggestions'
            elif line.startswith('PROBLEMAS:'):
                current_section = 'issues'
            elif line and current_section and line.startswith('-'):
                item = line[1:].strip()
                if current_section == 'elements':
                    # Processa elementos HTML (ex: "h1: encontrado", "h2: ausente")
                    if ':' in item:
                        element, status = item.split(':', 1)
                        required_elements[element.strip()] = 'encontrado' in status.lower()
                elif current_section == 'comments':
                    comments.append(item)
                elif current_section == 'suggestions':
                    suggestions.append(item)
                elif current_section == 'issues':
                    issues.append(item)
        
        return HTMLAnalysis(
            score=score,
            required_elements=required_elements,
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        ) 