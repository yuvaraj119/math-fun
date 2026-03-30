import json
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

print("Loading Addition Quiz...")

st.session_state["current_page"] = "addition"

SESSIONS_FILE = Path("sessions.json")

ADDITION_LEVELS = {
    "Beginner (1-10)": (1, 10),
    "Intermediate (1-50)": (1, 50),
    "Advanced (1-100)": (1, 100),
}


def _safe_load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_sessions() -> list[dict]:
    return _safe_load_json(SESSIONS_FILE, [])


def append_session(session_row: dict) -> None:
    sessions = load_sessions()
    sessions.append(session_row)
    _safe_save_json(SESSIONS_FILE, sessions)


def settings_fingerprint(level_name: str, min_num: int, max_num: int, total_q: int, seconds_per_q: int) -> str:
    return json.dumps(
        {
            "operation": "addition",
            "level": str(level_name),
            "operand_min": int(min_num),
            "operand_max": int(max_num),
            "total_q": int(total_q),
            "seconds_per_q": int(seconds_per_q),
        },
        sort_keys=True,
    )


def reset_quiz_state():
    for key in [
        "quiz_started",
        "quiz_finished",
        "order",
        "idx",
        "score",
        "attempts",
        "start_ts",
        "deadline_ts",
        "current_q",
        "history",
        "last_feedback",
        "mode_meta",
        "seconds_per_q",
        "session_id",
        "finalized_session",
        "active_settings_fp",
    ]:
        st.session_state.pop(key, None)


def generate_addition_questions(min_num: int, max_num: int, total_q: int) -> list[tuple[int, int]]:
    all_pairs = [
        (num1, num2)
        for num1 in range(min_num, max_num + 1)
        for num2 in range(min_num, max_num + 1)
    ]
    random.shuffle(all_pairs)

    if total_q <= len(all_pairs):
        return all_pairs[:total_q]

    out = all_pairs[:]
    while len(out) < total_q:
        out.append(random.choice(all_pairs))
    random.shuffle(out)
    return out


def start_quiz(level_name: str, min_num: int, max_num: int, total_q: int, seconds_per_q: int):
    order = generate_addition_questions(min_num, max_num, total_q)

    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False
    st.session_state.finalized_session = False

    st.session_state.order = order
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.last_feedback = ""
    st.session_state.current_q = order[0]
    st.session_state.seconds_per_q = int(seconds_per_q)

    st.session_state.mode_meta = {
        "operation": "addition",
        "level": level_name,
        "operand_min": int(min_num),
        "operand_max": int(max_num),
        "total_q": int(total_q),
        "seconds_per_q": int(seconds_per_q),
    }

    now = time.time()
    st.session_state.start_ts = now
    st.session_state.deadline_ts = now + int(seconds_per_q)
    st.session_state.session_id = f"add-{int(now)}-{random.randint(1000,9999)}"


def advance_question_or_finish():
    st.session_state.idx += 1
    if st.session_state.idx >= len(st.session_state.order):
        st.session_state.quiz_finished = True
        return

    st.session_state.current_q = st.session_state.order[st.session_state.idx]
    now = time.time()
    st.session_state.start_ts = now
    st.session_state.deadline_ts = now + int(st.session_state.seconds_per_q)


def record_result(result: str, your_answer, correct: int, elapsed_s: float):
    num1, num2 = st.session_state.current_q
    st.session_state.history.append(
        {
            "num1": num1,
            "num2": num2,
            "your_answer": your_answer,
            "correct": correct,
            "result": result,
            "elapsed_s": float(elapsed_s),
        }
    )


def record_timeout():
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    elapsed = time.time() - float(st.session_state.start_ts)

    record_result("TIMEOUT", None, correct, elapsed)
    st.session_state.last_feedback = f"⏰ Time's up! Correct: **{num1} + {num2} = {correct}**"
    advance_question_or_finish()


