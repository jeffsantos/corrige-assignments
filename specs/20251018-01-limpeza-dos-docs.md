Tarefa: Limpeza e Atualização dos Documentos Markdown

Descrição:

Ao longo do desenvolvimento do projeto definimos vários arquivos markdown que documentam o sistema e suas funcionalidades. Com o tempo, alguns ficaram muito extensos e repetitivos, enquanto outros ficaram desatualizados. Vamos proceder uma limpeza e atualização dos documentos produzidos. Algumas referências: 

- README.md
  - Esse é a fonte principal de informações, ponto de partida para usuários-finais e para desenvolvedores, mas ficou longo e repetitivo. Os exemplos de comandos e suas variações se repetem em várias partes do documento. 
- CLAUDE.md
  - Repetitivo com o README.md e com o contexto.md, que era usado antes da sua criação. Precisa verificar necessidade de atualização após as últimas implementações. 
- contexto.md
  - Era usado antes da criação do CLAUDE.md. Devemos avaliar se há algum conteúdo relevante nele que pode ser movido para outro lugar e removê-lo. 
- docs/sistema-notas.md
  - Documenta mudanças no cálculo de notas. Pode estar desatualizado depois das últimas mudanças. 
- docs/solucao-scraping-llm.md
  - Documenta uma decisão específica na implementação da funcionalidade de scraping para assignments que tenham esse componente. Pode estar desatualizado depois das últimas mudanças. 

Além dos arquivos markdown há também o script example_usage.py que também serve como um tipo de documentação, mas que também precisa ser avaliado quanto à atualização dos exemplos. 

---
### Ajustes

1. O comando mais importante é o comando de execução completa das correções (correct-all-with-visual). Ele deveria aparecer como exemplo no CLAUDE.md e no README.md. 

2. No CLAUDE.md, o setup do ambiente aparece no meio dos exemplos de comandos. Seria melhor mantê-los em seções diferentes. 

3. O README.md ainda permanece muito grande (mais de 400 linhas). O ideal é que ele seja uma apresentação resumido do projeto, dê os exemplos de uso mais comuns e resuma a implementação técnica para desenvolvedores interessados. Podemos separar os detalhes para arquivos específicos na pasta de documentação. Talvez, com isso, essa pasta e os markdowns já existentes precisem ser renomeados para manter um padrão como os novos arquivos que serão criados para o desmembramento do README.md.  