# Math Game Quiz - Requirements Document

## Overview
This document specifies functional requirements for the Math Game Quiz application using user stories with acceptance criteria and EARS (Event, Action, Response) format for system behaviors.

---

## Requirement Master Table

| Requirement ID | Feature Reference | Status | Priority | Target Version | Documentation |
|----------------|-------------------|--------|----------|----------------|---------------|
| **REQ-001** | Multiplication Quiz (F-001) | ✅ Implemented | P0 | v1.0 | Core multiplication tables practice |
| **REQ-002** | Dashboard & Analytics (F-002) | ✅ Implemented | P0 | v1.0 | Session history, metrics, and trends |
| **REQ-003** | Session Persistence | ✅ Implemented | P0 | v1.0 | Local JSON storage for scores/sessions |
| **REQ-004** | State & Navigation | ✅ Implemented | P0 | v1.0 | Application flow and state management |
| **REQ-005** | Addition Quiz (F-003) | 🔄 Planned | P1 | v2.0 | Single/double digit addition practice |
| **REQ-006** | Subtraction Quiz (F-004) | 🔄 Planned | P1 | v2.0 | Age-appropriate subtraction practice |
| **REQ-007** | Division Quiz (F-005) | 🔄 Planned | P1 | v2.0 | Division with remainder options |
| **REQ-008** | Difficulty Progression (F-006)| 🔄 Planned | P2 | v3.0 | Automatic level adjustment |
| **REQ-009** | Audio Feedback (F-007) | 🔄 Planned | P2 | v3.0 | Educational sound effects |
| **REQ-010** | Mobile Optimization (F-008) | 🔄 Planned | P3 | v4.0 | Responsive layout for tablets/mobile |

**Legend**: ✅ = Implemented | 🔄 = Planned | 🚫 = Removed

---

## 1. Multiplication Quiz Game (REQ-001)

### 1.1 Quiz Configuration
#### User Story
AS A student  
WHEN I load the Multiplication quiz page  
I WANT to customize my quiz settings  
SO THAT I can practice at my preferred difficulty level

#### Acceptance Criteria
1. **WHEN** a user selects multiplication tables  
   **THE SYSTEM SHALL** allow selection of any combination from tables 2-20

2. **WHEN** a user selects a difficulty level (Easy/Medium/Hard)  
   **THE SYSTEM SHALL** update the multiplier range accordingly:
   - Easy (1-6): multipliers from 1 to 6
   - Medium (1-12): multipliers from 1 to 12
   - Hard (1-20): multipliers from 1 to 20

3. **WHEN** a user specifies total questions  
   **THE SYSTEM SHALL** accept values from 1 to 500

4. **WHEN** a user adjusts the timer per question  
   **THE SYSTEM SHALL** accept values from 2 to 60 seconds

5. **WHEN** no tables are selected  
   **THE SYSTEM SHALL** disable the Start button

6. **WHEN** a user clicks "Start"  
   **THE SYSTEM SHALL** initialize quiz with selected configuration

7. **WHEN** a user clicks "Stop"  
   **THE SYSTEM SHALL** reset all quiz state and return to settings view

### 1.2 Question Generation
#### User Story
AS A student  
WHEN I start a quiz  
I WANT the system to generate random questions  
SO THAT I get varied practice

#### Acceptance Criteria
1. **WHEN** quiz initializes  
   **THE SYSTEM SHALL** generate random question order from selected tables and multipliers

2. **WHEN** total questions exceed available unique pairs  
   **THE SYSTEM SHALL** allow duplicate pairs in random order

3. **WHEN** questions are generated  
   **THE SYSTEM SHALL** ensure unpredictable ordering to prevent pattern memorization

### 1.3 Live Quiz Display
#### User Story
AS A student  
WHEN I'm actively answering quiz questions  
I WANT to see my progress and time remaining  
SO THAT I can manage my pace and focus

#### Acceptance Criteria
1. **WHEN** quiz is running  
   **THE SYSTEM SHALL** display current score (X / Total) prominently

2. **WHEN** quiz is running  
   **THE SYSTEM SHALL** display countdown timer in large font

3. **WHEN** quiz is running  
   **THE SYSTEM SHALL** show question number (X / Total)

4. **WHEN** quiz is running  
   **THE SYSTEM SHALL** display current question (e.g., "What is 7 × 8?")

5. **WHEN** quiz is running  
   **THE SYSTEM SHALL** show a progress bar indicating completion percentage

6. **WHEN** timer reaches 0 seconds  
   **THE SYSTEM SHALL** automatically advance to next question

