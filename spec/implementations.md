# Math Game Quiz - Implementation Details

## Current Implementation Summary

This document provides detailed implementation notes for the current Math Game Quiz application, explaining how requirements are implemented in code.

## Part 1: Core Quiz Architecture

### 1.1 Quiz State Management (`pages/Multiplication.py` lines 1-90)

**Implementation Pattern**: Streamlit session_state dictionary

**Key State Variables**:
```python
# Control state
st.session_state.quiz_started: bool          # Quiz initialization flag
st.session_state.quiz_finished: bool         # Quiz completion flag
st.session_state.finalized_session: bool     # Prevent duplicate saves
st.session_state.celebrated: bool            # Show balloons once

# Question management
st.session_state.order: list[tuple[int, int]]  # [(2,1), (3,2), ...]
st.session_state.idx: int                      # Current question index
st.session_state.current_q: tuple[int, int]    # Current question

# Scoring
st.session_state.score: int                    # Correct answer count
st.session_state.attempts: int                 # Total attempts
st.session_state.history: list[dict]           # Full answer history

# Timing
st.session_state.start_ts: float               # Question start time
st.session_state.deadline_ts: float            # Question deadline
st.session_state.seconds_per_q: int            # Timer setting

# Metadata
st.session_state.mode_key: str                 # SHA256 hash of config
st.session_state.mode_meta: dict               # Full config metadata
st.session_state.session_id: str               # Unique session ID
```


**Why This Pattern?**:
- Persists across Streamlit reruns
- Automatically serialized to browser storage
- No external session management needed
- Clean key-value access

---

### 1.2 Question Generation (`pages/Multiplication.py` lines 109-124)

**Function**: `generate_questions(tables: list[int], max_multiplier: int, total_q: int)`

**Algorithm**:
```python
def generate_questions(tables, max_multiplier, total_q):
    # Step 1: Create all possible combinations
    all_pairs = [
        (t, m) 
        for t in tables 
        for m in range(1, max_multiplier + 1)
    ]
    # Example: tables=[2,3], max=2 → [(2,1), (2,2), (3,1), (3,2)]
    
    # Step 2: Shuffle for randomness
    random.shuffle(all_pairs)
    
    # Step 3: Select required count
    if total_q <= len(all_pairs):
        return all_pairs[:total_q]
    
    # Step 4: If need more, add duplicates with re-shuffle
    out = all_pairs[:]
    while len(out) < total_q:
        out.append(random.choice(all_pairs))
    random.shuffle(out)
    return out
```

**Complexity**: O(n * m + n log n) where n=tables, m=multipliers  
**Time**: <100ms for typical settings (5 tables, max 12, 20 questions)  
**Space**: O(n * m) for question list

**Example Execution**:
```
Input: tables=[2,3,4], max_multiplier=12, total_q=20
Step 1: Create 36 pairs [(2,1)...(4,12)]
Step 2: Shuffle to random order
Step 3: Return first 20 questions in random order
Output: 20 questions, no duplicates
```

---

### 1.3 Quiz Initialization (`pages/Multiplication.py` lines 127-157)

**Function**: `start_quiz(tables, level_name, max_multiplier, total_q, seconds_per_q)`

**Implementation Details**:

```python
def start_quiz(...):
    # Generate question order
    order = generate_questions(tables, max_multiplier, total_q)
    
    # Set control flags
    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False
    st.session_state.finalized_session = False
    st.session_state.celebrated = False
    
    # Initialize quiz data
    st.session_state.order = order
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.current_q = order[0]  # First question
    st.session_state.seconds_per_q = int(seconds_per_q)
    
    # Create mode key for best score tracking
    st.session_state.mode_key = make_mode_key(
        tables, level_name, total_q, seconds_per_q
    )
    
    # Store full metadata for later
    st.session_state.mode_meta = {
        "operation": "multiplication",
        "tables": sorted(tables),
        "level": level_name,
        "multiplier_max": int(max_multiplier),
        "total_q": int(total_q),
        "seconds_per_q": int(seconds_per_q),
    }
    
    # Initialize timer
    now = time.time()
    st.session_state.start_ts = now
    st.session_state.deadline_ts = now + int(seconds_per_q)
    
    # Create unique session identifier
    st.session_state.session_id = f"mul-{int(now)}-{random.randint(1000,9999)}"
```

**Why This Approach?**:
- Centralizes initialization logic
- Ensures all state vars exist before quiz
- Creates unique session IDs (timestamp + random)
- Sets precise timer boundaries

---

### 1.4 Timer Mechanism (`pages/Multiplication.py` lines 308-323)

**Implementation**: Real-time countdown with auto-advance

**Code**:
```python
# Calculate remaining time
now = time.time()
deadline = float(st.session_state.deadline_ts)
remaining = max(0, int(deadline - now))

# Display timer in large font
st.markdown(
    f'<div style="font-size:52px;...">⏳ {remaining}s</div>',
    unsafe_allow_html=True
)

# Check for timeout
if remaining <= 0:
    record_timeout()
    st.rerun()

# Auto-rerun every 250ms to update display
time.sleep(0.25)
st.rerun()
```

**Why This Design?**:
- `max(0, ...)` prevents negative displays
- `int()` truncates to whole seconds (human-readable)
- `time.sleep(0.25) + st.rerun()` = ~250ms timer granularity
- Timeout detection is instantaneous

**Timing Accuracy**: ±250ms (acceptable for learning apps)

