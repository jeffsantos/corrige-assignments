"""
Serviço para análise de código usando IA (OpenAI).
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import OpenAI
from ..domain.models import CodeAnalysis, HTMLAnalysis, Assignment
from .prompt_manager import PromptManager
from config import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
import re


class AIAnalyzer:
    """Serviço para análise de código usando IA."""
    
    def __init__(self, api_key: str = None, enunciados_path: Path = None, logs_path: Path = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Busca na home do usuário
            secrets_path = Path.home() / ".secrets" / "open-ai-api-key.txt"
            if secrets_path.exists():
                try:
                    self.api_key = secrets_path.read_text(encoding="utf-8").strip()
                    # Remove quebras de linha, espaços e caracteres de controle
                    self.api_key = "".join(char for char in self.api_key if char.isprintable() or char == '-')
                    print(f"✅ Chave da OpenAI carregada de: {secrets_path}")
                except Exception as e:
                    print(f"⚠️  Erro ao ler chave da OpenAI em {secrets_path}: {e}")
        
        # Busca no diretório do projeto
        if not self.api_key:
            project_secrets_path = Path(".secrets") / "open-ai-api-key.txt"
            if project_secrets_path.exists():
                try:
                    self.api_key = project_secrets_path.read_text(encoding="utf-8").strip()
                    # Remove quebras de linha, espaços e caracteres de controle
                    self.api_key = "".join(char for char in self.api_key if char.isprintable() or char == '-')
                    print(f"✅ Chave da OpenAI carregada de: {project_secrets_path}")
                except Exception as e:
                    print(f"⚠️  Erro ao ler chave da OpenAI em {project_secrets_path}: {e}")
        
        self.ai_available = bool(self.api_key)
        
        if self.ai_available:
            self.client = OpenAI(api_key=self.api_key)
            print(f"🤖 OpenAI API configurada com sucesso (chave: {self.api_key[:10]}...{self.api_key[-4:]})")
        else:
            print("⚠️  OpenAI API key não configurada. A análise de IA será limitada.")
        
        # Inicializa o gerenciador de prompts
        self.prompt_manager = PromptManager(enunciados_path) if enunciados_path else None
        
        # Configuração de logs
        self.logs_path = logs_path or Path("logs")
        self.logs_path.mkdir(exist_ok=True)
        
        # Caminho para enunciados (usado para ler código do enunciado)
        self.enunciados_path = enunciados_path
    
    def _save_ai_log(self, assignment_name: str, submission_identifier: str, 
                    analysis_type: str, prompt: str, response: str, 
                    parsed_result: Dict[str, Any]) -> None:
        """
        Salva log da análise da IA para auditoria.
        
        Args:
            assignment_name: Nome do assignment
            submission_identifier: Identificador da submissão (login ou grupo)
            analysis_type: Tipo de análise ('python' ou 'html')
            prompt: Prompt enviado para a IA
            response: Resposta raw da IA
            parsed_result: Resultado processado da análise
        """
        try:
            # Cria estrutura de diretórios: logs/YYYY-MM-DD/assignment_name/
            today = datetime.now().strftime("%Y-%m-%d")
            log_dir = self.logs_path / today / assignment_name
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo de log
            timestamp = datetime.now().strftime("%H-%M-%S")
            log_filename = f"{submission_identifier}_{analysis_type}_{timestamp}.json"
            log_file = log_dir / log_filename
            
            # Dados do log
            log_data = {
                "metadata": {
                    "assignment_name": assignment_name,
                    "submission_identifier": submission_identifier,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "ai_model": OPENAI_MODEL
                },
                "prompt": prompt,
                "raw_response": response,
                "parsed_result": parsed_result
            }
            
            # Salva o log
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Log salvo: {log_file}")
            
        except Exception as e:
            print(f"⚠️  Erro ao salvar log: {e}")
    
    def analyze_python_code(self, submission_path: Path, assignment: Assignment, python_execution: Optional[Any] = None, test_results: Optional[List[Any]] = None) -> CodeAnalysis:
        """Analisa código Python usando IA com prompt específico do assignment."""
        if not self.ai_available:
            return self._analyze_python_code_basic(submission_path, assignment)
        
        # Lê os arquivos Python da submissão
        python_files = self._read_python_files(submission_path)
        
        if not python_files:
                    return CodeAnalysis(
            score=0.0,
            score_justification="Nenhum arquivo Python encontrado para análise",
            comments=["Nenhum arquivo Python encontrado"],
            issues_found=["Arquivos Python ausentes"]
        )
        
        # Constrói o prompt específico para o assignment
        if self.prompt_manager:
            prompt = self.prompt_manager.get_assignment_prompt(
                assignment=assignment,
                assignment_type="python",
                student_code=self._format_python_files(python_files),
                python_execution=python_execution,
                test_results=test_results
            )
        else:
            # Fallback para prompt genérico
            prompt = self._build_python_analysis_prompt(python_files, assignment, python_execution, test_results)
        
        try:
            # Chama a API do OpenAI
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um professor experiente de Python analisando código de alunos. Seja construtivo e específico, considerando os requisitos específicos do assignment."},
                    {"role": "user", "content": prompt}
                ]
                #max_tokens=OPENAI_MAX_TOKENS,
                #temperature=OPENAI_TEMPERATURE
            )
            
            # Processa a resposta
            analysis_text = response.choices[0].message.content
            parsed_result = self._parse_python_analysis(analysis_text)
            
            # Salva log da análise
            submission_identifier = submission_path.name.split('-', 1)[1] if '-' in submission_path.name else submission_path.name
            self._save_ai_log(
                assignment_name=assignment.name,
                submission_identifier=submission_identifier,
                analysis_type="python",
                prompt=prompt,
                response=analysis_text,
                parsed_result={
                    "score": parsed_result.score,
                    "score_justification": parsed_result.score_justification,
                    "comments": parsed_result.comments,
                    "suggestions": parsed_result.suggestions,
                    "issues_found": parsed_result.issues_found
                }
            )
            
            return parsed_result
            
        except Exception as e:
            return CodeAnalysis(
                score=0.0,
                score_justification=f"Erro na análise de IA: {str(e)}",
                comments=[f"Erro na análise de IA: {str(e)}"],
                issues_found=["Falha na análise automática"]
            )
    
    def analyze_html_code(self, submission_path: Path, assignment: Assignment) -> HTMLAnalysis:
        """Analisa código HTML usando IA com prompt específico do assignment."""
        if not self.ai_available:
            return self._analyze_html_code_basic(submission_path, assignment)
        
        # Lê os arquivos HTML e CSS da submissão
        html_files = self._read_html_files(submission_path)
        css_files = self._read_css_files(submission_path)
        
        if not html_files:
                    return HTMLAnalysis(
            score=0.0,
            score_justification="Nenhum arquivo HTML encontrado para análise",
            comments=["Nenhum arquivo HTML encontrado"],
            issues_found=["Arquivos HTML ausentes"]
        )
        
        # Constrói o prompt específico para o assignment
        if self.prompt_manager:
            prompt = self.prompt_manager.get_assignment_prompt(
                assignment=assignment,
                assignment_type="html",
                student_code=self._format_html_files(html_files, css_files)
            )
        else:
            # Fallback para prompt genérico
            prompt = self._build_html_analysis_prompt(html_files, css_files, assignment)
        
        try:
            # Chama a API do OpenAI
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um professor experiente de HTML/CSS analisando páginas web de alunos. Seja construtivo e específico, considerando os requisitos específicos do assignment."},
                    {"role": "user", "content": prompt}
                ]
                #max_tokens=OPENAI_MAX_TOKENS,
                #temperature=OPENAI_TEMPERATURE
            )
            
            # Processa a resposta
            analysis_text = response.choices[0].message.content
            parsed_result = self._parse_html_analysis(analysis_text)
            
            # Salva log da análise
            submission_identifier = submission_path.name.split('-', 1)[1] if '-' in submission_path.name else submission_path.name
            self._save_ai_log(
                assignment_name=assignment.name,
                submission_identifier=submission_identifier,
                analysis_type="html",
                prompt=prompt,
                response=analysis_text,
                parsed_result={
                    "score": parsed_result.score,
                    "required_elements": parsed_result.required_elements,
                    "comments": parsed_result.comments,
                    "suggestions": parsed_result.suggestions,
                    "issues_found": parsed_result.issues_found
                }
            )
            
            return parsed_result
            
        except Exception as e:
            return HTMLAnalysis(
                score=0.0,
                score_justification=f"Erro na análise de IA: {str(e)}",
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
    
    def _build_python_analysis_prompt(self, python_files: Dict[str, str], assignment: Assignment, python_execution: Optional[Any] = None, test_results: Optional[List[Any]] = None) -> str:
        """Constrói o prompt para análise de código Python."""
        # Lê código do enunciado se disponível
        enunciado_code = self._read_enunciado_code(assignment.name)
        
        prompt = f"""
