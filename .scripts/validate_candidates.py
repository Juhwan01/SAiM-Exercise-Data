"""
Curated candidate URLs for each problematic ID, based on domain knowledge.
Validate each by fetching and checking content match.
"""
import sys, os, json, urllib.request, urllib.parse, ssl, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

# ID → list of curated candidate URLs (in priority order)
CANDIDATES = {
    # === 4 confirmed 404s ===
    'D05': [  # 분할 루틴 비교
        'https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter',
        'https://rpstrength.com/blogs/video-guides/how-to-build-a-training-split-that-actually-works',
        'https://www.strongerbyscience.com/training-frequency/',
    ],
    'E11': [  # 풀업 폼 큐
        'https://www.strongerbyscience.com/training-program-design/',
        'https://startingstrength.com/article/chins-and-pullups',
        'https://www.t-nation.com/training/tip-the-perfect-pull-up/',
    ],
    'L03': [  # 청소년 가이드라인 (NSCA position)
        'https://pubmed.ncbi.nlm.nih.gov/19620931/',  # Faigenbaum 2009 NSCA youth
        'https://journals.lww.com/nsca-jscr/Fulltext/2009/08005/Youth_Resistance_Training__Updated_Position.2.aspx',
        'https://www.nsca.com/contentassets/116c55d64e1343d2b264e05aaf158a91/nsca_position_statement_youth.pdf',
    ],
    'O02': [  # HIIT vs LISS
        'https://www.strongerbyscience.com/concurrent-training/',
        'https://www.strongerbyscience.com/the-effects-of-cardio-on-gains/',
        'https://pubmed.ncbi.nlm.nih.gov/22002517/',
    ],
    # === 19 homepage-only ===
    'A01': [  # RPE 정의 (Tuchscherer RTS)
        'https://articles.reactivetrainingsystems.com/2015/10/21/rts-101-introduction-to-rpe/',
        'https://www.reactivetrainingsystems.com/Knowledge-Base/Articles/2015/10/21/rts-101-introduction-to-rpe',
        'https://articles.reactivetrainingsystems.com/',
        'https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/',
    ],
    'C11': [  # Hackett 2018 session length
        'https://pubmed.ncbi.nlm.nih.gov/29490526/',
        'https://journals.lww.com/nsca-scj/fulltext/2018/04000/training_practices_and_ergogenic_aids_used_by_male.7.aspx',
    ],
    'E07': [  # 벤치프레스 폼 큐
        'https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology',
        'https://startingstrength.com/article/the-bench-press',
        'https://powerliftingtechnique.com/bench-press-cues/',
        'https://www.strongerbyscience.com/how-to-bench-press/',
    ],
    'E15': [  # 부상 신호 vs 근육통
        'https://blog.nasm.org/the-difference-between-muscle-soreness-and-injury',
        'https://www.acefitness.org/resources/pros/expert-articles/5413/muscle-soreness-vs-injury-what-s-the-difference/',
        'https://blog.nasm.org/delayed-onset-muscle-soreness',
    ],
    'E16': [  # 컴파운드 셋업 체크리스트
        'https://startingstrength.com/article/the_squat',
        'https://www.strongerbyscience.com/how-to-squat/',
        'https://powerliftingtechnique.com/setup-for-the-big-three/',
    ],
    'E17': [  # 그립 너비/유형
        'https://powerliftingtechnique.com/grip-width-bench-press/',
        'https://www.strongerbyscience.com/grip-width/',
        'https://barbend.com/grip-width-bench-press/',
    ],
    'F05': [  # SFR
        'https://renaissanceperiodization.com/exercise-selection-stimulus-fatigue-ratio/',
        'https://rpstrength.com/blogs/articles/stimulus-to-fatigue-ratio-explained',
        'https://www.strongerbyscience.com/stimulus-to-fatigue-ratio/',
    ],
    'H01': [  # Helms pyramid
        'https://muscleandstrengthpyramids.com/training/',
        'https://muscleandstrengthpyramids.com/the-muscle-and-strength-pyramid-training/',
        'https://www.3dmusclejourney.com/blog/the-pyramid-of-muscle-and-strength',
    ],
    'H02': [  # Adherence first
        'https://muscleandstrengthpyramids.com/training/',
        'https://www.3dmusclejourney.com/articles/adherence',
        'https://strongerbyscience.com/individual-differences/',
    ],
    'I01': [  # 초보자 LP (Rippetoe)
        'https://startingstrength.com/get-started/programs',
        'https://thefitness.wiki/routines/starting-strength/',
        'https://startingstrength.com/article/the-novice-effect',
    ],
    'I02': [  # Tempo Notation
        'https://www.strongerbyscience.com/tempo/',
        'https://www.t-nation.com/training/tempo-training-revisited/',
        'https://barbend.com/tempo-training/',
    ],
    'I03': [  # 운동 순서 (compound first)
        'https://www.nsca.com/education/articles/exercise-order/',
        'https://www.strongerbyscience.com/exercise-order/',
        'https://barbend.com/exercise-order/',
    ],
    'I04': [  # ACWR Gabbett
        'https://bjsm.bmj.com/content/50/5/273',
        'https://pubmed.ncbi.nlm.nih.gov/26758673/',
        'https://www.scienceforsport.com/acutechronic-workload-ratio/',
    ],
    'J01': [  # 부상별 대체 운동
        'https://renaissanceperiodization.com/training-around-injuries/',
        'https://www.strongerbyscience.com/training-around-injuries/',
        'https://barbend.com/exercise-substitutions-for-injuries/',
    ],
    'J04': [  # 편측 vs 양측
        'https://pubmed.ncbi.nlm.nih.gov/15903374/',  # McCurdy 2005
        'https://www.strongerbyscience.com/unilateral-vs-bilateral-training/',
        'https://barbend.com/unilateral-vs-bilateral-training/',
    ],
    'J05': [  # 컴파운드:아이솔 비율
        'https://renaissanceperiodization.com/compound-vs-isolation-exercises/',
        'https://www.strongerbyscience.com/exercise-selection/',
        'https://barbend.com/compound-vs-isolation-exercises/',
    ],
    'J06': [  # 선호 운동 매칭 (Helms adherence)
        'https://muscleandstrengthpyramids.com/training/',
        'https://www.3dmusclejourney.com/articles/exercise-selection',
        'https://www.strongerbyscience.com/exercise-selection/',
    ],
    'M02': [  # 진행도 평가 주기
        'https://muscleandstrengthpyramids.com/training/',
        'https://www.strongerbyscience.com/measuring-progress/',
        'https://barbend.com/measuring-progress-strength-training/',
    ],
    'P04': [  # 관절 모빌리티
        'https://blog.nasm.org/the-importance-of-joint-mobility',
        'https://www.acefitness.org/resources/pros/expert-articles/6020/joint-mobility-vs-flexibility/',
        'https://blog.nasm.org/dynamic-warm-up',
    ],
}

