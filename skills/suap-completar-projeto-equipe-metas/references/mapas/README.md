# Mapas canônicos dos formulários SUAP

Mapeados na execução real do projeto #9139 (edital 02/2026, 2026-04-20) via Playwright.

## Arquivos

| Arquivo | URL do form | ID do form | Descrição |
|---------|-------------|-----------|-----------|
| `adicionar-aluno.json` | `/pesquisa/adicionar_participante_aluno/{projeto_id}/` | `participacaoaluno_form` | Cadastro de aluno na equipe |
| `adicionar-servidor.json` | `/pesquisa/adicionar_participante_servidor/{projeto_id}/` | `participacaoservidor_form` | Cadastro de servidor na equipe |
| `adicionar-meta.json` | `/pesquisa/adicionar_meta/{projeto_id}/` | `meta_form` | Cadastro de meta (objetivo específico) |
| `adicionar-atividade.json` | `/pesquisa/adicionar_etapa/{meta_id}/` | `etapa_form` | Cadastro de atividade (etapa) |

Também existe `/pesquisa/adicionar_participante_colaborador/{projeto_id}/` para colaboradores externos, mas não foi mapeado.

Para editar atividade já criada: `/pesquisa/editar_etapa/{etapa_id}/` — mesmo form `etapa_form`.

## Quando refazer descoberta

Refazer descoberta via Playwright se:
- O SUAP foi atualizado e campos novos apareceram.
- Um submit retornou erro "campo obrigatório" que não está no mapa.
- A URL base mudou (improvável, mas verificar se o IFRN migrou versão do SUAP).

## Como usar

Scripts Python da Fase 3 leem estes JSONs diretamente (campo `fields[].name`, `fields[].id`) para construir os payloads e o JS de preenchimento — sem precisar abrir o DOM do SUAP.

A Fase 1 da skill deve verificar se os mapas existem aqui antes de tentar qualquer descoberta via Playwright.
