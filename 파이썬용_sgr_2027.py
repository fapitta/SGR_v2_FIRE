import pandas as pd
import numpy as np
import warnings
from flask import Flask, render_template, request, send_file, jsonify
import io
import os
import datetime
from openpyxl import load_workbook

# 경고 무시 설정
warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------
# 1. 데이터 로드 및 전처리 클래스 (Advanced DataProcessor)
# ----------------------------------------------------------------------

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.GROUP_MAPPING = {
            '병원(계)': ['상급종합', '종합병원', '병원', '요양병원'], '의원(계)': ['의원'],
            '치과(계)': ['치과병원', '치과의원'], '한방(계)': ['한방병원', '한의원'], '약국(계)': ['약국']
        }
        self.raw_data = self._load_data()
        self.HOSPITAL_TYPES = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']

    def _load_sheet(self, sheet_name, index_col=0, filter_years=False):
        try:
            # Load data without setting index initially to find potential 'Time'/'Year' columns securely
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, index_col=None)
            
            # Set Index Logic
            if filter_years:
                # Priority: '연도' column -> 'Year' column -> 1st column
                target_col = None
                if '연도' in df.columns:
                    target_col = '연도'
                elif 'Year' in df.columns:
                    target_col = 'Year'
                else:
                    target_col = df.columns[0]
                
                df = df.set_index(target_col)
                
                # Robust filtering for Years
                # Force index to numeric, turn errors to NaN
                df.index = pd.to_numeric(df.index, errors='coerce')
                # Drop rows where index is NaN (e.g. string headers, empty rows)
                df = df[df.index.notna()]
                # Convert to integer and filter
                df.index = df.index.astype(int)
                df = df[df.index > 1990]
            else:
                # For non-time-series (like weights), use standard index_col=0 behavior
                if not df.empty and len(df.columns) > 0:
                     df = df.set_index(df.columns[0])

            # Clean columns and index to prevent whitespace issues
            df.columns = [str(c).strip() for c in df.columns]
            if df.index.dtype == 'object':
                df.index = [str(i).strip() if isinstance(i, str) else i for i in df.index]

            return df.apply(pd.to_numeric, errors='coerce')
        except Exception as e:
            print(f"Sheet {sheet_name} load warning: {e}")
            return pd.DataFrame()

    def _load_data(self):
        try:
            # Check if file exists first to avoid confusing errors
            if not os.path.exists(self.file_path):
                 raise FileNotFoundError(f"File not found: {self.file_path}")

            # Load into temp dictionary
            new_data = {
                'df_expenditure': self._load_sheet('expenditure_real', filter_years=True),
                'df_weights': self._load_sheet('cost_structure').T,
                'df_raw_mei_inf': self._load_sheet('factor_pd', filter_years=True),
                'df_gdp': self._load_sheet('GDP', filter_years=True),
                'df_pop': self._load_sheet('pop', filter_years=True),
                'df_sgr_reval': self._load_sheet('cf_t', filter_years=True),
                'df_sgr_law': self._load_sheet('law', filter_years=True),
                'df_rel_value': self._load_sheet('rvs', filter_years=True)
            }
            
            # Integrity Check: Validation of Critical Data
            if new_data['df_expenditure'].empty:
                raise ValueError("Critical Validation Error: 'expenditure_real' sheet is empty or failed to load.")
            
            return new_data
        except Exception as e:
            print(f"❌ 데이터 로드 치명적 오류: {e}")
            raise e

    def reload_data(self):
        """Force reload data from Excel file (SAFE RELOAD)"""
        print(f"[INFO] Reloading data from {self.file_path}...")
        try:
            temp_data = self._load_data()
            self.raw_data = temp_data
            print("[SUCCESS] Data reloaded successfully.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to reload data (keeping previous state): {e}")
            # Do NOT update self.raw_data if reload fails
            return False

    def save_overrides_to_excel(self, overrides, mode='final'):
        """
        Save user overrides back to the Excel file using openpyxl to preserve formatting.
        overrides: dict of {key: value} where key is like '병원_2025', 'I1_2025', etc.
        """
        try:
            target_path = self.file_path
            if mode == 'temp':
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = os.path.join(os.path.dirname(self.file_path), f"SGR_data_임시_{timestamp}.xlsx")

            wb = load_workbook(self.file_path)
            
            # Helper to find column index by header name
            def get_col_idx(ws, header_name, header_row=1):
                for cell in ws[header_row]:
                    if cell.value == header_name:
                        return cell.column
                return None

            # Helper to find row index by year (mostly in column 1)
            def get_row_idx_by_year(ws, year, year_col=1):
                for row in ws.iter_rows(min_row=2, max_col=year_col): # Assuming year is in first few columns
                    cell = row[year_col-1]
                    if cell.value == int(year) or str(cell.value) == str(year):
                        return cell.row
                return None

            # Mapping Logic
            # Key prefixes/patterns -> Sheet Name, Column Name mapping
            # This logic needs to match _apply_overrides reversed
            
            updates_count = 0
            
            for key, value in overrides.items():
                try:
                    sheet_name = None
                    row_key = None # Year or Row Name
                    col_name = None
                    
                    if '_' not in key: continue

                    # 1. Weights: WEIGHT_{TYPE}_{COL}
                    if key.startswith('WEIGHT_'):
                        parts = key.split('_') # WEIGHT, 병원, 인건비
                        if len(parts) == 3:
                            sheet_name = 'cost_structure'
                            row_key = parts[1] # 병원
                            col_name = parts[2] # 인건비 (Header)
                            # For weights, rows are Types, Col is Category
                            # This sheet usually has Type in Col A?
                            # Let's check logic: _load_sheet('cost_structure').T
                            # This means original sheet has Types as Columns probably? Or Types as Rows?
                            # If we transposed it (.T), then originally:
                            # If Types are indices in DF, then in Excel they are likely in the first column?
                            # Wait, 'cost_structure' usually is small. 
                            # Let's assume standard format: Row=Type, Col=Component OR Row=Component, Col=Type
                            # self._load_sheet('cost_structure') -> index_col=0. 
                            # If .T makes Types indices, then originally Types were Columns.
                            # So Sheet: Rows=Components(Index), Cols=Types.
                            # So we search Col = matching Type. Row = matching Component ('인건비').
                            pass # Logic handled below specially for weights

                    else:
                        # Standard Time Series: FIELD_YEAR
                        field, year = key.rsplit('_', 1)
                        if not year.isdigit(): continue # Skip if not a year-based key
                        year = int(year)
                        row_key = year
                        
                        # MEI
                        if field in ['I1', 'I2', 'I3', 'M1', 'M2', 'Z1', 'Z2']:
                            sheet_name = 'factor_pd'
                            col_map = {'I':'인건비','M':'관리비','Z':'재료비'}
                            col_name = f"{col_map[field[0]]}_{field[1]}"
                        
                        # GDP
                        elif field == 'GDP':
                            sheet_name = 'GDP'
                            col_name = '실질GDP'
                        elif field == 'POP':
                            sheet_name = 'GDP'
                            col_name = '영안인구'
                        
                        # Population
                        elif field == 'NHI_POP':
                            sheet_name = 'pop'
                            # In pop sheet, we might have basic or aged. 
                            # Front end sends 'NHI_POP' for 'basic'. 
                            # Is there 'aged'? user input only mapped 'basic' to NHI_POP_xxx so far in my js?
                            # Ah, js: if (item.key === 'basic') allOverrides[`NHI_POP_${year}`]...
                            # I didn't verify if I added overrides for 'aged'.
                            # In main.js saveAllToExcelFile loop: if (userData.population[year].basic !== undefined) ...
                            # It seems I only supported basic there.
                            col_name = '건보대상자수'

                        # Law
                        elif field.startswith('LAW_') or field == 'LAW':
                             sheet_name = 'law'
                             # Parse type if present
                             parts = field.split('_') # LAW, 병원
                             if len(parts) == 2:
                                 col_name = parts[1] # htype
                             else:
                                 # Fallback if no type? 
                                 pass

                        # RV
                        elif field.startswith('RV_') or field == 'RV':
                             sheet_name = 'rvs'
                             parts = field.split('_')
                             if len(parts) == 2:
                                 col_name = parts[1] # htype

                        # Medical
                        elif field in self.HOSPITAL_TYPES:
                            sheet_name = 'expenditure_real'
                            col_name = field
                        
                        # CF
                        elif field.startswith('CF_') and field[3:] in self.HOSPITAL_TYPES:
                            sheet_name = 'cf_t'
                            col_name = field[3:]

                    # --- EXECUTE UPDATE ---
                    if sheet_name and sheet_name in wb.sheetnames:
                        ws = wb[sheet_name]
                        # 1. Find Column
                        target_col_idx = get_col_idx(ws, col_name)
                        
                        # 2. Find Row
                        target_row_idx = None
                        if sheet_name == 'cost_structure':
                             # Special handling for weights
                             # Weights logic: Row=Component('인건비'..), Col=Type ? Or vice versa?
                             # In `_load_sheet`: `df_weights = self._load_sheet('cost_structure').T`
                             # The `.T` implies the excel has Types as Columns (and Components as Rows).
                             # So we look for Col = Type (row_key), Row = Component (col_name)
                             # row_key was parts[1] (Type), col_name was parts[2] (Component)
                             # Excel: Headers are Types?
                             target_col_idx = get_col_idx(ws, row_key) # Type
                             # Find row for component
                             for r in range(1, 20): # Scan first 20 rows
                                 if ws.cell(row=r, column=1).value == col_name:
                                     target_row_idx = r
                                     break
                        else:
                             # Standard Time Series
                             target_row_idx = get_row_idx_by_year(ws, row_key)

                        if target_row_idx and target_col_idx:
                            ws.cell(row=target_row_idx, column=target_col_idx).value = float(value)
                            updates_count += 1
                
                except Exception as loop_e:
                    print(f"Error updating key {key}: {loop_e}")
                    continue
            
            wb.save(target_path)
            print(f"[SUCCESS] Saved {updates_count} changes to {target_path}.")
            
            # Only reload data and return special msg if final save
            if mode == 'final':
                self.reload_data()
                return True, f"{updates_count}개 항목 원본 업데이트 성공"
            else:
                return True, f"임시 파일 저장 성공: {os.path.basename(target_path)}"

        except Exception as e:
            print(f"[ERROR] Save to Excel failed: {e}")
            return False, str(e)

