## Phase 1: Frontend Migration (Vue.js)

**Goal**: Modernize the frontend stack for better maintainability and performance.

- [x] Migrate existing challenges

## Phase 2: Experimental Logic & Metrics

**Goal**: Implement extra stats to capture user behavior.

- [x] Focus Tracking (The "LLM Detector"): Check when window/tab loses focus to be interpreted as LLM usage.

## Phase 3: Survey & Data Collection

**Goal**: Capture the demographics and qualitative confidence metrics.

- [ ] Expanded Pre-Task Questionnaire: Academic Background (CS Student, Professional, Self-taught), Specialization (Security Expert, Dev, RE Novice), LLM Familiarity (Frequency of use, preferred models).

- [ ] Post-Task Questionnaire

## Phase 4: New Content

Goal: Create the specific conditions needed to test the RQs.

- [ ] Create a "Helper" modal or sidebar containing the x86 Primer / Cheat Sheet.

- [ ] Design a challenge that forces LLMs to hallucinate explanations. Ensure LLM prompts produce confident but wrong explanations.

## Example of Questinnaires

### Part 1: Pre-Test Questionnaire

**Goal**: Segment the audience (Student vs. Pro) and establish a baseline for their trust/usage of LLMs.

Section A: Demographics & Background

1. Current Role:
[ ] Computer Science Student (Undergrad/Master)
[ ] Software Developer (Non-Security)
[ ] Cybersecurity Professional (Non-RE focus)
[ ] Other

2. How would you rate your experience with Reverse Engineering (RE)?
* (1) Absolute Beginner (Never opened a disassembler)
* (2) Novice (Tried a few crackmes/CTFs)
* (3) Intermediate (Can solve standard challenges)
* (4) Advanced/Professional

3. How familiar are you with x86 Assembly architecture?
* (1) I cannot read it at all.
* (2) I know basic instructions (MOV, ADD, CMP).
* (3) I can read control flow and stack operations comfortably.
* (4) I write assembly manually.

Section B: LLM Habits (Baseline) 

4. How frequently do you use LLMs (ChatGPT, Claude, Copilot) for coding tasks? 
* (1) Never 
* (2) Rarely (Once a month) 
* (3) Occasionally (Weekly) 
* (4) Daily 

5. In your daily life, how much do you trust code explanations provided by LLMs? 
* (1) I verify everything line-by-line. 
* (2) I verify complex logic but trust the basics. 
* (3) I generally trust it unless it looks obviously wrong. 
* (4) I trust it completely.

### Part 2: Post-Test Questionnaire

Section A: Confidence & Trust (Addressing RQ2)

1. How confident are you that your final solutions are correct?
(Scale 1-5: Not Confident at all -> Extremely Confident)

2. Did you use an external LLM (ChatGPT, etc.) during the challenges?
[ ] Yes
[ ] No

3. (If Yes) Did you notice the LLM providing any incorrect or "hallucinated" information?
[ ] No, the answers seemed perfect.
[ ] Yes, minor syntax errors.
[ ] Yes, it completely invented logic that wasn't there.
[ ] I'm not sure.


Section B: Efficiency & Workflow 

4. When using the LLM, what was your primary strategy? 
[ ] Copy-pasting the whole code and asking for a summary. 
[ ] Copy-pasting small functions one by one. 
[ ] Describing the logic to the LLM to verify my own understanding. 
[ ] I did not use the LLM. 

6. How did the LLM affect your ability to ignore irrelevant code? 
(Scale 1-5: It added more noise/confusion -> It helped me zoom in on important parts immediately) 

7. Estimate the balance of your time usage: Please ensure the total equals 100% 
* Reading/Annotating Code manually: [ ___ ] % 
* Writing Prompts/Reading LLM Output: [ ___ ] % 
* Debugging/Testing: [ ___ ] % 

8. Which activity felt more "expensive" or tiring to you? 
[ ] Trying to understand the Assembly manually. 
[ ] Trying to get the LLM to give me a useful answer (Prompt Engineering).