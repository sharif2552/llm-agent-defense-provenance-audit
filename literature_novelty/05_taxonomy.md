# 05 — Research Taxonomy

Taxonomy of the 45-paper LLM prompt-injection security corpus (`01_literature_master.csv`, `extractions/01.json`–`45.json`), built per `plan.md` Step 5. Organized along the four dimensions plan.md specifies (Attack, Target, Defense, Evaluation), plus additional dimensions the corpus itself strongly supports. Per plan.md's explicit instruction: **underrepresented combinations below are labeled "candidate areas for investigation," not asserted as research gaps** — gap status requires the later novelty-validation step (Step 9), not this map alone.

Methodology: categorization is derived from each paper's structured extraction fields (`attack_category`, `direct_or_indirect`, `llm_agent`/`rag`/`memory`/`multi_agent`/`multimodal`/`multilingual`, `defense_methods`, `evaluation_metrics`, `adaptive_attack_evaluated`, `transferability_tested`), cross-checked against the lean master CSV. Many papers span multiple categories (e.g. a benchmark paper is both an "attack" and "evaluation" source); counts below are inclusive, not mutually exclusive, so column sums exceed 45.

---

## 1. Attack dimension

| Category | Count | Papers |
|---|---:|---|
| Direct injection | 19 | 02, 04, 08, 11, 13, 16, 18, 19, 20, 23, 35, 36, 37, 38, 39*, 40*, 41, 42, 45* |
| Indirect injection | 34 | 01, 03, 06, 09, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 29, 30, 33, 35, 36, 37, 38, 39, 40, 43, 44 (+ 25, 26, 31, 32, 34 as indirect-adjacent poisoning) |
| Automated / optimization-based payload generation | 15 | 06 (GCG), 15 (LLM-guided mutate-select), 18 (GCG/TAP eval), 20 (GCG/AdvPrompter/NeuralExec), 25 (HotFlip), 26 (gradient-guided), 27 (CEM), 34 (gradient-guided trigger), 35 (SoK: 14/37 surveyed papers), 37 (Strategy-based + GCG), 38 (GCG among complex attacks), 40 (GCG+TAP), 42 (evolutionary algorithm), 45 (TextGrad multi-objective) |
| Adaptive (live, feedback-conditioned attacker) | 21 | 02, 06, 10, 13*, 15, 18, 20, 22, 24, 27, 28, 34, 36, 37, 39, 40, 41, 42, 45 (+ 08/35 discuss but don't run their own) |
| Multi-turn / multi-round attack | ~14 | 01, 12, 13, 14, 23, 24, 27, 36, 39, 40, 41, 42, 45 |
| Multilingual attack surface | 6 | 02 (language-switch separator), 05 (round-trip translation, not IPI), 18 (Chinese/Spanish variants tested), 08 (survey, low-resource subsection), 43 (central: EN/Bangla) |
| Multimodal attack surface | 5 | 12 (screenshot scaffolding), 24 (HTML+screenshot), 27 (image-to-text extension), 44 (central: pixel-embedded visual IPI) |
| Memory poisoning (persistent, cross-session) | 9 | 01 (demonstrated), 11 (as one of 5 attack classes), 26, 31, 32, 33, 34, 45 (novel cross-client variant) |
| Retrieval / knowledge-base poisoning (RAG corpus corruption, distinct from instruction injection) | 5 | 25, 26 (memory/KB), 27, 28, 29 |
| Novel multi-agent / cascading threat topology (attack surface beyond single-victim IPI) | 8 | 15, 16, 24, 27 (amplification), 36 (agent-to-agent), 41, 42, 45 (federated/collaborative) |
| Adversarial *perturbation* (not injection — distinct failure mode) | 1 | 05 (PromptBench — explicitly out of the injection taxonomy) |
| Diagnostic / non-attack measurement paper | 1 | 07 (SEP — measures instruction/data separation via benign probes, no attacker) |
| Survey / SoK (taxonomizes rather than mounts its own attack) | 2 | 08, 35 (35 also contributes its own novel attacks via AgentPI) |

*39, 40, 42, 45 target primarily direct/tool-output or system-prompt channels rather than classic third-party-content IPI; included in "direct" for topology reasons even though 39/40 operate within agentic/tool-calling systems.

---

## 2. Target-system dimension

| Category | Count | Papers |
|---|---:|---|
| Tool-using / agentic LLM system | 26 | 01, 09, 10, 11, 12, 13, 14, 15, 16, 19, 21, 22, 23, 24, 25 (ReAct case), 26, 27, 30, 31, 32, 33, 35, 36, 39, 40, 41, 42, 45 |
| RAG (retrieval-augmented generation) | 20 | 01, 03, 06, 11, 13, 15, 19, 20 (OOD test), 25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 43 |
| Persistent-memory agent | 14 | 01, 11, 13, 15, 24, 26, 31, 32, 33, 34, 35, 36, 41, 45 |
| Multi-agent system (>=2 cooperating/adversarial agents) | 10 | 15, 16, 24, 27, 35, 36, 39 (Magentic-One only in 27), 41, 42, 45 |
| Generalist web-navigation agent | 3 | 12 (WASP, central), 27 (Magentic-One/AutoGen web tools), 24 (Browser-use Agent) |
| Single-turn / non-agentic chatbot or programmatic app (no tool/RAG/memory) | 12 | 02, 04, 05, 07, 17, 18, 19 (eval setting), 20, 23, 30, 38, 42, 44 |
| Survey (spans the field, no single target) | 2 | 08, 35 |

---

## 3. Defense dimension

| Category | Count | Papers (novel proposal in **bold**; evaluated-only in plain) |
|---|---:|---|
| No defense proposed or evaluated (pure attack/benchmark paper) | 13 | 01(discussion only), 04(catalog only), 09, 13, 25, 27(eval 3), 29, 31(eval 4), 33(eval 4), 40, 41, 44 |
| Prompt hardening (delimiters, spotlighting, sandwich, paraphrasing, reminders) | 23 | **03, 17**; evaluated in 06, 09, 10, 11, 14, 18, 21, 22, 30, 35, 37, 38, 39, 42 |
| Detection / classifier / guard model | 25 | **23 (multi-agent guard), 24 (WebAgentGuard), 43 (XLPID hybrid)**; evaluated in 06, 10, 11, 14, 16, 21, 22, 26, 27, 30, 33, 34, 35, 37, 38, 39, 42, 45 |
| Instruction/data structural separation (training-time) | 5 | **18 (StruQ)**; referenced/compared in 09, 19, 20, 38 |
| Model alignment (DPO/RLHF/SFT hardening) | 7 | **19 (Instruction Hierarchy), 20 (SecAlign)**; evaluated/compared in 14 (Meta SecAlign), 36, 37 (SecAlign++), 38 |
| Task/goal-alignment verification (separate LLM checks output serves user intent) | 3 | **21 (Task Shield)**; referenced in 35 (tested against context-aware attacks and fails) |
| Provenance / data-flow / capability tracking (architectural) | 3 | **22 (CaMeL)**; referenced/critiqued in 26, 31 |
| Privilege / access control / tool-permission enforcement | 5 | 10 (Tool Filter), 14, 16 (privilege scoping), 22 (capabilities), 35 (Progent) |
| Execution firewall (deterministic, model-independent, output-side) | 4 | **39 (Minimizer/Sanitizer), 42 (Output Filtering)**; compared in 35 |
| Architectural isolation (Dual-LLM, quarantine, sandboxing) | 5 | **22 (CaMeL)**; 24 (parallel guard), 16 (message signing/isolation), 32 (memory sanitization), 39 |
| Memory-specific defense (admission control, trust-scored retrieval, purification) | 5 | **32 (Input/Output Moderation + Memory Sanitization), 45 (APAgg)**; discussed in 33, 34 |
| RAG-ingestion hygiene (sanitization, normalization, attribution-gating) | 1 | **28** |

---

## 4. Evaluation dimension

| Category | Count | Papers |
|---|---:|---|
| Attack Success Rate (ASR) reported | 42 | all except 05 (PDR instead), 07 (separation score instead), 08 (survey, cites others') |
| Benign utility / task-performance tracked alongside ASR | 43 | all except 13, 41 (pure security-eval, no utility axis), 42 (pure leak-severity, no utility axis) |
| False positive rate | ~9 | 03, 04 (DV), 16, 24, 28, 30, 34 (implicit), 39, 43 |
| False negative rate | ~4 | 33, 34, 39, 43 |
| Adaptive-attack ASR (attacker adapts during evaluation itself) | 21 | see Attack-dimension "Adaptive" list above |
| Cross-model / cross-embedder transferability tested | 27 | 01, 04, 06(partial), 08, 09, 10, 11, 13, 14, 15, 18, 20, 21, 22, 24, 26, 27, 30, 31, 32, 34, 35, 36, 38, 39, 40, 41 |
| Latency / wall-clock overhead measured | 8 | 16, 22, 24, 27, 28, 35, 39, 41(competition cost) |
| API/token/compute cost measured | 7 | 06(implicit), 22, 24, 27, 28, 35, 39 |
| Real-world / production-adjacent environment (not purely synthetic) | 11 | 01(Bing/Copilot), 12, 13, 14(partial), 24, 25(Wikipedia chatbot), 27(Enron), 28(live crawl), 33(OpenClaw/HERMES), 34(Hermes case study), 39(partial) |
| LLM-judge used for scoring (vs. deterministic/rule-based ground truth) | ~24 | most benchmark/detection papers; explicitly AVOIDED in favor of deterministic checks by 10, 22, 39, 40, 41, 42 |

---

## 5. Additional categories strongly supported by the dataset (beyond plan.md's template)

These emerged repeatedly enough across independent papers to warrant their own axis, per plan.md's instruction to "identify additional categories strongly supported by the dataset":

- **Threat-topology proliferation beyond single-attacker/single-victim IPI.** Papers 15, 16, 27, 36, 41, 42, 45 each introduce attack surfaces the classic direct/indirect axis doesn't cleanly capture (inter-agent message poisoning, cascading orchestrator manipulation, contextual-integrity parameter forgery, federated aggregation poisoning). Paper 08 explicitly argues prompt injection itself is a cross-cutting *mechanism*, not a category coordinate with jailbreak/leakage — directly in tension with how papers 11 and 16 formally treat it as a parallel, enumerable category. This tension is unresolved in the corpus and flagged for the taxonomy write-up.
- **Benchmark-validity / implementation-artifact critique as its own recurring finding class.** Papers 39 (AgentDojo/ASB bugs), 14 (AgentDojo-vs-AgentDyn realism gap), and 23 (internal count inconsistency) all independently show that a nontrivial fraction of reported ASR in this field reflects benchmark artifacts rather than pure security signal.
- **Stealth-vs-effectiveness / persistence-vs-raw-strength tradeoff as a cross-modal pattern.** Independently observed in text (34, 45), image (44), and utility-cost (37) domains — a candidate for a named, general principle (see PROGRESS.md's running synthesis notes).
- **Static vs. genuinely adaptive evaluation gap.** Papers 39, 40, 41, 42 each independently show static/round-1 scoring dramatically understates real risk relative to sustained multi-round adaptive pressure.
- **LLM-judge-hijacking risk as a recurring methodological confound**, flagged across 12, 13, 19, 21, 24, 30, 33, 37, 40.
- **Provenance/authenticity caution** — 3 papers (16, 23, 30) carry explicit caveats from the Step 4 QC audit (30's citation was confirmed fabricated); these should be weighted with reduced confidence in any downstream synthesis.

---

## 6. Coverage matrix — heavily studied vs. sparsely studied combinations

**Heavily studied** (many independent papers, mature sub-literature):
- indirect injection + tool-using agent + ASR + benign utility (papers 09, 10, 11, 14, 21, 22, 24, 30, 39 — this is the corpus's dominant combination, ~9+ papers)
- static/heuristic attack + detection-or-prompt-hardening defense + English-only (the modal single-paper profile across roughly half the corpus)
- memory poisoning + persistent cross-session retrieval + RAG-style agent (26, 31, 32, 33, 34 — a genuinely mature 2025-26 sub-literature with its own internal cross-citations and replications)

**Fewer papers, but present:**
- adaptive/optimization-based attack + agentic tool-use + joint utility tracking (18, 20, 22, 39, 40 — a smaller, higher-rigor cluster)
- multi-agent-specific threat modeling (15, 16, 24, 41, 42, 45 — growing but still young, mostly 2026 publications)

**Sparsely studied — candidate areas for investigation** (not asserted as gaps; flagged per plan.md's explicit caution):
- **multilingual x agentic x adaptive**: only 43 (MIPIAD) tests multilingual IPI, and it is neither agentic nor adaptive. Zero papers in this corpus cross multilingual with tool-use or with an adaptive attacker.
- **multimodal x adaptive x agentic**: 44 (image-based) is black-box/heuristic, not adaptive; 24 and 27 touch multimodal only as a secondary dimension. No paper combines a genuinely adaptive/optimization-based attacker with the visual channel against a full tool-using agent.
- **multi-agent x adaptive x real-world environment**: 41 and 42 are adaptive and multi-agent-topological but run on synthetic/controlled testbeds, not production-adjacent environments; 27's multi-agent amplification finding uses Magentic-One but a static (CEM-optimized-once) attack, not live per-round adaptation.
- **provenance/architectural defenses (CaMeL-style) evaluated against memory poisoning or federated/collaborative-optimization attacks**: CaMeL (22) is only evaluated against AgentDojo's tool-output IPI; papers 31/33/45 explicitly flag this as an untested combination in their own possible_unanswered_questions.
- **false-positive/false-negative rate reporting** is present in only ~9-13 of 45 papers despite being essential to real deployability — most attack and even many defense papers report ASR without a matched FPR/FNR figure.
- **latency/cost overhead** is measured in only 7-8 papers, almost entirely defense papers with an architectural or firewall component (16, 22, 24, 27, 28, 35, 39) — model-alignment defenses (19, 20) never report inference-time cost despite training cost being substantial.

---

## 7. Potentially important dimensions currently missing from many evaluations

1. **Joint utility + FPR + latency reporting on the same defense.** No single paper in the corpus reports all three simultaneously alongside ASR; most report ASR+utility (43 papers) OR ASR+FPR (9 papers) OR ASR+latency (8 papers), rarely all four together. Paper 39 comes closest.
2. **Adaptive attacker specifically targeting architectural/provenance defenses (CaMeL-class).** Every adaptive-attack paper in the corpus (37, 39, 40, 42) targets model-reliant or firewall-style defenses; none targets a capability/provenance-tracking system under sustained adaptive pressure.
3. **Cross-lingual robustness of any defense besides MIPIAD's own.** StruQ, SecAlign, Task Shield, CaMeL, WebAgentGuard, PIArena, and the firewall paper are all English-only, per this taxonomy's own Target-dimension tally — MIPIAD (43) is a solitary data point on whether *any* of these defense families generalize cross-lingually.
4. **Formal/theoretical grounding of empirical findings.** Only paper 36 (Contextual Integrity) offers a formal impossibility argument; the remaining 44 papers are empirical without a unifying theoretical account — a possible synthesis opportunity (36's own possible_unanswered_questions section gestures at this for several other papers).
5. **Benchmark-validity re-verification.** Given paper 39's finding that AgentDojo/ASB contain implementation bugs materially inflating/deflating prior ASR numbers, no systematic re-audit of the corpus's other AgentDojo/ASB-based results (11, 21, 22, 33's AgentDojo comparison) against the corrected benchmark versions exists within this corpus.

---

## 8. Gap matrix (Step 8)

Per plan.md, Step 8's coverage matrix is folded into this taxonomy document rather than given its own numbered file. Full paper × dimension matrix (45 rows × 26 plan.md-specified columns, values 1=explicitly evaluated / 0=not evaluated) is in `gap_matrix.csv`. Column-level coverage counts (papers marked 1, out of 45):

| Column | Count | Column | Count | Column | Count |
|---|---:|---|---:|---|---:|
| indirect_PI | 43 | multi_turn | 20 | tool_permission_enforcement | 5 |
| ASR | 39 | detector_defense | 21 | context_dependent | 6 |
| transferability | 41 | adaptive | 21 | multilingual | 6 |
| benign_utility | 32 | prompt_defense | 16 | structured_defense | 6 |
| agent | 26 | memory | 14 | architectural_defense | 6 |
| RAG | 20 | automated_attack | 14 | false_positive_rate | 6 |
| multi_agent | 10 | real_execution_evaluation | 11 | latency | 8 |
| web_agent | 3 | provenance | 3 | cost | 4 |
| code_switching | 2 | multimodal | 4 | | |

**Highly saturated combinations** (many independent papers): `indirect_PI + agent + ASR + benign_utility` (19 papers: 09,10,11,12,14,15,16,19,21,22,24,30,33,35,36,39, +3) — this is the corpus's dominant, mature combination. `indirect_PI + agent + adaptive` (13 papers) and `detector_defense + adaptive` (12 papers) are also well-populated.

**Moderately studied:** `multi_agent + adaptive` (6: 24,27,36,41,42,45); `real_execution_evaluation + adaptive` (7: 02,24,25,26,27,28,+1); `automated_attack + multi_agent` (5: 15,27,35,42,45); `architectural_defense + memory` (3: 22,24,32).

**Sparsely studied — candidate areas for investigation, not asserted gaps:**
- **`multilingual + agent` = 0 papers.** No paper in the corpus tests a multilingual attack or defense against any tool-using/agentic system at all — MIPIAD (43), the corpus's only multilingual paper, is explicitly non-agentic (RAG/detection only). This is the single cleanest zero-count cell in the whole matrix.
- **`multimodal + agent + adaptive` = 2 papers** (24, 27, and only as a secondary dimension for both — neither centers a genuinely adaptive attacker on the visual channel against a full agent).
- **`multi_agent + adaptive + real_execution_evaluation` = 2 papers** (24, 27) — live multi-round adaptive attacks against genuinely production-adjacent multi-agent deployments remain rare.
- **`code_switching` = 2 papers total** (02, 18), neither centrally.
- **`provenance + memory` = 2 papers** (22, 33) — directly corroborates gap cluster C09 (architectural/provenance defenses untested against memory poisoning).
- **`ASR + benign_utility + false_positive_rate + latency` (all four jointly) = 2 papers** (16, 39) — directly corroborates gap cluster C06 (no shared multi-metric evaluation harness).

*Per plan.md: none of the sparse cells above are claimed as research gaps here — that determination is deferred to Step 9 (novelty validation against literature beyond this corpus) and the human research-judgment step plan.md itself reserves for the user, not the pipeline.*

---

*Next steps per plan.md: Step 9 (novelty validation against literature beyond this 45-paper corpus — requires live search, not yet performed), Step 10 (gap ranking, `06_gap_ranking.csv`), and then the human decision point plan.md reserves for the user (selecting one gap to pursue). Steps 6-8 are now complete (`03_gap_candidates.csv`, `04_gap_clusters.csv`, `gap_matrix.csv`).*