---

### 1.5 Answer Processing (`pages/Multiplication.py` lines 192-218)

**Function**: `submit_answer(answer_text: str)`

**Workflow**:
```python
def submit_answer(answer_text):
    # Get current question
    t, m = st.session_state.current_q
    correct = t * m
    
    # Track attempt
    st.session_state.attempts += 1
    
    # Calculate elapsed time
    elapsed = time.time() - float(st.session_state.start_ts)
    
    # Try to parse answer as integer
    try:
        ans = int(answer_text.strip())
    except Exception:
        # Invalid input → record and move on
        record_result("INVALID", answer_text, correct, elapsed)
        st.session_state.last_feedback = "⚠️ Please enter a whole number."
        return
    
    # Validate answer
    if ans == correct:
        st.session_state.score += 1
        record_result("CORRECT", ans, correct, elapsed)
        st.session_state.last_feedback = f"✅ Correct! **{t} × {m} = {correct}**"
    else:
        record_result("WRONG", ans, correct, elapsed)
        st.session_state.last_feedback = f"❌ Wrong. Correct: **{t} × {m} = {correct}**"
    
    # Move to next question
    advance_question_or_finish()
```

**Result Types**:
- `CORRECT`: ans == correct (score++)
- `WRONG`: ans != correct (no score)
- `TIMEOUT`: time expired (recorded separately)
- `INVALID`: non-numeric input (user error)

**Data Recorded**:
```python
{
    "table": 7,
    "multiplier": 8,
    "your_answer": 56,
    "correct": 56,
    "result": "CORRECT",
    "elapsed_s": 2.345
}
```

---

### 1.6 Results Summary (`pages/Multiplication.py` lines 251-308)

**Calculation Pipeline**:

```python
# Extract results
correct_n = sum(1 for h in hist if h["result"] == "CORRECT")
wrong_n = sum(1 for h in hist if h["result"] == "WRONG")
timeout_n = sum(1 for h in hist if h["result"] == "TIMEOUT")
invalid_n = sum(1 for h in hist if h["result"] == "INVALID")
answered_n = correct_n + wrong_n

# Accuracy percentage
accuracy = (correct_n / answered_n * 100.0) if answered_n else 0.0

# Speed metrics
speed = compute_speed(hist)
# {
#     "avg_time_all": 5.234,
#     "avg_time_answered": 5.234,
#     "qpm": 11.47
# }

# Per-table breakdown
table_df = per_table_breakdown(hist)
# DataFrame with columns: table, total, correct, wrong, timeout, invalid, accuracy_pct
```

**Display Example**:
```
Final Score: 18 / 20
✅ Correct: 18 | ❌ Wrong: 2 | ⏰ Timeout: 0 | ⚠️ Invalid: 0
🎯 Accuracy: 90.00%

Speed:
- Avg time per question: 5.23s
- Avg time per answered: 5.23s
- Speed: 11.47 questions/min

Per-table breakdown:
| table | total | correct | wrong | accuracy_pct |
|-------|-------|---------|-------|--------------|
| 2     | 3     | 3       | 0     | 100.00       |
| 7     | 5     | 4       | 1     | 80.00        |
| ...
```

---

## Part 2: Data Persistence

### 2.1 JSON Helper Functions (`pages/Multiplication.py` lines 45-69)

**Pattern**: Safe JSON I/O with error recovery

```python
def _safe_load_json(path: Path, default):
    """Load JSON file safely, return default on error"""
    if not path.exists():
        return default  # File doesn't exist → return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default  # Corrupted → return default

def _safe_save_json(path: Path, data):
    """Save JSON file with UTF-8 encoding"""
    path.write_text(
        json.dumps(data, indent=2),  # 2-space indent
        encoding="utf-8"
    )
```

**Why Safe Pattern?**:
- Handles missing files gracefully (empty default)
- Catches JSON parse errors (user continues)
- Handles encoding issues (explicit UTF-8)
- No try-catch bloat in calling code

**Usage**:
```python
# Load
scores = _safe_load_json(SCORES_FILE, {})      # Default: empty dict
sessions = _safe_load_json(SESSIONS_FILE, [])  # Default: empty list

# Save
_safe_save_json(SCORES_FILE, scores)
_safe_save_json(SESSIONS_FILE, sessions)
```

---

### 2.2 Best Score Tracking (`pages/Multiplication.py` lines 71-101)

**Function**: `update_best_score(mode_key: str, todays_score: int, total_q: int)`

**Implementation**:
```python
def update_best_score(mode_key, todays_score, total_q):
    # Load current scores
    scores = load_best_scores()
    today = str(date.today())  # "2024-03-01"
    
    # Ensure mode exists in dict
    if mode_key not in scores:
        scores[mode_key] = {}
    
    # Get previous best for today (if exists)
    prev = scores[mode_key].get(today)
    
    # Determine if new score is better
    is_new_best = (
        prev is None or 
        int(prev.get("score", -1)) < int(todays_score)
    )
    
    # Update if better
    if is_new_best:
        scores[mode_key][today] = {
            "score": int(todays_score),
            "out_of": int(total_q),
            "updated_at_epoch": int(time.time()),
        }
        save_best_scores(scores)
    
    # Return (is_new_best, current_best_entry)
    return is_new_best, scores[mode_key].get(today, prev or {})
```

