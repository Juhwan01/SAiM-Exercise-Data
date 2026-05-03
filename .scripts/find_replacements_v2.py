"""
v2: Use Bing HTML search (more bot-friendly), with DDG fallback.
Serial with delay to avoid rate limiting.
"""
import csv, os, sys, json, urllib.request, urllib.parse, urllib.error, ssl, re, time
from urllib.parse import urlparse, parse_qs, unquote

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

QUERIES = {
    'D05': ['rpstrength training split muscle growth', 'best training split frequency Schoenfeld'],
    'E11': ['stronger by science pull up technique', 'pull up form cues guide'],
    'L03': ['NSCA youth resistance training position statement 2009', 'youth resistance training NSCA position'],
    'O02': ['stronger by science cardio interference muscle', 'HIIT vs LISS muscle interference'],
    'A01': ['Mike Tuchscherer RPE RIR definition', 'RPE RIR autoregulation reactive training'],
    'C11': ['training session length 60 90 minutes Hackett', 'Hackett 2018 bodybuilder session length'],
    'E07': ['starting strength bench press cues form', 'bench press technique cues setup'],
    'E15': ['injury versus DOMS muscle soreness signs', 'soreness vs injury exercise signs'],
    'E16': ['compound lift setup checklist five steps', 'powerlifting setup checklist'],
    'E17': ['powerliftingtechnique grip width bench', 'grip width pull up bench deadlift'],
    'F05': ['stimulus fatigue ratio SFR Israetel exercise selection', 'SFR Israetel exercise selection'],
    'H01': ['Helms muscle strength pyramid hierarchy training', 'Helms training pyramid adherence volume'],
    'H02': ['Helms adherence first principle best program', 'best program is one you stick to Helms'],
    'I01': ['novice linear progression Rippetoe starting strength', 'novice 5x5 program linear progression'],
    'I02': ['tempo notation lifting eccentric concentric 4 number', 'tempo prescription strength training NSCA'],
    'I03': ['exercise order compound before isolation NSCA', 'order of exercises compound first'],
    'I04': ['Gabbett ACWR acute chronic workload ratio', 'acute chronic workload ratio injury'],
    'J01': ['exercise substitution injury alternative knee shoulder', 'knee pain squat alternative leg press'],
    'J04': ['unilateral bilateral training muscle activation', 'McCurdy unilateral bilateral comparison'],
    'J05': ['compound to isolation ratio Israetel beginner advanced', 'compound isolation ratio programming'],
    'J06': ['Helms adherence preferred exercise substitute SFR', 'preferred exercise selection adherence'],
    'M02': ['progress measurement frequency hypertrophy strength', 'how often measure progress strength training'],
    'P04': ['joint mobility hip ankle thoracic squat', 'mobility work hip ankle compound lifts'],
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

def bing_search(q):
    """Bing HTML search."""
    url = 'https://www.bing.com/search?q=' + urllib.parse.quote_plus(q) + '&count=10'
    res = fetch(url, headers={'Referer': 'https://www.bing.com/'})
    if not res['ok']: return []
    html = res['data'].decode('utf-8', errors='replace')
    out = []
    # Bing organic results: <li class="b_algo"><h2><a href="URL">Title</a>...
    for m in re.finditer(r'<li class="b_algo"[^>]*>[\s\S]*?<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', html):
        href = m.group(1)
        title = re.sub(r'<[^>]+>', '', m.group(2))
        title = re.sub(r'\s+', ' ', title).strip()
        if href.startswith('http'):
            out.append({'title': title, 'url': href})
        if len(out) >= 8: break
    return out

def brave_search(q):
    """Brave HTML search fallback."""
    url = 'https://search.brave.com/search?q=' + urllib.parse.quote_plus(q)
    res = fetch(url, headers={'Referer': 'https://search.brave.com/'})
    if not res['ok']: return []
    html = res['data'].decode('utf-8', errors='replace')
    out = []
    for m in re.finditer(r'<a[^>]+class="[^"]*result-header[^"]*"[^>]+href="([^"]+)"', html):
        href = m.group(1)
        if href.startswith('http'):
            out.append({'title': '', 'url': href})
        if len(out) >= 8: break
    if not out:
        # alternative pattern
        for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="[^"]*snippet[^"]*"', html):
            out.append({'title':'', 'url': m.group(1)})
            if len(out) >= 8: break
    return out

def search_multi(q):
    r = bing_search(q)
    if r: return ('bing', r)
    time.sleep(2)
    r = brave_search(q)
    if r: return ('brave', r)
    return ('none', [])

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
    cands = []
    seen = set()
    for q in queries:
        eng, results = search_multi(q)
        for r in results:
            u = r['url']
            host = urlparse(u).netloc
            if any(x in host for x in ['bing.com', 'duckduckgo', 'youtube.com', 'reddit.com/login', 'facebook.com', 'twitter.com', 'pinterest', 'amazon.com', 'instagram']):
                continue
            if u in seen: continue
            seen.add(u)
            cands.append({'q': q, 'engine': eng, 'host': host, 'url': u, 'title': r['title']})
            if len(cands) >= 8: break
        time.sleep(2.5)
        if len(cands) >= 6: break
    # validate
    for c in cands:
        res = fetch(c['url'])
        if res['ok'] and res['status'] == 200:
            c['status'] = 200
            c['page_title'] = title_of(res['data'])
            c['snippet'] = text_of(res['data'], res.get('ct',''))[:600]
        else:
            c['status'] = res.get('status')
            c['error'] = res.get('err','')
    return cands

results = {}
ids = list(QUERIES.keys())
print(f'Searching for {len(ids)} IDs (Bing primary, Brave fallback)...')
for i, rid in enumerate(ids, 1):
    print(f'  [{i}/{len(ids)}] {rid}', flush=True)
    try:
        results[rid] = evaluate(rid, QUERIES[rid])
    except Exception as e:
        results[rid] = [{'error': f'{type(e).__name__}: {e}'}]
    # save incremental in case it crashes
    with open('.scripts/fetched/_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    time.sleep(2)

print('\n=== Top 200-OK candidate per ID ===')
for rid in ids:
    cands = results.get(rid, [])
    ok = [c for c in cands if c.get('status') == 200]
    if not ok:
        print(f'  {rid}: NO valid candidate (had {len(cands)} hits, engines: {set(c.get("engine","?") for c in cands)})')
        continue
    c = ok[0]
    print(f'  {rid}: {c["host"]}  ({c.get("engine")})')
    print(f'         {c["url"]}')
    print(f'         title: {c.get("page_title","")[:120]}')
print('\nFull report at .scripts/fetched/_candidates.json')
