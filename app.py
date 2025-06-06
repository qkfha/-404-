import streamlit as st
import random
import time
import re
import base64
import streamlit.components.v1 as components

image_path = "image.png"
with open(image_path, "rb") as img_file:
    img_bytes = img_file.read()
    img_b64 = base64.b64encode(img_bytes).decode()

image_path2 = "back.jpg"
with open(image_path2, "rb") as img_file:
    img_bytes2 = img_file.read()
    bg_base64 = base64.b64encode(img_bytes2).decode()


# --- 1) 원문 데이터 & 유틸리티 함수 ---
original_text = """할루시네이션은 환각 또는 망상 등으로 불리며, AI가 생성한 정보에 허위 또는 날조된 정보가 포함되는 현상이다. 
할루시네이션은 실제 사실과 AI를 거친 정보가 다른 내재성 환각과 실제로 존재하지 않는 사실을 창작해서 제공하는 외재적 환각으로 나뉜다.
챗GPT에 질문을 했는데 역사적 사실을 왜곡하거나, 이미지 생성 시 현실 법칙에 위배된 이미지 등을 제공하는 게 할루시네이션의 영향이다. 
할루시네이션은 자연어 처리를 넘어 거의 모든 AI 분야에서 발생한다. 
사용자 입장에서 외재성 환각은 구분하기 쉽지만, 교묘하게 숫자나 출처가 바뀐 내재성 환각은 구분이 어렵다. 
수익 보고서처럼 숫자만 다르거나, 요약하라고 하면 원본 데이터와 대조해보지 않고서는 사실 여부를 판단하기가 어렵다. 
특히 GPT-3처럼 데이터가 한정된 생성형 AI일수록 할루시네이션 발생이 심하다. 
할루시네이션을 최대한 피하기 위해서는 데이터의 출처를 확실히 해야 한다. 
유료 서비스인 GPT4는 웹 연동 서비스를 통해 매개변수를 포함한 웹 기반 데이터도 검색하는 기능이 있다. 
또 GPT4에 내장된 컨센서스 등의 툴을 활용하면 논문 검색 시 실존하고 출처가 확실한 자료만으로 찾는다. 
프롬프트를 정밀하게 입력하는 것도 도움이 된다. 
AI의 답변은 정보를 나열했을 뿐, 이해하고 제공하는 게 아니다. 
따라서 질문할 때 ‘공식 보고서나 논문 검색 등을 인용해서’ 설명해 달라고 하거나, ‘최근 5년 간, 국내에서 기사로 확인할 수 있는 내용’ 같은 문장을 덧붙이면 정확성이 향상된다.
우리가 AI에 주문을 내리면, 컴퓨터가 학습한 데이터로 연산을 처리한 뒤 결론을 도출한다. 
문제는 어떤 데이터가 어떻게 상호 영향을 미쳤는지 인과관계를 파악하기 어렵고, 이 과정에서 할루시네이션이 발생한다.
"""
# ──────────────────────────────────────────
# 오류 포함 요약문 예시 (동아일보 기사 기반)
ERROR_SUMMARY_EXAMPLE = """\
✅정의\n\n
• AI가 고의로 정보를 삭제하거나 과장해 생성하는 현상.\n
• ‘환각(hallucination)’ 또는 ‘함정’으로 비유됨.\n\n

✅유형\n\n
• 내재성 환각: 완전히 존재하지 않는 정보를 창작해 제공하는 경우\n
• 외재성 환각: 실제 사실이지만, 숫자·출처 등이 교묘히 왜곡된 경우\n\n

✅발생 영역\n\n
• 데이터 자체 오류를 제외하면 거의 모든 LLM에서는 전혀 발생하지 않는 편임.\n
• 단순 오류와 달리, “존재하지 않는 객체 인식” 등의 심각한 오작동을 유발할 수 있음.\n\n

✅구분의 어려움\n\n
• 외재성 환각은 원본을 대조하지 않아도 눈으로 바로 구분할 수 있다.\n\n
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
"""

# --- 2) 세션 초기화 & 페이지 설정 ---
if "stage"      not in st.session_state: st.session_state.stage      = "start"
if "chat"       not in st.session_state: st.session_state.chat       = []
if "errors"     not in st.session_state: st.session_state.errors     = []
if "error_origin" not in st.session_state: st.session_state.error_origin = []
if "start_time" not in st.session_state: st.session_state.start_time = None

