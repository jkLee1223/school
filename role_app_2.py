import streamlit as st
from datetime import datetime
import os

# 교사용 비밀번호 설정
TEACHER_PASSWORD = "rytkdyd"  #이 값을 비번으으로 적절히 설정(교사용 영타) 

# 파일 이름 생성 함수
def get_filename(month):
    return f"1인 1역 결산({month}월).txt"

# 제출 처리 함수
def submit(writer, bestst, bestst_reason, worstst, worstst_reason, suggestion, month):
    filename = get_filename(month)

    with open(filename, "a", encoding="utf-8") as f:
        if bestst and bestst_reason:
            f.write(f"BESTST,{bestst},{bestst_reason} ({writer})\n")
        if worstst and worstst_reason:
            f.write(f"WORSTST,{worstst},{worstst_reason} ({writer})\n")
        if suggestion:
            f.write(f"SUGGESTION, ,{suggestion} ({writer})\n")

    st.success(f"제출 완료! '{filename}' 파일에 저장되었습니다.")

# 통계 보기 함수
def show_stats(month):
    filename = get_filename(month)
    if not os.path.exists(filename):
        st.warning(f"{month}월 결산 파일이 없습니다.")
        return

    stats = {}
    suggestions = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",", 2)
            if len(parts) < 3:
                continue
            category, name, reason = parts

            if category == "SUGGESTION":
                suggestions.append(reason.strip())
                continue

            if "(" in reason and reason.endswith(")"):
                reason_text = reason[:reason.rfind("(")].strip()
                writer = reason[reason.rfind("("):].strip()
            else:
                reason_text = reason.strip()
                writer = ""

            if name not in stats:
                stats[name] = {"열심히 함": [], "노력 필요": []}

            if category == "BESTST":
                stats[name]["열심히 함"].append(f"{reason_text} {writer}")
            elif category == "WORSTST":
                stats[name]["노력 필요"].append(f"{reason_text} {writer}")

    st.subheader(f"📊 {month}월 통계 보기")

    if suggestions:
        st.markdown("### 📌 건의사항")
        for s in suggestions:
            st.write(f"- {s}")
        st.markdown("---")

    for name in sorted(stats.keys()):
        best = stats[name]["열심히 함"]
        worst = stats[name]["노력 필요"]
        st.markdown(f"#### {name}")
        st.write(f"- 열심히 함: {len(best)}회")
        if best:
            st.write(", ".join(best))
        st.write(f"- 노력 필요: {len(worst)}회")
        if worst:
            st.write(", ".join(worst))

# 통계 저장 함수
def save_clean_stats(month):
    filename = get_filename(month)
    if not os.path.exists(filename):
        st.warning(f"{month}월 결산 파일이 없습니다.")
        return

    now = datetime.now()
    timestamp = now.strftime("%m%d_%H%M")
    save_filename = f"1인 1역 통계 정리본({month}월)_{timestamp}.txt"

    stats = {}
    suggestions = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",", 2)
            if len(parts) < 3:
                continue
            category, name, reason = parts

            if category == "SUGGESTION":
                suggestions.append(reason.strip())
                continue

            if "(" in reason and reason.endswith(")"):
                reason_text = reason[:reason.rfind("(")].strip()
                writer = reason[reason.rfind("("):].strip()
            else:
                reason_text = reason.strip()
                writer = ""

            if name not in stats:
                stats[name] = {"열심히 함": [], "노력 필요": []}

            if category == "BESTST":
                stats[name]["열심히 함"].append(f"{reason_text} {writer}")
            elif category == "WORSTST":
                stats[name]["노력 필요"].append(f"{reason_text} {writer}")

    with open(save_filename, "w", encoding="utf-8") as f:
        if suggestions:
            f.write("건의사항\n")
            for s in suggestions:
                f.write(f"- {s}\n")
            f.write("\n")

        for name in sorted(stats.keys()):
            best = stats[name]["열심히 함"]
            worst = stats[name]["노력 필요"]

            f.write(f"{name}\n")
            f.write(f"- 열심히 함 : {len(best)}회")
            if best:
                f.write(f" ({', '.join(best)})\n")
            else:
                f.write("\n")

            f.write(f"- 노력 필요 : {len(worst)}회")
            if worst:
                f.write(f" ({', '.join(worst)})\n")
            else:
                f.write("\n")
            f.write("\n")

    st.success(f"'{save_filename}' 파일로 통계가 저장되었습니다.")

# ---------- Streamlit 화면 구성 ----------
st.set_page_config(page_title="1인 1역 결산", layout="centered")

st.title("📋 1인 1역 결산 프로그램")

tab1, tab2 = st.tabs(["🧑‍🎓 학생용 제출", "👩‍🏫 교사용 메뉴"])

with tab1:
    st.markdown("#### ✍️ 작성자 정보를 입력하세요.")
    writer = st.text_input("작성자 이름", max_chars=20)

    st.markdown("#### ✅ 열심히 수행한 친구")
    bestst = st.text_input("이름 (열심히 한 친구)")
    bestst_reason = st.text_area("이유", height=70, key="bestst_reason")

    st.markdown("#### ⚠️ 노력이 필요한 친구")
    worstst = st.text_input("이름 (노력이 필요한 친구)")
    worstst_reason = st.text_area("이유", height=70, key="worstst_reason")

    st.markdown("#### 💡 우리 반에 건의합니다! (선택사항)")
    suggestion = st.text_area("건의사항", height=70, key="suggestion_text")

    selected_month = st.selectbox("📆 월 선택 (저장 구분용)", list(range(1, 13)), index=datetime.now().month - 1)

    if st.button("📤 제출하기", type="primary"):
        if not writer:
            st.warning("작성자 이름을 입력해주세요.")
        elif not (bestst and bestst_reason) and not (worstst and worstst_reason) and not suggestion:
            st.warning("하나 이상 내용을 입력해야 제출됩니다.")
        else:
            submit(writer, bestst, bestst_reason, worstst, worstst_reason, suggestion, selected_month)

with tab2:
    st.markdown("#### 🔒 교사용 기능 (비밀번호 필요)")
    password = st.text_input("비밀번호 입력", type="password")

    selected_month_teacher = st.selectbox("📅 확인/저장할 월 선택", list(range(1, 13)), index=datetime.now().month - 1)

    if password == TEACHER_PASSWORD:
        if st.button("📊 통계 보기"):
            show_stats(selected_month_teacher)
        if st.button("💾 통계 저장 (.txt)"):
            save_clean_stats(selected_month_teacher)

        st.markdown("---")
        st.markdown("#### 🗑️ 월별 기록 리셋 (주의!)")
        confirm_reset = st.checkbox("⚠️ 정말로 이 월의 데이터를 완전히 삭제하시겠습니까?")
        if confirm_reset:
            if st.button("🚨 선택한 월 기록 완전 삭제"):
                filename_to_delete = get_filename(selected_month_teacher)
                if os.path.exists(filename_to_delete):
                    os.remove(filename_to_delete)
                    st.success(f"{selected_month_teacher}월의 기록 파일이 삭제되었습니다.")
                else:
                    st.warning("해당 월에 저장된 파일이 없습니다.")

    elif password:
        st.error("비밀번호가 틀렸습니다.")

  
