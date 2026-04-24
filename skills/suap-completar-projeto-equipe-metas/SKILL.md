---
name: suap-completar-projeto-equipe-metas
description: Preenche as abas "Equipe" e "Objetivos específicos" de um projeto de pesquisa já cadastrado no SUAP do IFRN, a partir do PDF do Plano de Trabalho. Filtra a equipe pela coluna Instituição (default IFRN), cadastra alunos como bolsistas e servidores como colaboradores, gera 12 atividades de 30 dias distribuídas entre as metas com responsáveis atribuídos por papel. Usa Playwright com sessão autenticada pelo usuário e NUNCA submete — apenas salva rascunho. Use quando o usuário disser "completar projeto SUAP", "preencher equipe e metas do projeto", "preencher aba equipe do SUAP", "cadastrar metas no SUAP", ou quando tiver um projeto já criado (via skill suap-cadastrar-projeto-edital) e precisar complementar Equipe e Objetivos específicos.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# suap-completar-projeto-equipe-metas

Complemento da skill `suap-cadastrar-projeto-edital`. Enquanto a skill-pai cobre Fases 1–4 (cadastro do formulário principal → Salvar rascunho), esta cobre a **Fase 5 parcial**: duas das cinco pendências pós-salvamento — aba Equipe e aba Objetivos específicos. As outras três pendências (Anexos, Anuência, Classificar TRL) ficam em skills separadas.

## Escopo

- Aba **Equipe** do SUAP: cadastrar membros da equipe com função, carga horária, data de início.
- Aba **Objetivos específicos / Metas**: cadastrar as metas do plano + atividades de 30 dias sob cada meta, com responsável principal e corresponsáveis.

**Fora do escopo** (por design): Anexos, Anuência da chefia, Classificar TRL, valores em R$ em qualquer campo, submissão final.

## Parâmetros

| Nome | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `pasta_dados` | path | — | Pasta base dos seus dados (ex.: `~/Documents/meus-dados-suap/`) |
| `projeto_id` | int | — | ID do projeto no SUAP (URL `/pesquisa/projeto/{id}/`) |
| `pdf_plano` | path | — | Caminho absoluto do Plano de Trabalho em PDF |
| `edital_slug` | string | — | Slug do edital para nome de pasta (ex.: `edital-02-2026`) |
| `total_atividades` | int | `12` | Número total de atividades de 30 dias distribuídas entre as metas |
| `duracao_atividade_dias` | int | `30` | Duração de cada atividade em dias corridos |
| `filtrar_coluna_instituicao` | string | `IFRN` | Substring exigida na última coluna da tabela §11 |
| `preencher_valores_em_reais` | bool | `false` | Trava explícita — se `true`, a skill para e pede confirmação extra |

## Fluxo (4 fases, 1 checkpoint humano)

### Passo 0 — Bootstrap de dependências (idempotente)

Antes de qualquer outro passo, verificar e instalar dependências:

```bash
bash <PLUGIN_DIR>/scripts/bootstrap_deps.sh
```

`<PLUGIN_DIR>` é a raiz do plugin instalado. Se `${CLAUDE_PLUGIN_ROOT}` estiver definido no ambiente, use-o. Caso contrário, perguntar via `AskUserQuestion`: "Qual o caminho de instalação do plugin claude-suap-ifrn? (ex.: ~/Projects/claude-suap-ifrn)". O script é no-op silencioso se `pypdf`, `playwright` e `keyring` já estiverem importáveis.

### Fase 1 — Verificar mapas (sem checkpoint)

Os mapas dos formulários SUAP já foram descobertos na execução de 2026-04-20 e estão em `references/mapas/`. **Não é necessário redescobrir via Playwright** em condições normais.

1. Verificar se `references/mapas/adicionar-{aluno,servidor,meta,atividade}.json` existem.
2. Se sim: pular para Fase 2 imediatamente.
3. Se não (mapas ausentes ou suspeita de mudança de layout do SUAP): abrir Playwright, usuário autentica manualmente, navegar para `/pesquisa/projeto/{projeto_id}/`, raspar os forms das abas Equipe e Metas, salvar novos mapas, atualizar `references/mapas/`. Reportar campos novos/mudados antes de continuar.