Analise o código Python abaixo para o assignment "{assignment.name}".

Descrição do assignment:
{assignment.description}

Requisitos:
{chr(10).join(f"- {req}" for req in assignment.requirements)}

CÓDIGO DO ENUNCIADO:
{enunciado_code}

CÓDIGO DO ALUNO:
"""
        
        for filename, content in python_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        # Adiciona informações sobre a execução do código se disponível
        if python_execution:
            prompt += f"""

RESULTADO DA EXECUÇÃO DO CÓDIGO:
Status: {python_execution.execution_status}
Tempo de execução: {python_execution.execution_time:.2f} segundos
Código de retorno: {python_execution.return_code}

Output do terminal (stdout):
{python_execution.stdout_output}

Erros do terminal (stderr):
{python_execution.stderr_output}

"""
        
        # Adiciona informações sobre os resultados dos testes se disponível
        if test_results:
            prompt += f"""

RESULTADO DOS TESTES:
Total de testes: {len(test_results)}
Testes que passaram: {sum(1 for test in test_results if test.result.value == 'passed')}
Testes que falharam: {sum(1 for test in test_results if test.result.value == 'failed')}
Testes com erro: {sum(1 for test in test_results if test.result.value == 'error')}

Detalhes dos testes:
"""
            for test in test_results:
                status_emoji = "✅" if test.result.value == 'passed' else "❌" if test.result.value == 'failed' else "⚠️"
                prompt += f"{status_emoji} {test.test_name} ({test.result.value.upper()})"
                if test.message:
                    prompt += f" - {test.message}"
                if test.execution_time > 0:
                    prompt += f" ({test.execution_time:.3f}s)"
                prompt += "\n"
            
            prompt += "\n"
        
        # Adiciona instruções críticas sobre execução e testes
        prompt += """
