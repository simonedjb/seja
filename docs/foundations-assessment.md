# Foundations assessment

We wrote this file as a companion to [foundations.md](foundations.md).
Where the primer walks through the semiotic-engineering tradition in plain language, this file does the next thing down.
It lines up specific concepts from that tradition against specific SEJA artifacts and says, for each one, how we currently read the correspondence.

See [foundations.md](foundations.md) for the theoretical primer this assessment leans on.
If you have not read it yet, the rows below will be harder to follow.
Each row assumes you already know what metacommunication, sign classes, and abduction mean in the semiotic-engineering sense, and the primer is where those terms get introduced.

Every row in this file is a reading, not a fact.
We hold each correspondence provisionally.
We have tried to name, in a dedicated column on every table, the kind of counter-observation that would make us change our mind.
We expect some of the readings to move as our understanding does, as the framework grows, and as designers who use SEJA in their own practice tell us where we got it wrong.

The split between this file and the primer is deliberate.
The primer is where we argue, in plain language, that SEJA sits inside a particular intellectual tradition; this file is where we show our work.
You can read the primer and skip this file, but you cannot read this file and skip the primer and expect the rows to make sense.

If your practice suggests a different correspondence, open an issue or propose an amendment via `/advise`.
The contribution pathway at the bottom of this file says exactly how.

## How to read the tables

Every correspondence below is tagged with one of five relationship values.
Each value is prefixed with "we currently see" to hold the frame that the assessment is abductive, not deductive.
The prefix is not cosmetic: it is the grammatical form that carries the provisionality of the whole file.

- **Direct** -- we currently see a one-to-one operationalization of the source concept in a SEJA artifact.
- **Analogous** -- we currently see a similar purpose, framed differently, in a SEJA artifact.
- **Implicit** -- we currently see the concept present in SEJA but not named as such.
- **Gap** -- we do not currently see the concept in SEJA at all.
- **SEJA extends** -- we currently see SEJA going beyond what the source concept proposes.

The final column on each table is "What would change this reading."
That column is the core hedging mechanism of the whole file.
Each cell names, in one sentence, the kind of counter-observation that would make us retract or revise the correspondence.
If you find yourself nodding along to the counter-observation because your experience matches it, that is the moment to open an advisory.

## Metacommunication

This section asks what SEJA does with the metacommunication premise that software is the designer's message to the user.
We currently read the answer as: SEJA does not merely cite the premise, it operationalizes it into files and skills that teams edit on a normal working day.

This is the section we are most confident about.
It traces the thread that made us recognize SEJA as a semiotic-engineering framework at all, rather than as a collection of stylistic rules that happen to look opinionated.
The table consolidates two sub-sections of the internal mapping: the metacommunication template itself (from de Souza 2005 and extended by Barbosa et al. 2021) and the metacommunication frame form (from SigniFYI 2016).
Where the internal mapping carries both as separate subtables, we have merged them here because the distinction matters more to researchers than to the designer the primer is written for.

| SemEng concept | SEJA counterpart | Relationship | What would change this reading |
|---|---|---|---|
| The metacommunication template as the designer's message to the user (de Souza 2005, Ch. 1 and 3) | `product-design-as-intended.md` and `product-design-as-coded.md` as the paired living message | Direct | If the `product-design-*` files turn out, in practice, to be read as project-management artifacts rather than as the designer's voice, the correspondence collapses. |
| First-person "I" and second-person "you" phrasing in the template (de Souza 2005, Ch. 3) | Phrasing rule in `_references/general/shared-definitions.md`, enforced across metacomm files and skill prompts | Direct | If teams using SEJA find that the first-person voice dilutes into committee prose at team sizes above three or four, the correspondence becomes aspirational rather than direct. |
| Extended Metacommunication Template with four lifecycle dimensions and ethical guiding questions (Barbosa et al. 2021, FAccT) | SEJA's `/design` questionnaire carrying the EMT chapters (analysis, design, implementation, post-deployment) with base plus ethical questions | Direct + extends | If the ethical questions in the EMT chapters become rote boilerplate that designers skip past, the extension is nominal rather than real. |
| Post-deployment monitoring and "how much of my vision is reflected in actual use" (Barbosa et al. 2021, pp.367-368) | `/explain spec-drift` comparing as-intended and as-coded, plus the drift-detection pipeline | SEJA extends | If drift detection turns out to flag noise more often than meaningful intent-to-code mismatch, the correspondence is operationalized in name but not in function. |
| "Distributed we to collective we to I" team consensus process (Barbosa et al. 2021, p.368) | The `/design` questionnaire plus council-debate for multi-perspective negotiation | Analogous | If the council-debate rarely produces a genuine "I" at the end and instead keeps a plural voice, the operationalization is partial at best. |
| Theory-based meaning categories as a reusable tagging vocabulary (SigniFYI 2016) | No formalized tagging vocabulary in SEJA | Gap | If we discover that the lifecycle markers or the role-family tags are, in fact, a close analog to the SigniFYI categories, the gap closes to "analogous." |
| Metacommunication frame form as a structured elicitation instrument (SigniFYI 2016) | The `/design` skill's structured questionnaire | Analogous | If a future frame-form-style instrument lands in the framework with named slots and a fixed vocabulary, the reading moves to "direct." |

