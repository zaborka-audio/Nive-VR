cd /home/claude/pcb
GAP="13250,-7255,13560,-7185"
REST=$(python3 -c "
f='L_A0,L_A2,L_OE,L_STB,L_PS,L_MOSI,CTL_PAD_B,L_A4,CTL_PAD_A,ENB0,ENA2,ENA1,ENA0,MA3,MA2,MA1,MA0,ISEN_VL,VSENSE,ENB2'.split(',')
print(','.join(n for n in open('mz/order20.txt').readline().strip().split(',') if n not in f))")
MZKO="$GAP;13470,-9850,13850,-5800" MZN=8000000 python3 mz/route.py eeA.dsn "$REST" mz/s2C.json > mz/s2C.log 2>&1
python3 mz/tojs.py mz/s2C.json /tmp/c.js; python3 mz/merge.py eeA.dsn mz/s2C.json ee2C.dsn
MZKO="$GAP;13460,-7280,13850,-4500" MZN=15000000 python3 mz/route.py ee2C.dsn ENB0,ENA2,ENA1,ENA0,MA3,MA2,MA1,MA0,ISEN_VL,VSENSE,ENB2 mz/s2B.json > mz/s2B.log 2>&1
python3 mz/tojs.py mz/s2B.json /tmp/b.js
echo DONE
