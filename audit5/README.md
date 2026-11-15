# Audit 5 — board copper vs schematic (VR Channel Bench main board)

All files exported 2026-11-15 ~08:50 from EasyEDA Pro 3.2 (the live project).

- sch_netlist_jlceda.json — netlist exported FROM THE SCHEMATIC (sch_ManufactureData.getNetlistFile, JLCEDA JSON format, 16 pages).
- sch_netlist_pads.asc — same schematic netlist in PADS ASCII (*PART* / *NET* sections). Use either; they should agree.
- pcb_v30.dsn — Specctra DSN exported from the PCB: footprints (images/pins/padstacks), placement, the PCB's own net list (network), and all tracks and vias (wiring).
- pcb_pours.json — copper pours on Inner1 (there are no other pours): 'pours' = outlines; 'poured' = actual filled copper after clearances/thermals (PourFills[].path.complexPolygon, EasyEDA path syntax: x,y pairs, 'L' = line-to, 'ARC' angle x y = arc to x,y).
- components.csv, page_notes.txt — BOM/footprints and designer notes (from 2026-11-14, values may differ slightly; not needed for connectivity).

Coordinate facts:
- Units mil. DSN y = EasyEDA y + 9850 (EasyEDA y is negative downward, board 13850 x 9850 mil). pcb_pours.json is in EasyEDA coordinates.
- 4 layers: TopLayer, BottomLayer, Inner1 (GND pour + three GNDA pours), Inner2 (tracks only). All parts through-hole.
- Vias appear in the DSN wiring as (via ...) AND are also exported as pins of a fake component (padstack pf07a228c575f71a, component reference like u1). Those fake pins are vias, not parts.
- GND and GNDA are intentionally separate nets joined only through R26 (net tie).
- Pours connect to pads/vias of their own net by thermal spokes; the 'poured' fills show what is really connected.