def submit_answer(answer_text: str):
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    st.session_state.attempts += 1
    elapsed = time.time() - float(st.session_state.start_ts)

    try:
        answer = int(answer_text.strip())
    except Exception:
        record_result("INVALID", answer_text, correct, elapsed)
        st.session_state.last_feedback = "⚠ Please enter a whole number."
        return

    if answer == correct:
        st.session_state.score += 1
        record_result("CORRECT", answer, correct, elapsed)
        st.session_state.last_feedback = f"✅ Correct! **{num1} + {num2} = {correct}**"
    else:
        record_result("WRONG", answer, correct, elapsed)
        st.session_state.last_feedback = f"❌ Wrong. Correct: **{num1} + {num2} = {correct}**"

    advance_question_or_finish()


def compute_speed(history: list[dict]) -> dict:
    if not history:
        return {"avg_time_all": 0.0, "avg_time_answered": 0.0, "qpm": 0.0}

    all_times = [entry["elapsed_s"] for entry in history if isinstance(entry.get("elapsed_s"), (int, float))]
    answered_times = [
        entry["elapsed_s"]
        for entry in history
        if entry.get("result") in ("CORRECT", "WRONG") and isinstance(entry.get("elapsed_s"), (int, float))
    ]

    avg_all = sum(all_times) / len(all_times) if all_times else 0.0
    avg_answered = sum(answered_times) / len(answered_times) if answered_times else 0.0
    qpm = (60.0 / avg_answered) if avg_answered > 0 else 0.0
    return {"avg_time_all": avg_all, "avg_time_answered": avg_answered, "qpm": qpm}


st.set_page_config(page_title="Addition Quiz", page_icon="➕", layout="centered")
st.title("➕ Addition Quiz")

with st.sidebar:
    st.header("Settings")
    level_name = st.selectbox("Level", list(ADDITION_LEVELS.keys()), index=1)
    min_num, max_num = ADDITION_LEVELS[level_name]
    total_q = st.number_input("Total questions", min_value=1, max_value=500, value=20, step=1)
    seconds_per_q = st.slider("Timer per question (seconds)", 2, 60, 10, 1)
    st.caption(f"Operand range: **{min_num}..{max_num}**")

    fp_now = settings_fingerprint(level_name, min_num, max_num, total_q, seconds_per_q)
    mode_meta = st.session_state.get("mode_meta", {})

    if mode_meta and mode_meta.get("operation") not in (None, "addition"):
        reset_quiz_state()

    prev_page = st.session_state.get("last_page_seen")
    if prev_page and prev_page != "addition" and st.session_state.get("quiz_finished", False):
        reset_quiz_state()

    if st.session_state.get("quiz_finished", False):
        last_fp = st.session_state.get("last_settings_fp")
        if last_fp and last_fp != fp_now:
            reset_quiz_state()

    st.session_state["last_page_seen"] = "addition"
    st.session_state["last_settings_fp"] = fp_now

    c1, c2 = st.columns(2)
    start_btn = c1.button("▶ Start / Restart", use_container_width=True)
    stop_btn = c2.button("⏹ Stop", use_container_width=True)

    if stop_btn:
        reset_quiz_state()
        st.success("Quiz stopped.")

    if start_btn:
        reset_quiz_state()
        start_quiz(level_name, int(min_num), int(max_num), int(total_q), int(seconds_per_q))
        st.session_state["active_settings_fp"] = fp_now
        st.rerun()

if not st.session_state.get("quiz_started", False):
    st.info("Choose settings and press **Start**.")
    st.caption("Addition sessions are saved to sessions.json and appear in the Dashboard.")
    st.stop()

