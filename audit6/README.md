# Audit 6 — VR Channel Bench design vs. the Neve VR service manual (Book 1)

Goal: check that the test bench (our design) is configured correctly for the real Neve VR console channel module,
using the scanned Neve VR service manual, Book 1 (first of three volumes being scanned).

## The bench (our design)
A bench/tester for Neve VR console channel modules. The module under test plugs into
J1 (back connector 1, DIN 41612 type C, 96 pins: logic/control lines) and J2 (back connector 2, DIN 41612, 64 pins:
audio + channel supplies) on the Main board. The bench:
- switches the channel's supplies on/off (relays K23/K24/K25) and generates them: +16 V (CH_P16), -16 V (CH_N16),
  VL logic rail -15 V (CH_VL), VR recall rail -15 V (CH_VR), VECAM +12 V, +48 V phantom (PH48 via K12);
  measures voltages/currents;
- routes audio in/out through relays (K1-K22) to XLR J5-J8 and a summing bus (J12 -> Bus board, pages B1-B3);
- drives/reads the channel's logic lines through CD4094/CD4021 shift registers + LM339 level shifters
  (channel logic: 0 V = logic 1, about -15 V (VL) = logic 0 as we understood it);
- reads the channel's recall data (CH_DATA vs CH_REF) with an ADC front end;
- is controlled by a NUCLEO-F767ZI.

## Files
- book1/ — the manual scans (PDF with an OCR text layer of uneven quality). Folders = manual sections:
  1.x channel module boards (1.6 = Channel Module Interconnect Board 11496 — the connectors), 5.x faders,
  6.x meters, 7.x Kingshill power supplies, 8.x, 9.x (survey them). Parts lists ("SINGLE LEVEL BILL") are interleaved.
  OCR is unreliable for diagrams and pin tables: render pages to images (python pymupdf is installed:
  `page.get_pixmap(dpi=150).save(...)`, then view the PNG) and read them visually.
- sch_netlist_pads.asc / sch_netlist_jlceda.json — our schematic netlist (current, exported 2026-11-15). Net names
  on J1.x / J2.x pins tell what the bench puts on each channel connector pin.
- components.csv — our BOM with pin names (2026-11-14; values may be slightly stale).
- page_notes.txt — the designer's notes from each schematic page (2026-11-14; some notes are stale, e.g. J1/J2 are
  on the TOP side now; U45/U46 run from P12 / N17A, not ±19 V).
- Pages B1-B3 in the netlist are the separate Bus board (summing bus mux), J12/J13 link it to the Main board.
