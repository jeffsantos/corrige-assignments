Tarefa: Redefinir o workflow de spec no CLAUDE.md

Descrição: 

Vamos seguir o workflow abaixo para lidar com as specs: 

## Workflow com Especificações (Specs)

### Criando Specs
- Formato: `specs/yyyymmdd-99-titulo-curto.md` (99 = sequencial 01, 02, ...)
- Backlog: `specs/backlog.md` para implementações futuras

### Respondendo a Specs
1. Ler `specs/yyyymmdd-99-titulo.md`
2. Executar tarefas/análises solicitadas
3. **SEMPRE criar** `specs/yyyymmdd-99-titulo-RESPOSTA.md` contendo:
   - Análise detalhada
   - Decisões técnicas
   - Resultados de testes/validações
   - Arquivos modificados com linhas relevantes
4. **SEMPRE comitar** após concluir a resposta da spec:
   - Incluir a spec original, resposta e todos os arquivos relacionados
   - Usar mensagem de commit descritiva seguindo Conventional Commits
   - Exemplo: `docs(specs): adiciona resposta da spec XX - título-da-spec`

### Aplicando Ajustes a Specs
1. **SEMPRE atualizar** o arquivo `-RESPOSTA.md` correspondente
2. Documentar cada ajuste em nova seção
3. Manter histórico cronológico completo
4. **SEMPRE comitar** os ajustes com mensagem descritiva referenciando a spec

Isso deve ser registrado no CLAUDE.md para ser lembrado nas interações futuras. 

---
### Ajustes

1. As primeiras specs desse projeto foram criadas antes da regra que acabamos de estabelecer e, portanto, não possuem arquivos de resposta. Para mantermos o padrão estabelecido, seria possível criar os arquivos de resposta faltante a partir dos logs de commits associados às primeiras specs?