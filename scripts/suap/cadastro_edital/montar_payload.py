"""Extrai valores dos MDs de revisão e monta JSON de preenchimento.

Uso:
    python3 scripts/suap/cadastro_edital/montar_payload.py \
        projeto_pesquisa/campos/edital-02-2026 \
        > projeto_pesquisa/campos/edital-02-2026/_snapshot/payload.json
"""
from __future__ import annotations

import json
import pathlib
import re
import sys


def extract_valor_proposto(md_text: str) -> str:
    m = re.search(r"## Valor proposto\s*\n+(.*?)(?=\n## )", md_text, re.DOTALL)
    return m.group(1).strip() if m else ""


def markdown_to_html(text: str) -> str:
    """Converte blockquote + **bold** + *em* para HTML simples."""
    lines = text.split("\n")
    paragraphs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            paragraphs.append(" ".join(current))
            current.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            if content:
                current.append(content)
            else:
                flush()
        elif stripped == "":
            flush()
        else:
            current.append(stripped)
    flush()

    html_ps = []
    for p in paragraphs:
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", p)
        html_ps.append(f"<p>{p}</p>")
    return "\n".join(html_ps)


def extract_plain_text(md_value: str) -> str:
    """Extrai texto simples de valores que começam com **X** ou blockquote."""
    first_line = md_value.split("\n")[0].strip()
    # Remove leading blockquote
    first_line = first_line.lstrip(">").strip()
    # Remove markdown bold/italic
    first_line = re.sub(r"\*\*(.+?)\*\*", r"\1", first_line)
    first_line = re.sub(r"\*(.+?)\*", r"\1", first_line)
    return first_line


# Mapeamento: nome do MD → (name do campo SUAP, tipo de preenchimento)
# tipos: text | date | select | select-autocomplete | checkbox-termo | ckeditor | skip
FIELDS = {
    "01-campus.md": ("uo", "select-autocomplete", None),  # preencher via AskUserQuestion
    "02-titulo.md": ("titulo", "text", None),
    "03-valor-global.md": ("valor_global_projeto", "text", None),
    "04-inicio-execucao.md": ("inicio_execucao", "date", None),
    "05-termino-execucao.md": ("fim_execucao", "date", None),
    "06-area-conhecimento.md": ("area_conhecimento", "select", "12"),
    "07-grupo-pesquisa.md": ("grupo_pesquisa", "select-autocomplete", "NADIC"),
    "08-ppg.md": ("ppg", "skip", None),
    "09-parceria-externa.md": ("parceria_externa", "skip", None),
    "10-palavras-chave.md": ("palavras_chaves", "text", None),
    "11-trl.md": ("classificacao_trl", "select", "TRL 7"),
    "12-cep-ceua-sisgen-sisbio.md": ("_etica", "multi-select", {
        "precisa_cep": "False",
        "precisa_ceua": "False",
        "precisa_sisgen": "False",
        "precisa_sisbio": "False",
    }),
    "13-laboratorio-multiusuario.md": ("vinculado_laboratorio_multiusuario", "select", "False"),
    "14-ods.md": ("tem_ods", "select", "False"),
    "15-resumo.md": ("resumo", "ckeditor", None),
    "16-introducao.md": ("introducao", "ckeditor", None),
    "17-justificativa.md": ("justificativa", "ckeditor", None),
    "18-fundamentacao-teorica.md": ("fundamentacao_teorica", "ckeditor", None),
    "19-objetivo-geral.md": ("objetivo_geral", "ckeditor", None),
    "20-metodologia.md": ("metodologia", "ckeditor", None),
    "21-acompanhamento-avaliacao.md": ("acompanhamento_e_avaliacao", "ckeditor", None),
    "22-resultados-esperados.md": ("resultados_esperados", "ckeditor", None),
    "23-referencias.md": ("referencias_bibliograficas", "ckeditor", None),
    "24-termo-compromisso.md": ("aceita_termo", "checkbox-termo", True),
}


def main() -> None:
    base = pathlib.Path(sys.argv[1])
    payload: list[dict] = []
    for md_name, (field_name, kind, override) in FIELDS.items():
        md_path = base / md_name
        if not md_path.exists():
            continue
        raw = md_path.read_text(encoding="utf-8")
        status_match = re.search(r"^status:\s*(\S+)", raw, re.MULTILINE)
        status = status_match.group(1) if status_match else "pendente"

        valor = extract_valor_proposto(raw)

        entry: dict = {
            "md": md_name,
            "field": field_name,
            "kind": kind,
            "status": status,
        }

        if kind == "skip":
            entry["value"] = None
            entry["note"] = "campo deixado vazio por decisão do usuário"
        elif kind == "ckeditor":
            entry["html"] = markdown_to_html(valor)
        elif kind == "multi-select":
            entry["values"] = override
        elif kind == "checkbox-termo":
            entry["checked"] = True
        elif kind == "select-autocomplete":
            entry["search_term"] = override
        elif kind == "select":
            entry["value"] = override
        elif kind == "text":
            # Pega primeira linha não-vazia após "## Valor proposto"
            plain = extract_plain_text(valor)
            # Remove **markdown** bold leftovers
            entry["value"] = plain
        elif kind == "date":
            # Valor tipo "**2025-11-01** (01/11/2025)" → "2025-11-01"
            m = re.search(r"\d{4}-\d{2}-\d{2}", valor)
            entry["value"] = m.group(0) if m else ""
        payload.append(entry)

    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
