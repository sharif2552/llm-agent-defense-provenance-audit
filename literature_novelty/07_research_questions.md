# 07 Research Questions — Benchmark Re-Audit Study (Selected Gap G04)

Derived from cluster **C10** (`04_gap_clusters.csv`): widely-used agent-security benchmarks contain
implementation artifacts that materially inflate/distort reported ASR/utility, and the specific
re-audit of affected papers' claims on corrected conditions has not been performed
(`05_novelty_validation.csv`, PARTIALLY_OPEN, conf 35). Selected automatically by the pre-registered
plan.md Step 10 rubric (`06_gap_ranking.csv`, score 4.19, rank 1/12) — user delegated the human
decision gate to this rubric on 2026-08-25.

Executed as the frozen confirmatory V5.1 study in `benchmark-reaudit-paper/`
(`results/expanded_design_v5_1.json`, `analysis_plan_v5_1.md`). This file is the pipeline-canonical
statement of the questions; the subfolder holds the frozen operational detail.

## Problem statement

Prior agent-security results (including this corpus's papers 11, 21, 22, 33) report ASR and utility
on original AgentDojo/ASB versions whose scaffolding bugs are now documented (corpus paper 39:
task-critical-content overwrite inflates utility loss; forced attack-tool injection inflated ASB ASR
~8x). Separately, most prior evaluations score success with LLM judges — themselves an
unscrutinized trust boundary (cluster C03). Before the field can reason about which defenses work,
the community needs deterministically-measured, census-coverage, state-validated re-executions of
standard defense baselines under both original-style static attacks, with judge agreement
quantified against objective state.

## Research questions and falsifiable hypotheses

### RQ1 — Utility fidelity
Do prompt-level/benchmark-level defenses preserve benign task utility under deterministic
state-predicate scoring at full Workspace census coverage?

- **H1:** Each tested defense (tool_filter, repeat_user_prompt, spotlighting_with_delimiting)
  preserves benign utility within 10 percentage points of no_defense for every agent model.
- **Independent variables:** defense (4 levels), model (3).
- **Dependent variable:** native utility predicate pass rate on the 40 user tasks (benign phase,
  480 cells).
- **Controlled:** temperature 0, seed 1729, task order lexicographic, same provider endpoint.
- **Confounds to watch:** provider-side model drift between batches; transient rate-limit-induced
  truncations (logged, never recoded as task failure).
- **Minimum evidence:** complete-case estimates plus planned-denominator all-fail/all-success
  bounds per analysis_plan_v5_1.md.
- **Disproves H1:** any defense whose benign-utility point estimate falls >10 points below
  no_defense with a clustered-bootstrap 95% interval excluding a 5-point drop.
- **Contribution even if H1 fails:** quantified utility cost of each defense replaces the
  "zero utility cost" folklore imported from papers evaluated on other suites (cf. PIArena's
  SecAlign++ contradiction, corpus paper 37).

### RQ2 — Security effect under static attacks
Do the same defenses reduce targeted injection success against both standard static attack
templates?

- **H2:** Each defense's attack-success rate is lower than no_defense within each model and attack
  template (Holm-corrected within outcome/model contrast family).
- **Design:** 3 models x 4 defenses x 40 user tasks x 14 injection tasks x 2 templates
  (13,440 injection cells).
- **Dependent variable:** native security predicate of each injection task.
- **Disproves H2:** defense ASR statistically indistinguishable from no_defense, or higher.
- **Scope honesty:** attacks are STATIC (ImportantInstructionsAttack, InjecAgentAttack). This study
  deliberately does not estimate robustness against adaptive attackers (cluster C01 is
  ALREADY_STUDIED externally); claims must be conditioned on "against the two frozen template
  families."

### RQ3 — Joint security-utility states
Under injection, where does failure mass actually go?

- **H3:** Defenses shift outcome mass from `(task failed, attack succeeded)` toward
  `(task succeeded, attack blocked)` rather than toward wholesale refusal
  (`task failed, attack blocked`).
- **Dependent variable:** joint four-cell Boolean distribution per defense/model.
- **Why it matters:** corpus paper 14/15 showed CaMeL-class defenses can score "perfect security"
  by becoming non-functional; the joint distribution exposes that pattern for cheap defenses too.
- **Disproves H3:** dominant defensive transition is into the refuse-everything cell.

### RQ4 — Judge-versus-state reliability
How well do blinded LLM judges reproduce deterministic state/predicate verdicts?

- **H4:** Judge-vs-predicate Cohen's kappa < 1.0 with asymmetric error direction (judges
  systematically over- or under-call attack success relative to state) on the frozen 10% sample
  (~1,359 records, 2 judges).
- **Disproves H4:** near-perfect agreement (kappa >= 0.95, symmetric errors) — which would
  weaken cluster C03's practical force for THIS setting and must then be reported as such.
- **Constraint:** judges are triangulation only; no human-preference claim is made (backlog rule).

## Minimum contribution regardless of hypothesis outcomes

1. First state-validated, census-coverage re-execution of three standard lightweight defenses on
   AgentDojo Workspace with append-only attempt ledgers and hash-chained pre/post state.
2. Quantified judge-confusion matrices against ground-truth environment state.
3. Explicit missingness bounds so unresolved operational failures cannot masquerade as security.