if st.session_state.get("quiz_finished", False):
    meta = st.session_state.mode_meta
    history = st.session_state.history
    total = len(st.session_state.order)
    score = int(st.session_state.score)

    correct_n = sum(1 for entry in history if entry["result"] == "CORRECT")
    wrong_n = sum(1 for entry in history if entry["result"] == "WRONG")
    timeout_n = sum(1 for entry in history if entry["result"] == "TIMEOUT")
    invalid_n = sum(1 for entry in history if entry["result"] == "INVALID")
    answered_n = correct_n + wrong_n
    accuracy = (correct_n / answered_n * 100.0) if answered_n else 0.0
    speed = compute_speed(history)

    if not st.session_state.get("finalized_session", False):
        st.session_state.finalized_session = True
        append_session(
            {
                "session_id": st.session_state.session_id,
                "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
                "operation": "addition",
                "level": meta["level"],
                "operand_min": meta["operand_min"],
                "operand_max": meta["operand_max"],
                "seconds_per_q": meta["seconds_per_q"],
                "total_q": total,
                "score": score,
                "correct": correct_n,
                "wrong": wrong_n,
                "timeout": timeout_n,
                "invalid": invalid_n,
                "answered": answered_n,
                "accuracy_pct": round(accuracy, 2),
                "avg_time_all_s": round(speed["avg_time_all"], 3),
                "avg_time_answered_s": round(speed["avg_time_answered"], 3),
                "speed_q_per_min": round(speed["qpm"], 3),
            }
        )

    st.header("✅ Quiz finished!")
    st.markdown(
        f"<div style='font-size:44px;font-weight:900;'>Final Score: {score} / {total}</div>",
        unsafe_allow_html=True,
    )

    st.subheader("Speed")
    st.write(f"- Avg time per question (including timeouts): **{speed['avg_time_all']:.2f}s**")
    st.write(f"- Avg time per answered question (correct/wrong): **{speed['avg_time_answered']:.2f}s**")
    st.write(f"- Speed: **{speed['qpm']:.2f} questions/min**")

    st.subheader("Overall totals")
    st.write(f"Total questions: **{total}**")
    st.write(
        f"✅ Correct: **{correct_n}**   |   ❌ Wrong: **{wrong_n}**   |   ⏰ Timeout: **{timeout_n}**   |   ⚠ Invalid: **{invalid_n}**"
    )
    st.write(f"🎯 Accuracy (correct/answered): **{accuracy:.2f}%**")
    st.write(f"Level: **{meta['level']}** | Range: **{meta['operand_min']}..{meta['operand_max']}**")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Play again"):
            reset_quiz_state()
            start_quiz(
                meta["level"],
                int(meta["operand_min"]),
                int(meta["operand_max"]),
                int(meta["total_q"]),
                int(meta["seconds_per_q"]),
            )
            st.session_state["active_settings_fp"] = settings_fingerprint(
                meta["level"],
                int(meta["operand_min"]),
                int(meta["operand_max"]),
                int(meta["total_q"]),
                int(meta["seconds_per_q"]),
            )
            st.rerun()
    with col_b:
        st.page_link("pages/Dashboard.py", label="Go to Dashboard", icon="📊")

    st.stop()

now = time.time()
deadline = float(st.session_state.deadline_ts)
remaining = max(0, int(deadline - now))

if remaining <= 0:
    record_timeout()
    st.rerun()

total = len(st.session_state.order)
idx = int(st.session_state.idx) + 1
score = int(st.session_state.score)
meta = st.session_state.mode_meta

st.markdown(
    f"""
<div style="display:flex;justify-content:space-between;align-items:center;">
  <div style="font-size:40px;font-weight:900;">Score: {score} / {total}</div>
  <div style="font-size:52px;font-weight:900; padding: 12px 22px; border-radius: 16px;
              border: 4px solid #999; min-width: 160px; text-align:center;">
    ⏳ {remaining}s
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write(
    f"Mode: **{meta['level']}** | Range: **{meta['operand_min']}..{meta['operand_max']}** | "
    f"Question: **{idx}/{total}** | Timer: **{meta['seconds_per_q']}s**"
)
st.progress((idx - 1) / total)

num1, num2 = st.session_state.current_q
st.subheader(f"What is {num1} + {num2} ?")

if st.session_state.get("last_feedback"):
    st.write(st.session_state.last_feedback)

with st.form("answer_form", clear_on_submit=True):
    answer_text = st.text_input("Your answer", placeholder="Type a number and press Submit")
    submitted = st.form_submit_button("Submit")

if submitted:
    submit_answer(answer_text)
    st.rerun()

time.sleep(0.25)
st.rerun()
