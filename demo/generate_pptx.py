"""Generate the ten-slide synthetic 5G RAN operations demo deck.

Usage: ``uv run python demo/generate_pptx.py [--output PATH]``.

Every slide carries a visible SYNTHETIC banner and footer. All operator names,
incidents and metrics are invented for the demonstration; none come from, or
represent, a real operator. Output bytes are deterministic (fixed document
properties and ZIP timestamps), so the same code always yields the same SHA-256.
The deck is generated rather than committed (``demo/*.pptx`` is gitignored).
"""

from __future__ import annotations

import argparse
import datetime as dt
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "5G_RAN_Operations_Demo.pptx"

BANNER = "SYNTHETIC DEMO DATA"
FOOTER = (
    "Synthetic dataset for demonstration only. ExampleNet Mobile is fictional; "
    "metrics are invented and do not represent any real operator."
)
# Speaker notes are excluded from extraction; tests assert this text is never indexed.
NOTES_MARKER = "PRESENTER NOTE (not indexed)"

_FIXED_TIME = dt.datetime(2026, 1, 1, 0, 0, 0)
_ZIP_TIME = (2026, 1, 1, 0, 0, 0)

# (title, body paragraphs). Slide numbers are list positions + 1.
SLIDES: list[tuple[str, list[str]]] = [
    (
        "Overview: ExampleNet Mobile 5G operations (fictional)",
        [
            "ExampleNet Mobile is a fictional operator used for this demonstration.",
            "The synthetic environment covers 120 gNodeB sites in the Metro North region.",
            "This deck reviews network KPIs, the fictional incident INC-042 and follow-up actions.",
        ],
    ),
    (
        "RAN architecture: gNodeB, transport and 5G core",
        [
            "Radio units connect to gNodeB baseband in each site.",
            "Transport carries traffic from gNodeB sites over fronthaul and backhaul links "
            "to the aggregation routers.",
            "The 5G core (AMF, SMF, UPF) terminates control and user-plane traffic.",
        ],
    ),
    (
        "Network KPIs: availability, throughput, latency, utilization",
        ["Monthly synthetic KPI summary for the Metro North region:"],
    ),
    (
        "Latency performance",
        [
            "Baseline user-plane latency in the Metro North region was 18 ms.",
            "During incident INC-042 latency rose to a peak of 46 ms on cell cluster C7 "
            "during the evening busy hour.",
            "Latency returned to the 18 ms baseline after mitigation.",
        ],
    ),
    (
        "Cell congestion",
        [
            "PRB utilization on cell cluster C7 reached 92% during congestion in the evening "
            "busy hour.",
            "The illustrative congestion threshold is 85% PRB utilization.",
            "Sustained utilization above the threshold reduced per-user throughput.",
        ],
    ),
    (
        "Incident overview: INC-042",
        [
            "INC-042 is a fictional incident: elevated latency on cell cluster C7.",
            "Duration: 3 hours 20 minutes during the evening busy hour.",
            "Impact: 14 cells with degraded user-plane latency and lower throughput.",
        ],
    ),
    (
        "Root-cause investigation",
        [
            "Root cause: backhaul saturation on the transport link serving cell cluster C7.",
            "Peak-hour congestion (PRB utilization 92%) coincided with the saturated backhaul.",
            "Together, backhaul saturation and peak-hour congestion raised latency "
            "from 18 ms to 46 ms.",
        ],
    ),
    (
        "Troubleshooting procedure",
        [
            "When latency rises during peak hours, investigate in this order:",
            "1. Validate traffic volume against the busy-hour traffic profile.",
            "2. Check cell counters such as PRB utilization and RRC connected users.",
            "3. Inspect transport and backhaul utilization, packet loss and errors.",
            "4. Review active alarms on the gNodeB and transport equipment.",
        ],
    ),
    (
        "Optimization actions",
        [
            "Capacity balancing: shift load from congested C7 cells to neighbouring cells.",
            "Transport upgrade: increase the C7 backhaul link from 1 Gbps to 10 Gbps.",
            "KPI monitoring: alert when PRB utilization exceeds 85% or latency exceeds 30 ms.",
        ],
    ),
    (
        "Lessons learned",
        [
            "Detection improvement: correlate radio and transport KPIs on one dashboard.",
            "Alert earlier on sustained PRB utilization above the 85% threshold.",
            "Recommendation: review backhaul capacity before forecast traffic peaks.",
        ],
    ),
]

