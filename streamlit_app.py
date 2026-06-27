from __future__ import annotations

import json
from datetime import datetime

import requests
import streamlit as st

from question_bank import (
    QUESTION_TYPES,
    TOPICS,
    assignment_payload,
    decode_payload,
    encode_payload,
    generate_questions,
    questions_to_dicts,
)


st.set_page_config(page_title="AI Quiz Chương 6 Toán 10", page_icon="📘", layout="wide")


def get_query_params() -> dict:
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()


def set_query_params(**kwargs):
    try:
        st.query_params.clear()
        for key, value in kwargs.items():
            st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**kwargs)


def app_url_with_payload(token: str) -> str:
    try:
        base = st.context.url.split("?")[0]
    except Exception:
        base = ""
    return f"{base}?mode=student&a={token}" if base else f"?mode=student&a={token}"


def render_question(i: int, q: dict, key_prefix: str, disabled: bool = False):
    st.markdown(f"**Câu {i}.** {q['prompt']}")
    choice = st.radio(
        "Chọn đáp án",
        q["options"],
        key=f"{key_prefix}_{q['id']}",
        horizontal=q["qtype"] == "true_false",
        label_visibility="collapsed",
        disabled=disabled,
    )
    return choice


def submit_to_google_script(gas_url: str, payload: dict) -> tuple[bool, str]:
    if not gas_url:
        return False, "Chưa cấu hình Google Apps Script URL."
    try:
        response = requests.post(gas_url, json=payload, timeout=15)
        if 200 <= response.status_code < 300:
            return True, response.text[:300]
        return False, f"HTTP {response.status_code}: {response.text[:300]}"
    except Exception as exc:
        return False, str(exc)


def teacher_page():
    st.title("Tạo bài tập online Chương 6 - Toán 10")
    st.caption("Giáo viên chọn dạng toán, số câu và loại câu hỏi; ứng dụng tạo link để học sinh làm bài và gửi kết quả về Google Apps Script.")

    with st.sidebar:
        st.header("Cấu hình bài tập")
        title = st.text_input("Tên bài tập", "Luyện tập Chương 6 - Toán 10")
        teacher = st.text_input("Tên giáo viên", "")
        topic = st.selectbox("Dạng toán", list(TOPICS), format_func=lambda k: TOPICS[k])
        qtype = st.radio("Loại câu hỏi", list(QUESTION_TYPES), format_func=lambda k: QUESTION_TYPES[k])
        count = st.slider("Số câu", min_value=3, max_value=30, value=10)
        seed = st.number_input("Mã đề/seed", min_value=1, max_value=999999, value=12345, step=1)
        gas_url = st.text_input("Google Apps Script Web App URL", placeholder="https://script.google.com/macros/s/.../exec")
        generate = st.button("Tạo bài tập", type="primary", use_container_width=True)

    if generate or "teacher_payload" not in st.session_state:
        st.session_state.teacher_payload = assignment_payload(topic, qtype, count, title, teacher, gas_url, seed)

    payload = st.session_state.teacher_payload
    questions = generate_questions(payload["topic"], payload["qtype"], payload["count"], payload["seed"])
    token = encode_payload(payload)
    student_link = app_url_with_payload(token)

    col1, col2 = st.columns([1.2, 0.8], gap="large")
    with col1:
        st.subheader(payload["title"])
        st.write(f"**Dạng toán:** {TOPICS[payload['topic']]}")
        st.write(f"**Loại câu hỏi:** {QUESTION_TYPES[payload['qtype']]}")
        st.write(f"**Số câu:** {payload['count']} | **Mã đề:** {payload['seed']} | **Mã bài:** {payload['assignment_id']}")
        st.text_input("Link giao cho học sinh", student_link)
        st.download_button(
            "Tải dữ liệu câu hỏi JSON",
            data=json.dumps({"assignment": payload, "questions": questions_to_dicts(questions)}, ensure_ascii=False, indent=2),
            file_name=f"bai-tap-chuong-6-{payload['assignment_id']}.json",
            mime="application/json",
        )
    with col2:
        st.info("Khi triển khai lên Streamlit Community Cloud, link ở trên sẽ là link thật của app. Nếu chạy local, học sinh phải dùng cùng mạng hoặc bạn triển khai app trước.")
        if not payload["gas_url"]:
            st.warning("Chưa có Google Apps Script URL, học sinh vẫn làm được nhưng kết quả sẽ không gửi về Google Sheet.")

    st.divider()
    st.subheader("Xem trước đề")
    for i, q in enumerate(questions, 1):
        with st.container(border=True):
            st.markdown(f"**Câu {i}.** {q.prompt}")
            if q.qtype == "mcq":
                for label, option in zip(["A", "B", "C", "D"], q.options):
                    st.markdown(f"{label}. {option}")
            else:
                st.markdown("A. Đúng&nbsp;&nbsp;&nbsp;&nbsp;B. Sai")
            with st.expander("Đáp án và hướng dẫn"):
                st.markdown(f"**Đáp án:** {q.answer}")
                st.markdown(q.explanation)


