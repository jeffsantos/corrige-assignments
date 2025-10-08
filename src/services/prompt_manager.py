"""
Gerenciador de prompts específicos por assignment.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
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

- Penalize a nota e aponte como PROBLEMA se o código não mostrar nada no terminal, mesmo sem erro.
- NÃO avalie se as tags HTML, classes CSS ou seletores usados no scraping estão "corretos" baseado no conhecimento sobre as páginas originais. Esses elementos podem mudar e não são critério de avaliação. O que importa é se o código funciona e produz o resultado esperado.

"""

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

ELEMENTOS: [lista de elementos HTML encontrados/ausentes]

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

- Penalize a nota e aponte como PROBLEMA se o código não mostrar nada no terminal, mesmo sem erro.
- NÃO avalie se as tags HTML, classes CSS ou seletores usados no scraping estão "corretos" baseado no conhecimento sobre as páginas originais. Esses elementos podem mudar e não são critério de avaliação. O que importa é se o código funciona e produz o resultado esperado.

"""

    def get_assignment_prompt(self, assignment: Assignment, assignment_type: str,
                            student_code: str, assessment_criteria: str = "", python_execution: Optional[Any] = None, test_results: Optional[List[Any]] = None, streamlit_thumbnail: Optional[Any] = None) -> str:
        """Gera o prompt específico para um assignment."""
        
        # Tenta carregar prompt personalizado do assignment
        custom_prompt = self._load_custom_prompt(assignment.name)
        
        if custom_prompt:
            # Usa prompt personalizado
            return self._format_custom_prompt(custom_prompt, assignment, student_code, python_execution, test_results, streamlit_thumbnail)
        else:
            # Usa template padrão
            return self._format_default_prompt(assignment, assignment_type, student_code, assessment_criteria, python_execution, test_results, streamlit_thumbnail)
    
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
    
    def _format_custom_prompt(self, prompt_template: str, assignment: Assignment, student_code: str, python_execution: Optional[Any] = None, test_results: Optional[List[Any]] = None, streamlit_thumbnail: Optional[Any] = None) -> str:
        """Formata prompt personalizado."""
        # Escapa chaves no código do aluno para evitar conflitos com .format()
        escaped_student_code = student_code.replace('{', '{{').replace('}', '}}')
        escaped_enunciado_code = self._read_enunciado_code(assignment.name).replace('{', '{{').replace('}', '}}')

        formatted_prompt = prompt_template.format(
            assignment_name=assignment.name,
            assignment_description=assignment.description,
            assignment_requirements="\n".join(f"- {req}" for req in assignment.requirements),
            enunciado_code=escaped_enunciado_code,
            student_code=escaped_student_code
        )
        
        # Adiciona informações sobre a execução do código se disponível
        if python_execution:
            execution_info = f"""

RESULTADO DA EXECUÇÃO DO CÓDIGO:
Status: {python_execution.execution_status}
Tempo de execução: {python_execution.execution_time:.2f} segundos
Código de retorno: {python_execution.return_code}

--- Output do terminal (stdout): ---
{python_execution.stdout_output}
--- Fim do stdout ---

--- Erros do terminal (stderr): ---
{python_execution.stderr_output}
--- Fim do stderr ---

"""
            formatted_prompt += execution_info
        
        # Adiciona informações sobre os resultados dos testes se disponível
        if test_results:
            test_info = f"""

RESULTADO DOS TESTES:
Total de testes: {len(test_results)}
Testes que passaram: {sum(1 for test in test_results if test.result.value == 'passed')}
Testes que falharam: {sum(1 for test in test_results if test.result.value == 'failed')}
Testes com erro: {sum(1 for test in test_results if test.result.value == 'error')}

