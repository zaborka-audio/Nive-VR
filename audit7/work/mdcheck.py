import io, sys
# Checks that every Markdown table row has the same number of unescaped pipes as its header row.
path = sys.argv[1]
lines = io.open(path, encoding='utf-8').read().split('\n')
hdr = None; bad = 0; incode = False
for i, l in enumerate(lines, 1):
    if l.startswith('```'):
        incode = not incode; continue
    if incode: continue
    if l.startswith('|'):
        n = 0; prev = ''
        for ch in l:
            if ch == '|' and prev != chr(92): n += 1
            prev = ch
        if hdr is None: hdr = n
        elif n != hdr:
            print('line', i, 'pipes', n, 'expected', hdr, ':', l[:90]); bad += 1
    else:
        hdr = None
print('bad rows', bad, '| lines', len(lines), '| chars', sum(len(x) for x in lines))
