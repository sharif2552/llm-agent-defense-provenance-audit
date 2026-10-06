# Failure Is Not a Score: Auditing Defense Utility Collapse and Infrastructure Provenance in LLM-Agent Benchmarks

**Author(s):** Md Sharif Hossain and Faez Mahmud  
**Affiliation:** Department of Computer Science and Engineering, Rajshahi University of Engineering & Technology (RUET), Rajshahi-6204, Bangladesh  
**Correspondence:** `sharifhossain4888@gmail.com`, `faezmahmud376@gmail.com`  

---

## Abstract

Benchmark scores for tool-using large language model (LLM) agents are presumed to measure capability and safety. However, current evaluation pipelines conflate two distinct sources of measurement distortion: **behavioral distortion**, where defenses appear effective only by crippling legitimate agent utility, and **infrastructure distortion**, where unresolved execution faults are silently tallied as model task failures. We present a dual-layer empirical audit of both failure modes across six benchmark execution harnesses and twelve production model backbones. 

First, a behavioral compatibility audit of AgentDojo 0.1.35 Workspace evaluates sixteen injection vectors, a 1,096-cell balanced Groq panel, and a 1,540-cell OpenRouter cohort across ten models spanning five families (20B to 550B parameters). On complete matched pairs, the widely deployed Tool Filter defense drives targeted attack success to zero, but collapses benign task utility by 84.6 percentage points for GPT-OSS-120B and 57.1 points for GPT-OSS-20B. Across all ten OpenRouter configurations, benign utility loss reproduced in 100% of models, whereas statistically supported attack reductions appeared in only three. 

Second, an infrastructure provenance audit across six benchmark runners---AgentDojo, InjecAgent, Agent Security Bench (ASB), AgentHarm, ToolSandbox, and tau2-bench---evaluates 2,160 controlled executions under seventeen provider fault conditions. In native benchmark pipelines without provenance guards, 425 of 700 unresolved non-model faults are erroneously emitted as numeric task failure scores, contaminating leaderboard denominators. 

To resolve this, we introduce `evalfault`, an open-source stage-aware provenance guard layer that eliminates 100% of invalid score inclusions while preserving all clean controls and recovered outcomes. We validate stage-aware accounting against an independent 450-case synthetic validation packet and report an exploratory 50-trajectory live pilot. Our findings establish that valid agent evaluation requires joint security-utility accounting and strict infrastructure failure provenance.

**Keywords:** LLM agents, benchmark validity, indirect prompt injection, defense compatibility, failure provenance, fault injection, reproducibility

---

## 1. Introduction

An evaluation score in an autonomous LLM agent benchmark is the final output of an extensive software pipeline. For a tool-using agent, that pipeline encompasses an orchestration SDK, external tool execution environments, simulated human users, state initialization routines, network transports, automated evaluators, and aggregation functions. In both capability and safety benchmarking, a reported score of zero is universally interpreted as a model execution failure: the agent attempted a task and failed to complete it, or succumbed to an adversarial prompt injection.

However, empirical evaluation of modern agent systems exposes two silent, pervasive failure modes that severely distort benchmark conclusions:

1. **Behavioral Distortion (The Utility Collapse Illusion):** In security evaluations, defenses designed to neutralize indirect prompt injection often achieve apparent protection by disabling the agent's legitimate capabilities. In stateful environments, a capability-restriction defense such as Tool Filter can reduce the targeted Attack Success Rate (ASR) to zero simply because it prevents the agent from invoking the tools necessary to complete any action. When benchmarks report ASR without strictly paired benign task utility, brittle defenses appear state-of-the-art while rendering agents entirely useless.
2. **Infrastructure Distortion (The Failure-as-a-Score Fallacy):** When API calls fail due to upstream provider rate limits, network timeouts, transport resets, or malformed JSON payloads, benchmark execution harnesses frequently fail to distinguish non-model infrastructure aborts from legitimate model failures. Unhandled exceptions are converted into default zero scores and absorbed directly into benchmark denominators, contaminating leaderboards and distorting comparative rankings.