# ----------------------------------------------------------------------
# 2. 통합 산출 엔진 (CalculationEngine)
# ----------------------------------------------------------------------

# ... (MeiCalculator, SgrCalculator skipped for brevity) ...

class CalculationEngine:
    def run_full_analysis(self, target_year=2025):
        # 2014년부터 2028년까지 분석 (사용자 요청: 2010-2013 제외)
        years = range(2014, 2029) 
        print(f"[INFO] Analysis Range (Calculated): {list(years)}")
        history = {
            'years': list(years), 
            'S1': {}, 'S2': {}, 'Link': {}, 'MEI': {}, 'GDP': {}, 
            'UAF_S1': {}, 'UAF_S2': {},
            'SGR_S1_INDEX': {}, 'SGR_S2_INDEX': {},
            'Target_S1': {}, 'Target_S2': {}
        }
        details = {'mei_raw': {}, 'sgr_factors': {}}
        
        # Additional bulk data for 2020-2026 comparison
        bulk_sgr = {
            'reval_rates': {}, 'pop_growth': {}, 'law_changes': {}, 
            'gdp_growth': {}, 'scenario_adjustments': {}
        }

        # Key Mapping for MEI display (Match Frontend Keys)
        key_map = {
            '병원': '병원(계)', '의원': '의원(계)', '치과': '치과(계)', 
            '한방': '한방(계)', '약국': '약국(계)'
        }

        for y in years:
            df_mei = self.mei_calc.calc_mei_index_by_year(y)
            if df_mei is not None:
                # Rename indices to match frontend expected keys (with suffix)
                df_renamed = df_mei.rename(index=key_map)
                details['mei_raw'][y] = (df_renamed.round(4)).to_dict()

# ----------------------------------------------------------------------
# 2. 통합 산출 엔진 (CalculationEngine)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 2. 산출 엔진 (MeiCalculator, SgrCalculator, CalculationEngine)
# ----------------------------------------------------------------------