7. **WHEN** quiz reaches final question  
   **THE SYSTEM SHALL** advance to results screen upon completion

### 1.4 Answer Validation
#### User Story
AS A student  
WHEN I submit an answer  
I WANT immediate feedback on correctness  
SO THAT I learn from my mistakes

#### Acceptance Criteria
1. **WHEN** a student submits non-numeric input  
   **THE SYSTEM SHALL** display "⚠️ Please enter a whole number" error

2. **WHEN** a student submits an empty answer  
   **THE SYSTEM SHALL** treat as invalid input error

3. **WHEN** a student submits correct answer  
   **THE SYSTEM SHALL** increment score, display ✅ feedback with correct answer, and advance question

4. **WHEN** a student submits incorrect answer  
   **THE SYSTEM SHALL** display ❌ feedback showing correct answer and advance question

5. **WHEN** timer expires before answer  
   **THE SYSTEM SHALL** record as TIMEOUT, display ⏰ feedback, and advance question

6. **WHEN** answer is submitted  
   **THE SYSTEM SHALL** record elapsed time for that question

### 1.5 Results & Summary
#### User Story
AS A student  
WHEN I complete a quiz  
I WANT to see detailed performance summary  
SO THAT I understand my strengths and weaknesses

#### Acceptance Criteria
1. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** display final score prominently (X / Total)

2. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** show visual celebration (balloons) once per session only

3. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** calculate and display:
   - Overall accuracy percentage
   - Average time per question (including timeouts)
   - Average time per answered question (excluding timeouts)
   - Questions per minute (speed metric)

4. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** display result breakdown:
   - Total questions attempted
   - Correct answers count
   - Wrong answers count
   - Timeout count
   - Invalid input count

5. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** display per-table breakdown showing:
   - Table number
   - Total questions for that table
   - Correct, wrong, timeout, invalid counts
   - Accuracy percentage per table

6. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** provide buttons to "Play again" or "Go to Dashboard"

### 1.6 Best Score Tracking
#### User Story
AS A student  
WHEN I complete a quiz with a specific configuration  
I WANT my best score for that exact configuration saved  
SO THAT I can track daily progress for that mode

#### Acceptance Criteria
1. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** create unique mode key from (tables, level, total_q, seconds_per_q)

2. **WHEN** mode configuration matches existing best score  
   **THE SYSTEM SHALL** compare new score with best score

3. **WHEN** new score exceeds today's best  
   **THE SYSTEM SHALL** update best_scores.json with new best

4. **WHEN** new score doesn't exceed today's best  
   **THE SYSTEM SHALL** keep existing best and display it

5. **WHEN** user views sidebar before starting quiz  
   **THE SYSTEM SHALL** display today's best for current mode configuration (if exists)

6. **WHEN** changing settings that affect mode key  
   **THE SYSTEM SHALL** refresh best score display in sidebar

---

## 2. Session Persistence (REQ-003)

### 2.1 Session Recording
#### User Story
AS A student  
WHEN I complete a quiz  
I WANT the session automatically recorded  
SO THAT my progress is tracked over time

#### Acceptance Criteria
1. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** record exactly once (prevent duplicate saves on reruns)

2. **WHEN** recording session  
   **THE SYSTEM SHALL** capture:
   - Unique session ID
   - ISO timestamp
   - Operation type (multiplication)
   - Selected tables
   - Difficulty level
   - Multiplier max for that level
   - Seconds per question setting
   - Total questions configured
   - Final score achieved
   - Count: correct, wrong, timeout, invalid answers
   - Total answered questions
   - Accuracy percentage
   - Speed metrics (avg time, questions per minute)

3. **WHEN** session data is recorded  
   **THE SYSTEM SHALL** append to sessions.json without overwriting

4. **WHEN** sessions.json doesn't exist  
   **THE SYSTEM SHALL** create it with proper JSON formatting

### 2.2 Score File Management
#### User Story
AS THE SYSTEM  
WHEN storing scores and sessions  
I WANT proper error handling  
SO THAT no data is lost due to file errors

#### Acceptance Criteria
1. **WHEN** reading JSON file  
   **THE SYSTEM SHALL** return default value (empty dict/list) if file doesn't exist

2. **WHEN** reading JSON file  
   **THE SYSTEM SHALL** return default value if file is corrupted/unreadable

3. **WHEN** writing JSON file  
   **THE SYSTEM SHALL** use UTF-8 encoding

4. **WHEN** writing JSON file  
   **THE SYSTEM SHALL** format with 2-space indentation for readability

