# Neve VR channel: how the EQ, dynamics, insert and filters are wired, and what the routing buttons do

**Sources (book1):**
- 1.4 p1-2: 11491 description.
- 1.4 p9-10: EX11491 sheet 1, with S2 DYN at p10 lower right (about x 0.6-0.85, y 0.70-0.85).
- 1.4 p11-12: EX11491 sheet 2 (insert circuits, CONN 2/3/18).
- 1.4 p13: 11492 description.
- 1.4 p20-21: EX11492.
- 1.5 p1-3: 11498/11499 description.
- 1.5 p11-12: EX11498 sheet 1, with S6/S7/S8 at p12 x 0.2-0.86, y 0.07-0.47.
- 1.6 p1: 11496 description.
- 1.6 p6-7: EX11496 sheet 1 (interconnect).
- 1.2 p2, p9, p17-19: 11493/11494/11495 descriptions.
- `controls_11493_11494.md`.

**Crops used:** `audit6/work/img/book1_1.4_p10_*`, `book1_1.4_p11_*`, `book1_1.4_p12_*`, `book1_1.4_p20_*`, `book1_1.4_p21_*`, `book1_1.5_p12_450_*`, `book1_1.6_p7_*`, and `s91_preq.png`.

**Confidence tags:** [H] read directly; [M] read but with one inferred link, or inferred from names plus the description; [L] estimate.

**How to read the switch symbols** (from the LED-shunt sections, where the LED is lit when the button is pressed):
- The filled dot is the at-rest (N/C) throw.
- The open circle is the pressed (N/O) throw.
- The line on the blade side, labelled with the section letter, is the common. [H]

---

## 0. Two different sets of "DYN / INS / EQ" buttons
| Panel location | Button | Board / switch | Function |
|---|---|---|---|
| EQ section | **INS** (green LED) | 11492 S1 → latch IC3 → FETs TR1/TR2 on 11491 | Insert loop in/out [H, p13 + p2] |
| EQ section | **PREQ** (yellow LED1) | 11491 S1 | Moves the insert loop between the pre slot and the post slot [H for function (p2); contacts M, see 2] |
| EQ section | **DYN** (red LED2) | 11491 S2 | **Puts the EQ into the dynamics side chain** (see 1) [H] |
| EQ section | **EQ** (green LED4) | 11492 S4 → IC3 → FETs TR1/TR2 on 11492 | EQ in/out, with a FET cross-fade [H] |
| Monitor section (`m_dyn`, `m_ins`, `m_eq`, green LEDs 7/6/8) | DYN / INS / EQ | 11498 S6 / S7 / S8 | Swap the dynamics, the pre-insert slot and the EQ between the **channel path and the monitor path** (p1: "switched between the primary (channel) path and the secondary (monitor) paths") [H] |

## 1. DYN on 11491 (S2): the EQ goes into the dynamics side chain [H for contacts; M-H overall]

**Where it is:** EX11491 sheet 1, p10, grid H-J/11-12.
- S2 has sections a (LED2 red shunt), d, c, f and e.
- S2b (sheet 2, CONN 18) is the recall resistor R134 15K.

**Nets:**
- ST1/8 = 11492 input (EQ section in). [H, 11492 p20 G1]
- ST1/7 = 11492 output, after the EQ in/out FETs. [H, p21 top + p20]
- CONN2/6 = **EQ INPUT** and CONN3/9 = **EQ OUTPUT**. These are the EQ slot as seen by the routing on 11498. [H, sheet 2 p12 legends]
- CONN1/6 = **SEND FROM DYN S/C** and CONN1/7 = **RET. FROM DYN S/C** (names from the EX11496 p7 connector legend). CONN1/8, 9, 10 = "DYN SW W / N/C / N/O" (S2e, a spare changeover brought out to the interconnect; where it goes was not traced).

