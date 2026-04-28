# CRITERIOS_VALIDACAO.md — Critérios de validação documental

Base da **Fase 4** do pipeline. Para cada tipo de documento, define o que torna um arquivo válido para o período, de onde ele vem e quais sinais indicam problema.

**Regra geral**: um documento só recebe `status_validacao: "valido"` no manifesto quando **todos** os critérios abaixo para o seu tipo estiverem satisfeitos. Em caso de dúvida, marcar `"duvida"` e registrar a questão em `duvidas[]`.

---

## 1. PIT aprovado

**O que é**: versão final aprovada do Planejamento Individual de Trabalho para o período.

**Origem típica**: SUAP (download direto do sistema), eventualmente webmail.

**Critérios de validade**:
- [ ] Contém o nome do período correto (ano e semestre) no documento ou nos metadados.
- [ ] Tem registro de aprovação (assinatura digital, carimbo, status "aprovado" no SUAP, ou comunicação de aprovação por e-mail).
- [ ] Não é uma versão "recusado" ou "em análise".
- [ ] É a versão mais recente entre as versões do período (registrar todas em `_ref/pit_historico/`).

**Sinais de alerta**:
- Nome do arquivo contém "recusado", "v1", "v2" sem "aprovado" → verificar.
- Arquivo mais antigo que a data de início do período → pode ser do semestre anterior.
- Múltiplos arquivos com "pit" no nome para o mesmo período → tratar como conflito, listar todos.

---

## 2. Requerimento e histórico de versões do PIT

**O que é**: formulário de solicitação de aprovação do PIT e versões anteriores (recusadas).

**Origem típica**: webmail (enviado/recebido), SUAP.

**Critérios de validade**:
- [ ] Período do requerimento corresponde ao período-alvo.
- [ ] Há correspondência clara entre o requerimento e o PIT submetido junto.
- [ ] Se houver versões recusadas: todas ficam em `_ref/pit_historico/` com sufixo `_v1_recusado`, `_v2_recusado` etc.
- [ ] A versão aprovada é a última da sequência.

**Sinais de alerta**:
- Requerimento sem data ou com data de período diferente.
- Versão "aprovada" com data anterior à de uma versão "recusada".

---

## 3. Disciplinas ministradas

**O que é**: plano de ensino, diário de classe ou relatório de disciplinas do período.

**Origem típica**: SUAP.

**Critérios de validade**:
- [ ] Lista disciplinas pertencentes ao período-alvo.
- [ ] Inclui nome da disciplina, carga horária e turma(s).
- [ ] Não mistura disciplinas de semestres anteriores ou futuros.

**Sinais de alerta**:
- Nome do arquivo com typo (`discplinas.pdf`) → renomear; registrar nome original no manifesto.
- Arquivo com data de modificação muito fora do período → investigar antes de marcar válido.

---

## 4. Portaria NDE

**O que é**: portaria de nomeação dos membros do Núcleo Docente Estruturante.

**Origem típica**: SUAP ou e-mail da coordenação / diretoria.

**Critérios de validade**:
- [ ] Nome do usuário consta como membro nomeado.
- [ ] Vigência da portaria cobre o período-alvo (portarias NDE costumam valer vários semestres).
- [ ] Número da portaria e data de emissão são legíveis.

**Sinais de alerta**:
- Portaria de período antigo usada em período atual sem confirmação de vigência → verificar com coordenação.
- Portaria de curso ao qual o usuário não está vinculado.

---

## 5. Ata de colegiado

**O que é**: registro oficial de reunião de colegiado de curso.

**Origem típica**: webmail (enviado pela coordenação), SUAP.

**Critérios de validade**:
- [ ] Data da reunião está dentro do período-alvo.
- [ ] Nome do usuário consta como presente (assinatura, lista de presença, ou menção).
- [ ] Identifica o curso e a instância (colegiado do curso correspondente).

