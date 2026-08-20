import json
from datetime import datetime
from typing import List, Dict, Any

# ---------------------------------------------------------
# 1. 설정 및 데이터 정의 (사내 규정에 따라 수정 필요)
# ---------------------------------------------------------

# 작업 유형별 필수 안전조치 항목 정의 (예시 데이터)
# 실제 개발 시 한국서부발전의 최신 지침서를 기반으로 정확한 항목으로 채워야 합니다.
SAFETY_RULES = {
    "고소작업": [
        "안전대 및 안전고리 착용 상태 확인",
        "작업발판의 견고성 및 난간 설치 확인",
        "추락방지망 설치 여부 확인",
        "기상 상태 (강풍, 비 등) 작업 적합성 확인",
        "작업 구역 하단 통제선 설치 및 경고 표지판 부착",
        "공구 낙하 방지 조치 (공구 주머니 등) 확인",
        "작업자 건강 상태 및 특수건강진단 여부 확인",
        "감시자 배치 및 통신 수단 확보",
        "비상시 구조 계획 수립 및 공유"
    ],
    "화기작업": [
        "주변 가연물 제거 또는 방염포 덮기",
        "소화기 비치 및 소화전 사용 가능 상태 확인",
        "용접기 및 가스용접 장비 누출 점검",
        "화기감시자 지정 및 상시 대기 확인",
        "작업 후 잔불 정리 및 30 분 이상 감시 계획",
        "밀폐공간 내 환기 장치 가동 확인 (해당 시)",
        "가스 농도 측정 및 기록 (해당 시)",
        "작업 허가 구역 명확히 표시",
        "비상 연락체계 구축"
    ],
    "밀폐공간작업": [
        "산소 농도 및 유해가스 농도 측정 기록",
        "강제 환기 장치 가동 및 덕트 연결 확인",
        "입구 감시자 배치 및 교대 근무 계획",
        "구조용 삼각대 및 윈치 설치 확인",
        "보호구 (방독면, 공기호흡기) 착용 상태 확인",
        "조명 및 통신 장비 작동 확인",
        "작업자 인원 파악 시스템 (출입 명부) 운영",
        "비상 구조팀 대기 현황 확인",
        "작업 전 안전교육 이수 확인"
    ]
}

# ---------------------------------------------------------
# 2. 핵심 로직 클래스 정의
# ---------------------------------------------------------

class WorkPermitGenerator:
    def __init__(self):
        self.permit_count = 0

    def generate_permit_number(self) -> str:
        """허가서 번호 자동 생성 (WP-YYYYMMDD-XXX 형식)"""
        self.permit_count += 1
        today = datetime.now().strftime("%Y%m%d")
        return f"WP-{today}-{self.permit_count:03d}"

    def collect_safety_measures(self, work_types: List[str]) -> List[str]:
        """선택된 작업 유형에 따른 안전조치 항목 통합 및 중복 제거"""
        all_measures = []
        for work_type in work_types:
            if work_type in SAFETY_RULES:
                all_measures.extend(SAFETY_RULES[work_type])
            else:
                print(f"경고: '{work_type}'에 대한 안전규칙이 정의되지 않았습니다.")
        
        # 중복 제거 (순서 유지)
        unique_measures = []
        seen = set()
        for measure in all_measures:
            if measure not in seen:
                unique_measures.append(measure)
                seen.add(measure)
                
        return unique_measures

    def create_permit(self, location: str, manager: str, workers: List[str], work_types: List[str]) -> Dict[str, Any]:
        """허가서 데이터 생성"""
        permit_no = self.generate_permit_number()
        safety_measures = self.collect_safety_measures(work_types)
        
        permit_data = {
            "permit_number": permit_no,
            "issue_date": datetime.now().isoformat(),
            "location": location,
            "manager_in_charge": manager,
            "workers": workers,
            "work_types": work_types,
            "required_safety_measures": safety_measures,
            "status": "대기중"  # 초기 상태
        }
        
        return permit_data

    def print_permit_report(self, data: Dict[str, Any]):
        """사람이 읽기 쉬운 형태의 보고서 출력"""
        print("\n" + "="*60)
        print("[한국서부발전 위험작업허가서 초안]")
        print("="*60)
        print(f"허가서 번호 : {data['permit_number']}")
        print(f"발급 일시   : {data['issue_date']}")
        print(f"작업 장소   : {data['location']}")
        print(f"작업 책임자 : {data['manager_in_charge']}")
        print(f"참여 작업자 : {', '.join(data['workers'])}")
        print(f"작업 유형   : {', '.join(data['work_types'])}")
        print("-" * 60)
        print("<< 필수 안전조치 항목 >>")
        for i, measure in enumerate(data['required_safety_measures'], 1):
            print(f"{i}. {measure}")
        print("="*60)
        print("위 항목을 모두 점검하였음에 서명합니다.\n")


# ---------------------------------------------------------
# 3. 실행 시뮬레이션 (메인 함수)
# ---------------------------------------------------------

if __name__ == "__main__":
    # 생성자 인스턴스화
    generator = WorkPermitGenerator()
    
    # [시나리오] 태안발전본부에서 고소작업과 화기작업을 동시에 수행하는 경우
    
    # 1. 입력 데이터 정의 (모바일 앱에서 사용자 입력을 받는 부분과 연동됨)
    input_location = "태안발전본부 3 호기 보일러 실"
    input_manager = "김안전 팀장"
    input_workers = ["이작업 사원", "박점검 대리", "최안전 주임"]
    selected_works = ["고소작업", "화기작업"] # 사용자가 체크박스에서 선택한 값 가정
    
    # 2. 허가서 생성 로직 실행
    permit_result = generator.create_permit(
        location=input_location,
        manager=input_manager,
        workers=input_workers,
        work_types=selected_works
    )
    
    # 3. 결과 출력 (텍스트 형태)
    generator.print_permit_report(permit_result)
    
    # 4. 시스템 연동을 위한 JSON 데이터 확인 (백엔드 API 응답용)
    print("[JSON 데이터 미리보기]")
    print(json.dumps(permit_result, ensure_ascii=False, indent=2))