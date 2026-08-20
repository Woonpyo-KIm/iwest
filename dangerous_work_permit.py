import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(page_title="스마트 안전작업 허가 시스템", page_icon="🛡️", layout="wide")

# --- 1. 가상 데이터베이스 ---
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

if 'submitted_permit' not in st.session_state:
    st.session_state['submitted_permit'] = None

# --- 3. 화면 분리 ---
st.title("🛡️ 한국서부발전 스마트 안전작업 허가 시스템")
tab1, tab2 = st.tabs(["📱 현장 작업자 입력 (모바일 뷰)", "💻 감독자 확인 및 결재 (대시보드 뷰)"])

# =====================================================================
# TAB 1: 현장 작업자 입력 화면 (모바일 뷰)
# =====================================================================
with tab1:
    st.markdown("### 👷 현장 작업자 입력 폼")
    
    with st.form("mobile_input_form"):
        st.subheader("1. 작업 기본 정보")
        work_name = st.selectbox("작업명", options=["선택하세요", "5호기 EP Manual Valve 점검 및 정비", "일반 용접 작업 (예시)"])
        location = st.text_input("작업 장소", placeholder="예: 5호기 EP Area")
        workers = st.text_input("작업자 명단", placeholder="쉼표로 구분 (예: 홍길동, 김철수)")
        
        st.divider()
        st.subheader("2. 필수 환경 측정 (현재 수치 입력)")
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
        st.subheader("3. 작업 위험성평가표 (JSA)")
        
        if work_name in JSA_DB:
            df_jsa = pd.DataFrame(JSA_DB[work_name])
        else:
            df_jsa = pd.DataFrame([{"작업단계": "", "위험요인": "", "위험성수준": "", "감소대책": ""}])
            
        edited_jsa = st.data_editor(df_jsa, num_rows="dynamic", use_container_width=True)
        submit_btn = st.form_submit_button("감독자에게 허가서 전송하기 🚀")
        
        if submit_btn:
            if work_name == "선택하세요":
                st.error("작업명을 선택해 주세요.")
            else:
                st.session_state['submitted_permit'] = {
                    "work_name": work_name,
                    "location": location,
                    "workers": workers,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "gas_data": {"O2": o2_val, "LEL": lel_val, "CO": co_val, "H2S": h2s_val, "CO2": co2_val},
                    "jsa_data": edited_jsa
                }
                st.success("✅ 허가서가 전송되었습니다!")

