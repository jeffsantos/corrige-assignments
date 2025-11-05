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

2. Após o ajuste 1, parece que agora estamos capturando corretamente a saída da execução dos programas dos alunos. Mas o STDERR continua indicando mensagem ao ambiente pipenv de execução dos programas. Quando indiquei isso na descrição original da spec, a solução dada e registrada no arquivo de resposta foi filtrar as mensanges pipenv da execução dos alunos. Parece que parte da mensagem foi filtrada e outra parte continuou sendo exibida. Essa solução de filtro de mensagens que aplicamos não parece muito robusta. Fiz um backup dos reports da última execução na pasta `reports/2025-11-04`. Os logs estão em `logs/2025-11-04`. 

Acho que identifiquei o problema. Quando rodo o programa de correção de assignments por fora do VS Code, a execução dos alunos é corretamente capturada e nenhum STDERR relativo a ambientes pipenv aparecem. 

**Rodando com pipen run**

```shell
pipenv run python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog2-as --submissao Brenoall
```

**Entrando primeiro no shell do pipenv e rodando o programa na sequência**
```shell
pipenv shell

python -m src.main correct-all-with-visual --turma ebape-prog-aplic-barra-2025 --assignment prog2-as --submissao Brenoall
```

Em ambos os casos, tudo ocorre quando esperado. O problema acontece quando rodo do terminal integrado do VS Code. O terminal integrado primeiro carrega o ambiente python associado ao projeto usando como referência o path que escolhi o Python: Select Interpreter na workspace. Nesse caso, o pipenv carregado para a execução dos programas dos alunos parece ter uma incompatibilidade com a forma que o VS Code carregou o ambiente primário. 

Temos duas alternativas: 

1. Deixar como está e passar a rodar o programa de correção sempre fora do VS Code. Seria bom registrar isso no documento `docs/guia-de-uso.md`. Nesse caso, acho que podemos remover o filtro de mensagens pipenv que adicionamos anteriormente, já que ele não resolveu o problema. 

2. Implementar na execução do ambiente de execução dos trabalhos dos alunos alguma forma de suprimir mensagens quando rodando dentro de outro ambiente previamente carregado. 

A opção mais simples deve ser adotada. 