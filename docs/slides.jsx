// Slide definitions. Each slide: {title, steps, notes, render(step)}
const D = window.DATA;
const M = D.models;
const accSeries = (block) => MODE_SERIES(M.map(m => block[m].acc));
const statusLegend = Object.entries(D.status).filter(([k]) => k !== "FUTURE").map(([k, c]) => ({label: k, color: c}));
const SLIDES = [
  // 0 ---------------------------------------------------------------- title
  {title: "Title", steps: 0, notes: "Open with the one-line idea: RAG fails when the retrieved document is itself outdated. TVA-RAG tells the generator which evidence is still valid at the reference date, instead of hoping it reads the dates itself.",
    render: () => (
      <div className="slide title-slide">
        <div className="kicker">Major project · retrieval-augmented generation · temporal validity</div>
        <h1>Temporal-Validity-Aware <span className="grad">Retrieval-Augmented Generation</span></h1>
        <p className="sub" style={{marginTop: 26, fontSize: 26}}>RAG that knows when its evidence expired: it detects <b>superseded</b> documents, answers <b>as of</b> any date, reports the <b>validity window</b>, and <b>abstains</b> when it cannot tell.</p>
        <div className="title-meta">
          <Pill kind="acc">llama3.2:3b · llama3.1:8b · qwen2.5:7b · qwen3.5:35b</Pill><Pill kind="teal">TempRev · 71 reversals · 20 controls</Pill><Pill kind="gold">4,332 generations · zero failures</Pill><Pill>no fine-tuning · local Ollama</Pill>
        </div>
        <div style={{display: "flex", gap: 70, marginTop: 70}}>
          <div className="hero-num"><div className="v grad">0.34 → 0.84</div><div className="k">pooled accuracy as of a past date, naive RAG → TVA-RAG</div></div>
          <div className="hero-num"><div className="v grad">−26 to −76 pts</div><div className="k">stale-document flip rate when only stale evidence exists (0.67–0.93 → 0.15–0.42)</div></div>
          <div className="hero-num"><div className="v grad">1.000</div><div className="k">control accuracy, every retrieval mode, every model</div></div>
        </div>
      </div>)},
  // 1 ---------------------------------------------------------------- motivation
  {title: "Motivation", steps: 1, notes: "A knowledge base is rarely cleaned. Two GST circulars, both retrieved, and naive RAG follows the one that answers most directly, even though at the reference date it was ten months in the future. Then the poisoning study numbers and the observation that drives the whole project.",
    render: () => (
      <div className="slide">
        <Header kicker="Motivation" title="RAG cures outdated model knowledge, until the retrieved document is itself outdated" />
        <div className="body"><div className="svgwrap"><StaleProblem /></div>
          <Frag i={1}><div className="row" style={{gap: 20}}>
            <Card className="rose" style={{flex: 1}}><p><b>Stale-document poisoning (arXiv 2609.31342, Sept 2026):</b> an outdated document flips <b>30–37 %</b> of otherwise-correct answers, and up to <b>75 %</b> when the model is told to trust the document. The paper's recency reranker recovered only 4.6–10 points.</p></Card>
            <Card className="accent" style={{flex: 1}}><p><b>Its key observation:</b> models follow current evidence 97–100 % of the time, and switch almost perfectly <b>when told when the old evidence stopped applying</b>. The generator does not need better reading; the system must say which evidence is still valid.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 2 ---------------------------------------------------------------- problem statement
  {title: "Problem statement", steps: 3, notes: "Read the formal statement, then the six requirements two at a time. Note the scope: English short-answer questions, notice-length documents, open-weight models run locally.",
    render: () => (
      <div className="slide">
        <Header kicker="Problem definition" title="Answer a question as it was correctly answerable on a given date" />
        <div className="body">
          <div className="quote">Given a corpus <K tex="D" /> whose documents about the same fact were written at different times and may contradict each other, a question <K tex="q" /> and a reference date <K tex="t" />, build <K tex="S(q,t,D)" /> returning an answer <K tex="a" />, cited documents <K tex="C" />, a validity window <K tex="[v_{\text{from}}, v_{\text{to}})" /> and an abstention flag.</div>
          <div className="grid3" style={{marginTop: 30}}>
            <Frag i={1}><Card tag="(a) temporal correctness" title="Right answer for t"><p><K tex="a" /> equals the answer that was true at time <K tex="t" />, not the answer that is true today.</p></Card></Frag>
            <Frag i={1}><Card tag="(b) supersession detection" title="Never present replaced evidence as current"><p>A document whose answer has been replaced by a later document dated <K tex="\le t" /> is never used as the current answer.</p></Card></Frag>
            <Frag i={2}><Card tag="(c) as-of reasoning" title="Ignore the future"><p>Documents dated after <K tex="t" /> are not used at all.</p></Card></Frag>
            <Frag i={2}><Card tag="(d) validity reporting" title="Say from when"><p><K tex="v_{\text{from}}" /> is the date from which <K tex="a" /> holds.</p></Card></Frag>
            <Frag i={3}><Card tag="(e) calibrated abstention" title="Refuse when unverifiable"><p>When the only relevant evidence has an unknown date and conflicts with other evidence, the system abstains.</p></Card></Frag>
            <Frag i={3}><Card tag="(f) no regression" title="Stable facts stay solved"><p>Accuracy on questions whose answer never changed is unchanged.</p></Card></Frag>
          </div>
          <Frag i={3}><p className="sub" style={{marginTop: 22, fontSize: 18}}><b>Primary metrics:</b> temporal accuracy at t · stale-answer rate · stale-document flip rate · abstention rate · validity-window agreement · control accuracy. <b>Scope:</b> English short-answer questions, notice-length documents, open-weight models run locally.</p></Frag>
        </div>
      </div>)},
  // 3 ---------------------------------------------------------------- related work
  {title: "Related work", steps: 1, notes: "Four strands. The poisoning paper measures the problem and hints at the fix. Conflict-aware RAG systems detect and resolve inter-document conflicts but do not expose validity windows or filter future evidence. Adaptive retrieval gates on confidence, which is blind to a stable but wrong retrieval state. Temporal QA benchmarks test closed-book models and do not ship the conflicting documents.",
    render: () => (
      <div className="slide">
        <Header kicker="Related work" title="Four strands, and the gap between them" />
        <div className="body"><div className="grid4" style={{flex: 1}}>
          <Card tag="stale-document poisoning" title="The problem, measured"><p>317 reversals, 12 models: outdated retrieval flips 30 % (Llama) and 37 % (Qwen) of answers, 66–75 % with a trust instruction. Matched up-to-date evidence is followed 97–100 %. Telling the model <b>when</b> old evidence stopped applying restores correctness; a recency reranker recovers only 4.6–10 points.</p></Card>
          <Card tag="knowledge conflicts in RAG" title="Detect and resolve"><p><b>ConflictRAG</b> detects, classifies and resolves inter-document conflicts; <b>EvoTrustRAG</b> builds a conflict evidence graph with temporal relations; <b>ArbGraph</b> arbitrates claims before long-form generation; <b>DRAGged into Conflicts</b> gives a taxonomy.</p></Card>
          <Card tag="adaptive retrieval · abstention" title="Gate on confidence"><p><b>Retrieval-state lock-in</b>: sampling-based confidence is blind to errors caused by a stable but wrong retrieval state. <b>Know Before You Fetch</b> and <b>TARG</b> gate retrieval on calibrated uncertainty. TVA-RAG's abstention is evidence-driven instead.</p></Card>
          <Card tag="temporal QA" title="Time-dependent questions"><p><b>TimeQA</b>, <b>TempLAMA</b> and <b>SituatedQA</b> study time-dependent questions for closed-book models. None supplies the conflicting documents, so retrieval-side handling of stale evidence cannot be measured.</p></Card>
        </div>
          <Frag i={1}><Card className="accent" style={{marginTop: 22}}><p><b>Gap:</b> none of the conflict-aware systems exposes validity windows, filters future evidence for as-of queries, or abstains on undated evidence. TVA-RAG operationalises the validity-signalling finding as a system component and adds conflict detection, as-of filtering and abstention; TempRev supplies the conflicting documents themselves.</p></Card></Frag>
        </div>
      </div>)},
  // 4 ---------------------------------------------------------------- key idea
  {title: "Key idea", steps: 2, notes: "Validity is not a property of a document; it is a property of the pair (document, reference date). Step through: no date, then t = present, then t in the past where the newer document becomes FUTURE and is dropped.",
    render: (s) => (
      <div className="slide">
        <Header kicker="Key idea" title="Validity is a function of the document and the reference date" sub="Instead of ordering documents by date, attach to each one a status computed relative to t, and tell the generator." />
        <div className="body"><div className="svgwrap"><TimelineIdea step={s} /></div></div>
      </div>)},
  // 5 ---------------------------------------------------------------- architecture
  {title: "Architecture", steps: 3, notes: "Build the pipeline: ingestion annotates dates offline; at query time hybrid retrieval, then the two purple additions (detector and status), then the reranker and validity prompting. Everything purple is new relative to an advanced RAG pipeline.",
    render: (s) => (
      <div className="slide">
        <Header kicker="System architecture" title="From (question, reference date) to an answer with a validity window" />
        <div className="body"><div className="svgwrap"><Pipeline step={s} /></div></div>
      </div>)},
  // 6 ---------------------------------------------------------------- temporal extractor
  {title: "Temporal extractor", steps: 1, notes: "Regex over seven header date styles and three effective-date styles. Confidence by where the date was found. The anchor is the effective date if present, else the publication date. LLM fallback only when nothing is found, and it is told not to infer dates from content. Results: perfect anchor accuracy on the 162 rendered documents, zero hallucinated dates.",
    render: () => (
      <div className="slide">
        <Header kicker="Architecture · ingestion" title="Temporal metadata extractor: one anchor date per document, with a confidence" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div className="svgwrap" style={{flex: 1.25}}><ExtractorDiag /></div>
          <div className="col" style={{flex: 1, justifyContent: "center"}}>
            <Card tag="7 header date formats"><p className="mono" style={{fontSize: 15.5, lineHeight: 1.7}}>Published: 24 August 2006 · Date: 2006-08-24 · Last updated: August 2006 · Press release dated 24/08/2006 · Notification dated 24th August, 2006 · (Issued 24 Aug 2006) · August 24, 2006</p><p>Also ISO, day-month-year and month-day-year with ordinals, dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy and month-year forms (month precision).</p></Card>
            <Frag i={1}><Card className="teal"><div className="row" style={{gap: 30}}>
              <div><div className="big grad">1.000</div><p>anchor-date accuracy, 162 documents</p></div>
              <div><div className="big grad">7 / 7</div><p>undated documents correctly reported “unknown”</p></div>
              <div><div className="big grad">0 / 7</div><p>dates hallucinated by the LLM fallback</p></div>
            </div></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 7 ---------------------------------------------------------------- retriever + detector
  {title: "Conflict detector", steps: 1, notes: "Question-conditioned: the detector states the shortest answer each document gives to this exact question, or NONE after a scope check. Two documents conflict when both give an answer and the answers are different. A cheap similarity gate runs first, and every call is cached and shared across generator models. The NLI variant is kept as an ablation.",
    render: () => (
      <div className="slide">
        <Header kicker="Architecture · query time" title="Question-conditioned, claim-level conflict detection" sub="Hybrid retriever first: BM25 + bge-base-en-v1.5 fused with reciprocal rank fusion (k = 60), top five documents." />
        <div className="body"><div className="svgwrap" style={{flex: 1}}><DetectorDiag /></div>
          <Frag i={1}><div className="grid3">
            <Card><p><b>Gate</b> whole-text embedding similarity ≥ 0.60 with at least one other retrieved document. Cheap, and it removes most pairs before any LLM call.</p></Card>
            <Card className="violet"><p><b>Claims, not labels</b> the detector LLM (qwen3.5:35b) answers the question from each document's point of view. Different names, numbers, versions, dates, or opposite yes / no → conflict.</p></Card>
            <Card><p><b>Ablation variant</b> an NLI cross-encoder (nli-deberta-v3-base) behind the same gate. 30× cheaper, 1.2 F1 points worse, and unusable without the gate.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 8 ---------------------------------------------------------------- validity status
  {title: "Validity status", steps: 1, notes: "The decision tree runs per retrieved document relative to t. FUTURE documents are dropped; SUPERSEDED documents get a low validity but stay visible; UNVERIFIED covers undated documents. Pairwise rather than transitive clusters, so one false conflict cannot poison a group.",
    render: () => (
      <div className="slide">
        <Header kicker="Architecture · query time" title="Pairwise validity status relative to the reference date" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div className="svgwrap" style={{flex: 1.15}}><StatusFlow /></div>
          <div className="col" style={{flex: 1, justifyContent: "center"}}>
            <table className="t">
              <thead><tr><th>Status</th><th>Condition</th><th>Validity</th></tr></thead>
              <tbody>
                <tr><td style={{color: "var(--fut)"}}>FUTURE</td><td>anchor date &gt; t</td><td className="mono">0 · dropped</td></tr>
                <tr><td style={{color: "var(--sup)"}}>SUPERSEDED</td><td>conflicts with a non-future document whose anchor is later; records <i>superseded_by</i>, <i>superseded_on</i></td><td className="mono">0.25</td></tr>
                <tr><td style={{color: "var(--cur)"}}>CURRENT</td><td>conflicts with others and none is later</td><td className="mono">1.0</td></tr>
                <tr><td style={{color: "var(--unv)"}}>UNVERIFIED</td><td>no date could be established</td><td className="mono">0.6 · 0.4 if conflicting</td></tr>
                <tr><td style={{color: "var(--acc2)"}}>UNCONFLICTED</td><td>dated, no conflicts</td><td className="mono">1.0</td></tr>
              </tbody></table>
            <Frag i={1}><Card className="accent"><p><b>What the detector gets right in practice</b> (t = 2026-01-01, 4 models × 71 items): 76 % of current documents marked CURRENT, 68 % of stale documents SUPERSEDED, 10 % UNVERIFIED (the undated ones), and only <b>1.4 % of current documents wrongly SUPERSEDED</b>.</p>
              <Stacked rows={[{name: "stale doc", parts: D.statusDist.stale.map(([k, v]) => ({v, color: D.status[k]}))}, {name: "current doc", parts: D.statusDist.current.map(([k, v]) => ({v, color: D.status[k]}))}]} legend={statusLegend} width={700} barH={28} labelW={120} /></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 9 ---------------------------------------------------------------- reranker + prompting
  {title: "Reranker & prompting", steps: 1, notes: "Two shared layers downstream of the status. The reranker multiplies retrieval score by validity so superseded documents sink but remain visible. The prompt annotates each document with date and status and states explicit rules, including when abstention is and is not allowed. In the stale-only setting the document's age is stated instead.",
    render: () => (
      <div className="slide">
        <Header kicker="Architecture · query time" title="Rerank by validity, then tell the generator what each document is" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div className="col" style={{flex: 1}}>
            <Card tag="validity-aware reranker" className="violet"><Eq small tex="\text{final} = \text{retrieval}\times\text{validity}(t)\times\text{source trust}" /><p style={{textAlign: "center"}}>SUPERSEDED documents sink below CURRENT ones but stay in the context, so the model can explain the history. FUTURE documents never reach the prompt.</p></Card>
            <Card tag="rules in the prompt">
              <ul className="list small">
                <li><b>Prefer CURRENT</b> evidence; never return a SUPERSEDED answer as current.</li>
                <li>If a CURRENT document answers the question, <b>answer from it; do not abstain</b>.</li>
                <li>Answer <b>ABSTAIN</b> only when no CURRENT document answers and the only relevant evidence is DATE UNKNOWN and conflicting.</li>
                <li>The ANSWER line holds the answer itself, never a status word.</li>
              </ul></Card>
            <Frag i={1}><Card className="rose"><p><b>Stale-only variant:</b> the document's age at t is stated and the model is told not to assume a time-varying fact still holds, to use its own knowledge if confident, and otherwise to abstain.</p></Card></Frag>
          </div>
          <Card tag="annotated context · mixed setting" style={{flex: 1.15}}>
            <Code style={{marginTop: 8}}>{"Reference date: "}<b>2026-01-01</b>{". Answer the question as it would be\ncorrectly answered on the reference date.\n\n"}<span className="k">[Document 1 | dated: 2025-09-22 | status: </span><span className="cur">CURRENT as of 2026-01-01</span><span className="k">]</span>{"\nGST exemption on health insurance ... individual health\ninsurance policies are now exempt from GST ...\n\n"}<span className="k">[Document 2 | dated: 2024-02-05 | status: </span><span className="sup">SUPERSEDED on 2025-09-22 by Document 1</span><span className="k">]</span>{"\nGST on insurance premiums ... attract GST at 18 percent ...\n\n"}<span className="k">[Document 3 | dated: unknown | status: </span><span className="unv">DATE UNKNOWN</span><span className="k">]</span>{"\n...\n\nQuestion: What GST rate applies to individual health insurance\npremiums in India?\n\n"}<span className="v">ANSWER:</span>{" <answer as of the reference date, or ABSTAIN>\n"}<span className="v">VALID_FROM:</span>{" <date from which this answer holds, or unknown>\n"}<span className="v">BASIS:</span>{" <document numbers used>"}</Code>
          </Card>
        </div></div>
      </div>)},
  // 10 --------------------------------------------------------------- baselines
  {title: "Baselines", steps: 0, notes: "Five modes on identical retrieval. Every baseline is told the reference date, so any failure at a past date is an evidence-selection failure, not a missing instruction. naive_trust and recency replicate the poisoning paper's conditions.",
    render: () => (
      <div className="slide">
        <Header kicker="Experimental setup" title="Five systems on the same retriever, the same models, the same reference date" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div style={{flex: 1.4}}><table className="t" style={{fontSize: 19}}>
            <thead><tr><th>Mode</th><th>What the generator receives</th><th>Replicates</th></tr></thead>
            <tbody>
              <tr><td>closed_book</td><td>no retrieval; the question and the reference date</td><td>parametric knowledge</td></tr>
              <tr><td>naive</td><td>hybrid top-5, raw documents (dates visible in the text)</td><td>standard RAG</td></tr>
              <tr><td>naive_trust</td><td>naive + “your answer must follow the information in the documents”</td><td>the poisoning paper's trust condition</td></tr>
              <tr><td>recency</td><td>top-5 ordered newest first by extracted anchor date; no status annotation</td><td>the poisoning paper's reranker</td></tr>
              <tr className="hl"><td>tva</td><td>full TVA-RAG: FUTURE dropped, validity rerank, status annotation, abstention path</td><td>ours</td></tr>
            </tbody></table></div>
          <div className="col" style={{flex: 1}}>
            <Card tag="generation"><p>Ollama, <b>temperature 0</b>, fixed seed, thinking disabled, 6,144-token context, ≤ 220 output tokens. Client retries with back-off; the grid runner resumes by record key.</p></Card>
            <Card tag="labelling"><p>Alias match settles <b>85.8 %</b> of answers; a cached LLM judge (qwen3.5:35b) settles the remaining <b>14.2 %</b>.</p></Card>
            <Card tag="hardware"><p>One NVIDIA RTX PRO 5000 (48 GB), 123 GB RAM. Python 3.14, PyTorch 2.14, sentence-transformers 6.2, rank_bm25, Ollama 0.31.</p></Card>
          </div>
        </div></div>
      </div>)},
  // 11 --------------------------------------------------------------- benchmark design
  {title: "TempRev · design", steps: 1, notes: "The poisoning paper's data is not public, so the project ships its own. Each reversal yields a stale and a current document, rendered with one of seven header date styles; seven stale documents are rendered undated to test abstention. Two corpus settings and two reference dates.",
    render: () => (
      <div className="slide">
        <Header kicker="The TempRev benchmark" title="71 real-world knowledge reversals, each with a dated stale and a dated current document" />
        <div className="body"><div className="svgwrap" style={{flex: 1}}><BenchBuild /></div>
          <Frag i={1}><div className="grid3">
            <Card><p><b>Item fields</b> question · old answer + aliases · new answer + aliases · old document (title, date, 40–90 word body) · new document (optional effective date, usually a supersession sentence) · change date · undated_old · t_past.</p></Card>
            <Card className="teal"><p><b>Two reference dates per reversal</b> t = 2026-01-01 (gold = current answer) and t_past = midpoint of the stale document's date and the change date (gold = historical answer).</p></Card>
            <Card className="rose"><p><b>Two corpus settings</b> <i>mixed</i> keeps all 162 documents; <i>stale-only</i> removes the 71 current documents, replicating the poisoning condition.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 12 --------------------------------------------------------------- benchmark composition
  {title: "TempRev · composition", steps: 0, notes: "Eight domains, heavy on software and world politics, with a deliberate Indian policy and law block. Most changes are recent, so the reversals are ones the models may or may not know. Note the caveat: team-authored from public facts, not independently audited.",
    render: () => (
      <div className="slide">
        <Header kicker="The TempRev benchmark" title="Eight domains, change dates from 2006 to September 2025" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div className="col" style={{flex: 1.1}}>
            <Card><HBar title="reversal items per domain (71 total)" rows={D.domains.map(([n, v]) => ({name: n, v, color: "#3dd6c6"}))} fmt={v => String(v)} max={22} labelW={230} star={false} width={700} /></Card>
            <Card className="gold"><p style={{fontSize: 16.5}}><b>Controls:</b> 20 stable facts (speed of light, capital of Australia, HTTP 404, Git's creator, Republic Day). <b>Caveat:</b> items were authored from well-documented public facts but are not independently audited.</p></Card>
          </div>
          <div className="col" style={{flex: 1.2}}>
            <Card><YearHist data={D.years} /></Card>
            <Card tag="examples"><p style={{fontSize: 16.5}}>{D.domains.map(([n, v, ex]) => <span key={n}><b>{n}:</b> {ex}. </span>)}</p></Card>
          </div>
        </div></div>
      </div>)},
  // 13 --------------------------------------------------------------- experimental grid
  {title: "Experimental grid", steps: 1, notes: "Four generators, two corpora, five modes in mixed and three in stale-only. 4,332 generations in total, zero failures. Metrics as defined in the problem statement. A pilot run exposed an over-abstention problem; the TVA instruction was clarified and rerun, baselines untouched, both versions reported.",
    render: () => (
      <div className="slide">
        <Header kicker="Experimental setup" title="4,332 generations across four models, two corpora and five modes" />
        <div className="body"><div className="svgwrap" style={{flex: 1}}><GridDiag /></div>
          <Frag i={1}><div className="grid3" style={{marginTop: 10}}>
            <Card tag="metrics"><p><b>Accuracy at t</b> (label = gold) · <b>stale-answer rate</b> (OLD when gold is NEW) · <b>flip rate</b> (among items correct closed-book at t = now, fraction answered OLD under a RAG mode) · <b>abstention rate</b> · <b>validity window</b> (VALID_FROM within 31 days / 1 year of the change).</p></Card>
            <Card tag="component metrics"><p>Extractor anchor accuracy · retrieval recall@5 of both item documents · detector pair precision and recall on on-topic retrieved pairs · status correctness of each item's own documents.</p></Card>
            <Card tag="prompt refinement" className="gold"><p>A pilot showed qwen2.5:7b abstaining on 15.5 % of present-date queries with a CURRENT document available, and the 3B model writing “CURRENT” as its answer. The TVA instruction was clarified and rerun; <b>baselines were not changed</b>, both TVA versions are reported.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 14 --------------------------------------------------------------- results: past date
  {title: "Results · past date", steps: 1, notes: "The decisive setting. Every baseline is told the date, yet naive RAG answers with the current fact in 182 of its 187 errors. Retrieval makes the small models worse than closed-book. TVA-RAG drops FUTURE documents and labels the rest: pooled 0.342 to 0.838, 0.972 with llama3.1:8b.",
    render: () => (
      <div className="slide">
        <Header kicker="Results · mixed corpus · t before the change (gold = historical answer)" title="Only TVA-RAG reliably answers as of a past date" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <Card style={{flex: 1.5}}><GroupedBars cats={M} series={accSeries(D.past)} title="accuracy at t_past · 71 questions per model" /></Card>
          <div className="col" style={{flex: 1}}>
            <Card className="violet"><div className="big grad">0.838<small>pooled · vs 0.342 naive</small></div><p style={{marginTop: 10}}>closed-book 0.549 · naive + trust 0.254 · recency 0.370. TVA-RAG abstains on 7.4 %, mostly qwen2.5:7b (0.169) and qwen3.5:35b (0.127).</p></Card>
            <Card><p><b>Retrieval makes small models worse than no retrieval:</b> llama3.2:3b 0.465 → 0.085, qwen2.5:7b 0.394 → 0.028. Only the 35B model partially reasons about dates by itself (0.817).</p></Card>
            <Frag i={1}><Card className="rose"><p><b>182 of naive RAG's 187 errors are the current fact.</b> This is an evidence-selection failure, not a prompt-reading failure, so it has to be solved before generation. FUTURE filtering plus status labels add +50 points pooled.</p></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 15 --------------------------------------------------------------- results: present date
  {title: "Results · present date", steps: 1, notes: "With the current document present, naive RAG is already near the ceiling: modern instruction-tuned models prefer the document that answers most directly, and most current documents carry a supersession sentence. TVA-RAG matches it for two models; the pooled gap is qwen2.5:7b's abstentions. The recency reranker is worse than naive RAG for three models.",
    render: () => (
      <div className="slide">
        <Header kicker="Results · mixed corpus · t = 2026-01-01 (gold = current answer)" title="With the current document available, naive RAG is near the ceiling; TVA-RAG matches it and lowers the stale-answer rate" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <Card style={{flex: 1.3}}><GroupedBars cats={M} series={accSeries(D.now)} title="accuracy at t = 2026-01-01 · 71 questions per model" /></Card>
          <div className="col" style={{flex: 1.1, justifyContent: "center"}}>
            <table className="t c"><thead><tr><th>Model</th><th>Naive</th><th>Recency</th><th>TVA-RAG</th><th>TVA abst.</th></tr></thead><tbody>
              {M.map(m => { const r = D.now[m]; return <tr key={m}><td>{m}</td><td>{r.acc[1].toFixed(3)} <span className="mono" style={{fontSize: 13}}>({r.stale[1].toFixed(3)})</span></td><td>{r.acc[3].toFixed(3)} <span className="mono" style={{fontSize: 13}}>({r.stale[3].toFixed(3)})</span></td><td className="vio">{r.acc[4].toFixed(3)} <span className="mono" style={{fontSize: 13, color: "var(--muted)"}}>({r.stale[4].toFixed(3)})</span></td><td>{r.abst.toFixed(3)}</td></tr>; })}
              <tr className="hl"><td>Pooled</td><td>0.986 (0.011)</td><td>0.947 (0.053)</td><td>0.940 (0.014)</td><td>0.046</td></tr>
            </tbody></table>
            <p className="sub" style={{fontSize: 15, margin: 0}}>accuracy (stale-answer rate in brackets)</p>
          </div>
        </div>
          <Frag i={1}><div className="grid2" style={{marginTop: 20}}>
            <Card className="gold"><p><b>Recency reranker is worse than naive RAG for three of four models</b> (pooled stale rate 0.053 vs 0.011): newest-first ordering surfaces recent documents about <i>other</i> topics and the model over-weights “Document 1”.</p></Card>
            <Card><p><b>The pooled TVA-RAG gap (4.6 points) is almost entirely qwen2.5:7b</b>: 10 of 71 abstentions, all with a CURRENT document present. TVA-RAG has the lowest stale-answer rate of the retrieval modes for three models.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 16 --------------------------------------------------------------- results: stale-only
  {title: "Results · poisoning", steps: 1, notes: "The poisoning replication: only the stale document exists. Flip rate = among items answered correctly closed-book, fraction turned into the stale answer. Naive flips are higher than in the paper because TempRev's stale documents answer the question directly and the models are small. TVA-RAG's age signalling converts most flips into abstentions or correct parametric answers.",
    render: () => (
      <div className="slide">
        <Header kicker="Results · stale-only corpus · t = 2026-01-01" title="When only stale evidence exists, TVA-RAG stops the model from confidently repeating it" sub="Flip rate: among questions the model answered correctly closed-book, the fraction turned into the stale answer by the stale document." />
        <div className="body"><div className="row" style={{flex: 1}}>
          <Card style={{flex: 1.2}}><GroupedBars cats={M} series={[{key: "naive", label: "Naive RAG", color: D.colors.naive, values: M.map(m => D.flip[m].naive)}, {key: "trust", label: "Naive + trust", color: D.colors.naive_trust, values: M.map(m => D.flip[m].trust)}, {key: "tva", label: "TVA-RAG (ours)", color: D.colors.tva, values: M.map(m => D.flip[m].tva)}]} title="stale-document flip rate · lower is better" /></Card>
          <div className="col" style={{flex: 1}}>
            <Card tag="what happens to TVA-RAG's closed-book-correct items"><Stacked rows={M.map(m => ({name: m, parts: [{v: D.flip[m].tva, color: D.status.SUPERSEDED}, {v: D.flip[m].abst, color: D.status.UNVERIFIED}, {v: D.flip[m].still, color: D.status.CURRENT}]}))} legend={[{label: "flipped to stale answer", color: D.status.SUPERSEDED}, {label: "abstained", color: D.status.UNVERIFIED}, {label: "still correct", color: D.status.CURRENT}]} width={720} barH={30} labelW={130} /></Card>
            <Frag i={1}><Card className="violet"><p><b>Flip rate falls by 26–76 points.</b> qwen3.5:35b keeps 60 % of its correct closed-book answers (vs 4 % with naive RAG) and abstains on another 26 %. Pooled stale-only accuracy 0.102 → 0.303; stale-answer rate 0.856 → 0.437. In the mixed setting every RAG mode flips below 0.10 and TVA-RAG has <b>zero</b> flips for llama3.1:8b and qwen3.5:35b.</p></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 17 --------------------------------------------------------------- validity window, controls, latency
  {title: "Validity window · controls · cost", steps: 1, notes: "The outputs no baseline produces: a validity window that matches the true change date within a month for 72 to 96 percent of items. No regression on the 20 stable facts. Latency: a quarter second of extra generation plus a detection cost that is cached per question.",
    render: () => (
      <div className="slide">
        <Header kicker="Results · what TVA-RAG adds that no baseline has" title="A validity window at month-level accuracy, no regression on stable facts, 0.25 s extra" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <Card style={{flex: 1.2}} tag="VALID_FROM at the present date"><GroupedBars cats={M} series={[{key: "stated", label: "VALID_FROM stated", color: "#94a3b8", values: M.map(m => D.validity[m][0])}, {key: "d31", label: "within 31 days of the change", color: "#c084fc", values: M.map(m => D.validity[m][1])}, {key: "year", label: "within 1 year", color: "#3dd6c6", values: M.map(m => D.validity[m][2])}]} hl="d31" title="share of the 71 present-date reversal questions" /></Card>
          <div className="col" style={{flex: 1}}>
            <Card className="teal"><div className="big grad">1.000</div><p>control accuracy on 20 stable facts for <b>every retrieval mode and every model</b> (closed-book 0.85–1.00). TVA-RAG causes no regression.</p></Card>
            <Card tag="mean latency per query · mixed corpus"><HBar rows={D.latency.map(([n, v]) => ({name: n, v, color: n.startsWith("TVA") ? "#c084fc" : "#60a5fa"}))} fmt={v => v.toFixed(2) + " s"} max={0.9} star={false} labelW={210} barH={24} width={700} /><p style={{fontSize: 16, marginTop: 2}}>Uncached detection ≈ 1.7 s (qwen3.5:35b) or 0.06 s (NLI); cached per question, shared across models.</p></Card>
            <Frag i={1}><Card><p><b>Month-level validity:</b> VALID_FROM is within 31 days of the true change date for 87–96 % of items on three models; qwen2.5:7b trails at 72 %.</p></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 18 --------------------------------------------------------------- qualitative example
  {title: "Qualitative example", steps: 0, notes: "One question, one model, two dates, two systems. Naive RAG gives the same answer regardless of the date and is wrong in the past. TVA-RAG returns the right answer for each date, with the date from which it holds.",
    render: () => (
      <div className="slide">
        <Header kicker="Qualitative example · llama3.1:8b" title="Same question, same documents, two reference dates" sub="What GST rate applies to individual health insurance premiums in India?" />
        <div className="body"><table className="t" style={{fontSize: 20}}>
          <thead><tr><th>Mode</th><th>Reference date</th><th>Output</th><th></th></tr></thead>
          <tbody>
            <tr><td>Naive RAG</td><td className="mono">2026-01-01</td><td>“As per Document 2, dated September 22, 2025, individual health insurance policies are exempt from GST. ANSWER: Exempt.”</td><td className="good">correct</td></tr>
            <tr><td>Naive RAG</td><td className="mono">2024-11-28</td><td>“As per Document 2 dated September 22, 2025, individual health insurance policies are <b>now exempt</b> from GST. ANSWER: Exempt.”</td><td className="bad">wrong: the exemption was ten months in the future</td></tr>
            <tr className="hl"><td>TVA-RAG</td><td className="mono">2026-01-01</td><td className="mono">ANSWER: Exempt · VALID_FROM: 2025-09-22 · BASIS: Document 1</td><td className="good">correct, with the validity window</td></tr>
            <tr className="hl"><td>TVA-RAG</td><td className="mono">2024-11-28</td><td className="mono">ANSWER: 18% · VALID_FROM: 2024-02-05 · BASIS: Document 1</td><td className="good">correct: the 2025 document was FUTURE and dropped</td></tr>
          </tbody></table>
          <div className="grid3" style={{marginTop: 28}}>
            <Card><p>The naive prompt contains the reference date too. The model reads the document's date and <b>still</b> treats it as applicable: date-reading is not the bottleneck.</p></Card>
            <Card className="violet"><p>TVA-RAG never shows the generator a document dated after t. The answer changes with t because the <b>evidence</b> changes with t.</p></Card>
            <Card className="teal"><p>The Streamlit demo (<span className="mono">app.py</span>) runs naive and TVA-RAG side by side on the same retrieved documents for any question, date and model.</p></Card>
          </div>
        </div>
      </div>)},
  // 19 --------------------------------------------------------------- component evaluation
  {title: "Component evaluation", steps: 1, notes: "Each component measured on its own. Retrieval is not the bottleneck: both conflicting documents are nearly always in the top five, which is exactly what makes stale evidence dangerous. Detector precision is high by design; recall is where the cost is paid.",
    render: () => (
      <div className="slide">
        <Header kicker="Component evaluation" title="Each stage measured on its own" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div style={{flex: 1.5}}><table className="t" style={{fontSize: 19}}>
            <thead><tr><th>Component</th><th>Metric</th><th>Value</th><th>n</th></tr></thead>
            <tbody>{D.components.map((r, i) => <tr key={i}><td>{r[0]}</td><td>{r[1]}</td><td className="mono good">{r[2]}</td><td className="mono">{r[3]}</td></tr>)}</tbody></table></div>
          <div className="col" style={{flex: 1}}>
            <Card className="accent"><p><b>Retrieval is not the bottleneck.</b> Hybrid recall@5 of <i>both</i> item documents is 0.986 (dense alone 1.000). The stale document is almost always in the context, which is exactly what makes it a problem.</p></Card>
            <Frag i={1}><Card><p><b>Status assignment</b> is correct for 84.8 % of the items' own documents at t = 2026-01-01. The misses are mostly undetected conflicts, which leave both documents UNCONFLICTED and degrade TVA-RAG to naive behaviour for that query.</p></Card></Frag>
            <Frag i={1}><Card className="imgcard" style={{flex: 1}}><img src="fig/status_distribution.png" alt="Validity status assigned to each item's documents" /></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 20 --------------------------------------------------------------- detector ablation
  {title: "Detector ablation", steps: 1, notes: "Three detector variants on on-topic retrieved pairs. Precision was chosen over recall deliberately: a false conflict can mark the correct document SUPERSEDED, whereas a missed conflict only degrades to naive behaviour. The NLI model alone was unusable; the 8B model judged main and master to be the same answer.",
    render: () => (
      <div className="slide">
        <Header kicker="Ablation · conflict detector variants" title="Precision over recall: a false conflict hurts more than a missed one" sub="On-topic retrieved pairs, 71 present-date questions." />
        <div className="body"><div className="row" style={{flex: 1}}>
          <Card style={{flex: 1.3}}><GroupedBars cats={["Precision", "Recall", "F1"]} series={D.detectors.map(d => ({key: d[0], label: d[0], color: d[5], values: [d[1], d[2], d[3]]}))} hl={D.detectors[0][0]} title="detector quality on on-topic pairs" /></Card>
          <div className="col" style={{flex: 1}}>
            <table className="t c"><thead><tr><th>Detector</th><th>P</th><th>R</th><th>F1</th><th>Cost / query</th></tr></thead><tbody>
              {D.detectors.map((d, i) => <tr key={d[0]} className={i === 0 ? "hl" : ""}><td>{d[0]}</td><td>{d[1].toFixed(3)}</td><td>{d[2].toFixed(3)}</td><td>{d[3].toFixed(3)}</td><td className="mono">{d[4]}</td></tr>)}
            </tbody></table>
            <Frag i={1}><Card className="rose"><p><b>Why precision:</b> a false conflict can mark the <i>correct</i> document SUPERSEDED, whereas a missed conflict only degrades TVA-RAG to naive behaviour for that query.</p></Card></Frag>
            <Frag i={1}><Card><p><b>NLI alone was unusable:</b> median contradiction probability 0.99 on <i>unrelated</i> pairs and 0.003 on a genuine mammography 50-vs-40 conflict. It works only behind the similarity gate. <b>llama3.1:8b</b> extracted claims adequately but judged “main” and “master” to be the same answer.</p></Card></Frag>
          </div>
        </div></div>
      </div>)},
  // 21 --------------------------------------------------------------- prompt ablation + error analysis
  {title: "Prompt ablation · errors", steps: 1, notes: "Clarifying the abstention rule helped llama3.1:8b substantially at the past date and barely moved the others; qwen2.5:7b's over-abstention is a model trait. Then the error analysis, grouped by setting.",
    render: () => (
      <div className="slide">
        <Header kicker="Prompt ablation and error analysis" title="Where TVA-RAG still fails, and why" />
        <div className="body"><div className="row" style={{flex: 1}}>
          <div className="col" style={{flex: 1}}>
            <Card tag="pilot vs final TVA instruction · accuracy"><table className="t c" style={{fontSize: 16.5}}>
              <thead><tr><th>Setting</th>{M.map(m => <th key={m}>{m}</th>)}</tr></thead>
              <tbody>{D.promptAbl.map((r, i) => <tr key={i} className={r[0].endsWith("final") ? "hl" : ""}><td>{r[0]}</td>{r.slice(1).map((v, k) => <td key={k} className="mono">{v}</td>)}</tr>)}</tbody></table>
              <p style={{fontSize: 16.5}}>Clarifying the abstention rule lifted llama3.1:8b at the past date from 0.817 to 0.972 and barely moved the others; <b>qwen2.5:7b's over-abstention is a model trait</b>. Baselines were not rerun.</p></Card>
          </div>
          <Frag i={1} style={{flex: 1.15}}><Card tag="error analysis" style={{height: "100%"}}>
            <ul className="list small">
              <li><b>TVA-RAG, present date: 4 non-abstaining errors of 284.</b> llama3.2:3b follows its parametric prior over a CURRENT document three times (triple talaq, 5G, US President); qwen2.5:7b once echoed the status word (“Croatian kuna (SUPERSEDED)”).</li>
              <li><b>qwen2.5:7b abstains on 10 of 71</b> present-date questions despite a CURRENT document; seven are software-lifecycle yes/no questions. A deterministic post-check that overrides ABSTAIN when a CURRENT document carries a claim would remove most.</li>
              <li><b>TVA-RAG, past date: 46 errors of 284.</b> llama3.2:3b leaks the current fact from memory 15 times after the current document is dropped as FUTURE; 43 % of the 21 abstentions are on the undated items, where abstaining is the designed behaviour.</li>
              <li><b>Naive RAG, past date: 187 errors,</b> 182 of them the current fact. <b>Recency reranker:</b> all 18 present-date errors are stale answers caused by date-only ordering.</li>
              <li><b>Undated stale documents (7 items):</b> naive 1.000 vs TVA 0.821 with 10.7 % abstentions: the price of the abstention rule on a benchmark where the undated document is always the stale one.</li>
            </ul></Card></Frag>
        </div></div>
      </div>)},
  // 22 --------------------------------------------------------------- discussion
  {title: "Discussion", steps: 1, notes: "Three regimes. With the current document present, accuracy is saturated and TVA-RAG adds the validity window. At a past date, no baseline copes and FUTURE filtering is decisive. With only stale evidence, nobody can produce the current answer from the documents; TVA-RAG's job is to stop confident repetition.",
    render: () => (
      <div className="slide">
        <Header kicker="Discussion" title="Three regimes, three different jobs for the same mechanism" />
        <div className="body"><div className="grid3" style={{flex: 1}}>
          <Card tag="regime 1 · current doc present, t = now" title="Accuracy is saturated" className="teal"><p>Modern instruction-tuned models already pick the document that answers most directly (naive 0.986 pooled). TVA-RAG matches it for two models, <b>lowers the stale-answer rate</b>, and adds a validity window. The remaining gap is one model's over-abstention.</p></Card>
          <Card tag="regime 2 · t before the change" title="FUTURE filtering is decisive" className="violet"><p>No baseline copes, including the largest model with the date in its prompt. Dropping documents dated after t and labelling the rest adds <b>+50 points pooled</b> (0.342 → 0.838) and reaches 0.972 with llama3.1:8b.</p></Card>
          <Card tag="regime 3 · only stale evidence" title="Stop confident repetition" className="rose"><p>No retrieval system can produce the current answer from documents that do not contain it. TVA-RAG's contribution is to <b>convert flips into abstentions or correct parametric answers</b>: flip rate 0.67–0.93 → 0.15–0.42.</p></Card>
        </div>
          <Frag i={1}><div className="grid3" style={{marginTop: 22}}>
            <Card><p><b>Order vs interpretation.</b> The recency reranker changes order but not interpretation, and date-only ordering surfaces off-topic recent documents. TVA-RAG's labels are attached to the documents and are robust to ordering.</p></Card>
            <Card><p><b>Abstention is model-dependent</b> (1.4 % for three models, 14 % for qwen2.5:7b) and should be calibrated per model or implemented as a deterministic post-check on the detector's claims.</p></Card>
            <Card><p><b>Cost.</b> About 0.25 s of extra generation plus a detection cost cached per question. The NLI detector is 30× cheaper at 1.2 F1 points less, so the trade-off is tunable.</p></Card>
          </div></Frag>
        </div>
      </div>)},
  // 23 --------------------------------------------------------------- contributions
  {title: "Contributions", steps: 4, notes: "Summarise the four deliverables: the benchmark, the system, the controlled evaluation and the component study.",
    render: () => (
      <div className="slide">
        <Header kicker="Contributions" title="What this project delivers" />
        <div className="body"><div className="col" style={{gap: 24}}>
          <Frag i={1}><Step n="1" title="TempRev: a benchmark for stale evidence in RAG">71 verified knowledge reversals with dated stale and current documents, a two-reference-date protocol, seven undated-document cases for abstention testing and 20 control facts. The poisoning paper's data is not public; this is.</Step></Frag>
          <Frag i={2}><Step n="2" title="A complete TVA-RAG implementation">Regex temporal extractor, hybrid BM25 + dense retrieval, question-conditioned claim-level conflict detector, pairwise validity status, validity-aware reranking, validity prompting and abstention, plus a Streamlit demo. Pure Python on local Ollama models.</Step></Frag>
          <Frag i={3}><Step n="3" title="A controlled evaluation on four open models">Against closed-book, naive RAG, naive RAG with a trust instruction and the recency reranker, in a mixed and a stale-only corpus: 4,332 generations. As-of accuracy 0.34 → 0.84 pooled, flip rate down 26–76 points, control accuracy unchanged at 1.000.</Step></Frag>
          <Frag i={4}><Step n="4" title="Component evaluation, ablations and error analysis">Extractor, retriever and three detector variants measured separately; a prompt ablation with both versions reported; an error analysis that names the two residual weaknesses (model-dependent over-abstention, detector cost) and their remedies.</Step></Frag>
        </div></div>
      </div>)},
  // 24 --------------------------------------------------------------- limitations & future work
  {title: "Limitations & future work", steps: 0, notes: "Be upfront: a small team-authored benchmark with regular headers makes extraction and detection easier than in the wild; single deterministic runs; part of the labels from an LLM judge; a 35B detector. Then the concrete next steps.",
    render: () => (
      <div className="slide">
        <Header kicker="Limitations and next steps" title="Where the evidence stops" />
        <div className="body"><div className="grid2" style={{flex: 1}}>
          <Card tag="limitations" title="Scope of the claims">
            <ul className="list">
              <li>71 team-authored reversals: confidence intervals of roughly <b>±10 points</b> per model.</li>
              <li>Regular header templates and explicit supersession sentences make extractor and detector numbers <b>optimistic</b> relative to documents in the wild.</li>
              <li>Single deterministic runs; 14 % of labels from an LLM judge without a human-labelled subset.</li>
              <li>The deployed detector is a 35B model; English only, short documents, single-hop questions.</li>
              <li>The benchmark's present is fixed at 2026-01-01; items are not independently audited.</li>
            </ul></Card>
          <Card tag="future work" title="Natural extensions" className="teal">
            <ul className="list">
              <li>A <b>deterministic abstention post-check</b> calibrated per model, overriding ABSTAIN when a CURRENT document carries a claim.</li>
              <li><b>Distil</b> the claim-equivalence judgement into a small cross-encoder from the cached 35B decisions.</li>
              <li>A <b>learned validity function</b> in place of the fixed 1.0 / 0.6 / 0.4 / 0.25 weights.</li>
              <li>An <b>Indian citizen-service</b> extension over scheme circulars and GST notifications in Hindi and Telugu.</li>
              <li>A larger, audited benchmark with multi-step reversals and long documents; integration with retrieval-state confidence gating.</li>
            </ul></Card>
        </div></div>
      </div>)},
  // 25 --------------------------------------------------------------- references
  {title: "References", steps: 0, notes: "",
    render: () => (
      <div className="slide">
        <Header kicker="References" title="Key sources" />
        <div className="body twocol-refs" style={{display: "block"}}>
          {[
            "Stale-Document Poisoning: When Outdated Retrieval Overrides Correct Model Answers. <i>arXiv:2609.31342</i>, 2026.",
            "ConflictRAG: Detecting and Resolving Knowledge Conflicts in RAG. <i>arXiv:2605.17301</i>, 2026.",
            "EvoTrustRAG: Evolution-Aware Conflict Attribution and Evidence Handling for Reliable RAG. <i>arXiv:2608.07933</i>, 2026.",
            "ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form RAG. <i>arXiv:2604.18362</i>, 2026.",
            "DRAGged into Conflicts: Detecting and Addressing Conflicting Sources in Search-Augmented LLMs. <i>arXiv:2506.08500</i>, 2025.",
            "When Confidence Takes the Wrong Path: Diagnosing Retrieval-State Lock-In in RAG. <i>arXiv:2606.22728</i>, 2026.",
            "Know Before You Fetch: Calibrated Retrieval-Budget Allocation for RAG. <i>arXiv:2606.29959</i>, 2026.",
            "Retrieval as a Decision: Training-Free Adaptive Gating for Efficient RAG (TARG). <i>arXiv:2511.09803</i>, 2025.",
            "When Retrieval Succeeds and Fails: Rethinking RAG for LLMs. <i>arXiv:2510.09106</i>, 2025.",
            "Singh et al. (2025). Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG. <i>arXiv:2501.09136</i>.",
            "Chen et al. (2021). A Dataset for Answering Time-Sensitive Questions (TimeQA). <i>NeurIPS Datasets and Benchmarks</i>.",
            "Dhingra et al. (2022). Time-Aware Language Models as Temporal Knowledge Bases (TempLAMA). <i>TACL</i>.",
            "Zhang, Choi (2021). SituatedQA: Incorporating Extra-Linguistic Contexts into QA. <i>EMNLP</i>.",
            "Xiao et al. (2023). C-Pack: Packaged Resources To Advance General Chinese Embedding (bge). <i>arXiv</i>.",
            "Cormack, Clarke, Buettcher (2009). Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods. <i>SIGIR</i>.",
            "Robertson, Zaragoza (2009). The Probabilistic Relevance Framework: BM25 and Beyond. <i>Foundations and Trends in IR</i>.",
            "He et al. (2023). DeBERTaV3. <i>ICLR</i>.",
            "Es et al. (2024). RAGAS: Automated Evaluation of Retrieval Augmented Generation. <i>EACL demo</i>.",
          ].map((r, i) => <p key={i} className="ref" dangerouslySetInnerHTML={{__html: r}} />)}
        </div>
      </div>)},
  // 26 --------------------------------------------------------------- end
  {title: "Thank you", steps: 0, notes: "",
    render: () => (
      <div className="slide title-slide">
        <h1 style={{fontSize: 96}}>Thank <span className="grad">you</span></h1>
        <div className="title-meta" style={{marginTop: 48}}>
          <a href="https://github.com/Yeluri-Nakshatra/Temporal-Validity-Aware-RAG" target="_blank" rel="noopener" style={{textDecoration: "none"}}><Pill kind="acc">github.com/Yeluri-Nakshatra/Temporal-Validity-Aware-RAG</Pill></a>
        </div>
      </div>)},
];