def headers_for(url):
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*',
         'Accept-Language': 'en-US,en;q=0.9', 'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1'}
    host = urlparse(url).netloc
    if 'pubmed' in host or 'ncbi' in host or 'bmj.com' in host:
        h['Referer'] = 'https://www.google.com/'
    return h

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=headers_for(url))
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return {'ok': True, 'status': r.status, 'final_url': r.geturl(),
                    'data': r.read(800_000), 'ct': r.headers.get('Content-Type','')}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'status': e.code, 'err': f'HTTP {e.code}', 'final_url': url}
    except Exception as e:
        return {'ok': False, 'status': None, 'err': f'{type(e).__name__}: {e}', 'final_url': url}

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

import urllib.error

# Validate all candidates in parallel
all_urls = sorted({u for v in CANDIDATES.values() for u in v})
print(f'Validating {len(all_urls)} candidate URLs...')
fetched = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(fetch, u): u for u in all_urls}
    for i, fut in enumerate(as_completed(futs), 1):
        u = futs[fut]
        try: fetched[u] = fut.result()
        except Exception as e: fetched[u] = {'ok': False, 'err': str(e)}
        if i % 10 == 0: print(f'  {i}/{len(all_urls)}')

# Build per-ID report (best 200 candidate)
report = {}
for rid, urls in CANDIDATES.items():
    entries = []
    for u in urls:
        r = fetched.get(u, {})
        e = {'url': u, 'status': r.get('status'), 'error': r.get('err','')}
        if r.get('ok') and r.get('status') == 200:
            e['title'] = title_of(r['data'])
            e['snippet'] = text_of(r['data'], r.get('ct',''))[:500]
        entries.append(e)
    report[rid] = entries

with open('.scripts/fetched/_curated.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('\n=== Per-ID best result ===\n')
for rid in CANDIDATES:
    entries = report[rid]
    ok = [e for e in entries if e.get('status') == 200]
    if ok:
        e = ok[0]
        print(f'  [OK]  {rid}  {e["url"]}')
        print(f'         title: {e.get("title","")[:130]}')
    else:
        print(f'  [--]  {rid}  no valid candidate')
        for e in entries:
            print(f'         x {e.get("status")}  {e["url"]}')

print('\nSaved: .scripts/fetched/_curated.json')
