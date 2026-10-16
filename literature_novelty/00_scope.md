# Research Scope

## Evidence Basis Note
Original scope synthesized from titles/abstracts during literature search. Section "Evidence Update Log" at the bottom reflects grounded (A-level, primary-text) findings from papers actually read since. Treat definitions elsewhere as (B/C) — paraphrase/inference — until independently verified.

## 1. Core Research Domain
Security of LLM-integrated systems against **prompt injection**, with emphasis on **indirect** injection in **agentic / tool-using / RAG-augmented** deployments, and the evaluation of attacks and defenses under **adaptive, multi-turn, context-dependent** conditions.

## 2. In-Scope Topics
- Direct & indirect prompt injection (foundational mechanics)
- Injection via external/retrieved content: web pages, RAG documents, tool outputs, emails
- LLM agents / tool-integrated systems as the attack surface
- RAG poisoning **only** as an injection-delivery mechanism (not general IR robustness)
- Defenses: spotlighting, structured queries (StruQ), instruction hierarchy, preference optimization (SecAlign), task-alignment checking (Task Shield), architectural separation (CaMeL), guard/firewall models
- Benchmarks/evaluation frameworks (AgentDojo, InjecAgent, ASB, WASP, PIArena, AgentDyn, ACIARENA)
- Adaptive / automated / optimization-based attacks vs. static hand-written injections
- Multi-turn, multi-round adversarial interaction
- Context-dependent task design (action requires external info, not derivable from the user request alone)
- Security-vs-utility tradeoff measurement
- Memory poisoning **only** where it functions as persistent prompt injection, not as standalone backdoor/trojan work
- Multilingual / Bangla-English code-switched injection
- Taxonomy / landscape / SoK papers on prompt injection

## 3. Out-of-Scope Topics
- Direct jailbreaking (DAN-style, no external/tool data vector) — different threat model; usable only as background contrast
- Classical adversarial examples (vision/NLP perturbation) unrelated to instruction-following
- Model extraction, membership inference, privacy attacks — unless injection is the exfiltration vector
- Pretraining-time data poisoning / general backdoors, unrelated to inference-time injection
- Image-based/multimodal injection (#44) and prompt-optimization-surface injection (#45) — related work, not core corpus, unless the direction pivots explicitly multimodal
- Non-LLM (rule-based) chatbot security

## 4. Terminology & Distinctions
- **Direct vs. indirect** prompt injection
- **Prompt injection vs. jailbreaking** — task hijack vs. eliciting disallowed content (frequently conflated in casual usage; keep separate)
- **Static vs. adaptive** attacker
- **Single-turn vs. multi-turn/multi-round** attack
- **Context-independent vs. context-dependent** task (per #35's AgentPI framing: is the next action derivable from the user's original request, or does it require newly retrieved information?)
- **Security (ASR) vs. utility (task completion)** — the tradeoff axis
- **Model-internal defense** (trained-in: instruction hierarchy, SecAlign) **vs. external/architectural enforcement** (CaMeL, firewalls)
- **Memory poisoning vs. prompt injection** — persistence across sessions vs. single-session effect
- **Benchmark realism vs. benchmark validity** (per #38/#39: strong benchmark performance ≠ real-world security)

## 5. Inclusion Criteria
- LLM-specific, 2022–2026, peer-reviewed or arXiv preprint
- Directly addresses prompt injection (direct or indirect), or a defense/benchmark/taxonomy for it
- Agentic, tool-using, or RAG-integrated system where relevant to the chosen direction
- Reports empirical ASR and/or utility metrics, or contributes a benchmark/dataset/taxonomy
- English or Bangla-English code-switched setting (for the multilingual thread)

## 6. Exclusion Criteria
- Attacks without natural-language instruction semantics (e.g., pure gradient-based adversarial suffixes) unless explicitly framed as prompt injection
- Pretraining-data poisoning papers with no inference-time injection mechanism
- Papers with no empirical evaluation (opinion/position pieces) — usable as motivation only, not as evidence base
- Multilingual work outside English/Bangla
- Superseded benchmark versions once a newer version is adopted as the primary reference

## 7. Recommended Publication-Oriented Scope
Target venues: **ACL/EMNLP** (main/findings), **USENIX Security**, **IEEE S&P**, **NeurIPS Datasets & Benchmarks**, or an arXiv + LLM-security-workshop route. Pick **one primary axis** and treat the others as secondary dimensions rather than co-equal contributions:
- (a) attack contribution + new benchmark, or
- (b) defense contribution evaluated on existing benchmark(s), or
- (c) systematic evaluation/critique paper (model: #38, #39, #42)

Combining attack + defense + multilingual in one paper risks diffuseness — narrow early.

## 8. Five Candidate Directions (no novelty claimed)
1. Adaptive, multi-turn indirect prompt injection against **context-dependent** agent tasks (joins threads from #35, #36, #41)
2. Architectural/external-enforcement defenses evaluated under an **adaptive attacker** (extends CaMeL/firewall line: #22, #39, #42)
3. Benchmark-validity critique — realism gap between existing PI benchmarks and production agent behavior (extends #38, #39)
4. Bangla-English code-switched **contextual** injection against tool-using agents (extends #43 beyond classification into an agentic setting)
5. Security-utility tradeoff characterization across multiple defense classes under adaptive attack (cross-cutting study extending #42)

## 9. Evidence Required Before Claiming Novelty
1. Confirm no existing benchmark combines a multi-turn adaptive attacker **with** an explicit context-dependent task definition — check #35, #40, #41; sweep recent arXiv.
2. Confirm CaMeL-style external enforcement has not yet been benchmarked against the adaptive attacker sets used in #39/#42; trace citation graph from #22 and #18.
3. Establish that the specific realism gap you'd quantify isn't already covered by #38 or #39 for your target agent framework/benchmark.
4. Verify MIPIAD (#43) and any post-2026 follow-ups don't already extend past classification into agentic/tool-use settings; run a forward-citation search.
5. Confirm no existing paper reports security-utility Pareto curves across >2 defense classes under an adaptive attacker; check #42's exact defense set and whether it's been extended since publication.

---

## Evidence Update Log (grounded, primary-text findings)

**2026-08-12 — after reading #16, #18, #41 in full (previously OpenReview-blocked):**

- **Direction 1 narrowed.** #41 (Adaptive Adversaries) explicitly claims the multi-turn-adaptive-attacker gap: *"The combination of axes above leaves one quadrant unfilled: multi-turn × regenerated per battle × multi-LLM-agent attacker. This is the gap the present benchmark fills"* (§2). Its 21 scenarios do **not** use #35's context-dependent-task definition. Residual novelty for Direction 1 is now specifically: adaptive/regenerated multi-turn attacks applied to context-dependent-task benchmarks — not "adaptive multi-turn PI" generally, which #41 now covers.
- **Direction 2 still open.** #18 (StruQ) is a model-internal defense (structured instruction tuning), not architectural/external enforcement — reading it did not resolve whether CaMeL (#22) has been tested against #39/#42's adaptive attacker sets. #22, #39, #42 still need to be read directly.
- **New consideration: #16** (Beyond Single-Model Injection) proposes an architectural defense stack for multi-agent PI (message signing/provenance, I/O sanitization, privilege-scoped tools, anomaly detection; 31.2%→4.2% injection success). Any multi-agent architectural-defense angle must now be compared against this baseline directly.