class MeiCalculator:
    def __init__(self, data, hospital_types):
        self.data = data
        self.hospital_types = hospital_types

    def calc_mei_index_by_year(self, target_year):
        # target_year 환산지수를 위해 T-2년(target_year-2) MEI를 산출
        calc_year = target_year - 2
        df_inf = self.data['df_raw_mei_inf']
        df_weights = self.data['df_weights']
        
        try:
            I_types = [c for c in df_inf.columns if '인건비' in c] # 인건비_1, 2, 3
            # 인건비 지수는 최근 3개년 연평균 증가율 적용
            # 2014년 기준 calc_year=2012년인 경우 2009년 데이터가 필요함.
            # 데이터가 2010년부터 있다면 2013년부터 3년 평균 가능.
            # 2012년의 경우 2010~2012 (2년) 또는 1년치만 사용할 수 있도록 예외처리
            try:
                base_year = calc_year - 3
                if base_year not in df_inf.index:
                    base_year = max(df_inf.index.min(), 2010)
                
                years_diff = calc_year - base_year
                if years_diff <= 0:
                    labor_rates = pd.Series(1.0, index=I_types)
                else:
                    labor_rates = (df_inf.loc[calc_year, I_types] / df_inf.loc[base_year, I_types])**(1/years_diff)
            except:
                labor_rates = pd.Series(1.0, index=I_types)
            
            non_I_types = [c for c in df_inf.columns if '관리비' in c or '재료비' in c]
            try:
                raw_rates = df_inf.loc[calc_year, non_I_types] / df_inf.loc[calc_year-1, non_I_types]
            except:
                raw_rates = pd.Series(1.0, index=non_I_types)
            
            M_types = [c for c in raw_rates.index if '관리비' in c]
            Z_types = [c for c in raw_rates.index if '재료비' in c]
            
            results = {}
            for i_t in I_types:
                for m_t in M_types:
                    for z_t in Z_types:
                        name = f"I{i_t.split('_')[-1]}M{m_t.split('_')[-1]}Z{z_t.split('_')[-1]}"
                        # Ensure we only use the specified hospital types and match the names exactly
                        w_l = df_weights['인건비'].reindex(self.hospital_types).fillna(0)
                        w_m = df_weights['관리비'].reindex(self.hospital_types).fillna(0)
                        w_z = df_weights['재료비'].reindex(self.hospital_types).fillna(0)
                        
                        results[name] = (w_l * labor_rates[i_t] + 
                                       w_m * raw_rates[m_t] + 
                                       w_z * raw_rates[z_t])
            
            df = pd.DataFrame(results)
            df_final = pd.concat([df, pd.DataFrame({
                '평균': df.mean(axis=1), '최대': df.max(axis=1), 
                '최소': df.min(axis=1), '중위수': df.median(axis=1)
            })], axis=1)
            return df_final
        except Exception as e:
            print(f"MEI 산출 중 오류 ({target_year}): {e}")
            return None

class SgrCalculator:
    def __init__(self, data, hospital_types, group_mapping=None):
        self.data = data
        self.hospital_types = hospital_types
        self.group_mapping = group_mapping or {}

    def _safe_get(self, df, year, col=None):
        try:
            y = max(df.index.min(), min(year, df.index.max()))
            if col: return df.loc[y, col]
            return df.loc[y]
        except: 
            return 1.0

    def _calc_sgr_components(self, year):
        try:
            gdp, pop, law, reval = self.data['df_gdp'], self.data['df_pop'], self.data['df_sgr_law'], self.data['df_sgr_reval']
            exp = self.data['df_expenditure']
            
            # Global (SGR uses per-capita GDP)
            denom = self._safe_get(gdp, year-1, '실질GDP') / self._safe_get(gdp, year-1, '영안인구')
            num = self._safe_get(gdp, year, '실질GDP') / self._safe_get(gdp, year, '영안인구')
            g_s1 = num / denom
            p_s1 = self._safe_get(pop, year, '건보대상자수') / self._safe_get(pop, year-1, '건보대상자수')
            g_s2 = 1 + (g_s1 - 1) * 0.8
            p_col_s2 = '건보_고령화반영후(대상자수)' if '건보_고령화반영후(대상자수)' in pop.columns else '건보대상자수'
            p_s2 = self._safe_get(pop, year, p_col_s2) / self._safe_get(pop, year-1, '건보대상자수')
            
            # Type Specific
            l = self._safe_get(law, year)
            r = self._safe_get(reval, year) / self._safe_get(reval, year-1)
            
            # Add Groups
            w_year = year - 2
            if w_year in exp.index:
                ae_w = exp.loc[w_year]
                for g, members in self.group_mapping.items():
                    valid = [m for m in members if m in l.index and m in ae_w.index]
                    if valid:
                        weights = ae_w[valid] / ae_w[valid].sum()
                        l[g] = (l[valid] * weights).sum()
                        r[g] = (r[valid] * weights).sum()
            
            return {'g_s1': g_s1, 'p_s1': p_s1, 'g_s2': g_s2, 'p_s2': p_s2, 'l': l, 'r': r}
        except: return None

    def calc_sgr_index(self, components, model='S1'):
        if not components: return pd.Series(1.0, index=self.hospital_types + list(self.group_mapping.keys()))
        g = components['g_s1'] if model == 'S1' else components['g_s2']
        p = components['p_s1'] if model == 'S1' else components['p_s2']
        return g * p * components['l'] * components['r']

    def calc_paf_s1(self, target_year):
        ae_actual = self.data['df_expenditure']
        types_all = self.hospital_types + list(self.group_mapping.keys())
        
        # 1. Individual components
        y_recent = target_year - 2
        c_recent = self._calc_sgr_components(y_recent)
        idx_recent = self.calc_sgr_index(c_recent, model='S1')
        
        ae_22 = self._safe_get(ae_actual, y_recent-1)
        ae_23 = self._safe_get(ae_actual, y_recent)
        tge_recent = ae_22 * idx_recent
        
        # 2. Accumulation Loop
        y_start, y_end = target_year-11, target_year-2
        sums_tge = pd.Series(0.0, index=types_all)
        sums_ae = pd.Series(0.0, index=types_all)
        
        for y in range(y_start, y_end + 1):
            c = self._calc_sgr_components(y)
            idx = self.calc_sgr_index(c, model='S1')
            a_prev = self._safe_get(ae_actual, y-1)
            a_curr = self._safe_get(ae_actual, y)
            
            # For individuals
            for t in self.hospital_types:
                sums_tge[t] += a_prev[t] * idx[t]
                sums_ae[t] += a_curr[t]
            
            # Aggregates for groups
            for g, members in self.group_mapping.items():
                sums_tge[g] += sum([a_prev[m] * idx[m] for m in members if m in a_prev.index])
                sums_ae[g] += sum([a_curr[m] for m in members if m in a_curr.index])

        # 3. Denominators
        c_24 = self._calc_sgr_components(target_year-1)
        idx_24 = self.calc_sgr_index(c_24, model='S1')
        denoms = pd.Series(0.0, index=types_all)
        
        for t in self.hospital_types:
            denoms[t] = ae_23[t] * (1 + idx_24[t])
            
        for g, members in self.group_mapping.items():
             denoms[g] = sum([ae_23[m] * (1 + idx_24[m]) for m in members if m in ae_23.index])

        # 4. Final UAF
        # Short Term Gap
        # For groups, GapShort must also use Aggregate
        gap_short = pd.Series(0.0, index=types_all)
        for t in self.hospital_types:
            gap_short[t] = (tge_recent[t] - ae_23[t]) / ae_23[t]
        
        for g, members in self.group_mapping.items():
            agg_tge = sum([ae_22[m] * idx_recent[m] for m in members if m in ae_22.index])
            agg_ae = sum([ae_23[m] for m in members if m in ae_23.index])
            gap_short[g] = (agg_tge - agg_ae) / agg_ae

        gap_accum = (sums_tge - sums_ae) / denoms
        uaf = gap_short * 0.75 + gap_accum * 0.33
        return uaf

    def calc_paf_s2(self, target_year):
        # S2 usually follows similar aggregate logic for groups
        ae_actual = self.data['df_expenditure']
        types_all = self.hospital_types + list(self.group_mapping.keys())
        
        # We'll calculate weighted average of gaps for S2 or Aggregate Ratio?
        # Given S1 correction, Aggregate Ratio is safer.
        group_pafs = pd.Series(0.0, index=types_all)
        
        for lag, weight in [(2, 0.5), (3, 0.3), (4, 0.2)]:
            y = target_year - lag
            c = self._calc_sgr_components(y)
            idx = self.calc_sgr_index(c, model='S2')
            
            ae_prev = self._safe_get(ae_actual, y-1)
            ae_curr = self._safe_get(ae_actual, y)
            
            term_gaps = pd.Series(0.0, index=types_all)
            for t in self.hospital_types:
                tge = ae_prev[t] * idx[t]
                term_gaps[t] = (tge - ae_curr[t]) / ae_curr[t]
                
            for g, members in self.group_mapping.items():
                agg_t = sum([ae_prev[m] * idx[m] for m in members if m in ae_prev.index])
                agg_a = sum([ae_curr[m] for m in members if m in ae_curr.index])
                term_gaps[g] = (agg_t - agg_a) / agg_a
                
            group_pafs += term_gaps * weight
            
        return group_pafs

