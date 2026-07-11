This skill distills the SkillsBench paper (Li et al., 2026,
arXiv:2602.12670v3) into principles for designing skills on this
project. The paper benchmarks 86 tasks across 11 domains against
7 model-harness configurations under three conditions (no skills,
curated skills, self-generated skills), producing 7,308 trajectories.
The paper's findings are direct evidence for how to grow this
project's skill set — what to encode, what to leave out, and how
many skills to maintain.
The headline findings
Curated skills help substantially but with high variance.
Average +16.2 percentage points across configurations (range +13.6
to +23.3pp), 95% CIs typically ±2.5–3.1pp. Real effect, not noise.
But 16 of 84 tasks showed negative deltas — skills can hurt by
introducing conflicting guidance or unnecessary complexity for tasks
models already handle well.
Self-generated skills don't help. When models were prompted to
write their own procedural knowledge before solving tasks, average
effect was −1.3pp. Models cannot reliably author the procedural
knowledge they benefit from consuming.
2–3 skills are optimal, 4+ degrade. Tasks with 2–3 skills showed
+18.6pp gain; 4+ skills showed only +5.9pp. More skills don't
compound — they interfere.
Detailed and compact skills beat comprehensive. Compact
(+17.1pp) and detailed (+18.8pp) skills outperformed comprehensive
skills (−2.9pp, worse than no skills). Focused procedural guidance
beats exhaustive documentation.
What "human-curated" actually means
The self-generation finding is about a specific failure mode:
models asked to "write the skills you'd need before solving this
task" produce imprecise or incomplete skills that miss the
genuinely specialized knowledge required.
It does NOT mean models can't draft skill content. Skills drafted
by a model from validated human practice — operator-directed scope,
rules derived from real session evidence, patterns surfaced through
actual use — are human-curated with model assistance for drafting.
That's the same quadrant as a human writing the skill, not the
self-generation quadrant.
For this project: the operator directs what skills exist and when
they trigger. Rules come from real failures or repeated patterns.
Claude drafts the prose. The paper's negative result on
self-generation doesn't apply.
How many skills
The 2–3 optimum is per-task, not per-directory. What matters is
how many skills activate together for a typical conversation; many
skills can coexist if descriptions are tight enough that they don't
all trigger simultaneously.
Where skills help on this project
Software Engineering showed the smallest benefit (+4.5pp) of any
domain in the benchmark — strong pretraining coverage means less
upside from procedural guidance. Most of this project's work is SE,
so realistic expectations apply.
Skills are more likely to help where pretraining coverage is weak:

Beds24 API specifics (specialized vendor knowledge)
Project-specific architectural decisions (non-public)
aapanel and VPS-specific quirks (specialized infrastructure)
The styling contract bridge between plugin and themes

Citation
Li, X. et al. (2026). SkillsBench: Benchmarking How Well Agent
Skills Work Across Diverse Tasks. arXiv:2602.12670v3.

https://arxiv.org/html/2602.12670v4