# VR Channel Bench — main board: facts for the audit

Purpose (from the project): a bench/tester for console channel modules ("VR channel"). The module under test plugs into
J1 (96-pin DIN 41612, logic/control lines) and J2 (64-pin Harting, audio + channel supplies). The bench switches the
channel's supplies on/off (relays K23/K24/K25), measures their voltages/currents, routes audio in/out through relays
(K1–K22) to XLR J5–J8 and a summing bus (J12), drives/reads the channel's logic lines through CD4094/CD4021 + LM339
level shifters, and is controlled by a NUCLEO-F767ZI (plugs into CN7–CN10, Zio sockets; mirrored footprints because
the Nucleo plugs in from above). 24 V DC input (J11) → switchers/linear regulators → ±16 V, ±17 V, VL, VR, +12 V,
+48 V phantom (HV50), etc. Nucleo is powered from VIN via U50 TSR 1-2490 (24 V → 9 V).

Files in this folder:
- netlist.txt — every net with DES.pin(pinname). Built from the PCB (EasyEDA Pro), identical to the schematic.
- components.csv — page, designator, value, MPN, manufacturer, LCSC, footprint, pin names.
- page_notes.txt — the designer's text notes on each schematic page (intent, formulas, thresholds).
- pcb_src.json / sch_src.json — raw dumps: PCB component positions (mil, y negative downward, board 13850×9850 mil = 352×250 mm), rotation, footprint, pad nets; schematic components with attributes and page texts.

PCB facts: 4 layers. Top/Bottom signals; Inner1 = GND plane with GNDA islands (relay/summing area, XLR area), joined
GND–GNDA through R26 (net tie) only; Inner2 = signals + pours VL (logic area) and VIN24 (relay area). All parts THT.
Design rules: clearance 0.25 mm; track ≥8 mil; class "power" ≥0.6 mm (±16 V, VL, VR, P12, HV50, PH48, +5V, CH_* rails…),
"powerhi" ≥0.8 mm (P17, N17A, N17L, VIN_F, VIN_RAW, SW1–SW4). EasyEDA DRC currently reports 0 errors.

Owner's operating assumptions: 24 V supply rated ≥ 4 A. Firmware is written by the owner (not part of this review).
