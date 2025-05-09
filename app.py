import streamlit as st
import random
import time
import re
from streamlit_autorefresh import st_autorefresh

# --- 1) 원문 데이터 & 유틸리티 함수 ---
original_text = """할루시네이션은 환각 또는 망상 등으로 불리며, AI가 생성한 정보에 허위 또는 날조된 정보가 포함되는 현상이다. 
할루시네이션은 실제 사실과 AI를 거친 정보가 다른 내재성 환각과 실제로 존재하지 않는 사실을 창작해서 제공하는 외재적 환각으로 나뉜다.
챗GPT에 질문을 했는데 역사적 사실을 왜곡하거나, 이미지 생성 시 현실 법칙에 위배된 이미지 등을 제공하는 게 할루시네이션의 영향이다. 
할루시네이션은 자연어 처리를 넘어 거의 모든 AI 분야에서 발생한다. 
예를 들어 사람이나 물체를 감지하는 AI가 사람을 전혀 다른 사물로 인지하거나, 제3의 사물을 사람으로 인식할 수 있다. 
사용자 입장에서 외재성 환각은 구분하기 쉽지만, 교묘하게 숫자나 출처가 바뀐 내재성 환각은 구분이 어렵다. 
앞서 갭 수익 보고서처럼 숫자만 다르거나, 요약하라고 하면 원본 데이터와 대조해보지 않고서는 사실 여부를 판단하기가 어렵다. 
특히 GPT-3처럼 데이터가 한정된 생성형 AI일수록 할루시네이션 발생이 심하다. 
할루시네이션을 최대한 피하기 위해서는 데이터의 출처를 확실히 해야 한다. 
유료 서비스인 GPT4는 웹 연동 서비스를 통해 매개변수를 포함한 웹 기반 데이터도 검색하는 기능이 있다. 
또 GPT4에 내장된 컨센서스 등의 툴을 활용하면 논문 검색 시 실존하고 출처가 확실한 자료만으로 찾는다. 
프롬프트를 정밀하게 입력하는 것도 도움이 된다. 
AI의 답변은 정보를 나열했을 뿐, 이해하고 제공하는 게 아니다. 
따라서 질문할 때 ‘공식 보고서나 논문 검색 등을 인용해서’ 설명해 달라고 하거나, ‘최근 5년 간, 국내에서 기사로 확인할 수 있는 내용’ 같은 문장을 덧붙이면 정확성이 향상된다.
안타깝게도 아직까지 AI에서 할루시네이션이 발생하는 원인은 완전히 파악되지 않았다. 
심지어는 AI가 결과를 도출하는 과정도 미지수다. 
우리가 AI에 주문을 내리면, 컴퓨터가 학습한 데이터로 연산을 처리한 뒤 결론을 도출한다. 
문제는 어떤 데이터가 어떻게 상호 영향을 미쳤는지 인과관계를 파악하기 어렵고, 이 과정에서 할루시네이션이 발생한다.
제약 회사에서 AI를 활용해 혁신적인 신약 후보물질을 만들었다고 가정하자. 
이때 신약 물질을 만드는 수식을 명령으로 내렸고, 신약 후보 물질의 구조를 만드는 것까지는 확인할 수 있다. 
하지만 AI 내부에서 어떤 데이터를 활용하고 조합했을지까지는 완벽하게 분석할 수 없다. 
이 문제를 블랙박스 현상이라고 하며, 최근에는 도출 과정까지 명확하게 확인할 수 있는 설명 가능한 AI(Explainable AI)에 대한 연구가 이어지고 있다.
"""
# ──────────────────────────────────────────
# 오류 포함 요약문 예시 (동아일보 기사 기반)
ERROR_SUMMARY_EXAMPLE = """\
✅정의\n\n
• AI가 고의로 정보를 삭제하거나 과장해 생성하는 현상.\n
• ‘환각(hallucination)’ 또는 ‘망상’으로 비유됨.\n\n

✅유형\n\n
• 내재성 환각: 완전히 존재하지 않는 정보를 창작해 제공하는 경우\n
• 외재성 환각: 실제 사실이지만, 숫자·출처 등이 교묘히 왜곡된 경우\n\n

✅발생 영역\n\n
• 데이터 자체 오류를 제외하면 거의 모든 LLM에서는 전혀 발생하지 않는 편임.\n
• 단순 오류와 달리, “존재하지 않는 객체 인식” 등의 심각한 오작동을 유발할 수 있음.\n\n

✅구분의 어려움\n\n
• 외재성 환각은 원본을 대조하지 않아도 눈으로 바로 구분할 수 있다\n\n

✅블랙박스 & 설명 가능한 AI\n\n
• AI 내부 처리 과정을 완벽히 알 수 있는 ‘블랙박스 현상’ 존재.\n
• 이를 해소하기 위한 Explainable AI 연구가 활발히 진행 중.\n\n
"""