## Communicability

This section asks whether SEJA has anything to say about the quality of a metacommunication, not just its existence.
We currently read the answer as a partial yes, bounded by the side of the designer-user exchange that SEJA can reach.

Communicability is the quality criterion de Souza and Leitao (2009) propose for evaluating whether the designer's deputy succeeds at full metacommunication.
It is the SemEng answer to the question "how do we know this software is any good at being a message?"

We currently see SEJA addressing it from the emission side (what the designer produces) more than from the reception side (what the user experiences).
This is a structural asymmetry, not an oversight.
SEJA is a framework for producing software, not an analytical instrument for inspecting existing interfaces, and the reception-side methods (CEM in particular) rely on user observation that SEJA's pipeline does not currently carry.
The rows below reflect that asymmetry: most are "analogous" rather than "direct," and the one partial gap is on the reception side.

| SemEng concept | SEJA counterpart | Relationship | What would change this reading |
|---|---|---|---|
| Communicability as quality criterion (de Souza 2005, Ch. 4; de Souza and Leitao 2009, pp.24-25) | Spec-drift detection between as-intended and as-coded tracks whether intent survives | Analogous | If a quantitative communicability measure surfaces in SEJA (not just a boolean drift flag), the correspondence becomes direct. |
| SIM exploring emission of metacommunication (de Souza and Leitao 2009, p.25) | `/check review` inspecting code and design artifacts from the designer's side | Analogous | If a dedicated segmented-analysis-by-sign-class mode lands in `/check`, the reading moves toward direct. |
| CEM exploring reception of metacommunication (de Souza and Leitao 2009, p.25) | No user-observation method; `/explain` comes closest by reconstructing understanding | Partial gap | If SEJA grows a skill that elicits user breakdown utterances in a structured way, the gap closes. |
| Alternative metacommunication templates for different user profiles (de Souza and Leitao 2009, pp.76-77) | Role families (BLD, SHP, GRD) and expertise levels (L1 to L5); `/communication` generating audience-specific material | Direct | If designers report that the role and expertise scaffolds collapse to a single voice in practice, the correspondence is aspirational. |
| Design-time communication support for cohesive discourse (de Souza and Leitao 2009, p.78) | Pre and post-skill pipelines, constitution, and `shared-definitions.md` enforcing design-time consistency | Analogous | If those pipelines turn out to enforce surface consistency without improving downstream communicability, the analogy is cosmetic. |

## Sign classes and signification

This section asks whether SEJA carries the taxonomic vocabulary that semiotic engineering uses to break an interface apart into its constituent signs.
We currently read the answer as largely no, and we think the absence is honest rather than accidental, because SEJA produces rather than inspects.

This section joins two parts of the internal mapping.
The first is the three-class taxonomy of interface signs (static, dynamic, metalinguistic) that de Souza 2005 introduces and de Souza and Leitao 2009 formalizes as the structural basis of the Semiotic Inspection Method.
The second is Eco's distinction between signification systems and communication processes that de Souza 2005 picks up in Chapter 2 to distinguish the shared pool of conventional signs from any individual act of using them.

We currently see a sharp gap on the first and an analogy on the second.
The gap on sign classes is the single sharpest absence in SEJA's relationship to the semiotic-engineering literature, and we do not think it is accidental.
SEJA does not inspect existing interfaces; it helps produce new ones, and the sign-class taxonomy is an inspection tool.
The analogy on signification systems is carried by `conventions.md`, which we read as the project-specific pool that the framework and the designer both reach into.