=== INSTRUÇÕES CRÍTICAS SOBRE EXECUÇÃO E TESTES ===

⚠️ **REGRA FUNDAMENTAL**: AVALIE APENAS O QUE O CÓDIGO FAZ, NÃO COMO ELE FAZ!
- Sempre considere o resultado dos testes e da execução do código na sua avaliação.
- O campo "Output do terminal (stdout)" deve mostrar algo relevante. Se estiver vazio, isso indica que o programa não produziu nenhuma saída, o que é um erro lógico para aplicações de terminal.
- O campo "Erros do terminal (stderr)" deve estar vazio. Se houver mensagens aqui, o código apresentou erros de execução.
- Se ambos os campos estiverem vazios, o código rodou sem erro, mas não produziu nenhuma saída — isso deve ser considerado um problema grave, pois toda aplicação de terminal deve exibir alguma informação ao usuário.
- Penalize a nota e aponte como PROBLEMA se o código não mostrar nada no terminal, mesmo sem erro.

🚫 **PROIBIDO AVALIAR**:
- NÃO avalie se as tags HTML, classes CSS ou seletores usados no scraping estão "corretos" baseado no seu conhecimento sobre as páginas originais
- NÃO critique seletores CSS específicos como "incorretos" 
- NÃO sugira seletores "melhores" ou "mais corretos"
- NÃO avalie se a estrutura HTML extraída corresponde ao que você espera da página original
- NÃO sugira revisar, ajustar ou corrigir seletores CSS
- Esses elementos podem mudar constantemente e NÃO são critério de avaliação

⚠️ **IMPORTANTE**: Não repita o mesmo problema múltiplas vezes. Se um dado não foi extraído corretamente, mencione apenas UMA vez como problema.

📊 **CALIBRAÇÃO DE NOTAS**:
- Se o código roda, exibe output e passa nos testes, mas apenas UM campo específico não foi extraído corretamente, considere uma nota entre 7-8
- Se múltiplos campos não foram extraídos ou o código não funciona, aplique penalização maior
- Se o código funciona perfeitamente mas tem pequenos problemas de formatação, considere nota 9-10
- Se o código roda sem erros
- Se exibe output no terminal
- Se passa nos testes automatizados