KPI_TABLE = [
    ("KPI", "Synthetic value"),
    ("Availability", "99.95%"),
    ("Average downlink throughput", "310 Mbps"),
    ("Baseline latency", "18 ms"),
    ("Average PRB utilization", "61%"),
]


def _text_box(slide, left, top, width, height, text: str, size: int, bold: bool = False):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    frame.text = text
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(size)
            run.font.bold = bold
    return box


def _add_body(slide, paragraphs: list[str]) -> None:
    box = slide.shapes.add_textbox(Inches(0.6), Inches(1.9), Inches(8.8), Inches(4.2))
    frame = box.text_frame
    frame.word_wrap = True
    frame.text = paragraphs[0]
    for text in paragraphs[1:]:
        frame.add_paragraph().text = text
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(16)


def _add_architecture_group(slide) -> None:
    """Slide 2 body as a group shape, so extraction must recurse into groups."""
    group = slide.shapes.add_group_shape()
    for i, label in enumerate(("gNodeB", "Transport (backhaul)", "5G core")):
        _text_box(group, Inches(0.6 + 3.0 * i), Inches(4.6), Inches(2.6), Inches(0.8), label, 16)


def _add_kpi_table(slide) -> None:
    rows, cols = len(KPI_TABLE), 2
    shape = slide.shapes.add_table(rows, cols, Inches(0.6), Inches(2.5), Inches(8.8), Inches(2.5))
    for r, row in enumerate(KPI_TABLE):
        for c, value in enumerate(row):
            shape.table.cell(r, c).text = value


def build_deck() -> Presentation:
    prs = Presentation()
    blank = prs.slide_layouts[6]
    for number, (title, body) in enumerate(SLIDES, start=1):
        slide = prs.slides.add_slide(blank)
        _text_box(slide, Inches(0.6), Inches(0.2), Inches(8.8), Inches(0.5), BANNER, 14, True)
        _text_box(slide, Inches(0.6), Inches(0.8), Inches(8.8), Inches(1.0), title, 28, True)
        _add_body(slide, body)
        if number == 2:
            _add_architecture_group(slide)
        if number == 3:
            _add_kpi_table(slide)
        _text_box(slide, Inches(0.6), Inches(6.7), Inches(8.8), Inches(0.6), FOOTER, 10)
        slide.notes_slide.notes_text_frame.text = f"{NOTES_MARKER}: slide {number} talking points."
    props = prs.core_properties
    props.title = "5G RAN Operations Demo (synthetic)"
    props.author = "SlideRAG Mini demo generator"
    props.last_modified_by = "SlideRAG Mini demo generator"
    props.created = _FIXED_TIME
    props.modified = _FIXED_TIME
    props.revision = 1
    return prs


def _normalize_zip(path: Path) -> None:
    """Rewrite member timestamps so identical content yields identical bytes."""
    with zipfile.ZipFile(path) as source:
        members = [(info.filename, source.read(info)) for info in source.infolist()]
    tmp = path.with_name(path.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            target.writestr(info, data)
    tmp.replace(path)


def write_deck(output: Path = DEFAULT_OUTPUT) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    build_deck().save(str(output))
    _normalize_zip(output)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the synthetic SlideRAG Mini demo deck.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output .pptx path (default: {DEFAULT_OUTPUT.name} next to this script)",
    )
    args = parser.parse_args(argv)
    path = write_deck(args.output)
    print(f"wrote {path} ({len(SLIDES)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