class CalculationEngine:
    def __init__(self, baseline_data, overrides=None):
        self.HOSPITAL_TYPES = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
        self.GROUP_MAPPING = {
            '병원(계)': ['상급종합', '종합병원', '병원', '요양병원'], '의원(계)': ['의원'],
            '치과(계)': ['치과병원', '치과의원'], '한방(계)': ['한방병원', '한의원'], '약국(계)': ['약국']
        }
        self.data = self._apply_overrides(baseline_data, overrides)
        self.mei_calc = MeiCalculator(self.data, self.HOSPITAL_TYPES)
        # Pass group mapping to sgr_calc
        self.sgr_calc = SgrCalculator(self.data, self.HOSPITAL_TYPES, self.GROUP_MAPPING)

    def _apply_overrides(self, baseline, overrides):
        if not overrides: return baseline
        new_data = {k: v.copy() for k, v in baseline.items()}
        
        # Generic override injection for any year present in the overrides keys
        # Format expected: FIELD_YEAR (e.g., I1_2025, GDP_2024, etc.)
        for key, value in overrides.items():
            try:
                if '_' not in key: continue
                
                # Handling WEIGHT overrides (WEIGHT_{TYPE}_{COL})
                if key.startswith('WEIGHT_'):
                    parts = key.split('_')
                    if len(parts) == 3:
                        _, htype, col = parts
                        if htype in self.HOSPITAL_TYPES and col in ['인건비', '관리비', '재료비']:
                            new_data['df_weights'].loc[htype, col] = float(value)
                    continue

                field, year = key.rsplit('_', 1)
                year = int(year)
                
                # MEI Inflation
                if field in ['I1', 'I2', 'I3', 'M1', 'M2', 'Z1', 'Z2']:
                    col_map = {'I':'인건비','M':'관리비','Z':'재료비'}
                    col_name = f"{col_map[field[0]]}_{field[1]}"
                    if year in new_data['df_raw_mei_inf'].index:
                        new_data['df_raw_mei_inf'].loc[year, col_name] = float(value)
                
                # Macro Factors
                elif field == 'GDP':
                    new_data['df_gdp'].loc[year, '실질GDP'] = float(value)
                elif field == 'POP':
                    new_data['df_gdp'].loc[year, '영안인구'] = float(value)
                elif field == 'NHI_POP':
                    new_data['df_pop'].loc[year, '건보대상자수'] = float(value)
                
                # Law & RV (Type-specific)
                elif field.startswith('LAW_'):
                    parts = field.split('_')
                    if len(parts) == 2:
                        htype = parts[1]
                        if year in new_data['df_sgr_law'].index:
                            new_data['df_sgr_law'].loc[year, htype] = float(value)
                
                elif field.startswith('RV_'):
                    parts = field.split('_')
                    if len(parts) == 2:
                        htype = parts[1]
                        if year in new_data['df_rel_value'].index:
                            new_data['df_rel_value'].loc[year, htype] = float(value)

                elif field == 'LAW':
                    new_data['df_sgr_law'].loc[year] = float(value)
                elif field == 'RV':
                    # Relative value usually affects T-2 for CF calculation
                    if (year-2) in new_data['df_rel_value'].index:
                        new_data['df_rel_value'].loc[year-2] = 1 + float(value)/100

                # Medical Expenditure (Direct overrides)
                elif field in self.HOSPITAL_TYPES:
                    if year in new_data['df_expenditure'].index:
                        new_data['df_expenditure'].loc[year, field] = float(value)
                
                # CF Revaluation
                elif field.startswith('CF_') and field[3:] in self.HOSPITAL_TYPES:
                    actual_field = field[3:]
                    if year in new_data['df_sgr_reval'].index:
                        new_data['df_sgr_reval'].loc[year, actual_field] = float(value)

            except Exception as e:
                print(f"Override error for {key}: {e}")
                continue
                
        return new_data

    def calc_group_average(self, df_values, target_year):
        weight_year = target_year - 2
        try: exp = self.data['df_expenditure'].loc[weight_year]
        except: return pd.Series(np.nan, index=list(self.GROUP_MAPPING.keys())+['전체'])

        results = {}
        for group, members in self.GROUP_MAPPING.items():
            valid = [m for m in members if m in df_values.index and m in exp.index]
            if not valid: continue
            w = exp.loc[valid] / exp.loc[valid].sum()
            results[group] = (df_values.loc[valid] * w).sum()
        
        all_m = [m for sub in self.GROUP_MAPPING.values() for m in sub if m in df_values.index]
        w_all = exp.loc[all_m] / exp.loc[all_m].sum()
        results['전체'] = (df_values.loc[all_m] * w_all).sum()
        return pd.Series(results)

    def run_full_analysis(self, target_year=2025):
        # 2014년부터 2028년까지 분석 (사용자 요청: 2010-2013 제외)
        years = range(2014, 2029) 
        print(f"[INFO] Analysis Range (Calculated): {list(years)}")
        history = {
            'years': list(years), 
            'S1': {}, 'S2': {}, 'Link': {}, 'MEI': {}, 'GDP': {}, 
            'UAF_S1': {}, 'UAF_S2': {},
            'SGR_S1_INDEX': {}, 'SGR_S2_INDEX': {},
            'Target_S1': {}, 'Target_S2': {}
        }
        details = {'mei_raw': {}, 'sgr_factors': {}}
        
        # Additional bulk data for 2020-2026 comparison
        bulk_sgr = {
            'reval_rates': {}, # 환산지수 변화율 (Index)
            'reval_growth': {}, # 환산지수 변화율 (%)
            'pop_growth': {},  # 인구증가율 (s1, s2)
            'law_changes': {}, # 법과제도
            'gdp_growth': {},   # GDP 증가율 (s1, s2, total)
            'mei_growth': {},   # MEI 증가율 (%)
            'factor_growth': {}, # 생산요소 물가 증가율
            'scenario_adjustments': {}, # 16가지 시나리오별 조정률
            'ar_analysis': {} # AR모형 시나리오 분석 (30개)
        }
        
        # Helper: Combined for UAF (Rates) - already includes group results in the Series
        def get_rate_combined(rates):
            # rates is a Series indexed by both individuals and groups
            # Increase precision to 3 decimal places as requested
            return (rates * 100).round(3).to_dict()


        # Helper: Combined for generic values (MEI, etc) - still using AE weights for averages
        def get_combined(values, year):
            indiv = ((values[self.HOSPITAL_TYPES] - 1) * 100).round(2)
            groups = ((self.calc_group_average(values[self.HOSPITAL_TYPES], year) - 1) * 100).round(2)
            return {**indiv.to_dict(), **groups.to_dict()}

        # Helper: Indices (1.xxxx)
        def get_combined_index(values, year):
            indiv = values[self.HOSPITAL_TYPES].round(4)
            groups = self.calc_group_average(values[self.HOSPITAL_TYPES], year).round(4)
            return {**indiv.to_dict(), **groups.to_dict()}

        # Helper: Absolute (Target expenditures) - Sum for groups
        def get_combined_absolute(values, year):
            indiv = values[self.HOSPITAL_TYPES]
            results = {}
            for g, members in self.GROUP_MAPPING.items():
                results[g] = values[members].sum() if all(m in values.index for m in members) else 0
            results['전체'] = values[self.HOSPITAL_TYPES].sum()
            return {**indiv.round(0).to_dict(), **results}

        for y in years:
            # Initialize for safety (prevent JS error on frontend if calc fails)
            # 1. Initialize for the year y
            for k in ['S1', 'S2', 'Link', 'MEI', 'GDP', 'UAF_S1', 'UAF_S2', 'SGR_S1_INDEX', 'SGR_S2_INDEX', 'Target_S1', 'Target_S2']:
                history[k][y] = {}

            # 2. Base MEI Calculation (Current Year y gets T-2 data)
            df_mei = None
            mei_avg = None
            try:
                df_mei = self.mei_calc.calc_mei_index_by_year(y)
                if df_mei is not None:
                    details['mei_raw'][y] = df_mei.round(4).to_dict()
                    mei_avg = df_mei['평균']
            except Exception as e:
                print(f"[WARN] MEI calc failed for {y}: {e}")

            # 3. SGR Standard (S1) and Improved (S2) - FULL REVERT
            uaf_s1 = None
            uaf_s2 = None
            try:
                uaf_s1 = self.sgr_calc.calc_paf_s1(y)
                uaf_s2 = self.sgr_calc.calc_paf_s2(y)
                
                if mei_avg is not None:
                    if uaf_s1 is not None:
                        history['UAF_S1'][y] = get_rate_combined(uaf_s1)
                        cf_s1_idx = mei_avg * (1 + uaf_s1[self.HOSPITAL_TYPES])
                        history['S1'][y] = get_combined(cf_s1_idx, y)
                    
                    if uaf_s2 is not None:
                        history['UAF_S2'][y] = get_rate_combined(uaf_s2)
                        cf_s2_idx = mei_avg * (1 + uaf_s2[self.HOSPITAL_TYPES])
                        history['S2'][y] = get_combined(cf_s2_idx, y) # NO RV Deduction for SGR as requested
            except Exception as e:
                print(f"[WARN] SGR S1/S2 calc failed for {y}: {e}")

            # 4. Macro Indicator Models (GDP, MEI, Link) - Apply Simple Subtraction
            # [USER REQUEST] 2025 adjustment = (Indicator Index - RV Index) * 100
            # 복잡한 연산 없이 이미 산출된 지수 간의 차이만 가져와서 %로 표시 (매우 단순화)
            calc_year = y - 2
            try:
                # Get RV Index (Default: 1.0)
                rv_file = self.data['df_rel_value']
                rv_idx = pd.Series(1.0, index=self.HOSPITAL_TYPES)
                if calc_year in rv_file.index:
                    rv_idx = rv_file.loc[calc_year].reindex(self.HOSPITAL_TYPES).fillna(1.0)

                # 1. GDP Model
                gdp_file = self.data['df_gdp']
                g_idx = self.sgr_calc._safe_get(gdp_file, calc_year, '실질GDP') / self.sgr_calc._safe_get(gdp_file, calc_year-1, '실질GDP')
                
                # GDP Adjustment (%) = (GDP Index - RV Index) * 100
                indiv_gdp = ((g_idx - rv_idx) * 100).round(2)
                group_gdp = ((g_idx - self.calc_group_average(rv_idx, y)) * 100).round(2)
                history['GDP'][y] = {**indiv_gdp.to_dict(), **group_gdp.to_dict()}

                if mei_avg is not None:
                    # 2. MEI Model (Section 11)
                    # [USER REQUEST] mei_평균 index (1.0389 등) - rv_index (1.0 등)
                    m_idx = mei_avg 
                    indiv_mei = ((m_idx - rv_idx) * 100).round(2)
                    group_mei = ((self.calc_group_average(m_idx, y) - self.calc_group_average(rv_idx, y)) * 100).round(2)
                    history['MEI'][y] = {**indiv_mei.to_dict(), **group_mei.to_dict()}

                    # 3. Macro Link Model
                    # Link logic: G + 1/3*(M-G)
                    link_idx = m_idx.map(lambda m: g_idx + (1/3*(m-g_idx)) if m > g_idx else g_idx)
                    indiv_link = ((link_idx - rv_idx) * 100).round(2)
                    group_link = ((self.calc_group_average(link_idx, y) - self.calc_group_average(rv_idx, y)) * 100).round(2)
                    history['Link'][y] = {**indiv_link.to_dict(), **group_link.to_dict()}
            except Exception as e:
                print(f"[WARN] Macro models correction failed for {y}: {e}")

            # 5. SGR Index & Components for Current Year
            comp_y = None
            try:
                comp_y = self.sgr_calc._calc_sgr_components(y)
                if comp_y:
                    idx_s1 = self.sgr_calc.calc_sgr_index(comp_y, model='S1')
                    idx_s2 = self.sgr_calc.calc_sgr_index(comp_y, model='S2')
                    
                    history['SGR_S1_INDEX'][y] = get_combined_index(idx_s1, y)
                    history['SGR_S2_INDEX'][y] = get_combined_index(idx_s2, y)
                    
                    if (y-1) in self.data['df_expenditure'].index:
                        ae_prev = self.data['df_expenditure'].loc[y-1]
                        target_s1 = ae_prev * idx_s1
                        target_s2 = ae_prev * idx_s2
                        history['Target_S1'][y] = get_combined_absolute(target_s1, y)
                        history['Target_S2'][y] = get_combined_absolute(target_s2, y)

                    # Save Factors
                    factors_dict = {}
                    for k, v in comp_y.items():
                        if k in ['l', 'r'] and isinstance(v, (pd.Series, pd.DataFrame)):
                            pre_calc_val = None
                            for key_check in ['전체', '계', '평균']:
                                if key_check in v.index:
                                    pre_calc_val = float(v[key_check])
                                    break
                            
                            if pre_calc_val is not None:
                                factors_dict[k] = pre_calc_val
                            else:
                                avg_series = self.calc_group_average(v, y)
                                factors_dict[k] = float(avg_series['전체'])
                        elif hasattr(v, 'iloc'):
                            factors_dict[k] = float(v.iloc[0])
                        else:
                            factors_dict[k] = float(v)
                    details['sgr_factors'][y] = factors_dict
            except Exception as e:
                print(f"[WARN] SGR Components/Index calc failed for {y}: {e}")

            # 5. Bulk Data (Monitoring) - Range 2014-2028
            try:
                if 2014 <= y <= 2028:
                    
                    # Reval (상대가치 변화지수 원시값) 및 증가율
                    rv_raw = self.data['df_rel_value']
                    if y in rv_raw.index:
                        rv_vals = rv_raw.loc[y].reindex(self.HOSPITAL_TYPES).fillna(1.0)
                        bulk_sgr['reval_rates'][y] = get_combined_index(rv_vals, y)
                        bulk_sgr['reval_growth'][y] = get_combined(rv_vals, y)
                    
                    # MEI (해당 조정 연도 y에서 계산된 y-2년 MEI 평균 증가율 활용)
                    if mei_avg is not None:
                        bulk_sgr['mei_growth'][y-2] = get_combined(mei_avg, y)
                    
                    # Pop (건보대상자수 증가율)
                    pop = self.data['df_pop']
                    if y in pop.index and y-1 in pop.index:
                        p_cur = pop.loc[y, '건보대상자수']
                        p_prev = pop.loc[y-1, '건보대상자수']
                        s1_growth = (p_cur / p_prev - 1) * 100
                        
                        p_col_s2 = '건보_고령화반영후(대상자수)' if '건보_고령화반영후(대상자수)' in pop.columns else '건보대상자수'
                        s2_index_val = pop.loc[y, p_col_s2] / p_prev
                        s2_growth = (s2_index_val - 1) * 100
                        
                        bulk_sgr['pop_growth'][y] = {
                            's1': round(s1_growth, 3), 
                            's2': round(s2_growth, 3),
                            's2_index': round(s2_index_val, 4)
                        }
                    
                    # Law (법과제도 변화지수)
                    law = self.data['df_sgr_law']
                    if y in law.index:
                        indiv_law_idx = law.loc[y]
                        group_law_idx = self.calc_group_average(indiv_law_idx, y)
                        combined_law_idx = {**group_law_idx.to_dict(), **indiv_law_idx.to_dict()}
                        for key_check in ['전체', '계', '평균']:
                            if key_check in indiv_law_idx.index:
                                combined_law_idx['전체'] = indiv_law_idx[key_check]
                                break
                        bulk_sgr['law_changes'][y] = {k: round(v, 4) for k, v in combined_law_idx.items()}
                    
                    # GDP (1인당 실질 GDP 증가율 vs 실질 GDP 증가율 총액)
                    gdp = self.data['df_gdp']
                    if y in gdp.index and y-1 in gdp.index:
                        # 1인당 GDP 증가율 (SGR 모델용)
                        g1 = gdp.loc[y, '실질GDP'] / gdp.loc[y, '영안인구']
                        g0 = gdp.loc[y-1, '실질GDP'] / gdp.loc[y-1, '영안인구']
                        g_per_growth = (g1 / g0 - 1) * 100
                        
                        # GDP 총액 증가율 (거시 GDP 모형 및 모니터링용)
                        g_total_idx = gdp.loc[y, '실질GDP'] / gdp.loc[y-1, '실질GDP']
                        gdp_total_growth = (g_total_idx - 1) * 100
                        
                        bulk_sgr['gdp_growth'][y] = {
                            's1': round(g_per_growth, 3), 
                            's2': round(g_per_growth * 0.8, 3),
                            'total': round(gdp_total_growth, 3) 
                        }

                    # Factor Price (생산요소 물가 증가율)
                    inf = self.data['df_raw_mei_inf']
                    if y in inf.index:
                        f_growth = {}
                        # Labor (3yr Geometric Mean Growth)
                        if y-3 in inf.index:
                            for i in [1, 2, 3]:
                                col = f'인건비_{i}'
                                if col in inf.columns:
                                    rate = (inf.loc[y, col] / inf.loc[y-3, col])**(1/3) - 1
                                    f_growth[col] = round(rate * 100, 3)
                        # Admin & Material (Prev Year Growth)
                        if y-1 in inf.index:
                            for prefix in ['관리비', '재료비']:
                                for i in [1, 2]:
                                    col = f'{prefix}_{i}'
                                    if col in inf.columns:
                                        rate = (inf.loc[y, col] / inf.loc[y-1, col]) - 1
                                        f_growth[col] = round(rate * 100, 3)
                        bulk_sgr['factor_growth'][y] = f_growth

                    # Scenario Adjustments
                    if df_mei is not None and uaf_s1 is not None and uaf_s2 is not None:
                        summary_cols = ['평균', '최대', '최소', '중위수']
                        other_cols = [c for c in df_mei.columns if c not in summary_cols]
                        ordered_cols = summary_cols + other_cols
                        
                        bulk_sgr['scenario_adjustments'][y] = {}
                        for sn in ordered_cols:
                            if sn in df_mei.columns:
                                bulk_sgr['scenario_adjustments'][y][sn] = {
                                    'S1': get_combined(df_mei[sn] * (1 + uaf_s1), y),
                                    'S2': get_combined(df_mei[sn] * (1 + uaf_s2), y)
                                }

                        # --- AR Model Scenario Analysis (2020-2028) ---
                        if 2020 <= y <= 2028:
                            ar_results = []
                            base_rate_keys = ['GDP', 'MEI', 'Link']
                            mei_scenario_keys = ['I1M2Z2', '평균']
                            r_values = [1.0, 0.75, 0.5, 0.25, 0.15, 0.0]
                            
                            # expenditure for weighting (y-2)
                            try:
                                exp_weight = self.data['df_expenditure'].loc[y-2].reindex(self.HOSPITAL_TYPES).fillna(0)
                                total_exp = exp_weight.sum()
                            except:
                                exp_weight = pd.Series(1.0, index=self.HOSPITAL_TYPES)
                                total_exp = len(self.HOSPITAL_TYPES)

                            for br_key in base_rate_keys:
                                if y in history[br_key] and history[br_key][y]:
                                    base_rates = history[br_key][y]
                                    
                                    for mei_sn in mei_scenario_keys:
                                        if mei_sn in bulk_sgr['scenario_adjustments'][y]:
                                            # CF_S,i (S1 adjustment rate %)
                                            cf_s_dict = bulk_sgr['scenario_adjustments'][y][mei_sn]['S1']
                                            cf_s_indiv = pd.Series({t: cf_s_dict[t] for t in self.HOSPITAL_TYPES})
                                            
                                            # Weighted average CF_S
                                            avg_cf_s = (cf_s_indiv * exp_weight).sum() / total_exp if total_exp > 0 else cf_s_indiv.mean()
                                            
                                            # CF_adj_i = CF_S,i - avg_cf_s
                                            cf_adj = cf_s_indiv - avg_cf_s
                                            
                                            for r in r_values:
                                                final_rates_indiv = {}
                                                for t in self.HOSPITAL_TYPES:
                                                    # Base_Rate_i + r * CF_adj_i
                                                    final_rates_indiv[t] = float(base_rates[t]) + r * float(cf_adj[t])
                                                
                                                # Calculate group averages
                                                rates_series = pd.Series(final_rates_indiv)
                                                group_avgs = self.calc_group_average(rates_series/100 + 1, y) # calc_group_average expects index format
                                                final_rates_combined = {**{t: round(v, 2) for t, v in final_rates_indiv.items()}, 
                                                                        **{k: round((v-1)*100, 2) for k, v in group_avgs.to_dict().items()}}
                                                
                                                ar_results.append({
                                                    'base_rate': br_key,
                                                    'mei_scenario': mei_sn,
                                                    'r': r,
                                                    'rates': final_rates_combined
                                                })
                            bulk_sgr['ar_analysis'][y] = ar_results
            except Exception as e:
                print(f"[WARN] Bulk SGR calc failed for {y}: {e}")

        return history, details, bulk_sgr