Detalhes dos testes:\n"""
            for test in test_results:
                status_emoji = "✅" if test.result.value == 'passed' else "❌" if test.result.value == 'failed' else "⚠️"
                test_info += f"{status_emoji} {test.test_name} ({test.result.value.upper()})"
                if test.message:
                    test_info += f" - {test.message}"
                if hasattr(test, 'execution_time') and test.execution_time > 0:
                    test_info += f" ({test.execution_time:.3f}s)"
                test_info += "\n"
            test_info += "\n"
            formatted_prompt += test_info

        # Adiciona informações sobre erros do Streamlit se disponível
        if streamlit_thumbnail and hasattr(streamlit_thumbnail, 'streamlit_exceptions') and streamlit_thumbnail.streamlit_exceptions:
            streamlit_errors_info = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ERROS CRÍTICOS DE EXECUÇÃO DO STREAMLIT 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status da aplicação: {streamlit_thumbnail.streamlit_status.upper()}

⛔ A aplicação Streamlit FALHOU DURANTE A EXECUÇÃO com os seguintes erros:

"""
            for idx, error in enumerate(streamlit_thumbnail.streamlit_exceptions, 1):
                streamlit_errors_info += f"━━━ ERRO {idx} (CRÍTICO) ━━━\n{error}\n\n"

            streamlit_errors_info += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 **INSTRUÇÕES OBRIGATÓRIAS PARA AVALIAÇÃO** 🚨

1. ⛔ ERROS DE EXECUÇÃO = FUNCIONALIDADE NÃO FUNCIONA
   - Se o Streamlit apresenta erros, o dashboard NÃO está funcional
   - Testes estáticos podem passar, mas a aplicação FALHA na execução real
   - Um dashboard que não funciona NÃO pode receber nota alta

2. 📊 **PESO DOS ERROS DE EXECUÇÃO**:
   - Dashboard com erros de execução = máximo 5.0 pontos (50% da nota)
   - Para cada erro de execução, reduza 1-2 pontos dependendo da gravidade
   - Erros que impedem a aplicação de carregar = redução de 3-4 pontos

3. ⚖️ **CALIBRAÇÃO DE NOTAS COM ERROS DE EXECUÇÃO**:
   - Dashboard NÃO FUNCIONA (erros críticos) = nota máxima 5.0
   - Dashboard PARCIALMENTE funcional (erros menores) = nota máxima 7.0
   - Dashboard TOTALMENTE funcional (sem erros) = nota até 10.0

4. ❌ **CLASSIFIQUE ERROS DE EXECUÇÃO COMO PROBLEMAS CRÍTICOS**:
   - TODOS os erros de execução devem ir na seção PROBLEMAS
   - Descreva cada erro como problema crítico que impede funcionamento
   - NÃO minimize a gravidade: "aplicação não funciona" é PROBLEMA, não sugestão

5. 🎯 **EXEMPLO DE AVALIAÇÃO CORRETA**:
   ```
   NOTA: 4.0
   JUSTIFICATIVA: Embora o código esteja estruturado e os testes passem, a aplicação Streamlit apresenta erros CRÍTICOS de execução que impedem seu funcionamento. Um dashboard que não executa não atende aos requisitos da prova.

   PROBLEMAS:
   - Dashboard Streamlit apresenta erro de execução crítico (KeyError/AttributeError/etc)
   - Aplicação não carrega e não pode ser utilizada
   - Funcionalidade principal do dashboard comprometida
   ```

