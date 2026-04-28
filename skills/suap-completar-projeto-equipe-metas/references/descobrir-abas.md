# Descobrir abas Equipe e Objetivos específicos

Adaptação do `descobrir-formulario.md` da skill-pai, agora para o projeto já salvo.

## Contexto

Ao abrir `https://suap.ifrn.edu.br/pesquisa/projeto/<id-do-projeto>/` (modo edição), o SUAP expõe abas para Detalhes, Equipe, Metas/Objetivos, Anexos, Plano de Aplicação, Histórico. Cada aba pode ser: (a) inline formset Django na mesma página, (b) página separada com POST próprio, (c) modal JS com endpoint AJAX. A Fase 1 descobre qual.

## Script JS de mapeamento

Executar via `browser_evaluate` após navegar para cada aba:

```javascript
() => {
  const out = { aba_href: location.href, form: null, campos: [], botoes: [], formsets: [] };

  // 1. Form principal da aba
  const forms = Array.from(document.querySelectorAll('form'));
  const mainForm = forms.find(f => f.id?.includes('equipe') || f.id?.includes('meta') || f.action?.includes('equipe') || f.action?.includes('meta')) || forms[0];
  if (!mainForm) return out;
  out.form = { id: mainForm.id, action: mainForm.action, method: mainForm.method };

  // 2. Campos regulares
  Array.from(mainForm.querySelectorAll('input, select, textarea')).forEach(el => {
    if (el.type === 'hidden' && el.name?.includes('TOTAL_FORMS')) {
      // Django inline formset sentinel
      out.formsets.push({
        prefix: el.name.replace('-TOTAL_FORMS', ''),
        total_forms: el.value,
        initial_forms: mainForm.querySelector(`[name="${el.name.replace('TOTAL', 'INITIAL')}"]`)?.value,
      });
      return;
    }
    if (el.type === 'hidden') return;
    out.campos.push({
      name: el.name,
      id: el.id,
      type: el.type || el.tagName.toLowerCase(),
      tag: el.tagName.toLowerCase(),
      options: el.tagName === 'SELECT' ? Array.from(el.options).map(o => ({ value: o.value, text: o.text })).slice(0, 20) : null,
      required: el.required,
    });
  });

  // 3. Botões de ação (Adicionar, Salvar, Cancelar, Remover)
  Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a.btn')).forEach(el => {
    const text = (el.value || el.textContent || '').trim().slice(0, 80);
    if (!text) return;
    out.botoes.push({
      tag: el.tagName.toLowerCase(),
      type: el.type,
      text: text,
      href: el.href || null,
      onclick: el.getAttribute('onclick'),
    });
  });

  // 4. Select2 containers (bolsas, responsáveis)
  out.select2 = Array.from(document.querySelectorAll('.select2-container')).length;

  return out;
}
```

## Armadilhas específicas das abas Equipe/Metas

1. **Inline formset + TOTAL_FORMS**: a aba pode listar N membros atuais. Para adicionar um novo, o JS precisa:
   - Clicar no botão "Adicionar membro" (normalmente classe `.add-row` ou link `<a>` específico).
   - O Django template adiciona uma nova linha com prefixo `equipe_set-N-<field>` onde N = `TOTAL_FORMS` atual.
   - Incrementar `TOTAL_FORMS` (Django valida esse sentinel).
   - Popular campos da nova linha com `setNative` (Receita 1 da skill-pai).

2. **Select2 AJAX para pessoa**: campo `equipe_set-N-pessoa` é `<select>` vazio populado por AJAX. Usar Receita 3 (skill-pai) buscando por CPF (`"<CPF_COM_PONTUACAO>"` com pontuação; se falhar, sem pontuação `"<CPF_SEM_PONTUACAO>"`) ou nome parcial.

3. **Aba Metas pode abrir modal**: em alguns templates SUAP, "Adicionar meta" abre um modal separado que POSTa via AJAX. Nesse caso:
   - Não é inline formset — é um endpoint `/pesquisa/adicionar_meta/{projeto_id}/`.
   - A Fase 3 precisa submeter formulário do modal (sem clicar no botão principal de "Salvar").
   - Detectar pelo atributo `data-toggle="modal"` ou pelo `href="#"` + JS handler.

4. **Dropdown de responsável de atividade**: lista pessoas já cadastradas na equipe + coordenador. Se a aba Equipe não foi salva antes, o dropdown vem vazio — por isso **Fase 3 preenche Equipe antes de Metas**.

5. **Botão "Enviar para Avaliação"**: pode aparecer também na aba Objetivos. O gerador JS precisa bloquear seletores com `value` contendo "Enviar", "Submeter", "Encaminhar".

## Saída esperada

Dois arquivos JSON salvos em `{edital_slug}/_snapshot/`:
- `mapa-campos-equipe.json`
- `mapa-campos-metas.json`

Cada um seguindo o schema do script acima. A Fase 2 lê esses JSONs para gerar JS compatível com o DOM real (não com o esperado).
