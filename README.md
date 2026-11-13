# VR Channel Bench — main PCB (v2 layout)

- `project/ProPrj_VR Channel Bench_2026-11-13.epro2` — EasyEDA Pro project snapshot (File → Open Project; save-history stripped).
- `pcb/PLAN_v2.md` — floorplan decisions, status log and tooling lessons.
- `pcb/` — placement (`plv2.py`, `plv2.json`), routing data (`v2.dsn`, FreeRouting runs `v2_fr*.dsn/.ses`, final result `final9.json`), helper scripts in `pcb/mz/`.
- `exports/` — dumps from EasyEDA (pre-v2 copper backup, DSN, DRC reports, design rules).
- `tools/easyeda-pro/` — reusable EasyEDA Pro workflow notes and scripts (FreeRouting prep, A* router `route2.py`, clearance/connectivity checks, track insertion).

State (2026-11-13): Nucleo powered via VIN from U50 TSR 1-2490 (24→9 V); v2 placement; fully routed; EasyEDA DRC = 0.