**Estrutura real dos formulários SUAP** (descoberta 2026-04-20 — substituiu hipótese de inline formset):

| Operação | URL | Form ID |
|----------|-----|---------|
| Adicionar aluno | `/pesquisa/adicionar_participante_aluno/{projeto_id}/` | `participacaoaluno_form` |
| Adicionar servidor | `/pesquisa/adicionar_participante_servidor/{projeto_id}/` | `participacaoservidor_form` |
| Adicionar colaborador | `/pesquisa/adicionar_participante_colaborador/{projeto_id}/` | não mapeado |
| Criar meta | `/pesquisa/adicionar_meta/{projeto_id}/` | `meta_form` |
| Criar atividade | `/pesquisa/adicionar_etapa/{meta_id}/` | `etapa_form` |
| Editar atividade | `/pesquisa/editar_etapa/{etapa_id}/` | `etapa_form` |

Campos detalhados: ver `references/mapas/*.json`.

### Fase 2 — Geração dos MDs de revisão (único checkpoint humano)

Cria em uma única passada, sem pausas intermediárias:

- `<pasta_dados>/campos/{edital_slug}/equipe/00-equipe-manifesto.md` + 1 MD por pessoa filtrada (`filtrar_coluna_instituicao`).
- `<pasta_dados>/campos/{edital_slug}/objetivos/00-matriz-atividades.md` (visão global das atividades).
- `<pasta_dados>/campos/{edital_slug}/objetivos/01-meta-*.md` a `07-meta-*.md` (ou quantas metas tiver no PDF).

**MDs excluem completamente campos monetários** conforme parâmetro `preencher_valores_em_reais: false`.

**Mensagem final da Fase 2**:
> "Gerei N MDs em `{paths}`. Revise cada um, marque `status: aprovado` (ou `ajustado`/`rejeitado`). Quando terminar, responda **continuar**."

### Fase 3 — Preenchimento automatizado (sem pausas)

Só executa se a Fase 2 foi aprovada. Fluxo linear:

1. `grep -L "^status: aprovado"` — se algum MD não estiver aprovado, aborta.
2. Para cada aluno aprovado: POST em `/pesquisa/adicionar_participante_aluno/{projeto_id}/` com os campos do mapa. Busca via Select2 AJAX usando CPF sem pontuação (ver `references/select2-ajax-suap.md`).
3. Para cada servidor aprovado: POST em `/pesquisa/adicionar_participante_servidor/{projeto_id}/` com SIAPE.
4. Se SUAP rejeitar (`.alert`/`.errorlist`): capturar mensagem, registrar no report, substituir em atividades se necessário, continuar.
5. Para cada meta aprovada: POST em `/pesquisa/adicionar_meta/{projeto_id}/` com `ordem` e `descricao`. Após salvar, raspar IDs de meta via `a[href*="adicionar_etapa"]`.
6. Para cada atividade da meta: POST em `/pesquisa/adicionar_etapa/{meta_id}/` com `ordem`, `descricao`, `indicadores_qualitativos`, `responsavel` (ID de participação), `integrantes` (checkboxes), `inicio_execucao`, `fim_execucao`.
7. **Submit**: sempre via `document.querySelector('input[type="submit"][name="{formId}"]').click()` dentro de `browser_evaluate` — nunca `browser_click` com `ref` (refs ficam stale após mutação do DOM).
8. Emite `_snapshot/fase-5-report-{timestamp}.md` com sucesso/falhas e pendências humanas.

### Fase 4 — Auto-adaptação da skill (novo — sempre executar)

Após o report da Fase 3, a skill compara o fluxo documentado com o que aconteceu de fato e propõe ajustes a si mesma. Ver template em `references/auto-adaptacao.md`.

1. **Coletar diffs**: URLs que diferiram, campos novos/ausentes nos mapas, mensagens de erro novas, ordem de operações ajustada, heurísticas revisadas manualmente.
2. **Propor edições concretas**: listar por arquivo (`SKILL.md`, `references/*.md`, `references/mapas/*.json`) o que adicionar/mudar/remover, com trechos prontos.
3. **Pausar**: apresentar o plano de ajustes ao usuário e perguntar: "Detectei N aprendizados. Aplico estas mudanças à skill? (sim/ajustes/não)".
4. **Só após confirmação "sim"**: editar os arquivos da skill.

