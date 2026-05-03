"""
For each of the 23 problematic entries (4 hard 404s + 19 homepage-only),
search DuckDuckGo for a replacement URL and validate it.

Output: .scripts/fetched/_candidates.json with top candidates per ID.
"""
import csv, os, sys, json, urllib.request, urllib.parse, urllib.error, ssl, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, unquote

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

# ID → search query (curated based on 항목 + 출처 + key terms)
QUERIES = {
    # confirmed 404s
    'D05': ['site:rpstrength.com training split muscle', 'best training split frequency Schoenfeld'],
    'E11': ['site:strongerbyscience.com pull up technique', 'pull up form cues stronger by science'],
    'L03': ['NSCA youth resistance training position statement', 'site:nsca.com youth resistance training'],
    'O02': ['site:strongerbyscience.com cardio interference', 'HIIT LISS muscle interference Schoenfeld'],
    # homepage-only
    'A01': ['Mike Tuchscherer RPE RIR definition reactive training systems', 'RPE RIR Tuchscherer autoregulation'],
    'C11': ['Hackett 2018 session length training duration', 'training session length 60 90 minutes cortisol'],
    'E07': ['site:startingstrength.com bench press cues', 'bench press technique cues starting strength'],
    'E15': ['site:nasm.org injury versus muscle soreness', 'injury signs vs DOMS Hartmann'],
    'E16': ['compound lift setup checklist NSCA', 'compound exercise setup five steps'],
    'E17': ['site:powerliftingtechnique.com grip width', 'grip width bench deadlift powerlifting technique'],
    'F05': ['stimulus fatigue ratio SFR Israetel', 'SFR exercise selection RP Strength'],
    'H01': ['Helms muscle and strength pyramid training', 'Helms training hierarchy adherence volume'],
    'H02': ['Helms adherence first principle training', 'best program adherence Eric Helms'],
    'I01': ['site:startingstrength.com novice linear progression', 'novice linear progression Rippetoe'],
    'I02': ['tempo notation lifting 4 number eccentric', 'tempo prescription strength NSCA'],
    'I03': ['exercise order compound before isolation NSCA', 'NSCA Essentials exercise order'],
    'I04': ['Gabbett 2016 ACWR acute chronic workload', 'acute chronic workload ratio injury Gabbett'],
    'J01': ['exercise substitution injury alternative Israetel', 'knee pain squat alternative leg press'],
    'J04': ['unilateral bilateral training muscle activation', 'McCurdy unilateral bilateral'],
    'J05': ['compound isolation ratio Israetel programming', 'compound to isolation ratio beginner advanced'],
    'J06': ['Helms adherence exercise selection preference', 'preferred exercise substitute SFR'],
    'M02': ['Helms muscle pyramid progress measurement', 'progress measurement frequency hypertrophy strength'],
    'P04': ['joint mobility work hip ankle thoracic compound lifts', 'NASM mobility hip ankle squat'],
}

def fetch(url, headers=None, timeout=15):
    h = {'User-Agent': UA, 'Accept': 'text/html,*/*', 'Accept-Language': 'en-US,en;q=0.9'}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return {'ok': True, 'status': r.status, 'final_url': r.geturl(),
                    'data': r.read(800_000), 'ct': r.headers.get('Content-Type','')}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTP {e.code}'}
    except Exception as e:
        return {'ok': False, 'status': None, 'err': f'{type(e).__name__}: {e}'}

def ddg_search(q):
    """DuckDuckGo HTML — returns list of {title, url, snippet}."""
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote_plus(q)
    res = fetch(url, headers={'Referer': 'https://duckduckgo.com/'})
    if not res['ok']:
        return []
    html = res['data'].decode('utf-8', errors='replace')
    out = []
    # results have class="result__a" (link), class="result__snippet" (text)
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', html):
        href = m.group(1)
        # DDG wraps in /l/?uddg=...
        if href.startswith('/l/?') or href.startswith('//duckduckgo.com/l/'):
            qs = parse_qs(urlparse(href).query)
            href = unquote(qs.get('uddg', [href])[0])
        title = re.sub(r'\s+', ' ', m.group(2)).strip()
        out.append({'title': title, 'url': href})
        if len(out) >= 8: break
    # try to attach snippets (best effort, optional)
    return out

def title_of(b):
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, flags=re.I)
    return (m.group(1).strip() if m else '')[:200]

def text_of(b, ct=''):
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    if 'json' in ct.lower(): return html[:1500]
    html = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', ' ', html, flags=re.I)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()

def evaluate(rid, queries):
    """Search and return up to 5 candidates per ID."""
    seen = set()
    cands = []
    for q in queries:
        for r in ddg_search(q):
            u = r['url']
            if not u or u.startswith('javascript:'): continue
            host = urlparse(u).netloc
            # skip search engine / aggregator junk
            if any(x in host for x in ['duckduckgo', 'youtube.com', 'reddit.com/login', 'facebook.com', 'twitter.com', 'linkedin.com', 'pinterest']):
                continue
            if u in seen: continue
            seen.add(u)
            cands.append({'q': q, 'host': host, 'url': u, 'title': r['title']})
            if len(cands) >= 8: break
        time.sleep(0.7)
        if len(cands) >= 8: break
    # validate each candidate
    for c in cands:
        res = fetch(c['url'])
        if res['ok'] and res['status'] == 200:
            c['status'] = 200
            c['page_title'] = title_of(res['data'])
            c['snippet'] = text_of(res['data'], res.get('ct',''))[:500]
        else:
            c['status'] = res.get('status')
            c['error'] = res.get('err','')
    return cands

results = {}
ids = list(QUERIES.keys())
print(f'Searching for {len(ids)} IDs...')
for i, rid in enumerate(ids, 1):
    print(f'  [{i}/{len(ids)}] {rid}')
    try:
        results[rid] = evaluate(rid, QUERIES[rid])
    except Exception as e:
        results[rid] = [{'error': f'{type(e).__name__}: {e}'}]
    time.sleep(1.2)  # be polite to DDG

with open('.scripts/fetched/_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Summary
print('\n=== Top candidate per ID (200-OK only) ===')
for rid in ids:
    cands = results.get(rid, [])
    ok = [c for c in cands if c.get('status') == 200]
    if not ok:
        print(f'  {rid}: NO valid candidate (had {len(cands)} hits)')
        for c in cands[:3]:
            print(f'         x  {c.get("status")}  {c.get("url")}')
        continue
    c = ok[0]
    print(f'  {rid}: {c["host"]}')
    print(f'         {c["url"]}')
    print(f'         title: {c.get("page_title","")[:120]}')

print('\nFull report at .scripts/fetched/_candidates.json')