| Section | Common | At rest (DYN off) | Pressed (DYN on) |
|---|---|---|---|
| c | CONN2/6 EQ INPUT | → ST1/8 (EQ in) | → CONN3/9 EQ OUTPUT, so the **EQ is bypassed in the main path** |
| d | ST1/7 (EQ out) | → CONN3/9 EQ OUTPUT | → CONN1/7 RET (to side chain) |
| f | CONN1/6 SEND | → CONN1/7 RET (straight link) | → ST1/8 (EQ in) |
| e | CONN1/8 | CONN1/9 | CONN1/10 (destination not traced) |

**Interconnect (EX11496 p7, traced with a line-follower and checked against crops):**
- CONN1/7 RET runs to **11494 CON3/6 SIDECHAIN I/P** [M-H].
- CONN1/6 SEND runs to **11494 CON3/3 DYN I/P Hi**, the VCA input [M]. The trace drifts about 0.007 page-height over the run, and the RET trace drifts the same amount (scan skew), so this is consistent.

**Result:**
- **DYN off:** the side chain takes the VCA input signal (SEND linked straight to RET). The EQ sits in the main path.
- **DYN on:** the EQ is removed from the main path (EQ INPUT is wired directly to EQ OUTPUT). The VCA input signal goes through the EQ (11492 + 11491 filters) and then into both the L/C side chain and the gate side chain.
  - The gate side chain gets it through 11493 KEY S3c at rest, which takes the L/C I/P (see `controls_11493_11494.md` 1B).
  - The EQ is then a **side-chain EQ only** (de-essing / frequency-conscious compression).
  - The EQ in/out button still applies. With EQ out, the side chain passes flat through the 11492 bypass FETs.

**Drafting anomaly:** a junction dot is drawn where the S2f common drops past the ST1/8 line (p10 at about x 0.705, y 0.825; 800-dpi crop `book1_1.4_p10_800_*`).
- Taken literally, it ties SEND to ST1/8 permanently. That makes section f pointless, and at rest it would short the VCA input to the EQ input.
- Without the dot, every section has a purpose and the behaviour matches the connector names. So I treat it as a crossing [M-H]. **Check on a real 11491 if possible** (S2f common should not be continuous with ST1/8).

## 2. Channel block order and what each button changes

### 2A. The fixed order of the slots (11498 S6/S7/S8 at rest, i.e. everything in the channel path) [M-H]
EX11498 p12 contacts were read at 450 dpi:

FILTER O/P Hi (1/49) → S7d → **PRE INS I/P (2/14)** … **PRE INS O/P (2/26)** → S7b → S6c → **DYN I/P Hi (2/15)** … **DYN O/P Hi (1/48)** → S6d → S8c → **EQ I/P (2/6)** … **EQ O/P (2/9)** → S8d → … → S7f → **POST INS I/P (2/13)** … **POST INS O/P (2/8)** → S7g → **CH POST EQ O/P (2/28)** → (fader / routing).

So **in the default state the dynamics come before the EQ**. The S8d-common → S7f link was not followed pixel by pixel [M].

**What the 11498 buttons do when pressed:**
- **S7 (INS to monitor)**
  - The channel bypasses the pre slot (S7b: FILTER O/P straight on).
  - The pre slot is fed from the monitor chain instead (S7d N/O / S7c).
  - S7e/f/g do the same for the post slot. MONITOR POST EQ O/P (2/7) is the monitor-side output.
- **S6 (DYN to monitor)**
  - The channel bypasses the dynamics (S6d N/O).
  - DYN I/P takes the monitor signal (S6c N/O), and the monitor continues from DYN O/P (S6f N/O).
- **S8 (EQ to monitor)**
  - The channel goes through slot "E2" instead (S8e/d).
  - The EQ goes into the monitor path (S8b/c).
  - E2 I/P (CON1/16) and E2 O/P (CON1/14) are linked on 11496 by R8 (0R, the value is hard to read), so **E2 is just a wire**. It is a placeholder for whichever path does not have the EQ [M].

### 2B. Where the 11491/11492 buttons act
- **EQ slot** (EQ INPUT → EQ OUTPUT on 11491):
  - 11491 S2c routes EQ INPUT → 11492 → 11492 EQ in/out FETs → 11491 S2d → EQ OUTPUT.
  - 11492 EQ in/out: TR1 (bypass) / TR2 (return) with a cross-fade (R45-R48, D7/D8, C4/C13). [H]