# ----------------------------------------------------------------------
# 3. Flask Server
# ----------------------------------------------------------------------

app = Flask(__name__)
processor = DataProcessor('SGR_data.xlsx')

# 전역 캐시 변수 - 초기 로딩 시간 단축
_cached_analysis = None

def get_cached_analysis():
    """캐시된 분석 결과를 반환하거나 새로 계산"""
    global _cached_analysis
    
    if _cached_analysis is None:
        print("[INFO] 초기 분석 실행 중...")
        engine = CalculationEngine(processor.raw_data)
        history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)
        
        groups_list = engine.HOSPITAL_TYPES + ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체']
        scenarios_list = list(components['mei_raw'][2025].keys()) if 2025 in components['mei_raw'] else ['평균', '최대', '최소', '중위수']
        
        _cached_analysis = {
            'history': history,
            'components': components,
            'bulk_sgr': bulk_sgr,
            'groups': groups_list,
            'scenarios': scenarios_list,
            'model_name_map': {
                'SGR_S1': 'S1', 'SGR_S2': 'S2', 'MACRO_GDP': 'GDP', 'MACRO_MEI': 'MEI', 'MACRO_LINK': 'Link'
            }
        }
        print("[SUCCESS] 초기 분석 완료!")
    
    return _cached_analysis