**Data Structure**:
```python
best_scores = {
    "a1b2c3d4e5f6g7h8": {  # mode_key (16-char SHA256)
        "2024-03-01": {
            "score": 20,
            "out_of": 20,
            "updated_at_epoch": 1709289600
        },
        "2024-02-29": {
            "score": 18,
            "out_of": 20,
            "updated_at_epoch": 1709203200
        }
    }
}
```

**Key Features**:
- One best score per mode per day
- Multiple days tracked per mode
- Uses epoch timestamp for verification
- Returns both flag and score data

---

### 2.3 Mode Key Generation (`pages/Multiplication.py` lines 59-67)

**Function**: `make_mode_key(tables, level_name, total_q, seconds_per_q)`

**Implementation**:
```python
def make_mode_key(tables, level_name, total_q, seconds_per_q):
    # Create canonical JSON representation
    payload = {
        "operation": "multiplication",
        "tables": sorted(tables),           # Normalize order
        "level": level_name,
        "total_q": total_q,
        "seconds_per_q": seconds_per_q,
    }
    
    # Serialize to JSON deterministically
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    
    # Create SHA256 hash
    hash_full = hashlib.sha256(raw).hexdigest()  # 64 chars
    
    # Return first 16 chars (collisions negligible)
    return hash_full[:16]
```

**Why This Approach?**:
- Deterministic: same config → same key
- Compact: 16 chars vs 64
- Collision-resistant: ~4.3 billion keys before collision
- Human-readable enough: `a1b2c3d4e5f6g7h8`

**Example**:
```
tables=[2,3,4], level="Medium (1-12)", total_q=20, seconds_per_q=10
→ SHA256(...)[:16]
→ "7f8e9a0b1c2d3e4f"
```

---

### 2.4 Session Recording (`pages/Multiplication.py` lines 281-308)

**Trigger**: When `quiz_finished` state changes and `finalized_session` is False

**Implementation**:
```python
if not st.session_state.get("finalized_session", False):
    st.session_state.finalized_session = True  # Mark as finalized
    
    # Update best score
    update_best_score(
        st.session_state.mode_key,
        score,
        total
    )
    
    # Create session record
    session_record = {
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
    
    # Append to sessions
    append_session(session_record)
```

**Why `finalized_session` Flag?**:
- Streamlit reruns page multiple times
- Flag prevents duplicate saves
- Checked at very beginning of results phase
- Only runs once per quiz completion

---

## Part 3: Dashboard Analytics

### 3.1 Data Loading (`pages/Dashboard.py` lines 11-19)

**Function**: `load_sessions()`

```python
def load_sessions():
    if not SESSIONS_FILE.exists():
        return []
    try:
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []
```

**Characteristics**:
- Returns list of dicts
- Empty list if file missing
- Empty list if corrupted
- Never raises exception

---

### 3.2 Data Transformation Pipeline (`pages/Dashboard.py` lines 26-50)

---

## Part 4: Addition Quiz Implementation Plan (REQ-005)

### 4.1 Target File Structure (`pages/Addition.py`)

**Implementation Goal**: Reuse the multiplication page architecture where it reduces risk, but simplify where Addition does not need per-mode daily best tracking.

**Planned File Layout**:
```python
import json
import random
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

SESSIONS_FILE = Path("sessions.json")

ADDITION_LEVELS = {
    "Beginner (1-10)": (1, 10),
    "Intermediate (1-50)": (1, 50),
    "Advanced (1-100)": (1, 100),
}

# JSON helpers
# analytics helpers
# quiz state helpers
# question generation
# answer submission / timeout logic
# settings sidebar
# active quiz view
# results summary and session persistence
```

**Why This Shape?**:
- Keeps the page easy to compare with `pages/Multiplication.py`
- Minimizes cognitive load during implementation and review
- Preserves room to extract shared helpers later without forcing a refactor now

---

### 4.2 Session State Reuse Strategy

**Implementation Pattern**: Mirror the Multiplication session keys wherever the behavior is the same.

**Recommended State Keys**:
```python
quiz_started: bool
quiz_finished: bool
finalized_session: bool
order: list[tuple[int, int]]
idx: int
current_q: tuple[int, int]
score: int
attempts: int
history: list[dict]
last_feedback: str
start_ts: float
deadline_ts: float
seconds_per_q: int
mode_meta: dict
session_id: str
active_settings_fp: str
last_settings_fp: str
```

**Notes**:
- Omit `mode_key`, `celebrated`, and best-score-specific state unless requirements expand later.
- Keep `finalized_session` to prevent duplicate `sessions.json` writes during Streamlit reruns.
- Use the same reset behavior after a finished quiz when settings change.

---

### 4.3 Question Generation Plan (`T-101`)

**Function**: `generate_addition_questions(min_num: int, max_num: int, total_q: int) -> list[tuple[int, int]]`

**Reference Algorithm**:
```python
def generate_addition_questions(min_num, max_num, total_q):
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
```

**Implementation Notes**:
- Ordered pairs are acceptable for v1 of Addition; `(2, 5)` and `(5, 2)` may both appear because they produce different visual prompts even though the sum matches.
- This mirrors the multiplication generator and keeps behavior predictable.
- For `Advanced (1-100)`, the unique pair pool is large enough for all expected quiz sizes.

**Complexity**:
- Time: O(n^2) to build the pair pool for a selected range
- Space: O(n^2) for the unique pair list
- Acceptable for current range sizes and local-only app usage

---

### 4.4 Quiz Initialization (`T-100`)

**Function**: `start_quiz(level_name, min_num, max_num, total_q, seconds_per_q)`

