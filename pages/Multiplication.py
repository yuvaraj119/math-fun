import json
import time
import random
import hashlib
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.session_state["current_page"] = "multiplication"

SCORES_FILE = Path("best_scores.json")
SESSIONS_FILE = Path("sessions.json")

LEVELS = {
    "Easy (1–6)": 6,
    "Medium (1–12)": 12,
    "Hard (1–20)": 20,
}


# ----------------------------
# JSON helpers
# ----------------------------
def _safe_load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_best_scores() -> dict:
    return _safe_load_json(SCORES_FILE, {})


def save_best_scores(scores: dict) -> None:
    _safe_save_json(SCORES_FILE, scores)


def load_sessions() -> list[dict]:
    return _safe_load_json(SESSIONS_FILE, [])


def append_session(session_row: dict) -> None:
    sessions = load_sessions()
    sessions.append(session_row)
    _safe_save_json(SESSIONS_FILE, sessions)


def make_mode_key(tables: list[int], level_name: str, total_q: int, seconds_per_q: int) -> str:
    payload = {
        "operation": "multiplication",
        "tables": sorted(tables),
        "level": level_name,
        "total_q": total_q,
        "seconds_per_q": seconds_per_q,
    }
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def update_best_score(mode_key: str, todays_score: int, total_q: int) -> tuple[bool, dict]:
    scores = load_best_scores()
    today = str(date.today())

    if mode_key not in scores:
        scores[mode_key] = {}

    prev = scores[mode_key].get(today)
    is_new_best = prev is None or int(prev.get("score", -1)) < int(todays_score)

    if is_new_best:
        scores[mode_key][today] = {
            "score": int(todays_score),
            "out_of": int(total_q),
            "updated_at_epoch": int(time.time()),
        }
        save_best_scores(scores)

    return is_new_best, scores[mode_key].get(today, prev or {})


def get_today_best(mode_key: str) -> dict | None:
    scores = load_best_scores()
    return scores.get(mode_key, {}).get(str(date.today()))


# ----------------------------
# Settings fingerprint + breakdown
# ----------------------------
def settings_fingerprint(tables, level_name, total_q, seconds_per_q):
    return json.dumps(
        {
            "tables": sorted([int(x) for x in tables]),
            "level": str(level_name),
            "total_q": int(total_q),
            "seconds_per_q": int(seconds_per_q),
        },
        sort_keys=True,
    )


def per_table_breakdown(history: list[dict]) -> pd.DataFrame:
    buckets = {}
    for h in history:
        t = h.get("table")
        if t is None:
            continue
        buckets.setdefault(
            t, {"table": t, "total": 0, "correct": 0, "wrong": 0, "timeout": 0, "invalid": 0}
        )
        buckets[t]["total"] += 1
        r = h.get("result")
        if r == "CORRECT":
            buckets[t]["correct"] += 1
        elif r == "WRONG":
            buckets[t]["wrong"] += 1
        elif r == "TIMEOUT":
            buckets[t]["timeout"] += 1
        elif r == "INVALID":
            buckets[t]["invalid"] += 1

    rows = []
    for t in sorted(buckets.keys()):
        b = buckets[t]
        answered = b["correct"] + b["wrong"]
        acc = (b["correct"] / answered * 100.0) if answered > 0 else 0.0
        b["accuracy_pct"] = round(acc, 2)
        rows.append(b)

    return pd.DataFrame(rows)


# ----------------------------
# Quiz helpers
# ----------------------------
def reset_quiz_state():
    for k in [
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
        "mode_key",
        "mode_meta",
        "seconds_per_q",
        "session_id",
        "finalized_session",
        "celebrated",
    ]:
        st.session_state.pop(k, None)


def generate_questions(tables: list[int], max_multiplier: int, total_q: int) -> list[tuple[int, int]]:
    all_pairs = [(t, m) for t in tables for m in range(1, max_multiplier + 1)]
    random.shuffle(all_pairs)

    if total_q <= len(all_pairs):
        return all_pairs[:total_q]

    out = all_pairs[:]
    while len(out) < total_q:
        out.append(random.choice(all_pairs))
    random.shuffle(out)
    return out


