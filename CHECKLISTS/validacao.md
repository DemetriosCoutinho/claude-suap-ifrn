# Checklist de Validação — Fase 4

**Período**: ___________  
**Tipo**: PIT / RIT  
**Data de início da validação**: ___________  
**Responsável**: ___________

---

## Pré-condição

- [ ] Coleta concluída e aprovada (Fase 3 encerrada com OK do usuário).
- [ ] Manifesto em `status: "validando"`.

---

## Para cada documento no manifesto

Percorrer cada entrega em `entregas[]` e marcar:

### Verificação de período

- [ ] O documento menciona explicitamente o semestre/ano correto (ou sua data de emissão cobre o período).
- [ ] Não é uma versão de período anterior reutilizada sem justificativa.

### Verificação de versão

- [ ] É a versão mais recente para este tipo de documento **com evidência** (não apenas por ser o arquivo mais novo).
- [ ] Se há múltiplas versões: a escolhida está registrada em `versao_evidencia` com justificativa explícita.
- [ ] Versões descartadas (se existirem) estão em `_revisar/` ou `_ref/pit_historico/`, não apagadas.

### Verificação de integridade

- [ ] O arquivo abre sem erro (não corrompido, não protegido por senha sem a senha).
- [ ] O conteúdo visível bate com o tipo esperado (ex.: um "disciplinas.pdf" realmente lista disciplinas).
- [ ] Nome do usuário está no documento onde esperado (portaria, ata, declaração, comprovante).

### Verificação de classificação

- [ ] O arquivo está na subpasta canônica correta (ensino / pesquisa / gestao / orientacoes / _ref).
- [ ] Nome do arquivo segue convenção: sem espaços, sem acentos, lowercase ou snake_case.

### Resultado por item

- [ ] Marcar `status_validacao: "valido"` — todos os critérios acima OK.
- [ ] Marcar `status_validacao: "conflito"` — versões concorrentes sem desempate claro.
- [ ] Marcar `status_validacao: "duvida"` — algum critério não pôde ser verificado.
- [ ] Criar entrada em `duvidas[]` para cada item marcado `conflito` ou `duvida`.

---

## Verificação de cobertura do manifesto

- [ ] Todo item obrigatório está `valido` ou tem dúvida registrada em `duvidas[]`.
- [ ] Nenhum item cruzado entre eixos errados.
- [ ] Nenhum arquivo em `_revisar/` esquecido — cada um tem linha em `duvidas[]`.

---

## Ao finalizar a validação

- [ ] Manifesto atualizado com `status: "redigindo"` (somente se **todos** os obrigatórios estiverem `valido`).
- [ ] Lista de conflitos e dúvidas apresentada ao usuário.
- [ ] **Não avançar para redação sem aprovação humana da lista de validações.**
- [ ] Dúvidas resolvidas pelo usuário registradas em `decisoes[]` com data e aprovador.