---

## 3. Dashboard & Analytics (REQ-002)

### 3.1 Session History Viewing
#### User Story
AS A student  
WHEN I visit the Dashboard  
I WANT to see all my previous quiz sessions  
SO THAT I can review my performance history

#### Acceptance Criteria
1. **WHEN** Dashboard loads and sessions exist  
   **THE SYSTEM SHALL** display all sessions in a table format

2. **WHEN** sessions exist  
   **THE SYSTEM SHALL** sort by timestamp (most recent first)

3. **WHEN** no sessions exist  
   **THE SYSTEM SHALL** display friendly message "No sessions yet. Play the Multiplication quiz..."

4. **WHEN** sessions are displayed  
   **THE SYSTEM SHALL** show columns:
   - Timestamp (ISO format)
   - Operation type
   - Level
   - Tables
   - Total questions
   - Score
   - Accuracy percentage
   - Average time (all questions)
   - Average time (answered only)
   - Speed (questions/minute)
   - Seconds per question setting

### 3.2 Summary Metrics
#### User Story
AS A student  
WHEN I view the Dashboard  
I WANT to see summary metrics of all my sessions  
SO THAT I can understand my overall progress

#### Acceptance Criteria
1. **WHEN** Dashboard loads  
   **THE SYSTEM SHALL** display 4 summary cards:
   - Total sessions count
   - Average score across all sessions
   - Average accuracy percentage across all sessions
   - Average speed (questions per minute) across all sessions

2. **WHEN** calculating metrics  
   **THE SYSTEM SHALL** handle missing data gracefully (default to 0)

### 3.3 Filtering
#### User Story
AS A student  
WHEN I review my session history  
I WANT to filter by operation and level  
SO THAT I can focus on specific practice modes

#### Acceptance Criteria
1. **WHEN** Dashboard loads  
   **THE SYSTEM SHALL** provide expandable Filters section

2. **WHEN** filters exist  
   **THE SYSTEM SHALL** show:
   - Multi-select dropdown for operations (dynamically populated from data)
   - Multi-select dropdown for levels (dynamically populated from data)

3. **WHEN** filters are applied  
   **THE SYSTEM SHALL** update displayed sessions to match selected filters

4. **WHEN** no filter is selected for a category  
   **THE SYSTEM SHALL** show all sessions (no filtering for that category)

5. **WHEN** filters change  
   **THE SYSTEM SHALL** update trend visualizations to match filtered data

### 3.4 Trend Visualization
#### User Story
AS A student  
WHEN I view the Dashboard  
I WANT to see visual trends in my performance  
SO THAT I can identify improvement or decline

#### Acceptance Criteria
1. **WHEN** Dashboard loads  
   **THE SYSTEM SHALL** display "Trends" section with 2 line charts

2. **WHEN** sufficient data exists (>1 session)  
   **THE SYSTEM SHALL** display score trend over time

3. **WHEN** insufficient data  
   **THE SYSTEM SHALL** show message "Not enough data for score trend yet"

4. **WHEN** sufficient data exists  
   **THE SYSTEM SHALL** display speed (questions/minute) trend over time

5. **WHEN** filters are applied  
   **THE SYSTEM SHALL** update trends to show only filtered sessions

---

## 4. State & Navigation (REQ-004)

### 4.1 Session State Handling
#### User Story
AS THE SYSTEM  
WHEN managing quiz state across page navigation  
I WANT to handle state properly  
SO THAT users don't see conflicting data

#### Acceptance Criteria
1. **WHEN** user navigates away from quiz page  
   **THE SYSTEM SHALL** preserve quiz state in session_state

2. **WHEN** user navigates to a different page  
   **THE SYSTEM SHALL** track current page

3. **WHEN** user navigates back to quiz from Dashboard  
   **THE SYSTEM SHALL** maintain quiz state if quiz is in progress

4. **WHEN** quiz is finished and user changes settings  
   **THE SYSTEM SHALL** reset quiz state before starting new quiz

5. **WHEN** user moves to different page while quiz is finished  
   **THE SYSTEM SHALL** reset quiz state on re-entry to quiz page

6. **WHEN** quiz settings change after finish  
   **THE SYSTEM SHALL** detect settings fingerprint change and reset state

### 4.2 Page Navigation
#### User Story
AS A student  
WHEN I want to move between quiz and dashboard  
I WANT convenient navigation  
SO THAT I don't have to manually enter URLs

#### Acceptance Criteria
1. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** provide "Play again" button (restarts same mode)

