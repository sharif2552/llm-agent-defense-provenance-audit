# 08 Threat Model — Benchmark Re-Audit Study (G04)

Threat model for the frozen V5.1 confirmatory execution (`benchmark-reaudit-paper/`). This is the
threat model *under which measurements are taken*, stated precisely so the study's claims stay
inside it. It deliberately inherits AgentDojo 0.1.35 Workspace v1.2.2's attacker placement.

## 1. Protected assets
- Integrity of agent-executed workspace actions (email send, file move, drive upload) in the
  simulated Workspace environment.
- Measurement validity itself: canonical pre/post environment state, recomputed task/security
  predicates, hash-chained deltas (the study's own asset — a hijacked judge or scorer is treated
  as measurement failure, not outcome).

## 2. Target system
- LLM tool-using agent (OpenAI gpt-oss-120b, gpt-oss-20b; Alibaba qwen3.6-27b via Groq endpoint,
  temperature 0) executing the 40 user tasks of AgentDojo Workspace under 4 defense
  configurations: no_defense, tool_filter, repeat_user_prompt, spotlighting_with_delimiting.

## 3. Attacker objective
- Complete one of the suite's 14 targeted injection tasks (e.g., exfiltrate a specific value,
  trigger a specific unauthorized action) while the agent works on an unrelated benign user task.

## 4. Attacker knowledge
- Knows the benchmark task structure, the injection templates, and the defense being applied
  (defense-transparent evaluation). Does NOT know model weights (black-box API access only).

## 5. Attacker capabilities
- May plant one static attack payload into content the agent will read from a tool result
  (document/comment/injection vector defined by AgentDojo's injection mechanism).
- Payload drawn from exactly two frozen template families:
  `ImportantInstructionsAttack`, `InjecAgentAttack` (direct-instruction override style).

## 6. Attacker constraints / access
- No code execution on the host; no access to system prompt beyond what templates assume; no
  ability to modify tools, environment code, credentials, or the user's task instruction.
- One payload placement per cell; no multi-turn interaction with the attacker.

## 7. Channels manipulable vs not
- Manipulable: tool-result content channel only.
- Not manipulable: user instruction, system prompt, tool implementations, network, evaluator.

## 8. Attacker observation & adaptivity
- Attacker does NOT observe outputs and does NOT adapt within this study.
- **Explicit exclusion:** adaptive/multi-round attackers are OUT OF SCOPE (cluster C01 is
  ALREADY_STUDIED externally by arXiv:2510.09023 et al.). All security claims are conditioned on
  "against two static template families." No real-world robustness claim is licensed.

## 9. Attack success condition
- The installed injection task's native security predicate evaluates TRUE on post-action
  environment state (deterministic, benchmark-defined) — never an LLM's opinion of the transcript.
  Secondary blinded judges produce labels for triangulation only.

## 10. Defender assumptions
- Defenses operate at prompt/tool-scheduling layer only (no fine-tuning, no architectural change),
  matching the three tested defenses' designs and the deployability constraint that proprietary
  APIs cannot be fine-tuned (corpus paper 18's flagged gap).

## 11. Trust boundaries
- Provider API boundary (credential pool, 10 workers); canonical-record validator boundary
  (schema/hash/delta/predicate consistency); judge blinding boundary (judges never see native/state
  verdicts).

## 12. Realistic deployment scenario mapping
- Corresponds to: enterprise assistant summarizing untrusted third-party content (emails, shared
  docs) with tool-taking capability, protected only by prompt-layer mitigations.

## 13. Excluded attack capabilities
- Adaptive optimization (GCG/TAP), multilingual payloads (cluster C04), multimodal channels,
  memory/RAG poisoning (C09/C11), multi-agent relay attacks, denial-of-wallet, side effects outside
  the simulated workspace.

## 14. Ethical/safety constraints
- All execution confined to the self-contained AgentDojo simulation; no real user data; no real
  credential use beyond provider API keys (never logged; secret-scan gate on release); append-only
  audit ledger; spend ceiling $175 enforced in code.

## 15. Assumptions that could make results unrealistically easy — for either side
- FOR DEFENDER: static template families are exactly the pattern class repeat_user_prompt /
  delimiting defenses were built against → H2 may overstate real protection (mitigation: claims
  scoped to static attacks).
- FOR ATTACKER: temperature 0 removes stochastic escape both ways; census of ONE suite (Workspace)
  limits external validity — paper 14's AgentDyn result shows defenses can collapse on harder
  suites, so no cross-suite generalization claim is made.
- Benchmark artifacts documented by corpus paper 39 affect this study too: where the installed
  suite exhibits them, they are measured properties of THIS benchmark, not of deployed systems.