⚠️ LEMBRE-SE: Código que não executa = código que não funciona = NOTA BAIXA
Não dê nota alta para código que apresenta erros de execução, mesmo que pareça bem escrito!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            formatted_prompt += streamlit_errors_info

        # Adiciona instruções críticas sobre execução e testes se houver execução ou testes
        if python_execution or test_results or (streamlit_thumbnail and streamlit_thumbnail.streamlit_exceptions):
            instructions = """

=== INSTRUÇÕES CRÍTICAS SOBRE EXECUÇÃO E TESTES ===

⚠️ **REGRA FUNDAMENTAL**: AVALIE APENAS O QUE O CÓDIGO FAZ, NÃO COMO ELE FAZ!
- Sempre considere o resultado dos testes e da execução do código na sua avaliação.
- O campo \"Output do terminal (stdout)\" deve mostrar algo relevante. Se estiver vazio, isso indica que o programa não produziu nenhuma saída, o que é um erro lógico para aplicações de terminal.
- O campo \"Erros do terminal (stderr)\" deve estar vazio. Se houver mensagens aqui, o código apresentou erros de execução.
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

✅ **O QUE AVALIAR**:
- Se o código roda sem erros
- Se exibe output no terminal
- Se passa nos testes automatizados

**LEMBRE-SE**: O que importa é se o código FUNCIONA e produz RESULTADO, não como ele chega nesse resultado!

=== INSTRUÇÕES ESPECÍFICAS PARA SCRAPING ===

🚨 **SE ESTE FOR UM ASSIGNMENT DE SCRAPING**: AVALIE APENAS O RESULTADO FINAL!

⚠️ **PROIBIDO TOTALMENTE EM SCRAPING**:
- ❌ NÃO avalie se os seletores CSS estão "corretos" ou "incorretos"
- ❌ NÃO critique classes CSS, IDs ou estrutura HTML usados
- ❌ NÃO sugira seletores "melhores" ou "mais apropriados"
- ❌ NÃO avalie se a estrutura HTML corresponde ao que você conhece da página
- ❌ NÃO mencione que "a página deveria ter tabela" ou "deveria usar classes específicas"
- ❌ NÃO desconsidere dados extraídos só porque usou método diferente do esperado

✅ **O QUE AVALIAR EM SCRAPING**:
- ✅ O código roda sem erros?
- ✅ Extrai os dados solicitados?
- ✅ Retorna no formato correto?
- ✅ Exibe output no terminal no formato especificado?
- ✅ Passa nos testes automatizados?

📊 **CRITÉRIOS DE NOTA PARA SCRAPING**:
- **NOTA 10**: Código roda + extrai todos os dados + formato correto + passa testes
- **NOTA 8-9**: Código roda + extrai dados (mesmo com pequenos problemas) + formato correto
- **NOTA 6-7**: Código roda + extrai alguns dados + formato parcialmente correto
- **NOTA 4-5**: Código roda mas não extrai dados corretos
- **NOTA 0-3**: Código não roda ou não extrai nada

🎯 **EXEMPLO DE AVALIAÇÃO CORRETA PARA SCRAPING**:
Se o aluno extrai dados corretos e o código roda sem erro:
- ✅ CORRETO: "Extrai dados corretos e código funciona"
- ❌ INCORRETO: "Usa seletores CSS incorretos, deveria usar tabela"

"""
            formatted_prompt += instructions
        return formatted_prompt
    
    def _format_default_prompt(self, assignment: Assignment, assignment_type: str,
                              student_code: str, assessment_criteria: str, python_execution: Optional[Any] = None, test_results: Optional[List[Any]] = None, streamlit_thumbnail: Optional[Any] = None) -> str:
        """Formata prompt usando template padrão."""
        
        # Lê README.md do enunciado
        readme_content = self._read_assignment_readme(assignment.name)
        
        # Analisa estrutura esperada
        expected_structure = self._analyze_expected_structure(assignment.name)
        
        # Lista arquivos fornecidos no enunciado
        provided_files = self._list_provided_files(assignment.name)
        
        template = self.prompt_templates.get(assignment_type, self.prompt_templates["python"])
        
        formatted_prompt = template.format(
            assignment_name=assignment.name,
            assignment_description=assignment.description,
            assignment_requirements="\n".join(f"- {req}" for req in assignment.requirements),
            expected_structure=expected_structure,
            provided_files=provided_files,
            enunciado_code=self._read_enunciado_code(assignment.name),
            student_code=student_code,
            assessment_criteria=assessment_criteria or "Avalie se o aluno seguiu corretamente os requisitos e estrutura especificados."
        )
        
        # Detecta se é um assignment de scraping
        is_scraping_assignment = self._is_scraping_assignment(assignment)
        
        # Adiciona instruções específicas para scraping se aplicável
        if is_scraping_assignment:
            scraping_instructions = self._get_scraping_instructions()
            formatted_prompt += scraping_instructions
        
        # Adiciona informações sobre a execução do código se disponível
        if python_execution:
            execution_info = f"""

RESULTADO DA EXECUÇÃO DO CÓDIGO:
Status: {python_execution.execution_status}
Tempo de execução: {python_execution.execution_time:.2f} segundos
Código de retorno: {python_execution.return_code}

--- Output do terminal (stdout): ---
{python_execution.stdout_output}
--- Fim do stdout ---

--- Erros do terminal (stderr): ---
{python_execution.stderr_output}
--- Fim do stderr ---

"""
            formatted_prompt += execution_info
        
        # Adiciona informações sobre os resultados dos testes se disponível
        if test_results:
            test_info = f"""

RESULTADO DOS TESTES:
Total de testes: {len(test_results)}
Testes que passaram: {sum(1 for test in test_results if test.result.value == 'passed')}
Testes que falharam: {sum(1 for test in test_results if test.result.value == 'failed')}
Testes com erro: {sum(1 for test in test_results if test.result.value == 'error')}

Detalhes dos testes:\n"""
            for test in test_results:
                status_emoji = "✅" if test.result.value == 'passed' else "❌" if test.result.value == 'failed' else "⚠️"
                test_info += f"{status_emoji} {test.test_name} ({test.result.value.upper()})"
                if test.message:
                    test_info += f" - {test.message}"
                if hasattr(test, 'execution_time') and test.execution_time > 0:
                    test_info += f" ({test.execution_time:.3f}s)"
                test_info += "\n"
            test_info += "\n"
            formatted_prompt += test_info

        # Adiciona informações sobre erros do Streamlit se disponível
        if streamlit_thumbnail and hasattr(streamlit_thumbnail, 'streamlit_exceptions') and streamlit_thumbnail.streamlit_exceptions:
            streamlit_errors_info = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ERROS CRÍTICOS DE EXECUÇÃO DO STREAMLIT 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status da aplicação: {streamlit_thumbnail.streamlit_status.upper()}

