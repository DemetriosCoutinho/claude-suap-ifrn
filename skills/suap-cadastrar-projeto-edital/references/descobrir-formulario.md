# Descoberta do formulário SUAP — detalhes técnicos

Referência carregada sob demanda pela skill `suap-cadastrar-projeto-edital`,
Fase 1. Inclui o script JS completo de mapeamento dos ~56 campos do formulário
e instruções de pós-processamento.

## Pré-requisitos

1. Playwright MCP ativo (`mcp__plugin_playwright_playwright__*`).
2. Usuário já autenticado no SUAP (fez login manual no navegador aberto).
3. Navegador na URL `https://suap.ifrn.edu.br/pesquisa/adicionar_projeto/<id>/`
   onde `<id>` é o ID interno do edital (descoberto em
   `/pesquisa/editais_abertos/`).

## Script de mapeamento (colar em `browser_evaluate`)

```javascript
(() => {
  const form = document.getElementById('projeto_form');
  if (!form) {
    return JSON.stringify({ error: 'projeto_form not found' });
  }

  const findLabel = (el) => {
    if (el.id) {
      const lbl = document.querySelector(`label[for="${el.id}"]`);
      if (lbl) return lbl.textContent.trim().replace(/\s+/g, ' ');
    }
    const p = el.closest('.form-row, .form-group, .field-box, .fieldWrapper, tr, dd, dl');
    if (p) {
      const lbl = p.querySelector('label');
      if (lbl) return lbl.textContent.trim().replace(/\s+/g, ' ');
    }
    return null;
  };

  const fields = [];
  form.querySelectorAll('input, select, textarea').forEach((el, idx) => {
    const base = {
      idx,
      tag: el.tagName.toLowerCase(),
      type: el.type || null,
      name: el.name || null,
      id: el.id || null,
      required: el.required,
      label: findLabel(el),
      value: el.value || null,
      hidden: el.type === 'hidden' || el.offsetParent === null,
      maxLength: el.maxLength > 0 ? el.maxLength : null,
    };
    if (el.tagName.toLowerCase() === 'select') {
      base.options = Array.from(el.options).map(o => ({
        value: o.value,
        text: o.textContent.trim(),
        selected: o.selected,
      }));
    }
    fields.push(base);
  });
  return JSON.stringify({ action: form.action, fields }, null, 2);
})()
```

## Armadilha crítica: `document.querySelector('form')` é errado

O cabeçalho do SUAP tem uma barra de busca que também é um `<form>`
(`#__buscar_menu__`). Se usar `document.querySelector('form')` vai mapear
os campos errados. **Sempre** usar `#projeto_form` (ou `form.action`
terminando em `/pesquisa/adicionar_projeto/<id>/`).

## Armadilha crítica: JSON-escape duplo do `browser_evaluate`

Quando a função JS passada para `browser_evaluate` retorna uma **string**
(não um objeto), o MCP do Playwright serializa o retorno como JSON mais uma
vez. O arquivo salvo fica com aspas e backslashes escapados (`\"action\":...`).

Decodificar em Python assim:

```python
import json, pathlib

raw = pathlib.Path('_snapshot/mapa-campos.raw.json').read_text()
# 1ª decodificação: retira o JSON-wrapper do MCP
inner = json.loads(raw)
# inner agora é a string JSON original produzida pelo JS
# 2ª decodificação: parse do JSON real
mapa = json.loads(inner)
pathlib.Path('_snapshot/mapa-campos.json').write_text(
    json.dumps(mapa, ensure_ascii=False, indent=2)
)
```

Alternativa: fazer a função JS retornar o objeto direto (sem `JSON.stringify`)
e deixar o MCP serializar uma vez só. Mas aí perde a formatação legível.

## O que salvar em `_snapshot/`

- `01-formulario.snapshot.md` — saída do `browser_snapshot` (accessibility
  tree; útil para pegar `ref` de botões/labels).
- `01-formulario.png` — screenshot fullPage do form em branco.
- `01-formulario.html` — `document.documentElement.outerHTML` para grep
  offline.
- `mapa-campos.json` — JSON decodificado acima. Estrutura:
  `{ action: "<url>", fields: [ {idx, tag, type, name, id, required, label,
  value, hidden, maxLength, options?}, ... ] }`.
- `termo-compromisso.txt` — `document.getElementById('id_termo_compromisso_coordenador').value`
  (é o texto que o sistema força o usuário a aceitar).

## IDs instáveis (regenerados a cada render)

Alguns campos têm sufixo aleatório no `id`, p.ex.:

- Campus: `uo_L9nTFnmHpK`, `uo_AB12CdEfGh`, ...
- Grupo de pesquisa: `grupo_pesquisa_M9uXCv5C3N`, ...
- Edital: `edital_UqMTeD3hWJ`, ...

**Sempre preencher por `[name="..."]`**, nunca por `#id_...` para esses campos.
Os `name` são estáveis: `uo`, `grupo_pesquisa`, `edital`, etc.

Campos `id_titulo`, `id_resumo`, `id_introducao`, etc. (prefixo `id_`) são
estáveis — foram gerados pelo Django automaticamente a partir do `name`.

## Verificação de sucesso da Fase 1

Após salvar `mapa-campos.json`, confirmar:

- `fields.length >= 20` (form real tem ~56 campos, contando hidden).
- `fields` contém campos com `name` em: `csrfmiddlewaretoken`, `uo`, `edital`,
  `titulo`, `inicio_execucao`, `fim_execucao`, `area_conhecimento`,
  `grupo_pesquisa`, `palavras_chaves`, `classificacao_trl`, `precisa_cep`,
  `precisa_ceua`, `precisa_sisgen`, `precisa_sisbio`,
  `vinculado_laboratorio_multiusuario`, `tem_ods`, `resumo`, `introducao`,
  `justificativa`, `fundamentacao_teorica`, `objetivo_geral`, `metodologia`,
  `acompanhamento_e_avaliacao`, `resultados_esperados`,
  `referencias_bibliograficas`, `termo_compromisso_coordenador`,
  `aceita_termo`.
- Selects principais têm `options` não-vazia: `area_conhecimento` (~80),
  `classificacao_trl` (9), `precisa_*` (2: Sim/Não), `tem_ods` (2: Sim/Não),
  `vinculado_laboratorio_multiusuario` (2).
- Campus (`uo`) e Grupo de Pesquisa (`grupo_pesquisa`) vêm como `<select>`
  mas com `options` vazia ou só com placeholder — são Select2 com AJAX;
  a descoberta de opções é feita na Fase 4 ao vivo.
