import os

file_path = r'h:\병원환산지수연구_2027년\SGR앱개발_v2\static\js\main.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
garbage_start_marker = "    'S2_1': {"
garbage_end_marker = "};"
in_garbage = False

for i, line in enumerate(lines):
    # Detect the specific garbage block starting at line ~1816
    # It starts after the valid 'S2_3' block closure and '};'
    if "    'S2_1': {" in line and "name:" in lines[i+1]:
        # This identifies the start of the garbage block which repeats S2_1
        # But we must be careful not to delete the valid one inside scenarioInfo
        # The valid one is indented deeper (8 spaces), garbage is 4 spaces.
        if line.startswith("    'S2_1': {"): 
            in_garbage = True
    
    if in_garbage:
        if line.strip() == "};":
            in_garbage = False
            continue # Skip the closing }; of garbage
        continue # Skip garbage lines

    # Update HTML header to be dynamic
    if "2. 실제 수가계약 결과를 반영한 환산지수 조정률과 추가소요재정" in line and "(" not in line:
        line = line.replace("재정", "재정 (${year}년 분석)")
    
    if "과거 수가협상 결과(2020-2024)" in line:
        line = line.replace("2020-2024", "${year-5}-${year-1}")
    
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully fixed main.js")
