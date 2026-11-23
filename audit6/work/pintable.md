| Конт. J2 | Сеть стенда | По мануалу (BACK CONNECTOR 2) | Итог |
|---|---|---|---|
| 1a | GNDA | 0V AUDIO | ок |
| 1c | GNDA | 0V AUDIO | ок |
| 2a | MTK_OUT_C | MULTITRACK O/P Lo | ок |
| 2c | MTK_OUT_H | MULTITRACK O/P Hi | ок |
| 3a | - (не подключён) | SPARE | ок |
| 3c | - (не подключён) | MIC I/P 0V | ! F1: MIC I/P 0V не подключён |
| 4a | GNDA | GROUP O/P 0V | ок |
| 4c | GNDA | MT O/P 0V | ок |
| 5a | PH_PIN | PHANTOM PWR | ок |
| 5c | PH_PIN | PHANTOM PWR | ок |
| 6a | - (не подключён) | SPARE | ок |
| 6c | - (не подключён) | SPARE | ок |
| 7a | - (не подключён) | SPARE | ок |
| 7c | - (не подключён) | SPARE | ок |
| 8a | - (не подключён) | SPARE | ок |
| 8c | GNDA | FADER I/P 0V | ок |
| 9a | - (не подключён) | SPARE | ок |
| 9c | - (не подключён) | SPARE | ок |
| 10a | GNDA | LINE IP SCN | ок |
| 10c | GNDA | LINE IP SCN | ок |
| 11a | LINE_IN_C | LINE IP Lo | ок |
| 11c | LINE_IN_H | LINE IP Hi | ок |
| 12a | GNDA | INSERTION RTN SCN - MODULE EARTH | ок |
| 12c | GNDA | INSERTION RTN SCN - MODULE EARTH | ок |
| 13a | INS_RTN_C | INSERTION RTN Lo | ок |
| 13c | INS_RTN_H | INSERTION RTN Hi | ок |
| 14a | GNDA | 0V AUDIO | ок |
| 14c | GNDA | 0V AUDIO | ок |
| 15a | INS_SEND_C | INSERTION SEND Lo | ок |
| 15c | INS_SEND_H | INSERTION SEND Hi | ок |
| 16a | GNDA | 0V AUDIO | ок |
| 16c | GNDA | 0V AUDIO | ок |
| 17a | GND | 0V LOGIC | ок (GND = логический 0 В) |
| 17c | GND | 0V LOGIC | ок (GND = логический 0 В) |
| 18a | CH_N16 | -16 V | ок |
| 18c | CH_N16 | -16 V | ок |
| 19a | CH_VL | -15 V LOGIC | ок |
| 19c | CH_VL | -15 V LOGIC | ок |
| 20a | CH_P16 | +16 V | ок |
| 20c | CH_P16 | +16 V | ок |
| 21a | - (не подключён) | SPARE | ок |
| 21c | GNDA | INSERTION SEND 0V | ок |
| 22a | MON_IN_C | MONITOR I/P Lo | ок |
| 22c | MON_IN_H | MONITOR I/P Hi | ок |
| 23a | CH_VR | -15 V R | ок (см. F7) |
| 23c | CH_VR | -15 V R | ок (см. F7) |
| 24a | TAPE_IN_C | TAPE I/P Lo | ок |
| 24c | TAPE_IN_H | TAPE I/P Hi | ок |
| 25a | GATE_IN_C | GATE I/P Lo | ок |
| 25c | GATE_IN_H | GATE I/P Hi | ок |
| 26a | - (не подключён) | SPARE | ок |
| 26c | - (не подключён) | SPARE | ок |
| 27a | FDIR_C | FADER DIRECT Lo | ок |
| 27c | FDIR_H | FADER DIRECT Hi | ок |
| 28a | - (не подключён) | SPARE | ок |
| 28c | - (не подключён) | SPARE | ок |
| 29a | GNDA | 0V AUDIO | ок |
| 29c | GNDA | 0V AUDIO | ок |
| 30a | GNDA | MIC I/P SCN - MODULE EARTH | ок |
| 30c | GNDA | MIC I/P SCN - MODULE EARTH | ок |
| 31a | MIC_IN_C | MIC I/P Lo | ок |
| 31c | MIC_IN_H | MIC I/P Hi | ок |
| 32a | GNDA | 0V AUDIO | ок |
| 32c | GNDA | 0V AUDIO | ок |

