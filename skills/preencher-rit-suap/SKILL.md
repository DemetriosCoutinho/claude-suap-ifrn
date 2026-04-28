---
name: preencher-rit-suap
description: >
  Use sempre que o usuário pedir para preencher, cadastrar, submeter ou salvar o RIT
  (Relatório Individual de Trabalho) no SUAP do IFRN — mesmo que não mencione "SUAP"
  explicitamente. Dispara em pedidos como "cadastrar RIT 2026.1", "salvar meu relatório
  no sistema", "mandar o RIT pro sistema", "preencher o formulário do semestre", "enviar
  o relatório para o diretor aprovar". Automatiza o fluxo completo: extrai os 9 textos
  aprovados de _redacao/, consolida PDFs por seção, abre o formulário SUAP via Playwright
  MCP, preenche os 9 CKEditors com HTML formatado, anexa os PDFs e salva como rascunho
  (nunca clica em "Enviar ao Diretor"). NÃO usar para PIT. NÃO substitui a fase de
  redação — exige as 9 redações já aprovadas em periodos/<periodo>/rit/_redacao/.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# preencher-rit-suap

Skill para preencher o formulário RIT do SUAP via Playwright MCP. Codifica os padrões
descobertos na sessão RIT 2025.2 — em especial o CKEditor 4 e o upload de arquivo
com input escondido — para que o próximo semestre não precise redescobrir tudo.

## Quando NÃO usar

- Período com MDs ainda em `status: rascunho` → redirecionar para a fase de redação primeiro.
- Formulário PIT (planejamento) → sem suporte por ora.
- Botão "Enviar ao Diretor" → fora de escopo, continua manual por política.

## Pré-requisitos — conferir antes de começar

1. 9 arquivos `periodos/<periodo>/rit/_redacao/NN_<secao>.md` com `status: aprovado` no frontmatter YAML (inclusive os "Não houve." com `tipo: nao_se_aplica` precisam ter `status: aprovado`).
2. `periodos/<periodo>/rit/_meta/manifesto.json` com `entregas` preenchidas e `status_validacao: valido`.
3. `scripts/suap/.discovery/rit_form_schema.json` presente (cristalizado em 2026-04-16; válido enquanto o SUAP não mudar layout).
4. `pypdf` instalado: `python3 -m pip install pypdf`.

## Inputs obrigatórios — coletar via `AskUserQuestion` no início

Se qualquer um dos inputs abaixo estiver ausente, perguntar via `AskUserQuestion` antes de qualquer outra ação.

- **`pasta_dados`** — pasta base onde ficam seus dados SUAP (ex.: `~/Documents/meus-dados-suap/`)
- **`periodo`** — formato `AAAA.S` (ex.: `2026.1`)
- **`form_url`** — URL completa do formulário RIT do semestre:
  `https://suap.ifrn.edu.br/pit_rit_v2/preencher_relatorio_individual_trabalho/<ID>/`
  (o usuário acha em SUAP → PIT/RIT → clicar "Preencher" no semestre certo)

## Fluxo em 7 passos — executar em ordem

### Passo 0 — Bootstrap de dependências (idempotente)

Antes de qualquer outro passo, verificar e instalar dependências:

```bash
bash <PLUGIN_DIR>/scripts/bootstrap_deps.sh
```

`<PLUGIN_DIR>` é a raiz do plugin instalado. Se `${CLAUDE_PLUGIN_ROOT}` estiver definido no ambiente, use-o. Caso contrário, perguntar via `AskUserQuestion`: "Qual o caminho de instalação do plugin claude-suap-ifrn? (ex.: ~/Projects/claude-suap-ifrn)". O script é no-op silencioso se `pypdf`, `playwright` e `keyring` já estiverem importáveis.

### Passo 1 — Ler schema do formulário

```python
# Carregar em memória (não colar no contexto inteiro — só usar as chaves necessárias)
import json
schema = json.loads(open("scripts/suap/.discovery/rit_form_schema.json").read())
sel    = schema["mapeamento_secao_selector"]   # ex: {"aulas": "#id_obs_aulas", ...}
arq    = schema["mapeamento_secao_arquivo"]    # ex: {"aulas": "#id_arquivo_aulas", ...}
btn    = schema["salvar_button"]["selector"]   # "input[type='submit'][value='Salvar']"
```

### Passo 2 — Extrair textos dos MDs

```bash
python3 <PLUGIN_DIR>/skills/preencher-rit-suap/scripts/extrair_textos.py --periodo <P>
```

