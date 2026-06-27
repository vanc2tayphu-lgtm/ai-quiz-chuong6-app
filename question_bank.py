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
    "true_false": "Đúng/Sai 4 ý",
    "short_answer": "Trả lời ngắn",
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
    statements: list[dict] | None = None


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


def make_statement(label: str, text: str, answer: bool, explanation: str) -> dict:
    return {
        "label": label,
        "text": text,
        "answer": "Đúng" if answer else "Sai",
        "explanation": explanation,
    }


def make_true_false_group(topic: str, prompt: str, statements: list[dict]) -> Question:
    answer = "; ".join(f"{item['label']}) {item['answer']}" for item in statements)
    return Question(
        id=str(uuid.uuid4()),
        topic=topic,
        qtype="true_false",
        prompt=prompt,
        options=["Đúng", "Sai"],
        answer=answer,
        explanation="Chọn Đúng hoặc Sai cho từng ý a), b), c), d).",
        statements=statements,
    )


def decimal_comma(value: int | float | Fraction) -> str:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        raw = f"{value.numerator / value.denominator:.2f}"
    elif isinstance(value, float):
        raw = f"{value:.2f}"
    else:
        return str(value)
    raw = raw.rstrip("0").rstrip(".")
    return raw.replace(".", ",")


def gen_true_false_group_question(rng: random.Random, topic: str) -> Question:
    if topic == "ham_so_gia_tri":
        a = rng.choice([1, 2, -1, -2])
        b = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        c = rng.randint(-5, 5)
        x0 = rng.randint(-3, 3)
        x1 = rng.randint(-3, 3)
        y0 = a * x0 * x0 + b * x0 + c
        y1 = a * x1 * x1 + b * x1 + c
        wrong = y0 + rng.choice([-3, -2, -1, 1, 2, 3])
        prompt = f"Cho hàm số $f(x)={poly_text(a, b, c)}$. Xét tính đúng sai của các mệnh đề sau:"
        statements = [
            make_statement("a", f"$f({x0})={y0}$.", True, f"Thay $x={x0}$ vào hàm số được {y0}."),
            make_statement("b", f"Điểm $M({x1}; {y1})$ thuộc đồ thị hàm số.", True, f"Vì $f({x1})={y1}$ nên điểm đã cho thuộc đồ thị."),
            make_statement("c", f"Phương trình $f(x)={c}$ có hai nghiệm là $x=0$ và $x={frac_text(Fraction(-b, a))}$.", True, "Vì $f(x)=c$ tương đương $ax^2+bx=0$."),
            make_statement("d", f"Đồ thị hàm số cắt trục $Oy$ tại điểm $(0; {wrong})$.", False, f"Đồ thị cắt trục $Oy$ tại $(0; {c})$."),
        ]
        return make_true_false_group(topic, prompt, statements)

    if topic == "ham_so_bac_hai_dinh":
        a = rng.choice([1, 2, -1, -2])
        h = rng.randint(-4, 4)
        k = rng.randint(-5, 5)
        b = -2 * a * h
        c = a * h * h + k
        prompt = f"Cho parabol $(P): y={poly_text(a, b, c)}$. Xét tính đúng sai của các mệnh đề sau:"
        statements = [
            make_statement("a", f"Trục đối xứng của $(P)$ là đường thẳng $x={h}$.", True, "Trục đối xứng có phương trình $x=-\\frac{b}{2a}$."),
            make_statement("b", f"Tọa độ đỉnh của $(P)$ là $I({h}; {k})$.", True, "Thay hoành độ đỉnh vào hàm số được tung độ đỉnh."),
            make_statement("c", f"Giá trị {'nhỏ nhất' if a > 0 else 'lớn nhất'} của hàm số bằng {k}.", True, "Giá trị cực trị của hàm số bậc hai chính là tung độ đỉnh."),
            make_statement("d", f"Bất phương trình ${poly_text(a, b, c)} {'<=' if a > 0 else '>='} {k}$ đúng với mọi số thực $x$.", False, f"Ta có $y={a}(x-{h})^2+{k}$ nên dấu bất đẳng thức trong mệnh đề bị ngược."),
        ]
        return make_true_false_group(topic, prompt, statements)

    if topic == "ham_so_bac_hai_giao_diem":
        r1 = rng.randint(-4, 1)
        r2 = rng.randint(r1 + 1, 5)
        a = rng.choice([1, -1, 2, -2])
        b = -a * (r1 + r2)
        c = a * r1 * r2
        prompt = f"Cho parabol $(P): y={poly_text(a, b, c)}$. Xét tính đúng sai của các mệnh đề sau:"
        statements = [
            make_statement("a", f"$(P)$ cắt trục $Ox$ tại $({r1};0)$ và $({r2};0)$.", True, "Giao điểm với Ox là nghiệm của phương trình y=0."),
            make_statement("b", f"$(P)$ cắt trục $Oy$ tại $(0;{c})$.", True, "Cho x=0 thì y=c."),
            make_statement("c", f"Tổng hoành độ hai giao điểm với $Ox$ bằng {r1 + r2}.", True, "Hai hoành độ là hai nghiệm r1 và r2."),
            make_statement("d", f"Đường thẳng $y={c}$ cắt $(P)$ tại hai điểm có hoành độ đối nhau.", False, f"Giải $y={c}$ được $x=0$ hoặc $x={r1+r2}$, không nhất thiết là hai số đối nhau."),
        ]
        return make_true_false_group(topic, prompt, statements)

    if topic in {"dau_tam_thuc", "bpt_bac_hai"}:
        r1 = rng.randint(-4, 1)
        r2 = rng.randint(r1 + 1, 5)
        a = rng.choice([1, -1, 2, -2])
        b = -a * (r1 + r2)
        c = a * r1 * r2
        pos, neg = sign_answer(a, r1, r2)
        prompt = f"Cho tam thức $f(x)={poly_text(a, b, c)}$. Xét tính đúng sai của các mệnh đề sau:"
        statements = [
            make_statement("a", f"Tam thức có hai nghiệm là $x={r1}$ và $x={r2}$.", True, "Tam thức được tạo từ hai nghiệm này."),
            make_statement("b", f"$f(x)>0$ trên {pos}.", True, "Dựa vào dấu của hệ số a và hai nghiệm."),
            make_statement("c", f"Tập nghiệm của bất phương trình $f(x)\\le 0$ là {inequality_answer(a, r1, r2, '<= 0')}.", True, "Lấy thêm hai nghiệm vì dấu là không dương."),
            make_statement("d", f"Tập nghiệm của bất phương trình $f(x)\\ge 0$ là {neg}.", False, f"Với dấu không âm, tập nghiệm đúng là {inequality_answer(a, r1, r2, '>= 0')}."),
        ]
        return make_true_false_group(topic, prompt, statements)

    u1 = rng.choice([1, 4])
    u2 = rng.choice([9, 16])
    b = -(u1 + u2)
    c = u1 * u2
    roots = sorted({-int(u1**0.5), int(u1**0.5), -int(u2**0.5), int(u2**0.5)})
    prompt = f"Cho phương trình $x^4 {b:+d}x^2 {c:+d}=0$. Xét tính đúng sai của các mệnh đề sau:"
    statements = [
        make_statement("a", "Có thể đặt $t=x^2$ để đưa phương trình về bậc hai.", True, "Đây là phương trình trùng phương."),
        make_statement("b", f"Phương trình theo $t$ có hai nghiệm $t={u1}$ và $t={u2}$.", True, "Thay t=x^2 vào phương trình."),
        make_statement("c", f"Phương trình ban đầu có {len(roots)} nghiệm thực.", True, "Mỗi nghiệm dương của t cho hai nghiệm x đối nhau."),
        make_statement("d", f"Tổng bình phương tất cả các nghiệm thực của phương trình bằng {u1+u2}.", False, f"Mỗi giá trị t dương cho hai nghiệm đối nhau, tổng bình phương đúng là {2*(u1+u2)}."),
    ]
    return make_true_false_group(topic, prompt, statements)


