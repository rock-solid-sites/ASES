# Source map and version routing

This skill was synthesized from the user-supplied sources and checked against current official Alloy 6 pages on 2026-08-02. Re-verify release-sensitive details when a user asks for the latest version.

## Primary Alloy 6 authorities

- [Alloy 6 changes and compatibility](https://alloytools.org/alloy6.html): native mutability, prime, lasso traces, temporal bounds/operators, complete temporal checking, and pre-6 compatibility.
- [Alloy 6 language reference](https://alloytools.org/spec.html): canonical syntax and semantics.
- [Official download page](https://alloytools.org/download.html): current distribution routing.
- [Alloy 6.2.0 release](https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0): version-pinned distribution and CLI/LSP release notes. The official site listed 6.2.0 as latest when this skill was built.
- [Version-pinned parser grammar](https://github.com/AlloyTools/org.alloytools.alloy/blob/v6.2.0/org.alloytools.alloy.core/parser/Alloy.cup) and [lexer](https://github.com/AlloyTools/org.alloytools.alloy/blob/v6.2.0/org.alloytools.alloy.core/parser/Alloy.lex): exact 6.2.0 implementation syntax.
- [Version-pinned Markdown extractor](https://github.com/AlloyTools/org.alloytools.alloy/blob/v6.2.0/org.alloytools.alloy.core/src/main/java/edu/mit/csail/sdg/parser/MarkdownHandler.java): exact frontmatter and fenced-block handling for literate Alloy files.

The user-supplied [documentation page](https://alloytools.org/documentation.html) is a directory, not the best current-version authority: it still links directly to 6.0.0 and routes to some Alloy 4 or explicitly outdated material. Use it to find the reference, API docs, FAQ, grammar, and examples; verify versions at the official download/release pages.

## Practical Alloy

- [Practical Alloy](https://practicalalloy.github.io/): current hands-on Alloy 6 guide.
- [Structural modeling](https://practicalalloy.github.io/chapters/structural-modeling/)
- [Relational logic primer](https://practicalalloy.github.io/chapters/structural-topics/topics/relational-logic/)
- [Commands and scopes](https://practicalalloy.github.io/chapters/structural-topics/topics/commands/)
- [Model finding](https://practicalalloy.github.io/chapters/structural-topics/topics/model-finding/)
- [Behavioral modeling](https://practicalalloy.github.io/chapters/behavioral-modeling/)
- [Temporal logic](https://practicalalloy.github.io/chapters/behavioral-topics/topics/temporal-logic/)
- [Trace scenarios](https://practicalalloy.github.io/chapters/behavioral-topics/topics/scenarios/)
- [Safety, liveness, and fairness](https://practicalalloy.github.io/chapters/behavioral-topics/topics/fairness/)
- [Inductive invariants](https://practicalalloy.github.io/chapters/behavioral-topics/topics/inductive-invariants/)

Use Practical Alloy as the pedagogical and idiomatic spine. Use the official language reference when exact semantics or grammar matters.

## Legacy tutorial material

- [Day-course landing page](https://alloytools.org/tutorials/day-course/)
- [Session 1: logic](https://alloytools.org/tutorials/day-course/s1_logic.pdf)
- [Session 2: language and analysis](https://alloytools.org/tutorials/day-course/s2_language.pdf)
- [Session 3: static modeling](https://alloytools.org/tutorials/day-course/s3_static.pdf)
- [Session 4: dynamic modeling](https://alloytools.org/tutorials/day-course/s4_dynamic.pdf)

All four decks identify themselves as Alloy Analyzer 4. Keep their relational progression—classify, relate, constrain, run, inspect, refine, check—but modernize dynamic modeling to native Alloy 6.

## Web-attack model

- [Rendered simple web-attack model](https://alloytools.org/models/simple-webattack.html)
- [Markdown source](https://github.com/AlloyTools/alloytools.github.io/blob/master/_models/simple-webattack.md)
- [2018 creation commit](https://github.com/AlloyTools/alloytools.github.io/commit/d5951b395bf28ca6984ef0f50e7e356bcbbc7bf7)

The model predates Alloy 6. Use it as a security-assumption and counterexample case study, not as copy-ready Alloy 6 code.

## Community skill comparison

- [Paul deGrandis's `alloy` skill](https://github.com/ohpauleez/devbox/blob/main/.opencode/skills/alloy/SKILL.md)
- [Paul deGrandis's `alloy-more` skill](https://github.com/ohpauleez/devbox/blob/main/.opencode/skills/alloy-more/SKILL.md)

These MIT-licensed community skills prompted the independently rewritten sections on `disj`, message representation, exact trace tails, event depiction, literate Markdown, and cross-state pitfalls. Their examples and strong semantic claims were not copied blindly; adopted patterns were checked against Alloy 6.2.0 and the primary sources above.
