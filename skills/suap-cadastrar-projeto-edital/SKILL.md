---
name: suap-cadastrar-projeto-edital
description: Automatiza, com revisão humana obrigatória, o cadastro de projetos de pesquisa/inovação no SUAP do IFRN a partir de um PDF de Plano de Trabalho e do número do edital. Cobre descoberta do formulário, geração de MDs de revisão campo-a-campo, preenchimento via Playwright e parada em "Salvar rascunho" (nunca submete). Use esta skill sempre que o usuário mencionar "cadastrar projeto SUAP", "adicionar projeto pesquisa IFRN", "edital NN/YYYY da PROPI", "submeter projeto edital", "projeto no SUAP", ou disser "tenho o PDF do Plano de Trabalho, quero cadastrar" — mesmo que não cite a skill pelo nome.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Cadastro de projeto no SUAP (edital de pesquisa IFRN)

Automatiza o fluxo da primeira etapa (Fases 1–4): do formulário em branco
até `Salvar rascunho`. **Para aí.** A segunda etapa (Equipe, Metas, Anexos,
Anuência, botão Classificar TRL) é a **Fase 5**, coberta por uma skill futura
(ver `references/fase-5-pendencias.md`).

## Regra inviolável — CLAUDE.md §Regra 5

**Nunca clicar em "Enviar", "Submeter", "Finalizar", "Enviar para Avaliação"
ou qualquer botão equivalente de submissão final.** O único clique final
permitido nesta skill é `input[value="Salvar"]`, que gera rascunho.

O form do edital 02/2026 **só tem "Salvar"** (não há "Submeter" na tela de
criação). A submissão final acontece depois, na tela do projeto já salvo,
fora do escopo desta skill.

## Quando usar

- Usuário quer cadastrar projeto novo em um edital PROPI/RE aberto.
- Usuário tem o PDF do Plano de Trabalho (fonte primária).
- Opcional: PDF/print do cadastro do ano anterior (referência para campos
  continuados como Área, Palavras-chave, ODS, TRL).

## Quando NÃO usar

- **Prorrogação** de projeto: SUAP tem fluxo próprio em
  `/pesquisa/solicitar_prorrogacao/...`.
- **Clonagem** de projeto: SUAP tem ação nativa `/pesquisa/clonar_projeto/<id>/`.
- **Fase 5** (pós-salvamento): não é esta skill — ver
  `references/fase-5-pendencias.md`.
- **Submissão final**: nunca — é manual pelo usuário.

## Parâmetros esperados

Ao ser invocada, a skill deve receber (usar `AskUserQuestion` para qualquer parâmetro ausente):

| Parâmetro | Obrigatório | Exemplo |
|-----------|-------------|---------|
| `pasta_projeto` | sim | `~/Documents/meus-dados-suap/projeto_pesquisa/` |
| `edital` | sim | `"02/2026"` (vira slug `edital-02-2026`) |
| `pdf_plano_trabalho` | sim | `<pasta_projeto>/plano-de-trabalho.pdf` |
| `pdf_projeto_anterior` | não | `<pasta_projeto>/projeto-anterior.pdf` |

## Fluxo em 4+1 fases

```
Fase 0  Bootstrap (slug + pastas + leitura dos PDFs)
Fase 1  Descoberta do formulário SUAP (mapa-campos.json)
Fase 2  Geração dos MDs de revisão (1 por campo)
Fase 3  Revisão humana (bloqueante — status: pendente → aprovado)
Fase 4  Preenchimento + Salvar rascunho (para aqui)
──────────────────────────────────────────────────────────────
Fase 5  Pós-salvamento — PRÓXIMA SKILL (não executar agora)
```

### Passo 0 — Bootstrap de dependências Python (idempotente)

Antes de qualquer outro passo, verificar e instalar dependências:

```bash
bash <PLUGIN_DIR>/scripts/bootstrap_deps.sh
```

`<PLUGIN_DIR>` é a raiz do plugin instalado. Se `${CLAUDE_PLUGIN_ROOT}` estiver definido no ambiente, use-o. Caso contrário, perguntar via `AskUserQuestion`: "Qual o caminho de instalação do plugin claude-suap-ifrn? (ex.: ~/Projects/claude-suap-ifrn)". O script é no-op silencioso se `pypdf`, `playwright` e `keyring` já estiverem importáveis.

### Fase 0 — Bootstrap

1. Derivar `slug = "edital-<NN>-<YYYY>"` a partir de `edital="NN/YYYY"`.
2. Criar:
   - `<pasta_projeto>/campos/<slug>/`
   - `<pasta_projeto>/campos/<slug>/_snapshot/`
3. Ler o(s) PDF(s) com `pages: "1-N"` explícito (Plano tem ~13 páginas;
   projeto-anterior ~4). Extrair:
   - Título do projeto (seção "Dados do Plano de Trabalho").
   - Datas início/fim (intervalo executado).
   - Valor global (ou combinar com usuário se não aplicável).
   - Palavras-chave candidatas.
   - Texto narrativo das seções Resumo/Introdução/Justificativa/etc.

### Fase 1 — Descoberta do formulário