def gen_short_answer_question(rng: random.Random, topic: str) -> Question:
    if topic == "ham_so_gia_tri":
        a = rng.choice([1, 2, -1, -2, 3])
        b = rng.randint(-5, 5)
        c = rng.randint(-6, 6)
        x0 = rng.randint(-4, 4)
        value = a * x0 * x0 + b * x0 + c
        prompt = f"Cho hàm số $f(x)={poly_text(a, b, c)}$. Tính $f({x0})$."
        answer = decimal_comma(value)
        explanation = f"Thay $x={x0}$ vào hàm số, ta được $f({x0})={answer}$."
    elif topic == "ham_so_bac_hai_dinh":
        a = rng.choice([1, 2, -1, -2])
        h = rng.randint(-4, 4)
        k = rng.randint(-5, 5)
        b = -2 * a * h
        c = a * h * h + k
        ask_x = rng.choice([True, False])
        prompt = f"Cho parabol $y={poly_text(a, b, c)}$. {'Tính hoành độ' if ask_x else 'Tính tung độ'} đỉnh của parabol."
        answer = decimal_comma(h if ask_x else k)
        explanation = f"Đỉnh là $I({h}; {k})$."
    elif topic == "ham_so_bac_hai_giao_diem":
        r1 = rng.randint(-4, 1)
        r2 = rng.randint(r1 + 1, 6)
        a = rng.choice([1, -1, 2, -2])
        b = -a * (r1 + r2)
        c = a * r1 * r2
        prompt = f"Parabol $y={poly_text(a, b, c)}$ cắt trục $Ox$ tại hai điểm có hoành độ $x_1, x_2$. Tính $x_1+x_2$."
        answer = decimal_comma(r1 + r2)
        explanation = f"Hai nghiệm là {r1} và {r2}, nên tổng bằng {r1 + r2}."
    elif topic in {"dau_tam_thuc", "bpt_bac_hai"}:
        r1 = rng.randint(-4, 1)
        r2 = rng.randint(r1 + 1, 6)
        a = rng.choice([1, -1, 2, -2])
        b = -a * (r1 + r2)
        c = a * r1 * r2
        prompt = f"Tam thức $f(x)={poly_text(a, b, c)}$ có hai nghiệm $x_1<x_2$. Tính $x_2-x_1$."
        answer = decimal_comma(r2 - r1)
        explanation = f"Hai nghiệm là {r1} và {r2}, nên $x_2-x_1={r2-r1}$."
    else:
        u1 = rng.choice([1, 4])
        u2 = rng.choice([9, 16])
        b = -(u1 + u2)
        c = u1 * u2
        prompt = f"Phương trình $x^4 {b:+d}x^2 {c:+d}=0$ có bao nhiêu nghiệm thực?"
        answer = "4"
        explanation = f"Đặt $t=x^2$, được $t={u1}$ hoặc $t={u2}$; mỗi giá trị dương của t cho hai nghiệm x."
    return Question(
        id=str(uuid.uuid4()),
        topic=topic,
        qtype="short_answer",
        prompt=prompt,
        options=[],
        answer=answer,
        explanation=explanation,
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
    if qtype == "true_false":
        questions = [gen_true_false_group_question(rng, topic) for _ in range(count)]
    elif qtype == "short_answer":
        questions = [gen_short_answer_question(rng, topic) for _ in range(count)]
    else:
        questions = [GENERATORS[topic](rng, qtype) for _ in range(count)]
    stable_seed = seed if seed is not None else "random"
    for index, question in enumerate(questions, start=1):
        question.id = f"{topic}-{qtype}-{stable_seed}-{index}"
        if question.statements:
            for statement in question.statements:
                statement["id"] = f"{question.id}-{statement['label']}"
    return questions


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