sentences = [line for line in original_text.split("\n") if line.strip()]


# --- 정정된(올바른) 요약 문장 리스트 ---
CORRECT_SUMMARY_EXAMPLE = """\
✅정의\n\n
• AI가 생성한 정보에 허위·날조된 내용이 섞여 나오는 현상.\n
• ‘환각(hallucination)’ 또는 ‘망상’으로 비유됨.\n\n

✅유형\n\n
• 내재성 환각: 실제 사실이지만, 숫자·출처 등이 교묘히 왜곡된 경우\n
• 외재성 환각: 완전히 존재하지 않는 정보를 창작해 제공하는 경우\n\n

✅발생 영역\n\n
• 자연어 처리뿐 아니라 이미지 인식, 객체 감지 등 거의 모든 AI 분야에서 나타남.\n
• 단순 오류와 달리, “존재하지 않는 객체 인식” 등의 심각한 오작동을 유발할 수 있음.\n\n

✅구분의 어려움\n\n
• 외재성 환각은 눈으로 확인하기 쉽지만, 내재성 환각은 원본과 대조하지 않으면 판별이 어려움.\n\n

✅블랙박스 & 설명 가능한 AI\n\n
• AI가 어떻게 결과를 도출했는지 내부 작동을 알 수 없는 ‘블랙박스 현상’ 존재\n
• 이를 해소하기 위한 Explainable AI 연구가 활발히 진행 중.
"""
def evaluate_summary(user_summary: str, error_sents: list):
    total = len(error_sents)
    fixed = sum(1 for err in error_sents if err not in user_summary)
    pct = (fixed / total * 100) if total else 0
    if pct >= 85:   grade = "A"
    elif pct >= 65: grade = "B"
    elif pct >= 40: grade = "C"
    else:
        grade = "D"    # 여기서 F는 절대 안 내려줍니다.
    return fixed, total, pct, grade

# --- 2) 세션 초기화 & 페이지 설정 ---
if "stage"      not in st.session_state: st.session_state.stage      = "start"
if "chat"       not in st.session_state: st.session_state.chat       = []
if "errors"     not in st.session_state: st.session_state.errors     = []
if "error_origin" not in st.session_state: st.session_state.error_origin = []
if "start_time" not in st.session_state: st.session_state.start_time = None

st.set_page_config(layout="wide")

# 페이지를 1초마다 자동 리프레시해 줍니다--실시간 업데이트트
st_autorefresh(interval=1000, key="timer_refresh") 에러발생!!

# --- 4) 시작 화면 ---
if st.session_state.stage == "start":
    st.title("🎮 할루시네이션 게임")
    st.markdown("**게임 설명:** 제한 시간 5분 내로 최대한 정확하게 요약 과제를 제출하라")
    if st.button("다음", key="start_next"):
        st.session_state.start_time = time.time()
        st.session_state.stage      = "awaiting_task"
    st.stop()

