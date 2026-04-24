"""
Consolida PDFs de evidência por seção do formulário SUAP RIT (não por eixo do manifesto).

O mapeamento eixo→seção é diferente do mapeamento eixo→eixo que merge_eixo.py faz.
Por exemplo, 'gestao' do SUAP inclui itens de eixo 'gestao' + 'ensino' (Comissão PPC ADS).

Lê o manifesto do período para descobrir quais arquivos existem; não hard-codes paths.

Uso:
    python3 .claude/skills/preencher-rit-suap/scripts/consolidar_pdfs.py --periodo 2026.1
    python3 .claude/skills/preencher-rit-suap/scripts/consolidar_pdfs.py --periodo 2026.1 --dry-run
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

try:
    from pypdf import PdfWriter
except ImportError:
    print("ERRO: pypdf não instalado. Rode: python3 -m pip install pypdf", file=sys.stderr)
    sys.exit(1)

PLUGIN_DIR = Path(__file__).resolve().parents[4]  # claude-suap-ifrn/

# Palavras-chave que identificam entradas de eixo 'ensino' que pertencem à seção 'gestao' do SUAP
# (comissão de elaboração do PPC — portaria da reitoria)
PALAVRAS_PPC = re.compile(r"ppc|comiss[aã]o ppc|comissão ppc", re.IGNORECASE)


def classificar_entrega(entrega: dict) -> str | None:
    """
    Devolve a seção SUAP para a qual esta entrega deve ir, ou None se não for para nenhuma.

    Seções sem PDF (preparacao_ensino, projetos_ensino, reunioes, extensao): retornam None.
    """
    eixo = entrega.get("eixo", "")
    nome = entrega.get("nome", "")
    arquivo = entrega.get("arquivo", "")
    status = entrega.get("status_validacao", "")

    # Referências (_ref/) nunca viram consolidados de seção
    if arquivo.startswith("_ref/"):
        return None

    # Eixo ref (disciplinas.pdf, pit, rit anterior) também são referências
    if eixo == "ref":
        return None

    if eixo == "ensino":
        if PALAVRAS_PPC.search(nome):
            return "gestao"
        return "apoio_ensino"

    if eixo == "pesquisa":
        return "pesquisa"

    if eixo == "gestao":
        return "gestao"

    if eixo == "orientacoes":
        return "atendimento_orientacao"

    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolida PDFs de evidência por seção SUAP (não por eixo)."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("."),
        help="Pasta raiz dos dados SUAP (onde fica periodos/). Default: dir atual.")
    parser.add_argument("--periodo", required=True, help="Semestre AAAA.S (ex.: 2026.1)")
    parser.add_argument("--dry-run", action="store_true", help="Apenas listar, não gravar.")
    args = parser.parse_args()
    data_dir = args.data_dir.expanduser().resolve()

    base = data_dir / "periodos" / args.periodo / "rit"
    manifesto_path = base / "_meta" / "manifesto.json"

    if not manifesto_path.exists():
        print(f"ERRO: Manifesto não encontrado: {manifesto_path}", file=sys.stderr)
        sys.exit(1)

    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    entregas = manifesto.get("entregas", [])

    # Agrupar por seção
    por_secao: dict[str, list[Path]] = {}

    for entrega in entregas:
        secao = classificar_entrega(entrega)
        if secao is None:
            continue
        pdf_path = base / entrega["arquivo"]
        if not pdf_path.exists():
            print(f"  AVISO: arquivo ausente — {entrega['arquivo']}")
            continue
        por_secao.setdefault(secao, []).append(pdf_path)

    # Aulas: caso especial — usa _ref/disciplinas.pdf diretamente
    disciplinas = base / "_ref" / "disciplinas.pdf"
    if disciplinas.exists():
        por_secao["aulas"] = [disciplinas]
    else:
        print("  AVISO: _ref/disciplinas.pdf não encontrado — aulas sem PDF.")

    # Ordem canônica de geração
    ordem = ["aulas", "apoio_ensino", "atendimento_orientacao", "pesquisa", "gestao"]
    consolidados_dir = base / "_consolidados"

    if not args.dry_run:
        consolidados_dir.mkdir(parents=True, exist_ok=True)

    for secao in ordem:
        pdfs = por_secao.get(secao, [])
        if not pdfs:
            print(f"[{secao}] sem PDFs — pulando.")
            continue

        saida = consolidados_dir / f"{secao}.pdf"
        print(f"[{secao}] {len(pdfs)} arquivo(s):")
        for p in pdfs:
            print(f"  + {p.relative_to(base)}")

        if args.dry_run:
            print(f"  → (dry-run) gravaria {saida.relative_to(data_dir)}")
            continue

        if len(pdfs) == 1:
            # Cópia direta — sem overhead de re-encode via pypdf
            shutil.copy2(str(pdfs[0]), str(saida))
        else:
            writer = PdfWriter()
            for p in pdfs:
                writer.append(str(p))
            with open(saida, "wb") as f:
                writer.write(f)

        print(f"  → {saida.relative_to(data_dir)}")


if __name__ == "__main__":
    main()