2. **WHEN** quiz finishes  
   **THE SYSTEM SHALL** provide "Go to Dashboard" page link

3. **WHEN** Dashboard is displayed  
   **THE SYSTEM SHALL** provide navigation to Multiplication quiz via sidebar

---

## 5. Addition Quiz (REQ-005)

### 5.1 Quiz Configuration
#### User Story
AS A student  
WHEN I load the Addition quiz page  
I WANT to customize my quiz settings  
SO THAT I can practice at my preferred difficulty level

#### Acceptance Criteria
1. **WHEN** a user selects difficulty level (Beginner/Intermediate/Advanced)  
   **THE SYSTEM SHALL** update the number range accordingly:
   - Beginner: 1-10
   - Intermediate: 1-50
   - Advanced: 1-100

2. **WHEN** a user specifies total questions  
   **THE SYSTEM SHALL** accept values from 1 to 500

3. **WHEN** a user adjusts the timer per question  
   **THE SYSTEM SHALL** accept values from 2 to 60 seconds

4. **WHEN** a user clicks "Start"  
   **THE SYSTEM SHALL** initialize quiz with selected configuration

### 5.2 Question Generation
#### User Story
AS A student  
WHEN I start an addition quiz  
I WANT the system to generate random questions  
SO THAT I get varied practice

#### Acceptance Criteria
1. **WHEN** quiz initializes  
   **THE SYSTEM SHALL** generate total_q unique random addition problems based on selected range

2. **WHEN** quiz runs  
   **THE SYSTEM SHALL** present questions in random order

### 5.3 Answer Validation
#### User Story
AS A student  
WHEN I submit an answer to an addition question  
I WANT immediate feedback on correctness  
SO THAT I know if I need to study more

#### Acceptance Criteria
1. **WHEN** a user submits a numeric answer  
   **THE SYSTEM SHALL** validate it against correct result

2. **WHEN** answer is correct  
   **THE SYSTEM SHALL** increment score counter and show ✅ feedback

3. **WHEN** answer is incorrect  
   **THE SYSTEM SHALL** show correct answer and move to next

4. **WHEN** timer expires before answer  
   **THE SYSTEM SHALL** record as TIMEOUT and advance

---

## 6. Subtraction Quiz (REQ-006)

### 6.1 Logic Constraints
#### User Story
AS A student  
WHEN I play the subtraction quiz  
I WANT to avoid negative results  
SO THAT I can focus on basic arithmetic

#### Acceptance Criteria
1. **WHEN** generating subtraction questions  
   **THE SYSTEM SHALL** ensure the first number (minuend) is greater than or equal to the second number (subtrahend)

2. **WHEN** a user selects difficulty level  
   **THE SYSTEM SHALL** set ranges (Beginner: 1-10, Intermediate: 1-20, Advanced: 1-50)

---

## 7. Division Quiz (REQ-007)

### 7.1 Operation Modes
#### User Story
AS A student  
WHEN I play the division quiz  
I WANT to practice with whole number results or remainders  
SO THAT I can master different division techniques

#### Acceptance Criteria
1. **WHEN** configuring division quiz  
   **THE SYSTEM SHALL** provide a toggle for "Whole Numbers Only" vs "With Remainders"

2. **WHEN** "Whole Numbers Only" is selected  
   **THE SYSTEM SHALL** generate questions where dividend is a multiple of divisor

---

## 8. Difficulty Progression (REQ-008)

### 8.1 Performance-Based Scaling
#### User Story
AS A student  
WHEN I consistently score well  
I WANT the system to suggest harder levels  
SO THAT I continue to be challenged

#### Acceptance Criteria
1. **WHEN** accuracy exceeds 90% for 3 consecutive sessions in one mode  
   **THE SYSTEM SHALL** suggest increasing difficulty level

---

## 9. Audio Feedback (REQ-009)

### 9.1 Audio Events
#### User Story
AS A student  
WHEN I answer questions  
I WANT sound effects for feedback  
SO THAT the experience is more engaging

#### Acceptance Criteria
1. **WHEN** answer is correct  
   **THE SYSTEM SHALL** play "correct" sound (if audio is enabled)

2. **WHEN** timer reaches 5 seconds  
   **THE SYSTEM SHALL** play "tick-tock" warning sound

---

## 10. Mobile Optimization (REQ-010)

### 10.1 UI Adaptability
#### User Story
AS A student  
WHEN I use the app on a tablet or mobile  
I WANT a responsive layout  
SO THAT it is easy to read and interact with

