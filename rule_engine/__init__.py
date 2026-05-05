"""SAiM 룰 엔진 — 두 가지 서비스의 진입점만 외부에 노출.

진입점:
    realtime_coaching(state)    실시간 코칭 (운동 중)
    recommend_routine(profile)  운동 루틴 추천 (프로그램 시작/주 단위)

진실의 원천: workout_knowledge_base.csv (153행) → rules/{ID}.yaml (153장)
이 패키지의 모든 함수는 위 카드에서 1:1로 파생된다. 추측 코드는 없고,
각 함수 docstring/주석에 출처(논문·매뉴얼·URL)와 신뢰도 별표를 명시한다.
"""

# 진입 함수는 lazy import — 모듈 빌드 중에는 import 실패 회피
def realtime_coaching(*args, **kwargs):
    from rule_engine.realtime_coaching import realtime_coaching as _impl
    return _impl(*args, **kwargs)


def recommend_routine(*args, **kwargs):
    from rule_engine.recommend_routine import recommend_routine as _impl
    return _impl(*args, **kwargs)


__all__ = ["realtime_coaching", "recommend_routine"]