**LEMBRE-SE**: O que importa é se o código FUNCIONA e produz RESULTADO, não como ele chega nesse resultado!

=== CRITÉRIOS FUNDAMENTAIS DE AVALIAÇÃO ===

**DEFINIÇÃO DE PROBLEMAS vs SUGESTÕES:**

**PROBLEMAS (só inclua aqui se for CRÍTICO):**
- Requisitos OBRIGATÓRIOS do enunciado que estão AUSENTES ou INCORRETOS
- Funções obrigatórias que não foram implementadas ou não funcionam
- Estrutura de código que não segue o especificado no enunciado
- Funcionalidades essenciais que não operam corretamente

**SUGESTÕES (inclua aqui melhorias opcionais):**
- Melhorias de código que não são obrigatórias
- Otimizações de performance que não afetam funcionalidade
- Adições de funcionalidades extras que enriquecem mas não são exigidas
- Melhorias de legibilidade ou organização não obrigatórias
- Sugestões de boas práticas que não são requisitos

**EXEMPLOS DE CLASSIFICAÇÃO:**
- ❌ PROBLEMA: "Função obrigatória não foi implementada" (se for obrigatória)
- ✅ SUGESTÃO: "Poderia adicionar mais tratamento de erros"
- ❌ PROBLEMA: "Estrutura de arquivos não segue o especificado" (se for obrigatório)
- ✅ SUGESTÃO: "Poderia melhorar a organização do código"

=== FORMATO DE RESPOSTA ===

Formate sua resposta EXATAMENTE assim:

NOTA: [número de 0 a 10]
JUSTIFICATIVA: [justificativa resumida e clara da nota]

COMENTARIOS: [lista de comentários sobre pontos positivos]

SUGESTOES: [lista de sugestões de melhoria - apenas melhorias opcionais]

PROBLEMAS: [lista de problemas encontrados - apenas requisitos obrigatórios ausentes/incorretos]

=== REGRAS CRÍTICAS ===

1. **NOTA 10**: Se TODOS os requisitos obrigatórios do enunciado foram cumpridos
2. **PROBLEMAS**: Só inclua requisitos OBRIGATÓRIOS ausentes/incorretos
3. **SUGESTÕES**: Inclua melhorias opcionais e aperfeiçoamentos
4. **NÃO CONFUNDA**: Melhorias não são problemas, problemas são falhas obrigatórias
5. **BASEIE A NOTA**: Nos requisitos do enunciado, não em suas preferências pessoais

Por favor, analise o código considerando:
1. Se o aluno seguiu a estrutura e requisitos específicos do assignment
2. Se implementou corretamente as funcionalidades solicitadas
3. Se manteve a qualidade do código (quando não fornecido no enunciado)
4. Se adicionou valor além do que foi fornecido no enunciado
"""
        
        return prompt
    
    def _build_html_analysis_prompt(self, html_files: Dict[str, str], css_files: Dict[str, str], assignment: Assignment) -> str:
        """Constrói o prompt para análise de código HTML."""
        # Lê código do enunciado se disponível
        enunciado_code = self._read_enunciado_code(assignment.name)
        
        prompt = f"""
Analise o código HTML/CSS abaixo para o assignment "{assignment.name}".

Descrição do assignment:
{assignment.description}

Requisitos:
{chr(10).join(f"- {req}" for req in assignment.requirements)}

CÓDIGO DO ENUNCIADO:
{enunciado_code}

CÓDIGO DO ALUNO:
"""
        
        for filename, content in html_files.items():
            prompt += f"\n--- {filename} ---\n{content}\n"
        
        if css_files:
            prompt += "\nArquivos CSS:\n"
            for filename, content in css_files.items():
                prompt += f"\n--- {filename} ---\n{content}\n"
        
        prompt += """
=== CRITÉRIOS FUNDAMENTAIS DE AVALIAÇÃO ===

**DEFINIÇÃO DE PROBLEMAS vs SUGESTÕES:**

**PROBLEMAS (só inclua aqui se for CRÍTICO):**
- Requisitos OBRIGATÓRIOS do enunciado que estão AUSENTES ou INCORRETOS
- Elementos HTML obrigatórios que não foram implementados
- Estrutura de arquivos que não segue o especificado no enunciado
- Funcionalidades essenciais que não funcionam

