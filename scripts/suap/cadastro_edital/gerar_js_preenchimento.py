"""Gera um bloco de código JavaScript (função auto-contida) que preenche os
campos simples do formulário do SUAP a partir do payload.json. Campos Select2
(autocomplete — uo, grupo_pesquisa) são apenas registrados; seu preenchimento
é feito em etapa separada.

Uso:
    python3 scripts/suap/cadastro_edital/gerar_js_preenchimento.py \
        projeto_pesquisa/campos/edital-02-2026/_snapshot/payload.json
"""
from __future__ import annotations

import json
import pathlib
import sys


def main() -> None:
    payload_path = pathlib.Path(sys.argv[1])
    payload = json.loads(payload_path.read_text())
    payload_js = json.dumps(payload, ensure_ascii=False)

    # fmt: off
    js = r"""() => {
  const payload = """ + payload_js + r""";
  const form = document.getElementById('projeto_form');
  const report = [];
  const setNative = (el, value) => {
    const proto = el.tagName === 'SELECT'
      ? Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value')
      : Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
    proto.set.call(el, value);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  };

  for (const entry of payload) {
    const {field, kind} = entry;
    try {
      if (kind === 'skip' || kind === 'select-autocomplete') {
        report.push({field, kind, action: 'deferred'});
        continue;
      }
      if (kind === 'multi-select') {
        for (const [name, value] of Object.entries(entry.values)) {
          const el = form.querySelector('[name="' + name + '"]');
          if (!el) { report.push({field: name, kind: 'multi-select', ok: false, err: 'not found'}); continue; }
          setNative(el, value);
          report.push({field: name, kind: 'multi-select', ok: el.value === value, applied: el.value});
        }
        continue;
      }
      if (kind === 'checkbox-termo') {
        const el = form.querySelector('[name="aceita_termo"]');
        if (!el) { report.push({field, ok: false, err: 'not found'}); continue; }
        if (!el.checked) el.click();
        report.push({field, kind, ok: el.checked, applied: el.checked});
        continue;
      }
      if (kind === 'ckeditor') {
        const editor = window.CKEDITOR && window.CKEDITOR.instances['id_' + field];
        if (!editor) { report.push({field, kind, ok: false, err: 'CKEDITOR instance missing'}); continue; }
        editor.setData(entry.html);
        editor.updateElement();
        const applied = (editor.getData() || '').length;
        report.push({field, kind, ok: applied > 0, applied_len: applied, expected_len: entry.html.length});
        continue;
      }
      // text / date / select
      const el = form.querySelector('[name="' + field + '"]');
      if (!el) { report.push({field, kind, ok: false, err: 'not found'}); continue; }
      setNative(el, entry.value);
      report.push({field, kind, ok: String(el.value) === String(entry.value), applied: el.value, expected: entry.value});
    } catch (e) {
      report.push({field, kind, ok: false, err: String(e)});
    }
  }
  return JSON.stringify(report, null, 2);
}
"""
    # fmt: on
    sys.stdout.write(js)


if __name__ == "__main__":
    main()