Este comportamento garante que cada execução real cristaliza conhecimento para a próxima, sem depender de tokens redescobrindo o que já foi visto.

## Regras invioláveis

1. **Nunca inventar dados** — se a coluna Instituição for ambígua/ilegível, registrar como pendência humana no manifesto (não presumir IFRN por default).
2. **Nunca submeter** — somente `input[value="Salvar"]`. Nunca clicar em "Enviar para Avaliação", "Submeter", "Encaminhar".
3. **Valores em R$ zerados** — `preencher_valores_em_reais=false` por padrão; payload descarta qualquer chave que contenha "valor", "bolsa", "r$", "real".
4. **Sessão autenticada pelo usuário** — nenhuma credencial em arquivo.

## Armadilhas conhecidas (da execução real 2026-04-20)

- **Select2 usa POST, não GET**: o endpoint `/json/edu/aluno/` e `/json/rh/servidor/` são POST com tokens assinados. Nunca montar o payload manualmente — extrair via `ajax.data()` do jQuery. Ver `references/select2-ajax-suap.md`.
- **Servidor rejeitado por grupo de pesquisa**: SUAP exige que servidor esteja vinculado a grupo de pesquisa. Capturar e registrar — não abortar. Ver `references/validacoes-suap.md`.
- **Aluno rejeitado por Lattes ausente**: SUAP exige URL Lattes no perfil do aluno. Mesmo comportamento. Ver `references/validacoes-suap.md`.
- **`browser_click` com ref stale**: refs do snapshot ficam inválidos após `browser_evaluate`. Usar sempre `.click()` via JS. Ver `references/submit-e-navegacao.md`.
- **Atividade = "etapa" no SUAP**: a URL e o form usam "etapa" — nunca "atividade". O campo "Resultados Esperados" do form tem `name="indicadores_qualitativos"`.
- **OCR da coluna Instituição**: pode confundir letras (ex.: "IFRN" ↔ "Redução"). Sinalizar como pendência, nunca descartar silenciosamente.
- **Integrante adicionado depois**: usar `/pesquisa/editar_etapa/{id}/` para marcar checkboxes adicionais. Ver `references/submit-e-navegacao.md`.

## References (leitura sob demanda)

- `references/mapas/README.md` + `references/mapas/*.json` — mapas canônicos dos 4 formulários (descobertos na execução real).
- `references/select2-ajax-suap.md` — snippet JS para busca e seleção via Select2 AJAX.
- `references/validacoes-suap.md` — erros conhecidos do SUAP e ação humana correspondente.
- `references/submit-e-navegacao.md` — padrões de submit via JS e descoberta de IDs pós-criação.
- `references/receitas-inline-formset.md` — estrutura real das abas (hipótese original corrigida).
- `references/filtro-ifrn.md` — lógica de filtragem por coluna Instituição do §11 do PDF.
- `references/distribuicao-atividades.md` — heurística de distribuição das atividades entre as metas.
- `references/matriz-responsaveis.md` — mapeamento papel-no-plano → responsável principal + corresponsáveis.
- `references/auto-adaptacao.md` — template do plano de ajustes da Fase 4.

## Dependências externas

- Skill pai: `suap-cadastrar-projeto-edital` (Fases 1–4) — projeto precisa já estar salvo.
- MCP Playwright para `browser_evaluate`, `browser_snapshot`, `browser_wait_for`, `browser_navigate`.

## Invocação

Usuário diz: "completar projeto SUAP #<id>, plano em `<pasta_dados>/projeto_pesquisa/plano.pdf`, edital 02/2026" → a skill é ativada com os parâmetros inferidos/perguntados.

Em novos editais, reutilizar trocando `projeto_id`, `pdf_plano`, `edital_slug`. O filtro IFRN pode ser relaxado se parceiros externos entrarem na equipe (mudar `filtrar_coluna_instituicao` para string vazia).
