# TEMPLATE — METACOMMUNICATION AS-IS

<!-- maintained-by: agent (post-skill) -->

> **How to use this template:** Copy this file to `project/metacomm-as-is.md` and document the metacommunication messages your system **currently implements**. This file is updated automatically by post-skill after plan execution.
>
> For the definition of metacommunication message, see `general/shared-definitions.md`.

---

## 1. Global Metacommunication Summary

> Summarize the current designer-to-user message as actually implemented in the system. **Phrasing: use "I" as the designer and "you" as the user — never third-person or passive voice (see `general/shared-definitions.md` § Phrasing rule).** Use the semiotic engineering frame: "Here is my understanding of who you are, what I've learned you want or need to do, in which preferred ways, and why. This is the system that I have therefore designed for you, and this is the way you can or should use it in order to fulfill a range of purposes that fall within this vision."

{{GLOBAL_METACOMM_SUMMARY}}

---

## 2. Extended Metacommunication Template Guiding Questions

1. Analysis (understanding needs and defining requirements)
   1.1. What do I know or don’t know about (all of) you and how?
   {{EMT_ANALYSIS_WHAT_I_KNOW_OR_DONT_KNOW_ABOUT_YOU_AND_HOW}}
   1.2. What do I know or don’t know about affected others and how?
   {{EMT_ANALYSIS_WHAT_I_KNOW_OR_DONT_KNOW_ABOUT_AFFECTED_OTHERS_AND_HOW}}
   1.3. What do I know or don’t know about the intended (and other anticipated) contexts of use?
   {{EMT_ANALYSIS_WHAT_I_KNOW_OR_DONT_KNOW_ABOUT_THE_INTENDED_AND_OTHER_ANTICIPATED_CONTEXTS_OF_USE}}
   1.4. *What ethical questions can be raised by what I have learned? Why?
   {{EMT_ANALYSIS_WHAT_ETHICAL_QUESTIONS_CAN_BE_RAISED_BY_WHAT_I_HAVE_LEARNED}}
2. Design
   2.1. What have I designed for you?
   {{EMT_DESIGN_WHAT_HAVE_I_DESIGNED_FOR_YOU}}
   2.2. Which of your goals have I designed the system to support?
   {{EMT_DESIGN_WHICH_OF_YOUR_GOALS_HAVE_I_DESIGNED_THE_SYSTEM_TO_SUPPORT}}
   2.3. In what situations/contexts do I intend/accept you will use the system to achieve each goal? Why?
   {{EMT_DESIGN_IN_WHAT_SITUATIONS_CONTEXTS_DO_I_INTEND_ACCEPT_YOU_WILL_USE_THE_SYSTEM_TO_ACHIEVE_EACH_GOAL}}
   2.4. How should you use the system to achieve each goal, according to my design?
   {{EMT_DESIGN_HOW_SHOULD_YOU_USE_THE_SYSTEM_TO_ACHIEVE_EACH_GOAL}}
   2.5. For what purposes do I not want you to use the system?
   {{EMT_DESIGN_FOR_WHAT_PURPOSES_DO_I_NOT_WANT_YOU_TO_USE_THE_SYSTEM}}
   2.6. *What ethical principles influenced my design decisions?
   {{EMT_DESIGN_WHAT_ETHICAL_PRINCIPLES_INFLUENCED_MY_DESIGN_DECISIONS}}
   2.7. *How is the system I designed for you aligned with those ethical considerations?
   {{EMT_DESIGN_HOW_IS_THE_SYSTEM_I_DESIGNED_FOR_YOU_ALIGNED_WITH_THOSE_ETHICAL_CONSIDERATIONS}}
3. Prototyping, implementation, and formative evaluation
   3.1. How have I built the system to support my design vision?
   {{EMT_PROTOTYPING_IMPLEMENTATION_AND_FORMATIVE_EVALUATION_HOW_HAVE_I_BUILT_THE_SYSTEM_TO_SUPPORT_MY_DESIGN_VISION}}
   3.2. What have I built into the system to prevent undesirable uses and consequences?
   {{EMT_PROTOTYPING_IMPLEMENTATION_AND_FORMATIVE_EVALUATION_WHAT_HAVE_I_BUILT_INTO_THE_SYSTEM_TO_PREVENT_UNDESIRABLE_USES_AND_CONSEQUENCES}}
   3.3. What have I built into the system to help identify and remedy unanticipated negative effects?
   {{EMT_PROTOTYPING_IMPLEMENTATION_AND_FORMATIVE_EVALUATION_WHAT_HAVE_I_BUILT_INTO_THE_SYSTEM_TO_HELP_IDENTIFY_AND_REMEDY_UNANTICIPATED_NEGATIVE_EFFECTS}}
   3.4. *What ethical scenarios have I used to evaluate the system?
   {{EMT_PROTOTYPING_IMPLEMENTATION_AND_FORMATIVE_EVALUATION_WHAT_ETHICAL_SCENARIOS_HAVE_I_USED_TO_EVALUATE_THE_SYSTEM}}
4. Continuous, post-deployment evaluation and monitoring
   4.1. How much of my vision is reflected in the system’s actual use?
   {{EMT_CONTINUOUS_POST_DEPLOYMENT_EVALUATION_AND_MONITORING_HOW_MUCH_OF_MY_VISION_IS_REFLECTED_IN_THE_SYSTEMS_ACTUAL_USE}}
   4.2. What unanticipated uses have been made? By whom? Why?
   {{EMT_CONTINUOUS_POST_DEPLOYMENT_EVALUATION_AND_MONITORING_WHAT_UNANTICIPATED_USES_HAVE_BEEN_MADE_BY_WHO_WHY}}
   4.3. What anticipated and unanticipated effects have resulted from its use? Whom do they affect? Why?
   {{EMT_CONTINUOUS_POST_DEPLOYMENT_EVALUATION_AND_MONITORING_WHAT_ANTICIPATED_AND_UNANTICIPATED_EFFECTS_HAVE_RESULVED_FROM_ITS_USE_WHO_DO_THEY_AFFECT_WHY}}
   4.4. *What ethical issues need to be handled through system redesign, redevelopment, policy, or even decommissioning?
   {{EMT_CONTINUOUS_POST_DEPLOYMENT_EVALUATION_AND_MONITORING_WHAT_ETHICAL_ISSUES_NEED_TO_BE_HANDLED_THROUGH_SYSTEM_REDESIGN_REVOLUTIONARY_POLICY_OR_EVEN_DECOMMISSIONING}}

## 3. Per-Feature Metacommunication Log

> For each feature or interaction flow, document the designer's intent as currently implemented. **Each intent must be phrased as "I ... for you / because you ..." — see `general/shared-definitions.md` § Phrasing rule.**

| Feature / Flow | Designer Intent | Implementation Status | Source | Last Updated |
|---|---|---|---|---|
| {{feature}} | {{intent}} | {{Implemented / Partial / Planned}} | {{human / agent (metacomm) / agent (post-skill)}} | {{YYYY-MM-DD}} |

---

## 4. Changelog

> Versioned entries tracking how the implemented metacommunication has evolved. Each entry is appended automatically by post-skill after plan execution.

### v1 — {{YYYY-MM-DD}}
- **Initial**: Baseline metacommunication record created
- **Source**: human (design)
