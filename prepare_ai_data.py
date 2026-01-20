"""
데이터 준비 스크립트
AI 최적화 모델을 위한 학습 데이터셋 준비
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


class AIDataPreparator:
    """AI 최적화를 위한 데이터 준비 클래스"""
    
    def __init__(self, file_path="SGR_data.xlsx"):
        self.file_path = file_path
        self.data = {}
        self.hospital_types = ['병원(계)', '의원', '치과(계)', '한방(계)', '약국']
        
    def load_all_data(self):
        """모든 필요한 데이터 로드"""
        print("Loading data from SGR_data.xlsx...")
        
        # 1. 수가계약 데이터 (핵심)
        self.data['contract'] = pd.read_excel(self.file_path, sheet_name='contract', index_col=0)
        print(f"✓ Contract data loaded: {self.data['contract'].shape}")
        
        # 2. 진료비 데이터
        self.data['expenditure'] = pd.read_excel(self.file_path, sheet_name='expenditure_real', index_col=0)
        print(f"✓ Expenditure data loaded: {self.data['expenditure'].shape}")
        
        # 3. CF (환산지수) 데이터
        self.data['cf'] = pd.read_excel(self.file_path, sheet_name='cf_t', index_col=0)
        print(f"✓ CF data loaded: {self.data['cf'].shape}")
        
        # 4. GDP 데이터
        self.data['gdp'] = pd.read_excel(self.file_path, sheet_name='GDP', index_col=0)
        print(f"✓ GDP data loaded: {self.data['gdp'].shape}")
        
        # 5. 인구 데이터
        self.data['pop'] = pd.read_excel(self.file_path, sheet_name='pop', index_col=0)
        print(f"✓ Population data loaded: {self.data['pop'].shape}")
        
        # 6. 상대가치점수 (RVS) 데이터
        self.data['rvs'] = pd.read_excel(self.file_path, sheet_name='rvs', index_col=0)
        print(f"✓ RVS data loaded: {self.data['rvs'].shape}")
        
        # 7. 법과 제도 지수
        self.data['law'] = pd.read_excel(self.file_path, sheet_name='law', index_col=0)
        print(f"✓ Law index data loaded: {self.data['law'].shape}")
        
        # 8. 재정 데이터
        self.data['finance'] = pd.read_excel(self.file_path, sheet_name='finance', index_col=0)
        print(f"✓ Finance data loaded: {self.data['finance'].shape}")
        
        return self.data
    
    def prepare_training_data(self, start_year=2021, end_year=2025):
        """학습용 데이터셋 준비 (2021-2025)"""
        training_data = []
        
        for year in range(start_year, end_year + 1):
            year_data = {
                'year': year,
                'rates': {},
                'budgets': {},
                'features': {}
            }
            
            # 수가 인상률
            for htype in self.hospital_types:
                col_name = f'인상율_{htype}'
                if col_name in self.data['contract'].columns:
                    year_data['rates'][htype] = float(self.data['contract'].loc[year, col_name])
            
            # 추가 소요 재정
            year_data['budgets']['전체'] = float(self.data['contract'].loc[year, '추가소요재정_전체'])
            for htype in self.hospital_types:
                col_name = f'추가소요재정_{htype}'
                if col_name in self.data['contract'].columns:
                    year_data['budgets'][htype] = float(self.data['contract'].loc[year, col_name])
            
            # 추가 특징 변수들
            # GDP
            if year in self.data['gdp'].index:
                year_data['features']['gdp_nominal'] = float(self.data['gdp'].loc[year, 'GDP(명목)']) if 'GDP(명목)' in self.data['gdp'].columns else None
                year_data['features']['gdp_per_capita'] = float(self.data['gdp'].loc[year, '1인당GDP(명목)']) if '1인당GDP(명목)' in self.data['gdp'].columns else None
            
            # 환산지수
            if year in self.data['cf'].index:
                for htype in self.hospital_types:
                    if htype in self.data['cf'].columns:
                        year_data['features'][f'cf_{htype}'] = float(self.data['cf'].loc[year, htype])
            
            # 진료비
            if year in self.data['expenditure'].index:
                for htype in self.hospital_types:
                    if htype in self.data['expenditure'].columns:
                        year_data['features'][f'expenditure_{htype}'] = float(self.data['expenditure'].loc[year, htype])
            
            # 상대가치점수
            if year in self.data['rvs'].index:
                for htype in self.hospital_types:
                    if htype in self.data['rvs'].columns:
                        year_data['features'][f'rvs_{htype}'] = float(self.data['rvs'].loc[year, htype])
            
            training_data.append(year_data)
        
        return training_data
    
    def calculate_budget_shares(self, start_year=2021, end_year=2025):
        """유형별 추가소요재정 점유율 계산"""
        shares = {htype: [] for htype in self.hospital_types}
        
        for year in range(start_year, end_year + 1):
            total_budget = self.data['contract'].loc[year, '추가소요재정_전체']
            for htype in self.hospital_types:
                col_name = f'추가소요재정_{htype}'
                if col_name in self.data['contract'].columns:
                    budget = self.data['contract'].loc[year, col_name]
                    share = (budget / total_budget) * 100
                    shares[htype].append(share)
        
        # 평균 점유율 계산
        avg_shares = {htype: np.mean(shares[htype]) for htype in self.hospital_types}
        
        return avg_shares, shares
    
    def calculate_budget_growth_rates(self, start_year=2021, end_year=2025):
        """추가소요재정 증가율 계산"""
        growth_rates = []
        
        for year in range(start_year + 1, end_year + 1):
            prev_budget = self.data['contract'].loc[year - 1, '추가소요재정_전체']
            curr_budget = self.data['contract'].loc[year, '추가소요재정_전체']
            growth_rate = ((curr_budget - prev_budget) / prev_budget) * 100
            growth_rates.append(growth_rate)
        
        avg_growth_rate = np.mean(growth_rates)
        
        return avg_growth_rate, growth_rates
    
    def get_sgr_ranks_from_dashboard(self):
        """
        대시보드에서 SGR 모형 순위 정보 추출
        Note: 실제로는 파이썬용_sgr_2027.py를 실행하여 얻은 결과를 사용해야 함
        여기서는 임시로 2026년 예측을 위한 플레이스홀더
        """
        # 이 부분은 실제 SGR 모형 실행 결과에서 가져와야 함
        # 임시로 반환 구조만 정의
        return {
            'year': 2026,
            'ranks': {},  # {유형: 순위} 형태로 채워져야 함
            'values': {}  # {유형: SGR 조정률} 형태로 채워져야 함
        }
    
    def save_to_json(self, data, filename="ai_training_data.json"):
        """데이터를 JSON 파일로 저장"""
        output_path = Path(filename)
        
        # NumPy 타입을 Python 기본 타입으로 변환
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            else:
                return obj
        
        data_converted = convert_types(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_converted, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Data saved to {output_path}")
        return output_path
    
    def generate_full_dataset(self):
        """전체 데이터셋 생성"""
        print("\n" + "="*60)
        print("AI 최적화를 위한 데이터셋 생성")
        print("="*60 + "\n")
        
        # 데이터 로드
        self.load_all_data()
        
        # 학습 데이터 준비
        print("\nPreparing training data (2021-2025)...")
        training_data = self.prepare_training_data(2021, 2025)
        print(f"✓ Training data prepared: {len(training_data)} years")
        
        # 추가소요재정 점유율
        print("\nCalculating budget shares...")
        avg_shares, yearly_shares = self.calculate_budget_shares(2021, 2025)
        print(f"✓ Average budget shares calculated")
        for htype, share in avg_shares.items():
            print(f"  - {htype}: {share:.2f}%")
        
        # 추가소요재정 증가율
        print("\nCalculating budget growth rates...")
        avg_growth, yearly_growth = self.calculate_budget_growth_rates(2021, 2025)
        print(f"✓ Average growth rate: {avg_growth:.2f}%")
        print(f"  Yearly rates: {[f'{g:.2f}%' for g in yearly_growth]}")
        
        # 전체 데이터셋 구성
        full_dataset = {
            'metadata': {
                'created_at': pd.Timestamp.now().isoformat(),
                'training_period': '2021-2025',
                'target_year': 2026,
                'hospital_types': self.hospital_types
            },
            'training_data': training_data,
            'statistics': {
                'avg_budget_shares': avg_shares,
                'yearly_budget_shares': yearly_shares,
                'avg_budget_growth_rate': avg_growth,
                'yearly_budget_growth_rates': yearly_growth
            },
            'constraints': {
                'rate_ranges': {
                    'all_types': {'min': 1.5, 'max': 3.6},
                    '병원(계)': {'min': 1.8, 'max': 2.2},
                    '약국': {'min': 2.9, 'max': 3.6, 'target': 3.4}
                },
                'gap_constraints': {
                    'clinic_group_max_gap': 0.5,  # 치과, 한방, 의원 상호 격차
                    'type_diff_range': {'min': 0.7, 'max': 2.1}
                },
                'target_avg_rate': 1.56
            }
        }
        
        # JSON 저장
        self.save_to_json(full_dataset, "ai_training_data.json")
        
        print("\n" + "="*60)
        print("데이터셋 생성 완료!")
        print("="*60)
        
        return full_dataset


if __name__ == "__main__":
    preparator = AIDataPreparator("SGR_data.xlsx")
    dataset = preparator.generate_full_dataset()
    
    print("\n\n데이터셋 요약:")
    print(f"- 학습 데이터: {len(dataset['training_data'])}년치")
    print(f"- 병원 유형: {len(dataset['metadata']['hospital_types'])}개")
    print(f"- 평균 추가소요재정 증가율: {dataset['statistics']['avg_budget_growth_rate']:.2f}%")
