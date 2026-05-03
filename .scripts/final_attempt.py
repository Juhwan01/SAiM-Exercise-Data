"""
Final pass: try alternative URLs for the still-problematic entries,
plus PubMed canonical references for the bot-blocked ones.
"""
import sys, os, json, urllib.request, ssl, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import urllib.error

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

CANDIDATES = {
    # A01: RPE definition — RTS site is empty, find alt
    'A01': [
        'https://articles.reactivetrainingsystems.com/2015/10/21/rts-101-introduction-to-rpe/',
        'https://articles.reactivetrainingsystems.com/',
        'https://www.t-nation.com/training/the-rpe-scale-explained/',
        'https://www.juggernauttraining.com/the-importance-of-the-rpe-scale-and-rir/',
        'https://barbend.com/rpe-rir-explained/',
    ],
    # E15: injury vs DOMS — ACE redirected to wrong content
    'E15': [
        'https://www.healthline.com/health/exercise-fitness/muscle-soreness-vs-pain-or-injury',
        'https://blog.nasm.org/uncategorized/exercise-induced-muscle-soreness',
        'https://www.barbend.com/muscle-soreness-vs-injury/',
        'https://stronger.run/muscle-soreness-vs-injury/',
        'https://www.runnersworld.com/training/a20825814/training-pain-vs-injury/',
    ],
    # P04: joint mobility
    'P04': [
        'https://blog.nasm.org/joint-flexibility-vs-mobility',
        'https://www.acsm.org/blog-detail/acsm-certified-blog/2019/04/15/seven-ways-improve-flexibility-mobility',
        'https://www.strongerbyscience.com/mobility/',
        'https://barbend.com/mobility-vs-flexibility/',
        'https://www.precisionnutrition.com/category/movement',
    ],
    # E17: grip width
    'E17': [
        'https://barbend.com/bench-press-grip-width/',
        'https://www.strongerbyscience.com/correct-bench-grip/',
        'https://startingstrength.com/article/grip-width-on-the-bench-press',
        'https://powerliftingtechnique.com/blog/',
        'https://liftbigeatbig.com/grip-width-bench-press/',
    ],
    # F05: stimulus-fatigue ratio
    'F05': [
        'https://www.t-nation.com/training/tip-the-stimulus-to-fatigue-ratio/',
        'https://rpstrength.com/blogs/articles/exercise-selection',
        'https://renaissanceperiodization.com/exercise-selection/',
        'https://www.youtube.com/results?search_query=stimulus+fatigue+ratio+israetel',
        'https://www.strongerbyscience.com/exercise-selection/',
    ],
    # J01: injury substitution
    'J01': [
        'https://www.strongerbyscience.com/training-around-pain/',
        'https://renaissanceperiodization.com/training-with-pain/',
        'https://barbend.com/exercise-modifications-injuries/',
        'https://www.t-nation.com/training/training-around-injuries/',
        'https://www.precisionnutrition.com/category/movement',
    ],
    # PubMed canonical references (will 403 to Python but valid for users)
    # Mark these explicitly as "use as-is, browser-valid"
    'L03_pubmed': ['https://pubmed.ncbi.nlm.nih.gov/19620931/'],
    'C11_pubmed': ['https://pubmed.ncbi.nlm.nih.gov/29490526/'],
    'J04_pubmed': ['https://pubmed.ncbi.nlm.nih.gov/15903374/'],
}

def headers_for(url):
    h = {'User-Agent': UA, 'Accept': 'text/html,*/*', 'Accept-Language': 'en-US,en;q=0.9',
         'Referer': 'https://www.google.com/'}
    return h

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=headers_for(url))
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read(800_000)
            return {'ok': True, 'status': r.status, 'final_url': r.geturl(), 'data': data}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTP {e.code}'}
    except Exception as e:
        return {'ok': False, 'status': None, 'err': f'{type(e).__name__}: {e}'}

def title_of(b):
    try: html = b.decode('utf-8', errors='replace')
    except: return ''
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, flags=re.I)
    return (m.group(1).strip() if m else '')[:200]

def words_of(b):
    try: html = b.decode('utf-8', errors='replace')
    except: return 0
    text = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return len(re.sub(r'\s+', ' ', text).strip().split())

all_urls = sorted({u for v in CANDIDATES.values() for u in v})
print(f'Validating {len(all_urls)} URLs')
res = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u): u for u in all_urls}
    for fut in as_completed(futs):
        u = futs[fut]
        try: res[u] = fut.result()
        except Exception as e: res[u] = {'ok': False, 'err': str(e)}

print('\n=== Final candidates ===')
for rid, urls in CANDIDATES.items():
    print(f'\n[{rid}]')
    for u in urls:
        r = res.get(u, {})
        if r.get('ok'):
            data = r.get('data', b'')
            words = words_of(data) if data else 0
            mark = 'OK ' if words > 200 else 'thin'
            print(f'  {mark} {r.get("status")} ({words}w)  {u[:80]}')
            if mark == 'OK ':
                print(f'        title: {title_of(data)[:120]}')
                print(f'        final: {r.get("final_url","")[:120]}')
        else:
            print(f'  ERR {r.get("status")} {r.get("err","")[:30]}  {u[:80]}')
