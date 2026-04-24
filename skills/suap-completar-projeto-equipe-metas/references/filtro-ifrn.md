# Filtro por Instituição (coluna §11 do PDF)

## Regra

Só entram na aba Equipe do SUAP membros cuja última coluna da tabela §11 do Plano de Trabalho contenha a substring definida em `filtrar_coluna_instituicao` (default: `"IFRN"`). Todos os outros são **excluídos** da aba Equipe — registrados apenas no `00-equipe-manifesto.md` como "excluídos por filtro".

**Por quê**: o PDF do Plano inclui colaboradores externos (UFRN, empresas parceiras, etc.) para fins de documentação acadêmica/orçamentária, mas o formulário SUAP de Equipe é restrito a vinculados da instituição que sedia o projeto.

## Extração da coluna

A tabela §11 tem cabeçalho variável por edital. Exemplos:

- Edital 02/2026: colunas "Nome", "CPF", "Função", "Carga Horária", "Lattes", "Instituição".
- A última coluna é tipicamente **"Instituição"** (ou "Vínculo", "Origem").

Algoritmo (`scripts/suap/completar_projeto/extrair_equipe_pdf.py`):

```python
import pdfplumber

def extrair_equipe(pdf_path: str, filtro: str = "IFRN") -> list[dict]:
    membros = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # heurística: tabela com cabeçalho que contenha "Instituição" ou "Vínculo"
                header = table[0] if table else []
                if not any("Institui" in (c or "") or "V\u00EDnculo" in (c or "") for c in header):
                    continue
                idx_instituicao = next(
                    (i for i, c in enumerate(header) if "Institui" in (c or "") or "V\u00EDnculo" in (c or "")),
                    -1,
                )
                for row in table[1:]:
                    if not row or all(not (c or "").strip() for c in row):
                        continue
                    instituicao = (row[idx_instituicao] or "").strip()
                    passa_filtro = filtro.lower() in instituicao.lower()
                    membros.append({
                        "nome": (row[0] or "").strip(),
                        "instituicao_raw": instituicao,
                        "passa_filtro": passa_filtro,
                        "linha_bruta": row,
                    })
    return membros
```

## Pendências conhecidas por OCR

OCRs de PDFs escaneados confundem:

- "IFRN" ↔ "Redução" (letras com serifas parecidas em scans ruins)
- "IFRN" ↔ "IFPB"/"IFRJ" (depende do campus)
- "UFRN" ↔ "IFRN" (quando a primeira letra está borrada)

**Política**: se a célula for ambígua ou ilegível, **não** classificar automaticamente. Registrar em `00-equipe-manifesto.md` como pendência humana, com transcrição literal do que o OCR leu + indicação da provável interpretação. Usuário decide na revisão.

Exemplo no manifesto (pendência #1 do projeto #9139):

> **Rayron Victor Medeiros de Araújo** — última coluna lida como `"Redução/Aluno"`. Provável leitura errada de `"IFRN/Aluno"`. Decidir: incluir (IFRN) ou excluir (outro).

## Relação com a aba Equipe

Após o filtro:

- `passa_filtro=True` → gerar MD em `{edital_slug}/equipe/NN-{slug-nome}.md` com `status: pendente`.
- `passa_filtro=False` → **não** gerar MD. Apenas listar no manifesto como "excluído por filtro" com o valor exato da coluna.
- Ambíguos → gerar MD mas com `status: pendente` e observação destacada; pendência humana no manifesto.

## Relaxamento do filtro

Em editais onde **parcerias externas precisam entrar na Equipe do SUAP** (raro, mas possível), invocar a skill com `filtrar_coluna_instituicao=""` (string vazia) — todo mundo passa. Nesse caso o humano é quem decide exclusões no momento da revisão.