| SemEng concept | SEJA counterpart | Relationship | What would change this reading |
|---|---|---|---|
| Static and dynamic signs as formal classes (de Souza 2005, Ch. 4; de Souza and Leitao 2009, pp.19-20) | No explicit classification of interface signs | Gap | If SEJA adopts sign-class tagging as a first-class concept (for example as a review lens), the gap becomes an analogy. |
| Metalinguistic signs (de Souza 2005, Ch. 4) | The `/explain` and `/help` skills serve a metalinguistic function by explaining how the framework's own signs work | Analogous | If `/explain` and `/help` cease to carry the second-order explanatory weight we currently assign them, the reading becomes implicit rather than analogous. |
| Peirce's icon, index, and symbol classification (de Souza 2005, Ch. 2) | No formal adoption in SEJA | Gap | If a future review perspective or marker grammar names icon, index, or symbol explicitly, the gap closes. |
| Conventionalized expression-content associations (de Souza 2005, Ch. 2, citing Eco 1976) | `conventions.md` as the project-specific signification system | Analogous | If `conventions.md` turns out, in audit, to be used primarily for compliance rather than for meaning, the analogy weakens. |
| Invention of new signs in communication (de Souza 2005, Ch. 2) | User-defined extensions like custom review perspectives and user-defined tags | Analogous | If users rarely extend the system in practice, the concept is present in principle but not operationalized. |
| Professional microculture shared by senders and receivers (de Souza 2005, Ch. 2) | Role families and expertise levels segment the audience by shared culture | Analogous | If role and expertise scaffolds are read as org-chart labels rather than as a shared semiotic pool, the analogy is weaker than we claim. |

## Abduction and semiosis

This section asks whether SEJA treats interpretation as a process with a beginning, a middle, and an always-deferred end.
We currently read the answer as yes, though the reading rests on operational patterns rather than on vocabulary the framework uses about itself.

We currently see SEJA embodying abductive logic without naming it.
The council-debate is the clearest example: it assembles plural interpretive perspectives, surfaces the disagreements between them, and produces a synthesis that is explicitly provisional.
The as-intended and as-coded pair embodies ongoing semiosis (meaning is always revisable) as a routine operation rather than as a theoretical commitment; the two files sit next to each other and drift detection watches the gap between them.

The reason we hedge the whole section at "analogous" rather than "direct" is that SEJA never uses the words "abduction" or "semiosis" in its public docs.
If those words surfaced in the framework's own vocabulary, the correspondence would tighten; as it stands, the concepts are operationalized without being named.

| SemEng concept | SEJA counterpart | Relationship | What would change this reading |
|---|---|---|---|
| Abduction as the logic of sense-making (de Souza 2005, Ch. 2, on Peirce) | `/advise` deep-dive mode using hypothesis and evidence reasoning | Analogous | If `/advise` shifts toward deductive checklist logic, the analogy weakens. |
| Provisional conclusions revised by new evidence (de Souza 2005, Ch. 2) | The as-intended / as-coded pair embodying revisable understanding | Analogous | If the as-coded side turns out, in practice, to be treated as authoritative rather than as provisional evidence, the correspondence flips. |
| Ongoing semiosis, never-finished interpretation (de Souza 2005, Ch. 2) | The iterative plan, implement, check, advise cycle | Analogous | If the cycle collapses toward a one-shot waterfall in practice, the semiosis reading becomes aspirational. |
| Council-debate as assembled plural interpretive perspectives (Analysis, building on SemEng-2005) | `/advise --deep` running a council of named experts and surfacing disagreement | SEJA extends | If the council synthesis collapses the plurality into a single recommendation at the end, the extension is nominal. |

## Where SEJA extends SemEng

This short table collects the places where we currently read SEJA as going beyond what the source literature proposes, rather than simply operationalizing it.
The word "extends" is doing real work here.
An operationalization turns a concept into a routine, but the concept is the source of truth; an extension adds something that the source concept does not itself propose and then asks whether the source framework can absorb the addition.
Each row below is a candidate extension, and each one could turn out to be a misreading of ours in which we have confused SEJA's operational choices with theoretical innovations.

