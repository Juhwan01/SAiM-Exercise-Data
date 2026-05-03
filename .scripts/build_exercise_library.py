"""
exercise_pool.csv (449행, 부위·운동명) → exercise_library.csv (룰베이스 필요 필드 추가)

추가 필드:
  - 장비       (운동명 키워드 추출)
  - 분류       (컴파운드 / 아이솔레이션 / 유산소)
  - 주동근      (부위 + 운동명 조합)
  - 협동근      (컴파운드 운동에 한해 추정)
  - 권장 렙범위 (분류·부위 룰)
  - 휴식초      (C07 룰)
  - 무게 단위    (장비 룰)
  - 난이도      (운동명·장비 휴리스틱)
  - 모호도      (자동추출 신뢰도; 낮음일수록 사람 검토 필요)
"""
import csv, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

SRC = 'exercise_pool.csv'
OUT = 'exercise_library.csv'

# ─────────────────────────────────────────
# 1. 장비 추출 (우선순위 순)
# ─────────────────────────────────────────
def detect_equipment(name: str, body_part: str) -> str:
    n = name
    if body_part == '유산소':
        # 유산소 기구는 운동명 그대로
        if any(k in n for k in ['트레드밀', '엘립티컬', '싸이클', '바이크',
                                 '스텝 머신', '스텝 밀', '스텝퍼', '로잉', '스키 에르그',
                                 '아크트레이너', '에어 바이크', '무동력']):
            return '유산소 기구'
        if '러닝' in n: return '맨몸/야외'
        return '맨몸'  # 버피, 점핑잭, 줄넘기, 마운틴 클라이머 등

    # 우선순위: 스미스 머신 > 머신 > 바벨 > 덤벨 > 케이블 > 케틀벨 > 밴드 > 이지바 > 플레이트 > 맨몸
    if '스미스 머신' in n or '스미스머신' in n or '스미스' in n: return '스미스 머신'
    if '케티블' in n: return '케틀벨'  # 오타 케티블=케틀벨
    if '머신' in n: return '머신'
    if '바벨' in n: return '바벨'
    if '덤벨' in n: return '덤벨'
    if '케이블' in n: return '케이블'
    if '케틀벨' in n: return '케틀벨'
    if '밴드' in n: return '밴드'
    if '이지바' in n: return '바벨'  # 이지바는 바벨 계열
    if '플레이트' in n: return '플레이트'
    if '보수볼' in n: return '보수볼'
    # 맨몸 키워드
    bw_keywords = ['(맨몸)', '푸쉬업', '풀 업', '풀업', '친 업', '친업', '딥스', '버피',
                   '플랭크', '브이 업', '브이업', '크런치', '레그 레이즈', '싯 업', '싯업',
                   '러시안 트위스트', 'AB슬라이드', '머슬업', '슈퍼맨', '버드 독',
                   '마운틴 클라이머', '스파이더맨', '드래곤 플래그', '물구나무',
                   '점프', '터치다운', '훌라후프', '훌라', '암 앤 레그']
    if any(k in n for k in bw_keywords): return '맨몸'
    if name.startswith('('): return '맨몸'  # (맨몸)런지 등

    # ─── 장비 명시 없는 헬스장 디폴트 ───
    if body_part == '하체':
        # 머신 종목들
        if any(k in n for k in ['레그 프레스', '레그 컬', '레그 익스텐션',
                                 '브이 스쿼트', '핵 프레스', '펜들럼', '핵 스쿼트',
                                 '리버스 핵 스쿼트', '리버스 브이 스쿼트', '레버리지']):
            return '머신'
        if any(k in n for k in ['카프 레이즈', '카프레이즈']) and '스미스' not in n and '바벨' not in n and '덤벨' not in n:
            return '머신'
        if '힙 어덕션' in n or '힙 어브덕션' in n: return '머신'
        if '힙 익스텐션' in n or '힙 글루트' in n: return '머신'
        if any(k in n for k in ['글루트 킥', '글루트 햄', '몬스터 글루트', '글루트 믹']):
            return '머신'
        # 케틀벨/덤벨 디폴트
        if '고블릿' in n: return '덤벨'
        # 맨몸 디폴트
        if '피스톨' in n or '하이 니' in n: return '맨몸'
        if '런지' in n and '바벨' not in n and '덤벨' not in n and '케틀벨' not in n and '스미스' not in n and '밴드' not in n:
            return '맨몸'
        # 바벨 디폴트
        if '데드리프트' in n: return '바벨'
        if '스쿼트' in n: return '바벨'
        if '굿모닝' in n: return '바벨'
        if '힙 쓰러스트' in n: return '바벨'
        if '원 레그 니 업' in n or '원레그' in n: return '맨몸'

    if body_part == '복근':
        return '맨몸'  # 복근은 맨몸 디폴트 (머신/케이블 운동은 이미 위에서 잡힘)
    if body_part == '전완근':
        if '리스트 컬' in n: return '바벨'  # 단독 표기는 바벨 디폴트
        return '바벨'
    if body_part == '등':
        if '굿모닝' in n: return '바벨'
        if '백 익스텐션' in n: return '머신'  # 디폴트 머신 (45도 백익스텐션 머신)
        if '풀 업' in n or '풀업' in n or '친 업' in n or '친업' in n: return '맨몸'
        if '랫 풀다운' in n or '풀다운' in n: return '머신'  # 케이블 풀리 머신
        if '시티드 로우' in n or '로우 머신' in n: return '머신'
        if '데드리프트' in n: return '바벨'
        if '바벨 로우' in n or '로우' in n: return '바벨'  # 일반 로우 디폴트
    if body_part == '가슴':
        if '벤치 프레스' in n: return '바벨'  # 명시 없으면 바벨
        if '펙덱' in n or '펙 덱' in n: return '머신'
        if '푸쉬업' in n: return '맨몸'
        if '딥스' in n: return '맨몸'
        if '체스트 프레스' in n: return '머신'
    if body_part == '어깨':
        if '오버헤드 프레스' in n: return '바벨'
        if '숄더 프레스' in n: return '머신'
        if '프론트 레이즈' in n or '레터럴 레이즈' in n or '리어 델트' in n:
            return '덤벨'  # 일반 디폴트
        if '슈러그' in n: return '바벨'
    if body_part == '하체':
        # 추가 디폴트
        if '사이드 킥' in n or '사이드 레이즈' in n: return '맨몸'
        if '크랩 워킹' in n: return '맨몸'
        if '노르딕 컬' in n: return '맨몸'
        if '백 익스텐션' in n: return '머신'
        if '원 레그 니 업' in n: return '맨몸'
    if body_part == '등':
        if '펙덱' in n or '펙 덱' in n: return '머신'
        if '암 풀' in n: return '케이블'  # 암 풀 다운, 암 풀다운 → 케이블 풀리
        if '랙 풀' in n: return '바벨'
    if body_part == '어깨':
        if '페이스 풀' in n or '페이스풀' in n: return '케이블'
        if '아놀드 프레스' in n: return '덤벨'
        if '비하인드 넥' in n and '바벨' not in n and '덤벨' not in n and '스미스' not in n:
            return '바벨'
        if '랜드마인' in n: return '바벨'
    if body_part == '가슴':
        if '풀라이' in n: return '케이블'  # 벤치 케이블 풀라이 → 케이블
        if '어시스트 입스' in n or '어시스트 딥스' in n: return '머신'  # assist dip machine
    if body_part == '삼두':
        if '스컬 크러셔' in n or '라잉 트라이셉스 익스텐션' in n: return '바벨'  # EZ-바벨이 일반적
        if '클로즈 그립 벤치 프레스' in n and '인클라인' not in n: return '바벨'
    if body_part == '이두':
        if '컨센트레이션' in n: return '덤벨'
    if body_part == '어깨':
        if '바이킹 프레스' in n: return '바벨'

    return '미분류'