| Конт. J1 | Сеть стенда | По мануалу (BACK CONNECTOR 1) | Что это в канале | Итог |
|---|---|---|---|---|
| 1a | G_MIC_TALLY | MIC TALLY | выход канала (КМОП 4013, 11494 IC1/12) | ок |
| 1b | G_CD_TALLY | C.D. TALLY | вход (шина пульта) | ок |
| 1c | G_EXPAND_CNTL | EXPAND CNTL | АНАЛОГОВЫЙ выход ОУ через 33R (EXPAND METER, 11494 CONN4/10) | ! F4 |
| 2a | G_MIC_COUGH | MIC COUGH | вход | ок |
| 2b | G_GROUP_TALLY | GROUP TALLY | вход | ок |
| 2c | G_LC_CONTROL | LC CONTROL | АНАЛОГОВЫЙ выход ОУ через 33R (COMPRESS METER, 11494 CONN4/9) | ! F4 |
| 3a | METER_C | METER O/P Lo | аудио выход | ок |
| 3b | G_CHOP_TALLY | CH-OP TALLY | вход (100k к VSS) | ок |
| 3c | G_OVERLOAD | OVERLOAD | выход TL034 (питание +/-16 В) через 47k - детектор сигнала | ! F5 |
| 4a | METER_H | METER O/P Hi | аудио выход | ок |
| 4b | G_TIMT | TIMT | логика | ок |
| 4c | G_INS_CONTROL | INS CONTROL | ТРЁХУРОВНЕВЫЙ вход управления | ! F6 |
| 5a | G_BYPASS | BYPASS | к опц. плате метра SBN801-030 | ок |
| 5b | G_INS_EVENT | INS EVENT | выход (транзистор CA3086, fly event) | F9 (открыто) |
| 5c | G_EQ_CONTROL | EQ CONTROL | ТРЁХУРОВНЕВЫЙ вход управления | ! F6 |
| 6a | - (не подключён) | SPARE B | - | ок |
| 6b | G_EQ_EVENT | EQ EVENT | выход (транзистор CA3086) | F9 (открыто) |
| 6c | G_MON_CONTROL | MON. CONTROL | ТРЁХУРОВНЕВЫЙ вход (MNCR) | ! F6 |
| 7a | - (не подключён) | SPARE C | - | ок |
| 7b | G_MONCUT_EVENT | MON CUT EVENT | выход | F9 (открыто) |
| 7c | G_CHAN_CONTROL | CHAN. CONTROL | ТРЁХУРОВНЕВЫЙ вход (CNCR) | ! F6 |
| 8a | - (не подключён) | SPARE D | - | ок |
| 8b | G_CHANCUT_EVENT | CHAN. CUT EVENT | выход | F9 (открыто) |
| 8c | CH_SEL | CHANNEL SELECT | вход, активный НИЗКИЙ (-15 В = выбран), 1k + 220k к -15VL | ок |
| 9a | FE9A | FADER END SW No2 | контакт фейдера | ок |
| 9b | OSC_TB | OSC & T.B. BUS | аудио вход | ок |
| 9c | FE9C | FADER END SW W 2 | контакт фейдера | ок |
| 10a | LIM_IN | LIM. LOOP-IN | линк компрессоров | ок |
| 10b | OSC_TB0V | OSC & T.B. 0V | 0 В | ок |
| 10c | LIM_OUT | LIM. LOOP-OUT | линк компрессоров | ок |
| 11a | G_CUT_B | (срезано на стыке скана; по смыслу CUT B) | вход шины | F12 (не проверено) |
| 11b | G_CUT_A | CUT A | вход шины (через S18/диод) | ок |
| 11c | CH_DATA | ANALOG DATA BUS | выход мультиплексора recall (4067 COM) | ! F3 |
| 12a | G_SHB | SHB | вход, 1M к -15VL | ок |
| 12b | G_FSB | FSB | вход, 1k + 1M к -15VL | ок |
| 12c | G_MBCB | MBCB | вход, то же | ок |
| 13a | G_TIMB | TIMB | вход, то же | ок |
| 13b | G_TIB | TIB | вход, то же | ок |
| 13c | G_SFBB | SFBB | вход, то же | ок |
| 14a | G_RECB | RECB | вход, то же | ок |
| 14b | G_MDB | MDB | вход, то же | ок |
| 14c | G_ODB | ODB | вход, то же | ок |
| 15a | G_CPEB | CPEB | вход, то же | ок |
| 15b | G_MAB | MAB | выход на шину через диод (monitor AFL DC bus) | ок |
| 15c | G_CAB | CAB | выход на шину через диод (chan AFL DC bus) | ок |
| 16a | G_MSCB | MSCB | шина solo cut | ок |
| 16b | G_SRB | SRB | вход (solo reset) | ок |
| 16c | G_CSCB | CSCB | шина solo cut | ок |
| 17a | G_MASTER_MIC | MASTER MIC | вход | ок |
| 17b | CH_A0 | ADDRESS 0 | вход, 1k + 220k к -15VL | ок |
| 17c | CH_A1 | ADDRESS 1 | то же | ок |
| 18a | CH_A2 | ADDRESS 2 | то же | ок |
| 18b | CH_A3 | ADDRESS 3 | то же | ок |
| 18c | CH_A4 | ADDRESS 4 | то же | ок |
| 19a | CH_A5 | ADDRESS 5 | то же | ок |
| 19b | G_ADDR6 | ADDRESS 6 | в модуле только тест-пад (T19) | ок |
| 19c | G_ADDR7 | ADDRESS 7 | в модуле только тест-пад (T20) | ок |
| 20a | G_SLB | SOLO LAMP BUS (SLB) | вход (1k + 220k, 4013) | ок |
| 20b | - (не подключён) | MTR-LINE (инв.) | к опц. плате метра | ок |
| 20c | G_OVL_MASTER | OVERLOAD MASTER BUS | АНАЛОГОВЫЙ вход порога (отриц. напряжение, R204 100k) | ! F8 |
| 21a | FENO2 | FADER END SW N.O. 2 | фейдер | ок |
| 21b | VECAM | VECAM +12V | в модуле только тест-пад (T23) | F11 (не нужен) |
| 21c | FEW2 | FADER END SW W 2 | фейдер | ок |
| 22a | FRET2 | FADER RET 2 | аудио вход | ок |
| 22b | PFL | PFL | аудио выход на шину | ок |
| 22c | FRET1 | FADER RET 1 | аудио вход | ок |
| 23a | - (не подключён) | FADER -16V | ВЫХОД питания фейдера (-16 В через R7 10R) | ок |
| 23b | FSEND1_H | FADER SEND Hi 1 | аудио выход | ок |
| 23c | - (не подключён) | FADER +16V | ВЫХОД питания фейдера (+16 В через R6 10R) | ок |
| 24a | FSEND2_H | FADER SEND Hi 2 | тест-пад (T24) | ок |
| 24b | FENO1 | FADER END SW N.O. 1 | фейдер | ок |
| 24c | FEW1 | FADER END SW W 1 | фейдер | ок |
| 25a | F0V | FADER SEND 0V 2 | тест-пад (T25) | ок |
| 25b | F0V | FADER SEND 0V 1 | 0 В фейдера | ок |
| 25c | F0V | FADER RET. 0V 1&2 | 0 В фейдера | ок |
| 26a | CH_REF | 0V REF. BUS | опорный 0 В микс-шин (BUS 0V REF усилителя 11403) | ! F2 |
| 26b | CH_REF | 0V REF. BUS | то же | ! F2 |
| 26c | CH_REF | 0V REF. BUS | то же | ! F2 |
| 27a | AUX7 | AUX 7 | выход на шину через 4k7 | ок |
| 27b | - (не подключён) | SPARE BUS | - | ок |
| 27c | AUX8 | AUX 8 | через 4k7 | ок |
| 28a | AUX5 | AUX 5 | через 4k7 | ок |
| 28b | - (не подключён) | SPARE BUS | - | ок |
| 28c | AUX6 | AUX 6 | через 4k7 | ок |
| 29a | AUX3 | AUX 3 | через 4k7 | ок |
| 29b | - (не подключён) | SPARE BUS | - | ок |
| 29c | AUX4 | AUX 4 | через 4k7 | ок |
| 30a | AUX1 | AUX 1 | через 4k7 | ок |
| 30b | - (не подключён) | SPARE BUS | - | ок |
| 30c | AUX2 | AUX 2 | через 4k7 | ок |
| 31a | AFL_L | AFL LEFT | через 4k7 | ок |
| 31b | - (не подключён) | SPARE BUS | - | ок |
| 31c | AFL_R | AFL RIGHT | через 4k7 | ок |
| 32a | - (не подключён) | SPARE BUS | - | ок |
| 32b | - (не подключён) | SPARE BUS | - | ок |
| 32c | - (не подключён) | SPARE BUS | - | ок |