def start_quiz(tables: list[int], level_name: str, max_multiplier: int, total_q: int, seconds_per_q: int):
    order = generate_questions(tables, max_multiplier, total_q)

    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False
    st.session_state.finalized_session = False
    st.session_state.celebrated = False

    st.session_state.order = order
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.last_feedback = ""
    st.session_state.current_q = order[0]
    st.session_state.seconds_per_q = int(seconds_per_q)

    st.session_state.mode_key = make_mode_key(tables, level_name, total_q, seconds_per_q)
    st.session_state.mode_meta = {
        "operation": "multiplication",
        "tables": sorted(tables),
        "level": level_name,
        "multiplier_max": int(max_multiplier),
        "total_q": int(total_q),
        "seconds_per_q": int(seconds_per_q),
    }

    now = time.time()
    st.session_state.start_ts = now
    st.session_state.deadline_ts = now + int(seconds_per_q)
    st.session_state.session_id = f"mul-{int(now)}-{random.randint(1000,9999)}"


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
    t, m = st.session_state.current_q
    st.session_state.history.append(
        {
            "table": t,
            "multiplier": m,
            "your_answer": your_answer,
            "correct": correct,
            "result": result,
            "elapsed_s": float(elapsed_s),
        }
    )


def record_timeout():
    t, m = st.session_state.current_q
    correct = t * m
    elapsed = time.time() - float(st.session_state.start_ts)

    record_result("TIMEOUT", None, correct, elapsed)
    st.session_state.last_feedback = f"⏰ Time's up! Correct: **{t} × {m} = {correct}**"
    advance_question_or_finish()


def submit_answer(answer_text: str):
    t, m = st.session_state.current_q
    correct = t * m
    st.session_state.attempts += 1
    elapsed = time.time() - float(st.session_state.start_ts)

    try:
        ans = int(answer_text.strip())
    except Exception:
        record_result("INVALID", answer_text, correct, elapsed)
        st.session_state.last_feedback = "⚠️ Please enter a whole number."
        return

    if ans == correct:
        st.session_state.score += 1
        record_result("CORRECT", ans, correct, elapsed)
        st.session_state.last_feedback = f"✅ Correct! **{t} × {m} = {correct}**"
    else:
        record_result("WRONG", ans, correct, elapsed)
        st.session_state.last_feedback = f"❌ Wrong. Correct: **{t} × {m} = {correct}**"

    advance_question_or_finish()


def compute_speed(history: list[dict]) -> dict:
    if not history:
        return {"avg_time_all": 0.0, "avg_time_answered": 0.0, "qpm": 0.0}

    all_times = [h["elapsed_s"] for h in history if isinstance(h.get("elapsed_s"), (int, float))]
    answered_times = [
        h["elapsed_s"]
        for h in history
        if h.get("result") in ("CORRECT", "WRONG") and isinstance(h.get("elapsed_s"), (int, float))
    ]

    avg_all = sum(all_times) / len(all_times) if all_times else 0.0
    avg_ans = sum(answered_times) / len(answered_times) if answered_times else 0.0
    qpm = (60.0 / avg_ans) if avg_ans > 0 else 0.0
    return {"avg_time_all": avg_all, "avg_time_answered": avg_ans, "qpm": qpm}


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Multiplication Quiz", page_icon="✖️", layout="centered")
st.title("✖️ Multiplication Quiz")

with st.sidebar:
    st.header("Settings")
    tables = st.multiselect("Select tables", options=list(range(2, 21)), default=[2, 3, 4, 5])
    level_name = st.selectbox("Level", list(LEVELS.keys()), index=1)
    max_multiplier = LEVELS[level_name]
    total_q = st.number_input("Total questions", min_value=1, max_value=500, value=20, step=1)
    seconds_per_q = st.slider("Timer per question (seconds)", 2, 60, 10, 1)
    st.caption(f"Multiplier range: **1..{max_multiplier}**")

    # auto-clear rules
    fp_now = settings_fingerprint(tables, level_name, total_q, seconds_per_q)

    prev_page = st.session_state.get("last_page_seen")
    if prev_page and prev_page != "multiplication" and st.session_state.get("quiz_finished", False):
        reset_quiz_state()

    if st.session_state.get("quiz_finished", False):
        last_fp = st.session_state.get("last_settings_fp")
        if last_fp and last_fp != fp_now:
            reset_quiz_state()

    st.session_state["last_page_seen"] = "multiplication"
    st.session_state["last_settings_fp"] = fp_now

    # Best score today for this mode
    if tables:
        mode_preview = make_mode_key([int(x) for x in tables], level_name, int(total_q), int(seconds_per_q))
        best = get_today_best(mode_preview)
        if best:
            st.success(f"🏆 Today best (this mode): **{best['score']} / {best['out_of']}**")
        else:
            st.info("No best saved today for this mode yet.")

    c1, c2 = st.columns(2)
    start_btn = c1.button("▶️ Start / Restart", use_container_width=True, disabled=(len(tables) == 0))
    stop_btn = c2.button("⏹️ Stop", use_container_width=True)

    if stop_btn:
        reset_quiz_state()
        st.success("Quiz stopped.")

    if start_btn:
        reset_quiz_state()
        start_quiz([int(x) for x in tables], level_name, int(max_multiplier), int(total_q), int(seconds_per_q))
        st.session_state["active_settings_fp"] = fp_now
        st.rerun()