Detalhes técnicos (script JS, decodificação JSON dupla, IDs instáveis,
armadilhas de `#__buscar_menu__`) em `references/descobrir-formulario.md`.
Leia esse arquivo antes de executar a Fase 1.

Passos:

1. `browser_navigate` → `https://suap.ifrn.edu.br/pesquisa/editais_abertos/`.
2. Pedir login manual ao usuário (CLAUDE.md §Credenciais: nunca senha em
   arquivo).
3. Identificar o edital-alvo pelo título, extrair `<id>` do link
   `/pesquisa/adicionar_projeto/<id>/`.
4. Navegar ao formulário; capturar em `_snapshot/`:
   - `00-editais-abertos.png`
   - `01-formulario.png` (fullPage)
   - `01-formulario.html` (`document.documentElement.outerHTML`)
   - `01-formulario.snapshot.md` (accessibility tree)
   - `mapa-campos.json` (JSON decodificado — ver reference)
   - `termo-compromisso.txt` (valor do `<textarea id="id_termo_compromisso_coordenador">`)

Critério de sucesso: `mapa-campos.json` tem ≥20 campos, com `options`
listadas para Área do Conhecimento, TRL, CEP, CEUA, SISGEN, SISBIO, Lab
Multi e ODS.

### Fase 2 — Geração dos MDs de revisão

Para cada campo relevante (os 24 da Rodada 1 são um bom ponto de partida —
vêem `<pasta_projeto>/campos/edital-02-2026/` como gabarito), criar
`<pasta_projeto>/campos/<slug>/<NN>-<nome>.md`:

```markdown
---
campo: "<label humana>"
seletor_suap: "<CSS estável; prefira [name='...']>"
tipo: "text|date|textarea-ckeditor|select|select-autocomplete|checkbox|multi-select"
status: pendente
origem:
  - "<trecho do PDF ou do mapa-campos.json>"
---

## Valor proposto

<valor sugerido>

## Justificativa/origem

<por que este valor, citando seção do PDF ou mapa-campos>

## Observações

<limites (ex. max 255), avisos de Select2, subjetividade (TRL), dúvidas>
```

Regras:

- **Status inicial** = `pendente`.
- **Valores de select** sempre dentre as opções reais do `mapa-campos.json`.
  Nunca inventar opção que não existe.
- **CEP/CEUA/SISGEN/SISBIO** cabem em um único MD (`12-cep-ceua-sisgen-sisbio.md`)
  já que a resposta padrão é "Não" para todos em projetos de pesquisa em
  computação. Se houver dúvida (projetos com humanos/animais), marcar
  `precisa_revisao_humana: true` no frontmatter.
- **TRL é subjetivo**: deixar proposta + intervalo defensável no MD; não
  decidir sozinho. Faixa típica em pesquisa aplicada: TRL 5–8.
- **Escrever `_INDEX.md`** com tabela `# | Campo | Tipo | Status | Seletor`
  para o humano navegar.
- **Campos sem fonte direta no PDF** (Fundamentação, Referências): rascunho
  explicitamente rotulado como "sugestão, confirmar".
- **Estilo curto por padrão**: Resumo em 1 parágrafo; seções narrativas em
  no máximo 2 parágrafos cada. O usuário pode pedir expansão — espere a
  revisão da Fase 3.

### Fase 3 — Revisão humana (bloqueante)

- Usuário lê cada MD, edita "Valor proposto" se precisar, muda `status:`
  para `aprovado` ou `ajustado`.
- **Claude NÃO avança** enquanto houver `status: pendente`. Checar com:

```bash
grep -l '^status: pendente' <pasta_projeto>/campos/<slug>/*.md
```

Se retornar algo, parar e listar os MDs pendentes.

### Fase 4 — Preenchimento + Salvar rascunho

Detalhes de receitas JS (setNative, CKEditor, Select2 AJAX) em
`references/preenchimento-recipes.md`. Leia antes de executar.

Pipeline em dois comandos + execução no browser:

```bash
# 1) Monta payload a partir dos MDs aprovados
python3 scripts/suap/cadastro_edital/montar_payload.py \
  <pasta_projeto>/campos/<slug>/ \
  > <pasta_projeto>/campos/<slug>/_snapshot/payload.json

# 2) Gera o JS que aplica o payload
python3 scripts/suap/cadastro_edital/gerar_js_preenchimento.py \
  <pasta_projeto>/campos/<slug>/_snapshot/payload.json \
  > /tmp/preencher.js
```

No navegador Playwright (reabrir `/pesquisa/adicionar_projeto/<id>/` com
sessão salva):

1. `browser_evaluate` do conteúdo de `/tmp/preencher.js` → preenche texto,
   data, select simples, multi-select (CEP/CEUA/...), CKEditor (10 campos)
   e marca o checkbox do termo.
2. Salvar o `report` retornado em `_snapshot/preenchimento-etapa-a-report.json`.
3. Select2 autocomplete (Campus `uo`, Grupo `grupo_pesquisa`): preencher em
   evaluates separados com a receita 3 (`references/preenchimento-recipes.md`).
   **Tip crítica**: para NADIC buscar `"Núcleo de Análise"`, não `"NADIC"` —
   busca literal retorna zero.