if st.session_state.stage not in (
    "thank_you",
    "survey_intro",
    "survey_info",
    "survey_gpt",
    "survey_consent",
):

    # --- 3) 남은 시간 표시 (항상 최상단) ---
    if st.session_state.start_time:
        elapsed   = time.time() - st.session_state.start_time
        remaining = max(0, 300 - int(elapsed))
        m, s      = divmod(remaining, 60)

        # HTML <progress> 로 바 만들기
        st.markdown(f"""
            <div class="timer-bar">
              <progress max="300" value="{remaining}" style="width:100%; height:12px;">    </progress>
            </div>
            <div class="timer-container">⏰남은 시간: {m:02d}:{s:02d}</div>
        """, unsafe_allow_html=True)

        # 시간 종료 시 처리
        if remaining <= 0 and st.session_state.stage != "finished":
            st.session_state.chat.append({
                "role":"assistant",
                "content":"⏰ **시간 종료!** 자동 F 처리되었습니다.🥲📻"
            })
            st.session_state.stage = "finished"


    # --- 5) 첫 인사 (awaiting_task) ---
    if st.session_state.stage == "awaiting_task" and not st.session_state.chat:
        st.session_state.chat.append({
            "role": "assistant",
            "content": "안녕하세요! ‘요약 과제’ 또는 ‘요약과제’라고 입력해 주세요."
        })

    # --- 7) 입력 처리 & 단계 전환 ---
    user_input = st.chat_input("명령어를 입력하세요 (예: 요약 과제)")
    if user_input:
        cmd = user_input.strip()
        st.session_state.chat.append({"role": "user", "content": cmd})

        # 7-1) 과제 제시
        if (st.session_state.stage == "awaiting_task"
                and ("요약 과제" in cmd or "요약과제" in cmd)):

            st.session_state.chat.append({
                "role": "assistant",
                "content": "📄 **요약 과제 (원문)**\n"
                           + "\n".join(f"- {s}" for s in sentences)
                           + "\n\n이제 ‘요약해줘’를 입력해 주세요."
            })
            st.session_state.stage = "awaiting_summary"

        # 7-2) 오류 포함 예시 제시
        elif st.session_state.stage == "awaiting_summary" and cmd == "요약해줘":
            st.session_state.chat.append({
                "role": "assistant",
                "content": (
                    "📝 **요약본**\n\n"  # 여기서 두 줄 바꿈
                    + ERROR_SUMMARY_EXAMPLE
                    + "\n\n이제 옵션(과제함 이동, 다시 요약해줘, 출처 알려줘)을 입력하세요."
                )
            })
            st.session_state.stage = "awaiting_option"

        # 7-3) 옵션 처리
        elif st.session_state.stage == "awaiting_option":
            if cmd in ("과제함 이동", "과제함이동"):
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "과제함으로 이동했습니다.\n최종 요약문을 작성한 뒤 ‘최종 제출’을 눌러주세요."
                })
                st.session_state.stage = "awaiting_final"

            elif cmd in ("다시 요약해줘", "다시요약해줘", "다시 요약", "다시요약"):
                err_lines = ERROR_SUMMARY_EXAMPLE.split("\n")
                cor_lines = CORRECT_SUMMARY_EXAMPLE.split("\n")
                diff_idxs = [i for i, (e, c) in enumerate(zip(err_lines, cor_lines)) if e != c]
                if diff_idxs:
                    n_fix = random.randint(1, len(diff_idxs))
                    for i in random.sample(diff_idxs, n_fix):
                        err_lines[i] = cor_lines[i]
                fixed_summary = "\n".join(err_lines)

                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "🛠 다시 요약본 :\n\n" + fixed_summary
                })

            elif cmd in ("출처 알려줘", "출처알려줘"):
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": (
                        "https://www.donga.com/news/It/article/all/20240329/124227094/1\n\n"
                        "출처: 동아일보·동아닷컴, 남시현 기자, 2024-03-29 21:59"
                    )
                })

            else:
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "죄송해요, 그 명령은 사용할 수 없습니다."
                })

    # --- 8) 채팅 로그 렌더링 (가장 마지막) ---
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- 8) 최종 제출 폼 (awaiting_final 단계에서만) ---
    if st.session_state.stage == "awaiting_final":
        final = st.text_area(
            "최종 요약문을 입력하세요:",
            value="\n".join(f"- {s}" for s in st.session_state.errors),
            height=200
        )
        if st.button("최종 제출"):
            fixed, total, pct, grade = evaluate_summary(
                final,
                st.session_state.error_origin
            )
            st.session_state.chat.append({
                "role": "assistant",
                "content": f"✅ 수정된 오류: {fixed}/{total}개 (정확도 {pct:.1f}%) → 등급 **{grade}**"
            })
            st.session_state.stage = "finished"

    # --- 10) 게임 종료 후 '다음' 버튼으로 감사 화면으로 ---
    if st.session_state.stage == "finished":
        if st.button("다음", key="to_thankyou"):
            st.session_state.stage = "thank_you"
        st.stop()

