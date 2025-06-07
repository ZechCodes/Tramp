# Planning Directory Structure

This directory organizes planning documents and improvement proposals for the Tramp project.

## Directory Organization

### 📂 `active/`
Planning documents for features and improvements currently being worked on. These represent active development efforts with assigned priorities and timelines.

### 📂 `backlog/`
Planning documents for features and improvements that are planned but not yet started. These are prioritized ideas waiting for development capacity.

### 📂 `completed/`
Planning documents for features and improvements that have been successfully implemented and deployed. Kept for historical reference and lessons learned.

### 📂 `archived/`
Planning documents for ideas that have been decided against, postponed indefinitely, or superseded by other approaches. Kept for reference but not actively pursued.

## Document Naming Convention

Use descriptive names with the following format:
- `YYYY-MM-DD_feature-name.md` - For time-sensitive features
- `feature-name.md` - For general features
- `module-name_improvement.md` - For module-specific improvements

## Document Template

Each planning document should include:
- **Overview**: Brief description of the feature/improvement
- **Motivation**: Why this change is needed
- **Checklist**: Actionable steps to implement
- **Priority**: High/Medium/Low
- **Estimated Effort**: Time/complexity estimate
- **Dependencies**: Other features this depends on
- **Success Criteria**: How to measure completion

## Status Transitions

```
backlog/ → active/ → completed/
    ↓
 archived/
```

Documents move between directories as their status changes during the development lifecycle.