⛔ A aplicação Streamlit FALHOU DURANTE A EXECUÇÃO com os seguintes erros:

"""
            for idx, error in enumerate(streamlit_thumbnail.streamlit_exceptions, 1):
                streamlit_errors_info += f"━━━ ERRO {idx} (CRÍTICO) ━━━\n{error}\n\n"

            streamlit_errors_info += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 **INSTRUÇÕES OBRIGATÓRIAS PARA AVALIAÇÃO** 🚨

1. ⛔ ERROS DE EXECUÇÃO = FUNCIONALIDADE NÃO FUNCIONA
   - Se o Streamlit apresenta erros, o dashboard NÃO está funcional
   - Testes estáticos podem passar, mas a aplicação FALHA na execução real
   - Um dashboard que não funciona NÃO pode receber nota alta

2. 📊 **PESO DOS ERROS DE EXECUÇÃO**:
   - Dashboard com erros de execução = máximo 5.0 pontos (50% da nota)
   - Para cada erro de execução, reduza 1-2 pontos dependendo da gravidade
   - Erros que impedem a aplicação de carregar = redução de 3-4 pontos

3. ⚖️ **CALIBRAÇÃO DE NOTAS COM ERROS DE EXECUÇÃO**:
   - Dashboard NÃO FUNCIONA (erros críticos) = nota máxima 5.0
   - Dashboard PARCIALMENTE funcional (erros menores) = nota máxima 7.0
   - Dashboard TOTALMENTE funcional (sem erros) = nota até 10.0

4. ❌ **CLASSIFIQUE ERROS DE EXECUÇÃO COMO PROBLEMAS CRÍTICOS**:
   - TODOS os erros de execução devem ir na seção PROBLEMAS
   - Descreva cada erro como problema crítico que impede funcionamento
   - NÃO minimize a gravidade: "aplicação não funciona" é PROBLEMA, não sugestão

5. 🎯 **EXEMPLO DE AVALIAÇÃO CORRETA**:
   ```
   NOTA: 4.0
   JUSTIFICATIVA: Embora o código esteja estruturado e os testes passem, a aplicação Streamlit apresenta erros CRÍTICOS de execução que impedem seu funcionamento. Um dashboard que não executa não atende aos requisitos da prova.

   PROBLEMAS:
   - Dashboard Streamlit apresenta erro de execução crítico (KeyError/AttributeError/etc)
   - Aplicação não carrega e não pode ser utilizada
   - Funcionalidade principal do dashboard comprometida
   ```

⚠️ LEMBRE-SE: Código que não executa = código que não funciona = NOTA BAIXA
Não dê nota alta para código que apresenta erros de execução, mesmo que pareça bem escrito!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            formatted_prompt += streamlit_errors_info

        # Adiciona instruções críticas sobre execução e testes se houver execução ou testes
        if python_execution or test_results or (streamlit_thumbnail and streamlit_thumbnail.streamlit_exceptions):
            instructions = """

