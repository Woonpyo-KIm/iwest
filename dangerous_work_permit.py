import streamlit as st
import pandas as pd
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="스마트 안전작업 허가 시스템", page_icon="🛡️", layout="wide")

# --- 1. 가상 데이터베이스 (추후 사내 ERP/DB와 연동될 부분) ---
# 작업 유형별 JSA 디폴트 데이터 (image_7.png, image_8.png 참고)
JSA_DB = {
    "5호기 EP Manual Valve 점검 및 정비": [
        {"작업단계": "작업 전 안전 교육", "위험요인": "없음", "위험성수준": "하", "감소대책": "작업전 안전교육 및 스트레칭 시행, 안전보호구 착용 철저"},
        {"작업단계": "작업 전 TBM 실시", "위험요인": "없음", "위험성수준": "하", "감소대책": "작업전 안전교육 및 스트레칭 시행, 안전보호구 착용 철저"},
        {"작업단계": "작업 구역 설정", "위험요인": "아차사고", "위험성수준": "중", "감소대책": "작업 전 스트레칭 철저, 안전구역 내 작업, 2인 1조 작업 철저"},
        {"작업단계": "작업 도구 준비", "위험요인": "공기구 운반시 찔림/베임", "위험성수준": "중", "감소대책": "안전보호구(안전장갑 등) 착용 철저"},
        {"작업단계": "작업반경 내 위험요소 확인", "위험요인": "전도", "위험성수준": "하", "감소대책": "작업구간 출입금지구역 설정"}
    ],
    "일반 용접 작업 (예시)": [
        {"작업단계": "주변 인화물질 제거", "위험요인": "화재", "위험성수준": "상", "감소대책": "방염포 설치 및 소화기 2대 이상 비치"},
        {"작업단계": "용접기 접지 확인", "위험요인": "감전", "위험성수준": "상", "감소대책": "누전차단기 확인 및 절연장갑 착용"}
    ]
}

# --- 2. 세션 상태 초기화 (데이터 임시 저장소) ---
if 'submitted_permit' not in st.session_state:
    st.session_state['submitted_permit'] = None

# --- 3. 화면 분리 (탭 생성) ---
st.title("🛡️ 한국서부발전 스마트 안전작업 허가 시스템")
tab1, tab2 = st.tabs(["📱 현장 작업자 입력 (모바일 뷰)", "💻 감독자 확인 및 결재 (대시보드 뷰)"])

