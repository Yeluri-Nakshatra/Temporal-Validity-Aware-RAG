# Problem Statements on Retrieval-Augmented Generation (RAG) Systems
## A Research Survey, Feasibility Analysis and Comparative Study for a Major Project

*Prepared: 6 November 2026*

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background: What RAG Is and Why It Matters Now](#2-background-what-rag-is-and-why-it-matters-now)
3. [How the Problem Statements Were Selected](#3-how-the-problem-statements-were-selected)
4. [Problem Statement 1: Stale-Evidence Poisoning and Temporal Validity in RAG (Recommended)](#4-problem-statement-1-stale-evidence-poisoning-and-temporal-validity-in-rag-recommended)
5. [Problem Statement 2: Trustworthy Multilingual RAG for Indian Citizen Services](#5-problem-statement-2-trustworthy-multilingual-rag-for-indian-citizen-services)
6. [Problem Statement 3: Defending RAG Knowledge Bases Against Poisoning and Indirect Prompt Injection](#6-problem-statement-3-defending-rag-knowledge-bases-against-poisoning-and-indirect-prompt-injection)
7. [Problem Statement 4: Knowing When RAG Is Wrong: Confidence, Abstention and Retrieval Gating](#7-problem-statement-4-knowing-when-rag-is-wrong-confidence-abstention-and-retrieval-gating)
8. [Problem Statement 5: Multimodal RAG over PDFs with Tables and Charts](#8-problem-statement-5-multimodal-rag-over-pdfs-with-tables-and-charts)
9. [Cross-Cutting Comparison of RAG Solution Families](#9-cross-cutting-comparison-of-rag-solution-families)
10. [Evaluation Methodology and Tooling](#10-evaluation-methodology-and-tooling)
11. [Final Recommendation and Project Plan](#11-final-recommendation-and-project-plan)
12. [References](#12-references)

---

## 1. Executive Summary

Retrieval-Augmented Generation (RAG) is the dominant architecture for connecting Large Language Models (LLMs) to private, domain-specific, or frequently changing information. Despite its popularity, the 2025–2026 research literature shows that RAG systems fail in several systematic and under-addressed ways. This report surveys that literature, identifies five problem statements that are both academically significant and feasible for a college major project, and proposes a concrete solution for each, with a comparison against all existing alternatives.

**Recommended problem statement:** *Temporal-Validity-Aware RAG* — detecting and handling retrieved evidence that is outdated so that the system answers correctly "as of" a given date. A September 2026 study showed that outdated documents flip 30–37% of otherwise-correct LLM answers, and up to 75% when the prompt instructs the model to trust the document. No mature solution exists, the dataset is public, and the project can run on a laptop with open-weight models.

**Best applied alternative:** *Trustworthy Multilingual RAG for Indian Citizen Services* (government schemes, legal provisions) in Hindi and Telugu, where published evidence shows retrieval collapses on colloquial and cross-language queries. This has high social relevance and can be combined with the recommended problem, since scheme rules and laws change over time.

| Rank | Problem Statement | Novelty | Feasibility | Compute | Data Availability |
|---|---|---|---|---|---|
| 1 | Stale-evidence poisoning / temporal validity | Very high (Sept 2026) | High | Low | Public (317 verified reversals) |
| 2 | Multilingual citizen-service RAG (Hindi/Telugu) | High for Telugu | Medium | Low–Medium | Partial; evaluation set must be built |
| 3 | Knowledge-base poisoning defence | High | High | Low | Public attack setups |
| 4 | Confidence, abstention and retrieval gating | High | Medium | Low | Public (HotpotQA, MuSiQue) |
| 5 | Multimodal RAG over PDFs (tables, charts) | Medium | Medium | High (GPU) | Public (UniDoc-Bench) |

---

## 2. Background: What RAG Is and Why It Matters Now

### 2.1 The core idea

An LLM is trained on a fixed snapshot of text. It cannot know about documents created after training, private organisational data, or very niche domains. RAG addresses this by inserting a retrieval step before generation:

1. **Ingestion.** Documents are split into chunks, converted into vector embeddings, and stored in a vector index (and often a keyword index as well).
2. **Retrieval.** At query time, the user question is embedded and the top-*k* most similar chunks are fetched. Modern systems use *hybrid retrieval* (dense vectors + BM25 keyword matching) followed by a *reranker*.
3. **Augmentation.** The retrieved chunks are placed in the prompt as context.
4. **Generation.** The LLM produces an answer grounded in the context, ideally with citations.

### 2.2 Why RAG remains relevant in 2026

- **Freshness and privacy.** RAG is the only practical way to give an LLM access to up-to-date and private information without retraining (Wang et al., 2025).
- **Cost.** Prompt caching has made *long-context prompting* competitive for small static corpora (under roughly one million tokens), but RAG remains necessary for large or changing corpora.
- **Industry adoption.** Enterprise assistants, customer support, legal and medical search, and government citizen-service chatbots are overwhelmingly built on RAG.

### 2.3 The evolution of RAG architectures

| Generation | Description | Typical Weakness |
|---|---|---|
| Naive RAG | Embed → top-k → stuff into prompt | Poor recall, no reasoning over evidence, no time awareness |
| Advanced RAG | Hybrid retrieval, reranking, query rewriting, chunk optimisation | Still single-shot; cannot resolve conflicting evidence |
| Modular / Agentic RAG | LLM plans, retrieves iteratively, uses tools, reflects | 3–10× slower and costlier; hard to evaluate |
| GraphRAG | Knowledge graph of entities/relations supports multi-hop | Expensive to construct; overkill for flat documents |
| Long-context + caching | Place the entire corpus in the prompt | Lost-in-the-middle effect; no freshness; same stale-evidence failure |

### 2.4 Recurring open problems reported in surveys

Across the agentic RAG survey (Singh et al., 2025), the systematic review (2025), and the 2026 robustness survey, the following gaps recur:

- Imperfect retrieval degrades answers; models generate anyway when retrieval fails.
- Handling **conflicting or ambiguous evidence** remains open.
- **Knowledge freshness** and **temporal validity** are rarely modelled.
- **Security**: corpus poisoning and indirect prompt injection.
- **Evaluation**: output-level metrics are insufficient for multi-step (agentic) pipelines.
- **Low-resource languages** lag significantly in retrieval quality.
- **Latency and cost** of retrieval and multi-round generation.

---

## 3. How the Problem Statements Were Selected

The selection used four criteria, each scored from the literature:

1. **Novelty** — Is the problem recognised in 2025–2026 peer-reviewed or preprint literature as unsolved? Is there a recent paper that names it explicitly?
2. **Feasibility** — Can a student team build and evaluate a solution in one academic semester (12–16 weeks) with open-weight models?
3. **Compute** — Can it run on a laptop or a single free/cheap GPU (Google Colab, Kaggle)?
4. **Data availability** — Is there a public benchmark, or can an evaluation set be constructed cheaply?

Sources were drawn from arXiv (2025–2026), ACL/EMNLP/SIGIR/KDD proceedings, Springer and MDPI journals, and practitioner reports. Vendor blogs were used only for cost/latency heuristics and are flagged as such. One frequently cited 2026 paper, *"SoK: Agentic RAG"* (arXiv 2603.07379), was **withdrawn by arXiv administrators** for not meeting content-quality standards and should **not** be cited.

---

## 4. Problem Statement 1: Stale-Evidence Poisoning and Temporal Validity in RAG (Recommended)

### 4.1 Background and evidence

RAG is meant to fix *outdated* model knowledge. But what happens when the *retrieved document itself* is outdated? The September 2026 paper *"Stale-Document Poisoning: When Outdated Retrieval Overrides Correct Model Answers"* (arXiv 2609.31342) studied exactly this:

- **Dataset:** 317 verified knowledge reversals across medicine, law, software and platform policy, each grounded in dated official sources. Example pattern: a drug guideline that was reversed, a law that was amended, a software API that was deprecated.
- **Finding 1:** When a model already answers correctly *without* retrieval, feeding it an outdated document flips **30% of Llama answers and 37% of Qwen answers** to the wrong answer, even without being told to trust the document.
- **Finding 2:** Adding the instruction "answer based on the document" raises the flip rate to **66% (Llama) and 75% (Qwen)**.
- **Finding 3:** Across four open models and four domains, poisoning ranges from **17% to 91%**.
- **Finding 4:** Matched up-to-date evidence is followed **97–100%** of the time. So the failure is purely about *temporal judgement*, not about reading comprehension.
- **Finding 5:** Changing only the evaluation date produces little change in behaviour. But when the model is explicitly told *when the old evidence stops applying*, large models switch to the correct answer almost perfectly.
- **Mitigation tested:** A fixed recency-aware hybrid reranker reduced poisoning by only **4.6–10.0 points**, and only when date metadata was accurate.

Related 2026 work treats conflict between documents as a separate problem: **ConflictRAG** (arXiv 2605.17301) detects, classifies (factual / temporal / opinion) and resolves inter-document conflicts; **EvoTrustRAG** (arXiv 2608.07933) builds a conflict evidence graph and uses temporal relations to decide whether a conflict reflects legitimate knowledge evolution; **ArbGraph** (arXiv 2604.18362) arbitrates claims before generation.

### 4.2 Formal problem statement

> *Given a corpus of documents D with heterogeneous and partially known publication/effective dates, a user query q, and a reference date t, design a RAG system that (a) retrieves the evidence that is valid at time t, (b) detects when retrieved evidence has been superseded, (c) generates an answer that is correct "as of t" with citations and an explicit validity window, and (d) abstains or flags uncertainty when temporal metadata is missing or conflicting — while minimising the stale-evidence flip rate without reducing accuracy on non-temporal queries.*

### 4.3 Objectives

1. Reproduce the stale-document poisoning baseline on 2–3 open models (e.g., Llama 3.x 8B, Qwen 2.5/3 7B, Gemma).
2. Build **Temporal-Validity-Aware RAG (TVA-RAG)** with the components below.
3. Reduce the flip rate by a statistically significant margin over the paper's recency reranker.
4. Produce a reusable *temporal metadata extraction* module and an *"as-of" answer format*.

### 4.4 Proposed solution: TVA-RAG architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              INGESTION PIPELINE              │
  Documents ──────► │ Parse → Chunk → Temporal Metadata Extractor  │
                    │   (publication date, effective date,         │
                    │    supersession links, "valid until")        │
                    │ → Dense + BM25 index with time fields        │
                    └─────────────────────────────────────────────┘
                                          │
  Query q, date t ──► Query Analyser ──► Hybrid Retriever (top-k)
                      (is q time-sensitive?)        │
                                                    ▼
                           Temporal Conflict Detector
                           (cluster claims; find contradictions;
                            order by effective date; mark superseded)
                                                    │
                                                    ▼
                           Validity-Aware Reranker
                           (score = relevance × validity(t) × trust)
                                                    │
                                                    ▼
                           Generator with Validity Prompting
                           ("Evidence A valid 2019–2023; superseded
                             by Evidence B effective 2024-01-01")
                                                    │
                                                    ▼
                           Answer + citations + validity window
                           + abstain flag if metadata missing
```

**Component details**

| Component | Method | Notes |
|---|---|---|
| Temporal Metadata Extractor | Regex + LLM extraction of publication date, effective date, "supersedes/replaced by" relations, version numbers | Store as structured fields; confidence score per field |
| Query Analyser | Small classifier (or LLM prompt) that labels queries as time-sensitive or not | Non-temporal queries bypass the temporal path to protect accuracy |
| Temporal Conflict Detector | Extract atomic claims from top-k chunks; embed; cluster; detect contradiction with an NLI model; order by effective date | Builds on ConflictRAG / EvoTrustRAG ideas |
| Validity-Aware Reranker | `score = relevance × validity(t) × source_trust`, where `validity(t)` decays after supersession | Improves on the static recency reranker in the 2026 paper |
| Validity Prompting | The prompt states, per chunk, "valid from X to Y; superseded by Z" | The paper shows models switch answers almost perfectly when told when evidence expires |
| Abstention | If temporal metadata confidence is low and claims conflict, answer with a caveat or abstain | Ties to Problem Statement 4 |

### 4.5 Dataset and evaluation

- **Primary:** The 317-reversal dataset from arXiv 2609.31342 (release expected with the paper; otherwise reconstruct a subset from dated official sources such as drug labels, Indian statutory amendments, and software changelogs).
- **Secondary:** Build a small Indian-context extension (e.g., 50 reversals from government scheme eligibility changes, GST rate changes, Supreme Court overrulings).
- **Metrics:**
  - *Flip rate* (correct → wrong after stale retrieval) — the primary metric.
  - *Temporal accuracy @ t* (fraction of answers correct for the reference date).
  - *Validity-window F1* (does the stated validity window match ground truth?).
  - *Non-temporal accuracy* (ensure no regression).
  - *Faithfulness* via RAGAS and a human-labelled subset.

### 4.6 Comparison with all available alternatives

| Approach | Handles stale evidence? | Needs date metadata? | Cost | Weakness |
|---|---|---|---|---|
| Naive / Advanced RAG | No | No | Low | Follows whatever is retrieved; 30–75% flip rate |
| Long-context (whole corpus in prompt) | No | No | Medium–High | Same failure; the issue is judgement, not retrieval |
| Fine-tuning on fresh data | Partially | No | High | Stale again the moment data changes; no citations |
| Recency filter / recency reranker (2026 paper) | Partially | Yes | Low | Only 4.6–10 point reduction; needs accurate dates |
| ConflictRAG | Partially (temporal conflict type) | No | Medium | Resolves contradictions but does not model expiry |
| ArbGraph | Partially | No | Medium | Claim arbitration for long-form, not validity windows |
| EvoTrustRAG | Mostly | Yes | Medium–High | Closest competitor; attributes conflict origin; no abstention |
| **TVA-RAG (proposed)** | **Yes** | Yes (with confidence) | Low–Medium | Depends on metadata extraction quality; mitigated by abstention |

### 4.7 Risks and mitigations

- *Metadata extraction errors.* Mitigate with confidence scores and abstention; evaluate extractor separately.
- *Dataset not yet released.* Reconstruct a subset; the construction process is itself a contribution.
- *Model variance.* Run each experiment with three seeds and report confidence intervals.

### 4.8 Why this is the recommended choice

Very recent, clearly measurable, low compute, public data, and socially important (medicine, law, policy). It yields a clean research narrative: *baseline → diagnosis → proposed architecture → measurable improvement*.

---

## 5. Problem Statement 2: Trustworthy Multilingual RAG for Indian Citizen Services

### 5.1 Background and evidence

India has hundreds of central and state welfare schemes and a large body of legal text, yet most RAG assistants are tested only in English.

- **IndicRAGSuite** (AI4Bharat / IIT Madras, arXiv 2506.01615) released IndicMSMarco (1,000 human-verified queries in 13 Indian languages) and large Wikipedia-derived training data. Retrieval quality varies sharply by language; BGE-M3 and multilingual-e5-large were the best embedding models; the authors list *low-resource Indian languages* as the remaining weak point.
- **Agricultural advisory study** (arXiv 2608.14886, 2026) on Bengali: dense retrieval Recall@10 fell from **0.970 on formal queries to 0.093 on colloquial farmer queries**; BM25 collapsed from 0.506 to **0.004** across languages; hybrid RRF was best overall (0.539); embedding configuration and passage length changed recall by up to **7×**. The authors recommend reporting results *per language condition and per query type*.
- A 2026 Springer survey of Indic cross-modal retrieval reports Hindi and Gujarati still trail significantly.
- Existing GitHub scheme chatbots (SchemeSetu, Sakhi, schemesure, rural-scheme-advisor, indicrag, SchemeSathiAI) claim Telugu or Hindi support, but none reports a validated Telugu or Hindi evaluation; one reports romanised Hindi as the hardest retrieval case, and one explicitly says Telugu support is a future direction.

### 5.2 Formal problem statement

> *Design and evaluate a RAG assistant over official Indian government scheme and legal documents that answers questions posed in Hindi, Telugu, English, and romanised (Latin-script) variants, including colloquial phrasing, with answers grounded in cited official text and a safe refusal path — and quantify retrieval and faithfulness per language condition and query style.*

### 5.3 Proposed solution architecture

```
 User query (Telugu / Hindi / English / romanised / colloquial)
        │
        ▼
 Language & Script Detector ──► Transliteration (romanised → native script)
        │
        ▼
 Query Normaliser (LLM few-shot): colloquial → formal scheme terminology;
   generate 2–3 paraphrases + English translation
        │
        ▼
 Hybrid Retrieval: BM25 (native script) + Dense (BGE-M3 / multilingual-e5)
   over both native-language and English document versions
        │   Reciprocal Rank Fusion
        ▼
 Cross-lingual Reranker (bge-reranker-v2-m3)
        │
        ▼
 Rule-based Eligibility Engine (age, income, state, category) ◄── structured
        │                                                          scheme DB
        ▼
 Generator (Indic-capable LLM, e.g., Sarvam, Gemma, Llama 3.x)
   with claim-level verification against retrieved spans
        │
        ▼
 Answer in user's language + page-level citations + refusal if unsupported
```

Key design decisions:

- **Eligibility is decided by rules, never by the LLM.** This eliminates the most dangerous hallucination class (telling a citizen they are eligible when they are not).
- **Claim-level verification.** Each sentence of the answer is checked against the retrieved span with an NLI model; unsupported claims are removed.
- **Per-condition evaluation.** Report Recall@k and MRR for every (query language × document language × query style) cell.

### 5.4 Dataset and evaluation

- **Corpus:** myScheme.gov.in records (~3,400 schemes), state scheme PDFs (e.g., Telangana / Andhra Pradesh), selected Acts.
- **Evaluation set:** 300–500 questions, written natively in Telugu and Hindi by native speakers (not translated), with colloquial and formal variants, plus romanised forms. Gold answers with page citations.
- **Metrics:** Recall@10, MRR (retrieval); faithfulness and answer relevance (RAGAS + human); refusal precision/recall; eligibility accuracy.

### 5.5 Comparison with all available alternatives

| Approach | Telugu/Hindi quality | Colloquial robustness | Cost | Weakness |
|---|---|---|---|---|
| English-only RAG | None | None | Low | Excludes most users |
| Translate-then-retrieve (query → English) | Medium | Low | Low | Translation errors on colloquial text; loses nuance |
| Native multilingual dense embeddings only | Medium–High | Low (0.093 R@10 on colloquial) | Low | Fails on informal phrasing |
| BM25 only | High for native-script exact terms | Low | Very low | Collapses cross-language (0.004) |
| Hybrid RRF (BM25 + dense) | High | Medium | Low | Still needs query normalisation |
| Long-context with full scheme corpus | Medium | Medium | Medium–High | ~3,400 schemes exceed cheap context; no citations |
| GraphRAG over scheme entities | High for relationship questions | Medium | High | Costly to build; eligibility better as rules |
| **Proposed: normaliser + hybrid + rerank + rules + verification** | **High** | **High** | Low–Medium | Needs native-speaker evaluation set |

### 5.6 Risks

- Building a Telugu evaluation set requires native speakers (the team can do this).
- Indic LLM quality varies; evaluate at least two generators.

---

## 6. Problem Statement 3: Defending RAG Knowledge Bases Against Poisoning and Indirect Prompt Injection

### 6.1 Background and evidence

- **Indirect prompt injection:** adversarial instructions hidden in a retrieved document reach the model's context and are executed.
- **Knowledge-base poisoning:** as few as **five crafted documents** can manipulate answers **90% of the time** (PoisonedRAG line of work).
- **PIDP-Attack** combines injection and poisoning to execute attacker instructions regardless of user input.
- A 2026 review found that **eight published defences were bypassed by adaptive attacks with >50% success each**, and that the field lacks rigorous threat models.
- **CleanBase** (arXiv 2605.00460, 2026) observes that malicious documents crafted for the same target question are highly similar, builds a similarity graph over the knowledge base, and detects *cliques*. It gives theoretical bounds on false positives/negatives.
- The survey *"Retrieved But Not Reliable"* (arXiv 2608.24977) organises attacks by objective (accuracy, privacy, fairness) and defences by stage (retrieval, rerank, generation, traceback).

### 6.2 Formal problem statement

> *Design a layered, model-agnostic defence for RAG knowledge bases that detects poisoned or instruction-bearing documents at ingestion and retrieval time, isolates retrieved content from system instructions, and verifies output consistency — and evaluate attack success rate versus utility loss under both fixed and adaptive (diversified) attackers.*

### 6.3 Proposed solution: layered defence

```
 Ingestion       │ Provenance & allowlisting → content hashing/signing
                 │ → instruction-pattern scanner → collective similarity-graph
                 │   clique detection (CleanBase-style) → quarantine queue
 ────────────────┼────────────────────────────────────────────────────────
 Retrieval       │ Diversity-aware retrieval (penalise near-duplicate clusters)
                 │ → per-source hit-rate anomaly monitor
 ────────────────┼────────────────────────────────────────────────────────
 Generation      │ Context isolation (data vs. instructions, delimiters,
                 │ "treat retrieved text as untrusted") → spotlighting
 ────────────────┼────────────────────────────────────────────────────────
 Output          │ Consistency check: answer with full context vs. answer
                 │ with suspicious cluster removed; flag divergence
                 │ → traceback: which chunk changed the answer?
```

**Novel contribution:** evaluate CleanBase-style clique detection against a *diversified* attacker (paraphrased, stylistically varied poison documents) and add a *retrieval-diversity* and *output-consistency* layer to close that gap.

### 6.4 Dataset and evaluation

- Base corpora: Natural Questions / HotpotQA / MS MARCO subsets.
- Attacks: PoisonedRAG-style targeted poisoning, indirect injection documents, diversified/paraphrased variants (adaptive).
- Metrics: Attack Success Rate (ASR), clean-accuracy drop, detection precision/recall, latency overhead.

### 6.5 Comparison with all available alternatives

| Defence | Model access needed | Catches diversified poison? | Utility loss | Weakness |
|---|---|---|---|---|
| Per-document instruction classifier | No | Partially | Low | Misses poison without explicit instructions |
| Fine-tuning the LLM to resist injection | White-box | Partially | Low | Not possible with API models; still bypassed |
| Retrieval-side filtering / perplexity | No | Low | Medium | Adds latency; degrades utility |
| Query rewriting | No | Low | Low | Only reduces exposure |
| CleanBase (clique detection) | No | Low (relies on similarity) | Low | Evadable by diversifying documents |
| Context isolation / spotlighting | No | n/a (injection only) | Low | Does not address poisoning |
| **Proposed layered defence** | No | **Medium–High** | Low–Medium | Needs careful threshold tuning; adaptive arms race |

---

## 7. Problem Statement 4: Knowing When RAG Is Wrong: Confidence, Abstention and Retrieval Gating

### 7.1 Background and evidence

- **Retrieval-state lock-in** (arXiv 2606.22728, 2026): repeated samples condition on the *same defective retrieval*, so they agree — and agreement falsely signals confidence. In the study, **42% of KG-RAG errors and 59% of dense-retrieval errors had zero answer dispersion**. Two variants: *absence* (empty/unusable retrieval → model falls back to memory) and *presence* (coherent but wrong neighbourhood). A three-check acceptance rule reached **91.9% precision** but certified only **7.7%** of answers.
- **Adaptive retrieval:** TARG (arXiv 2511.09803) gates retrieval on a no-context draft's entropy/margin; **Know Before You Fetch** (arXiv 2606.29959) calibrates uncertainty into a per-query choice among closed-book, compact context, full context, or abstain; **ReaLM-Retrieve** (SIGIR 2026) decides when to retrieve during reasoning (+10.1 F1, 47% fewer retrievals than IRCoT).
- Self-RAG and similar reflective methods require white-box model access.

### 7.2 Formal problem statement

> *Develop a model-agnostic confidence estimator for RAG that combines answer-level, evidence-level and retrieval-state-level signals to decide whether to answer, retrieve more, or abstain — maximising coverage at a target precision and detecting lock-in errors that sampling-based confidence misses.*

### 7.3 Proposed solution

```
 Query ──► No-context draft (logits: entropy, top-1/top-2 margin)
   │
   ├──► Retrieval ──► Retrieval-state features:
   │                   top-k score distribution, cluster coherence,
   │                   query–chunk entailment, empty/low-score flag
   │
   ├──► Generation with context ──► Evidence-support score (NLI/attribution)
   │
   └──► Answer dispersion across n samples
                 │
                 ▼
     Calibrated Gate (logistic / small GBM trained on held-out data)
        → ANSWER | RETRIEVE MORE (expand k, rewrite query) | ABSTAIN
```

The contribution is the **retrieval-state channel** and a learned gate that expands coverage beyond the 7.7% of the diagnosis paper while keeping precision high.

### 7.4 Evaluation

- Datasets: HotpotQA, MuSiQue, 2WikiMultiHopQA, plus a domain set (e.g., medical or legal).
- Metrics: selective accuracy / coverage curves (AUROC, AURC), lock-in detection rate, retrieval calls per query, latency.

### 7.5 Comparison with all available alternatives

| Method | Model access | Signals used | Detects lock-in? | Weakness |
|---|---|---|---|---|
| Sampling agreement (self-consistency) | Black-box | Answer only | No (blind by construction) | Agreement ≠ correctness under lock-in |
| Self-RAG | White-box (training) | Reflection tokens | Partially | Needs fine-tuning |
| DRAGIN / TARG | Logits | Token entropy | No | Ignores retrieval quality |
| Know Before You Fetch | Logits | Calibrated uncertainty | Partially | No retrieval-state channel |
| ReaLM-Retrieve | Training | Step-level uncertainty | Partially | Needs learned policy; underperforms on simple 2-hop |
| Lock-in diagnosis rule | Black-box | Answer + evidence + retrieval | Yes | 7.7% coverage |
| **Proposed calibrated multi-channel gate** | Black-box / logits | All three channels | **Yes** | Needs labelled calibration set |

---

## 8. Problem Statement 5: Multimodal RAG over PDFs with Tables and Charts

### 8.1 Background and evidence

- **UniDoc-Bench** (arXiv 2510.03663): 70k real PDF pages across 8 domains; evidence linked across text, tables and figures. Four paradigms compared: text-only, image-only, text-image fusion, joint multimodal embeddings. **Fusion consistently wins**; current joint multimodal embeddings fall short.
- **Chart-MRAG Bench** (arXiv 2502.14864): 4,738 QA pairs across 8 domains; unified multimodal embedding retrieval struggles on charts.
- 2025 survey (arXiv 2510.15253) covers the document-understanding RAG landscape (ViDoSeek, etc.).

### 8.2 Formal problem statement

> *Build a document-centric RAG system that retrieves and reasons over text, tables and charts in real-world PDFs by fusing textual and visual retrieval, and quantify when visual evidence adds value over text alone.*

### 8.3 Proposed solution

```
 PDF ──► Layout parser (Docling / Marker / Unstructured)
          ├── Text chunks (layout-aware)      ──► Dense + BM25 index
          ├── Tables → serialised Markdown/JSON ──► Table index + schema
          └── Figures/charts → page images     ──► Visual index (ColPali / ColQwen)
                                                    + chart-to-text captions
 Query ──► Parallel retrieval over all indices ──► Fusion (RRF + learned weights)
       ──► Vision-language generator (Qwen-VL / Gemma 3 / Llama 3.2-Vision)
       ──► Answer with text and figure citations
```

### 8.4 Comparison

| Paradigm | Tables | Charts | Cost | Weakness |
|---|---|---|---|---|
| Text-only (OCR) | Medium | Poor | Low | Loses layout and visual semantics |
| Image-only (ColPali) | Medium | Medium | High | Weak on dense text; large indices |
| Joint multimodal embedding | Medium | Poor | High | Underperforms fusion (UniDoc-Bench) |
| **Text-image fusion (proposed)** | **High** | **Medium–High** | High | Needs GPU; two indices |

*Note:* This is the most compute-intensive option and requires a GPU for the vision models.

---

## 9. Cross-Cutting Comparison of RAG Solution Families

| Family | Strengths | Weaknesses | Relative cost | Latency | Best suited for |
|---|---|---|---|---|---|
| Naive RAG | Cheap, simple | No time awareness, weak multi-hop, easily poisoned | 1× | Low | Baseline only |
| Advanced RAG (hybrid + rerank + rewriting) | Best recall per cost | Single-shot; cannot resolve conflicts | 1.5× | Low | Problems 1, 2, 3 |
| Agentic RAG | Multi-step, iterative retrieval | 3–10× slower; hard to evaluate; compounding errors | ~10× | High | Research-style questions |
| GraphRAG | Multi-hop over entities and relations | Expensive to build; overkill for flat corpora | High (build) | Medium | Relationship-heavy corpora |
| Long-context + prompt caching | Simplest for small static corpora | Lost-in-the-middle; no freshness; same stale-evidence failure | Varies | Medium–High | Corpora under ~1M tokens |
| Fine-tuning | Fast inference, style control | Stale as soon as data changes; no citations | High (train) | Low | Style and format, not facts |

**Routing guidance from the 2026 literature:** simple factual questions → advanced RAG; multi-hop/research questions → agentic RAG; relationship-heavy → GraphRAG; small static corpora → long-context with caching. Long-context models do better when evidence is spread evenly across many documents; RAG does better when evidence is sparse and retrieval is accurate; a hybrid of both is strongest.

---

## 10. Evaluation Methodology and Tooling

### 10.1 Frameworks

| Framework | Approach | Strengths | Weaknesses |
|---|---|---|---|
| RAGAS | Reference-free LLM-judge metrics: faithfulness, answer relevance, context precision/recall | Most widely used; easy CI integration | Judge-dependent; scores diverge from other tools |
| TruLens | "RAG Triad": context relevance, groundedness, answer relevance; OpenTelemetry tracing | Good for monitoring production traffic | Setup overhead |
| DeepEval | Pytest-style metrics incl. HallucinationMetric | Developer-friendly | Judge-dependent |
| ARES | Synthetic data + confidence-scored LLM judges with statistical inference | Less human annotation | Less maintained; verify against Stanford repo |
| FaithJudge / HHEM leaderboard | Claim-level faithfulness benchmarks | Fine-grained | Summarisation-centric |

A controlled 30-query study found RAGAS, DeepEval and an LLM-as-judge rubric **disagree** on the same outputs. Therefore: use one framework for iteration **and** a human-labelled subset (100–200 items) for final reporting.

### 10.2 Recommended evaluation protocol

1. Fix retrieval and generation components; evaluate retrieval (Recall@k, MRR, nDCG) separately from generation (faithfulness, correctness).
2. Report per-condition results (language, query style, temporal vs. non-temporal).
3. Three random seeds; report mean ± standard deviation.
4. Include ablations: remove each proposed component and measure the drop.
5. Report latency and cost per query.

---

## 11. Final Recommendation and Project Plan

### 11.1 Recommendation

**Primary:** Problem Statement 1 — *Temporal-Validity-Aware RAG (TVA-RAG)*.
**Optional extension:** apply TVA-RAG to Indian government schemes and legal amendments (merging Problem Statements 1 and 2), where rule changes are frequent and the social impact is high.

### 11.2 Suggested 14-week plan

| Weeks | Milestone |
|---|---|
| 1–2 | Literature review; finalise scope; set up environment (Python, LangChain/LlamaIndex or custom, Qdrant/Chroma, Ollama/vLLM) |
| 3–4 | Reproduce stale-document poisoning baseline on 2–3 open models; build or reconstruct evaluation set |
| 5–6 | Temporal metadata extractor; evaluate extraction accuracy |
| 7–8 | Conflict detector + validity-aware reranker |
| 9–10 | Validity prompting + abstention; end-to-end integration |
| 11 | Ablations, seeds, error analysis |
| 12 | Optional Indian-context extension (scheme amendments) |
| 13 | Demo UI (Streamlit/Gradio), documentation |
| 14 | Report, presentation, code release |

### 11.3 Suggested technology stack

- **Models:** Llama 3.x 8B, Qwen 2.5/3 7B, Gemma 3 (via Ollama or vLLM); optional API model for comparison.
- **Embeddings:** BGE-M3, multilingual-e5-large (Indic); bge-reranker-v2-m3.
- **Indexes:** Qdrant or Chroma (dense), Elasticsearch/OpenSearch or `rank_bm25` (sparse).
- **NLI / verification:** DeBERTa-v3 NLI or MiniCheck.
- **Evaluation:** RAGAS + custom metrics; human-labelled subset.
- **UI:** Streamlit or Gradio; FastAPI backend.

---

## 12. References

1. Stale-Document Poisoning: When Outdated Retrieval Overrides Correct Model Answers. arXiv:2609.31342 (2026). https://arxiv.org/abs/2609.31342
2. ConflictRAG: Detecting and Resolving Knowledge Conflicts in RAG. arXiv:2605.17301 (2026). https://arxiv.org/pdf/2605.17301
3. EvoTrustRAG: Evolution-Aware Conflict Attribution and Evidence Handling. arXiv:2608.07933 (2026). https://arxiv.org/abs/2608.07933
4. ArbGraph: Conflict-Aware Evidence Arbitration for Long-Form RAG. arXiv:2604.18362 (2026). https://arxiv.org/html/2604.18362v1
5. DRAGged into Conflicts: Detecting and Addressing Conflicting Sources in Search-Augmented LLMs. arXiv:2506.08500 (2025). https://arxiv.org/pdf/2506.08500
6. IndicRAGSuite: Large-Scale Datasets and a Benchmark for Indian Language RAG Systems. arXiv:2506.01615 (2025). https://arxiv.org/abs/2506.01615
7. Where Does Retrieval Fail? Evaluating RAG Architectures for Agricultural Advisory. arXiv:2608.14886 (2026). https://arxiv.org/pdf/2608.14886
8. A systematic survey of scalable cross-modal retrieval for inclusive multilingual information access in Indian languages. Discover Computing / Springer (2026). https://link.springer.com/article/10.1007/s10791-026-10771-0
9. Retrieved But Not Reliable: A Survey on Attacks and Defenses in RAG. arXiv:2608.24977 (2026). https://arxiv.org/pdf/2608.24977
10. CleanBase: Detecting Malicious Documents in RAG Knowledge Databases. arXiv:2605.00460 (2026). https://arxiv.org/pdf/2605.00460
11. Securing Retrieval-Augmented Generation: A Taxonomy of Attacks, Defenses, and Future Directions. arXiv:2604.08304 (2026). https://arxiv.org/html/2604.08304v1
12. Practical Poisoning Attacks against Retrieval-Augmented Generation. arXiv:2504.03957 (2025). https://arxiv.org/pdf/2504.03957
13. EcoSafeRAG: Efficient Security through Context Analysis in RAG. arXiv:2505.13506 (2025). https://arxiv.org/pdf/2505.13506
14. When Confidence Takes the Wrong Path: Diagnosing Retrieval-State Lock-In in RAG. arXiv:2606.22728 (2026). https://arxiv.org/html/2606.22728v1
15. When to Retrieve During Reasoning: Adaptive Retrieval for Large Reasoning Models (ReaLM-Retrieve). SIGIR 2026. arXiv:2604.26649. https://arxiv.org/abs/2604.26649
16. Know Before You Fetch: Calibrated Retrieval-Budget Allocation for RAG. arXiv:2606.29959 (2026). https://arxiv.org/abs/2606.29959
17. Retrieval as a Decision: Training-Free Adaptive Gating for Efficient RAG (TARG). arXiv:2511.09803 (2025). https://arxiv.org/abs/2511.09803
18. UniDoc-Bench: A Unified Benchmark for Document-Centric Multimodal RAG. arXiv:2510.03663 (2025). https://arxiv.org/html/2510.03663
19. Benchmarking Multimodal RAG through a Chart-based Document QA Generation Framework (Chart-MRAG). arXiv:2502.14864 (2025). https://arxiv.org/abs/2502.14864
20. Scaling Beyond Context: A Survey of Multimodal RAG for Document Understanding. arXiv:2510.15253 (2025). https://arxiv.org/pdf/2510.15253
21. When Retrieval Succeeds and Fails: Rethinking RAG for LLMs. arXiv:2510.09106 (2025). https://arxiv.org/pdf/2510.09106
22. Singh et al. Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG. arXiv:2501.09136 (2025). https://arxiv.org/abs/2501.09136
23. A Systematic Review of Key RAG Systems: Progress, Gaps, and Future Directions. arXiv:2507.18910 (2025). https://arxiv.org/pdf/2507.18910
24. Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards (FaithJudge). EMNLP 2025 Industry Track. https://arxiv.org/pdf/2505.04847
25. Disentangling Faithfulness Hallucinations in RAG: A Systematic Benchmark and Analysis. Machine Learning, vol. 115 (2026). https://link.springer.com/article/10.1007/s10994-026-07121-y
26. Benchmarking Hallucination Evaluation for RAG Under an Abstention Policy: RAGAS, DeepEval, and LLM-as-Judge (2026). https://www.researchgate.net/publication/399331938
27. RAG Evaluation Frameworks Compared: RAGAS vs TruLens vs DeepEval. Analytics Vidhya (2026). https://www.analyticsvidhya.com/blog/2026/07/rag-evaluation-frameworks/
28. RAG Techniques Compared: A Practical Guide (2026). https://blog.starmorph.com/blog/rag-techniques-compared-best-practices-guide
29. RAG security: indirect prompt injection and knowledge base poisoning. Prediction Guard (2026). https://predictionguard.com/blog/rag-security-indirect-prompt-injection-and-knowledge-base-poisoning
30. Example open-source scheme assistants: schemesure (https://github.com/aakashc23/schemesure), rural-scheme-advisor (https://github.com/adyasha-official/rural-scheme-advisor), indicrag (https://github.com/pandey0/indicrag).

*Note on a withdrawn source:* "SoK: Agentic RAG: Taxonomy, Architectures, Evaluation, and Research Directions" (arXiv:2603.07379) was withdrawn by arXiv administrators and is intentionally excluded from the reference list.