@app.route('/')
def landing():
    """Landing page with model selection"""
    return render_template('landing.html')

@app.route('/app')
def index():
    """Main application page"""
    selected_model = request.args.get('model', 'SGR_S2')
    
    # 캐시된 분석 결과 사용
    analysis_data = get_cached_analysis().copy()
    analysis_data['selected_model'] = selected_model

    # Convert pandas Series to dictionaries
    for k, v in analysis_data.items():
        if isinstance(v, dict):
            for sk, sv in v.items():
                if hasattr(sv, 'to_dict'):
                    analysis_data[k][sk] = sv.to_dict()
    
    return render_template('index.html', analysis_data=analysis_data)

@app.route('/simulate', methods=['POST'])
def simulate():
    overrides = request.json
    engine = CalculationEngine(processor.raw_data, overrides)
    history, components, bulk_sgr = engine.run_full_analysis()
    
    # Dynamic Scenario List
    scenarios_list = list(components['mei_raw'][2025].keys()) if 2025 in components['mei_raw'] else []
    if not scenarios_list:
        scenarios_list = ['평균', '최대', '최소', '중위수']

    return jsonify({
        'success': True,
        'analysis_data': {
            'history': history,
            'components': components,
            'bulk_sgr': bulk_sgr,
            'groups': engine.HOSPITAL_TYPES + ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'],
            'scenarios': scenarios_list,
            'model_name_map': {
                'SGR_S1': 'S1', 'SGR_S2': 'S2', 'MACRO_GDP': 'GDP', 'MACRO_MEI': 'MEI', 'MACRO_LINK': 'Link'
            }
        }
    })