| SEJA element | Source concept it builds on | What the extension adds | What would change this reading |
|---|---|---|---|
| Extended Metacommunication Template (EMT) with four lifecycle dimensions | Barbosa et al. (2021) FAccT paper | Operationalizes the EMT inside a live design questionnaire that tracks drift over time, not a one-shot artifact | If the EMT chapters become stale and are not revisited across the lifecycle, the extension is nominal. |
| Council-debate "distributed we to collective we to I" | Barbosa et al. (2021) team consensus process | Makes the consensus process a named skill with role personas and structured disagreement | If the council stops producing a genuine "I" at the end, the extension is partial. |
| Marker-based lifecycle (STATUS, ESTABLISHED, CHANGELOG_APPEND) | Sign-system concept from de Souza (2005, Ch. 4) | A small, machine-enforced vocabulary that tracks intent movement without rewriting prose | If the markers drift into boilerplate that designers stop reading, the extension loses force. |
| As-intended and as-coded pair with drift detection | Ongoing semiosis (de Souza 2005, Ch. 2) | A routine, machine-checkable operation rather than a theoretical commitment | If drift detection produces more noise than signal, the extension is aspirational. |

## Known gaps

These are places where we do not currently see SEJA carrying a counterpart to the source concept.
Each gap is an open question, not a declared absence.
The difference matters: a declared absence would mean we have audited the framework and found nothing, but what we are actually reporting is that we have read the source literature, looked at the SEJA artifacts we know about, and failed to find a correspondence.
If we have missed an artifact that already covers the concept, please tell us, and the gap becomes a correspondence we owe the rest of this file.

- Peirce's icon, index, and symbol classification (de Souza 2005, Ch. 2).
  We do not currently see SEJA formally adopting this three-way distinction.
  If we have missed it, please tell us.
- Full Cognitive Dimensions of Notations framework (SigniFYI 2016, citing Green and Petre).
  We do not currently see a systematic CDN-style analysis of SEJA's own notations.
  If we have missed it, please tell us.
- TNP triplet (Tool, Notation, People) from SigniFYI 2016.
  We do not currently see SEJA explicitly decomposing its own artifacts along the TNP axes.
  If we have missed it, please tell us.
- Formal semantic relations (IS-A, PART-OF, SPEAKS-FOR) from the SigniFYIng Traces ontology.
  We do not currently see SEJA carrying a formal structural ontology across the `_output/` corpus.
  If we have missed it, please tell us.
- CEM's 13 communicability breakdown categories (de Souza and Leitao 2009, pp.37-46).
  We do not currently see a structured user-side breakdown taxonomy in SEJA.
  If we have missed it, please tell us.

## Contribution pathway

If your practice suggests a different correspondence, here is how to propose a revised reading.

Open an advisory via `/advise`.
Describe the row you are disputing.
State the reading you propose in its place, and the counter-evidence that supports it.
Cite specific artifact paths wherever you can; concrete pointers go further than abstract disagreement, because this file is a mapping from concepts to artifacts and the artifacts are where the work happens.
A pointer to a file path, a skill name, or a convention that we had not considered is worth more than a general argument about semiotic engineering, because we already accept the general argument -- what we need is the specific counter-evidence.

We will respond to the advisory in the same session or the next one.
If the evidence persuades us, we will amend the table here with a dated note that names you and summarizes the change.
If the evidence does not persuade us, we will say why and add a note to the uncertainty section of `foundations.md` so the disagreement is visible even where we did not resolve it in your favor.

Either outcome is useful.
A correspondence that has survived a challenge is stronger than one that has never been tested.
A correspondence that collapses under a challenge is one we are glad to have retired before someone else acted on it.
And a disagreement that we recorded but did not resolve is a marker for where our reading is weakest, which is information the next reader of this file can use.

Here is a concrete example of the shape a revised-correspondence proposal can take.
Suppose a designer using SEJA with a small team notices that the role families (BLD, SHP, GRD) function in their practice as an ad-hoc org chart, not as a shared semiotic pool.
The row we currently label "analogous" in the sign-classes-and-signification table then has a counter-observation attached to it, and the designer can open an advisory that names the row, cites the practice, and proposes moving the reading from "analogous" to "implicit" or even "gap."
The proposal does not need to settle the question; it needs to give us enough to re-examine the row with a specific case in mind.
If we agree, the amendment says so and credits the reporter; if we do not, the uncertainty section of `foundations.md` records the disagreement with a short note about what we would need to see to change our mind.

> Last reviewed: 2026-04-11. We revisit this file on every major framework release.