# =====================================================================
# TAB 2: 감독자 확인 및 결재 (대시보드 뷰)
# =====================================================================
with tab2:
    data = st.session_state['submitted_permit']
    
    if data is None:
        st.warning("아직 현장에서 제출된 작업 허가서가 없습니다.")
    else:
        # 상단 제어 패널
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            if st.button("✅ 승인 및 허가서 발급", use_container_width=True, type="primary"):
                st.success("승인 완료! 아래 허가서를 출력하여 현장에 비치하세요.")
        with col_btn2:
            if st.button("❌ 반려", use_container_width=True):
                st.error("반려 처리되었습니다.")
        with col_btn3:
            components.html(
                """
                <button onclick="window.print()" 
                style="width: 100%; height: 40px; background-color: #f0f2f6; border: 1px solid #c4c4c4; border-radius: 5px; cursor: pointer; font-weight: bold;">
                🖨️ 현장 비치용 출력
                </button>
                """,
                height=50
            )

        st.divider()

        # ==========================================
        # 현장 비치용 출력 뷰 (Printable Area)
        # ==========================================
        with st.container(border=True):
            # [1페이지] 본문 내용
            st.markdown(f"<h2 style='text-align: center;'>안전작업 허가서 (현장 비치용)</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: right;'>발급일시: {data['time']}</p>", unsafe_allow_html=True)
            
            st.markdown("#### 1. 작업 개요")
            st.write(f"**작업명:** {data['work_name']}")
            st.write(f"**작업 장소:** {data['location']}")
            st.write(f"**투입 작업자:** {data['workers']}")
            
            st.markdown("#### 2. 필수 안전수칙 (TBM 전파사항)")
            st.info("""
            **[작업 전 반드시 작업자에게 알릴 사항]**
            * 현장 내 모든 작업자는 해당 작업의 **위험성평가(JSA) 내용**을 숙지할 것.
            * 보호구(안전모, 안전화, 보안경 등)는 임의로 탈착 금지.
            """)
            st.markdown("**🛡️ 핵심안전수칙 (WP Safety-10 Golden Rules)**\n1. 작업 전 안전점검회의(TBM) 참여 | 2. 안전보호구 착용 | 3. 밀폐공간 산소농도 측정 | 4. 고소작업 시 안전고리 체결 | 5. 화기작업 전 주변 가연물 제거 | 6. 가동설비 임의 조작 금지 | 7. 정비작업 시 LOTO(잠금장치) 실시 | 8. 지정된 통행로 이용 | 9. 불안전 상태 발견 시 즉시 작업 중지(Stop Work) | 10. 작업 전후 정리정돈")

            st.markdown("#### 3. 환경 측정 기록")
            gas = data['gas_data']
            col_gas1, col_gas2, col_gas3, col_gas4, col_gas5 = st.columns(5)
            col_gas1.write(f"**O2:** {gas['O2']}%")
            col_gas2.write(f"**LEL:** {gas['LEL']}%")
            col_gas3.write(f"**CO:** {gas['CO']}ppm")
            col_gas4.write(f"**H2S:** {gas['H2S']}ppm")
            col_gas5.write(f"**CO2:** {gas['CO2']}%")

            st.markdown("#### 4. 작업 위험성평가(JSA) 및 안전대책")
            st.table(data['jsa_data'])

            st.markdown("<br><br>", unsafe_allow_html=True)
            col_sign1, col_sign2, col_sign3 = st.columns(3)
            with col_sign1:
                st.write("작업책임자 (수급인) : ____________ (서명)")
            with col_sign2:
                st.write("공사감독원 : ____________ (서명)")
            with col_sign3:
                st.write("발전기승원(운전원) : ____________ (서명)")

            # [2페이지] 인쇄 시 뒷장으로 넘어가도록 CSS 적용된 허가서 기재요령
            st.markdown("""
            <div style="page-break-before: always; margin-top: 50px;">
                <h4>[허가서 기재요령]</h4>
                <div style="font-size: 12px; color: #555; line-height: 1.6;">
                    1. ①란은 발급검토자인 감독부서 공사감독원이 오더설계시 선택하여 신청자가 허가서를 신청하도록 사전에 작성한다.<br>
                    2. ②허가서 신청자인 공사업체(작업자)는 허가서에 일일작업시간(1일 8시간), 세부 작업내용을 입력하고 하단의 안전조치 요구사항을 지정(√) 한다. 수급업체 관리감독자는 허가서 결재 전 수정사항 및 검토의견을 기록할 수 있으며, 작업자는 해당사항을 TBM 시 전달 및 교육하여야 한다.<br>
                    3. 발급검토자인 감독부서 공사감독원은 허가서의 각 항목을 최종 확인 후 작업종류별 허가승인부서 결재단계 구분에 따라 안전검토 및 허가승인을 요청한다.<br>
                    4. ④란은 공사업체에서 안전이 확보되었을 경우 서명(안전관리자, 안전담당자 또는 안전패트롤)한다.<br>
                    5. ⑤란은 공사업체에서 안전이 확보되었을 경우 서명 날인(수급업체 관리감독자) 한다.<br>
                    6. ⑥란은 감독부서(관리감독원, 관리감독자 등) 및 운전부서가 작업 전 안전조치 확인 등 안전이 확보되었을 경우 서명한다.<br>
                    7. ⑦란은 작업종료시간 기록 후 관련자가 서명 날인하고 작업허가서 원본을 허가승인부서에 제출한다.<br>
                    8. ⑧란은 연속작업 2일차부터 생성되는 출력물로 안전조치 요구사항에 체크 및 이상이 없을 경우 수급인 관리감독자, 도급인 감독원, 발전부서에서 서명하고 실제 작업시간을 수기기록 하도록 한다.<br>
                    9. ⑨란은 주관부서 관리감독자, 공사업체 안전관리자 관리감독자, 한국산업안전공단이 정하는 '산소 및 유해가스 농도의 측정·평가에 관한 교육'을 이수한 자가 연장 측정 기록 후 해당란에 서명한다.<br>
                    10. ⑩란의 작업안전분석(JSA)은 공사업체(수급인)와 감독부서(도급인)가 합동으로 시행하여야 한다.<br>
                    11. 연장작업은 4시간 이내로 허가승인부서의 수기승인을 받고 시행 할 수 있으며, 연장작업시에는 작업 전 안전조치 요구사항을 재확인하여야 한다.<br>
                    12. 사업장 소속에 따라 '필수안전수칙(WP STAR-10)' 우측에 방재센터 전화번호가 자동기록된다.
                </div>
            </div>
            """, unsafe_allow_html=True)