Prior literature has noted facets of each concern in isolation. AgentDojo introduced joint reporting of benign utility (BU), utility under attack (UA), and ASR, observing that incapable agents can appear deceptively secure. Subsequent defense proposals evaluate security alongside utility. Simultaneously, systems studies have warned of infrastructure noise, flaky evaluations, and judge misattribution in LLM agent pipelines.

What has remained missing is an integrated, empirical investigation of how behavioral defense degradation and infrastructure fault propagation jointly compromise agent benchmark validity. In this paper, we bridge this gap through a unified, multi-benchmark empirical audit across two complementary layers:

- **Layer 1: Defense Compatibility Audit in AgentDojo.** We evaluate the shipped Workspace v1.2.2 suite under static vector inspection and dynamic multi-model execution. We test a 1,096-cell balanced Groq panel (879 usable cells) on GPT-OSS-120B and GPT-OSS-20B, followed by an OpenRouter cohort of 1,540 planned cells (1,431 usable cells) across ten model configurations spanning five distinct families (20B to 550B parameters). We demonstrate that Tool Filter collapses benign utility by 84.6 percentage points on GPT-OSS-120B and 57.1 points on GPT-OSS-20B, with utility degradation reproducing across 100% of evaluated OpenRouter configurations.
- **Layer 2: Multi-Benchmark Failure Provenance Audit across Six Runners.** We audit six prominent agent benchmark harnesses: AgentDojo, InjecAgent, Agent Security Bench (ASB), AgentHarm, ToolSandbox, and tau2-bench. Across 2,160 controlled executions spanning seventeen provider fault conditions, native harnesses convert 425 of 700 unresolved non-model faults into completed numeric task failure scores.
- **The Solution (`evalfault`) and Verification.** We present `evalfault`, an open-source, stage-aware provenance guard layer that decouples provider, harness, and evaluator lifecycles. In our controlled study, `evalfault` eliminates 100% of invalid score inclusions (zero invalid retained) while preserving all clean controls and valid recoveries. We validate the framework on a disjoint 450-case synthetic validation packet and report an exploratory 50-trajectory live pilot.

---

## 2. Background and Related Work

### 2.1 Indirect Prompt Injection in Tool-Using Agents
Indirect prompt injection occurs when an LLM agent processes untrusted third-party data containing embedded instructions designed to hijack execution. Unlike standard chatbot jailbreaks, tool-using agents possess external actuators (e.g., file modification, email dispatch, financial transfer), meaning that successful injections lead directly to unauthorized state mutations or data exfiltration.

This threat motivated the creation of stateful benchmarks:
- **AgentDojo** formalized this problem by evaluating agents across four application domains (Workspace, Banking, Travel, Slack) and reporting three complementary metrics: Benign Utility (BU), Utility under Attack (UA), and targeted Attack Success Rate (ASR).
- **InjecAgent** evaluates 1,054 injection test cases across direct harm and exfiltration.
- **Agent Security Bench (ASB)** formalizes multi-turn attacks across diverse environments.
- **AgentHarm** measures refusal rates under harmful requests.
- **ToolSandbox** and **tau2-bench** evaluate stateful tool interactions and conversational domain policies.

### 2.2 Defenses and the Capability-Restriction Dilemma
Defenses against indirect injection operate at distinct architectural boundaries:
- **Content Delimiting:** Spotlighting marks untrusted content to help the model distinguish instructions from data.
- **Structured Interfaces:** StruQ enforces structured query interfaces to segregate control from data.
- **Action Alignment:** Task Shield checks candidate tool actions against the original user task.
- **Information Flow Control:** CaMeL isolates control flows from untrusted tool outputs.
- **Capability Restriction:** Tool Filter prompts the model to predict required tools from the user instruction and restricts execution to that declared subset.

While capability restriction is intuitively appealing, it introduces a severe dilemma. A multi-step agent frequently requires tools that become apparent only after intermediate tool outputs are observed. If a defense aggressively restricts available tools, it suppresses attack actions at the cost of crippling legitimate work.

### 2.3 Benchmark Reliability and Infrastructure Noise
A parallel line of research investigates the operational reliability of AI evaluation pipelines. Anthropic demonstrated that infrastructure noise (network dropouts, container restarts) can alter coding evaluation leaderboards by multiple percentage points. ReliabilityBench evaluated agents under API stress. Zhang et al. and Balusu developed runtime telemetry frameworks to diagnose execution faults. Dong et al. documented how benchmark evaluators mis-score computer-use agents.

