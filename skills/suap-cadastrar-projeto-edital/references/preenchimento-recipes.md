# Receitas de preenchimento — Fase 4

Três receitas JS canônicas, testadas no edital 02/2026. Usadas pelo
`gerar_js_preenchimento.py` e executadas via `browser_evaluate`.

## Contexto

O formulário do SUAP/IFRN para cadastro de projeto combina três famílias de
campos, cada uma com sua API de preenchimento. Tentar usar `el.value = x`
direto **não funciona** na maior parte deles: React/Django+jQuery escutam
eventos específicos, e CKEditor substitui o `<textarea>` por um iframe.

## Receita 1 — Texto, data, select simples

Usar o descriptor nativo do prototype para driblar o setter override do
jQuery e disparar eventos `input` e `change` manualmente.

```javascript
function setNative(el, value) {
  const proto = el.tagName === 'SELECT'
    ? Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value')
    : Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
  proto.set.call(el, value);
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
}

// Exemplo: preencher título
const titulo = document.querySelector('[name="titulo"]');
setNative(titulo, '<titulo-do-projeto>');
```

Aplicável a:
- `titulo` (text, max 255)
- `valor_global_projeto` (text formatado como "0,0" ou "100000,00")
- `inicio_execucao`, `fim_execucao` (date: "YYYY-MM-DD")
- `palavras_chaves` (text, max 255)
- `area_conhecimento` (select com `value="12"` para Ciência da Computação)
- `classificacao_trl` (select: "TRL 1" a "TRL 9")
- `precisa_cep`, `precisa_ceua`, `precisa_sisgen`, `precisa_sisbio`
  (select Sim/Não: usar `"False"` / `"True"` como value)
- `vinculado_laboratorio_multiusuario` (select Sim/Não)
- `tem_ods` (select Sim/Não)

## Receita 2 — CKEditor (não TinyMCE!)

O SUAP usa **CKEditor 4.22.1** para os 10 textareas narrativos. `window.tinymce`
é `undefined` — não tente. A API correta:

```javascript
function setCk(fieldName, html) {
  const key = 'id_' + fieldName;
  const editor = window.CKEDITOR && window.CKEDITOR.instances[key];
  if (!editor) {
    return { ok: false, err: 'CKEDITOR instance missing for ' + key };
  }
  editor.setData(html);
  editor.updateElement();  // sincroniza o <textarea> escondido
  return { ok: true, applied_len: (editor.getData() || '').length };
}

// Exemplo
setCk('resumo', '<p>O projeto dá continuidade ao desenvolvimento da plataforma <strong>LMA</strong>...</p>');
```

Aplicável a (10 instâncias):
- `resumo`, `introducao`, `justificativa`, `fundamentacao_teorica`
- `objetivo_geral`, `metodologia`, `acompanhamento_e_avaliacao`
- `resultados_esperados`, `referencias_bibliograficas`
- `termo_compromisso_coordenador` (este é readonly — **não preencher**, só
  o checkbox `aceita_termo` é que muda)

### Conversão markdown → HTML esperada pelo CKEditor

CKEditor espera HTML limpo:

- Parágrafo = `<p>...</p>`, um por linha lógica.
- Negrito = `<strong>...</strong>` (não `<b>`).
- Itálico = `<em>...</em>` (não `<i>`).
- Listas = `<ul><li>...</li></ul>` ou `<ol>...</ol>`.
- **Não** usar `<br>` para quebra — criar novos `<p>`.

O helper `montar_payload.py` já converte blockquote-markdown nisso.

## Receita 3 — Select2 autocomplete com AJAX

Para Campus (`uo`) e Grupo de Pesquisa (`grupo_pesquisa`). Estes são `<select>`
"vazios" que o Select2 popula via AJAX conforme o usuário digita. Não dá para
fazer `setNative(select, value)` — o AJAX não dispara.

Sequência correta:

