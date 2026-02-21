# Task Management Guidelines

To ensure smooth progress and maintain the link between requirements and technical implementation, follow these instructions when working with `docs/tasks.md`:

## Working with the Task List
- **Marking Completion**: When a task is finished, change the `[ ]` to `[x]`.
- **Modifying Tasks**: If a task needs more detail or becomes obsolete, you may edit it, but ensure it remains linked to its original Plan Item and Requirement.
- **Adding New Tasks**: If you discover additional technical steps required to fulfill a plan item:
  - Add the new task to the appropriate Phase.
  - Link it explicitly to the corresponding Plan Item and Requirement(s).
  - Use the existing format: `N. [ ] Description. - *Plan Item*: X - *Requirement*: Y`.
- **Maintaining Phases**: Keep the existing phase structure (`Phase 1: ...`, `Phase 2: ...`) to track high-level progress.

## Synchronization
- Before starting a new phase, review the `docs/plan.md` to ensure the tasks fully cover the plan's objectives.
- If a requirement in `docs/requirements.md` changes, update the corresponding items in `docs/plan.md` and `docs/tasks.md` accordingly.

## Formatting
- Maintain consistent indentation (3 spaces for sub-points).
- Ensure the numbering remains sequential within each phase or across the entire document as currently styled.

## TDD Guidelines
- **Write Tests First**: Before implementing any feature, write a test that defines the expected behavior.
- **Red-Green-Refactor**:
  1. **Red**: Run the test and ensure it fails.
  2. **Green**: Write the minimum code necessary to make the test pass.
  3. **Refactor**: Clean up the code while ensuring tests remain green.

## Git Commit Standards
- **Format**: Start the first line with the issue code (e.g., `PWPT-1:`) followed by a concise summary.
- **Style**: Follow Google's commit message standard.
- **Constraints**: Every line of the commit message must be less than 50 characters.
- **Branching**: The branch to create in this project will always be `PWPT-{issue id}`.
- **Git Execution**: 
   - **Container**: ONLY `git commit` must be run inside the container.
     - Command: `docker exec -it app sh -l -c "git commit <...>"`
   - **Host**: All other `git` commands (push, pull, branch, checkout, etc.) and all `gh` commands (pr create, issue edit, project item-edit, etc.) MUST be run on the host machine.
   - **Project Status Updates**: Use `gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <option-id>` to update the status of the issue in the project board.
   - **Status Transitions**:
     - When starting an issue: Change to "In progress".
     - When completing a task: Change to "In review".

## Post-Implementation
- **Branch Pushing**: Always push the current branch to the remote repository.
- **PR Creation**: Create a Pull Request (PR) and link it to the issue (e.g., "Closes #5").
  - Command: `gh pr create --base main --head <current-branch> --title "PWPT-<id>: <summary>" --body "Closes #<id>"`
- **Project Update**: Use `gh project item-edit` to update the status of the item in the project board to "In review".

## Running Tests
- Use Docker to run tests to ensure environment consistency.
- **Command**: `docker exec app uv run python manage.py test <app_name>`
