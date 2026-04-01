# CONCEPTUAL DESIGN TO-BE -- TaskFlow Demo

<!-- maintained-by: human (designer) -->

> Target design for the TaskFlow demo project.

---

## 1. Platform Purpose

TaskFlow is a lightweight task management application for individuals. Users create tasks, assign them to categories, and track completion status. The app runs entirely in the browser with no backend -- local storage persists data between sessions.

### Design Philosophy

Simplicity over features. Every screen should be understandable within five seconds. If a feature requires explanation, it is too complex for this project.

---

## 2. Entity Hierarchy

```
Category
  +-- Task
```

### Category

Represents a grouping of related tasks (e.g., "Work", "Personal", "Errands").

- **Fields**: `id` (uuid), `name` (string, 1-30 chars), `color` (hex string)
- **Uniqueness**: Name must be unique (case-insensitive)
- **Default**: A "General" category exists on first launch and cannot be deleted

### Task

The atomic unit of work within a category.

- **Fields**: `id` (uuid), `title` (string, 1-120 chars), `description` (string, 0-500 chars, optional), `status` (enum: `todo` | `done`), `categoryId` (references Category.id), `createdAt` (ISO timestamp)
- **Scope**: Belongs to exactly one Category
- **Default status**: `todo` on creation
- **Soft delete**: Not supported -- tasks are permanently removed

---

## 3. Domain-Specific Concepts

### Status Toggle

A task's status flips between `todo` and `done` via a single click or keyboard action. There is no intermediate state (e.g., "in progress") by design -- this keeps the model binary and the UI simple.

---

## 4. Validation Constants

| Constant | Value | Rationale |
|----------|-------|-----------|
| Category name length | 1-30 chars | Short enough to fit in sidebar labels |
| Task title length | 1-120 chars | One line in most viewports |
| Task description length | 0-500 chars | Optional detail without encouraging essays |
| Max categories | 20 | Prevents choice overload |
| Max tasks per category | 200 | Performance guard for DOM rendering |