def student_page(payload: dict):
    st.title(payload["title"])
    st.caption("Học sinh làm bài và bấm nộp. Kết quả sẽ được gửi về giáo viên nếu bài tập đã cấu hình Google Apps Script.")

    questions = questions_to_dicts(generate_questions(payload["topic"], payload["qtype"], payload["count"], payload["seed"]))
    with st.sidebar:
        st.header("Thông tin bài")
        st.write(f"**Mã bài:** {payload['assignment_id']}")
        st.write(f"**Dạng:** {TOPICS[payload['topic']]}")
        st.write(f"**Số câu:** {payload['count']}")
        student_name = st.text_input("Họ và tên học sinh")
        student_class = st.text_input("Lớp")

    if not student_name.strip() or not student_class.strip():
        st.warning("Em nhập họ tên và lớp trước khi làm bài.")

    answers: dict[str, str] = {}
    for i, q in enumerate(questions, 1):
        with st.container(border=True):
            answers[q["id"]] = render_question(i, q, "student")

    submitted = st.button("Nộp bài", type="primary", disabled=not student_name.strip() or not student_class.strip())
    if submitted:
        score = 0
        details = []
        for i, q in enumerate(questions, 1):
            selected = answers.get(q["id"])
            ok = selected == q["answer"]
            score += int(ok)
            details.append(
                {
                    "index": i,
                    "question": q["prompt"],
                    "selected": selected,
                    "correct_answer": q["answer"],
                    "is_correct": ok,
                    "explanation": q["explanation"],
                }
            )

        result = {
            "submitted_at": datetime.now().isoformat(timespec="seconds"),
            "assignment_id": payload["assignment_id"],
            "assignment_title": payload["title"],
            "teacher": payload.get("teacher", ""),
            "topic": TOPICS[payload["topic"]],
            "question_type": QUESTION_TYPES[payload["qtype"]],
            "seed": payload["seed"],
            "student_name": student_name.strip(),
            "student_class": student_class.strip(),
            "score": score,
            "total": len(questions),
            "percent": round(score * 100 / len(questions), 2),
            "details": details,
        }

        st.success(f"Em đạt {score}/{len(questions)} câu đúng ({result['percent']}%).")
        ok, message = submit_to_google_script(payload.get("gas_url", ""), result)
        if ok:
            st.success("Đã gửi kết quả về Google Sheet.")
        else:
            st.warning(f"Chưa gửi được về Google Sheet: {message}")

        with st.expander("Xem đáp án và lời giải"):
            for item in details:
                icon = "✅" if item["is_correct"] else "❌"
                st.markdown(f"**Câu {item['index']} {icon}**")
                st.markdown(f"Em chọn: `{item['selected']}` | Đáp án đúng: `{item['correct_answer']}`")
                st.markdown(item["explanation"])


def main():
    params = get_query_params()
    mode = params.get("mode", "teacher")
    token = params.get("a", "")
    if isinstance(mode, list):
        mode = mode[0]
    if isinstance(token, list):
        token = token[0]

    if mode == "student" and token:
        try:
            student_page(decode_payload(token))
        except Exception as exc:
            st.error(f"Link bài tập không hợp lệ: {exc}")
            if st.button("Về trang giáo viên"):
                set_query_params(mode="teacher")
    else:
        teacher_page()


if __name__ == "__main__":
    main()
