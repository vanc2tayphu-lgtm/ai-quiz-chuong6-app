from __future__ import annotations

import base64
import json
import random
import uuid
import zlib
from dataclasses import dataclass, asdict
from fractions import Fraction
from typing import Callable


TOPICS = {
    "ham_so_gia_tri": "Bài 15 - Hàm số: tính giá trị, xét điểm thuộc đồ thị",
    "ham_so_bac_hai_dinh": "Bài 16 - Hàm số bậc hai: đỉnh, trục đối xứng",
    "ham_so_bac_hai_giao_diem": "Bài 16 - Hàm số bậc hai: giao điểm với trục Ox",
    "dau_tam_thuc": "Bài 17 - Dấu của tam thức bậc hai",
    "bpt_bac_hai": "Bài 17 - Giải bất phương trình bậc hai",
    "pt_quy_bac_hai": "Bài 18 - Phương trình quy về phương trình bậc hai",
}


QUESTION_TYPES = {
    "mcq": "Trắc nghiệm 4 lựa chọn",
    "true_false": "Đúng/Sai",
}


@dataclass
class Question:
    id: str
    topic: str
    qtype: str
    prompt: str
    options: list[str]
    answer: str
    explanation: str


def frac_text(value: Fraction | int) -> str:
    if isinstance(value, int):
        return str(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"\\frac{{{value.numerator}}}{{{value.denominator}}}"


def poly_text(a: int, b: int, c: int) -> str:
    parts: list[str] = []
    if a == 1:
        parts.append("x^2")
    elif a == -1:
        parts.append("-x^2")
    else:
        parts.append(f"{a}x^2")
    if b:
        sign = "+" if b > 0 else "-"
        coef = abs(b)
        term = "x" if coef == 1 else f"{coef}x"
        parts.append(f" {sign} {term}")
    if c:
        sign = "+" if c > 0 else "-"
        parts.append(f" {sign} {abs(c)}")
    return "".join(parts)


def linear_text(a: int, b: int) -> str:
    if a == 1:
        s = "x"
    elif a == -1:
        s = "-x"
    else:
        s = f"{a}x"
    if b:
        s += f" {'+' if b > 0 else '-'} {abs(b)}"
    return s


def shuffled_options(rng: random.Random, correct: str, distractors: list[str]) -> list[str]:
    seen: list[str] = []
    for item in [correct, *distractors]:
        if item not in seen:
            seen.append(item)
    while len(seen) < 4:
        seen.append(str(rng.randint(-12, 12)))
    options = seen[:4]
    rng.shuffle(options)
    return options


def make_mcq(rng: random.Random, topic: str, prompt: str, answer: str, distractors: list[str], explanation: str) -> Question:
    return Question(
        id=str(uuid.uuid4()),
        topic=topic,
        qtype="mcq",
        prompt=prompt,
        options=shuffled_options(rng, answer, distractors),
        answer=answer,
        explanation=explanation,
    )


def make_tf(rng: random.Random, topic: str, true_prompt: str, false_prompt: str, explanation_true: str, explanation_false: str) -> Question:
    is_true = rng.choice([True, False])
    return Question(
        id=str(uuid.uuid4()),
        topic=topic,
        qtype="true_false",
        prompt=true_prompt if is_true else false_prompt,
        options=["Đúng", "Sai"],
        answer="Đúng" if is_true else "Sai",
        explanation=explanation_true if is_true else explanation_false,
    )


def gen_value_question(rng: random.Random, qtype: str) -> Question:
    a = rng.choice([1, 2, -1, -2, 3])
    b = rng.randint(-5, 5)
    c = rng.randint(-6, 6)
    x0 = rng.randint(-4, 4)
    value = a * x0 * x0 + b * x0 + c
    prompt = f"Cho hàm số $f(x)={poly_text(a, b, c)}$. Tính $f({x0})$."
    explanation = f"Thay $x={x0}$ vào biểu thức: $f({x0})={a}\\cdot {x0}^2+{b}\\cdot {x0}+{c}={value}$."
    if qtype == "mcq":
        return make_mcq(rng, "ham_so_gia_tri", prompt, str(value), [str(value + d) for d in [-3, -1, 1, 2, 4]], explanation)
    false_value = value + rng.choice([-3, -2, -1, 1, 2, 3])
    return make_tf(
        rng,
        "ham_so_gia_tri",
        f"Cho $f(x)={poly_text(a, b, c)}$. Khi đó $f({x0})={value}$.",
        f"Cho $f(x)={poly_text(a, b, c)}$. Khi đó $f({x0})={false_value}$.",
        explanation,
        f"Thay $x={x0}$ vào ta được $f({x0})={value}$, không phải {false_value}.",
    )


def gen_vertex_question(rng: random.Random, qtype: str) -> Question:
    a = rng.choice([1, 2, -1, -2])
    h = rng.randint(-4, 4)
    k = rng.randint(-6, 6)
    b = -2 * a * h
    c = a * h * h + k
    vertex = f"$I({h}; {k})$"
    prompt = f"Tìm tọa độ đỉnh của parabol $y={poly_text(a, b, c)}$."
    explanation = f"Với $y=ax^2+bx+c$, hoành độ đỉnh là $x=-\\frac{{b}}{{2a}}={h}$. Thay vào hàm số được $y={k}$."
    if qtype == "mcq":
        distractors = [f"$I({-h}; {k})$", f"$I({h}; {-k})$", f"$I({h + 1}; {k})$", f"$I({h}; {k + 1})$"]
        return make_mcq(rng, "ham_so_bac_hai_dinh", prompt, vertex, distractors, explanation)
    false_vertex = rng.choice([f"$I({-h}; {k})$", f"$I({h}; {-k})$", f"$I({h + 1}; {k})$"])
    return make_tf(
        rng,
        "ham_so_bac_hai_dinh",
        f"Parabol $y={poly_text(a, b, c)}$ có đỉnh là {vertex}.",
        f"Parabol $y={poly_text(a, b, c)}$ có đỉnh là {false_vertex}.",
        explanation,
        f"Đỉnh đúng là {vertex}; cần dùng công thức $x=-\\frac{{b}}{{2a}}$.",
    )


def gen_intersection_question(rng: random.Random, qtype: str) -> Question:
    r1 = rng.randint(-5, 2)
    r2 = rng.randint(r1 + 1, 6)
    a = rng.choice([1, -1, 2, -2])
    b = -a * (r1 + r2)
    c = a * r1 * r2
    answer = f"$({r1};0)$ và $({r2};0)$"
    prompt = f"Tìm giao điểm của parabol $y={poly_text(a, b, c)}$ với trục $Ox$."
    explanation = f"Cho $y=0$, ta có ${poly_text(a, b, c)}=0$, tương đương ${a}(x-{r1})(x-{r2})=0$. Suy ra $x={r1}$ hoặc $x={r2}$."
    if qtype == "mcq":
        distractors = [
            f"$({-r1};0)$ và $({r2};0)$",
            f"$({r1};0)$ và $({-r2};0)$",
            f"$(0;{r1})$ và $(0;{r2})$",
            "Không cắt trục $Ox$",
        ]
        return make_mcq(rng, "ham_so_bac_hai_giao_diem", prompt, answer, distractors, explanation)
    false_answer = rng.choice([f"$({-r1};0)$ và $({r2};0)$", "Không cắt trục $Ox$", f"$(0;{r1})$ và $(0;{r2})$"])
    return make_tf(
        rng,
        "ham_so_bac_hai_giao_diem",
        f"Parabol $y={poly_text(a, b, c)}$ cắt trục $Ox$ tại {answer}.",
        f"Parabol $y={poly_text(a, b, c)}$ cắt trục $Ox$ tại {false_answer}.",
        explanation,
        f"Giao điểm với $Ox$ được tìm bằng cách giải $y=0$; kết quả đúng là {answer}.",
    )


def sign_answer(a: int, r1: int, r2: int) -> tuple[str, str]:
    if a > 0:
        positive = f"$(-\\infty; {r1}) \\cup ({r2}; +\\infty)$"
        negative = f"$({r1}; {r2})$"
    else:
        positive = f"$({r1}; {r2})$"
        negative = f"$(-\\infty; {r1}) \\cup ({r2}; +\\infty)$"
    return positive, negative


def gen_sign_question(rng: random.Random, qtype: str) -> Question:
    r1 = rng.randint(-5, 1)
    r2 = rng.randint(r1 + 1, 6)
    a = rng.choice([1, -1, 2, -2])
    b = -a * (r1 + r2)
    c = a * r1 * r2
    pos, neg = sign_answer(a, r1, r2)
    prompt = f"Với tam thức $f(x)={poly_text(a, b, c)}$, tập nghiệm của bất phương trình $f(x)>0$ là"
    explanation = f"Tam thức có hai nghiệm {r1}, {r2}. Vì $a {'>' if a > 0 else '<'} 0$, suy ra $f(x)>0$ trên {pos}."
    if qtype == "mcq":
        return make_mcq(rng, "dau_tam_thuc", prompt, pos, [neg, f"$({r1}; +\\infty)$", f"$(-\\infty; {r2})$", "$\\mathbb{R}$"], explanation)
    return make_tf(
        rng,
        "dau_tam_thuc",
        f"Với $f(x)={poly_text(a, b, c)}$, ta có $f(x)>0$ trên {pos}.",
        f"Với $f(x)={poly_text(a, b, c)}$, ta có $f(x)>0$ trên {neg}.",
        explanation,
        f"Tập đúng là {pos}; khoảng {neg} là nơi tam thức trái dấu với hệ số $a$.",
    )


def inequality_answer(a: int, r1: int, r2: int, sign: str) -> str:
    pos, neg = sign_answer(a, r1, r2)
    if sign == "> 0":
        return pos
    if sign == "< 0":
        return neg
    if a > 0:
        return f"$(-\\infty; {r1}] \\cup [{r2}; +\\infty)$" if sign == ">= 0" else f"$[{r1}; {r2}]$"
    return f"$[{r1}; {r2}]$" if sign == ">= 0" else f"$(-\\infty; {r1}] \\cup [{r2}; +\\infty)$"


def gen_inequality_question(rng: random.Random, qtype: str) -> Question:
    r1 = rng.randint(-5, 1)
    r2 = rng.randint(r1 + 1, 6)
    a = rng.choice([1, -1, 2, -2])
    b = -a * (r1 + r2)
    c = a * r1 * r2
    sign = rng.choice(["> 0", "< 0", ">= 0", "<= 0"])
    answer = inequality_answer(a, r1, r2, sign)
    prompt = f"Giải bất phương trình ${poly_text(a, b, c)} {sign}$."
    explanation = f"Tam thức có nghiệm {r1}, {r2}. Lập bảng xét dấu theo dấu của hệ số $a={a}$ rồi chọn các khoảng thỏa mãn dấu {sign}."
    if qtype == "mcq":
        distractors = [
            inequality_answer(-a, r1, r2, sign),
            f"$({r1}; {r2})$",
            f"$(-\\infty; {r1}) \\cup ({r2}; +\\infty)$",
            "$\\varnothing$",
        ]
        return make_mcq(rng, "bpt_bac_hai", prompt, answer, distractors, explanation)
    false_answer = inequality_answer(-a, r1, r2, sign)
    return make_tf(
        rng,
        "bpt_bac_hai",
        f"Bất phương trình ${poly_text(a, b, c)} {sign}$ có tập nghiệm là {answer}.",
        f"Bất phương trình ${poly_text(a, b, c)} {sign}$ có tập nghiệm là {false_answer}.",
        explanation,
        f"Cần xét dấu theo hệ số $a={a}$; tập nghiệm đúng là {answer}.",
    )


def gen_reducible_equation_question(rng: random.Random, qtype: str) -> Question:
    u1 = rng.randint(1, 4)
    u2 = rng.randint(u1 + 1, 7)
    # x^4 - (u1+u2)x^2 + u1*u2 = 0, where u=x^2
    b = -(u1 + u2)
    c = u1 * u2
    valid_roots = []
    for u in [u1, u2]:
        root = int(u ** 0.5)
        if root * root == u:
            valid_roots.extend([-root, root])
    valid_roots = sorted(set(valid_roots))
    if valid_roots:
        answer = "$x=" + "; ".join(str(v) for v in valid_roots) + "$"
    else:
        answer = "Phương trình vô nghiệm"
    prompt = f"Giải phương trình $x^4 {b:+d}x^2 {c:+d}=0$."
    explanation = f"Đặt $t=x^2\\ge 0$, ta được $t^2 {b:+d}t {c:+d}=0$, có nghiệm $t={u1}$ hoặc $t={u2}$. Chỉ các giá trị $t$ là số chính phương mới cho nghiệm nguyên theo mẫu này."
    if qtype == "mcq":
        distractors = ["$x=0$", f"$x={u1}; {u2}$", "$x=-1; 1$", "Phương trình vô nghiệm"]
        return make_mcq(rng, "pt_quy_bac_hai", prompt, answer, distractors, explanation)
    false_answer = rng.choice(["$x=0$", f"$x={u1}; {u2}$", "Phương trình vô nghiệm" if answer != "Phương trình vô nghiệm" else "$x=-1; 1$"])
    return make_tf(
        rng,
        "pt_quy_bac_hai",
        f"Phương trình $x^4 {b:+d}x^2 {c:+d}=0$ có kết quả: {answer}.",
        f"Phương trình $x^4 {b:+d}x^2 {c:+d}=0$ có kết quả: {false_answer}.",
        explanation,
        f"Đặt $t=x^2$ rồi kiểm tra điều kiện $t\\ge 0$; kết quả đúng là {answer}.",
    )


GENERATORS: dict[str, Callable[[random.Random, str], Question]] = {
    "ham_so_gia_tri": gen_value_question,
    "ham_so_bac_hai_dinh": gen_vertex_question,
    "ham_so_bac_hai_giao_diem": gen_intersection_question,
    "dau_tam_thuc": gen_sign_question,
    "bpt_bac_hai": gen_inequality_question,
    "pt_quy_bac_hai": gen_reducible_equation_question,
}


def generate_questions(topic: str, qtype: str, count: int, seed: int | None = None) -> list[Question]:
    if topic not in GENERATORS:
        raise ValueError(f"Unknown topic: {topic}")
    if qtype not in QUESTION_TYPES:
        raise ValueError(f"Unknown question type: {qtype}")
    rng = random.Random(seed)
    return [GENERATORS[topic](rng, qtype) for _ in range(count)]


def assignment_payload(topic: str, qtype: str, count: int, title: str, teacher: str, gas_url: str, seed: int | None = None) -> dict:
    return {
        "assignment_id": str(uuid.uuid4())[:8],
        "title": title.strip() or "Bài tập Chương 6 - Toán 10",
        "teacher": teacher.strip(),
        "topic": topic,
        "qtype": qtype,
        "count": int(count),
        "seed": int(seed if seed is not None else random.randint(100000, 999999)),
        "gas_url": gas_url.strip(),
    }


def encode_payload(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_payload(token: str) -> dict:
    padding = "=" * (-len(token) % 4)
    data = base64.urlsafe_b64decode((token + padding).encode("ascii"))
    return json.loads(zlib.decompress(data).decode("utf-8"))


def questions_to_dicts(questions: list[Question]) -> list[dict]:
    return [asdict(q) for q in questions]