Gera `<pasta_dados>/periodos/<P>/rit/_submissao/.textos_prontos.json`. Se abortar com erro de `status: rascunho`, pare e avise o usuário antes de tocar no navegador.

### Passo 3 — Consolidar PDFs por seção

```bash
python3 <PLUGIN_DIR>/skills/preencher-rit-suap/scripts/consolidar_pdfs.py --periodo <P>
```

Gera `<pasta_dados>/periodos/<P>/rit/_consolidados/<secao>.pdf`. Seções sem PDF (preparacao_ensino, projetos_ensino, reunioes, extensao) são puladas silenciosamente.

### Passo 4 — Playwright MCP: login e navegação

```
browser_navigate → https://suap.ifrn.edu.br/accounts/login/
```

Usar `AskUserQuestion` para aguardar o usuário fazer login manual na janela aberta. Claude **não toca em senhas**. Após confirmação:

```
browser_navigate → <form_url>
browser_wait_for → text="Relatório Individual de Trabalho"
```

> Para padrões exatos de preenchimento CKEditor: ler `references/ckeditor-pattern.md`

### Passo 5 — Preencher os 9 campos + anexar PDFs

**Ordem canônica** (sempre respeitar): aulas → preparacao_ensino → apoio_ensino → projetos_ensino → atendimento_orientacao → reunioes → pesquisa → extensao → gestao.

Para cada seção:

1. Converter o texto do `.textos_prontos.json` para HTML (`<p>`, `<ul><li>`, `<strong>`, `<em>`) — ver `references/ckeditor-pattern.md` para regras.
2. `browser_evaluate` com `CKEDITOR.instances['<id>'].setData('<html>')` — ex.:
   ```javascript
   CKEDITOR.instances['id_obs_aulas'].setData('<p>No período...</p>');
   ```
3. Se `_consolidados/<secao>.pdf` existir: upload via `references/file-upload-pattern.md`.

Ao final dos 9 campos:
```
browser_take_screenshot → periodos/<P>/rit/_submissao/screenshots/pre_salvamento.png
```

### Passo 6 — Checkpoint humano obrigatório

Usar `AskUserQuestion` com opções "Salvar agora" / "Cancelar sem salvar". Se cancelar: `browser_close`, não atualizar manifesto, registrar cancelamento no chat.

### Passo 7 — Salvar e registrar evidências

```
browser_click → input[type='submit'][value='Salvar']
browser_wait_for → time=3
```

Redirect para home (`https://suap.ifrn.edu.br/`) é **comportamento normal** do SUAP — não é erro. Reabrir `<form_url>` e verificar persistência via `CKEDITOR.instances[id].getData()` em ao menos 2 campos.

Pós-confirmação:
```
browser_take_screenshot → periodos/<P>/rit/_submissao/screenshots/pos_salvamento.png
```

Depois: ler campos via evaluate, gravar `<pasta_dados>/periodos/<P>/rit/_submissao/texto_salvo_<YYYYMMDD_HHMMSS>.txt`, atualizar `manifesto.json`:

```json
"submissao": {
  "status": "salvo_como_rascunho",
  "data": "<ISO-8601>",
  "url": "<form_url>",
  "metodo": "playwright_mcp",
  "editor": "ckeditor4",
  "screenshot_pre": "<pasta_dados>/periodos/<P>/rit/_submissao/screenshots/pre_salvamento.png",
  "screenshot_pos": "<pasta_dados>/periodos/<P>/rit/_submissao/screenshots/pos_salvamento.png",
  "texto_salvo": "<pasta_dados>/periodos/<P>/rit/_submissao/texto_salvo_<ts>.txt",
  "pdfs_anexados": {"aulas": "...", "apoio_ensino": "...", ...},
  "observacoes": "Salvo via Playwright MCP. NÃO enviado ao diretor."
}
```

Por último: `browser_close`.

## Nunca fazer

- Clicar em qualquer botão com texto "Enviar", "Submeter", "Finalizar" ou "Concluir".
- Usar `page.fill()` ou setter nativo de `<textarea>` para CKEditor — não atualiza o visual.
- Salvar sem checkpoint humano explícito (Passo 6).

## Referências (carregar só quando necessário)

| Arquivo | Quando ler |
|---------|-----------|
| `references/ckeditor-pattern.md` | Ao preencher os campos — snippets prontos, regras markdown→HTML, armadilhas |
| `references/file-upload-pattern.md` | Ao fazer upload de PDF — sequência exata click+chooser |
| `references/troubleshooting.md` | Ao encontrar erro ou comportamento inesperado |
