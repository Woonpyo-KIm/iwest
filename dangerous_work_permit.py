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

# --- 2. 화면 분리 ---
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
        # 상단 제어 버튼
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            if st.button("✅ 승인 및 허가서 발급", use_container_width=True, type="primary"):
                st.success("승인 완료! 아래 허가서를 출력하여 현장에 비치하세요.")
        with col_btn2:
            if st.button("❌ 반려", use_container_width=True):
                st.error("반려 처리되었습니다.")
        with col_btn3:
            # 부모 창(전체 페이지)을 출력하도록 JavaScript 수정
            components.html(
                """
                <button onclick="window.parent.print()" 
                style="width: 100%; height: 40px; background-color: #1f77b4; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 14px;">
                🖨️ 현장 비치용 출력 (A4)
                </button>
                """,
                height=50
            )

        st.divider()

        # 전체 화면 인쇄 스타일 제어 (인쇄 시 상단 버튼, 메뉴, 탭 숨김 처리)
        st.markdown("""
            <style>
            @media print {
                /* 불필요한 UI 숨기기 */
                header, footer, [data-testid="stHeader"], [data-testid="stToolbar"], .stTabs, button, iframe {
                    display: none !important;
                }
                .main .block-container {
                    padding: 0 !important;
                    margin: 0 !important;
                    width: 100% !important;
                }
                body {
                    background-color: white !important;
                    color: black !important;
                }
                /* 문서 테두리 인쇄 설정 */
                .print-area {
                    border: 2px solid #000 !important;
                    padding: 20px !important;
                    margin: 0 !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        # ==========================================
        # 현장 비치용 인쇄 문서 영역 (HTML/CSS 기반)
        # ==========================================
        jsa_html_rows = ""
        for idx, row in data['jsa_data'].iterrows():
            jsa_html_rows += f"""
            <tr>
                <td style="border:1px solid #333; padding:6px; text-align:center;">{row.get('작업단계','')}</td>
                <td style="border:1px solid #333; padding:6px; text-align:center;">{row.get('위험요인','')}</td>
                <td style="border:1px solid #333; padding:6px; text-align:center;">{row.get('위험성수준','')}</td>
                <td style="border:1px solid #333; padding:6px;">{row.get('감소대책','')}</td>
            </tr>
            """

        gas = data['gas_data']

        # 전체 인쇄 양식 HTML
        permit_html = f"""
        <div class="print-area" style="border: 2px solid #333; padding: 25px; border-radius: 5px; background-color: #fff; color: #000;">
            <h1 style="text-align: center; margin-bottom: 5px; font-size: 24px;">안전작업 허가서 (현장 비치용)</h1>
            <p style="text-align: right; font-size: 12px; margin-bottom: 20px;"><b>발급일시:</b> {data['time']}</p>
            
            <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 15px; font-size: 16px;">1. 작업 개요</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px;">
                <tr>
                    <td style="padding: 4px 0;"><b>작업명:</b> {data['work_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px 0;"><b>작업 장소:</b> {data['location']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px 0;"><b>투입 작업자:</b> {data['workers']}</td>
                </tr>
            </table>

            <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 15px; font-size: 16px;">2. 필수 안전수칙 (TBM 전파사항)</h3>
            <div style="background-color: #f8f9fa; border-left: 4px solid #1f77b4; padding: 10px; font-size: 12px; margin-bottom: 10px; color: #000;">
                <b>[작업 전 근로자 필수 전달]</b><br>
                • 현장 내 모든 작업자는 해당 작업의 <b>위험성평가(JSA) 내용</b>을 숙지할 것.<br>
                • 개인 보호구(안전모, 안전화, 보안경 등) 착용 상태를 상시 유지할 것.
            </div>
            <p style="font-size: 11px; line-height: 1.5; margin-bottom: 15px;">
                <b>🛡️ 핵심안전수칙 (WP Safety-10 Golden Rules):</b><br>
                1. TBM 참여 | 2. 보호구 착용 | 3. 산소농도 측정 | 4. 안전고리 체결 | 5. 가연물 제거 | 6. 임의조작 금지 | 7. LOTO 실시 | 8. 통행로 이용 | 9. Stop Work 권한 | 10. 정리정돈
            </p>

            <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 15px; font-size: 16px;">3. 환경 측정 기록</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #333; font-size: 12px; text-align: center; margin-bottom: 20px;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #333; padding: 6px;">O2 (%)</th>
                    <th style="border: 1px solid #333; padding: 6px;">가연성가스 LEL (%)</th>
                    <th style="border: 1px solid #333; padding: 6px;">CO (ppm)</th>
                    <th style="border: 1px solid #333; padding: 6px;">H2S (ppm)</th>
                    <th style="border: 1px solid #333; padding: 6px;">CO2 (%)</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 6px;">{gas['O2']}%</td>
                    <td style="border: 1px solid #333; padding: 6px;">{gas['LEL']}%</td>
                    <td style="border: 1px solid #333; padding: 6px;">{gas['CO']}ppm</td>
                    <td style="border: 1px solid #333; padding: 6px;">{gas['H2S']}ppm</td>
                    <td style="border: 1px solid #333; padding: 6px;">{gas['CO2']}%</td>
                </tr>
            </table>

            <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 15px; font-size: 16px;">4. 작업 위험성평가(JSA) 및 안전대책</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #333; font-size: 12px; margin-bottom: 30px;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="border:1px solid #333; padding:6px; width:20%;">작업단계</th>
                        <th style="border:1px solid #333; padding:6px; width:25%;">위험요인</th>
                        <th style="border:1px solid #333; padding:6px; width:15%;">위험성수준</th>
                        <th style="border:1px solid #333; padding:6px; width:40%;">감소대책</th>
                    </tr>
                </thead>
                <tbody>
                    {jsa_html_rows}
                </tbody>
            </table>

            <div style="margin-top: 40px; font-size: 13px;">
                <table style="width: 100%; text-align: center;">
                    <tr>
                        <td style="width: 33%;"><b>작업책임자 (수급인):</b> ________ (서명)</td>
                        <td style="width: 33%;"><b>공사감독원:</b> ________ (서명)</td>
                        <td style="width: 33%;"><b>발전기승원(운전원):</b> ________ (서명)</td>
                    </tr>
                </table>
            </div>

            <!-- 뒷장 인쇄용 허가서 기재요령 -->
            <div style="page-break-before: always; margin-top: 30px; padding-top: 20px;">
                <h3 style="border-bottom: 2px solid #333; padding-bottom: 5px; font-size: 16px;">[허가서 기재요령]</h3>
                <div style="font-size: 10.5px; color: #222; line-height: 1.6; text-align: justify;">
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
        </div>
        """
        
        # HTML 문서 화면 출력
        st.markdown(permit_html, unsafe_allow_html=True)