**Implementation Sketch**:
```python
def start_quiz(level_name, min_num, max_num, total_q, seconds_per_q):
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
    st.session_state.session_id = f"add-{int(now)}-{random.randint(1000, 9999)}"
```

**Key Decision**:
- Persist `operand_min` and `operand_max` directly in `mode_meta` so the saved session row is self-describing for future Dashboard enhancements.

---

### 4.5 Answer Validation and Timeout Flow (`T-102`)

**Core Functions**:
- `advance_question_or_finish()`
- `record_result(result, your_answer, correct, elapsed_s)`
- `record_timeout()`
- `submit_answer(answer_text)`

**Implementation Sketch**:
```python
def submit_answer(answer_text):
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    st.session_state.attempts += 1
    elapsed = time.time() - float(st.session_state.start_ts)

    try:
        answer = int(answer_text.strip())
    except Exception:
        record_result("INVALID", answer_text, correct, elapsed)
        st.session_state.last_feedback = "⚠ Please enter a whole number"
        advance_question_or_finish()
        return

    if answer == correct:
        st.session_state.score += 1
        record_result("CORRECT", answer, correct, elapsed)
        st.session_state.last_feedback = f"✅ Correct! {num1} + {num2} = {correct}"
    else:
        record_result("WRONG", answer, correct, elapsed)
        st.session_state.last_feedback = f"❌ Oops! {num1} + {num2} = {correct}"

    advance_question_or_finish()
```

**Timeout Rule**:
```python
def record_timeout():
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    elapsed = time.time() - float(st.session_state.start_ts)
    record_result("TIMEOUT", None, correct, elapsed)
    st.session_state.last_feedback = f"⏰ Time's up! {num1} + {num2} = {correct}"
    advance_question_or_finish()
```

**Important Guardrail**:
- Results for a question must be recorded exactly once. The timer rerun path and the submit path must not both finalize the same prompt.

---

### 4.6 Results and Session Recording (`T-103`)

**Implementation Goal**: Save Addition sessions using the Dashboard-compatible schema already consumed by `pages/Dashboard.py`.

**Session Save Sketch**:
```python
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
```

**Compatibility Notes**:
- Keep shared metric keys identical to Multiplication so Dashboard charts need minimal or no changes.
- Addition-specific keys should be additive, not replacements for existing fields.
- `operation = "addition"` is the main integration point for Dashboard filtering.

---

### 4.7 Dashboard Impact (`T-103`)

**Expected Changes**:
- `pages/Dashboard.py` should already ingest new Addition session rows because it reads generic JSON records and filters by `operation` and `level` when present.
- No mandatory Dashboard code changes are required if Addition rows preserve the existing metric field names.
- If the Addition page introduces fields absent from Multiplication, they should remain optional so the current `show_cols` filtering continues to work.

**Manual Verification Targets**:
- Addition sessions appear in the session table
- Addition appears in operation filter options
- Trend charts continue to render with mixed operation data
- Existing multiplication history remains readable

---

### 4.8 Recommended Build Order

1. Create `pages/Addition.py` scaffold with constants and shared JSON helpers.
2. Implement state reset and quiz initialization.
3. Implement question generation and active quiz loop.
4. Implement answer validation and timeout handling.
5. Implement results metrics and session persistence.
6. Verify Dashboard compatibility with mixed session data.

**Why This Order?**:
- It follows the dependency chain from `T-100` through `T-104`.
- It keeps state and question flow stable before analytics integration.
- It reduces the chance of debugging UI, timer, and persistence problems at the same time.

---

### 4.9 Risks and Watchpoints

- `Advanced (1-100)` creates 10,000 ordered pairs, which is acceptable locally but should still avoid unnecessary recomputation during reruns.
- Streamlit reruns can double-save results if `finalized_session` checks are misplaced.
- Invalid input handling must match the user-facing wording approved in `Requirements.md`.
- Addition session rows must not break Dashboard assumptions about optional columns.

**Step 1: Load and DataFrame conversion**
```python
sessions = load_sessions()
df = pd.DataFrame(sessions)
# Convert list of dicts → pandas DataFrame
```

**Step 2: Timestamp parsing and sorting**
```python
if "timestamp_iso" in df.columns:
    df["timestamp_iso"] = pd.to_datetime(
        df["timestamp_iso"],
        errors="coerce"  # Invalid → NaT
    )
    df = df.sort_values("timestamp_iso", ascending=False)
```

**Step 3: Summary metrics**
```python
total_sessions = len(df)
avg_score = df["score"].mean() if "score" in df.columns else 0
avg_accuracy = df["accuracy_pct"].mean() if "accuracy_pct" in df.columns else 0
avg_speed = df["speed_q_per_min"].mean() if "speed_q_per_min" in df.columns else 0
```

**Step 4: Filter application**
```python
df_filtered = df.copy()
if selected_ops:
    df_filtered = df_filtered[df_filtered["operation"].isin(selected_ops)]
if selected_levels:
    df_filtered = df_filtered[df_filtered["level"].isin(selected_levels)]
```

**Step 5: Display**
```python
st.dataframe(
    df_filtered[show_cols],
    use_container_width=True,
    hide_index=True
)
```

---

### 3.3 Analytics Functions (`pages/Multiplication.py` lines 220-257)

**Function**: `compute_speed(history: list[dict])`