# --- 11) 감사 인사 화면 ---
if st.session_state.stage == "thank_you":
    st.title("🙏 게임 참여 감사드립니다!")
    st.markdown("""
    저희는 서울여자대학교 바롬종합설계 404: Ethics Not Found 팀입니다.  
    AI 할루시네이션 체험 게임에 참여해 주셔서 감사합니다😊  
    참여 내역과 이후 설문은 **오직 연구 목적으로만** 사용됩니다.
    """)
    if st.button("다음", key="thankyou_next"):
        st.session_state.stage = "survey_intro"
    st.stop()

# --- 12) 설문 도입 ---
if st.session_state.stage == "survey_intro":
    st.header("본 설문에 동의하십니까?")
    st.write("""
    본 설문은 AI 오류 인식 수준과  
    비판적 수용 정도를 조사합니다.  
    익명으로 진행되며, 수집된 응답은 연구 목적으로만 사용됩니다.  
    문의: ssong9318@swu.ac.kr
    """)
    if st.button("동의", key="survey_agree"):
        st.session_state.stage = "survey_info"
    st.stop()

# --- 13) 기본 정보 수집 ---
if st.session_state.stage == "survey_info":
    st.header("1. 기본 정보")
    age = st.selectbox("연령대를 선택해주세요", ["10대", "20대", "30대", "40대", "50대 이상"])
    if st.button("다음", key="info_next"):
        st.session_state.age = age
        st.session_state.stage = "survey_gpt"
    st.stop()

# --- 14) GPT 사용 습관 점검표 ---
if st.session_state.stage == "survey_gpt":
    st.header("2. GPT 사용 습관 점검표")
    opts = [
        "나는 GPT가 알려준 정보를 검증하지 않고 바로 믿은 적이 있다.",
        "나는 GPT가 제공한 답변을 별다른 의심 없이 과제나 글에 사용한 적이 있다.",
        "GPT가 틀릴 수도 있다는 사실을 종종 잊는다.",
        "출처 확인 없이 GPT 답변을 복사해 사용한 적이 있다.",
        "GPT를 사용할 때 항상 여러 자료를 함께 참고한다.",
        "GPT가 잘못된 정보를 줄 경우, 스스로 오류를 찾아본 적이 있다.",
        "민감한 개인정보를 GPT에 입력한 적이 있다.",
        "AI가 만든 내용이 정말 정확한지 확인하는 습관이 있다.",
        "AI를 참고할 때, 나만의 생각이나 판단을 추가하려고 노력한다."
    ]
    checked = [o for o in opts if st.checkbox(o)]
    pledge = st.text_input("✍️ 앞으로의 다짐 (예: 정확도를 반드시 확인하겠습니다.)")
    if st.button("다음", key="gpt_next"):
        st.session_state.checked = checked
        st.session_state.pledge  = pledge
        st.session_state.stage   = "survey_consent"
    st.stop()

# --- 15) 최종 동의 ---
if st.session_state.stage == "survey_consent":
    st.header("3. 최종 동의")
    st.write("수집된 설문 결과는 연구 목적으로만 사용됩니다.")

    # 버튼 클릭 시 completed 플래그를 켭니다.
    if st.button("끝내기", key="final_submit"):
        st.session_state.completed = True

    # completed 플래그가 켜져 있으면 메시지를 항상 보여줍니다.
    if st.session_state.get("completed", False):
        st.success("모든 과정이 완료되었습니다! 참여해주셔서 감사합니다😊")
    st.stop()
