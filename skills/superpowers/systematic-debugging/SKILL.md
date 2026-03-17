---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes

## The Four Phases

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits

4. **Gather Evidence in Multi-Component Systems**
   - For EACH component boundary: log what enters, log what exits
   - Verify environment/config propagation
   - Check state at each layer

5. **Trace Data Flow**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

1. **Find Working Examples**
   - Locate similar working code in same codebase

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY

3. **Identify Differences**
   - What's different between working and broken?

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis

### Phase 4: Implementation

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?

4. **If 3+ Fixes Failed: Question Architecture**
   - STOP and question fundamentals
   - Discuss with your human partner before attempting more fixes

## Red Flags

**If you catch yourself thinking:**
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "One more fix attempt" (when already tried 2+)

**ALL of these mean: STOP. Return to Phase 1.**

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
