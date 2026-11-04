from pathlib import Path
import hashlib, json
k=Path('docs/research/kernel-0')
v=k/'timing-reduction/evidence/round2-rtl-boundaries.vectors'
raw=json.loads((k/'timing-reduction/evidence/round2-rtl-boundaries.raw.json').read_text())
assert raw['literal_vectors']==v.read_text()
for name, expected in raw['source_hashes'].items():
    assert hashlib.sha256((k/name).read_bytes()).hexdigest()==expected, name
ops=['establish','grant','restrict','replace','delegate','set','flip','accept','resume','pair','mixed']
for i,line in enumerate(v.read_text().splitlines()):
    reset,valid,p,s,res,com=(int(a,16) for a in line.split())
    op=p&15; actor=(p>>4)&7; target=(p>>7)&3; value=(p>>9)&7; other=(p>>12)&3; auth=(p>>14)&1
    rights=[(s>>(8+3*j))&7 for j in range(4)]
    print(f'{i:02} rst={reset} valid={valid} p={p:04x} op={ops[op] if op<len(ops) else op} actor={actor} target={target} value={value} other={other} auth={auth} -> {s:06x} est={s&1} xy={(s>>1)&1},{(s>>2)&1} content={(s>>3)&1} issued={(s>>4)&15:x} rights={rights} parent={(s>>20)&3} result={res}/{com}')
print('source hashes and literal raw vector copy match pin')
for name in ('reference','reset_loses_precedence','restriction_erases_issued'):
    r=raw['results'][name]
    print(name,'compile exit',r['compile']['exit'],'simulation exit',r['simulate']['exit'],'stdout:',repr(r['simulate']['stdout']))
