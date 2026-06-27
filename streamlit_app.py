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


st.set_page_config(page_title="AI Quiz Chương 6 Toán 10", page_icon="AI", layout="wide")


def apply_mobile_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1120px;
            padding-top: 1.25rem;
        }
        .student-shell .stRadio [role="radiogroup"] {
            gap: 0.45rem;
        }
        .student-shell .stRadio label {
            border: 1px solid #d7dde8;
            border-radius: 10px;
            padding: 0.7rem 0.8rem;
            background: #ffffff;
            min-height: 44px;
            align-items: center;
        }
        .student-shell .stRadio label:hover {
            border-color: #2563eb;
            background: #f8fbff;
        }
        .student-meta {
            color: #4b5563;
            font-size: 0.95rem;
            margin-bottom: 0.75rem;
        }
        .teacher-link input {
            font-size: 0.92rem !important;
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 0.8rem 0.85rem 5rem;
            }
            h1 {
                font-size: 1.55rem !important;
                line-height: 1.22 !important;
            }
            h2 {
                font-size: 1.25rem !important;
            }
            h3 {
                font-size: 1.08rem !important;
            }
            p, li, label, div[data-testid="stMarkdownContainer"] {
                font-size: 1rem;
            }
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            .student-shell .stRadio [role="radiogroup"] {
                display: flex;
                flex-direction: column;
            }
            .student-shell .stRadio label {
                width: 100%;
                min-height: 50px;
                font-size: 1rem;
            }
            .stButton > button, .stDownloadButton > button {
                width: 100%;
                min-height: 46px;
            }
            .teacher-link input {
                font-size: 0.82rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_query_params() -> dict:
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()


def set_query_params(**kwargs) -> None:
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


def default_gas_url() -> str:
    try:
        return st.secrets.get("GAS_WEB_APP_URL", "")
    except Exception:
        return ""


def render_question(i: int, q: dict, key_prefix: str, allow_empty: bool = False):
    st.markdown(f"**Câu {i}.** {q['prompt']}")
    return st.radio(
        "Chọn đáp án",
        q["options"],
        key=f"{key_prefix}_{q['id']}",
        horizontal=False,
        index=None if allow_empty else 0,
        label_visibility="collapsed",
    )


def submit_to_google_script(gas_url: str, payload: dict) -> tuple[bool, str]:
    if not gas_url:
        return False, "Chưa cấu hình Google Apps Script URL."
    try:
        response = requests.post(gas_url, json=payload, timeout=20)
        if 200 <= response.status_code < 300:
            return True, response.text[:300]
        return False, f"HTTP {response.status_code}: {response.text[:300]}"
    except Exception as exc:
        return False, str(exc)


def google_sheet_help() -> None:
    with st.expander("Thiết lập Google Sheet nhận kết quả"):
        st.markdown(
            """
            1. Tạo một Google Sheet mới.
            2. Vào **Extensions -> Apps Script**.
            3. Dán nội dung file `google_apps_script.gs` trong repo GitHub.
            4. Bấm **Deploy -> New deployment -> Web app**.
            5. Chọn **Execute as: Me** và **Who has access: Anyone**.
            6. Copy **Web app URL** rồi dán vào ô cấu hình trong app.

            Sau khi học sinh nộp bài, script sẽ tự tạo 2 sheet:
            `KetQua` để xem điểm tổng hợp và `ChiTiet` để xem từng câu học sinh chọn.
            """
        )


def teacher_page() -> None:
    st.title("Tạo bài tập online Chương 6 - Toán 10")
    st.caption(
        "Giáo viên chọn dạng toán, số câu và loại câu hỏi; ứng dụng tạo link để học sinh làm bài "
        "và gửi kết quả về Google Sheet thông qua Google Apps Script."
    )

    with st.sidebar:
        st.header("Cấu hình bài tập")
        title = st.text_input("Tên bài tập", "Luyện tập Chương 6 - Toán 10")
        teacher = st.text_input("Tên giáo viên", "")
        topic = st.selectbox("Dạng toán", list(TOPICS), format_func=lambda k: TOPICS[k])
        qtype = st.radio("Loại câu hỏi", list(QUESTION_TYPES), format_func=lambda k: QUESTION_TYPES[k])
        count = st.slider("Số câu", min_value=3, max_value=30, value=10)
        seed = st.number_input("Mã đề/seed", min_value=1, max_value=999999, value=12345, step=1)
        gas_url = st.text_input(
            "Google Apps Script Web App URL",
            value=default_gas_url(),
            placeholder="https://script.google.com/macros/s/.../exec",
        )
        generate = st.button("Tạo bài tập", type="primary", use_container_width=True)

    if generate or "teacher_payload" not in st.session_state:
        st.session_state.teacher_payload = assignment_payload(topic, qtype, count, title, teacher, gas_url, seed)

    payload = st.session_state.teacher_payload
    questions = generate_questions(payload["topic"], payload["qtype"], payload["count"], payload["seed"])
    token = encode_payload(payload)
    student_link = app_url_with_payload(token)

    col1, col2 = st.columns([1.3, 0.7], gap="large")
    with col1:
        st.subheader(payload["title"])
        st.write(f"**Dạng toán:** {TOPICS[payload['topic']]}")
        st.write(f"**Loại câu hỏi:** {QUESTION_TYPES[payload['qtype']]}")
        st.write(f"**Số câu:** {payload['count']} | **Mã đề:** {payload['seed']} | **Mã bài:** {payload['assignment_id']}")
        st.markdown('<div class="teacher-link">', unsafe_allow_html=True)
        st.text_input("Link giao cho học sinh", student_link)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "Tải dữ liệu câu hỏi JSON",
            data=json.dumps({"assignment": payload, "questions": questions_to_dicts(questions)}, ensure_ascii=False, indent=2),
            file_name=f"bai-tap-chuong-6-{payload['assignment_id']}.json",
            mime="application/json",
        )
    with col2:
        st.info("Sau khi deploy lên Streamlit Community Cloud, link giao bài là link thật để học sinh mở trên điện thoại.")
        if payload["gas_url"]:
            st.success("Đã có Google Apps Script URL. Kết quả học sinh sẽ được gửi về Google Sheet.")
        else:
            st.warning("Chưa có Google Apps Script URL. Học sinh vẫn làm được nhưng kết quả chưa gửi về Google Sheet.")
        google_sheet_help()

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