```javascript
async function fillSelect2(fieldName, searchTerm) {
  // 1. Achar o container Select2 do campo
  const select = document.querySelector(`[name="${fieldName}"]`);
  const container = select.parentElement.querySelector('.select2-selection');
  if (!container) return { ok: false, err: 'Select2 container missing' };

  // 2. Abrir o dropdown
  container.click();
  await new Promise(r => setTimeout(r, 400));

  // 3. Encontrar o input de busca (só existe quando aberto)
  const search = document.querySelector('.select2-search--dropdown .select2-search__field');
  if (!search) return { ok: false, err: 'search field missing' };

  // 4. Digitar via setter nativo (não `search.value = ...`)
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(search, searchTerm);
  search.dispatchEvent(new Event('input', { bubbles: true }));

  // 5. Esperar o AJAX (~2s é seguro; pior caso 3s)
  await new Promise(r => setTimeout(r, 2000));

  // 6. Clicar na primeira opção real (evitar "Pesquisando..." e erros)
  const opts = Array.from(document.querySelectorAll(
    '.select2-container--open .select2-results__option'
  )).filter(o => !o.classList.contains('loading-results')
             && !o.classList.contains('select2-results__message'));
  if (opts.length === 0) return { ok: false, err: 'no results for "' + searchTerm + '"' };

  opts[0].click();
  await new Promise(r => setTimeout(r, 300));
  return { ok: true, chosen: opts[0].textContent.trim(), value: select.value };
}
```

### Termos de busca que funcionaram (edital 02/2026)

- O campus deve ser buscado pelo nome do seu campus — o Select2 retorna o valor correto.
- Grupo **NADIC** → buscar `"NADIC"` retorna **zero** resultados. Buscar
  `"Núcleo de Análise"` → escolhe "Núcleo de Análise de Dados e Inteligência
  Computacional" (value=1447). **Registre no MD do campo qual termo funcionou**
  para a próxima rodada não precisar re-descobrir.

## Checkbox do termo de compromisso

```javascript
const el = document.querySelector('[name="aceita_termo"]');
if (!el.checked) el.click();  // click é melhor que checked=true; aciona handlers
```

Nunca "aceitar" sem que o usuário tenha visto o termo em `termo-compromisso.txt`.

## Orquestração completa via helpers

Em vez de escrever o JS à mão, use o pipeline:

```bash
# 1. Montar payload a partir dos MDs aprovados
python3 scripts/suap/cadastro_edital/montar_payload.py \
  projeto_pesquisa/campos/<slug>/ \
  > projeto_pesquisa/campos/<slug>/_snapshot/payload.json

# 2. Gerar o JS que aplica o payload
python3 scripts/suap/cadastro_edital/gerar_js_preenchimento.py \
  projeto_pesquisa/campos/<slug>/_snapshot/payload.json \
  > /tmp/preencher.js

# 3. Executar via browser_evaluate (MCP Playwright)
#    Passar o conteúdo de /tmp/preencher.js como parâmetro da função.
```

O JS gerado retorna um `report` JSON com `{field, kind, ok, applied, expected}`
por campo. Salvar em `_snapshot/preenchimento-etapa-a-report.json` para auditoria.

## Select-autocomplete fica fora do JS gerado

O script do `gerar_js_preenchimento.py` marca Select2 como `action: 'deferred'`
— não tenta preencher. Motivo: exige espera assíncrona que não cabe em um
único `browser_evaluate`. Preencher em passos separados: um `browser_evaluate`
só para o Campus, outro para o Grupo de Pesquisa, com `browser_wait_for` entre
eles.

## Diff de validação pré-Salvar

Antes de clicar em `input[value="Salvar"]`, rodar um snapshot do DOM e
comparar com o `payload.json`. Se algum campo divergir:

- **Divergência em text/date/select simples**: reaplicar `setNative`.
- **Divergência em CKEditor**: reaplicar `setData`. Se `getData()` vier vazio,
  o editor não estava pronto — aguardar `CKEDITOR.instances[x].status === 'ready'`.
- **Divergência em Select2**: usuário provavelmente cancelou o dropdown.
  Rerrodar a receita 3.

Só clicar em Salvar quando o diff estiver zerado.
