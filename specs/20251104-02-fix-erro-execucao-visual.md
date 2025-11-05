Tarefa: Corrigir erro ao executar a correção automática com visual

Descrição: 

Executei o seguinte comando no diretório raiz do projeto com o ambiente pipenv carregado (ou seja, dentro do `pipenv shell`): 

```shell
python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025
```

Os logs foram registrados em `logs/2025-11-04/*.json` e os reports gerados em `reports`. Olhando o `visual/prog2-as_ebape-prog-aplic-barra-2025_execution_visual.html` gerado, reparei que várias excuções das aplicações de terminal dos alunos indicaram algum tipo de erro. Vou enumerar alguns casos: 

1) Aluno Brenoall
    - Saída Padrão (STDOUT): Nenhuma saída
    - Saída de Erro (STDERR): Timeout: execução excedeu 30 segundos

2) Aluno dudusampaio1981
    - Saída Padrão (STDOUT): Nenhuma saída 
    - Saída de Erro (STDERR):
        Courtesy Notice:
        Pipenv found itself running within a virtual environment,  so it will 
        automatically use that environment, instead of  creating its own for any 
        project. You can set
        PIPENV_IGNORE_VIRTUALENVS=1 to force pipenv to ignore that environment and 
        create  its own instead.
        You can set PIPENV_VERBOSITY=-1 to suppress this warning.


Rodando o código do aluno 1 manualmente, funciona, pede para o usuário informar corretamente a cidade e apresenta o clima da cidade dentro das opções esperadas no arquivo config.py. Não entendi porque a execução não foi bem sucedida nesse caso

O código do aluno 2 está em branco, como foi entregue no enunciado (apenas um import). Isso deveria gerar uma execução sem erro e vazia (nenhum output no terminal), mas estamos, ao invés, apresentando um caso de erro.  

---
### Ajustes

1. Rodei novamente o mesmo comando. Os arquivos html gerados permanecem com o mesmo problema relatado na spec.