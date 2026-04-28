# Checklist de Submissão Assistida — Fase 8

**Período**: ___________  
**Tipo**: PIT / RIT  
**Data de submissão**: ___________  
**Responsável pela confirmação humana**: ___________

---

> **ATENÇÃO**: Esta fase só pode ser executada após confirmação humana explícita de cada item abaixo.
> Claude prepara o pacote e mostra exatamente o que será enviado. O envio em si é feito pelo usuário ou com sua confirmação verbal/escrita explícita.

---

## Pré-condição obrigatória

- [ ] Revisão concluída e aprovada pelo usuário (Fase 7 OK, lista assinada ou aprovada verbalmente).
- [ ] Manifesto em `status: "revisando"`.
- [ ] **Usuário declarou explicitamente: "pode submeter".**

---

## Preparação do pacote

- [ ] Documento final (PIT ou RIT) em versão definitiva identificada e isolada em `_meta/` ou raiz do tipo.
- [ ] Comprovantes necessários para a submissão listados e presentes.
- [ ] Nenhum arquivo de rascunho, versão antiga ou documento de outro período misturado no pacote.
- [ ] Nome do arquivo final segue convenção esperada pelo SUAP (confirmar com o usuário se há exigência específica de nomenclatura).

---

## Verificação antes de enviar

- [ ] Claude mostra ao usuário **exatamente** o que será enviado: lista de arquivos, destino no SUAP, campos preenchidos.
- [ ] Usuário revisou a lista e confirmou. (Sem confirmação → parar aqui.)
- [ ] Nenhum dado pessoal ou sensível não esperado no pacote.

---

## Execução da submissão

- [ ] Login no SUAP realizado (autenticação manual pelo usuário — Claude não guarda senha).
- [ ] Formulário de submissão navegado via Playwright com o usuário acompanhando.
- [ ] Cada campo preenchido mostrado ao usuário antes de avançar para o próximo passo.
- [ ] Revisão final da tela de confirmação do SUAP antes de clicar em "Enviar".
- [ ] **Usuário confirma o envio** (clique final ou instrução explícita "pode clicar").

---

## Após a submissão

- [ ] Comprovante de submissão (tela, e-mail, protocolo) capturado e salvo em `_meta/evidencias/`.
- [ ] Manifesto atualizado: `status: "submetido"` + campo `submissao` preenchido com `data`, `evidencia` (path) e `aprovador_humano`.
- [ ] Arquivamento manual do pacote de evidências (a pasta `periodos/` é gitignored — não commitar).

---

## Regra de ouro

Qualquer dúvida de última hora → parar, não enviar, registrar a dúvida em `duvidas[]`, consultar o usuário.
