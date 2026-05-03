---
name: task-management-workflow
description: Manages the structured task workflow for RSI project including creating proposals, to-do lists, task summaries, progress tracking, and update procedures. Use when creating new tasks, updating task status, managing task files, or when the user mentions "update", "task", "proposal", "to-do", or "task summary".
---

# Task Management Workflow

## Project-Level Authority and Plan Source

- `IMPLEMENTATION_PLAN.md` at repo root is the **single source of truth** for high-level phases and status.
- If a phase/subphase is added, removed, renamed, or status changes, update `IMPLEMENTATION_PLAN.md` first, then synchronize task files.
- After each completed subtask, update all tracking documents (`conversation_cursor`, `to-do`, `task_summary`, `structure/latest.md`, `progress/latest.md`) to keep them aligned with `IMPLEMENTATION_PLAN.md`.

## File Creation and Download Permission

- The agent may create/modify/download files without per-file confirmation when file size is **<= 200 MB**.
- For a file expected to exceed **200 MB**, inform the user before creating/downloading.

## Workflow Structure

This project uses a structured workflow to track tasks systematically with three synchronized files per task.

## File Locations

All files for the same task must use the **exact same filename** (task_name.md):

- `conversation_cursor/YYYYMM/YYYYMMDD/task_name.md` - Technical proposals and design decisions
- `to-do/YYYYMM/YYYYMMDD/task_name.md` - Checklists and actionable steps
- `task_summary/YYYYMM/YYYYMMDD/task_name.md` - Task objectives, deliverables, and progress

**Task naming**: task_name must start with a verb (e.g., "modify_solve_value_mean", "implement_feature", "refactor_pipeline")

## Reading Project Context

Before creating any task files, read these files in order:

1. **README.md** - Workflow and task management structure
2. **IMPLEMENTATION_PLAN.md** - Single-source high-level phase plan
3. **structure/latest.md** - Current project structure and file descriptions
4. **progress/latest.md** - Active tasks and their status
5. **task_summary/YYYYMM/YYYYMMDD/[most_recent].md** - Most recent task summary

## Creating Task Files

### 1. Create Proposal
**Location**: `conversation_cursor/YYYYMM/YYYYMMDD/task_name.md`
- Draft technical proposal
- Document design decisions and approach
- Focus on HOW and WHY (rationale, architecture)

### 2. Create To-Do List
**Location**: `to-do/YYYYMM/YYYYMMDD/task_name.md`
- Checklist with checkboxes for each subtask
- Contains only UNCOMPLETED tasks and next actions
- Focuses on what needs to be done

### 3. Create Task Summary
**Location**: `task_summary/YYYYMM/YYYYMMDD/task_name.md`
- Task objectives and deliverables
- Records completed work, current status, findings, and results
- Related files and dependencies
- Focuses on what has been done

## Content Division (Prevent Overlap)

- **TO-DO LIST**: Only UNCOMPLETED tasks and next actions. What needs to be done.
- **TASK SUMMARY**: Completed work, current status, findings, results. What has been done.
- **PROPOSAL**: Technical decisions, design choices, implementation approach, architectural rationale. HOW and WHY.

## Update Procedures

### "update" Command
Update these three files:
- ✓ `to-do/YYYYMM/YYYYMMDD/task_name.md` - Checklist of remaining actionable steps
- ✓ `task_summary/YYYYMM/YYYYMMDD/task_name.md` - Current state and progress summary
- ✓ `conversation_cursor/YYYYMM/YYYYMMDD/task_name.md` - Technical design and implementation decisions

### "update all" Command
Update the three files above PLUS:
- ✓ `structure/latest.md` - Update if project structure or file descriptions changed
- ✓ `progress/latest.md` - Update active/completed task status
- ✓ `IMPLEMENTATION_PLAN.md` - Update when adding/changing phases, subphases, or phase status

**Structure updates**: When updating `structure/latest.md`, use **high-level description only** and **structure-only** modifications (folder layout, brief purpose). Do not add low-level implementation detail or non-structural content.

## Task Completion

When a task is complete:
- ✓ `conversation_cursor` - Finalize with implementation results
- ✓ `to-do` - Mark all items complete
- ✓ `task_summary` - Final deliverables and outcomes
- ✓ `progress/latest.md` - Move to completed section
- ✓ `structure/latest.md` - Update file descriptions if needed (high-level, structure only; see ``update all'' rule)

**IMPORTANT**: Do NOT automatically create new tasks after completing a task. Wait for explicit user instruction.

## Testing Rule

When the user says "test" or requests testing:
1. **Run existing tests** - Execute test scripts from the `tests/` folder
2. **Write test scripts** - Create new test files in the `tests/` folder

Always clarify with the user which action is intended, or do both if appropriate.

## Examples

See [examples.md](examples.md) for examples.