**Sinais de alerta**:
- Ata de colegiado de curso ao qual o usuário não está vinculado → esclarecer antes de incluir.
- Múltiplas atas sem confirmação de quais pertencem ao período.

---

## 6. PAF

**O que é**: `[confirmar com usuário]` — sigla encontrada em alguns comprovantes de gestão. Significado e exigência variam conforme contexto institucional.

**Origem típica**: SUAP ou e-mail. `[confirmar]`

**Critérios de validade**: `[a definir após confirmação do tipo]`

**Sinais de alerta**: `[a definir após confirmação]`

---

## 7. Comprovante de pesquisa (projeto / orientação de IC)

**O que é**: documento que comprova participação em projeto de pesquisa ou orientação de iniciação científica.

**Origem típica**: SUAP (portaria do projeto, declaração de participação), webmail.

**Critérios de validade**:
- [ ] Nome do usuário consta no documento como participante ou coordenador.
- [ ] Projeto mencionado está ativo no período-alvo (datas de início e fim cobrindo o semestre).
- [ ] Tipo de participação está claro (orientador, membro, coordenador).

**Sinais de alerta**:
- Comprovante de projeto com datas fora do período-alvo → investigar se há renovação ou continuação.
- Múltiplos comprovantes de projetos similares → listar todos e perguntar quais incluir.

---

## 8. Declaração de docência

**O que é**: declaração emitida por coordenação ou diretoria atestando exercício das funções docentes.

**Origem típica**: webmail, entregue pessoalmente (escaneada).

**Critérios de validade**:
- [ ] Emitida no período-alvo ou cobrindo-o.
- [ ] Assinada por autoridade competente (coordenador, diretor).
- [ ] Identifica o usuário pelo nome e matrícula ou CPF.

**Sinais de alerta**:
- Declaração genérica sem período específico → verificar se é suficiente para o SUAP.
- Declaração de docência em turno diferente do atual → confirmar se ainda é válida.

---

## 9. Comprovante de orientação (TCC, estágio, banca)

**O que é**: documento que comprova orientação ou participação em banca de TCC ou estágio supervisionado.

**Origem típica**: SUAP, webmail, documento assinado escaneado.

**Critérios de validade**:
- [ ] Nome do usuário consta como orientador ou membro de banca.
- [ ] Nome do orientando e título do trabalho estão presentes.
- [ ] Data de defesa ou período de orientação está dentro do período-alvo.
- [ ] Tipo de atividade está claro (TCC, estágio, IC, integrado).

**Sinais de alerta**:
- Banca com data fora do período → verificar se conta para este período ou para o anterior.
- Comprovante de orientação sem data → não promover a válido sem investigação.

---

## 10. Comprovante de extensão

**O que é**: documento que comprova atividade de extensão (participação em projeto, evento ou ação de extensão).

**Origem típica**: SUAP, webmail, certificado emitido pela instituição.

**Critérios de validade**:
- [ ] Atividade ocorreu durante o período-alvo.
- [ ] Nome do usuário consta no documento.
- [ ] Tipo de participação é identificado (coordenador, colaborador, palestrante etc.).

**Sinais de alerta**:
- Certificado de evento externo sem menção ao usuário como participante da instituição.
- Data do evento fora do período-alvo sem justificativa de enquadramento.

---

## Como usar esta tabela

1. Para cada entrega do `manifesto.json`, identificar o tipo de documento.
2. Checar um a um os critérios acima.
3. Só marcar `"status_validacao": "valido"` se **todos** os critérios passarem.
4. Registrar no campo `versao_evidencia` o raciocínio: "portaria datada de 2021 — confirmado com coordenação em DD/MM/AAAA que ainda está vigente".
5. Em caso de dúvida, criar entrada em `duvidas[]` e marcar `"status_validacao": "duvida"`.

Este arquivo é evolutivo. Novos tipos de documento devem ser adicionados quando encontrados.
