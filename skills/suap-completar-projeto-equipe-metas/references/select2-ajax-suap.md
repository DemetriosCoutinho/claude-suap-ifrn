# Select2 AJAX no SUAP — padrão descoberto

Descoberto na execução do projeto #9139 (2026-04-20). Este padrão substitui qualquer tentativa de interagir visualmente com o Select2 via `browser_click` nos campos de pessoa.

## Endpoints

| Tipo | URL | Método | Chave de busca |
|------|-----|--------|----------------|
| Servidor IFRN | `/json/rh/servidor/` | POST | SIAPE (numérico) |
| Aluno IFRN | `/json/edu/aluno/` | POST | CPF sem pontuação (11 dígitos) |

## Por que POST com tokens assinados

O payload não é só `{q: "termo"}`. O Select2 monta um payload com campos de controle assinados pelo servidor (`control`, `ext_combo_template`, `search_fields`, etc.) que variam por sessão. Montá-los manualmente é impossível sem os tokens.

A solução: extrair a função `ajax.data()` do próprio Select2 no DOM e usá-la para montar o payload correto.

## Snippet completo — buscarPessoa

Cole este snippet em `browser_evaluate` para fazer a busca:

```javascript
async function buscarPessoa(selectName, termoBusca) {
  const sel = document.querySelector(`select[name="${selectName}"]`);
  if (!sel) return { ok: false, err: `select[name="${selectName}"] não encontrado` };
  const $sel = window.jQuery(sel);
  const ajax = $sel.data('select2').options.options.ajax;
  // ajax.url = '/json/rh/servidor/' ou '/json/edu/aluno/'
  const body = ajax.data({ term: termoBusca, page: 1 });
  const form = new URLSearchParams();
  for (const [k, v] of Object.entries(body)) if (v != null) form.append(k, v);
  const r = await fetch(ajax.url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    },
    body: form.toString()
  });
  const j = await r.json();
  // Resposta: { total: N, items: [{ id, text, html }, ...] }
  if (!j.items?.length) return { ok: false, err: `Nenhum resultado para "${termoBusca}"` };
  return { ok: true, item: j.items[0], total: j.total };
}
```

Uso:
- Servidor: `await buscarPessoa('servidor', '1935729')` — SIAPE numérico.
- Aluno: `await buscarPessoa('aluno', '07508142450')` — CPF sem pontuação (11 dígitos).

## Setar o Select2 após busca bem-sucedida

Após obter o `item`, programar o Select2:

```javascript
// sel = document.querySelector(`select[name="${selectName}"]`)
// $sel = window.jQuery(sel)
// item = { id: "38165", text: "<nome_servidor>..." }

sel.innerHTML = '';
const opt = new Option(item.text, item.id, true, true);
$sel.append(opt).trigger('change');
```

## setNative — para campos que ignoram atribuição direta

Use para inputs de data, texto ou selects nativos não-Select2:

```javascript
function setNative(el, val) {
  const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype
              : el.tagName === 'SELECT'   ? HTMLSelectElement.prototype
              : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
  el.dispatchEvent(new Event('input',  { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
}

// Exemplo:
setNative(document.querySelector('#id_data'), '01/11/2025');
setNative(document.querySelector('#id_carga_horaria'), '15');
setNative(document.querySelector('#id_vinculo'), 'Bolsista');
```

## Nome do select no DOM

O campo `name=` do select de pessoa **não** é `"aluno"` ou `"servidor"` com sufixo previsível — o SUAP usa um sufixo aleatório (ex.: `aluno_XXXXX`). O nome correto está em `references/mapas/adicionar-aluno.json` e `adicionar-servidor.json` (campo `fields[].name` cujo `tag = "select"`).

Estratégia de fallback se o nome mudar: `document.querySelector('select[id^="aluno_"], select[id^="servidor_"]')`.

## Formato de data esperado pelo SUAP

Campo `data` (data de início do membro): `DD/MM/YYYY`.
Campos `inicio_execucao` / `fim_execucao` das etapas: `DD/MM/YYYY`.