@app.route('/save_to_excel_file', methods=['POST'])
def save_to_excel_file():
    data = request.json
    overrides = data.get('overrides', data)
    mode = data.get('mode', 'final')
    
    success, msg = processor.save_overrides_to_excel(overrides, mode=mode)
    if success:
        if mode == 'final':
            # Re-run full analysis with new base data
            global _cached_analysis
            _cached_analysis = None # invalidate cache
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'error': msg})

@app.route('/download_ar/<int:year>')
def download_ar(year):
    """AR 모형 시나리오 분석 결과를 엑셀로 내보내기"""
    analysis = get_cached_analysis()
    ar_data = analysis['bulk_sgr']['ar_analysis'].get(year, [])
    
    if not ar_data:
        return "데이터가 없습니다. (2020-2028년 범위 내에서만 지원됩니다.)", 404

    # 데이터프레임 생성
    rows = []
    for d in ar_data:
        row = {
            '거시지표(B)': d['base_rate'],
            'MEI(S)': d['mei_scenario'],
            '적용률(r)': d['r']
        }
        # Rates 추가
        for k, v in d['rates'].items():
            row[k] = v
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'AR_Scenario_{year}')
        
        # 워크시트 스타일링 (가독성 향상)
        ws = writer.sheets[f'AR_Scenario_{year}']
        # 열 너비 조정
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"AR_Scenario_Analysis_{year}.xlsx")


@app.route('/download/<int:year>')