#### Acceptance Criteria
1. **WHEN** screen width is less than 768px  
   **THE SYSTEM SHALL** stack sidebar elements and use larger tap targets

---

## 11. Error Handling & Edge Cases

### 11.1 Invalid Input Handling
#### User Story
AS A student  
WHEN I submit answers to quiz questions  
I WANT the system to handle invalid input gracefully  
SO THAT I'm not confused by unexpected errors

#### Acceptance Criteria
1. **WHEN** student submits non-numeric text  
   **THE SYSTEM SHALL** display validation error without crashing

2. **WHEN** student submits empty input  
   **THE SYSTEM SHALL** treat as invalid input

3. **WHEN** student submits negative numbers  
   **THE SYSTEM SHALL** accept them (valid input, just wrong answer in most cases)

4. **WHEN** student submits decimal numbers  
   **THE SYSTEM SHALL** accept them (valid input, just wrong answer)

### 11.2 Data Corruption Recovery
#### User Story
AS THE SYSTEM  
WHEN files are missing or corrupted  
I WANT to recover gracefully  
SO THAT users aren't blocked from using the app

#### Acceptance Criteria
1. **WHEN** sessions.json is missing  
   **THE SYSTEM SHALL** initialize with empty list

2. **WHEN** best_scores.json is missing  
   **THE SYSTEM SHALL** initialize with empty dict

3. **WHEN** JSON files are corrupted  
   **THE SYSTEM SHALL** return default values and log gracefully

4. **WHEN** Dashboard loads with no sessions  
   **THE SYSTEM SHALL** show helpful message, not error

### 11.3 Time Handling
#### User Story
AS THE SYSTEM  
WHEN managing timers  
I WANT to handle edge cases  
SO THAT timing is accurate

#### Acceptance Criteria
1. **WHEN** timer reaches exactly 0 seconds  
   **THE SYSTEM SHALL** trigger timeout

2. **WHEN** timer goes negative (system lag)  
   **THE SYSTEM SHALL** trigger timeout, not show negative time

3. **WHEN** elapsed time is recorded  
   **THE SYSTEM SHALL** round to 3 decimal places

---

## 12. Performance & Constraints

### 12.1 Performance Requirements
- Quiz should respond to answer submissions within 200ms
- Dashboard should load with <1000 sessions in <2 seconds
- Timer update should refresh at least every 100ms for accuracy
- State transitions should be instantaneous

### 12.2 Data Constraints
- Maximum session file size: 100MB (accommodates ~100,000 sessions)
- Maximum score file entries: 10,000 unique mode keys
- Question generation must complete within 1 second
- Support up to 500 questions per quiz session

---

## TEMPLATE: Adding Requirements for a New Feature
**Step 2 in the Feature Development Flow (Requirements-First)**

After defining features in Features.md, formalize the "what" before the "how".

### Step 1: Update Requirement Master Table
Add a new row to the Requirement Master Table at the top of the file mapping to the Feature ID.

### Step 2: Create Feature Section with User Stories
Add a new section for the feature with User Stories and clear Acceptance Criteria.

### Step 3: Define System Behaviors (EARS Format)
Use the EARS format for precision and testability:
- **WHEN** [Event/Trigger]
- **THE SYSTEM SHALL** [Action/Response]

### Step 4: Define Functional Requirements
List specific functional capabilities required for the feature.

### Step 5: Define Edge Cases and Error Handling
Be explicit about how the system handles:
- Invalid inputs
- Missing data
- System failures/timeouts
- Boundary conditions

---

## Checklist When Adding Requirements
- [ ] Updated Requirement Master Table
- [ ] Created feature section with User Stories
- [ ] Acceptance criteria are clear and testable
- [ ] All System Behaviors in EARS format (**WHEN... THE SYSTEM SHALL...**)
- [ ] Functional requirements listed
- [ ] Edge cases and error handling defined
- [ ] Performance and non-functional constraints specified
- [ ] Validated all user scenarios are covered
- [ ] Ready to move to Design.md

### Next Step
After completing Requirements.md, proceed to **Design.md** to architect the solution.

**FEATURE DEVELOPMENT FLOW CHECKLIST:**
1. ✅ Features.md - Define what feature does
2. ✅ Requirements.md - Define acceptance criteria (YOU ARE HERE)
3. → Design.md - Architect the solution
4. → Architecture.md - Update system diagrams
5. → Tasks.md - Break into development tasks
6. → Implementations.md - Add code examples
7. → Testing.md - Define test strategy
8. → README.md - Update documentation
9. → Release.md - Tag and publish

