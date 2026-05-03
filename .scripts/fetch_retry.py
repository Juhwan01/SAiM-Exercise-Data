"""
Retry failed URLs with realistic browser headers.
Also flag homepage-only URLs (path '/' or '' = low information value).
"""
import csv, os, sys, json, hashlib, urllib.request, urllib.error, ssl, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')
OUT_DIR = '.scripts/fetched'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

def headers_for(url: str) -> dict:
    host = urlparse(url).netloc
    h = {
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    if 'pubmed' in host or 'ncbi.nlm.nih.gov' in host:
        h['Referer'] = 'https://www.google.com/'
    elif 'bmj.com' in host:
        h['Referer'] = 'https://www.google.com/'
    elif 'acsm.org' in host:
        h['Referer'] = 'https://www.google.com/'
    return h

def fetch(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers=headers_for(url))
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read(800_000)
            return {'ok': True, 'status': r.status, 'ct': r.headers.get('Content-Type',''),
                    'final_url': r.geturl(), 'data': data}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTPError {e.code}', 'final_url': url}
    except Exception as e:
        return {'ok': False, 'status': None, 'err': f'{type(e).__name__}: {e}', 'final_url': url}

def title(b: bytes) -> str:
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, flags=re.I)
    return (m.group(1).strip() if m else '')[:200]

def strip(b: bytes, ct: str) -> str:
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    if 'json' in ct.lower(): return html[:2000]
    html = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', ' ', html, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', html)
    return re.sub(r'\s+', ' ', text).strip()

# Load existing report
with open(os.path.join(OUT_DIR, '_report.json'), encoding='utf-8') as f:
    report = json.load(f)

# Identify rows that need retry: status != 200 or has error
to_retry = [r for r in report if r.get('error') or r.get('status') != 200]
unique_retry = sorted({r['URL'] for r in to_retry})
print(f'Retrying {len(unique_retry)} unique URLs ({len(to_retry)} rows)')

results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in unique_retry}
    for i, fut in enumerate(as_completed(futs), 1):
        u = futs[fut]
        try: results[u] = fut.result()
        except Exception as e: results[u] = {'ok': False, 'err': f'fut {e}'}
        if i % 5 == 0: print(f'  {i}/{len(unique_retry)} done')

# Update report
def slug(u): return hashlib.md5(u.encode()).hexdigest()[:12]

for r in report:
    if r.get('error') or r.get('status') != 200:
        u = r['URL']
        res = results.get(u)
        if res and res.get('ok'):
            r['status'] = res['status']
            r['final_url'] = res['final_url']
            r['title'] = title(res['data'])
            r['snippet'] = strip(res['data'], res.get('ct',''))[:600]
            r['error'] = ''
            with open(os.path.join(OUT_DIR, f"{slug(u)}.html"), 'wb') as f: f.write(res['data'])
            r['retry_ok'] = True
        elif res:
            r['status'] = res.get('status')
            r['error'] = res.get('err','')
            r['retry_ok'] = False

# Flag homepage-only URLs
def is_homepage(u: str) -> bool:
    p = urlparse(u).path
    return p in ('', '/', '/en/', '/blog/', '/articles/')

for r in report:
    r['is_homepage'] = is_homepage(r['URL'])

with open(os.path.join(OUT_DIR, '_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# Final summary
ok = [r for r in report if r['status'] == 200 and not r.get('error')]
err = [r for r in report if r.get('error') or (r.get('status') and r['status'] != 200)]
home = [r for r in ok if r['is_homepage']]
real = [r for r in ok if not r['is_homepage']]

print('\n=== After retry ===')
print(f'OK (200): {len(ok)}  Errors: {len(err)}')
print(f'  Homepage-only OK: {len(home)} (suspect — flag for manual decision)')
print(f'  Real article OK: {len(real)}')

print('\n--- Still failing ---')
for r in err:
    print(f"  {r['ID']:4} {r.get('status')!s:5} {r.get('error','')!s:35}  {r['URL']}")

print('\n--- Homepage-only (low info value) ---')
for r in home:
    print(f"  {r['ID']:4} {r['항목'][:30]:30}  {r['URL']}")
