# Foundations

We wrote this file because a designer who spends any real time inside SEJA eventually asks a version of the same question: why is the framework shaped this way?
Why first-person prose in the design specs, why three marker types instead of one status field, why a council debate for hard calls, why so much reflection machinery around every skill?

The honest answer is that SEJA sits inside a tradition -- semiotic engineering, and the reflective-practice literature it draws on -- and that tradition shapes every one of those choices.
This file is our attempt to hand you the tradition in the register we actually hold it in: plain-language, first-person, and provisional.
Everything below is a current reading. We have tried to be honest about what we know and where we are hedging, and we expect the file to move as our understanding does.

The audience we are writing for is the SEJA designer, not the HCI researcher.
You do not need to have read de Souza's 2005 book before you open this file; if you have, you will recognize the citations and probably disagree with at least one of our readings, which is fine.
You do not need to read this file to use SEJA; the critical path runs through the quickstart and the how-to guides.
Read this when you find yourself asking "why."

## Software as designed communication

We currently read software as a message.
Not as a product, not as a tool, not as a system -- as a message that a designer sends to a user, mediated by code that speaks on the designer's behalf at use time.

This is the central premise of semiotic engineering as de Souza articulated it in *The Semiotic Engineering of Human-Computer Interaction* (de Souza 2005, Ch. 1 and 3): human-computer interaction is a special case of computer-mediated human communication, and the interface is where the designer talks to the user through a stand-in.

De Souza calls that stand-in the **designer's deputy**.
The deputy is not the system; it is the designer's voice speaking through the system, at a moment the designer is not in the room.
Every label, every error message, every transition, every default value is a line of the deputy's script.
When the user opens the application and starts clicking around, they are reading the script; when the script fails them, the designer has failed them.

We find this framing clarifying because it puts responsibility where we think it belongs.
The system is not an autonomous thing with its own intentions; the system is the designer, speaking at a distance, through a medium that happens to be executable.
If the user cannot figure out what to do, the deputy stumbled over its lines.
That is a communication breakdown, and it is diagnosable the way communication breakdowns are diagnosable.

The implication for SEJA is that every artifact we help you produce -- `product-design-as-intended.md`, the marker system, the plans, the advisories -- is a scaffolding for that communication.
Not a project-management overlay. A way of being more deliberate about the message you are shipping.

## The metacommunication template and why we write metacomm in first person

De Souza proposed a template for the message (de Souza 2005, Ch. 1 p.25 and Ch. 3 p.84).
The template has three structural parts: what the designer believes about the user (profile, goals, context), what the designer built (the system description), and what the designer permits the user to do that the designer did not specifically plan for (appropriation provisions).

It reads in the first person: "Here is my understanding of who you are, here is what I learned you want, here is the system I built for you, here is how you can or should use it."

We write SEJA's metacommunication in first person because the template does.
This is not a stylistic preference.
When we say "I designed a postpone shortcut for you because I know you tend to over-schedule," we are committing, in public, to a claim about you and a choice we made on your behalf.
When the prose says "the system provides a postpone shortcut," no one is accountable for anything.

The first-person phrasing rule that lives in `_references/general/shared-definitions.md` is there to hold the moral weight of the template, not to enforce a house style.

Barbosa et al. (2021) extended the template in their FAccT paper as the **Extended Metacommunication Template (EMT)**.
They added four lifecycle dimensions -- analysis, design, implementation, and post-deployment evaluation -- each carrying base questions (what did I learn about you, what did I build) and explicit ethical questions about beneficence, non-maleficence, autonomy, and justice.

They also named the team dynamic we were circling around without a vocabulary: "distributed we to collective we to I," the process by which members of a design team each write their own metacommunication message, negotiate a shared version, and then converge on a single first-person voice.
SEJA's EMT chapters in the `/design` questionnaire come directly from this extension.
That is also where `product-design-as-intended.md` gets its shape.

## Sign systems and why SEJA's markers are one

Inside the same 2005 book, de Souza borrowed from Peirce and Eco to sort interface signs into three classes (de Souza 2005, Ch. 4; de Souza and Leitao 2009, pp.19-20).

**Static** signs are read in a single moment -- a label, a layout, an icon.
**Dynamic** signs emerge through interaction -- a state transition, a confirmation, an animation.
**Metalinguistic** signs explain the other two -- help text, error messages, tooltips.