- **Insert loop:**
  - There is one insert send/return, on 11491 sheet 2.
  - 11491 CONN2 has I/P TO PRE INS (5), O/P FROM PRE INS (3), I/P TO POST INS (4) and O/P FROM POST INS (1). They match 11498 PRE/POST INS I/P/O/P by name [M; the 11496 wiring was not traced].
  - S1 PREQ connects the insert block (IC1/IC17 input → TR1/TR2 → IC1b output "INS O/P") into the pre slot or the post slot, and links the other slot straight through (p2: "S1 (PREQ) dictates the position of the insertion … before or after equalization").
  - **S1's contacts are in the strip lost between p11 and p12** (`s91_preq.png`; only the wire stubs are visible). The exact contacts are therefore [M] (from the description and the pin names).
  - The yellow PREQ LED lit = insert in the **pre** slot. That slot sits **before the dynamics as well as before the EQ** (2A).
- **INS (11492 S1):** sets FETs TR1/TR2 on 11491 (ST1/24, ST1/28).
  - Off: TR2 on, giving the bypass IC17 → R10 → TR2 → IC1b.
  - On: TR1 on, giving the return.
  - The send amp is always driven (p2). [H]

### 2C. Signal flow per button combination (11498 S6/S7/S8 all at rest)
`pre` = pre slot, `post` = post slot; `[INS]` = insert loop (send → jackfield → return); `EQ` = EQ if the EQ button is in, else a flat wire.

| INS | PREQ | DYN (11491) | Main path | Dynamics side chain (L/C, and gate when KEY is off) |
|---|---|---|---|---|
| off | x | off | FILT → DYN → EQ → out | VCA input (post filter) |
| on | off | off | FILT → DYN → EQ → [INS] → out | VCA input |
| on | on | off | FILT → [INS] → DYN → EQ → out | VCA input (= post-insert) |
| off | x | on | FILT → DYN → out (no EQ) | VCA input → EQ |
| on | off | on | FILT → DYN → [INS] → out | VCA input → EQ |
| on | on | on | FILT → [INS] → DYN → out | post-insert VCA input → EQ |

Notes:
- With INS off, the send is still driven in the selected slot. The send is a "listen" feed only, and PREQ just moves that tap. [H, p2]
- "DYN" in the main path is the VCA. It is unity (passes the signal) unless L/C or GATE is in (`controls_11493_11494.md` 2B).
- If the 11498 monitor buttons are pressed, the named block leaves the channel table above and goes into the monitor path. 11491 S2 then acts on whichever path holds the EQ slot.

## 3. Side-chain source
- **L/C side chain** (11494 CON3/6 → FSP6/1):
  - DYN off: the **same signal as the VCA input** (FSP6/6). [M-H]
  - DYN on: that signal **after the EQ**. [M-H]
  - There is no other source, and **no filter-only (HPF/LPF) side-chain option** was found. The HPF/LPF act on the whole channel before the dynamics, so they are in both the VCA path and the side chain.