# =====================================================================
# TAB 1: 현장 작업자 입력 화면 (모바일 뷰)
# =====================================================================
with tab1:
    st.markdown("### 👷 현장 작업자 입력 폼")
    st.info("💡 모바일 기기에서 현장 작업자가 데이터를 입력하고 전송하는 화면입니다.")
    
    with st.form("mobile_input_form"):
        # 1. 기본 정보
        st.subheader("1. 작업 기본 정보")
        work_name = st.selectbox("작업명 (사내 작업 오더 선택)", options=["선택하세요", "5호기 EP Manual Valve 점검 및 정비", "일반 용접 작업 (예시)"])
        location = st.text_input("작업 장소", placeholder="예: 5호기 EP Area")
        workers = st.text_input("작업자 명단", placeholder="쉼표로 구분 (예: 홍길동, 김철수)")
        
        st.divider()
        
        # 2. 필수 측정 항목 (image_6.png 참고 - 수동 입력)
        st.subheader("2. 필수 환경 측정 (현재 수치 입력)")
        st.caption("현장에서 측정한 정확한 수치를 입력해 주세요.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            o2_val = st.number_input("O2 (%) [정상: 18~23.5]", value=0.0, step=0.1)
            lel_val = st.number_input("가연성 가스 LEL (%) [정상: 10미만]", value=0.0, step=0.1)
        with col2:
            co_val = st.number_input("CO (ppm) [정상: 30미만]", value=0, step=1)
            h2s_val = st.number_input("H2S (ppm) [정상: 10미만]", value=0, step=1)
        with col3:
            co2_val = st.number_input("CO2 (%) [정상: 1.5미만]", value=0.0, step=0.1)
            
        st.divider()
        
        # 3. 위험성 평가표 (JSA) - 자동 불러오기 및 수정
        st.subheader("3. 작업 위험성평가표 (JSA)")
        st.caption("선택한 작업에 대한 표준 위험성평가표가 자동으로 불러와집니다. 현장 상황에 맞게 수정하세요.")
        
        # 선택한 작업명에 따라 초기 데이터프레임 설정
        if work_name in JSA_DB:
            df_jsa = pd.DataFrame(JSA_DB[work_name])
        else:
            df_jsa = pd.DataFrame([{"작업단계": "", "위험요인": "", "위험성수준": "", "감소대책": ""}])
            
        # 데이터 에디터 (사용자가 표 형태로 직접 수정 가능)
        edited_jsa = st.data_editor(df_jsa, num_rows="dynamic", use_container_width=True)
        
        # 4. 제출 버튼
        submit_btn = st.form_submit_button("감독자에게 허가서 전송하기 🚀")
        
        if submit_btn:
            if work_name == "선택하세요":
                st.error("작업명을 선택해 주세요.")
            else:
                # 제출된 데이터를 세션에 저장 (DB 저장 시뮬레이션)
                st.session_state['submitted_permit'] = {
                    "work_name": work_name,
                    "location": location,
                    "workers": workers,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "gas_data": {"O2": o2_val, "LEL": lel_val, "CO": co_val, "H2S": h2s_val, "CO2": co2_val},
                    "jsa_data": edited_jsa
                }
                st.success("✅ 허가서가 성공적으로 전송되었습니다! 감독자 확인 탭을 눌러보세요.")

# =====================================================================
# TAB 2: 감독자 확인 및 결재 (대시보드 뷰)
# =====================================================================
with tab2:
    st.markdown("### 👨‍💼 관리 감독자 대시보드")
    st.info("💡 현장에서 올라온 허가서 데이터를 PC 뷰에서 종합적으로 검토하고 결재하는 화면입니다.")
    
    data = st.session_state['submitted_permit']
    
    if data is None:
        st.warning("아직 현장에서 제출된 작업 허가서가 없습니다.")
    else:
        # 상단 요약 정보
        st.subheader(f"📄 결재 대기중: {data['work_name']}")
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("작업 장소", data['location'])
        col_info2.metric("작업자", data['workers'])
        col_info3.metric("신청 시간", data['time'])
        
        st.divider()
        
        # 측정 결과 검증 로직 (image_6.png 기준 안전 범위 체크)
        st.markdown("#### 🔍 환경 측정 결과 검토")
        gas = data['gas_data']
        
        # 안전 여부 판단 로직
        is_o2_safe = 18.0 <= gas['O2'] <= 23.5
        is_lel_safe = gas['LEL'] < 10.0
        is_co_safe = gas['CO'] < 30
        is_h2s_safe = gas['H2S'] < 10
        is_co2_safe = gas['CO2'] < 1.5
        
        col_gas1, col_gas2, col_gas3, col_gas4, col_gas5 = st.columns(5)
        col_gas1.metric("O2 (%)", gas['O2'], "정상" if is_o2_safe else "위험", delta_color="normal" if is_o2_safe else "inverse")
        col_gas2.metric("LEL (%)", gas['LEL'], "정상" if is_lel_safe else "위험", delta_color="normal" if is_lel_safe else "inverse")
        col_gas3.metric("CO (ppm)", gas['CO'], "정상" if is_co_safe else "위험", delta_color="normal" if is_co_safe else "inverse")
        col_gas4.metric("H2S (ppm)", gas['H2S'], "정상" if is_h2s_safe else "위험", delta_color="normal" if is_h2s_safe else "inverse")
        col_gas5.metric("CO2 (%)", gas['CO2'], "정상" if is_co2_safe else "위험", delta_color="normal" if is_co2_safe else "inverse")
        
        st.divider()
        
        # JSA 결과 리뷰
        st.markdown("#### 📋 작업 위험성평가표 (JSA) 최종 확인")
        st.dataframe(data['jsa_data'], use_container_width=True)
        
        st.divider()
        
        # 결재 버튼 영역
        st.markdown("#### ✍️ 감독자 결재")
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("✅ 승인 및 허가서 발급", use_container_width=True, type="primary"):
                st.success("작업이 최종 승인되었습니다. 현장으로 승인 알림이 발송됩니다.")
        with col_btn2:
            if st.button("❌ 반려 (보완 지시)", use_container_width=True):
                st.error("반려 처리되었습니다. 현장 작업자에게 재측정 및 JSA 보완을 요청합니다.")