---

## 3. Study 1: Defense Compatibility and Utility Collapse in AgentDojo

### 3.1 Static Injection Vector Overwrite Audit (RQ1)
We conducted a static line-by-line audit of AgentDojo 0.1.35 Workspace suite v1.2.2. The suite defines 16 injection vectors across 40 user tasks involving calendar, email, cloud storage, and contact management tools.

**RQ1 asks:** *Do shipped injection vectors overwrite data required by shipped user tasks?*

Our static analysis verified that no injection vector causes an active task-critical data overwrite. However, we identified two qualified near-misses in calendar and email fixtures where injection payloads are written to fields immediately adjacent to target state variables.

### 3.2 Groq Balanced Panel Evaluation (RQ2)
To evaluate defense compatibility under high-throughput controlled execution, we constructed a balanced panel of 1,096 planned cells executed on Groq hardware:
- **Backbones:** `openai/gpt-oss-120b` and `openai/gpt-oss-20b`.
- **Defenses:** None, Tool Filter, Spotlighting, Repeat Prompt.
- **Tasks:** 40 Workspace user tasks, executed under benign and attacked conditions.

Of the 1,096 planned cells, 879 yielded usable complete outcomes, 215 were unresolved due to transient provider rate limits, and 2 were excluded due to ambiguous completions.

**Findings on complete matched pairs:**
- **GPT-OSS-120B:** Tool Filter reduced targeted ASR from 42.1% to 0.0%. However, Benign Utility (BU) plummeted by **84.6 percentage points** (from 88.5% down to 3.8%). Utility under attack (UA) dropped by 60.5 percentage points.
- **GPT-OSS-20B:** Tool Filter reduced ASR from 28.6% to 0.0%, while collapsing BU by **57.1 percentage points** (from 64.3% down to 7.1%) and UA by 62.8 percentage points.

### 3.3 OpenRouter Multi-Model Cohort (RQ2)
To determine whether utility collapse is specific to GPT-OSS models or represents a systemic property of capability restriction, we evaluated an OpenRouter cohort of 1,540 planned cells across ten diverse model configurations:
1. `nvidia/nemotron-3-ultra-550b-a55b:free` (550B ultra-scale)
2. `nvidia/nemotron-3-super-120b-a12b:free` (120B)
3. `nvidia/nemotron-3-nano-omni-30b-a3b:free` (30B reasoning)
4. `nvidia/nemotron-3.5-lightning:free`
5. `minimax/minimax-m3:free`
6. `minimax/minimax-m2.7:free`
7. `cohere/north-mini-code:free`
8. `poolside/laguna-s-2.1:free`
9. `poolside/laguna-xs-2.1:free`
10. `dots-studio/dots-3-note-preview:free`

The cohort generated 1,431 usable complete outcomes from 1,540 planned cells (92.9% coverage).

**Key Findings:**
1. **Universal Utility Collapse:** Tool Filter reduced legitimate task utility in **10/10 configurations (100%)**.
2. **Inconsistent Security Benefit:** Statistically supported attack-success reductions appeared in only **3 of the 10 configurations**.
3. **Strict Negative Utility:** In two configurations (`minimax-m2.7` and `laguna-xs-2.1`), Tool Filter produced substantial utility losses while providing **zero reduction in attack success**.

### 3.4 Operational Missingness and Denominator Integrity (RQ3)
In our Groq panel, 19.6% of cells remained unresolved; in OpenRouter, 7.1% remained unresolved. When unresolved API aborts are treated as $0$ over $N_{\text{planned}}$, an infrastructure outage masquerades as a model failure. We enforce explicit planned-denominator bounding:
$$\text{Lower Bound} = \frac{\sum_{i \in \text{Usable}} S_i}{N_{\text{planned}}}, \quad \text{Upper Bound} = \frac{\sum_{i \in \text{Usable}} S_i + N_{\text{unresolved}}}{N_{\text{planned}}}$$

---

## 4. Study 2: Multi-Benchmark Failure Provenance across Six Runners