The three classes are how the Semiotic Inspection Method segments its analysis before collating it back into a unified reading of the designer's message.

De Souza also picked up Eco's distinction between **signification systems** and **communication processes** (de Souza 2005, Ch. 2 pp.71-72, citing Eco 1976).
A signification system is the socially conventionalized pool of expression-content pairs a group has available; a communication process is what someone does when they reach into that pool and assemble an intentional message.
The two are related but not the same, and the gap between them is where invention happens.

We read SEJA's marker system -- STATUS, ESTABLISHED, CHANGELOG_APPEND -- as a designed signification system in exactly this sense.
The three markers are a small, conventionalized vocabulary for lifecycle events.
STATUS names where an item is on its way from `proposed` to `implemented` to `established`.
ESTABLISHED is the promotion stamp that records a human confirmation.
CHANGELOG_APPEND is the append-only channel for audit entries.

Each marker has a fixed shape (`apply_marker.py` enforces it) and a fixed place (`check_human_markers_only.py` rejects writes outside the allowed pattern).
Together they form a sign system in the semiotic sense: a small, conventionalized vocabulary that the designer and we can use to talk about lifecycle without either of us having to rewrite prose every time intent moves.

The concepts.md chapter on the sign system tells you how the vocabulary reads in practice; this file tells you why we treat the vocabulary as a sign system at all.

## Reflective practice and abduction

The other tradition SEJA sits inside is Donald Schon's **reflective practice** (Schon 1983, *The Reflective Practitioner*).
Schon named three registers of reflection and we keep them separate in our heads because they license different kinds of move.

**Reflection-in-action** is thinking about what you are doing while you are doing it -- the in-the-moment pause to second-guess a step.
**Reflection-on-action** is pausing after the work is done to think back over what happened.
**Reflection-on-practice** is the longer-horizon register where you surface and criticize the tacit patterns you have been running without noticing.

De Souza adopted Schon's view as the foundational stance of semiotic engineering (de Souza 2005, Ch. 1 pp.31-33), explicitly rejecting the technical-rationality framing in which design is a straight application of theory.

Schon's account pairs naturally with Peirce's **abduction**.
Abduction is the mode of reasoning where you observe a surprising fact, entertain a hypothesis that would explain it if true, and provisionally hold the hypothesis as your best available reading until something contradicts it.
Peirce is blunt about the provisionality: an abductive conclusion holds only until better evidence arrives.
It is the only mode of reasoning that admits creative formulations, and it is the engine of reflective sense-making.

SEJA operationalizes abduction explicitly in council-debate (the `--deep` mode of `/advise`).
A council is a small group of named experts, each running their own abductive reading of the same question, brought into structured disagreement so the synthesis we hand back has visible counter-readings baked in.

The design choice is deliberate: we do not want to pretend a single recommendation is the only plausible one, so we make the plurality of readings part of the deliverable.

## Reflecting while you work with SEJA

The framework carries three concrete scaffolds so reflective practice is not just something we talk about in a primer but something you can feel in your hands when you use the skills.

**Decision-point rationale at every AskUserQuestion.**
When a skill pauses to ask you a question -- pick a profile, pick a pattern, confirm a marker flip, pick the next suggestion -- we carry a short rationale for each option so you see not just "what" but "why this is on the menu."
The rationale is the smallest reflection-in-action scaffold we know how to build: it turns a silent branch into a tiny visible deliberation.
You can disagree with the rationale and pick the other option anyway.

**Post-action reflection loop after `/implement`, `/plan`, `/design`, and `/document`.**
When one of the heavier skills finishes, we write a brief reflection-on-action note covering what actually happened, what deviated from the plan, and what we are less sure about now than we were at the start.
The note is short on purpose.
It is not a postmortem; it is the smallest possible act of looking back before the next turn begins.

**The `/reflect` skill for cross-session pattern analysis.**
Reflection-on-practice is the longest-horizon register and it needs its own surface.
The `/reflect` skill scans recent briefs, QA logs, and pending-ledger entries to surface patterns across sessions -- what kinds of questions keep coming back, where confirmations stall, where the same drift recurs between intent and code.
This is the reflective register that cannot run inside a single turn; it needs the trail of many turns to see anything.

