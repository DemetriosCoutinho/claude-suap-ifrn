# CKEditor 4 — padrão de preenchimento (SUAP RIT)

## Por que CKEditor exige tratamento especial

O SUAP RIT usa **CKEditor 4** (não TinyMCE). O editor substitui cada `<textarea>` por um iframe com `contenteditable`. Qualquer tentativa de escrever diretamente na textarea (`page.fill()`, `el.value = ...`, textarea nativa) **não reflete no editor visual** — o campo parece preenchido no DOM mas aparece vazio para o usuário e é descartado no save.

A única API que funciona:

```javascript
CKEDITOR.instances['<textarea_id>'].setData('<html_string>');
```

Invocar via `browser_evaluate`.

## Detectar que o CKEditor carregou

Antes de qualquer `setData`, garantir que o formulário está totalmente carregado:

```javascript
// Verificar disponibilidade
typeof CKEDITOR !== 'undefined'
// → true

// Listar editores ativos (deve retornar 9 chaves para o RIT)
Object.keys(CKEDITOR.instances)
// → ["id_obs_aulas", "id_obs_preparacao_manutencao_ensino", ...]
```

Se `CKEDITOR` for `undefined`: usar `browser_wait_for(text="Relatório Individual de Trabalho")` e tentar novamente.

## Mapeamento secao → textarea id

| Seção canônica | Textarea ID |
|---------------|-------------|
| aulas | `id_obs_aulas` |
| preparacao_ensino | `id_obs_preparacao_manutencao_ensino` |
| apoio_ensino | `id_obs_apoio_ensino` |
| projetos_ensino | `id_obs_programas_projetos_ensino` |
| atendimento_orientacao | `id_obs_orientacao_alunos` |
| reunioes | `id_obs_reunioes` |
| pesquisa | `id_obs_pesquisa` |
| extensao | `id_obs_extensao` |
| gestao | `id_obs_gestao` |

(Fonte: `scripts/suap/.discovery/rit_form_schema.json` campo `mapeamento_secao_selector`)

## Snippet canônico — preencher um campo

```javascript
// via browser_evaluate
CKEDITOR.instances['id_obs_aulas'].setData(
  '<p>No período 2025.2, o professor...</p>'
);
```

Verificar após setar:

```javascript
CKEDITOR.instances['id_obs_aulas'].getData().length > 10
// → true se preenchido
```

## Regras de conversão markdown → HTML

O texto em `.textos_prontos.json` é markdown simples. Converter antes de chamar `setData`:

| Markdown | HTML |
|---------|------|
| Parágrafo separado por linha em branco | `<p>...</p>` |
| `- item` (lista com hífen) | `<ul><li>item</li></ul>` (agrupar consecutivos) |
| `**texto**` | `<strong>texto</strong>` |
| `*texto*` | `<em>texto</em>` |
| Sub-item `  - item` | `<ul><ul><li>item</li></ul></ul>` |
| Linha vazia entre lista e próximo parágrafo | fechar `</ul>` antes de abrir `<p>` |

**Regra geral**: cada bloco de texto separado por linha em branco vira um `<p>`. Listas contíguas ficam dentro de um único `<ul>`.

## Exemplo completo — seção pesquisa

**Entrada** (markdown de `.textos_prontos.json`):

```
Durante o semestre letivo de <ano-semestre>, o professor participou ativamente de diversas ações de pesquisa.

**Atividades realizadas:**

- Coordenação do projeto "<projeto-1>" (Edital <nn-aaaa>), período de <dd-mm-aaaa> a <dd-mm-aaaa>;
- Membro do projeto "<projeto-2>" (Edital <nn-aaaa>), a partir de <dd-mm-aaaa>;
- Orientação de N alunos de IC:
  - <aluno-1> (bolsista);
  - <aluno-2> (bolsista);
  - <aluno-3> (voluntário).
```

**Saída** (HTML para `setData`):

```html
<p>Durante o semestre letivo de <ano-semestre>, o professor participou ativamente de diversas ações de pesquisa.</p>
<p><strong>Atividades realizadas:</strong></p>
<ul>
<li>Coordenação do projeto "<projeto-1>" (Edital <nn-aaaa>), período de <dd-mm-aaaa> a <dd-mm-aaaa>;</li>
<li>Membro do projeto "<projeto-2>" (Edital <nn-aaaa>), a partir de <dd-mm-aaaa>;</li>
<li>Orientação de N alunos de IC:
  <ul>
  <li><aluno-1> (bolsista);</li>
  <li><aluno-2> (bolsista);</li>
  <li><aluno-3> (voluntário).</li>
  </ul>
</li>
</ul>
```

## Armadilhas conhecidas

- **Não usar `\n` literal dentro da string JS** passada via `browser_evaluate` — escapar ou usar template literal.
- **Aspas duplas no texto**: escapar para `&quot;` ou usar aspas simples na string JS.
- **`setData` sincrônico**: o dado fica disponível imediatamente via `getData()` — não precisa aguardar.
- **O save coleta do `getData()`, não da textarea**: mesmo que a textarea DOM esteja vazia, o CKEditor salva o que foi passado via `setData`. Mas se o editor não renderizou (JavaScript não carregou), o campo vai vazio.
