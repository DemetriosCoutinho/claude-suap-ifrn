"""
Unifica os PDFs de evidência de um eixo do RIT em um único arquivo consolidado.

Lê a ordem de arquivos do manifesto.json do período, filtra por eixo,
e concatena os PDFs na pasta _consolidados/.

Uso:
    python -m scripts.pdf.merge_eixo --periodo 2025.2
    python -m scripts.pdf.merge_eixo --periodo 2025.2 --eixo ensino
    python -m scripts.pdf.merge_eixo --periodo 2025.2 --eixo pesquisa
"""

import argparse
import json
from pathlib import Path

from pypdf import PdfWriter


PLUGIN_DIR = Path(__file__).resolve().parents[2]
EIXOS_VALIDOS = ("ensino", "pesquisa", "gestao", "orientacoes")


def merge_eixo(periodo: str, eixo: str, data_dir: Path) -> Path:
    """
    Concatena os PDFs de um eixo e salva em periodos/<periodo>/rit/_consolidados/<eixo>.pdf.

    Retorna o caminho do arquivo gerado.
    """
    base = data_dir / "periodos" / periodo / "rit"
    manifesto_path = base / "_meta" / "manifesto.json"

    if not manifesto_path.exists():
        raise FileNotFoundError(f"Manifesto não encontrado: {manifesto_path}")

    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    entregas = [
        e for e in manifesto.get("entregas", [])
        if e.get("eixo") == eixo
    ]

    if not entregas:
        print(f"[{eixo}] Nenhuma entrega no manifesto para este eixo. Pulando.")
        return None

    writer = PdfWriter()
    incluidos = []
    ausentes = []

    for entrega in entregas:
        pdf_path = base / entrega["arquivo"]
        if not pdf_path.exists():
            ausentes.append(entrega["arquivo"])
            print(f"  AVISO: arquivo não encontrado — {pdf_path}")
            continue
        writer.append(str(pdf_path))
        incluidos.append(pdf_path.name)
        print(f"  + {pdf_path.name}")

    if not incluidos:
        print(f"[{eixo}] Nenhum PDF encontrado em disco. Consolidado não gerado.")
        return None

    consolidados_dir = base / "_consolidados"
    consolidados_dir.mkdir(parents=True, exist_ok=True)
    saida = consolidados_dir / f"{eixo}.pdf"

    with open(saida, "wb") as f:
        writer.write(f)

    print(f"[{eixo}] Consolidado gerado: {saida.relative_to(data_dir)}")
    print(f"  Incluídos ({len(incluidos)}): {', '.join(incluidos)}")
    if ausentes:
        print(f"  Ausentes ({len(ausentes)}): {', '.join(ausentes)}")

    return saida


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unifica PDFs de evidência por eixo do RIT."
    )
    parser.add_argument(
        "--periodo",
        required=True,
        help="Semestre no formato AAAA.S (ex.: 2025.2)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("."),
        help="Pasta raiz dos dados SUAP (onde fica periodos/). Default: diretório atual.",
    )
    parser.add_argument(
        "--eixo",
        default="all",
        choices=[*EIXOS_VALIDOS, "all"],
        help="Eixo a consolidar. 'all' processa todos (padrão).",
    )
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    eixos = EIXOS_VALIDOS if args.eixo == "all" else (args.eixo,)

    for eixo in eixos:
        print(f"\n=== {eixo.upper()} ===")
        merge_eixo(args.periodo, eixo, data_dir)


if __name__ == "__main__":
    main()
