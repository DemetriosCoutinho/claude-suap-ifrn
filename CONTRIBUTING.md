# Como contribuir

## Propondo uma nova skill

1. Crie `skills/<verbo>-<objeto>-suap/SKILL.md` com o frontmatter mínimo:

```yaml
---
name: <verbo>-<objeto>-suap
description: >
  Uma linha descrevendo quando esta skill deve ser ativada automaticamente.
---
```

2. **`AskUserQuestion` é obrigatório** para qualquer path de dado do usuário. Nunca assuma paths hardcoded.

3. Padrão de naming: `verbo-objeto-suap` (ex.: `exportar-pit-suap`, `validar-rit-suap`).

4. Toda skill deve ter uma seção `## Nunca fazer` com pelo menos:
   - Não submeter sem confirmação humana explícita.
   - Não inventar dados ausentes.

## Enviando um PR

- Um PR por skill ou por funcionalidade.
- Inclua um exemplo de sessão no PR description.
- Garanta que nenhum dado pessoal (nome, matrícula, campus específico) está no código.

## Convenções

- **Commits**: em inglês, imperativos curtos (`fix`, `add`, `update`).
- **Idioma**: português em todos os artefatos (SKILL.md, checklists, docs).
- **Python**: gerenciar dependências com `uv` (`uv pip install`, `uv run`). Testes: `uv run pytest`.
- **Sem dados pessoais**: nenhum path absoluto, nome de usuário, matrícula ou campus específico no código.

## Reportando problemas

Abra uma issue descrevendo: o que tentou fazer, o comportamento esperado e o que aconteceu.
