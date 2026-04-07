# How to Think About Working with SEJA

This page covers the five essential concepts you need before your first SEJA session. Read it once, then move on to a [journey](../journeys/) or [tutorial](designers-first-hour.md).

## You are the designer

SEJA is built around a simple division of labor: **you describe what you want, and the agent builds it**.

You bring the vision -- user goals, experience flows, and design intent. The agent handles implementation -- code, file structure, validation, and testing. You stay in control at every step: review plans before execution, check results after, and adjust direction whenever needed.

Think of the agent as a capable colleague who follows your lead. It reads your design files, proposes approaches, and implements what you approve. It does not make design decisions on its own.

## Skills: your toolkit

You interact with SEJA through **skills** -- commands you type that activate specific workflows. Think of them as recipe cards you hand to a colleague: each one triggers a structured process with a clear outcome.

The five skills you will use most:

- `/design` -- set up your project by answering questions about your product, users, and goals
- `/plan` -- describe a change you want and get a step-by-step implementation plan to review
- `/implement` -- execute an approved plan, one step at a time
- `/check` -- verify that the implementation meets quality standards across multiple perspectives
- `/explain` -- ask the agent to explain how something works in the existing system

You type these in Claude Code's terminal. Each skill guides you through its workflow -- you do not need to memorize options or syntax.

## What the agent sees

When you run a skill, the agent reads your project files to understand your intentions. The most important files are:

- **Design intent** -- where you describe what users should experience and why
- **Conventions** -- your project's structure, technology choices, and standards
- **Constitution** -- your project's immutable principles (the rules nothing can override)

The better you describe your vision in these files, the better the agent's work aligns with your intent. The `/design` skill helps you create these files through a guided questionnaire.

## What gets created

SEJA creates files you can read, edit, and track:

- **Plans** -- step-by-step implementation roadmaps you review before execution
- **Code** -- source files that implement your design
- **Reports** -- quality reviews, advisory logs, and explanation documents
- **Design specs** -- structured descriptions of your project's architecture and intent

Everything is saved as files in your project folder. Nothing is hidden or ephemeral. You can open any file, read it, and edit it directly.

## When things go wrong

If the agent's output does not match your intent:

- **Re-run with a clearer description.** The agent improves when you are specific about what you want and why.
- **Edit the files directly.** Design intent files, plans, and even generated code are all editable text files.
- **Ask the agent.** Type `/explain` followed by your question to understand what happened and why.
- **Undo changes.** The agent commits changes to version control, so you can always revert to a previous state.

You are always in control. The agent proposes; you decide.

## What to do next

- Read [What Is SEJA and Why Does It Exist?](../concepts/what-is-seja.md) for the full motivation and theory
- Choose a journey: [New Product](../journeys/journey-solo-designer-greenfield.md) or [Existing Product](../journeys/journey-solo-designer-brownfield.md)
- Try the [Your First Hour with SEJA](designers-first-hour.md) guided tutorial