# ─────────────────────────────────────────
# 2. 분류 (컴파운드 / 아이솔레이션 / 유산소)
# ─────────────────────────────────────────
ISOLATION_KEYWORDS = ['컬', '익스텐션', '레이즈', '플라이', '크런치', '슈러그',
                      '페이스 풀', '페이스풀', '카프 레이즈', '킥백', '킥 백', '푸쉬다운',
                      '리스트', '롤러', '사이드 밴드', '슈러그', '플랭크',
                      '레그 컬', '레그 익스텐션', '힙 어덕션', '힙 어브덕션',
                      '리어 델트', '레터럴 레이즈', '프론트 레이즈',
                      '프리쳐 컬', '스컬 크러셔', '풀오버', '딥스(머신)',
                      '풀라이', '암 풀']

COMPOUND_KEYWORDS = ['스쿼트', '데드리프트', '벤치 프레스', '오버헤드 프레스',
                     '숄더 프레스', '체스트 프레스', '로우', '풀 업', '풀업',
                     '친 업', '친업', '딥스', '풀다운', '런지', '힙 쓰러스트',
                     '클린', '스내치', '스윙', '쓰러스트', '머슬업', '핵 스쿼트',
                     '핵 프레스', '레그 프레스', '브이 스쿼트', '점프 스쿼트',
                     '굿모닝', '스텝업', '하이풀',
                     '푸쉬업', '크로스오버', '풀 쓰루', '박스 점프', '점프', '버피',
                     '랜드마인', '바이킹',
                     '숄더프레스', '아놀드', '비하인드 넥', '딥스', '원 레그 니 업',
                     '크랩 워킹', '랙 풀', '어시스트 입스']