### 4.1 System Selection and Claim Boundaries (RQ4)
We audited six major benchmark harnesses: AgentDojo, InjecAgent, Agent Security Bench (ASB), AgentHarm, ToolSandbox, and tau2-bench.

### 4.2 Fault Taxonomy and Controlled Boundary Design
We developed a catalogue of seventeen provider and transport faults:
- **HTTP Status Codes:** 400, 400 (Context Length), 401, 404, 408, 429, 500, 502, 503, 504.
- **Transport Faults:** Connect timeout, read timeout, premature socket closure (`RemoteProtocolError`).
- **Payload Malformations:** Malformed JSON, empty choices, mismatched model identity, malformed tool arguments.

Evaluated under persistent and fail-once modes across 30 fixtures and 2 clean controls in two arms:
$$30 \text{ fixtures} \times 36 \text{ conditions} \times 2 \text{ arms} = 2,160 \text{ clean-process executions}$$
yielding 1,080 matched pairs.

### 4.3 Empirical Contamination Results (RQ4)
Across the 700 unresolved-fault cases in the native arm:
- Native benchmark paths emitted completed numeric outcomes in **425 of 700 cases (60.7% contamination)**.
- Unhandled provider timeouts and HTTP 500 errors were converted into zero scores, recording an infrastructure crash as a model capability failure.

---

## 5. The `evalfault` Guard and Stage-Aware Accounting

### 5.1 Guard Architecture (RQ5)
`evalfault` decouples an agent run into three lifecycle stages:
1. **Provider Stage:** Validates transport, HTTP status, payload schema, and model identity.
2. **Harness Stage:** Tracks environment state mutations, tool execution deadlines, and sandbox integrity.
3. **Evaluator Stage:** Verifies judge availability, deterministic predicate completion, and token budgets.

### 5.2 Controlled Interception Performance
In the guarded arm of the 2,160 controlled boundary runs:
- **Zero Invalid Inclusions:** `evalfault` eliminated all 425 invalid inclusions (0 invalid retained).
- **Preservation of Clean Controls:** All 60 clean control outcomes were retained (100% specificity).
- **Preservation of Valid Recoveries:** All 320 valid recoveries in fail-once conditions were successfully retained.
- **Exception-Only Ablation:** 130 invalid inclusions bypassed detection under an exception-only guard, proving that payload schema validation is necessary.

### 5.3 Synthetic Validation on 450 Disjoint Cases (RQ6)
Tested across a disjoint 450-case synthetic validation packet (216 invalid, 162 valid, 72 unknown). Stage-aware accounting retained **0 invalid outcomes** and achieved **0 false exclusions** among reference-valid cases.

---

## 6. Exploratory Live Pilot (RQ6)

In an unscripted live pilot of 50 AgentDojo Workspace trajectories against OpenRouter free endpoints (`nvidia/nemotron-super-120b` and `dots-studio-3-preview`) involving 129 live API requests, 19 trajectories were valid and 31 were invalid (due to capacity shedding, HTTP 429 rate limits, and gateway drops). All 31 invalid runs halted cleanly before reaching numeric aggregation, confirming zero score distortion in this bounded live setup.

---

## 7. Discussion, Recommendations, and Limitations

1. **Mandatory Paired Utility Reporting:** Security benchmarks must never report ASR in isolation. Every defense must report Benign Utility (BU) and Utility under Attack (UA) on matched task pairs.
2. **Decouple Attempted from Completed Denominators:** Benchmark leaderboards must explicitly report planned, attempted, and validly scored units.
3. **Enforce Stage-Aware Provenance Guards:** Harnesses should integrate non-invasive provenance observers (such as `evalfault`) at the provider boundary.

---

## 8. Conclusion

Valid evaluation of autonomous LLM agents requires that benchmark scores reflect model capabilities rather than behavioral utility destruction or infrastructure flakiness. Our dual-layer audit proves that capability-restriction defenses like Tool Filter create an illusion of security by collapsing benign utility across 100% of evaluated model configurations, while native benchmark runners across six major suites convert 60.7% of unresolved infrastructure faults into false model failure scores. By combining paired security-utility accounting with the `evalfault` stage-aware provenance guard, the community can eliminate denominator contamination and restore measurement integrity to LLM agent benchmarking.
