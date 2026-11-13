---
name: easyeda-pro
description: Working on EasyEDA Pro schematics and PCBs on this Windows PC through its script API and computer use — dumping boards, editing schematics, importing changes, placing parts, autorouting (FreeRouting + own A* router), inserting tracks, pours, DRC. Use for ANY EasyEDA Pro task (VR Channel Bench, ZABORKA, Studer A80, synth boards, new projects).
---

# EasyEDA Pro: proven workflow (learned on VR Channel Bench, 2026-11-13)

Projects live in `C:\Users\theli\Documents\EasyEDA-Pro\projects\*.eprj2` (EasyEDA Pro 3.2 desktop app, "Half Offline").
Per-project work folders (scripts, dumps, plans) go next to them, e.g. `projects\VR Channel Bench\`.
Helper scripts: `~/.claude/skills/easyeda-pro/scripts/` (Python 3.12 via `py`; needs numpy scipy pillow matplotlib shapely).

## 1. Driving the app (computer use)
- `request_access(["EasyEDA Pro"])` with clipboard read+write. Coordinates below are for the 1456x819 screenshot frame on the DELL monitor.
- `open_application("EasyEDA Pro")` often brings up an EMPTY second window (Start Page, "No Data") — sometimes seconds later, mid-batch. Minimize it with its minimize button (≈1356,11) and check the screenshot shows the project window before typing. If "desktop shell is frontmost", call open_application again, then minimize the empty window.
- Never type/paste unless the Run Script editor surely has focus: a click that lands on the canvas + Ctrl+A/Ctrl+V selects everything and starts a paste (right panel shows "Paste"). Escape twice cancels it. The Run Script dialog can be moved by the user — take a screenshot before clicking into it.

## 2. Running API scripts
- Advanced menu (≈657,12) → Run Script (≈672,52). Click editor (≈730,400), Ctrl+A, Ctrl+V, then **F9** (the Run button click is unreliable).
- Put script text in the clipboard: small → `write_clipboard`; large (80 KB+) → PowerShell `Get-Content -Raw file.js | Set-Clipboard` (doesn't cost tokens).
- Getting results back: clipboard/`navigator.clipboard`/`document` do NOT work in the script sandbox. Always end with
  `const f=new File([JSON.stringify(out)],'name.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'name.json');`
  → a Save dialog opens in Downloads → click Save (≈598,383). If the name exists, a "Confirm Save As / replace?" box appears → Yes (≈761,401). Then read `~/Downloads/name.json` (use `PYTHONUTF8=1` — files contain Chinese text). Check LastWriteTime to be sure it's fresh.
- After closing Run Script a "script not saved" warning appears → Don't Save (≈777,446).
- `eda.sys_Message.showToastMessage(msg)` for quick feedback.
- Long scripts: one big async IIFE with try/catch per item and an error list in the output file.

## 3. Useful API (verified)
- Dump PCB: `eda.pcb_PrimitiveComponent.getAll()`, per comp `getState_Designator/X/Y/Rotation/Layer`, `eda.pcb_Primitive.getPrimitivesBBox([id])`, `eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)` (pins: getState_PadNumber/X/Y/Net). Generic state dumper: iterate `getState_*` methods. Other getAll: PrimitiveLine, Via, Pour, Polyline, Pad (free pads = mounting holes), Fill, String.
- Modify: `pcb_PrimitiveComponent.modify(id,{x,y,rotation})`, `pcb_PrimitivePad.modify(id,{x,y})`; delete in chunks of 500: `pcb_PrimitiveLine.delete(ids)`.
- Create: `pcb_PrimitiveLine.create(net,layer,x1,y1,x2,y2,width)`, `pcb_PrimitiveVia.create(net,x,y,15.7,31.5)`, `pcb_PrimitivePour.create(net,layer,eda.pcb_MathPolygon.createComplexPolygon([x,y,'L',x,y,...]),'solid',false,name,priority,0.2,false)`, `pcb_PrimitivePolyline.create('',layer,eda.pcb_MathPolygon.createPolygon([...]),width,false)`.
- Layers: 1 Top, 2 Bottom, 15 Inner1, 16 Inner2, 3 Top silk, 11 outline, 13 document. Units mil, y negative downward, origin top-left.
- DSN export: `await eda.pcb_ManufactureData.getDsnFile()` → `.text()` → save. DSN y = EasyEDA y + board height.
- DRC: `await eda.pcb_Drc.check(false,false,true)` returns a nested list (empty list = 0 errors). Walk nodes with `errorType`. Rules: `eda.pcb_Drc.getNetRules()` (per-net "Track" rule name, e.g. power/powerhi) and `getCurrentRuleConfiguration().config.Physics.Track[rule].form.data['1'].minValue` (mm).
- Schematic: `eda.dmt_Schematic.getAllSchematicPagesInfo()`, `eda.dmt_EditorControl.openDocument(pageUuid)` (+wait ~4 s), `eda.lib_Device.search('MPN')` → pick by `supplierId` (LCSC C-number), `eda.sch_PrimitiveComponent.create(dev,x,y,undefined,rot,false,true,true)`, `.modify(id,{designator})`, `getAllPinsByPrimitiveId` (pin rotation = outward direction), `eda.sch_PrimitiveWire.create([x1,y1,x2,y2],netName)` (a wire with a net name = net label), `eda.sch_PrimitiveComponent.createNetFlag('Power'|'Ground',net,x,y,rot,false)`. Schematic units 0.01 inch, y up, keep everything on a 5-unit grid. Wires that touch/cross get merged — never let a label stub touch foreign wires/pins. Ctrl+S saves.
- Schematic → PCB: Design → Import Changes from Schematic; review the change list, Apply Changes.

## 4. GUI steps that scripts can't do
- After inserting tracks/vias by script: Ctrl+S, close the PCB tab (right-click tab → Close Tab), reopen from the project tree (Project Design panel, double-click PCB) — otherwise script vias count as unconnected.
- Rebuild pours: Tools → Copper Manager → Rebuild All → Confirm (Shift+B is unreliable). Priority 1 is poured first.
- Route → Remove Loop must be OFF (no checkmark) before inserting tracks by script.

## 5. Routing recipe
1. Export DSN. Prepare a FreeRouting copy (Python):
   - inner plane layers → `(type power)` and add `(plane NET (polygon Inner1 0 x y ...))` AFTER the last `(layer …)` block (before `(placement`), else NullPointerException.
   - EasyEDA's per-net classes use quoted names (`'VIN24'`) that FreeRouting ignores → delete them and write `(class w24 NET1 NET2 (circuit (use_via via0)) (rule (width 24) (clearance 10)))`. Take widths from the project rules (`getNetRules`), round UP (0.6 mm → 24 mil, 0.8 mm → 32 mil); clearance 10 mil when the rule is 0.25 mm.
   - drop stray wiring with unknown layer names.
2. Run FreeRouting 2.5 (installed, has its own Java):
   `"/c/Users/theli/AppData/Local/freerouting/freerouting.exe" --gui.enabled=false -de <win path>.dsn -do <win path>.ses --router.autorouter.max_passes=60 --router.automatic_neckdown=false`
   Launch detached `( ... &)`, then wait in background with `until grep -q "finished with state" log; do sleep 20; done`. ~20–50 min, plateaus at 20–60 unrouted; 0 violations.
   - Without `automatic_neckdown=false` it narrows tracks to 6–9 mil at pins → DRC width errors.
   - Big power nets with many pins (logic VL, relay VIN24) fail as tracks; a conduction area `(wire (polygon Inner2 0 ...) (net X) (type fix))` helps FreeRouting, BUT it is NOT an obstacle for other nets — they still route through it, so the EasyEDA pour later breaks into islands. Prefer real tracks for such nets in the end.
3. `ses2json.py in.ses out.json` (net names may be quoted in SES).
4. Leftovers: `route2.py board.dsn order.txt out.json prev.json` (windowed A*, 3 layers Top/Bottom/Inner2, grid MZG=5). order line: `NET [width] [x1,y1;x2,y2]` — the 3rd field routes just that pin pair (stitches). Env: MZHW=3 (heuristic weight, fast), MZM=3..5 (extra clearance; 1 gives DRC misses), MZPK=0, MZN=8e6, POURS='{"GND":[[poly]],...}' (pins inside own plane count as connected; outside ones get routed to a via in the plane), AREAS='[["VL",[poly]]]' (own-net Inner2 areas; painted only on empty cells).
   - Pitfall: route2 replays prev paths snapped to the 5-mil grid. NEVER use its output as the final file — take the exact original paths + only the new ones: `merge2.py base.json prev.json:new.json ... out.json` (also snaps new path ends onto pad centres). Ends that land on another track/via need snapping to that point/via centre too.
   - Pitfall: running only my own router from scratch walls in connector pin rows (hugging tracks on all layers) → use FreeRouting first.
5. Verify before inserting: `unr3.py board.dsn res.json` (connectivity; GND/GNDA plane polygons inside are project-specific — edit GA) and `CL=9.84 chk2.py board.dsn res.json` (shapely clearance). Both must be 0.
6. `tojs2.py res.json prefix 1500` → prefix_N.js (lines+vias, 1500 items per script, writes vrb_insN.json). Insert, then section 4, then DRC script.
7. Typical DRC leftovers and fixes: pads isolated from a pour (thermal blocked / island) → stitch track to a connected pad of the same net; separate pour islands of one net (e.g. GNDA under XLRs) are NOT connected to each other — add tracks; width-rule errors → fix classes and reroute.

## 6. Working style the user wants
- Speak Russian. Keep the user informed during long waits; never sit silent.
- Make a full JSON backup (all lines/vias/pours/pads) before wiping copper.
- Show a picture (matplotlib render, `view2.py`) before big changes; report DRC numbers honestly.
- Don't re-litigate an approved floorplan; ask only real decisions (e.g. which regulator).
