Tarefa: Retirar a tarefa de dar nota pela IA, deixá-la apenas gerando um parecer

Descrição:

No modelo atual implementado no código (`src`), a correção do trabalho pela IA (API Open AI) produz uma nota de correção da IA que é persistida no json e apresentada nos htmls dos relatórios de execução. Gostaria de remover essa característica: ou seja, a IA continua gerando sua avaliação dos trabalhos, exatamente como está fazendo hoje, mas não entrega uma nota final, deixando essa decisão para o professor. 