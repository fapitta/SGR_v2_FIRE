"""
AI 최적화 모듈 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_ai_simulation():
    """시뮬레이션 API 테스트"""
    print("\n" + "="*60)
    print("1. AI 시뮬레이션 테스트")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/ai_simulation")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 시뮬레이션 성공!")
        print(f"  최적 k: {data['optimal_k']}")
        print(f"  최적 j: {data['optimal_j']}")
        print(f"  평균 오차율: {data['mean_error']:.2f}%")
        print(f"\n  연도별 오차율:")
        for year, error in data['year_errors'].items():
            print(f"    {year}: {error:+.2f}%")
        return data
    else:
        print(f"✗ 시뮬레이션 실패: {response.status_code}")
        print(response.text)
        return None


def test_ai_optimization(sgr_results=None):
    """최적화 API 테스트"""
    print("\n" + "="*60)
    print("2. AI 최적화 테스트")
    print("="*60)
    
    if sgr_results is None:
        # 2026년 contract 시트의 실제 값 사용
        sgr_results = {
            '병원(계)': 2.0,
            '의원': 1.7,
            '치과(계)': 2.0,
            '한방(계)': 1.9,
            '약국': 3.3
        }
    
    payload = {
        'target_year': 2026,
        'sgr_results': sgr_results
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai_optimization",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 최적화 성공!")
        print(f"  최적 파라미터: k={data['optimal_k']}, j={data['optimal_j']}")
        print(f"\n  SGR 모형 입력:")
        for htype, rate in data['sgr_input'].items():
            print(f"    {htype}: {rate:.2f}%")
        print(f"\n  AI 최적화 결과:")
        for htype, rate in data['optimized_rates'].items():
            print(f"    {htype}: {rate:.2f}%")
        print(f"\n  제약 조건 충족: {'✓ 예' if data['constraints_satisfied'] else '✗ 아니오'}")
        return data
    else:
        print(f"✗ 최적화 실패: {response.status_code}")
        print(response.text)
        return None


def test_ai_full_report(sgr_results=None):
    """전체 리포트 API 테스트"""
    print("\n" + "="*60)
    print("3. AI 전체 리포트 테스트")
    print("="*60)
    
    payload = {
        'target_year': 2026,
        'sgr_results': sgr_results
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai_full_report",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 전체 리포트 생성 성공!")
        
        # 시뮬레이션 결과
        sim = data.get('simulation', {})
        print(f"\n  [시뮬레이션]")
        print(f"    최적 k: {sim.get('optimal_k')}")
        print(f"    최적 j: {sim.get('optimal_j')}")
        print(f"    평균 오차율: {sim.get('mean_error', 0):.2f}%")
        
        # 최적화 결과
        opt = data.get('optimization', {})
        print(f"\n  [최적화]")
        print(f"    목표 연도: {opt.get('year')}")
        if 'optimized_rates' in opt:
            print(f"    예측 수가 인상률:")
            for htype, rate in opt['optimized_rates'].items():
                print(f"      {htype}: {rate:.2f}%")
        
        return data
    else:
        print(f"✗ 전체 리포트 실패: {response.status_code}")
        print(response.text)
        return None


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*70)
    print("AI 최적화 API 테스트 시작")
    print("="*70)
    print("\n⚠ 주의: Flask 서버가 실행 중이어야 합니다!")
    print("  실행 명령: python 파이썬용_sgr_2027.py")
    
    try:
        # 서버 연결 확인
        response = requests.get(f"{BASE_URL}/")
        print(f"\n✓ 서버 연결 확인 완료")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ 서버에 연결할 수 없습니다. Flask 서버를 먼저 실행하세요.")
        return
    
    # 테스트 실행
    sim_result = test_ai_simulation()
    opt_result = test_ai_optimization()
    full_result = test_ai_full_report()
    
    # 결과 요약
    print("\n" + "="*70)
    print("테스트 결과 요약")
    print("="*70)
    print(f"  시뮬레이션: {'✓ 성공' if sim_result else '✗ 실패'}")
    print(f"  최적화: {'✓ 성공' if opt_result else '✗ 실패'}")
    print(f"  전체 리포트: {'✓ 성공' if full_result else '✗ 실패'}")
    
    # 결과 저장
    if full_result:
        with open('ai_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 전체 결과가 ai_test_results.json에 저장되었습니다.")
    
    print("\n" + "="*70)
    print("테스트 완료!")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
