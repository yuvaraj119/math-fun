# Math Game Quiz - Testing Specification

## 1. Testing Strategy
Our testing strategy focus on manual verification and data integrity checks, aligned with our local-only, no-server architecture.

---

## Test Master Table

| Test ID | Test Scenario | Target Feature | Priority | Status | Result |
|---------|---------------|----------------|----------|--------|--------|
| **T-MQ-01** | No tables selected validation | Multiplication Quiz | P0 | ✅ Pass | Start button disabled |
| **T-MQ-02** | Multiplication table selection | Multiplication Quiz | P0 | ✅ Pass | Questions filtered |
| **T-MQ-03** | Difficulty range validation | Multiplication Quiz | P0 | ✅ Pass | Multipliers correct |
| **T-MQ-04** | Question timer accuracy | Multiplication Quiz | P0 | ✅ Pass | Countdown works |
| **T-AV-01** | Correct answer submission | Answer Validation | P0 | ✅ Pass | Score increments |
| **T-AV-02** | Wrong answer submission | Answer Validation | P0 | ✅ Pass | Correct answer shown |
| **T-AV-03** | Non-numeric input handling | Answer Validation | P1 | ✅ Pass | Warning message shown |
| **T-AV-05** | Question timeout handling | Answer Validation | P1 | ✅ Pass | Auto-advance works |
| **T-DI-01** | Session record persistence | Data Integrity | P0 | ✅ Pass | Saved to sessions.json |
| **T-DI-02** | Best score update logic | Data Integrity | P0 | ✅ Pass | Saved to best_scores.json |
| **T-DA-01** | Dashboard history display | Dashboard | P1 | ✅ Pass | History loaded |
| **T-DA-02** | Dashboard filtering | Dashboard | P1 | ✅ Pass | Filters applied |
| **T-AQ-01** | Addition quiz setup | Addition Quiz | P1 | 🔄 Pending | To be implemented |

**Legend**: ✅ = Pass | ❌ = Fail | 🔄 = Pending | 🚧 = In Progress

---

## 2. Manual Test Cases

### 2.1 Quiz Configuration (Multiplication)
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-MQ-01 | No tables selected | "Start Quiz" button is disabled | ✅ Pass |
| T-MQ-02 | Select tables 2, 5, 10 | Questions only generated from these tables | ✅ Pass |
| T-MQ-03 | Change difficulty to "Hard" | Multipliers range from 1 to 20 | ✅ Pass |
| T-MQ-04 | Set timer to 5 seconds | Timer starts at 5 and counts down to 0 | ✅ Pass |

### 2.2 Answer Validation
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-AV-01 | Enter correct answer | Score increments, ✅ shown, auto-advances | ✅ Pass |
| T-AV-02 | Enter wrong answer | Score stays, ❌ shown with correct answer, auto-advances | ✅ Pass |
| T-AV-03 | Enter text "abc" | Warning "⚠️ Please enter a whole number" | ✅ Pass |
| T-AV-04 | Leave blank and submit | Warning "⚠️ Please enter a whole number" | ✅ Pass |
| T-AV-05 | Timer reaches 0 | ⏰ Timeout recorded, auto-advances | ✅ Pass |

### 2.3 Data Integrity
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-DI-01 | Complete quiz | Session appended to `sessions.json` | ✅ Pass |
| T-DI-02 | Achieve new best score | `best_scores.json` updated for current mode | ✅ Pass |
| T-DI-03 | Corrupt `sessions.json` | App handles error gracefully (safe load) | ✅ Pass |
| T-DI-04 | Delete `best_scores.json` | App recreates file with default data | ✅ Pass |

### 2.4 Dashboard & Analytics
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-DA-01 | Open Dashboard | Charts and tables display session history | ✅ Pass |
| T-DA-02 | Filter by Difficulty | Table only shows sessions of selected level | ✅ Pass |
| T-DA-03 | Empty History | Dashboard shows "No sessions found" message | ✅ Pass |

### 2.5 Addition Quiz (Planned)
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-AQ-01 | Select Beginner level | Numbers generated in 1-10 range | 🔄 Pending |
| T-AQ-02 | Enter correct sum | Score increments, ✅ feedback | 🔄 Pending |
| T-AQ-03 | Timer expires | ⏰ Timeout recorded, auto-advance | 🔄 Pending |

### 2.6 Subtraction Quiz (Planned)
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-SQ-01 | Generate questions | Minuend >= Subtrahend (No negative results) | 🔄 Pending |

### 2.7 Division Quiz (Planned)
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-DQ-01 | Whole Numbers Only mode | Dividend is exact multiple of divisor | 🔄 Pending |
| T-DQ-02 | Division by zero | Prevented in question generation | 🔄 Pending |

### 2.8 Gamification & UX (Planned)
| Test ID | Scenario | Expected Result | Status |
|---------|----------|-----------------|--------|
| T-GP-01 | 3 sessions >90% accuracy | System suggests increasing difficulty | 🔄 Pending |
| T-AF-01 | Correct answer sound | "Ding" sound plays (if enabled) | 🔄 Pending |
| T-MO-01 | Mobile screen width | UI elements stack and use larger targets | 🔄 Pending |

---

## 3. Automated Validation

## TEMPLATE: Defining Test Strategy
**Step 7 in the Feature Development Flow (Quality Assurance Phase)**

After implementing the feature, define how it will be verified against the Requirements and Design.

### Step 1: Update Test Master Table
Add new test cases with sequential IDs (T-XXX), target feature, and priority.

### Step 2: Define Manual Test Cases
- **Scenario**: What action is the tester performing?
- **Expected Result**: What should happen according to the Requirements?
- **Status**: 🔄 Pending | ✅ Pass | ❌ Fail.

### Step 3: Define Automated Validation
- **Unit Tests**: List specific functions to be tested (e.g., math logic, data transformation).
- **Integration Tests**: Define end-to-end flows (e.g., quiz start to results save).
- **Schema Validation**: Verify JSON data structures.

### Step 4: Regression Testing
Identify existing features that could be affected by this new feature and must be re-tested.

---

## Checklist When Defining Test Strategy
- [ ] Test Master Table updated
- [ ] Manual test cases cover all Acceptance Criteria from Requirements.md
- [ ] Edge cases and error handling scenarios included
- [ ] Automated validation (Unit/Integration) defined
- [ ] Regression tests identified
- [ ] Pass/Fail criteria are clear and measurable
- [ ] Ready to move to README.md

### Next Step
After completing Testing.md, proceed to **README.md** to update documentation.

**FEATURE DEVELOPMENT FLOW CHECKLIST:**
1. ✅ Features.md - Define what feature does
2. ✅ Requirements.md - Define acceptance criteria
3. ✅ Design.md - Architect the solution
4. ✅ Architecture.md - Update system diagrams
5. ✅ Tasks.md - Break into development tasks
6. ✅ Implementations.md - Add code examples
7. ✅ Testing.md - Define test strategy (YOU ARE HERE)
8. → README.md - Update documentation
9. → Release.md - Tag and publish