```python
def compute_speed(history):
    if not history:
        return {
            "avg_time_all": 0.0,
            "avg_time_answered": 0.0,
            "qpm": 0.0
        }
    
    # All times (including timeouts)
    all_times = [
        h["elapsed_s"]
        for h in history
        if isinstance(h.get("elapsed_s"), (int, float))
    ]
    
    # Only answered (correct or wrong)
    answered_times = [
        h["elapsed_s"]
        for h in history
        if h.get("result") in ("CORRECT", "WRONG")
        and isinstance(h.get("elapsed_s"), (int, float))
    ]
    
    # Calculate averages
    avg_all = sum(all_times) / len(all_times) if all_times else 0.0
    avg_ans = sum(answered_times) / len(answered_times) if answered_times else 0.0
    
    # Questions per minute
    qpm = (60.0 / avg_ans) if avg_ans > 0 else 0.0
    
    return {
        "avg_time_all": avg_all,
        "avg_time_answered": avg_ans,
        "qpm": qpm
    }
```

**Example Calculation**:
```
History of 5 questions (4 answered, 1 timeout):
1. CORRECT, 2.5s
2. WRONG, 3.0s
3. CORRECT, 2.0s
4. TIMEOUT, 10.0s
5. CORRECT, 2.5s

avg_time_all = (2.5+3.0+2.0+10.0+2.5) / 5 = 4.0s
avg_time_answered = (2.5+3.0+2.0+2.5) / 4 = 2.5s
qpm = 60.0 / 2.5 = 24.0 questions/min
```

**Function**: `per_table_breakdown(history: list[dict])`

```python
def per_table_breakdown(history):
    buckets = {}
    
    # Group by table
    for h in history:
        t = h.get("table")
        if t is None:
            continue
        
        # Initialize bucket if needed
        if t not in buckets:
            buckets[t] = {
                "table": t,
                "total": 0,
                "correct": 0,
                "wrong": 0,
                "timeout": 0,
                "invalid": 0
            }
        
        # Count result
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
    
    # Calculate accuracy
    rows = []
    for t in sorted(buckets.keys()):
        b = buckets[t]
        answered = b["correct"] + b["wrong"]
        acc = (b["correct"] / answered * 100.0) if answered > 0 else 0.0
        b["accuracy_pct"] = round(acc, 2)
        rows.append(b)
    
    return pd.DataFrame(rows)
```

**Output Example**:
```
| table | total | correct | wrong | timeout | invalid | accuracy_pct |
|-------|-------|---------|-------|---------|---------|--------------|
| 2     | 3     | 3       | 0     | 0       | 0       | 100.0        |
| 5     | 4     | 3       | 1     | 0       | 0       | 75.0         |
| 7     | 3     | 2       | 0     | 1       | 0       | 100.0        |
```

---

## Part 4: State Management & Navigation

### 4.1 State Reset Function (`pages/Multiplication.py` lines 103-120)

**Purpose**: Clear all quiz-related session state

```python
def reset_quiz_state():
    keys_to_clear = [
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
    ]
    
    for k in keys_to_clear:
        st.session_state.pop(k, None)  # Remove if exists
```

**When Called**:
- User clicks "Stop" button
- User clicks "Start" (before starting new quiz)
- Settings change after quiz finished
- Page changes from/to quiz

---

### 4.2 Settings Fingerprint Detection (`pages/Multiplication.py` lines 231-243)

**Purpose**: Detect when user changes settings after finishing quiz

**Implementation**:
```python
# Create fingerprint of current settings
fp_now = settings_fingerprint(
    tables, level_name, total_q, seconds_per_q
)

# Get previous fingerprint
last_fp = st.session_state.get("last_settings_fp")

# If changed and quiz finished, reset
if (
    last_fp and 
    last_fp != fp_now and 
    st.session_state.get("quiz_finished", False)
):
    reset_quiz_state()

# Store current for next check
st.session_state["last_settings_fp"] = fp_now
```

**Fingerprint Function**:
```python
def settings_fingerprint(tables, level_name, total_q, seconds_per_q):
    return json.dumps({
        "tables": sorted([int(x) for x in tables]),
        "level": str(level_name),
        "total_q": int(total_q),
        "seconds_per_q": int(seconds_per_q),
    }, sort_keys=True)
```

**Example**:
```
Before: {"level":"Medium","tables":[2,3],"seconds_per_q":10,"total_q":20}
User changes total_q to 30
After: {"level":"Medium","tables":[2,3],"seconds_per_q":10,"total_q":30}
Result: Different → Reset state
```

---

### 4.3 Advance Question Logic (`pages/Multiplication.py` lines 160-169)

```python
def advance_question_or_finish():
    st.session_state.idx += 1
    
    # Check if quiz is complete
    if st.session_state.idx >= len(st.session_state.order):
        st.session_state.quiz_finished = True
        return
    
    # Else: move to next question
    st.session_state.current_q = st.session_state.order[st.session_state.idx]
    
    # Reset timer for new question
    now = time.time()
    st.session_state.start_ts = now
    st.session_state.deadline_ts = now + int(st.session_state.seconds_per_q)
```

**State Transitions**:
```
Before: idx=3, 5 total questions
Call: advance_question_or_finish()
  idx < len(order)? (3 < 5) → YES
  idx becomes 4
  current_q = order[4]
  Timer reset

Before: idx=4, 5 total questions
Call: advance_question_or_finish()
  idx < len(order)? (5 < 5) → NO
  quiz_finished = True
  Timer not reset (quiz ended)
```