# ------- 새로 추가된 score 초기화 --------
if "score" not in st.session_state:
    st.session_state.score = 50

st.set_page_config(layout="wide")

# 1) 게임 시작 시점에 타이머 총시간(초)을 session_state 에 저장
if "start_time" not in st.session_state:
    st.session_state.start_time = None

width_percent = st.slider("이미지 너비 조절 (%)", min_value=10, max_value=100, value=50)

# --- 4) 시작 화면 ---
if st.session_state.stage == "start":
    st.title("🎮 AI 할루시네이션 게임")
    st.markdown("**게임 설명:** 제한 시간 **5분** 내로 최대한 **정확하게** 요약 과제를 제출하여 최대한 ⭐높은 점수⭐를 획득하세요")
    img = f"""
        <img src="data:image/png;base64,{bg_base64}" width="150">
        """
    st.markdown(img, unsafe_allow_html=True)
    
    if st.button("다음", key="start_next"):
        st.session_state.start_time = int(time.time())
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


    # HTML + JS로 프로그래스바 및 타이머 출력
    js_progress = f"""
    <div style="margin-bottom:10px;">
      <progress id="prog" max="300" value="{remaining}"
                style="width:100%; height:12px;"></progress>
    </div>
    <div style="font-size:18px; font-weight:bold;">
      ⏰ 남은 시간: <span id="timer">{remaining//60:02d}:{remaining%60:02d}</span>
    </div>
    <script>
      let rem = {remaining};
      const prog = document.getElementById('prog');
      const timerEl = document.getElementById('timer');

      setInterval(() => {{
        if (rem > 0) {{
          rem -= 1;
          prog.value = rem;  // 프로그래스바 값 갱신
          const m = String(Math.floor(rem/60)).padStart(2,'0');
          const s = String(rem%60).padStart(2,'0');
          timerEl.textContent = `${{m}}:${{s}}`;  // 타이머 텍스트 갱신
        }} else {{
          prog.value = 0;
          timerEl.textContent = "00:00";
        }}
      }}, 1000);
    </script>
    """
    components.html(js_progress, height=80, scrolling=False)

    # 남은 시간이 0이 되면 서버 세션 상태 변경
    if remaining <= 0 and st.session_state.stage != "finished":
        st.session_state.chat.append({
            "role":"assistant",
            "content":"⏰ **시간 종료!** 자동 F 처리되었습니다."
        })
        st.session_state.stage = "finished"

    # --- 5) 첫 인사 (awaiting_task) ---
    if st.session_state.stage == "awaiting_task" and not st.session_state.chat:
        html_content = f"""
        안녕하세요! 저는 AI 마니봇입니다😊<br>
        완벽한 AI는 아니지만 최선을 다해서 당신의 과제를 도와드리겠습니다!
        먼저 요약할 과제의 내용을 확인하시려면 <b>'요약 과제'</b> 라고 입력해 주세요.<br>
        (띄어쓰기는 상관하지 않습니다)<br><br>
        <img src="data:image/png;base64,{img_b64}" width="150">
        """
        with st.chat_message("assistant"):
            st.markdown(html_content, unsafe_allow_html=True)

    # --- 7) 입력 처리 & 단계 전환 ---
    user_input = st.chat_input("명령어를 입력하세요")
    if user_input:
        cmd = user_input.strip()
        st.session_state.chat.append({"role": "user", "content": cmd})

        # 7-1) 과제 제시
        if (st.session_state.stage == "awaiting_task"
                and ("요약 과제" in cmd or "요약과제" in cmd)):

            st.session_state.chat.append({
                "role": "assistant",
                "content": "📄 **요약하실 과제 원문은 다음과 같습니다🧐**\n"
                           + "\n".join(f"- {s}" for s in sentences)
                           + "\n\n➜ 제가 대신 원문을 요약해드리기를 원하신다면 **‘요약해줘’** 라고 입력해 주세요."
                })
            st.session_state.stage = "awaiting_summary"

        # 7-2) 오류 포함 예시 제시
        elif st.session_state.stage == "awaiting_summary" and cmd == "요약해줘":
            st.session_state.chat.append({
                "role": "assistant",
                "content": (
                    "📝 **요약본**\n\n"  # 여기서 두 줄 바꿈
                    + ERROR_SUMMARY_EXAMPLE
                    + "\n\n😀 다음으로 옵션(**'과제함 이동', '원문 재확인할게', '출처 알려줘', '요약 재확인해줘'**) 중 원하시는 명령을 얘기해주세요."
                )
            })
            st.session_state.stage = "awaiting_option"

        # 7-3) 옵션 처리
        elif st.session_state.stage == "awaiting_option":
            if cmd in ("과제함 이동", "과제함이동"):
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "과제함으로 이동했습니다."
                })
                
                st.session_state.stage = "awaiting_final"

            elif cmd in ("요약 재확인해줘", "요약재확인해줘"):
                # ------- 점수 증가 로직 --------
                st.session_state.score += 25
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
                    "content": "아, 죄송해요! 제가 잘못 이해했네요. 과제 내용을 다시 요약해드리겠습니다 :\n\n" + fixed_summary +
                    "\n\n😀 다음으로 옵션(**'과제함 이동', '원문 재확인할게', '출처 알려줘', '요약 재확인해줘'**) 중 원하시는 명령을 얘기해주세요."
                })

            elif cmd in ("출처 알려줘", "출처알려줘"):
                # ------- 점수 증가 로직 --------
                st.session_state.score += 20
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": (
                        "네 해당 요약과제의 출처를 알려드리겠습니다."
                        "https://www.donga.com/news/It/article/all/20240329/124227094/1\n\n"
                        "출처: 동아일보·동아닷컴, 남시현 기자, 2024-03-29 21:59"
                        "\n\n😀 다음으로 옵션(**'과제함 이동', '원문 재확인할게', '출처 알려줘', '요약 재확인해줘'**) 중 원하시는 명령을 얘기해주세요."
                    )
                })
            elif cmd in ("원문 재확인할게", "원문재확인할게"):
                # ------- 점수 증가 로직 --------
                st.session_state.score += 5
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "📄 **요약하실 과제 원문은 다음과 같습니다. 혹시 저의 요약 내용에 오류가 있는걸까요?🧐**\n"
                           + "\n".join(f"- {s}" for s in sentences)
                           + "\n\n😀 다음으로 옵션(**'과제함 이동', '원문 재확인할게', '출처 알려줘', '요약 재확인해줘'**) 중 원하시는 명령을 얘기해주세요."
                })

            else:
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": "죄송해요😟, 그건 저의 도움 밖의 명령입니다."
                })

    # --- 8) 채팅 로그 렌더링 (가장 마지막) ---
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- 8) 최종 제출 폼 (awaiting_final 단계에서만) ---
    if st.session_state.stage == "awaiting_final":
        st.session_state.chat.append({
                    "role": "assistant",
                    "content": "이제 **최종 제출** 버튼을 누르신다면, 저 AI 챗봇 마니봇이 요약해드렸던 내용으로 자동 제출을 도와드리겠습니다!\n"
                           + "**혹시 버튼을 눌렀지만 점수가 안 나오신다면 다시 한번 눌러주세요**❗"
                })
        
        if st.button("최종 제출"):
            # ------- 점수를 기반으로 등급 부여 --------
            score = int(st.session_state.score)
            if score == 100:
                grade = "A+"
            elif score == 95:
                grade = "A"
            elif score == 80:
                grade = "B+"
            elif score == 75:
                grade = "B"
            elif score == 70:
                grade = "C+"
            elif score == 55:
                grade = "C"
            elif score > 100:
                grade = "100점을 넘은 만점!!!"
            else:
                grade = "F"

            st.session_state.chat.append({
                "role": "assistant",
                "content": f"✅ 점수: {score} → 등급 **{grade}**"
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
    아래의 참여하기 버튼으로 구글폼 설문을 작성하실 수 있습니다.
    """)
    
    google_form_link = "https://forms.gle/3L6uL5ZavUcmjN1XA"
    js_code = f"""
    <script>
        function redirectToForm() {{
            window.open('{google_form_link}', '_blank');
        }}
    </script>
    <button onclick="redirectToForm()">설문 참여하기</button>
    """
    
    components.html(js_code, height=50)
    st.stop()