# Troubleshooting — preencher-rit-suap

## Campo aparece vazio no navegador após setData

**Causa**: `setData` chamado antes do CKEditor terminar de inicializar, ou o `evaluate` retornou sem erro mas o CKEDITOR não estava disponível.

**Solução**:
1. Verificar `typeof CKEDITOR !== 'undefined'` → se `false`, aguardar com `browser_wait_for(text="Relatório Individual de Trabalho")` e tentar novamente.
2. Re-executar o `setData` para a seção afetada.
3. Confirmar via `CKEDITOR.instances['id_obs_aulas'].getData().length > 10`.

## Texto salvo virou um bloco sem parágrafos ou listas

**Causa**: foi enviado plain-text com `\n\n` em vez de HTML.

**Solução**: re-executar o `setData` passando HTML formatado com `<p>`, `<ul><li>`. Ver `ckeditor-pattern.md` para regras de conversão.

## `browser_click` no botão Salvar gera timeout ou não retorna

**Causa**: o click dispara um submit + redirect de página, o que faz o Playwright MCP perder a referência da página atual antes de conseguir retornar a resposta.

**Solução**: não aguardar o retorno do click com timeout longo. Usar:
1. `browser_evaluate(() => document.querySelector("input[type='submit'][value='Salvar']").click())`
2. `browser_wait_for(time=3)`
3. Verificar se a URL atual é `https://suap.ifrn.edu.br/` (redirect ao home = sucesso normal do SUAP).

## SUAP redirecionou para home após Salvar — dados foram perdidos?

**Não** — é comportamento **normal** do SUAP. Reabrir a URL do formulário (`<form_url>`) e verificar:

```javascript
CKEDITOR.instances['id_obs_aulas'].getData()
// → deve retornar o HTML preenchido
```

Se retornar string vazia, o save realmente não funcionou — tentar novamente do Passo 5.

## `browser_file_upload` diz "no file chooser open"

**Causa**: o `browser_evaluate` com `el.click()` não abriu o diálogo, ou o Playwright MCP não interceptou a tempo.

**Solução**:
1. Garantir que o `el.click()` e o `browser_file_upload` são chamados em sequência imediata (sem passos no meio).
2. Tentar rolar o elemento pra view primeiro: `el.scrollIntoView({ behavior: 'instant' }); el.click();`.
3. Se persistir: navegar ao formulário novamente (às vezes uma segunda navegação resolve cache).

## Mais de um botão parece ser "Salvar"

**Solução**: filtrar por seletor exato `input[type='submit'][value='Salvar']` e confirmar que nenhum candidato tem texto contendo `enviar`, `submeter`, `finalizar`, `concluir` (case-insensitive). Se ainda houver ambiguidade, usar `AskUserQuestion` listando os candidatos.

## Schema desatualizado — seletores pararam de funcionar

**Sinal**: `CKEDITOR.instances[id].setData` lança erro ou a lista de instâncias não tem 9 chaves.

**Causa**: SUAP mudou o layout do formulário e os IDs das textareas mudaram.

**Solução**: rodar `discover_rit_form.py` novamente para regerar `rit_form_schema.json`:

```bash
python3 -m scripts.suap.discover_rit_form --url <form_url>
```

Commitar o novo schema após verificar que os novos seletores funcionam.

## `pypdf` não encontrado

```bash
python3 -m pip install pypdf
# ou, se o pip não estiver no PATH:
python3 -m pip install pypdf
```

## Manifesto não tem `entregas` preenchidas

O script `consolidar_pdfs.py` vai gerar consolidados vazios ou pular seções. Preencher `manifesto.json.entregas` antes de executar — cada entrega precisa de `eixo` e `arquivo` corretos.