4. Screenshot fullPage em `_snapshot/preenchido-antes-salvar.png`.
5. Diff DOM vs. `payload.json`. Se divergir em algum campo, parar e avisar
   o usuário antes de salvar.
6. Clicar em `input[value="Salvar"]`. **Não** em botões com "Enviar/Submeter".
7. Screenshot final em `_snapshot/apos-salvar.png`. Capturar a URL final
   (deve virar `/pesquisa/projeto/<ID>/`).
8. Atualizar `_INDEX.md` com: data/hora do salvamento, URL do rascunho,
   ID do projeto, e anexar a lista da Fase 5 (copiar de
   `references/fase-5-pendencias.md`).

Critério de sucesso: URL muda para `/pesquisa/projeto/<ID>/...`, DOM mostra
a mensagem "Projeto cadastrado com sucesso.", os dois screenshots estão
em `_snapshot/`.

### Fase 5 — Próxima rodada (NÃO executar nesta skill)

Após Salvar, o SUAP indica 5 pendências antes do projeto poder ser
enviado para avaliação:

1. Equipe (bolsistas + servidores + colaboradores externos).
2. Metas I–VI (cadastrar aba vazia).
3. Anexos (PDF do Plano + documentos exigidos pelo edital).
4. Anuência da chefia imediata.
5. Botão "Classificar TRL" (assistente guiado).

Detalhes em `references/fase-5-pendencias.md`. Estas ficam para a skill
seguinte (`suap-completar-projeto-edital`, a criar) — esta aqui **termina**
na Fase 4.

## Artefatos gerados por execução

```
projeto_pesquisa/campos/edital-<NN>-<YYYY>/
├── _INDEX.md                     # status global + URL do rascunho
├── _snapshot/
│   ├── 00-editais-abertos.png
│   ├── 01-formulario.{png,html,snapshot.md}
│   ├── mapa-campos.json
│   ├── termo-compromisso.txt
│   ├── payload.json
│   ├── preenchimento-etapa-a-report.json
│   ├── preenchido-antes-salvar.png
│   └── apos-salvar.png
├── 01-campus.md
├── 02-titulo.md
├── ...
└── 24-termo-compromisso.md
```

## Lições aprendidas

- **Editor rico é CKEditor 4.22.1**, não TinyMCE. `window.tinymce` é `undefined`.
  API correta: `CKEDITOR.instances['id_<field>'].setData(html); updateElement()`.
- **`document.querySelector('form')` pega a barra de busca do menu**
  (`#__buscar_menu__`). Sempre `#projeto_form`.
- **`browser_evaluate` serializa JSON duas vezes** quando a função retorna
  string. Decodificar duas vezes com `json.loads` antes de usar.
- **IDs instáveis**: `uo_L9nTFnmHpK`, `grupo_pesquisa_M9uXCv5C3N`,
  `edital_UqMTeD3hWJ`. Usar `[name="..."]` sempre.
- **NADIC não busca por sigla**: "Núcleo de Análise" retorna o grupo
  "Núcleo de Análise de Dados e Inteligência Computacional" (value=1447).
- **Select2 AJAX** precisa de ~2s de espera entre digitar e clicar.
- **Botão único "Salvar"**: a tela de criação só tem ele. Submeter é em
  outro fluxo depois.
- **Campos condicionais** (`num_protocolo_cep/ceua/sisgen/sisbio`,
  `atividades_sisgen/sisbio`) ficam `hidden` enquanto o select correspondente
  for "Não". Não tentar preencher.
- **ODS multi-select via AJAX**: aparece só depois de `tem_ods=Sim`. Para o
  LMA (02/2026) foi `tem_ods=Não` — não precisou.

## Riscos e armadilhas

- **TRL é decisão subjetiva** — sempre pedir confirmação explícita do
  usuário. Documentar no MD o intervalo defensável.
- **CEP/CEUA = Não** só vale se o projeto não interage com humanos/animais
  direto. Se dúvida, marcar `precisa_revisao_humana: true`.
- **Palavras-chave ≤ 255 chars** — contar antes.
- **PDF pode vir truncado**: sempre ler todas as páginas explicitamente
  (`pages: "1-13"` ou conforme o número real de páginas do seu PDF).
- **Mudar de edital**: o `mapa-campos.json` pode ter estrutura diferente.
  Rodar Fase 1 novamente a cada rodada — nunca reusar mapa de edital
  anterior.

## Arquivos de referência

- `references/descobrir-formulario.md` — JS de mapeamento + armadilhas.
- `references/preenchimento-recipes.md` — 3 receitas JS canônicas.
- `references/fase-5-pendencias.md` — ponto de partida da próxima rodada.
- `scripts/suap/cadastro_edital/` — helpers Python (`montar_payload.py`,
  `gerar_js_preenchimento.py`).
- `<pasta_projeto>/campos/edital-02-2026/` — execução de referência
  completa.
- `CLAUDE.md` — §Regra 5 (não submeter), §Credenciais (login manual).