**SUGESTÕES (inclua aqui melhorias opcionais):**
- Melhorias de design ou UX que não são obrigatórias
- Otimizações de código que não afetam funcionalidade
- Adições de conteúdo que enriquecem mas não são exigidas
- Melhorias de acessibilidade ou responsividade não obrigatórias
- Sugestões de boas práticas que não são requisitos

**EXEMPLOS DE CLASSIFICAÇÃO:**
- ❌ PROBLEMA: "Falta elemento HTML obrigatório" (se for obrigatório)
- ✅ SUGESTÃO: "Poderia melhorar o design visual"
- ❌ PROBLEMA: "Estrutura de arquivos incorreta" (se for obrigatória)
- ✅ SUGESTÃO: "Poderia adicionar mais responsividade"

=== FORMATO DE RESPOSTA ===

Formate sua resposta EXATAMENTE assim:

NOTA: [número de 0 a 10]
JUSTIFICATIVA: [justificativa resumida e clara da nota]

ELEMENTOS:
- Headings (h1, h2): [Presente/Ausente]
- Lists (ul/ol): [Presente/Ausente]
- Images (img): [Presente/Ausente]
- Links (a): [Presente/Ausente]
- Tables (table): [Presente/Ausente]

COMENTARIOS: [lista de comentários sobre pontos positivos]

SUGESTOES: [lista de sugestões de melhoria - apenas melhorias opcionais]

PROBLEMAS: [lista de problemas encontrados - apenas requisitos obrigatórios ausentes/incorretos]

=== REGRAS CRÍTICAS ===

1. **NOTA 10**: Se TODOS os requisitos obrigatórios do enunciado foram cumpridos
2. **PROBLEMAS**: Só inclua requisitos OBRIGATÓRIOS ausentes/incorretos
3. **SUGESTÕES**: Inclua melhorias opcionais e aperfeiçoamentos
4. **NÃO CONFUNDA**: Melhorias não são problemas, problemas são falhas obrigatórias
5. **BASEIE A NOTA**: Nos requisitos do enunciado, não em suas preferências pessoais