# Landing (before start)
if not st.session_state.get("quiz_started", False):
    st.info("Choose settings and press **Start**.")
    st.caption("Sessions are saved to sessions.json. Best scores saved to best_scores.json.")
    st.stop()

# Finished summary (show + save)
if st.session_state.get("quiz_finished", False):
    meta = st.session_state.mode_meta
    hist = st.session_state.history
    total = len(st.session_state.order)
    score = int(st.session_state.score)

    correct_n = sum(1 for h in hist if h["result"] == "CORRECT")
    wrong_n = sum(1 for h in hist if h["result"] == "WRONG")
    timeout_n = sum(1 for h in hist if h["result"] == "TIMEOUT")
    invalid_n = sum(1 for h in hist if h["result"] == "INVALID")
    answered_n = correct_n + wrong_n
    accuracy = (correct_n / answered_n * 100.0) if answered_n else 0.0

    speed = compute_speed(hist)
    table_df = per_table_breakdown(hist)

    # Save ONLY once
    if not st.session_state.get("finalized_session", False):
        st.session_state.finalized_session = True

        update_best_score(st.session_state.mode_key, score, total)

        append_session(
            {
                "session_id": st.session_state.session_id,
                "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
                "operation": "multiplication",
                "tables": meta["tables"],
                "level": meta["level"],
                "multiplier_max": meta["multiplier_max"],
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

    # Balloons only once per session
    if not st.session_state.get("celebrated", False):
        st.session_state["celebrated"] = True
        st.balloons()

    st.header("✅ Quiz finished!")
    st.markdown(
        f"<div style='font-size:44px;font-weight:900;'>Final Score: {score} / {total}</div>",
        unsafe_allow_html=True,
    )

    # Best score today display
    is_new_best, today_entry = update_best_score(st.session_state.mode_key, score, total)
    if is_new_best:
        st.success(f"🏆 New best today (this mode): **{today_entry['score']} / {today_entry['out_of']}**")
    else:
        if today_entry:
            st.info(f"🏆 Today best (this mode): **{today_entry.get('score')} / {today_entry.get('out_of')}**")

    st.subheader("Speed")
    st.write(f"- Avg time per question (including timeouts): **{speed['avg_time_all']:.2f}s**")
    st.write(f"- Avg time per answered question (correct/wrong): **{speed['avg_time_answered']:.2f}s**")
    st.write(f"- Speed: **{speed['qpm']:.2f} questions/min**")

    st.subheader("Overall totals")
    st.write(f"Total questions: **{total}**")
    st.write(
        f"✅ Correct: **{correct_n}**   |   ❌ Wrong: **{wrong_n}**   |   ⏰ Timeout: **{timeout_n}**   |   ⚠️ Invalid: **{invalid_n}**"
    )
    st.write(f"🎯 Accuracy (correct/answered): **{accuracy:.2f}%**")

    st.subheader("Per-table breakdown")
    if table_df.empty:
        st.info("No table breakdown available.")
    else:
        st.dataframe(
            table_df[["table", "total", "correct", "wrong", "timeout", "invalid", "accuracy_pct"]],
            use_container_width=True,
            hide_index=True,
        )

    colA, colB = st.columns(2)
    with colA:
        if st.button("Play again"):
            reset_quiz_state()
            st.rerun()
    with colB:
        st.page_link("pages/Dashboard.py", label="Go to Dashboard", icon="📊")

    st.stop()

# Live quiz screen
now = time.time()
deadline = float(st.session_state.deadline_ts)
remaining = max(0, int(deadline - now))

# Timeout
if remaining <= 0:
    record_timeout()
    st.rerun()

total = len(st.session_state.order)
idx = int(st.session_state.idx) + 1
score = int(st.session_state.score)
meta = st.session_state.mode_meta

# Big score + big clock
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
    f"Mode: **{meta['level']}** | Tables: **{meta['tables']}** | "
    f"Question: **{idx}/{total}** | Timer: **{meta['seconds_per_q']}s**"
)
st.progress((idx - 1) / total)

t, m = st.session_state.current_q
st.subheader(f"What is {t} × {m} ?")

if st.session_state.get("last_feedback"):
    st.write(st.session_state.last_feedback)

with st.form("answer_form", clear_on_submit=True):
    ans_text = st.text_input("Your answer", placeholder="Type a number and press Submit")
    submitted = st.form_submit_button("Submit")

if submitted:
    submit_answer(ans_text)
    st.rerun()

time.sleep(0.25)
st.rerun()