=== INSTRUÇÕES CRÍTICAS SOBRE EXECUÇÃO E TESTES ===

⚠️ **REGRA FUNDAMENTAL**: AVALIE APENAS O QUE O CÓDIGO FAZ, NÃO COMO ELE FAZ!
- Sempre considere o resultado dos testes e da execução do código na sua avaliação.
- O campo \"Output do terminal (stdout)\" deve mostrar algo relevante. Se estiver vazio, isso indica que o programa não produziu nenhuma saída, o que é um erro lógico para aplicações de terminal.
- O campo \"Erros do terminal (stderr)\" deve estar vazio. Se houver mensagens aqui, o código apresentou erros de execução.
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

✅ **O QUE AVALIAR**:
- Se o código roda sem erros
- Se exibe output no terminal
- Se passa nos testes automatizados

**LEMBRE-SE**: O que importa é se o código FUNCIONA e produz RESULTADO, não como ele chega nesse resultado!

=== INSTRUÇÕES ESPECÍFICAS PARA SCRAPING ===

🚨 **SE ESTE FOR UM ASSIGNMENT DE SCRAPING**: AVALIE APENAS O RESULTADO FINAL!

⚠️ **PROIBIDO TOTALMENTE EM SCRAPING**:
- ❌ NÃO avalie se os seletores CSS estão "corretos" ou "incorretos"
- ❌ NÃO critique classes CSS, IDs ou estrutura HTML usados
- ❌ NÃO sugira seletores "melhores" ou "mais apropriados"
- ❌ NÃO avalie se a estrutura HTML corresponde ao que você conhece da página
- ❌ NÃO mencione que "a página deveria ter tabela" ou "deveria usar classes específicas"
- ❌ NÃO desconsidere dados extraídos só porque usou método diferente do esperado

✅ **O QUE AVALIAR EM SCRAPING**:
- ✅ O código roda sem erros?
- ✅ Extrai os dados solicitados?
- ✅ Retorna no formato correto?
- ✅ Exibe output no terminal no formato especificado?
- ✅ Passa nos testes automatizados?

📊 **CRITÉRIOS DE NOTA PARA SCRAPING**:
- **NOTA 10**: Código roda + extrai todos os dados + formato correto + passa testes
- **NOTA 8-9**: Código roda + extrai dados (mesmo com pequenos problemas) + formato correto
- **NOTA 6-7**: Código roda + extrai alguns dados + formato parcialmente correto
- **NOTA 4-5**: Código roda mas não extrai dados corretos
- **NOTA 0-3**: Código não roda ou não extrai nada

🎯 **EXEMPLO DE AVALIAÇÃO CORRETA PARA SCRAPING**:
Se o aluno extrai dados corretos e o código roda sem erro:
- ✅ CORRETO: "Extrai dados corretos e código funciona"
- ❌ INCORRETO: "Usa seletores CSS incorretos, deveria usar tabela"