Por favor, analise o código considerando:
1. Se o aluno seguiu a estrutura e requisitos específicos do assignment
2. Se implementou corretamente os elementos HTML/CSS solicitados
3. Se manteve a qualidade do código (quando não fornecido no enunciado)
4. Se adicionou valor além do que foi fornecido no enunciado
"""
        
        return prompt
    
    def _parse_python_analysis(self, analysis_text: str) -> CodeAnalysis:
        """Processa a resposta da IA para análise Python."""
        lines = analysis_text.split('\n')
        score = 0.0
        score_justification = ""
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
            elif line.startswith('JUSTIFICATIVA:'):
                current_section = 'justification'
                score_justification = line.split(':', 1)[1].strip() if ':' in line else ""
            elif line.startswith('COMENTARIOS:') or line.startswith('COMENTÁRIOS:'):
                current_section = 'comments'
            elif line.startswith('SUGESTOES:') or line.startswith('SUGESTÕES:'):
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
            elif line and current_section == 'justification' and not line.startswith('-'):
                # Continua a justificativa se não for um item de lista
                if score_justification:
                    score_justification += " " + line
                else:
                    score_justification = line
        
        return CodeAnalysis(
            score=score,
            score_justification=score_justification,
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        )
    
    def _parse_html_analysis(self, analysis_text: str) -> HTMLAnalysis:
        """Processa a resposta da IA para análise HTML."""
        lines = analysis_text.split('\n')
        score = 0.0
        score_justification = ""
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
            elif line.startswith('JUSTIFICATIVA:'):
                current_section = 'justification'
                score_justification = line.split(':', 1)[1].strip() if ':' in line else ""
            elif line.startswith('ELEMENTOS:'):
                current_section = 'elements'
                # Processa elementos que podem estar na mesma linha após ELEMENTOS:
                elements_text = line.split(':', 1)[1].strip() if ':' in line else ""
                if elements_text:
                    self._parse_elements_line(elements_text, required_elements)
            elif line.startswith('COMENTARIOS:') or line.startswith('COMENTÁRIOS:'):
                current_section = 'comments'
            elif line.startswith('SUGESTOES:') or line.startswith('SUGESTÕES:'):
                current_section = 'suggestions'
            elif line.startswith('PROBLEMAS:'):
                current_section = 'issues'
            elif line and current_section and line.startswith('-'):
                item = line[1:].strip()
                if current_section == 'elements':
                    # Processa elementos HTML em formato de lista
                    self._parse_elements_line(item, required_elements)
                elif current_section == 'comments':
                    comments.append(item)
                elif current_section == 'suggestions':
                    suggestions.append(item)
                elif current_section == 'issues':
                    issues.append(item)
            elif line and current_section == 'justification' and not line.startswith('-'):
                # Continua a justificativa se não for um item de lista
                if score_justification:
                    score_justification += " " + line
                else:
                    score_justification = line
            elif line and current_section == 'elements' and not line.startswith('-') and line:
                # Processa elementos que podem estar em linhas separadas sem hífen
                self._parse_elements_line(line, required_elements)
        
        return HTMLAnalysis(
            score=score,
            score_justification=score_justification,
            required_elements=required_elements,
            comments=comments,
            suggestions=suggestions,
            issues_found=issues
        )
    
    def _parse_elements_line(self, line: str, required_elements: Dict[str, bool]) -> None:
        """Processa uma linha de elementos HTML para extrair status de presença."""
        # Remove parênteses e conteúdo dentro deles
        line = re.sub(r'\([^)]*\)', '', line)
        
        # Padrões para detectar elementos e seus status
        element_patterns = [
            # Padrão: "elemento: status" ou "elemento (status)"
            (r'(\w+)\s*[:\(]\s*(presente|encontrado|sim|true|yes)', True),
            (r'(\w+)\s*[:\(]\s*(ausente|não encontrado|não|false|no)', False),
            # Padrão: "elemento" seguido de "Presente" ou "Ausente" na mesma linha
            (r'(\w+).*?(presente|encontrado|sim|true|yes)', True),
            (r'(\w+).*?(ausente|não encontrado|não|false|no)', False),
        ]
        
        # Mapeamento de elementos comuns
        element_mapping = {
            'h1': 'h1', 'h2': 'h2', 'h3': 'h3', 'headings': 'headings',
            'ul': 'ul', 'ol': 'ol', 'lists': 'lists', 'list': 'lists',
            'img': 'img', 'images': 'img', 'image': 'img',
            'a': 'a', 'links': 'a', 'link': 'a',
            'table': 'table', 'tables': 'table'
        }
        
        line_lower = line.lower()
        
        # Verifica padrões específicos
        for pattern, status in element_patterns:
            matches = re.findall(pattern, line_lower)
            for match in matches:
                element_name = match[0].strip()
                if element_name in element_mapping:
                    mapped_element = element_mapping[element_name]
                    required_elements[mapped_element] = status
        
        # Verifica presença de elementos por palavras-chave
        if any(word in line_lower for word in ['h1', 'h2', 'h3', 'headings']):
            if 'headings' not in required_elements:
                required_elements['headings'] = True
        if any(word in line_lower for word in ['ul', 'ol', 'lists', 'list']):
            if 'lists' not in required_elements:
                required_elements['lists'] = True
        if any(word in line_lower for word in ['img', 'images', 'image']):
            if 'img' not in required_elements:
                required_elements['img'] = True
        if any(word in line_lower for word in ['a', 'links', 'link']):
            if 'a' not in required_elements:
                required_elements['a'] = True
        if any(word in line_lower for word in ['table', 'tables']):
            if 'table' not in required_elements:
                required_elements['table'] = True
    
    def _format_python_files(self, python_files: Dict[str, str]) -> str:
        """Formata arquivos Python para o prompt."""
        formatted = ""
        for filename, content in python_files.items():
            formatted += f"\n--- {filename} ---\n{content}\n"
        return formatted
    
    def _format_html_files(self, html_files: Dict[str, str], css_files: Dict[str, str]) -> str:
        """Formata arquivos HTML/CSS para o prompt."""
        formatted = "Arquivos HTML:\n"
        for filename, content in html_files.items():
            formatted += f"\n--- {filename} ---\n{content}\n"
        
        if css_files:
            formatted += "\nArquivos CSS:\n"
            for filename, content in css_files.items():
                formatted += f"\n--- {filename} ---\n{content}\n"
        
        return formatted
    
    def _read_enunciado_code(self, assignment_name: str) -> str:
        """Lê o código fornecido no enunciado do assignment."""
        if not self.enunciados_path:
            return "Caminho para enunciados não configurado."
        
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