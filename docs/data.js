// Numbers copied from results/metrics_main.csv, metrics_flip.csv, metrics_validity.csv,
// metrics_components.csv and the final report (TVA_RAG_Final_Report.tex).
window.DATA = {
  models: ["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b", "qwen3.5:35b"],
  modes: ["closed_book", "naive", "naive_trust", "recency", "tva"],
  modeLabel: {closed_book: "Closed-book", naive: "Naive RAG", naive_trust: "Naive + trust", recency: "Recency rerank", tva: "TVA-RAG (ours)"},
  colors: {closed_book: "#94a3b8", naive: "#7dd3fc", naive_trust: "#60a5fa", recency: "#ffc46b", tva: "#c084fc"},
  status: {CURRENT: "#4ade80", SUPERSEDED: "#fb7185", UNVERIFIED: "#ffc46b", FUTURE: "#94a3b8", UNCONFLICTED: "#6b7598", absent: "#2b3350"},

  // accuracy per model, order = modes; stale = stale-answer rate; abst = TVA abstention
  now: {
    "llama3.2:3b": {acc: [0.606, 0.972, 0.972, 0.887, 0.944], stale: [0.155, 0.028, 0.028, 0.113, 0.042], abst: 0.014},
    "llama3.1:8b": {acc: [0.690, 0.986, 0.986, 0.958, 0.986], stale: [0.239, 0.014, 0.014, 0.042, 0.000], abst: 0.014},
    "qwen2.5:7b":  {acc: [0.634, 1.000, 1.000, 0.944, 0.845], stale: [0.211, 0.000, 0.000, 0.056, 0.014], abst: 0.141},
    "qwen3.5:35b": {acc: [0.775, 0.986, 0.986, 1.000, 0.986], stale: [0.197, 0.000, 0.014, 0.000, 0.000], abst: 0.014},
    pooled: {acc: [0.676, 0.986, 0.986, 0.947, 0.940], stale: [0.201, 0.011, 0.014, 0.053, 0.014], abst: 0.046},
  },
  past: {
    "llama3.2:3b": {acc: [0.465, 0.085, 0.127, 0.169, 0.732], abst: 0.000},
    "llama3.1:8b": {acc: [0.577, 0.437, 0.352, 0.423, 0.972], abst: 0.000},
    "qwen2.5:7b":  {acc: [0.394, 0.028, 0.000, 0.099, 0.775], abst: 0.169},
    "qwen3.5:35b": {acc: [0.761, 0.817, 0.535, 0.789, 0.873], abst: 0.127},
    pooled: {acc: [0.549, 0.342, 0.254, 0.370, 0.838], abst: 0.074},
  },
  ctl: {closed_book: [0.85, 0.95, 1.00, 1.00], retrieval: 1.000},
  // stale-only corpus (poisoning): naive / naive_trust / tva
  staleOnly: {
    "llama3.2:3b": {acc: [0.225, 0.169, 0.366], stale: [0.732, 0.761, 0.535], abst: 0.070},
    "llama3.1:8b": {acc: [0.099, 0.113, 0.268], stale: [0.845, 0.845, 0.352], abst: 0.366},
    "qwen2.5:7b":  {acc: [0.056, 0.056, 0.113], stale: [0.930, 0.930, 0.549], abst: 0.338},
    "qwen3.5:35b": {acc: [0.028, 0.028, 0.465], stale: [0.915, 0.930, 0.310], abst: 0.225},
    pooled: {acc: [0.102, 0.092, 0.303], stale: [0.856, 0.866, 0.437], abst: 0.250},
  },
  // flip rate among closed-book-correct items (stale-only corpus)
  flip: {
    "llama3.2:3b": {n: 43, naive: 0.674, trust: 0.698, tva: 0.419, abst: 0.070, still: 0.512},
    "llama3.1:8b": {n: 49, naive: 0.776, trust: 0.776, tva: 0.204, abst: 0.388, still: 0.388},
    "qwen2.5:7b":  {n: 45, naive: 0.889, trust: 0.889, tva: 0.378, abst: 0.467, still: 0.156},
    "qwen3.5:35b": {n: 55, naive: 0.909, trust: 0.927, tva: 0.145, abst: 0.255, still: 0.600},
  },
  validity: { // VALID_FROM stated, within 31 days, within 1 year
    "llama3.2:3b": [1.000, 0.873, 0.901], "llama3.1:8b": [0.986, 0.944, 0.958],
    "qwen2.5:7b": [0.915, 0.718, 0.775], "qwen3.5:35b": [0.986, 0.958, 0.972],
  },
  latency: [["Closed-book", 0.46], ["Naive RAG", 0.49], ["Recency rerank", 0.48], ["TVA-RAG (detector cached)", 0.74]],
  components: [
    ["Temporal extractor (regex)", "anchor-date accuracy, 7 header formats", "1.000", "162 docs"],
    ["Temporal extractor (regex)", "reports “unknown” on undated documents", "1.000", "7 docs"],
    ["LLM date fallback (llama3.1:8b)", "hallucinated a date on undated documents", "0 / 7", "7 docs"],
    ["Retrieval recall@5, both item docs", "BM25 · dense · hybrid (RRF)", "0.944 · 1.000 · 0.986", "71 items"],
    ["Conflict detector (deployed, full run)", "pair precision · recall · F1", "0.922 · 0.757 · 0.831", "149 pairs"],
    ["Status assignment", "item documents with the correct status", "0.848", "211 docs"],
  ],
  detectors: [ // name, P, R, F1, cost, color
    ["Claims · qwen3.5:35b (used)", 0.898, 0.757, 0.822, "1.7 s uncached", "#c084fc"],
    ["NLI cross-encoder, similarity-gated", 0.727, 0.914, 0.810, "0.06 s", "#ffc46b"],
    ["Claims · llama3.1:8b", 0.549, 0.800, 0.651, "1.1 s", "#7dd3fc"],
  ],
  statusDist: { // share of queries, t = 2026-01-01, 4 models x 71 items
    stale:   [["SUPERSEDED", 0.676], ["UNCONFLICTED", 0.211], ["UNVERIFIED", 0.099], ["absent", 0.014]],
    current: [["CURRENT", 0.761], ["SUPERSEDED", 0.014], ["UNCONFLICTED", 0.225]],
  },
  domains: [
    ["Software & technology", 20, "Python 2 EOL · GitHub default branch · Java LTS · TLS 1.0/1.1 · Windows 10 · iPhone connector"],
    ["World politics & geography", 20, "UK monarch · newest NATO member · Türkiye · North Macedonia · Croatia's currency · US President · Pope"],
    ["Indian policy", 10, "default income-tax regime · GST on online gaming · GST on health insurance · GST slabs · Union Territories · 5G"],
    ["Medicine & public health", 7, "COVID-19 PHEIC · USPSTF aspirin · hypertension threshold · screening ages · peanut introduction · mpox"],
    ["Indian law", 5, "IPC → BNS · Evidence Act → BSA · Section 377 · triple talaq · Article 370"],
    ["Science", 5, "Pluto · kilogram · named elements · tallest building · Saturn's moons 146 → 274"],
    ["Business", 3, "Alphabet · Twitter ownership · Air India"],
    ["Sports", 1, "IPL team count"],
  ],
  years: [[2006, 1], [2010, 1], [2015, 2], [2016, 1], [2017, 5], [2018, 4], [2019, 6], [2020, 5], [2021, 4], [2022, 13], [2023, 9], [2024, 7], [2025, 13]],
  promptAbl: [ // metric, 3b, 8b, 7b, 35b
    ["t = now, pilot", "0.958", "0.972", "0.831 (abst 0.155)", "1.000"],
    ["t = now, final", "0.944", "0.986", "0.845 (abst 0.141)", "0.986"],
    ["t = past, pilot", "0.718", "0.817", "0.704", "0.873"],
    ["t = past, final", "0.732", "0.972", "0.775", "0.873"],
    ["stale-only, pilot", "0.380", "0.254", "0.113", "0.465"],
    ["stale-only, final", "0.366", "0.268", "0.113", "0.465"],
  ],
};
