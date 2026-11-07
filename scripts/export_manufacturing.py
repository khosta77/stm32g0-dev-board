#!/usr/bin/env python3
"""Regenerate manufacturing outputs (Gerber, drill, JLCPCB BOM/CPL, schematic PDF, renders).

Usage:
    python3 scripts/export_manufacturing.py [--kicad-cli PATH] [--no-render]
"""

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = "g0_dev_board"
PCB = ROOT / f"{PROJECT}.kicad_pcb"
SCH = ROOT / f"{PROJECT}.kicad_sch"
MFG = ROOT / "manufacturing"
GERBER_DIR = MFG / "gerber"
DOCS = ROOT / "docs"
DEFAULT_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
LAYERS = (
    "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,"
    "F.Mask,B.Mask,Edge.Cuts"
)
EXCLUDED_REF_PREFIXES = ("FID", "H")


def run(cli: str, *args: str) -> None:
    result = subprocess.run([cli, *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"kicad-cli failed: {' '.join(args[:3])}")


def export_gerbers(cli: str) -> None:
    shutil.rmtree(GERBER_DIR, ignore_errors=True)
    GERBER_DIR.mkdir(parents=True)
    run(cli, "pcb", "export", "gerbers", "--layers", LAYERS, "--no-protel-ext",
        "--subtract-soldermask", "--check-zones", "-o", f"{GERBER_DIR}/", str(PCB))
    run(cli, "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
        "--generate-map", "--map-format", "pdf", "--drill-origin", "absolute",
        "-o", f"{GERBER_DIR}/", str(PCB))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def ref_key(ref: str) -> tuple[str, int]:
    prefix = ref.rstrip("0123456789")
    number = ref[len(prefix):]
    return prefix, int(number) if number else 0


def export_bom(cli: str, tmp: Path) -> set[str]:
    raw = tmp / "bom.csv"
    run(cli, "sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,${DNP}",
        "--labels", "Ref,Value,Footprint,LCSC,DNP", "--group-by", "",
        "-o", str(raw), str(SCH))
    groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in read_csv(raw):
        ref = row["Ref"]
        if row["DNP"] or ref.startswith(EXCLUDED_REF_PREFIXES):
            continue
        footprint = row["Footprint"].split(":")[-1]
        groups[(row["Value"], footprint, row["LCSC"])].append(ref)
    rows = []
    placed: set[str] = set()
    for (value, footprint, lcsc), refs in groups.items():
        refs.sort(key=ref_key)
        placed.update(refs)
        rows.append([value, ",".join(refs), footprint, lcsc])
    rows.sort(key=lambda r: ref_key(r[1].split(",")[0]))
    write_csv(MFG / f"BOM-{PROJECT}.csv", ["Comment", "Designator", "Footprint", "LCSC Part #"], rows)
    return placed


def export_cpl(cli: str, tmp: Path, placed: set[str]) -> None:
    raw = tmp / "pos.csv"
    run(cli, "pcb", "export", "pos", "--side", "both", "--format", "csv", "--units", "mm",
        "--exclude-dnp", "-o", str(raw), str(PCB))
    rows = []
    for row in read_csv(raw):
        ref = row["Ref"]
        if ref not in placed:
            continue
        layer = "top" if row["Side"] == "top" else "bottom"
        rows.append([ref, row["Val"], row["Package"], f"{float(row['PosX']):.4f}mm",
                     f"{float(row['PosY']):.4f}mm", layer, f"{float(row['Rot']):.1f}"])
    rows.sort(key=lambda r: ref_key(r[0]))
    write_csv(MFG / f"CPL-{PROJECT}.csv",
              ["Designator", "Val", "Package", "Mid X", "Mid Y", "Layer", "Rotation"], rows)


def export_docs(cli: str, render: bool) -> None:
    (DOCS / "images").mkdir(parents=True, exist_ok=True)
    run(cli, "sch", "export", "pdf", "-o", str(DOCS / "schematic.pdf"), str(SCH))
    if not render:
        return
    for side in ("top", "bottom"):
        run(cli, "pcb", "render", "--side", side, "--quality", "high", "--background", "opaque",
            "--width", "1600", "--height", "2200", "-o", str(DOCS / "images" / f"pcb-{side}.png"),
            str(PCB))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kicad-cli", default=DEFAULT_CLI, help="path to kicad-cli")
    parser.add_argument("--no-render", action="store_true", help="skip 3D PNG renders")
    args = parser.parse_args()
    MFG.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        export_gerbers(args.kicad_cli)
        placed = export_bom(args.kicad_cli, tmp)
        export_cpl(args.kicad_cli, tmp, placed)
    export_docs(args.kicad_cli, not args.no_render)
    print(f"outputs written to {MFG.relative_to(ROOT)}/ and {DOCS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