def detect_category(name: str, body_part: str) -> str:
    if body_part == '유산소': return '유산소'
    n = name
    # 명백한 컴파운드 우선
    for k in COMPOUND_KEYWORDS:
        if k in n:
            # 풀오버는 아이솔
            if '풀오버' in n: return '아이솔레이션'
            # "백 익스텐션"은 척추기립근 단독 — 아이솔로
            if '백 익스텐션' in n: return '아이솔레이션'
            return '컴파운드'

    # 머신 보조운동 추정 (글루트/하이퍼 머신 류)
    if '글루트' in n and '머신' in n: return '아이솔레이션'
    if '하이퍼' in n and '머신' in n: return '아이솔레이션'
    # 아이솔 키워드
    for k in ISOLATION_KEYWORDS:
        if k in n: return '아이솔레이션'
    # 부위 디폴트
    if body_part in ('이두', '삼두', '전완근', '복근'): return '아이솔레이션'
    return '추정'


# ─────────────────────────────────────────
# 3. 주동근 (부위 + 운동명 세분)
# ─────────────────────────────────────────
LOWER_BODY_MAP = [
    (['카프', '종아리'], '비복근/가자미근'),
    (['힙 어덕션', '이너싸이', '이너 싸이'], '내전근'),
    (['힙 어브덕션', '아웃타이', '아웃 타이', '사이드 킥', '사이드 레이즈'], '중둔근'),
    (['힙 쓰러스트', '힙 익스텐션', '힙 글루트', '글루트 킥', '글루트 햄', '몬스터 글루트', '글루트 믹'], '대둔근/햄스트링'),
    (['루마니안', '스티프', '굿모닝', '백 익스텐션'], '햄스트링/대둔근'),
    (['데드리프트'], '햄스트링/대둔근/척추기립근'),
    (['레그 컬'], '햄스트링'),
    (['레그 익스텐션', '익스텐션 머신'], '대퇴사두근'),
    (['런지', '스플릿 스쿼트', '스텝업', '불가리안'], '대퇴사두근/대둔근'),
    (['프론트 스쿼트', '제르셔', '저쳐'], '대퇴사두근'),
    (['스쿼트', '레그 프레스', '브이 스쿼트', '핵 스쿼트', '핵 프레스', '씨시'], '대퇴사두근/대둔근'),
]

def detect_primary_muscle(name: str, body_part: str) -> str:
    if body_part == '하체':
        for keys, muscle in LOWER_BODY_MAP:
            if any(k in name for k in keys): return muscle
        return '대퇴사두근/대둔근'  # default 하체
    if body_part == '가슴':
        if '인클라인' in name or '인크라인' in name: return '상부 대흉근'
        if '디클라인' in name: return '하부 대흉근'
        if '풀오버' in name: return '대흉근/광배근'
        return '대흉근'
    if body_part == '등':
        if '풀다운' in name or '풀 업' in name or '풀업' in name or '친 업' in name or '친업' in name:
            return '광배근'
        if '슈러그' in name: return '승모근 상부'
        if '백 익스텐션' in name or '굿모닝' in name: return '척추기립근'
        if '데드리프트' in name: return '척추기립근/광배근'
        if '로우' in name: return '광배근/승모근 중하부'
        if '리어' in name or '펙덱 리어' in name: return '후면 삼각근/능형근'
        return '광배근'
    if body_part == '어깨':
        if '리어' in name or '리어 델트' in name or '벤트 오버' in name or '벤트오버' in name or '페이스 풀' in name or '페이스풀' in name or '리버스 케이블 플라이' in name:
            return '후면 삼각근'
        if '프론트' in name: return '전면 삼각근'
        if '레터럴 레이즈' in name: return '측면 삼각근'
        if '슈러그' in name: return '승모근 상부'
        if '업라이트 로우' in name: return '측면 삼각근/승모근'
        return '삼각근(전체)'
    if body_part == '삼두': return '삼두근'
    if body_part == '이두':
        if '해머' in name: return '이두근/상완근'
        if '리버스' in name: return '상완근/전완근'
        return '이두근'
    if body_part == '복근':
        if '사이드' in name or '러시안' in name or '트위스트' in name or '바이시클' in name or '클로스 바디' in name:
            return '복사근'
        if '플랭크' in name and '사이드' in name: return '복사근'
        if '슈퍼맨' in name or '버드 독' in name: return '척추기립근'
        return '복직근'
    if body_part == '전완근': return '전완 굴근/신근'
    if body_part == '유산소': return '심폐'
    return body_part


