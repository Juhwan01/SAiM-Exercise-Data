"""
Fetch every unique URL in the master CSV, save HTML/text to .scripts/fetched/,
and produce a small summary so we can judge which entries are meaningful.
"""
import csv, os, sys, json, hashlib, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request, urllib.error, ssl

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

OUT_DIR = '.scripts/fetched'
os.makedirs(OUT_DIR, exist_ok=True)

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

def slug(u: str) -> str:
    return hashlib.md5(u.encode('utf-8')).hexdigest()[:12]

def load_master():
    with open('workout_knowledge_base.csv', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def fetch(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*'})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read(800_000)  # cap 800 KB
            ct = r.headers.get('Content-Type', '')
            final_url = r.geturl()
            status = r.status
        return {'ok': True, 'status': status, 'ct': ct, 'final_url': final_url, 'bytes': len(data), 'data': data}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTPError {e.code}', 'final_url': url}
    except Exception as e:
        return {'ok': False, 'status': None, 'err': f'{type(e).__name__}: {e}', 'final_url': url}

def strip_html(b: bytes, ct: str) -> str:
    try:
        html = b.decode('utf-8', errors='replace')
    except Exception:
        return ''
    if 'json' in ct.lower():
        return html[:2000]
    # very lightweight tag strip
    import re
    html = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', ' ', html, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def title(b: bytes) -> str:
    try:
        html = b.decode('utf-8', errors='replace')
    except Exception:
        return ''
    import re
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, flags=re.I)
    return (m.group(1).strip() if m else '')[:200]

def work(rid_url):
    rid, url = rid_url
    res = fetch(url)
    rec = {'ID': rid, 'URL': url, 'final_url': res.get('final_url'), 'status': res.get('status')}
    if not res['ok']:
        rec['error'] = res['err']
        rec['title'] = ''
        rec['snippet'] = ''
        rec['saved'] = False
        return rec
    rec['ct'] = res['ct']
    rec['bytes'] = res['bytes']
    data = res['data']
    rec['title'] = title(data)
    rec['snippet'] = strip_html(data, res['ct'])[:1500]
    # save raw
    fp = os.path.join(OUT_DIR, f'{slug(url)}.html')
    with open(fp, 'wb') as f:
        f.write(data)
    rec['saved'] = True
    rec['file'] = fp
    return rec

rows = load_master()
# Map ID -> URL  (keep duplicates so we can see per-ID)
todo = [(r['ID'], r['URL']) for r in rows if r.get('URL')]
print(f'Total rows: {len(todo)}')
unique_urls = sorted({u for _, u in todo})
print(f'Unique URLs: {len(unique_urls)}')

results_by_url = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(work, ('-', u)): u for u in unique_urls}
    for i, fut in enumerate(as_completed(futs), 1):
        u = futs[fut]
        try:
            results_by_url[u] = fut.result()
        except Exception as e:
            results_by_url[u] = {'URL': u, 'error': f'fut {e}'}
        if i % 10 == 0:
            print(f'  {i}/{len(unique_urls)} done')

# Build per-row report
report = []
for r in rows:
    u = r.get('URL', '')
    res = results_by_url.get(u, {})
    report.append({
        'ID': r['ID'],
        '항목': r['항목'],
        '출처': r['출처'],
        'URL': u,
        'final_url': res.get('final_url'),
        'status': res.get('status'),
        'title': res.get('title', ''),
        'error': res.get('error', ''),
        'snippet': (res.get('snippet') or '')[:600],
    })

with open(os.path.join(OUT_DIR, '_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# Print summary
print('\n=== Summary ===')
ok = sum(1 for r in report if r['status'] == 200 and not r['error'])
err = sum(1 for r in report if r['error'])
other = len(report) - ok - err
print(f'OK 200: {ok}  Errors: {err}  Other: {other}')
print('\nNon-200 / errors:')
for r in report:
    if r['error'] or (r['status'] and r['status'] != 200):
        print(f"  {r['ID']:4} {r['status']!s:4} {r['error']!s:40}  {r['URL']}")
print('\nReport saved to', os.path.join(OUT_DIR, '_report.json'))
