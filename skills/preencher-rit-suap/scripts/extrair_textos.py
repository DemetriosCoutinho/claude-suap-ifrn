"""
Extrai o corpo de texto dos 9 MDs de _redacao/ e salva em _submissao/.textos_prontos.json.

Por que script e não loop no LLM: reler 9 MDs + remover frontmatter + strip H1 + cortar
seções de análise gasta ~8k tokens a cada invocação. Python faz em milissegundos, zero tokens.

Uso:
    python3 .claude/skills/preencher-rit-suap/scripts/extrair_textos.py --periodo 2026.1
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]  # suap-automation/

SECOES = [
    ("aulas",                  "01_aulas.md"),
    ("preparacao_ensino",      "02_preparacao_ensino.md"),
    ("apoio_ensino",           "03_apoio_ensino.md"),
    ("projetos_ensino",        "04_projetos_ensino.md"),
    ("atendimento_orientacao", "05_atendimento_orientacao.md"),
    ("reunioes",               "06_reunioes.md"),
    ("pesquisa",               "07_pesquisa.md"),
    ("extensao",               "08_extensao.md"),
    ("gestao",                 "09_gestao.md"),
]

SECOES_ANALISE = ("## Referência", "## Comparação", "## Discrepâncias")


def parse_md(path: Path) -> tuple[dict, str]:
    content = path.read_text(encoding="utf-8")
    meta = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                m = re.match(r'^(\w+):\s*"?([^"]+)"?\s*$', line.strip())
                if m:
                    meta[m.group(1)] = m.group(2).strip()
            body = parts[2].strip()

    return meta, body


def extrair_corpo(body: str) -> str:
    lines = body.splitlines()
    resultado = []
    dentro_analise = False

    for line in lines:
        if any(line.startswith(s) for s in SECOES_ANALISE):
            dentro_analise = True
        elif line.startswith("## ") and dentro_analise:
            dentro_analise = False
        if not dentro_analise:
            resultado.append(line)

    texto = "\n".join(resultado).strip()
    if texto.startswith("# "):
        texto = "\n".join(texto.splitlines()[1:]).strip()
    return texto


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai textos dos MDs aprovados para .textos_prontos.json"
    )
    parser.add_argument("--periodo", required=True, help="Semestre AAAA.S (ex.: 2026.1)")
    args = parser.parse_args()

    base = RAIZ / "periodos" / args.periodo / "rit" / "_redacao"
    if not base.exists():
        print(f"ERRO: Diretório não encontrado: {base}", file=sys.stderr)
        sys.exit(1)

    erros = []
    secoes: dict = {}

    for secao, filename in SECOES:
        path = base / filename
        if not path.exists():
            erros.append(f"  Arquivo não encontrado: {path.relative_to(RAIZ)}")
            continue

        meta, body = parse_md(path)
        status = meta.get("status", "").lower()
        tipo   = meta.get("tipo", "").lower()

        if status == "rascunho":
            erros.append(
                f"  [{secao}] status: rascunho em {filename} — altere para 'aprovado' antes de continuar."
            )
            continue

        if status not in ("aprovado",) and tipo not in ("nao_se_aplica", "n/a"):
            erros.append(f"  [{secao}] status desconhecido: '{status}' em {filename}.")
            continue

        texto = extrair_corpo(body)
        secoes[secao] = {
            "arquivo": str(path.relative_to(RAIZ)),
            "chars": len(texto),
            "texto": texto,
        }

    if erros:
        print("ERRO: Seções com problemas encontradas:", file=sys.stderr)
        for e in erros:
            print(e, file=sys.stderr)
        print("\nResolva antes de preencher o formulário SUAP.", file=sys.stderr)
        sys.exit(1)

    saida_dir = RAIZ / "periodos" / args.periodo / "rit" / "_submissao"
    saida_dir.mkdir(parents=True, exist_ok=True)
    saida = saida_dir / ".textos_prontos.json"

    resultado = {
        "gerado_em": str(date.today()),
        "periodo": args.periodo,
        "secoes": secoes,
    }

    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Textos prontos: {saida.relative_to(RAIZ)}")
    for secao, dados in secoes.items():
        print(f"  [{secao}] {dados['chars']} chars")


if __name__ == "__main__":
    main()