# ─────────────────────────────────────────
# 4. 협동근 (컴파운드 한정)
# ─────────────────────────────────────────
def detect_secondary(name: str, body_part: str, category: str) -> str:
    if category != '컴파운드': return ''
    if body_part == '하체':
        if '데드리프트' in name: return '광배근/승모근/전완근'
        if '런지' in name or '스텝업' in name: return '햄스트링/종아리'
        if '스쿼트' in name or '레그 프레스' in name: return '햄스트링/척추기립근'
        if '힙 쓰러스트' in name: return '대퇴사두근/햄스트링'
        return '햄스트링/종아리'
    if body_part == '가슴':
        if '인클라인' in name or '오버헤드' in name: return '전면 삼각근/삼두근'
        return '전면 삼각근/삼두근'
    if body_part == '등':
        if '풀 업' in name or '풀업' in name or '친 업' in name or '친업' in name or '풀다운' in name:
            return '이두근/후면 삼각근'
        if '로우' in name: return '이두근/후면 삼각근/척추기립근'
        if '데드리프트' in name: return '햄스트링/대둔근/전완근'
        return '이두근'
    if body_part == '어깨':
        if '오버헤드' in name or '숄더 프레스' in name or '아놀드' in name or '시티드 오버헤드' in name or '비하인드 넥' in name or '바이킹' in name or '랜드마인' in name:
            return '삼두근/상부 대흉근'
        return ''
    if body_part == '삼두':
        if '벤치 프레스' in name or '딥스' in name: return '대흉근/전면 삼각근'
        return ''
    return ''


# ─────────────────────────────────────────
# 5. 무게 단위 (장비 룰)
# ─────────────────────────────────────────
def detect_increment(equipment: str, body_part: str) -> str:
    if equipment in ('바벨', '이지바'): return '2.5kg'
    if equipment == '스미스 머신': return '2.5kg'
    if equipment == '덤벨': return '1~2.5kg'
    if equipment == '머신': return '5kg'
    if equipment == '케이블': return '2.5kg'
    if equipment == '케틀벨': return '4kg'
    if equipment == '밴드': return '저항 단계'
    if equipment == '플레이트': return '2.5kg'
    if equipment == '보수볼': return '맨몸'
    if equipment == '맨몸': return '맨몸/체중조끼'
    if body_part == '유산소': return '강도/시간'
    return '미분류'


# ─────────────────────────────────────────
# 6. 권장 렙범위 (분류·부위 룰; C02·C03 기반)
# ─────────────────────────────────────────
def detect_rep_range(category: str, body_part: str) -> str:
    if body_part == '유산소': return '시간/거리'
    if category == '컴파운드':
        if body_part == '하체': return '5~8 (근력) / 6~12 (비대)'
        return '5~8 (근력) / 6~12 (비대)'
    if category == '아이솔레이션':
        if body_part in ('복근',): return '12~20 (또는 시간)'
        if body_part == '전완근': return '10~15'
        if body_part in ('이두', '삼두'): return '8~15'
        if body_part == '하체' and '카프' in body_part: return '10~20'
        return '8~15'
    return '8~12'


# ─────────────────────────────────────────
# 7. 휴식초 (C07 룰)
# ─────────────────────────────────────────
def detect_rest(category: str, body_part: str) -> str:
    if body_part == '유산소': return '인터벌별'
    if category == '컴파운드':
        if body_part == '하체': return '180~300'
        return '120~180'
    if category == '아이솔레이션':
        return '60~120'
    return '90~120'