---

## Part 5: UI/UX Implementation

### 5.1 Page Configuration (`pages/Multiplication.py` line 231)

```python
st.set_page_config(
    page_title="Multiplication Quiz",
    page_icon="✖️",
    layout="centered"
)
st.title("✖️ Multiplication Quiz")
```

**Settings**:
- `page_title`: Browser tab title
- `page_icon`: Browser tab icon (emoji)
- `layout="centered"`: Constrains width, centers content

---

### 5.2 Sidebar Settings (`pages/Multiplication.py` lines 235-272)

```python
with st.sidebar:
    st.header("Settings")
    
    # Table selection
    tables = st.multiselect(
        "Select tables",
        options=list(range(2, 21)),  # 2-20
        default=[2, 3, 4, 5]
    )
    
    # Level selection
    level_name = st.selectbox(
        "Level",
        list(LEVELS.keys()),
        index=1  # Default to Medium
    )
    max_multiplier = LEVELS[level_name]
    
    # Questions count
    total_q = st.number_input(
        "Total questions",
        min_value=1,
        max_value=500,
        value=20,
        step=1
    )
    
    # Timer
    seconds_per_q = st.slider(
        "Timer per question (seconds)",
        2, 60, 10, 1  # min, max, default, step
    )
    
    # Info text
    st.caption(f"Multiplier range: **1..{max_multiplier}**")
```

**Component Types Used**:
- `multiselect`: Multi-choice (tables)
- `selectbox`: Single choice (level)
- `number_input`: Number entry (total_q)
- `slider`: Range selection (timer)
- `caption`: Small text (helper)

---

### 5.3 Live Quiz Display (`pages/Multiplication.py` lines 325-372)

**Header Section**:
```python
st.markdown(
    f"""
<div style="display:flex;justify-content:space-between;align-items:center;">
  <div style="font-size:40px;font-weight:900;">Score: {score} / {total}</div>
  <div style="font-size:52px;font-weight:900; padding: 12px 22px; 
              border-radius: 16px; border: 4px solid #999; 
              min-width: 160px; text-align:center;">
    ⏳ {remaining}s
  </div>
</div>
""",
    unsafe_allow_html=True
)
```

**Info Row**:
```python
st.write(
    f"Mode: **{meta['level']}** | Tables: **{meta['tables']}** | "
    f"Question: **{idx}/{total}** | Timer: **{meta['seconds_per_q']}s**"
)
```

**Progress Bar**:
```python
st.progress((idx - 1) / total)  # 0.0 to 1.0
```

**Question Display**:
```python
t, m = st.session_state.current_q
st.subheader(f"What is {t} × {m} ?")

if st.session_state.get("last_feedback"):
    st.write(st.session_state.last_feedback)  # Previous feedback
```

**Answer Form**:
```python
with st.form("answer_form", clear_on_submit=True):
    ans_text = st.text_input(
        "Your answer",
        placeholder="Type a number and press Submit"
    )
    submitted = st.form_submit_button("Submit")

if submitted:
    submit_answer(ans_text)
    st.rerun()

# Auto-rerun for timer
time.sleep(0.25)
st.rerun()
```

---

### 5.4 Results Screen (`pages/Multiplication.py` lines 251-290)

**Header**:
```python
st.header("✅ Quiz finished!")
st.markdown(
    f"<div style='font-size:44px;font-weight:900;'>Final Score: {score} / {total}</div>",
    unsafe_allow_html=True
)
st.balloons()  # Celebration animation (once via flag)
```

**Best Score Display**:
```python
is_new_best, today_entry = update_best_score(
    st.session_state.mode_key,
    score,
    total
)

if is_new_best:
    st.success(f"🏆 New best today: **{today_entry['score']} / {today_entry['out_of']}**")
else:
    if today_entry:
        st.info(f"🏆 Today best: **{today_entry.get('score')} / {today_entry.get('out_of')}**")
```

**Metrics Section**:
```python
st.subheader("Speed")
st.write(f"- Avg time per question: **{speed['avg_time_all']:.2f}s**")
st.write(f"- Avg time (answered only): **{speed['avg_time_answered']:.2f}s**")
st.write(f"- Speed: **{speed['qpm']:.2f} questions/min**")
```

**Breakdown Table**:
```python
st.subheader("Per-table breakdown")
if table_df.empty:
    st.info("No table breakdown available.")
else:
    st.dataframe(
        table_df[["table", "total", "correct", "wrong", "timeout", "invalid", "accuracy_pct"]],
        use_container_width=True,
        hide_index=True
    )
```

**Navigation Buttons**:
```python
colA, colB = st.columns(2)
with colA:
    if st.button("Play again"):
        reset_quiz_state()
        st.rerun()
with colB:
    st.page_link("pages/Dashboard.py", label="Go to Dashboard", icon="📊")

st.stop()  # Stop further execution
```

---

## Part 6: Streamlit-Specific Patterns

### 6.1 Form Clear on Submit

**Pattern**:
```python
with st.form("answer_form", clear_on_submit=True):
    ans_text = st.text_input(...)
    submitted = st.form_submit_button("Submit")

if submitted:
    submit_answer(ans_text)
    st.rerun()
```

**Behavior**:
- `clear_on_submit=True`: Input field empties after submit
- `st.form()`: Groups inputs, single submit button
- `st.form_submit_button()`: Only triggers on form submit
- `st.rerun()`: Refreshes page (updates timer, question)

