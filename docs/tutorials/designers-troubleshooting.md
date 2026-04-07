# Troubleshooting for Designers

Common situations you may encounter when working with SEJA, and how to resolve them.

---

## 1. /design asks a question I do not understand

**Situation**: The agent asks a configuration question using unfamiliar terminology.

**Why**: /design covers technical options that may not match your vocabulary yet.

**Fix**: Type `default` to accept the recommended value and move on. You can re-run `/design` later to revisit any answer once you understand the options better.

---

## 2. The generated code does not match my intent

**Situation**: The agent produced output that does not reflect what you described.

**Why**: The agent interprets your words literally. Vague or ambiguous descriptions lead to unexpected results.

**Fix**: Re-run the skill with a clearer, more specific description. Alternatively, open the design-intent files in your project and edit them directly -- the agent reads these files on every run.

---

## 3. I answered a question wrong and want to change it

**Situation**: You gave the wrong answer during /design and want to correct it.

**Why**: Answers are saved to configuration files as you go.

**Fix**: Re-run `/design`. It overwrites previous answers with your new responses. There is no need to manually find and edit configuration files.

---

## 4. The plan has too many steps and I feel overwhelmed

**Situation**: A generated plan has 10 or more steps and you do not know where to begin.

**Why**: Plans are comprehensive by design. They break large changes into small, safe increments.

**Fix**: Focus only on Step 1. The agent executes one step at a time. You do not need to understand all steps before starting. Each step builds on the previous one.

---

## 5. /check found issues I do not understand

**Situation**: The quality check reports problems using technical language.

**Why**: /check validates against multiple quality criteria, some of which are developer-oriented.

**Fix**: Ask the agent to explain the findings. Run `/explain` and paste the check output -- the agent will translate the issues into plain language and suggest next steps.

---

## 6. I see an error message in the terminal

**Situation**: Red text or a stack trace appears in the terminal during a command.

**Why**: Something unexpected happened -- a missing file, a permissions issue, or a configuration problem.

**Fix**: Copy the entire error message and paste it to the agent. Ask "What does this error mean and how do I fix it?" The agent can diagnose most errors from the message text alone.

---

## 7. I want to undo what the agent did

**Situation**: The agent made changes you do not want to keep.

**Why**: The agent commits changes to git after each step, which means every change is reversible.

**Fix**: Ask the agent to revert the last commit. Git tracks every change the agent makes, so you can always return to any previous state by reverting one or more commits.

---

## 8. The agent is asking for permission and I am not sure

**Situation**: A permission prompt appears and you do not know whether to allow or deny it.

**Why**: The agent requests permission before performing actions that modify files or run commands.

**Fix**: Read the description in the permission prompt carefully. **Read operations** (viewing files, searching code) are safe to allow. **Write operations** (creating files, running commands) deserve a closer look -- if the description matches what you asked for, allow it. When in doubt, deny and ask the agent to explain what it wants to do.
