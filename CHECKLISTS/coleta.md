# Checklist de Coleta — Fase 3

**Período**: ___________  
**Tipo**: PIT / RIT  
**Data de início da coleta**: ___________  
**Responsável**: ___________

---

## Antes de começar

- [ ] Período-alvo definido e confirmado (ano + semestre).
- [ ] Lista de entregas obrigatórias gerada (Fase 2 concluída).
- [ ] `periodos/AAAA.S/rit/_meta/manifesto.json` criado com `status: "coletando"`.
- [ ] Pasta de destino `periodos/AAAA.S/rit/` criada com subpastas canônicas.

---

## Coleta no SUAP (`https://suap.ifrn.edu.br`)

- [ ] Login realizado (autenticação manual no navegador Playwright — não salvar senha em arquivo).
- [ ] Localizado o PIT aprovado do período → salvo em `_ref/pit.pdf`.
- [ ] Localizado o relatório de disciplinas do período → salvo em `ensino/disciplinas.pdf`.
- [ ] Verificado se há outras seções relevantes no SUAP para o período (pesquisa, extensão, orientação).
- [ ] Cada download registrado no manifesto: campo `origem: "suap"` + data de download.
- [ ] Script de coleta criado/atualizado em `scripts/suap/` para reutilização futura.

---

## Coleta no webmail (`https://webmail.ifrn.edu.br`)

> **Fora do escopo automatizado do plugin** — coleta manual pelo usuário.
> Não existe `scripts/webmail/` neste repo; itens abaixo são feitos manualmente.

- [ ] Login realizado (autenticação manual — não salvar senha em arquivo).
- [ ] Pesquisado por e-mails com assunto/remetente relacionado ao período-alvo.
- [ ] Verificados anexos nas pastas: Entrada, Enviados, e qualquer subpasta de trabalho.
- [ ] Cada anexo relevante: baixado e salvo na subpasta correta do eixo.
- [ ] Cada item registrado no manifesto: campo `origem: "webmail"` + data do e-mail + remetente.

---

## Coleta manual (documentos físicos ou recebidos fora dos sistemas)

- [ ] Documentos recebidos por e-mail pessoal ou WhatsApp identificados e copiados.
- [ ] Documentos escaneados colocados na subpasta correta.
- [ ] Cada item registrado no manifesto: campo `origem: "manual"` + descrição da origem.

---

## Verificação de cobertura

- [ ] Todos os itens obrigatórios do manifesto têm `arquivo` preenchido (não `null`).
- [ ] Itens auxiliares e opcionais: cada um com status explícito (`pendente`, `não encontrado`, `não aplicável`).
- [ ] Nenhum arquivo está duplicado entre eixos.
- [ ] Nenhum arquivo de período diferente foi baixado junto.

---

## Ao finalizar a coleta

- [ ] Manifesto atualizado com `status: "validando"`.
- [ ] Lista de itens ainda pendentes registrada em `duvidas[]` do manifesto.
- [ ] Comunicar ao usuário o que falta antes de avançar para a Fase 4.
- [ ] **Não avançar para validação sem aprovação humana da lista de pendências.**
