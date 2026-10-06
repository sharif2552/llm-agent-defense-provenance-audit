# Failure Is Not a Score: Auditing Defense Utility Collapse and Infrastructure Provenance in LLM-Agent Benchmarks

[![Audit Status](https://img.shields.io/badge/Audit-100%25%20Verified%20(Exit%200)-success.svg)](#reproducibility)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Format: IEEEtran](https://img.shields.io/badge/Format-IEEEtran%20Two--Column-blue.svg)](paper/)

Official replication package and empirical audit suite for the research paper:  
**"Failure Is Not a Score: Auditing Defense Utility Collapse and Infrastructure Provenance in LLM-Agent Benchmarks"**  
Submitted to *IEEE Transactions on Dependable and Secure Computing (TDSC)*.

**Authors**: Md Sharif Hossain and Faez Mahmud  
*Department of Computer Science & Engineering, Rajshahi University of Engineering & Technology (RUET), Bangladesh*

---

## 📌 Overview

This repository provides the complete, self-contained replication bundle, raw attempt-level event ledgers, and automated audit scripts for:
1. **Study 1: Ecosystem-Wide Prompt-Injection Defense Utility Collapse**:
   - Multi-model evaluation across **12 models** (Groq and OpenRouter cohorts) and 5 model families.
   - Empirical proof that semantic Tool Filtering achieves zero attack success only by catastrophically collapsing legitimate agent utility in **10 out of 10 models** ($\Delta = -43.8\%$ to $-100.0\%$, $p < 0.001$).
2. **Study 2: Benchmark Failure Provenance and Denominator Contamination**:
   - Clean-process execution across **6 leading agent benchmarks** (`AgentDojo`, `AgentHarm`, `ASB`, `InjecAgent`, `TAU-Bench 2`, and `ToolSandbox`).
   - Discovery that native evaluation harnesses silently misattribute infrastructure and network anomalies as model reasoning failures in **425 of 700 unresolved non-model faults (60.7%)**.
   - Introduction of **`evalfault`**, a formal fault-injection taxonomy and provenance-aware observer that intercepts 100% of invalid runs ($C_i^* = 0$) while retaining 100% of clean controls (60/60) and valid recoveries (320/320).

---

## 📂 Repository Structure

```text
.
├── README.md                      # Replication guide and overview
├── LICENSE                        # MIT Open Source License
├── CITATION.cff                   # Citation metadata
├── reproduce.sh                   # One-step reproduction runner
├── run_audit.py                   # Two-stage meta-testing and Level-0 recomputation engine
├── SHA256SUMS                     # Cryptographic digests of all data and code artifacts
├── paper/                         # Publication sources
│   ├── main.tex                   # IEEEtran root LaTeX document
│   ├── body.tex                   # Two-column manuscript body
│   ├── references.bib             # Bibliography (39 citations)
│   ├── IEEEtran.cls               # IEEE document class
│   ├── manuscript.md              # Master readable Markdown manuscript
│   └── figures/                   # High-resolution publication figures (Figures 1-7)
└── data/                          # Audited Level-0 event ledgers
    ├── study1_groq/               # Groq balanced panel (v5.1, 4,344 attempt rows)
    ├── study1_openrouter/         # OpenRouter multi-model cohort (v5.3, 4,689 attempt rows)
    ├── study2_controlled_v2/      # 6-benchmark controlled boundary study (2,160 clean runs)
    ├── study2_synthetic_v3/       # Synthetic challenge suite (450 cases)
    └── study2_live_v4/            # Exploratory live infrastructure pilot (50 trajectories)
```

---

## 🚀 Quickstart & One-Step Reproduction

The audit suite requires **Python 3.8+** with standard library only (no third-party pip dependencies required).

### Run Verification

Clone the repository and run the audit:

```bash
git clone https://github.com/sharif2552/llm-agent-defense-provenance-audit.git
cd llm-agent-defense-provenance-audit
python3 run_audit.py
```
*(Or execute `./reproduce.sh`)*

### What the Auditor Verifies

The audit script executes a strict two-stage process:
* **Stage 1 ("Test the Test")**:
  - Injects adversarial mutations into hash verification, chained ledger integrity, denominator contamination logic ($C_i = E_i \cdot (1 - V_i)$), and missingness boundary conditions.
  - Verifies that the test harness rejects all 6 mutations before evaluating research data.
* **Stage 2 ("Test the Research")**:
  - Recomputes all statistical findings directly from the raw `.jsonl` attempt records on disk across **4,970 executions**.
  - Verifies cryptographic hash chains ($h_i = \text{SHA256}(h_{i-1} \parallel r_i)$) across all 2,160 Study 2 runs.
  - Verifies that all empirical claims match the manuscript text verbatim.

---

## 📊 Summary of Verified Empirical Findings

| Empirical Finding | Scope / Dataset | Raw Recomputed Metric | Verification Status |
| :--- | :--- | :--- | :--- |
| **GPT-OSS-120B Benign Utility Collapse** | Groq Balanced Panel ($n=13$ pairs) | $12/13 \to 1/13$ ($\mathbf{\Delta = -84.6\%}$) | **VERIFIED EXACT** |
| **GPT-OSS-20B Benign Utility Collapse** | Groq Balanced Panel ($n=14$ pairs) | $10/14 \to 2/14$ ($\mathbf{\Delta = -57.1\%}$) | **VERIFIED EXACT** |
| **Multi-Model Utility Breakdown** | OpenRouter Cohort (10 models, 5 families) | **10 / 10 models** ($\mathbf{100\%}$ collapse) | **VERIFIED EXACT** |
| **Native Denominator Contamination** | 6 Benchmarks, 2,160 runs ($n=700$ faults) | **425 / 700 (60.7%)** silently misattributed | **VERIFIED EXACT** |
| **Guarded Interception Retention** | `evalfault` provenance observer | **0 / 700 (0.0%)** contamination ($C_i^* = 0$) | **VERIFIED EXACT** |
| **Clean Control Preservation** | Clean unperturbed runs ($n=60$) | **60 / 60 (100%)** retained | **VERIFIED EXACT** |
| **Multi-Attempt Recovery Retention** | Recovered execution traces ($n=320$) | **320 / 320 (100%)** retained | **VERIFIED EXACT** |
| **Exception-Only Blind Spots** | Native exception handler failures | **130 / 700 (18.6%)** missed by native | **VERIFIED EXACT** |
| **Synthetic Benchmark Specificity** | 450 synthetic challenge test cases | **0 false exclusions** on valid runs | **VERIFIED EXACT** |
| **Live Pilot Benchmark Provenance** | 50 live trajectories, 129 OpenRouter calls | **0 live score contaminations** | **VERIFIED EXACT** |

---

## 📄 Citation

```bibtex
@article{hossain2026failure,
  author    = {Hossain, Md Sharif and Mahmud, Faez},
  title     = {Failure Is Not a Score: Auditing Defense Utility Collapse and Infrastructure Provenance in {LLM}-Agent Benchmarks},
  journal   = {IEEE Transactions on Dependable and Secure Computing},
  year      = {2026},
  note      = {Under Review}
}
```

---

## 📜 License

All code and evaluation harnesses are licensed under the [MIT License](LICENSE).  
The empirical dataset ledgers in `data/` are provided for research replication.