@app.route('/get_original_data')
def get_original_data():
    """원본 데이터를 JSON 형식으로 반환"""
    # Helper to safely convert values to JSON-compliant float or None
    def clean_val(x):
        try:
            if pd.isna(x): return None
            v = float(x)
            if np.isinf(v) or np.isnan(v): return None
            return v
        except:
            return None

    print("[API] get_original_data called")
    try:
        processor.reload_data()
        years = list(range(2010, 2029))  # 2010년부터 2028년까지 전체 기간으로 확장
        
        # MEI 물가지수 데이터
        mei_data = {}
        df_mei = processor.raw_data['df_raw_mei_inf']
        for field in ['인건비_1', '인건비_2', '인건비_3', '관리비_1', '관리비_2', '재료비_1', '재료비_2']:
            mei_data[field] = {}
            for year in years:
                if year in df_mei.index and field in df_mei.columns:
                    val = df_mei.loc[year, field]
                    mei_data[field][str(year)] = clean_val(val)
                else:
                    mei_data[field][str(year)] = None
        
        # 실제진료비 데이터
        medical_data = {}
        df_exp = processor.raw_data['df_expenditure']
        hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
        for htype in hospital_types:
            medical_data[htype] = {}
            for year in years:
                if year in df_exp.index and htype in df_exp.columns:
                    val = df_exp.loc[year, htype]
                    medical_data[htype][str(year)] = clean_val(val)
                else:
                    medical_data[htype][str(year)] = None
        
        # 환산지수 데이터
        cf_data = {}
        df_reval = processor.raw_data['df_sgr_reval']
        for htype in hospital_types:
            cf_data[htype] = {}
            for year in years:
                if year in df_reval.index and htype in df_reval.columns:
                    val = df_reval.loc[year, htype]
                    cf_data[htype][str(year)] = clean_val(val)
                else:
                    cf_data[htype][str(year)] = None
        
        # 건보대상자수
        # 건보대상자수
        pop_data = {}
        df_pop = processor.raw_data['df_pop']
        # Check available columns
        col_basic = '건보대상자수'
        col_aged = '건보_고령화반영후(대상자수)'
        
        for year in years:
            pop_data[str(year)] = {'basic': None, 'aged': None}
            if year in df_pop.index:
                if col_basic in df_pop.columns:
                    pop_data[str(year)]['basic'] = clean_val(df_pop.loc[year, col_basic])
                if col_aged in df_pop.columns:
                    pop_data[str(year)]['aged'] = clean_val(df_pop.loc[year, col_aged])
        
        # GDP 데이터
        gdp_data = {}
        df_gdp = processor.raw_data['df_gdp']
        for year in years:
            gdp_data[str(year)] = {}
            if year in df_gdp.index:
                for col in ['실질GDP', '영안인구']:
                    if col in df_gdp.columns:
                        val = df_gdp.loc[year, col]
                        gdp_data[str(year)][col] = clean_val(val)
        
        # 법과제도 데이터
        law_data = {}
        df_law = processor.raw_data['df_sgr_law']
        for htype in hospital_types:
            law_data[htype] = {}
            for year in years:
                if year in df_law.index and htype in df_law.columns:
                    val = df_law.loc[year, htype]
                    law_data[htype][str(year)] = clean_val(val)
                else:
                    law_data[htype][str(year)] = None
        
        # 상대가치변화
        rv_data = {}
        df_rv = processor.raw_data['df_rel_value']
        for htype in hospital_types:
            rv_data[htype] = {}
            for year in years:
                if year in df_rv.index and htype in df_rv.columns:
                    val = df_rv.loc[year, htype]
                    rv_data[htype][str(year)] = clean_val(val)
                else:
                    rv_data[htype][str(year)] = None
                    
        # 종별비용구조 (Weights)
        weights_data = {}
        df_w = processor.raw_data['df_weights']
        for htype in hospital_types:
            weights_data[htype] = {}
            for col in ['인건비', '관리비', '재료비']:
                 if htype in df_w.index and col in df_w.columns:
                     val = df_w.loc[htype, col]
                     weights_data[htype][col] = clean_val(val)
                 else:
                     weights_data[htype][col] = None

        return jsonify({
            'mei': mei_data,
            'medical': medical_data,
            'cf': cf_data,
            'population': pop_data,
            'gdp': gdp_data,
            'law': law_data,
            'rv': rv_data,
            'weights': weights_data
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/get_excel_raw_data')
def get_excel_raw_data():
    """메모리에 로드된 데이터를 반환 (요청 시 파일 리로드하여 최신 상태 반영)"""
    try:
        # User requested ability to modify Excel and see results.
        # Force reload from disk to ensure we serve the latest edits.
        success = processor.reload_data()
        
        if not success:
             return jsonify({'error': '데이터 파일(SGR_data.xlsx)을 열 수 없습니다. 파일이 다른 프로그램(Excel 등)에서 열려있는지 확인해주세요.'}), 503

        # 이미 로드된 DataProcessor의 데이터를 활용
        # 매핑: 한글 표시명 -> processor.raw_data 내부 키
        data_map = {
            '진료비_실제': 'df_expenditure',
            '종별비용구조': 'df_weights',
            '생산요소_물가': 'df_raw_mei_inf',
            '1인당GDP': 'df_gdp',
            '건보대상': 'df_pop',
            '연도별환산지수': 'df_sgr_reval',
            '법과제도': 'df_sgr_law',
            '상대가치변화': 'df_rel_value'
        }
        
        results = {}
        for kor_name, internal_key in data_map.items():
            if internal_key in processor.raw_data:
                df = processor.raw_data[internal_key]
                if df is None or df.empty:
                    continue
                
                # 데이터 정제 (NaN -> None 변환)
                # JSON 직렬화를 위해 float('nan')이나 np.nan을 None으로 변환. Infinity도 처리.
                # Must convert to object dtype to hold None instead of NaN
                df_temp = df.replace([np.inf, -np.inf], np.nan)
                
                # [USER FIX] RVS 시트의 경우 빈 컬럼(Unnamed) 제거
                if kor_name == '상대가치변화':
                    df_temp = df_temp.loc[:, ~df_temp.columns.astype(str).str.contains('^Unnamed')]

                df_clean = df_temp.astype(object).where(pd.notnull(df_temp), None)
                
                # Index를 컬럼으로 변환하여 함께 표시 (엑셀처럼)
                df_display = df_clean.reset_index()
                
                # 컬럼명 처리 (Index 이름이 없으면 '구분' 등으로 표시하거나 기본값 사용)
                cols = df_display.columns.tolist()
                cols = [(str(c) if c is not None else '') for c in cols] # 컬럼명 문자열 변환
                
                results[kor_name] = {
                    'headers': cols,
                    'rows': df_display.values.tolist()
                }
                
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)