def student_page(payload: dict) -> None:
    st.markdown('<div class="student-shell">', unsafe_allow_html=True)
    st.title(payload["title"])
    st.markdown(
        f"""
        <div class="student-meta">
        Mã bài: <b>{payload['assignment_id']}</b> | Dạng: <b>{TOPICS[payload['topic']]}</b> |
        Số câu: <b>{payload['count']}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    questions = questions_to_dicts(generate_questions(payload["topic"], payload["qtype"], payload["count"], payload["seed"]))

    with st.form("student_quiz_form"):
        st.subheader("Thông tin học sinh")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Họ và tên học sinh")
        with col2:
            student_class = st.text_input("Lớp")

        st.subheader("Bài làm")
        answers: dict[str, str | None] = {}
        for i, q in enumerate(questions, 1):
            with st.container(border=True):
                answers[q["id"]] = render_question(i, q, "student", allow_empty=True)

        submitted = st.form_submit_button("Nộp bài", type="primary", use_container_width=True)

    if submitted:
        if not student_name.strip() or not student_class.strip():
            st.error("Em cần nhập đầy đủ họ tên và lớp trước khi nộp bài.")
            st.stop()
        unanswered = [i for i, q in enumerate(questions, 1) if answers.get(q["id"]) is None]
        if unanswered:
            st.error("Em chưa chọn đáp án cho câu: " + ", ".join(map(str, unanswered)))
            st.stop()

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
                icon = "Đúng" if item["is_correct"] else "Sai"
                st.markdown(f"**Câu {item['index']} - {icon}**")
                st.markdown(f"Em chọn: `{item['selected']}` | Đáp án đúng: `{item['correct_answer']}`")
                st.markdown(item["explanation"])

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    apply_mobile_css()
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
