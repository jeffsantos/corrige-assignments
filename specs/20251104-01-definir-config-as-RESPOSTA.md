# Resposta: Spec 20251104-01 - Definir parâmetros no config.py para o assignment da AS

## Análise Realizada

Analisei os arquivos do assignment `prog2-as` para entender suas características e necessidades de configuração:

### Estrutura do Assignment prog2-as

O assignment é uma prova substitutiva (AS) composta de 3 partes:

1. **Parte 1 - Banco de Dados** (`bd.sql`)
   - Criação de banco PostgreSQL com 3-4 tabelas
   - Relacionamento N:N
   - Tabela de cidades obrigatória

2. **Parte 2 - Aplicação de Terminal** (`main.py`)
   - Aplicação interativa que consulta API de previsão do tempo
   - Solicita input do usuário (nome da cidade)
   - Exibe previsão do tempo usando Brasil API (CPTEC)
   - Workflow: input cidade → API busca código → API retorna previsão → exibe `condicao_desc`

3. **Parte 3 - Dashboard Streamlit** (`app_streamlit.py`)
   - Dashboard com integração banco + API
   - Tabela com JOIN exibindo cidades
   - Coluna adicional com previsão do tempo em tempo real
   - Filtros interativos e gráficos

## Configurações Adicionadas

### 1. Tipo de Submissão (config.py:50)

```python
"prog2-as": SubmissionType.INDIVIDUAL,  # Prova substitutiva (AS)
```

**Justificativa**: É uma prova individual (AS - Atividade Substitutiva).

### 2. Geração de Thumbnails (config.py:60)

```python
"prog2-as": "streamlit",  # Prova substitutiva (AS) com dashboard
```

**Justificativa**: Possui dashboard Streamlit (`app_streamlit.py`) que deve ter screenshots capturados.

### 3. Arquivo Streamlit (config.py:70)

```python
"prog2-as": "app_streamlit.py",
```

**Justificativa**: O arquivo do dashboard é `app_streamlit.py` (não o padrão `main.py`), conforme especificado no README.md.

### 4. Execução Python (config.py:81)

```python
"prog2-as": True,  # Prova substitutiva (AS) com aplicação de terminal
```

**Justificativa**: Possui aplicação de terminal (`main.py`) que deve ser executada para captura de output.

### 5. Configuração Interativa (config.py:116-124)

```python
"prog2-as": {
    "python_file": "main.py",
    "command_args": [],
    "inputs": [
        "São Paulo"  # Nome da cidade para consulta de previsão do tempo
    ],
    "timeout": 30,
    "expected_outputs": ["previsão", "tempo", "clima", "condição", "nublado", "sol", "chuva"]
}
```

**Justificativa**:
- A aplicação `main.py` é interativa e requer input do usuário
- Não possui argumentos de linha de comando (`command_args: []`)
- Input único: nome de uma cidade brasileira
- Expected outputs: termos relacionados a condições climáticas que devem aparecer na saída

## Validação

A configuração está completa e alinhada com o padrão já utilizado para outros assignments similares:

- ✅ Tipo de submissão definido
- ✅ Thumbnails configurados para Streamlit
- ✅ Arquivo Streamlit customizado especificado
- ✅ Execução Python habilitada
- ✅ Parâmetros interativos configurados

## Arquivos Modificados

- `config.py` (linhas 50, 60, 70, 81, 116-124): Adicionadas todas as configurações necessárias para o assignment `prog2-as`

## Conclusão

O assignment `prog2-as` está agora completamente parametrizado no `config.py`, permitindo:
- Correção automática com execução da aplicação de terminal
- Geração de thumbnails do dashboard Streamlit
- Execução interativa com inputs simulados
- Validação de outputs esperados
