# Spec-Driven Development Prompt
Transform the provided high-level requirements into a complete set of project planning artifacts for spec-driven development.  
## Instructions:
You must produce **four files** inside the `docs/` and `.junie/` directories:  
- `docs/requirements.md`  
- `docs/plan.md`  
- `docs/tasks.md`  
- `.junie/guidelines.md`  
Follow the methodology below step by step:
---
### Step 1: Create `docs/requirements.md`
- Title: **Requirements Document**  
- Introduction: Summarize the application purpose and key functionality.  
- Requirements section:  
  - Use sequential numbering (1, 2, 3, …).  
  - Each requirement must include:  
    - **User Story** in the format:  
      > As a user, I want [goal] so that [benefit/reason]  
    - **Acceptance Criteria** in the format:  
      > WHEN [condition] THEN the system SHALL [expected behavior]  
- Guidelines:
  - Focus on issue output, user goals and benefits.  
  - Make acceptance criteria specific, testable, and precise.  
  - Cover normal flows, edge cases, error handling, persistence, and UI/UX.  
  - Group related requirements logically.  
---
### Step 2: Create `docs/plan.md`
- Analyze `docs/requirements.md`.  
- Develop a **detailed implementation plan**:  
  - Link each plan item explicitly to the corresponding requirements.  
  - Assign priorities (e.g., High, Medium, Low).  
  - Group related plan items logically.  
- Ensure comprehensive coverage of all requirements.  
---
### Step 3: Create `docs/tasks.md`
- Based on the implementation plan in `docs/plan.md`, produce a **detailed enumerated technical task list**:  
  - Each task must have a placeholder `[ ]` to mark completion.  
  - Link each task both to:  
    - the development plan item in `docs/plan.md`  
    - the related requirement(s) in `docs/requirements.md`  
- Group tasks into **development phases**.  
- Organize phases logically (e.g., Setup → Core Features → Advanced Features → Testing & QA).  
---
### Step 4: Create/Update `.junie/guidelines.md`
- Add **concise technical instructions** on how to work with the `docs/tasks.md` checklist, follow TDD, maintain git standards, and run tests.  
- Instructions should include:  
  - **Task Management**: Mark tasks as `[x]` when completed, maintain links to plan items and requirements, and keep phases intact.  
  - **Synchronization**: Ensure `docs/requirements.md`, `docs/plan.md`, and `docs/tasks.md` are always in sync.  
  - **TDD Guidelines**: Explicitly mention the Red-Green-Refactor cycle.  
  - **Git Commit Standards**: Define the standard (Issue code prefix, Google style, <50 chars per line).  
  - **Running Tests**: Specify the command to run tests via Docker: `docker exec app uv run python manage.py test <app_name>`.  
  - **Formatting**: Keep formatting consistent with the existing style (e.g., 3-space indentation for sub-points).  
---
## Input:
[Ask user which issue they want to solve from `gh issue list`; The user should provide either the id or title of the issue.]  
## Output:
1. `docs/requirements.md` – structured requirements document  
2. `docs/plan.md` – implementation plan with priorities and links  
3. `docs/tasks.md` – detailed enumerated task list grouped into phases  
4. `.junie/guidelines.md` – updated concise instructions for working with the task list, TDD, git standards, and testing
