# Estrutura real das abas Equipe e Metas no SUAP

> **Nota histórica**: o plano original desta skill assumia que o SUAP usaria Django inline formsets (padrão `equipe_set-0-campo`). A hipótese era errada — o SUAP usa **páginas separadas por tipo** com POST tradicional. O código de inline formset abaixo é mantido apenas como referência para outros contextos.

## Estrutura real (SUAP projeto pesquisa)

O SUAP **não** usa inline formset nas abas Equipe e Objetivos específicos. O fluxo é:

```
/pesquisa/projeto/{id}/
  ↓ aba Equipe
  → /pesquisa/adicionar_participante_aluno/{id}/       form: participacaoaluno_form
  → /pesquisa/adicionar_participante_servidor/{id}/     form: participacaoservidor_form
  → /pesquisa/adicionar_participante_colaborador/{id}/  form: participacaocolaborador_form (não mapeado)

  ↓ aba Objetivos específicos
  → /pesquisa/adicionar_meta/{id}/                     form: meta_form
    → /pesquisa/adicionar_etapa/{meta_id}/             form: etapa_form
    → /pesquisa/editar_etapa/{etapa_id}/               form: etapa_form (mesmo, para edição)
```

Cada form tem um botão de submit cujo atributo `name` é igual ao ID do form (ex.: `name="participacaoaluno_form"`). Ver `references/mapas/README.md` para os campos de cada form.

---

## Proteção contra "Enviar para Avaliação" (mantida de qualquer abordagem)

No JS gerado, **nunca clicar** em:

```javascript
// Proibido — lista de guarda:
document.querySelector('input[value*="Enviar"]')
document.querySelector('input[value*="Submeter"]')
document.querySelector('input[value*="Encaminhar"]')
```

Constante Python no gerador:
```python
DENY_VALUES = ["Enviar para Avaliação", "Enviar", "Submeter", "Encaminhar", "Publicar"]
```

---

## Referência histórica — Django inline formset (outros sistemas)

Se alguma outra aba do SUAP (em futuros projetos) usar inline formset, o padrão é:

- Campos prefixados: `{prefix}-{N}-{field}` (ex.: `equipe_set-0-pessoa`).
- `TOTAL_FORMS` hidden input: **incrementar antes** de popular nova linha.
- Clicar no botão "Adicionar" → aguardar 300ms → preencher campos da linha nova.

```javascript
async function addFormsetRow(prefix, values) {
  const total = document.querySelector(`[name="${prefix}-TOTAL_FORMS"]`);
  if (!total) return { ok: false, err: 'não é formset — verificar estrutura real' };
  const idx = parseInt(total.value, 10);
  const addBtn = document.querySelector(`.add-row[data-prefix="${prefix}"]`);
  if (addBtn) {
    addBtn.click();
    await new Promise(r => setTimeout(r, 300));
  }
  // incrementar TOTAL_FORMS se o clique não fez
  if (parseInt(total.value, 10) <= idx) {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')
      .set.call(total, String(idx + 1));
  }
  for (const [fieldName, fieldValue] of Object.entries(values)) {
    const el = document.querySelector(`[name="${prefix}-${idx}-${fieldName}"]`);
    if (!el) continue;
    const setter = Object.getOwnPropertyDescriptor(
      el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype, 'value'
    ).set;
    setter.call(el, fieldValue);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  return { ok: true, idx };
}
```