"""
            formatted_prompt += instructions
        return formatted_prompt
    
    def _is_scraping_assignment(self, assignment: Assignment) -> bool:
        """Detecta se um assignment é de scraping baseado no nome e requisitos."""
        # Lista de assignments conhecidos de scraping
        known_scraping_assignments = [
            "prog1-tarefa-scrap-simples",
            "prog1-tarefa-scrap-yahoo",
            "prog1-prova-av"  # Também é de scraping
        ]
        
        # Verifica se é um assignment conhecido de scraping
        if assignment.name in known_scraping_assignments:
            return True
        
        # Verifica se os requisitos mencionam scraping
        scraping_keywords = ["scraping", "web scraping", "extrair dados", "requests", "beautifulsoup", "bs4"]
        requirements_text = " ".join(assignment.requirements).lower()
        
        return any(keyword in requirements_text for keyword in scraping_keywords)
    
    def _get_scraping_instructions(self) -> str:
        """Retorna as instruções específicas para assignments de scraping."""
        return """

=== INSTRUÇÕES ESPECÍFICAS PARA SCRAPING ===

🚨 **SE ESTE FOR UM ASSIGNMENT DE SCRAPING**: AVALIE APENAS O RESULTADO FINAL!

⚠️ **PROIBIDO TOTALMENTE EM SCRAPING**:
- ❌ NÃO avalie se os seletores CSS estão "corretos" ou "incorretos"
- ❌ NÃO critique classes CSS, IDs ou estrutura HTML usados
- ❌ NÃO sugira seletores "melhores" ou "mais apropriados"
- ❌ NÃO avalie se a estrutura HTML corresponde ao que você conhece da página
- ❌ NÃO mencione que "a página deveria ter tabela" ou "deveria usar classes específicas"
- ❌ NÃO desconsidere dados extraídos só porque usou método diferente do esperado

✅ **O QUE AVALIAR EM SCRAPING**:
- ✅ O código roda sem erros?
- ✅ Extrai os dados solicitados?
- ✅ Retorna no formato correto?
- ✅ Exibe output no terminal no formato especificado?
- ✅ Passa nos testes automatizados?

📊 **CRITÉRIOS DE NOTA PARA SCRAPING**:
- **NOTA 10**: Código roda + extrai todos os dados + formato correto + passa testes
- **NOTA 8-9**: Código roda + extrai dados (mesmo com pequenos problemas) + formato correto
- **NOTA 6-7**: Código roda + extrai alguns dados + formato parcialmente correto
- **NOTA 4-5**: Código roda mas não extrai dados corretos
- **NOTA 0-3**: Código não roda ou não extrai nada

🎯 **EXEMPLO DE AVALIAÇÃO CORRETA PARA SCRAPING**:
Se o aluno extrai dados corretos e o código roda sem erro:
- ✅ CORRETO: "Extrai dados corretos e código funciona"
- ❌ INCORRETO: "Usa seletores CSS incorretos, deveria usar tabela"

"""
    
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
                rel_path = py_file.relative_to(assignment_dir)
                try:
                    content = py_file.read_text(encoding="utf-8")
                    code_files.append(f"# {rel_path}\n{content}\n")
                except Exception as e:
                    code_files.append(f"# {rel_path} - Erro ao ler: {e}\n")

        # Lê arquivos HTML
        for html_file in assignment_dir.rglob("*.html"):
            if html_file.is_file():
                rel_path = html_file.relative_to(assignment_dir)
                try:
                    content = html_file.read_text(encoding="utf-8")
                    code_files.append(f"<!-- {rel_path} -->\n{content}\n")
                except Exception as e:
                    code_files.append(f"<!-- {rel_path} - Erro ao ler: {e} -->\n")

        # Lê arquivos CSS
        for css_file in assignment_dir.rglob("*.css"):
            if css_file.is_file():
                rel_path = css_file.relative_to(assignment_dir)
                try:
                    content = css_file.read_text(encoding="utf-8")
                    code_files.append(f"/* {rel_path} */\n{content}\n")
                except Exception as e:
                    code_files.append(f"/* {rel_path} - Erro ao ler: {e} */\n")

        if not code_files:
            return "Nenhum código fornecido no enunciado (arquivos vazios ou não encontrados)."

        return "\n".join(code_files) 