### 6.2 Conditional Stop

**Pattern**:
```python
if not st.session_state.get("quiz_started", False):
    st.info("Choose settings and press **Start**.")
    st.stop()
```

**Effect**:
- `st.stop()`: Stops rendering below this point
- Page shows info message, no further code runs
- Clean exit from page logic

---

### 6.3 Sidebar Permanent Section

**Pattern**:
```python
with st.sidebar:
    st.header("Settings")
    # ... settings controls ...
    
    # After form logic (outside context)
    # Logic still executes, controls persist
```

**Behavior**:
- Sidebar is always visible
- Settings update in real-time
- Main area can change based on sidebar values

---

---

## TEMPLATE: Documenting Implementation
**Step 6 in the Feature Development Flow (Implementation Phase)**

After breaking the feature into tasks, document the technical implementation details here for future maintenance and agent-led development.

### Step 1: Add Implementation Summary
Provide a high-level overview of how the feature was built and its place in the codebase.

### Step 2: Document Core Algorithms & Logic
- Explain complex logic (e.g., question generation, scoring algorithms).
- Use code blocks with comments to show the "how".
- Document time and space complexity if relevant.

### Step 3: Document State Management
List new `st.session_state` keys and explain their lifecycle (initialization, updates, reset).

### Step 4: Show UI/UX Patterns
- Document specific Streamlit components or custom CSS used.
- Explain form handling, reruns, and user feedback mechanisms.

### Step 5: Data Model Examples
Provide sample JSON structures for any new persistent data stored in `sessions.json` or `best_scores.json`.

### Step 6: IMPLEMENTATION CHANGE TEMPLATE (for requirement conflicts/changes)

When a task modifies or clarifies an existing requirement (see `spec/Tasks.md` NOTE section), authors MUST add a corresponding IMPLEMENTATION entry here with the following structure. This entry provides an auditable record of what was changed, why, and how to verify it.

```markdown
### IMPLEMENTATION: T-[number] - [Short summary]
**Status**: Draft | Implemented | Verified
**Related Task**: T-[number]
**Related Requirement(s)**: [Requirements.md section(s) or IDs]

**Original Requirement / Behavior (quote)**:
> "..."

**Modified Requirement / New Behavior**:
> "..."

**Rationale / Why changed**:
- Reason 1 (e.g., conflict with X, performance, security, UX)
- Reason 2 (link to discussion/issue/meeting notes)

**What changed (high-level)**:
- Bullet list of behavior changes

**Files / Symbols Modified**:
- `path/to/file.py` — function / class / line-range

**Code Diff or Summary of Changes**:
- (Prefer a small unified diff or a clear summary of code paths changed)

**Tests Added / Updated**:
- `tests/test_x.py` — unit/integration test description

**Verification Steps**:
1. Step-by-step verification for reviewer / QA
2. Expected outcomes and acceptance criteria mapping

**Backward Compatibility / Migration Notes**:
- Is this backward compatible? Yes/No
- If not, what migration steps or data transformation are required?

**References**:
- Link to issue, meeting notes, design doc, or Requirements.md

**Author**: Name / role
**Date**: YYYY-MM-DD
```

Add each IMPLEMENTATION entry here and include a cross-link back to the task (T-xxx) that triggered the change. Prefer a concise code diff or patch for reviewers.


---

## Checklist When Documenting Implementation
- [ ] Implementation summary provided
- [ ] Core algorithms and logic explained with code snippets
- [ ] State management (session_state) fully documented
- [ ] UI/UX patterns and components described
- [ ] Data model examples included (JSON samples)
- [ ] Ready to move to Testing.md

### Next Step
After completing Implementations.md, proceed to **Testing.md** to define test strategy.

**FEATURE DEVELOPMENT FLOW CHECKLIST:**
1. ✅ features.md - Define what feature does
2. ✅ requirements.md - Define acceptance criteria
3. ✅ design.md - Architect the solution
4. ✅ ARCHITECTURE.md - Update system diagrams
5. ✅ tasks.md - Break into development tasks
6. ✅ Implementations.md - Prepare implementation details (YOU ARE HERE)
7. → Coding.md - Implement approved source changes and record them
8. → Testing.md - Define test strategy
9. → README.md - Update documentation
10. → RELEASE - Tag and publish

---

## Part 4: Addition Quiz Implementation Plan (REQ-005)

### 4.1 Target File Structure (`pages/Addition.py`)
---
**Implementation Goal**: Reuse the multiplication page architecture where it reduces risk, but simplify where Addition does not need per-mode daily best tracking.
**Planned File Layout**:
```python
import json
import random
import time
from datetime import datetime
from pathlib import Path
import streamlit as st
SESSIONS_FILE = Path("sessions.json")
ADDITION_LEVELS = {
    "Beginner (1-10)": (1, 10),
    "Intermediate (1-50)": (1, 50),
    "Advanced (1-100)": (1, 100),
}
```
**Why This Shape?**:
- Keeps the page easy to compare with `pages/Multiplication.py`
- Minimizes cognitive load during implementation and review
- Preserves room to extract shared helpers later without forcing a refactor now

---

### 4.2 Session State Reuse Strategy