# ─────────────────────────────────────────
# 8. 난이도 (휴리스틱)
# ─────────────────────────────────────────
def detect_difficulty(name: str, equipment: str, category: str, body_part: str) -> str:
    # 고급: 자유중량 컴파운드 (특히 빅3) + 일부 고난이도
    advanced_keywords = ['피스톨', '머슬업', '한 손', '원 암 풀 업', '원 레그',
                         '오버헤드 스쿼트', '드래곤 플래그', '물구나무', '제르셔', '저쳐',
                         '바이킹 프레스', '랜드마인 프레스', '바벨 핵 스쿼트',
                         '클린', '스내치']
    if any(k in name for k in advanced_keywords): return '고급'

    # 컴파운드 자유중량 → 중급 디폴트
    if category == '컴파운드' and equipment in ('바벨', '덤벨', '케틀벨', '이지바'):
        # 빅3는 중급 (초보도 코치 감독 하에)
        if any(k in name for k in ['바벨 스쿼트', '벤치 프레스', '데드리프트', '오버헤드 프레스']):
            return '중급'
        return '중급'
    # 머신·아이솔 → 초보
    if equipment in ('머신', '스미스 머신', '케이블'): return '초보'
    if category == '아이솔레이션': return '초보'
    if equipment == '맨몸':
        if any(k in name for k in ['푸쉬업', '크런치', '플랭크', '버피', '점프']): return '초보'
        if '풀 업' in name or '풀업' in name or '친 업' in name or '친업' in name or '딥스' in name:
            return '중급'
        return '초보'
    return '초보'


# ─────────────────────────────────────────
# 9. 모호도 점수 (낮을수록 사람 검토 필요)
# ─────────────────────────────────────────
def confidence(equipment: str, category: str, primary: str) -> str:
    score = 0
    if equipment != '미분류': score += 1
    if category != '추정': score += 1
    if primary and primary not in ('하체', '가슴', '등', '어깨'): score += 1
    return ['낮음', '중간', '중간', '높음'][score]


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def make_id(idx: int) -> str:
    return f'P{idx:03d}'  # P001~P449

with open(SRC, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

out_rows = []
ambiguous = []
for i, r in enumerate(rows, 1):
    body = r['부위']
    name = r['운동명']
    equipment = detect_equipment(name, body)
    category = detect_category(name, body)
    primary = detect_primary_muscle(name, body)
    secondary = detect_secondary(name, body, category)
    increment = detect_increment(equipment, body)
    rep_range = detect_rep_range(category, body)
    rest = detect_rest(category, body)
    difficulty = detect_difficulty(name, equipment, category, body)
    conf = confidence(equipment, category, primary)

    rec = {
        'ID': make_id(i),
        '부위': body,
        '운동명': name,
        '장비': equipment,
        '분류': category,
        '주동근': primary,
        '협동근': secondary,
        '권장 렙범위': rep_range,
        '휴식초': rest,
        '무게 단위': increment,
        '난이도': difficulty,
        '신뢰도': conf,
    }
    out_rows.append(rec)
    if conf == '낮음' or category == '추정' or equipment == '미분류':
        ambiguous.append((rec['ID'], body, name, equipment, category))

# 저장
fields = ['ID','부위','운동명','장비','분류','주동근','협동근',
          '권장 렙범위','휴식초','무게 단위','난이도','신뢰도']
with open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out_rows)

# 요약 리포트
print(f'→ {OUT} 생성: {len(out_rows)}행')
print(f'  필드: {fields}\n')

from collections import Counter
print('=== 장비 분포 ===')
for k, v in Counter(r['장비'] for r in out_rows).most_common():
    print(f'  {k:12s}: {v}')

print('\n=== 분류 분포 ===')
for k, v in Counter(r['분류'] for r in out_rows).most_common():
    print(f'  {k:12s}: {v}')

print('\n=== 난이도 분포 ===')
for k, v in Counter(r['난이도'] for r in out_rows).most_common():
    print(f'  {k:12s}: {v}')

print('\n=== 신뢰도 분포 ===')
for k, v in Counter(r['신뢰도'] for r in out_rows).most_common():
    print(f'  {k:12s}: {v}')

print(f'\n=== 사람 검토 필요 ({len(ambiguous)}개) ===')
for aid, body, name, eq, cat in ambiguous[:30]:
    print(f'  {aid} [{body}] {name}  → 장비={eq}, 분류={cat}')
if len(ambiguous) > 30:
    print(f'  ... 외 {len(ambiguous)-30}개')
