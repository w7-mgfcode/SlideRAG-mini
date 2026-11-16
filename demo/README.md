# Synthetic demo deck

`generate_pptx.py` builds `5G_RAN_Operations_Demo.pptx`: ten slides of invented
5G RAN operations data for the fictional operator ExampleNet Mobile. Every slide
shows a `SYNTHETIC DEMO DATA` banner and a footer stating that the metrics are
invented and do not represent any real operator. Only this synthetic text may be
sent to the embedding and chat APIs.

```bash
uv run python demo/generate_pptx.py                         # writes demo/5G_RAN_Operations_Demo.pptx
uv run python demo/generate_pptx.py --output /tmp/deck.pptx # any other path
```

The deck is generated, not committed (`demo/*.pptx` is gitignored), and tests
build it into a temporary directory. Output is byte-deterministic: document
properties and ZIP timestamps are fixed, so unchanged code yields the same
SHA-256 (useful for the duplicate-upload check).

## Slide facts

| Slide | Topic | Key synthetic content |
|---:|---|---|
| 1 | Overview | Fictional operator, 120 gNodeB sites, Metro North region |
| 2 | RAN architecture | gNodeB → transport (fronthaul/backhaul) → 5G core (AMF, SMF, UPF); labels in a group shape |
| 3 | Network KPIs | Table: availability 99.95%, DL throughput 310 Mbps, baseline latency 18 ms, PRB 61% |
| 4 | Latency performance | Baseline 18 ms; INC-042 peak **46 ms** on cluster C7, evening busy hour |
| 5 | Cell congestion | PRB utilization **92%** during congestion; illustrative threshold **85%** |
| 6 | Incident overview | INC-042: 3 h 20 min, 14 cells affected |
| 7 | Root-cause investigation | Backhaul saturation plus peak-hour congestion raised latency 18 → 46 ms |
| 8 | Troubleshooting | Validate traffic → check cell counters → inspect transport/backhaul → review alarms |
| 9 | Optimization | Capacity balancing, backhaul 1 → 10 Gbps, KPI alerts at 85% PRB / 30 ms |
| 10 | Lessons learned | Correlated radio/transport dashboards, earlier alerting, capacity review |

Speaker notes contain a `PRESENTER NOTE (not indexed)` marker. Extraction
excludes notes, and a test asserts that the marker never reaches the index.

## Acceptance questions

| Type | Question | Expected |
|---|---|---|
| Factual | What was the peak latency during INC-042? | 46 ms, slide 4 |
| Factual | What PRB utilization was observed during congestion? | 92%, slide 5 |
| Multi-slide synthesis | Which conditions contributed to the latency increase? | Evidence from slides 4, 5 and 7 |
| Troubleshooting | What should an engineer investigate first when latency rises during peak hours? | Steps from slides 7–9 |
| Unsupported | What is the real current outage status of the operator's nationwide network? | Fallback, no citation |

These questions are a demonstration, not a measured accuracy or refusal rate.
Their live behaviour needs a real provider. Do not use their distances to choose
a retrieval threshold; calibration uses separate probes.