**Implementation Pattern**: Mirror the Multiplication session keys wherever the behavior is the same.
**Recommended State Keys**:
```python
quiz_started: bool
quiz_finished: bool
finalized_session: bool
order: list[tuple[int, int]]
idx: int
current_q: tuple[int, int]
score: int
attempts: int
history: list[dict]
last_feedback: str
start_ts: float
deadline_ts: float
seconds_per_q: int
mode_meta: dict
session_id: str
active_settings_fp: str
last_settings_fp: str
```
**Notes**:
- Omit `mode_key`, `celebrated`, and best-score-specific state unless requirements expand later.
- Keep `finalized_session` to prevent duplicate `sessions.json` writes during Streamlit reruns.
- Use the same reset behavior after a finished quiz when settings change.

---

### 4.3 Question Generation Plan (`T-101`)

**Function**: `generate_addition_questions(min_num: int, max_num: int, total_q: int) -> list[tuple[int, int]]`
**Reference Algorithm**:
```python
def generate_addition_questions(min_num, max_num, total_q):
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
```
**Implementation Notes**:
- Ordered pairs are acceptable for v1 of Addition; `(2, 5)` and `(5, 2)` may both appear because they produce different visual prompts even though the sum matches.
- This mirrors the multiplication generator and keeps behavior predictable.
- For `Advanced (1-100)`, the unique pair pool is large enough for all expected quiz sizes.
**Complexity**:
- Time: O(n²) to build the pair pool for a selected range
- Space: O(n²) for the unique pair list
- Acceptable for current range sizes and local-only app usage

---

### 4.4 Quiz Initialization (`T-100`)

**Function**: `start_quiz(level_name, min_num, max_num, total_q, seconds_per_q)`
**Implementation Sketch**:
```python
def start_quiz(level_name, min_num, max_num, total_q, seconds_per_q):
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
    st.session_state.session_id = f"add-{int(now)}-{random.randint(1000, 9999)}"
```
**Key Decision**:
- Persist `operand_min` and `operand_max` directly in `mode_meta` so the saved session row is self-describing for future Dashboard enhancements.

---

### 4.5 Answer Validation and Timeout Flow (`T-102`)

**Core Functions**:
- `advance_question_or_finish()`
- `record_result(result, your_answer, correct, elapsed_s)`
- `record_timeout()`
- `submit_answer(answer_text)`
**Implementation Sketch**:
```python
def submit_answer(answer_text):
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    st.session_state.attempts += 1
    elapsed = time.time() - float(st.session_state.start_ts)
    try:
        answer = int(answer_text.strip())
    except Exception:
        record_result("INVALID", answer_text, correct, elapsed)
        st.session_state.last_feedback = "⚠ Please enter a whole number"
        advance_question_or_finish()
        return
    if answer == correct:
        st.session_state.score += 1
        record_result("CORRECT", answer, correct, elapsed)
        st.session_state.last_feedback = f"✅ Correct! {num1} + {num2} = {correct}"
    else:
        record_result("WRONG", answer, correct, elapsed)
        st.session_state.last_feedback = f"❌ Oops! {num1} + {num2} = {correct}"
    advance_question_or_finish()
```
**Timeout Rule**:
```python
def record_timeout():
    num1, num2 = st.session_state.current_q
    correct = num1 + num2
    elapsed = time.time() - float(st.session_state.start_ts)
    record_result("TIMEOUT", None, correct, elapsed)
    st.session_state.last_feedback = f"⏰ Time's up! {num1} + {num2} = {correct}"
    advance_question_or_finish()
```
**Important Guardrail**:
- Results for a question must be recorded exactly once. The timer rerun path and the submit path must not both finalize the same prompt.

---

### 4.6 Results and Session Recording (`T-103`)

**Implementation Goal**: Save Addition sessions using the Dashboard-compatible schema already consumed by `pages/Dashboard.py`.
**Session Save Sketch**:
```python
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
```
**Compatibility Notes**:
- Keep shared metric keys identical to Multiplication so Dashboard charts need minimal or no changes.
- Addition-specific keys should be additive, not replacements for existing fields.
- `operation = "addition"` is the main integration point for Dashboard filtering.

---

### 4.7 Dashboard Impact (`T-103`)

**Expected Changes**:
- `pages/Dashboard.py` should already ingest new Addition session rows because it reads generic JSON records and filters by `operation` and `level` when present.
- No mandatory Dashboard code changes are required if Addition rows preserve the existing metric field names.
- If the Addition page introduces fields absent from Multiplication, they should remain optional so the current `show_cols` filtering continues to work.
**Manual Verification Targets**:
- Addition sessions appear in the session table
- Addition appears in operation filter options
- Trend charts continue to render with mixed operation data
- Existing multiplication history remains readable

---

### 4.8 Recommended Build Order

1. Create `pages/Addition.py` scaffold with constants and shared JSON helpers.
2. Implement state reset and quiz initialization.
3. Implement question generation and active quiz loop.
4. Implement answer validation and timeout handling.
5. Implement results metrics and session persistence.
6. Verify Dashboard compatibility with mixed session data.
**Why This Order?**:
- It follows the dependency chain from `T-100` through `T-104`.
- It keeps state and question flow stable before analytics integration.
- It reduces the chance of debugging UI, timer, and persistence problems at the same time.

---

### 4.9 Risks and Watchpoints

- `Advanced (1-100)` creates 10,000 ordered pairs, which is acceptable locally but should still avoid unnecessary recomputation during reruns.
- Streamlit reruns can double-save results if `finalized_session` checks are misplaced.
- Invalid input handling must match the user-facing wording approved in `Requirements.md`.
- Addition session rows must not break Dashboard assumptions about optional columns.
