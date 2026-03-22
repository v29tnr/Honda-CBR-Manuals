import fitz, re, json

pdf = fitz.open(r'c:\Users\Tyler.BOOK-4I1L5U5KL5\Manual Website\F3manual.pdf')
pat = re.compile(r'^\d+[-\u2013\u2011\u2012]\d+$')
norm = lambda s: s.replace('\u2013','-').replace('\u2011','-').replace('\u2012','-')

def lv(s): p=s.split('-'); return int(p[0])*100000+int(p[1])
def lp(s): p=s.split('-'); return {'ch':int(p[0]),'pg':int(p[1])}

n = pdf.page_count
perPage = [None] * (n + 1)  # 1-indexed

for i in range(n):
    page = pdf[i]
    rect = page.rect
    clip = fitz.Rect(0, rect.height * 0.92, rect.width, rect.height)
    words = page.get_text('words', clip=clip)
    words_sorted = sorted(words, key=lambda w: w[0])
    texts = [norm(w[4].strip()) for w in words_sorted if w[4].strip()]
    found = None
    for size in range(1, min(7, len(texts)+1)):
        for j in range(len(texts) - size + 1):
            cat = ''.join(texts[j:j+size])
            if pat.match(cat):
                found = cat
                break
        if found:
            break
    perPage[i+1] = found

pdf.close()

# Greedy monotone forward pass
assigned = [None] * (n + 1)
lastVal = -1; lastStr = None
for i in range(1, n+1):
    s = perPage[i]
    if not s: continue
    v = lv(s)
    if v <= lastVal: continue
    if lastStr and lp(s)['ch'] - lp(lastStr)['ch'] > 2: continue
    assigned[i] = s
    lastVal = v; lastStr = s

# Interpolation
for i in range(1, n+1):
    if assigned[i]: continue
    pi = ni = -1
    for j in range(i-1, 0, -1):
        if assigned[j]: pi=j; break
    for j in range(i+1, n+1):
        if assigned[j]: ni=j; break
    pL = lp(assigned[pi]) if pi>0 else None
    nL = lp(assigned[ni]) if ni>0 else None
    guess = None
    if pL and nL and pL['ch']==nL['ch']:
        gpg = round(pL['pg'] + (i-pi)*(nL['pg']-pL['pg'])/(ni-pi))
        guess = str(pL['ch'])+'-'+str(gpg)
    elif nL:
        guess = str(nL['ch'])+'-'+str(max(1, nL['pg']-(ni-i)))
    elif pL:
        guess = str(pL['ch'])+'-'+str(pL['pg']+(i-pi))
    if guess: assigned[i] = guess

# Write output — array indexed from 1, index 0 is null
out = [None] + [assigned[i] for i in range(1, n+1)]
with open(r'c:\Users\Tyler.BOOK-4I1L5U5KL5\Manual Website\page-labels.json', 'w', encoding='utf-8') as f:
    json.dump(out, f)

print(f"Done. {n} pages total.")
# Show chapter 19 area
for i in range(358, 375):
    raw_tag = f" [raw:{perPage[i]}]" if perPage[i] != assigned[i] else ""
    print(f"  PDF page {i}: {assigned[i]}{raw_tag}")