- **Gate side chain** (FSP4/1):
  - 11493 KEY at rest = L/C I/P (the same as above, so it is also EQ'd when DYN is on). [H]
  - KEY pressed = the external KEY input, which is never EQ'd.
- **Side-chain level change when DYN is on:**
  - The 11492 EQ-in path gain relative to bypass is 1.333 × the 11491 filter-chain flat gain (see 5). It is presumably designed as unity overall, but this was not verified.
  - So any flat-gain error shifts the effective threshold.

## 4. Filters
- **HPF:** 11494 IC7 + RV2, selected by the RV2 pull switch. [H, 1.2 p9]
- **LPF:** 11494 IC8 + 11493 RV2b/c (FSP2 pins 7-9), selected by the 11493 RV2 pull switch. [H, 1.2 p2/p9]
- **Position:**
  - 11494 CON2 "FILTER I/P" (from the input stage / group) → filters → CON3/1 "FILTER O/P Hi".
  - That goes to 11498 1/49 FILTER O/P Hi, which is the head of the slot chain in 2A. [H for the names, M for the 11496 link]
- **No interaction** with the DYN/PREQ/EQ switching. Filters always come before the pre-insert, the dynamics and the EQ.
- The HPF→LPF order inside 11494 was **not traced**.
- 11496 sheet 2 also taps "Channel pre-filter (D)" and "post-EQ output (F)" for the signal LED only [H, 1.6 p1].

## 5. Gains and levels on these paths
- **11492 (EQ in/out)** [H for values]
  - Input: IC1a inverting, R23 10K / R24 10K, gain -1.
  - EQ out (bypass): R25 7K5 → TR1 → IC2 virtual earth, R20 7K5, gain -1. Overall 0 dB, non-inverting.
  - EQ send to 11491 (ST1/32): R25 7K5 / R26 15K divider (0.667), then IC1b non-inverting ×2 (R13 = R14 = 7K5), giving **×1.333 (+2.5 dB)** relative to the input.
  - EQ return (ST1/11): C12 → R28 7K5 → TR2 → IC2 (R20 7K5), gain -1.
  - So EQ-in flat gain = 1.333 × G(11491 chain). The 11491 chain flat gain was not derived (the C68 / R124 / R125 4K7 network at the input) [L]. Assume it was designed for 0 dB overall.
- **11491 insert**
  - Bypass: IC17 (5534, 10K/10K, gain -1) → R10 8K2 → TR2 → IC1b (R14 8K2, gain -1), giving **0 dB**. [H]
  - Return: balanced amp IC3, Hi through RP1 11K922 to (-), Lo through 7K902 / 2K01 to (+), feedback 3K02. **Differential gain 0.253 (-11.9 dB)**, with diode clamps to ±16 V (D3-D6). Then R22 1K1 + R19 3K (4K1) → TR1 → IC1b (8K2), ×2.0. **Return path ≈ -5.9 dB** relative to the return input. [H for values, M for the R22-R19 series reading]
  - Send: IC1a unity buffer (R7 510R feedback, no gain leg fitted) → floating balanced send (IC4/IC2/IC3, RP2/RP3 networks, 33R ∥ 10 µH outputs). The gain was not derived. A floating stage normally gives **+6 dB differential**, which with the -5.9 dB return would make a unity external loop give about 0 dB [L].
- **Dynamics input:** there is no gain stage between 11494 CON3/3 and FSP6/6. The VCA input resistor R56 is on 11495 (value not read). The L/C detector log amp works at 1 V/10 dB over +20 to -60 dBu (1.2 p17). The DYN O/P buffer is IC13 on 11495.
- **Nominal console levels are not stated** in these pages.

## 6. Unreadable or unverified items
| Item | Where | Status |
|---|---|---|
| 11491 S1 PREQ contacts | Gap between p11 right edge and p12 left edge, y ≈ 0.62-0.84 | **Not in scan.** Function taken from the p2 text and pin names [M] |
| Junction dot at S2f common / ST1/8 | p10 at about (0.705, 0.825) | Treated as a crossing; verify on the hardware |
| S2e (CONN1/8-10) "DYN SW" destination | EX11496 p7 → p6 (heavy lines to the right) | Not traced |
| 11491 CONN2/3 ↔ 11498 PRE/POST INS, EQ I/P/O/P ↔ 11498 2/6, 2/9 on 11496 | p6/p7 | Matched by name only [M] |
| S8d common → S7f N/C (channel EQ out → post slot) | EX11498 p12 | Topology implied, not followed pixel by pixel [M] |
| E2 link resistor R8 value | EX11496 p6 at about (0.62, 0.35) | Reads as "0R0"/"3R3" [L] |
| 11491 EQ filter-chain flat gain; insert send gain; 11495 R56 | EX11491 sheet 1 / sheet 2; EX11495 | Not derived |
| HPF/LPF order inside 11494 | EX11494 | Not traced |