Each scaffold is deliberately minimal.
The point is not to ritualize reflection into a ceremony you will skip; the point is to put one small, structured pause at each of Schon's three registers so reflective practice becomes a habit you do not have to remember to adopt.

## What we are uncertain about

We are not confident the first-person phrasing rule survives a multi-designer team without dilution.
The EMT extension's "distributed we to collective we to I" process is an attempt to solve exactly this problem, but we have only run it in small collaborations, and we do not know what happens when the team is ten people.
We suspect the first-person voice starts to read as performative at some team size, and we do not yet know where the ceiling is.

We are also not confident that the post-action reflection loop will stay short.
The failure mode we are most worried about is that it turns into a boilerplate paragraph the designer stops reading, which would make the scaffold worse than having no reflection at all.
Keeping it minimal is a design choice we will need to defend each time the loop is tempted to grow.

We are least confident about the council-debate as an operationalization of abduction.
The debate does produce plural readings; we are less sure that the synthesis we hand back at the end does justice to the disagreement.
The temptation is to collapse plurality into a single recommendation because recommendations are easier to act on.

## A critical counter-reading

Eraut (1994, *Developing Professional Knowledge and Competence*) is sharp about the limits of reflection-on-action as a professional-learning mechanism.
His concern, which we take seriously, is that engineered reflection scaffolds can become performative rituals -- the professional learns to produce the shape of a reflection without doing the cognitive work the shape was meant to elicit.

Boud (2013) makes a related argument about reflective writing in educational settings: when the reflection becomes an assessed artifact, it stops being a thinking tool and starts being a genre performance.

The counter-reading would say that SEJA's reflection scaffolds -- the decision-point rationale, the post-action loop, the `/reflect` skill -- risk exactly this.
By turning reflection into something the framework will ask you to produce on a schedule, we may be training a habit of shape without substance.

We find this position instructive even where we do not fully accept it.
The version we accept is that the scaffolds must stay small enough that performance is not worth the effort; the version we do not accept is that the alternative -- no scaffolding at all -- produces better reflection.

## Further reading

The primary sources behind this primer are:

- de Souza, C.S. (2005). *The Semiotic Engineering of Human-Computer Interaction*. Cambridge, MA: MIT Press. The foundational theory book; metacommunication template (Ch. 1 and 3), sign classes (Ch. 4), designer's deputy, communicability.
- de Souza, C.S. and Leitao, C.F. (2009). *Semiotic Engineering Methods for Scientific Research in HCI*. Morgan and Claypool. Definitive methodological treatment of SIM and CEM; sign-class procedure; first-person collective sender framing.
- de Souza, C.S., Cerqueira, R.F.G., Afonso, L.M., Brandao, R.R.M., and Ferreira, J.S.J. (2016). *Software Developers as Users: Semiotic Investigations in Human-Centered Software Development* (the SigniFYI book). Springer. Extends semiotic engineering from end-user HCI to the developer-facing pipeline.
- Barbosa, S.D.J., Barbosa, G.D.J., de Souza, C.S., and Leitao, C.F. (2021). "A Semiotics-based epistemic tool to reason about ethical issues in digital technology design and development." *Proc. FAccT '21*, pp.363-374. The Extended Metacommunication Template (EMT) with its four lifecycle dimensions and the "distributed we to collective we to I" process.
- Schon, D.A. (1983). *The Reflective Practitioner: How Professionals Think in Action*. New York: Basic Books. Reflection-in-action, reflection-on-action, reflection-on-practice; conversation with materials.
- Eraut, M. (1994). *Developing Professional Knowledge and Competence*. London: Falmer Press. The critical counter-reading used above on the limits of engineered reflection.

The private `_output/semiotic-engineering/` corpus holds the longer, audit-grade draft I worked from while writing this file.
Readers who want the unabridged version can open `_output/semiotic-engineering/01-concepts.md` for the concept catalog, `_output/semiotic-engineering/03-current-reading.md` for my current fit assessment, and `_output/semiotic-engineering/04-working-synthesis.md` for the working synthesis.
Those files are private on purpose: they are the scaffolding, not the primer.

> Last reviewed: 2026-04-11. I revisit this file on every major framework release.
