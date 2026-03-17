---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

## When to Use

- Have implementation plan
- Tasks mostly independent
- Stay in same session

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Two-stage review after each task: spec compliance first, then code quality
- Faster iteration (no human-in-loop between tasks)

## The Process

1. Read plan, extract all tasks with full text, note context
2. For each task:
   - Dispatch implementer subagent with full task text + context
   - If implementer asks questions, answer clearly
   - Implementer implements, tests, commits, self-reviews
   - Dispatch spec reviewer subagent
   - If issues found, implementer fixes → re-review
   - Dispatch code quality reviewer subagent
   - If issues found, implementer fixes → re-review
   - Mark task complete
3. After all tasks: dispatch final code reviewer
4. Use finishing-a-development-branch skill

## Model Selection

Use the least powerful model that can handle each role to conserve cost and increase speed.

**Mechanical implementation tasks** (isolated functions, clear specs, 1-2 files): use a fast, cheap model.

**Integration and judgment tasks** (multi-file coordination, pattern matching, debugging): use a standard model.

**Architecture, design, and review tasks**: use the most capable available model.

## Handling Implementer Status

**DONE:** Proceed to spec compliance review.

**DONE_WITH_CONCERNS:** The implementer completed the work but flagged doubts. Read the concerns before proceeding.

**NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Provide the missing context and re-dispatch.

**BLOCKED:** The implementer cannot complete the task. Assess the blocker:
- If it's a context problem, provide more context and re-dispatch
- If the task requires more reasoning, re-dispatch with a more capable model
- If the task is too large, break it into smaller pieces
- If the plan itself is wrong, escalate to the human

## Red Flags

**Never:**
- Start implementation on main/master branch without explicit user consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents in parallel (conflicts)
- Start code quality review before spec compliance is ✅ (wrong order)
- Move to next task while either review has open issues

## Integration

**Required workflow skills:**
- **using-git-worktrees** - Set up isolated workspace before starting
- **writing-plans** - Creates the plan this skill executes
- **finishing-a-development-branch** - Complete development after all tasks
