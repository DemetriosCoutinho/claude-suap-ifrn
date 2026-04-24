# scripts/suap/cadastro_edital

Automação semi-assistida do cadastro de projetos de pesquisa no SUAP (IFRN).

Fluxo completo na skill `.claude/skills/suap-cadastrar-projeto-edital/SKILL.md`.

## Scripts disponíveis

- `montar_payload.py` — lê os MDs aprovados em `projeto_pesquisa/campos/<slug>/`
  e gera um `payload.json` com valores estruturados por campo (kind:
  text/date/select/multi-select/ckeditor/checkbox-termo/skip/select-autocomplete).
- `gerar_js_preenchimento.py` — consome o `payload.json` e emite uma função
  JavaScript auto-contida pronta para `browser_evaluate` do Playwright MCP.
  A função percorre o payload, preenche cada campo com a técnica correta
  (`setNative` para inputs, `CKEDITOR.setData` para textareas, ignora
  Select2/autocomplete) e devolve um relatório JSON por campo.

## Como rodar (exemplo edital 02/2026)

```bash
SLUG=edital-02-2026
BASE=projeto_pesquisa/campos/$SLUG

# 1) Monta payload a partir dos MDs aprovados (status != pendente)
python3 scripts/suap/cadastro_edital/montar_payload.py "$BASE/" \
  > "$BASE/_snapshot/payload.json"

# 2) Gera o JS de preenchimento
python3 scripts/suap/cadastro_edital/gerar_js_preenchimento.py \
  "$BASE/_snapshot/payload.json" \
  > /tmp/preencher.js
```

Depois, no navegador Playwright (MCP), chamar `browser_evaluate` passando
o conteúdo de `/tmp/preencher.js`. Salvar o relatório retornado em
`$BASE/_snapshot/preenchimento-etapa-a-report.json`.

Select2 autocomplete (Campus `uo`, Grupo `grupo_pesquisa`) é marcado como
`action: 'deferred'` pelo script — preencher em `browser_evaluate` separado
seguindo a Receita 3 de
`.claude/skills/suap-cadastrar-projeto-edital/references/preenchimento-recipes.md`.

## Armadilhas conhecidas

1. **`document.querySelector('form')` pega o form de busca do menu**
   (`#__buscar_menu__`), não o form do projeto. Usar `#projeto_form`.
2. **IDs com sufixo aleatório**: `uo_L9nTFnmHpK`, `grupo_pesquisa_M9uXCv5C3N`,
   `edital_UqMTeD3hWJ`. Sempre usar `[name="..."]` no preenchimento.
3. **`browser_evaluate` serializa strings em JSON-escaped duplo**.
   Decodificar com `json.loads` duas vezes antes de parsear.
4. **Editor rico é CKEditor 4.22.1** (não TinyMCE). Preencher via
   `window.CKEDITOR.instances['id_<field>'].setData(html)`.
5. **ODS via AJAX**: multi-select de subobjetivos só popula após
   `tem_ods=Sim`. Esperar antes de tentar selecionar.
6. **Botão final é `input[value="Salvar"]`** (rascunho). Não há botão
   "Submeter" na tela de criação do edital 02/2026 — a submissão fica em
   outro fluxo, coberto pela skill Fase-5.
7. **NADIC**: busca literal retorna zero. Usar `"Núcleo de Análise"` como
   termo de busca no Select2 do Grupo de Pesquisa.

## Regras de segurança (CLAUDE.md)

- **Nunca** senha em arquivo — login sempre manual pelo usuário.
- **Nunca** submeter/finalizar — só `Salvar rascunho`.
- Cookies de sessão ficam em `scripts/suap/cadastro_edital/cookies/`
  (gitignored).

## Próximos passos (fora desta skill)

Depois do `Salvar rascunho`, o SUAP exibe 5 pendências pós-salvamento
(Equipe, Metas, Anexos, Anuência, botão Classificar TRL). Esses itens
são a **Fase 5** — virão em uma skill/iteração separada
(`suap-completar-projeto-edital`). Detalhes em
`.claude/skills/suap-cadastrar-projeto-edital/references/fase-5-pendencias.md`.
