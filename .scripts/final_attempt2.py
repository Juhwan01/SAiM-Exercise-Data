"""
Last attempt: PubMed PMIDs for canonical research, plus a few new candidates.
"""
import sys, os, urllib.request, urllib.error, ssl, re, json
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

CANDIDATES = {
    # A01: Zourdos 2016 RPE validation paper
    'A01': [
        'https://pubmed.ncbi.nlm.nih.gov/26049792/',  # Zourdos 2016 RPE
        'https://www.juggernauttraining.com/rts/',
        'https://www.juggernauttraining.com/category/articles/training-articles/',
        'https://articles.reactivetrainingsystems.com/2015/10/21/rts-101-introduction-to-rpe',
    ],
    # E15: Hartmann 2013 / Cheung DOMS review
    'E15': [
        'https://pubmed.ncbi.nlm.nih.gov/12617692/',  # Cheung 2003 DOMS
        'https://pubmed.ncbi.nlm.nih.gov/24138782/',  # Hartmann 2013
        'https://www.physio-pedia.com/Delayed_Onset_Muscle_Soreness_(DOMS)',
        'https://www.ncbi.nlm.nih.gov/books/NBK557615/',
    ],
    # P04: Page 2012 mobility review
    'P04': [
        'https://pubmed.ncbi.nlm.nih.gov/22319684/',  # Page 2012 stretching
        'https://www.physio-pedia.com/Joint_Mobility',
        'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3273886/',
    ],
    # J01: Lorenz BJSM training around pain
    'J01': [
        'https://pubmed.ncbi.nlm.nih.gov/28953423/',  # Smith 2017 training with pain
        'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5198069/',
        'https://bjsm.bmj.com/content/53/19/1188',
    ],
    # H01: Helms Pyramid book canonical site (already homepage; can we find specific?)
    # Helms wrote articles on Stronger By Science:
    'H01': [
        'https://www.strongerbyscience.com/training-pyramid/',
        'https://www.3dmusclejourney.com/training',
        'https://muscleandstrengthpyramids.com/training/',
    ],
    'H02': [
        'https://www.strongerbyscience.com/individual-differences/',
        'https://www.3dmusclejourney.com/articles/adherence',
        'https://muscleandstrengthpyramids.com/training/',
    ],
}

def fetch(url, timeout=15):
    h = {'User-Agent': UA, 'Accept':'text/html,*/*', 'Accept-Language':'en-US,en;q=0.9',
         'Referer':'https://www.google.com/'}
    req = urllib.request.Request(url, headers=h)
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return {'ok': True, 'status': r.status, 'final_url': r.geturl(), 'data': r.read(800_000)}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTP {e.code}'}
    except Exception as e:
        return {'ok': False, 'err': f'{type(e).__name__}'}

def words_of(b):
    if not b: return 0
    try: html = b.decode('utf-8', errors='replace')
    except: return 0
    text = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.I)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text)).strip().split())

def title_of(b):
    if not b: return ''
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, flags=re.I)
    return (m.group(1).strip() if m else '')[:160]

all_urls = sorted({u for v in CANDIDATES.values() for u in v})
res = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in all_urls}
    for f in as_completed(futs):
        u = futs[f]
        try: res[u] = f.result()
        except Exception as e: res[u] = {'ok': False, 'err': str(e)}

for rid, urls in CANDIDATES.items():
    print(f'\n[{rid}]')
    for u in urls:
        r = res.get(u, {})
        if r.get('ok'):
            w = words_of(r.get('data'))
            mark = 'OK ' if w > 200 else 'thin'
            print(f'  {mark} {r.get("status")} ({w}w)  {u[:80]}')
            if w > 200:
                print(f'        title: {title_of(r["data"])}')
                print(f'        final: {r.get("final_url","")[:100]}')
        else:
            print(f'  ERR {r.get("status")} {r.get("err","")[:30]}  {u[:80]}')
