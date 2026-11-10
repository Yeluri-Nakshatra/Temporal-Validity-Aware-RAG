// Hand-built SVG diagrams for the deck.
// Palette: dark (deck) by default; window.THEME = "light" switches to a print palette (used by figure.html).
const LIGHT = (window.THEME === "light");
const INK = LIGHT ? "#0f172a" : "#e9edf9", MUTED = LIGHT ? "#475569" : "#9ba6c9", DIM = LIGHT ? "#64748b" : "#6b7598",
  ACC = LIGHT ? "#4f5bd5" : "#8b97ff", ACC2 = LIGHT ? "#0f8f85" : "#3dd6c6", GOLD = LIGHT ? "#c77d0a" : "#ffc46b",
  ROSE = LIGHT ? "#d6336c" : "#ff6f9c", VIO = LIGHT ? "#7e22ce" : "#c084fc", GREEN = LIGHT ? "#15803d" : "#4ade80", GREY = LIGHT ? "#64748b" : "#94a3b8";
const ST = {CURRENT: GREEN, SUPERSEDED: LIGHT ? "#be123c" : "#fb7185", UNVERIFIED: GOLD, FUTURE: GREY, UNCONFLICTED: ACC2};
// translucent white in the dark theme becomes translucent ink in the light theme
const wa = (a) => LIGHT ? `rgba(15,23,42,${Math.min(1, a * 1.6).toFixed(3)})` : `rgba(255,255,255,${a})`;
const hexa = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };

// ---------- primitives ----------
function Box({x, y, w, h, title, lines = [], color = ACC, fill, bold = false, titleSize = 16, lineSize = 12.5, dashed = false, opacity = 1}) {
  const lh = lineSize + 5; const blockH = titleSize + (lines.length ? 6 + lines.length * lh : 0);
  const startY = y + h / 2 - blockH / 2 + titleSize - 2;
  return (
    <g opacity={opacity} style={{transition: "opacity .4s"}}>
      <rect x={x} y={y} width={w} height={h} rx="14" fill={fill || hexa(color, LIGHT ? .08 : .12)} stroke={color} strokeWidth={bold ? 2.2 : 1.4} strokeDasharray={dashed ? "6 5" : undefined} />
      <text x={x + w / 2} y={startY} textAnchor="middle" fill={INK} fontSize={titleSize} fontWeight="700">{title}</text>
      {lines.map((l, i) => <text key={i} x={x + w / 2} y={startY + 6 + (i + 1) * lh} textAnchor="middle" fill={MUTED} fontSize={lineSize}>{l}</text>)}
    </g>
  );
}
function Head({x, y, ang, color}) {
  const hx = x - Math.cos(ang) * 10, hy = y - Math.sin(ang) * 10;
  return <polygon points={`${x},${y} ${hx + Math.sin(ang) * 6},${hy - Math.cos(ang) * 6} ${hx - Math.sin(ang) * 6},${hy + Math.cos(ang) * 6}`} fill={color} />;
}
function Arrow({x1, y1, x2, y2, color = DIM, flow = false, label, lx, ly, width = 2.2, opacity = 1}) {
  const ang = Math.atan2(y2 - y1, x2 - x1); const hx = x2 - Math.cos(ang) * 9, hy = y2 - Math.sin(ang) * 9;
  return (<g opacity={opacity} style={{transition: "opacity .4s"}}>
    <line x1={x1} y1={y1} x2={hx} y2={hy} stroke={color} strokeWidth={width} className={flow ? "flow" : ""} />
    <Head x={x2} y={y2} ang={ang} color={color} />
    {label && <text x={lx ?? (x1 + x2) / 2} y={ly ?? ((y1 + y2) / 2 - 8)} textAnchor="middle" fill={MUTED} fontSize="12" className="mono">{label}</text>}
  </g>);
}
function Elbow({pts, color = DIM, label, lx, ly, flow = false, opacity = 1}) {
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join(" ");
  const [ax, ay] = pts[pts.length - 1], [bx, by] = pts[pts.length - 2];
  return (<g opacity={opacity} style={{transition: "opacity .4s"}}>
    <path d={d} fill="none" stroke={color} strokeWidth="2.2" className={flow ? "flow" : ""} />
    <Head x={ax} y={ay} ang={Math.atan2(ay - by, ax - bx)} color={color} />
    {label && <text x={lx} y={ly} textAnchor="middle" fill={MUTED} fontSize="12" className="mono">{label}</text>}
  </g>);
}
function Diamond({x, y, w, h, text, lines = [], color = GOLD}) {
  const pts = `${x + w / 2},${y} ${x + w},${y + h / 2} ${x + w / 2},${y + h} ${x},${y + h / 2}`;
  const all = [text, ...lines]; const lh = 16; const sy = y + h / 2 - ((all.length - 1) * lh) / 2 + 5;
  return (<g><polygon points={pts} fill={hexa(color, .1)} stroke={color} strokeWidth="1.5" />
    {all.map((t, i) => <text key={i} x={x + w / 2} y={sy + i * lh} textAnchor="middle" fill={INK} fontSize={i ? 12.5 : 13.5} fontWeight={i ? 500 : 700}>{t}</text>)}</g>);
}
function Chip({x, y, text, color, size = 13}) {
  const w = text.length * size * 0.62 + 22;
  return (<g><rect x={x} y={y - 15} width={w} height={24} rx="12" fill={hexa(color, .16)} stroke={color} />
    <text x={x + w / 2} y={y + 2} textAnchor="middle" fill={color} fontSize={size} fontWeight="700" className="mono">{text}</text></g>);
}

// ---------- Slide: motivation — two documents, one retriever, the wrong answer ----------
function DocCard({x, y, w, h, tag, color, title, body, body2}) {
  return (<g>
    <rect x={x} y={y} width={w} height={h} rx="16" fill={hexa(color, .07)} stroke={hexa(color, .55)} />
    <text x={x + 24} y={y + 30} fill={color} fontSize="13" className="mono" fontWeight="700">{tag}</text>
    <text x={x + 24} y={y + 60} fill={INK} fontSize="18" fontWeight="700">{title}</text>
    <text x={x + 24} y={y + 88} fill={MUTED} fontSize="15.5" fontStyle="italic">{body}</text>
    {body2 && <text x={x + 24} y={y + 110} fill={MUTED} fontSize="15.5" fontStyle="italic">{body2}</text>}
  </g>);
}
function StaleProblem() {
  return (
    <svg viewBox="0 0 1400 450">
      {/* question */}
      <rect x="20" y="20" width="540" height="86" rx="16" fill={hexa(ACC, .1)} stroke={ACC} strokeWidth="1.5" />
      <text x="44" y="52" fill={INK} fontSize="17" fontWeight="600">q: What GST rate applies to individual health insurance premiums in India?</text>
      <text x="44" y="82" fill={ACC2} fontSize="14" className="mono">reference date t = 2024-11-28</text>
      {/* knowledge base */}
      <text x="20" y="134" fill={DIM} fontSize="13" className="mono" fontWeight="700">KNOWLEDGE BASE · never cleaned</text>
      <DocCard x={20} y={146} w={540} h={128} tag="DOC A · Published: 5 February 2024" color={GOLD} title="GST on insurance premiums" body="“Premiums for health insurance policies attract GST at 18 percent.”" />
      <DocCard x={20} y={300} w={540} h={128} tag="DOC B · Date: 2025-09-22" color={GREEN} title="GST exemption on health insurance" body="“Individual health insurance policies are now exempt from GST.”" />
      {/* retriever */}
      <path d="M560 210 C 610 210, 610 282, 640 282" fill="none" stroke={DIM} strokeWidth="2.5" className="flow" />
      <path d="M560 364 C 610 364, 610 282, 640 282" fill="none" stroke={DIM} strokeWidth="2.5" className="flow" />
      <Box x={640} y={237} w={210} h={92} title="hybrid retriever" lines={["BM25 + dense · top-5", "returns both documents"]} color={ACC2} />
      <Arrow x1={850} y1={283} x2={900} y2={283} flow />
      <Box x={900} y={237} w={200} h={92} title="generator" lines={["naive RAG prompt:", "“use the documents”"]} color={ACC} />
      <Arrow x1={1100} y1={283} x2={1128} y2={283} flow />
      {/* output */}
      <rect x="1130" y="190" width="250" height="190" rx="16" fill={hexa(ROSE, .07)} stroke={hexa(ROSE, .6)} />
      <text x="1152" y="220" fill={ROSE} fontSize="13" className="mono" fontWeight="700">OUTPUT · llama3.1:8b</text>
      <text x="1152" y="250" fill={MUTED} fontSize="15" fontStyle="italic">“…individual health insurance</text>
      <text x="1152" y="272" fill={MUTED} fontSize="15" fontStyle="italic">policies are now exempt</text>
      <text x="1152" y="294" fill={MUTED} fontSize="15" fontStyle="italic">from GST.”</text>
      <text x="1152" y="330" fill={ROSE} fontSize="20" fontWeight="800" className="mono">ANSWER: Exempt ✗</text>
      <text x="1152" y="360" fill={MUTED} fontSize="13.5">exemption still ten months away</text>
      {/* caption */}
      <text x="700" y="438" textAnchor="middle" fill={MUTED} fontSize="17">Similar text, contradictory claims, different dates: nothing in the pipeline says <tspan fill={INK} fontWeight="700">which document applies at t</tspan>.</text>
    </svg>
  );
}

// ---------- Slide: key idea — validity is a function of (document, t) ----------
function TimelineIdea({step = 0}) {
  const a = new Date("2023-09-01").getTime(), b = new Date("2026-05-01").getTime();
  const toX = (iso) => 120 + ((new Date(iso).getTime() - a) / (b - a)) * 1180;
  const AX = 270; const t = step >= 2 ? "2024-11-28" : "2026-01-01"; const tx = toX(t);
  const docs = [
    {id: "A", date: "2024-02-05", title: "GST on insurance premiums", claim: "18%", color: GOLD},
    {id: "B", date: "2025-09-22", title: "GST exemption on health insurance", claim: "Exempt", color: GREEN},
  ];
  const status = (d) => {
    if (step === 0) return null;
    if (new Date(d.date) > new Date(t)) return "FUTURE";
    if (d.id === "A" && step === 1) return "SUPERSEDED";
    return "CURRENT";
  };
  const captions = [
    "Two documents answer the same question; only their dates differ. Which one is the answer depends on when you ask.",
    "At t = 2026-01-01: B is the latest valid evidence → CURRENT. A conflicts with B and is older → SUPERSEDED on 2025-09-22 by B.",
    "At t = 2024-11-28: B is dated after t → FUTURE and dropped from the context. A is now CURRENT. Status is a function of (document, t), not of the document alone.",
  ];
  const out = step === 1 ? "ANSWER: Exempt · VALID_FROM: 2025-09-22 · BASIS: B" : step === 2 ? "ANSWER: 18% · VALID_FROM: 2024-02-05 · BASIS: A" : null;
  return (
    <svg viewBox="0 0 1400 470">
      {/* future shading */}
      {step >= 1 && <g opacity=".9"><rect x={tx} y={AX - 150} width={1310 - tx} height={210} fill={wa(.03)} />
        <text x={tx + 12} y={AX + 100} fill={DIM} fontSize="12" className="mono">AFTER t</text></g>}
      {/* axis */}
      <line x1="100" x2="1310" y1={AX} y2={AX} stroke={wa(.35)} strokeWidth="2" />
      <Head x={1318} y={AX} ang={0} color={wa(.35)} />
      {["2024-01-01", "2025-01-01", "2026-01-01"].map(d => <g key={d}><line x1={toX(d)} x2={toX(d)} y1={AX - 8} y2={AX + 8} stroke={wa(.35)} />
        <text x={toX(d)} y={AX + 30} textAnchor="middle" fill={DIM} fontSize="13" className="mono">{d.slice(0, 4)}</text></g>)}
      {/* docs */}
      {docs.map(d => { const x = toX(d.date); const s = status(d); const col = s ? ST[s] : d.color; const dropped = s === "FUTURE"; return (
        <g key={d.id} opacity={dropped ? .55 : 1} style={{transition: "opacity .4s"}}>
          <line x1={x} x2={x} y1={AX - 60} y2={AX} stroke={col} strokeWidth="2" strokeDasharray={dropped ? "5 5" : undefined} />
          <circle cx={x} cy={AX} r="8" fill={col} />
          <rect x={x - 150} y={AX - 150} width="300" height="90" rx="14" fill={hexa(col, .1)} stroke={col} strokeWidth="1.6" strokeDasharray={dropped ? "6 5" : undefined} />
          <text x={x - 134} y={AX - 124} fill={col} fontSize="13" className="mono" fontWeight="700">DOC {d.id} · {d.date}</text>
          <text x={x - 134} y={AX - 98} fill={INK} fontSize="16" fontWeight="700">{d.title}</text>
          <text x={x - 134} y={AX - 74} fill={MUTED} fontSize="14">claim: <tspan fill={INK} fontWeight="700" className="mono">{d.claim}</tspan></text>
          {s && <g><Chip x={x - 60} y={AX + 64} text={dropped ? "FUTURE · dropped" : s} color={col} /></g>}
          {s === "SUPERSEDED" && <text x={x} y={AX + 92} textAnchor="middle" fill={MUTED} fontSize="12" className="mono">on 2025-09-22 by DOC B</text>}
        </g>); })}
      {/* supersession arrow */}
      {step === 1 && <path d={`M${toX("2025-09-22") - 150} ${AX - 105} C ${toX("2024-02-05") + 220} ${AX - 190}, ${toX("2024-02-05") + 200} ${AX - 190}, ${toX("2024-02-05") + 150} ${AX - 105}`} fill="none" stroke={ST.SUPERSEDED} strokeWidth="2" className="flow" />}
      {/* reference date */}
      {step >= 1 && <g>
        <line x1={tx} x2={tx} y1={AX - 170} y2={AX + 110} stroke={ACC} strokeWidth="3" strokeDasharray="8 6" />
        <rect x={tx - 92} y={AX - 206} width="184" height="30" rx="15" fill={ACC} />
        <text x={tx} y={AX - 185} textAnchor="middle" fill="#07101f" fontSize="14" fontWeight="800" className="mono">t = {t}</text>
      </g>}
      {/* caption + output */}
      <text x="700" y="412" textAnchor="middle" fill={MUTED} fontSize="17">{captions[Math.min(step, 2)]}</text>
      {out && <g><rect x="440" y="430" width="520" height="34" rx="17" fill={hexa(GREEN, .12)} stroke={GREEN} />
        <text x="700" y="453" textAnchor="middle" fill={GREEN} fontSize="15" fontWeight="700" className="mono">{out}</text></g>}
    </svg>
  );
}

// ---------- Slide: architecture pipeline (step reveal) ----------
function Pipeline({step = 0}) {
  const on = (k) => step >= k ? 1 : 0.12;
  return (
    <svg viewBox="0 0 1400 570">
      {/* ingestion group */}
      <rect x="20" y="20" width="1070" height="165" rx="18" fill="none" stroke={hexa(ACC, .45)} strokeDasharray="8 6" />
      <text x="40" y="44" fill={ACC} fontSize="13" className="mono" fontWeight="700">INGESTION · offline</text>
      <Box x={40} y={62} w={150} h={100} title="Documents" lines={["notices, circulars,", "articles"]} color={GREY} />
      <Arrow x1={190} y1={112} x2={228} y2={112} />
      <Box x={230} y={62} w={150} h={100} title="Parse" lines={["title · header · body"]} color={ACC2} />
      <Arrow x1={380} y1={112} x2={418} y2={112} />
      <Box x={420} y={62} w={310} h={100} title="Temporal metadata extractor" lines={["publication date · effective date", "supersession cue · confidence"]} color={VIO} bold />
      <Arrow x1={730} y1={112} x2={768} y2={112} />
      <Box x={770} y={62} w={300} h={100} title="Time-indexed hybrid store" lines={["BM25 + bge-base-en-v1.5", "+ date fields"]} color={ACC2} />
      <text x="1120" y="92" fill={MUTED} fontSize="14">purple = additions to an</text>
      <text x="1120" y="112" fill={MUTED} fontSize="14">advanced RAG pipeline</text>
      <rect x="1120" y="128" width="14" height="14" rx="3" fill={VIO} /><text x="1142" y="140" fill={MUTED} fontSize="13">new component</text>
      {/* store -> retriever */}
      <Elbow pts={[[920, 162], [920, 232], [315, 232], [315, 298]]} label="search + date fields" lx={620} ly={224} opacity={on(1)} />
      {/* query group */}
      <rect x="20" y="268" width="1360" height="290" rx="18" fill="none" stroke={hexa(ACC2, .45)} strokeDasharray="8 6" opacity={on(1)} style={{transition: "opacity .4s"}} />
      <text x="40" y="292" fill={ACC2} fontSize="13" className="mono" fontWeight="700" opacity={on(1)}>QUERY TIME</text>
      <Box x={40} y={300} w={150} h={100} title="Question q" lines={["reference date t"]} color={GREY} opacity={on(1)} />
      <Arrow x1={190} y1={350} x2={228} y2={350} opacity={on(1)} />
      <Box x={230} y={300} w={170} h={100} title="Hybrid retriever" lines={["top-5 · RRF k = 60"]} color={ACC2} opacity={on(1)} />
      <Arrow x1={400} y1={350} x2={438} y2={350} opacity={on(2)} />
      <Box x={440} y={300} w={230} h={100} title="Conflict detector" lines={["similarity gate → claims", "→ equivalence"]} color={VIO} bold opacity={on(2)} />
      <Arrow x1={670} y1={350} x2={708} y2={350} opacity={on(2)} />
      <Box x={710} y={300} w={230} h={100} title="Validity status" lines={["CURRENT · SUPERSEDED", "UNVERIFIED · FUTURE"]} color={VIO} bold opacity={on(2)} />
      <Arrow x1={940} y1={350} x2={978} y2={350} opacity={on(3)} />
      <Box x={980} y={300} w={240} h={100} title="Validity-aware reranker" lines={["score × validity(t) × trust", "FUTURE dropped"]} color={VIO} bold opacity={on(3)} />
      <Arrow x1={1100} y1={400} x2={1100} y2={438} opacity={on(3)} />
      <Box x={980} y={440} w={240} h={96} title="Generator" lines={["validity prompting:", "[Document i | dated | status]"]} color={GOLD} opacity={on(3)} />
      <Arrow x1={980} y1={488} x2={962} y2={488} opacity={on(3)} />
      <Box x={620} y={440} w={340} h={96} title="ANSWER · VALID_FROM · BASIS" lines={["or ABSTAIN when the only relevant", "evidence is undated and conflicting"]} color={GREEN} bold opacity={on(3)} />
      <g opacity={on(3)} style={{transition: "opacity .4s"}}>
        <text x="40" y="462" fill={MUTED} fontSize="14">Superseded documents stay in the context so the model</text>
        <text x="40" y="482" fill={MUTED} fontSize="14">can explain the history, but sink below current ones.</text>
        <text x="40" y="502" fill={MUTED} fontSize="14">Mean latency 0.49 s (naive) → 0.74 s (TVA-RAG).</text>
        <text x="40" y="528" fill={DIM} fontSize="12.5" className="mono">detector calls cached per (question, document)</text>
      </g>
    </svg>
  );
}

// ---------- Slide: temporal extractor ----------
function ExtractorDiag() {
  const hl = (x, y, w, color) => <rect x={x} y={y} width={w} height="24" rx="6" fill={hexa(color, .18)} stroke={hexa(color, .6)} />;
  return (
    <svg viewBox="0 0 880 470">
      <rect x="20" y="20" width="400" height="430" rx="16" fill={wa(.04)} stroke={wa(.18)} />
      <text x="40" y="36" fill={DIM} fontSize="11" className="mono">DOCUMENT · as ingested</text>
      <text x="40" y="66" fill={INK} fontSize="17" fontWeight="700">GST exemption on health insurance</text>
      {hl(34, 80, 330, ACC2)}<text x="40" y="97" fill={INK} fontSize="14" className="mono">Notification dated 22nd September, 2025</text>
      <text x="40" y="134" fill={MUTED} fontSize="14">The Council has decided that individual health</text>
      <text x="40" y="156" fill={MUTED} fontSize="14">insurance policies are exempt from GST</text>
      {hl(34, 165, 232, GOLD)}<text x="40" y="182" fill={INK} fontSize="14" className="mono">with effect from 22.09.2025.</text>
      {hl(34, 200, 335, ROSE)}<text x="40" y="217" fill={INK} fontSize="14" className="mono">This notification supersedes the 18 %</text>
      <text x="40" y="242" fill={MUTED} fontSize="14">rate notified in February 2024. Insurers must</text>
      <text x="40" y="264" fill={MUTED} fontSize="14">update invoices and policy schedules accordingly.</text>
      <text x="40" y="300" fill={DIM} fontSize="13" fontStyle="italic">… body continues …</text>
      {/* connectors */}
      {[[92, ACC2], [177, GOLD], [212, ROSE]].map(([y, c]) => <line key={y} x1="366" x2="446" y1={y} y2={y} stroke={c} strokeWidth="1.5" strokeDasharray="4 4" />)}
      {/* annotations */}
      <circle cx="452" cy="92" r="5" fill={ACC2} />
      <text x="466" y="88" fill={INK} fontSize="15" fontWeight="700">publication date = 2025-09-22</text>
      <text x="466" y="108" fill={MUTED} fontSize="12.5">first date in the first 3 lines · confidence 0.95 (day precision),</text>
      <text x="466" y="126" fill={MUTED} fontSize="12.5">0.8 (month precision) · first date in the body instead → 0.5</text>
      <circle cx="452" cy="177" r="5" fill={GOLD} />
      <text x="466" y="173" fill={INK} fontSize="15" fontWeight="700">effective date = 2025-09-22</text>
      <text x="466" y="193" fill={MUTED} fontSize="12.5">a date within 40 characters of a cue: effective from ·</text>
      <text x="466" y="211" fill={MUTED} fontSize="12.5">with effect from · w.e.f. · comes into force</text>
      <circle cx="452" cy="250" r="5" fill={ROSE} />
      <text x="466" y="246" fill={INK} fontSize="15" fontWeight="700">supersession cue = true</text>
      <text x="466" y="266" fill={MUTED} fontSize="12.5">supersedes · replaces · no longer · repeal · retired · renamed</text>
      <Box x={450} y={300} w={410} h={74} title="anchor = effective date, else publication date" lines={["the one date used for all validity reasoning"]} color={VIO} bold titleSize={14.5} lineSize={12.5} />
      <text x="450" y="408" fill={MUTED} fontSize="13">No date → optional LLM fallback, told <tspan fill={INK} fontWeight="700">not</tspan> to infer dates</text>
      <text x="450" y="426" fill={MUTED} fontSize="13">from content. 0 / 7 hallucinated on the undated documents.</text>
    </svg>
  );
}

// ---------- Slide: conflict detector ----------
function DetectorDiag() {
  return (
    <svg viewBox="0 0 1400 440">
      <Box x={20} y={50} w={170} h={80} title="Top-5 documents" lines={["+ the question"]} color={GREY} />
      <Arrow x1={190} y1={90} x2={228} y2={90} />
      <Diamond x={230} y={35} w={240} h={110} text="sim(dᵢ, dⱼ) ≥ 0.60" lines={["with some other dⱼ?"]} />
      <Arrow x1={350} y1={145} x2={350} y2={188} label="no" lx={366} ly={172} />
      <Box x={255} y={190} w={190} h={66} title="Not a candidate" lines={["no LLM calls"]} color={GREY} dashed />
      <Arrow x1={470} y1={90} x2={508} y2={90} label="yes" lx={489} ly={78} />
      <Box x={510} y={50} w={260} h={80} title="Claim extraction (LLM)" lines={["scope check → shortest answer", "to this exact question, or NONE"]} color={VIO} bold />
      <Arrow x1={770} y1={90} x2={808} y2={90} />
      <Diamond x={810} y={35} w={200} h={110} text="claim = NONE?" />
      <Arrow x1={910} y1={145} x2={910} y2={188} label="yes" lx={930} ly={172} />
      <Box x={815} y={190} w={190} h={66} title="Does not address" lines={["the question"]} color={GREY} dashed />
      <Arrow x1={1010} y1={90} x2={1048} y2={90} label="no" lx={1029} ly={78} />
      <Box x={1050} y={50} w={330} h={80} title="Equivalence (per pair)" lines={["normalised string match, else", "LLM: same answer? YES / NO"]} color={VIO} bold />
      <Arrow x1={1215} y1={130} x2={1215} y2={188} label="different" lx={1262} ly={164} />
      <Box x={1120} y={190} w={190} h={66} title="Conflict pair" lines={["(dᵢ, dⱼ) + both claims"]} color={ROSE} bold />
      {/* example strip */}
      <rect x="20" y="290" width="1360" height="130" rx="16" fill={wa(.03)} stroke={wa(.12)} />
      <text x="40" y="316" fill={DIM} fontSize="12.5" className="mono" fontWeight="700">EXAMPLE · q: What GST rate applies to individual health insurance premiums in India?</text>
      <text x="40" y="352" fill={INK} fontSize="15" fontWeight="700">Doc A (2024)</text><Chip x={160} y={352} text="18%" color={GOLD} />
      <text x="400" y="352" fill={INK} fontSize="15" fontWeight="700">Doc B (2025)</text><Chip x={520} y={352} text="Exempt" color={GREEN} />
      <text x="780" y="352" fill={INK} fontSize="15" fontWeight="700">Doc C · GST slab restructuring (general)</text><Chip x={1120} y={352} text="NONE · scope check" color={GREY} />
      <text x="40" y="394" fill={MUTED} fontSize="14.5">A vs B: “18%” ≠ “Exempt” → <tspan fill={ROSE} fontWeight="700">conflict pair</tspan> · A vs C, B vs C: no claim → no pair · gate: no true conflicting pair on TempRev falls below 0.70 similarity</text>
      <text x="1360" y="414" textAnchor="end" fill={ACC2} fontSize="12" className="mono">cached per (question, document) · shared across all four generators</text>
    </svg>
  );
}

// ---------- Slide: pairwise validity status ----------
function StatusFlow() {
  return (
    <svg viewBox="0 0 1000 660">
      <Box x={100} y={10} w={300} h={50} title="For each retrieved document d" color={GREY} titleSize={15} />
      <Arrow x1={250} y1={60} x2={250} y2={88} />
      <Diamond x={130} y={90} w={240} h={90} text="anchor(d) > t ?" />
      <Arrow x1={370} y1={135} x2={558} y2={135} label="yes" lx={460} ly={125} />
      <Box x={560} y={100} w={210} h={70} title="FUTURE" lines={["validity 0 · dropped"]} color={ST.FUTURE} />
      <Arrow x1={250} y1={180} x2={250} y2={208} label="no" lx={268} ly={198} />
      <Diamond x={110} y={210} w={280} h={100} text="any non-future" lines={["conflict partner?"]} />
      <Arrow x1={390} y1={260} x2={558} y2={260} label="no" lx={474} ly={250} />
      <Diamond x={560} y={215} w={170} h={90} text="dated?" />
      <Arrow x1={730} y1={260} x2={788} y2={260} label="yes" lx={759} ly={250} />
      <Box x={790} y={225} w={190} h={70} title="UNCONFLICTED" lines={["validity 1.0"]} color={ST.UNCONFLICTED} />
      <Arrow x1={645} y1={305} x2={645} y2={338} label="no" lx={663} ly={326} />
      <Box x={545} y={340} w={220} h={70} title="UNVERIFIED" lines={["no date · 0.6 (0.4 if conflicting)"]} color={ST.UNVERIFIED} />
      <Arrow x1={250} y1={310} x2={250} y2={338} label="yes" lx={272} ly={328} />
      <Diamond x={140} y={340} w={220} h={90} text="d dated?" />
      <Arrow x1={360} y1={385} x2={543} y2={378} label="no" lx={450} ly={372} />
      <Arrow x1={250} y1={430} x2={250} y2={458} label="yes" lx={272} ly={448} />
      <Diamond x={110} y={460} w={280} h={100} text="a partner with" lines={["a later anchor?"]} />
      <Arrow x1={390} y1={510} x2={558} y2={510} label="yes" lx={474} ly={500} />
      <Box x={560} y={475} w={230} h={70} title="SUPERSEDED" lines={["by the newest partner · 0.25"]} color={ST.SUPERSEDED} bold />
      <Arrow x1={250} y1={560} x2={250} y2={588} label="no" lx={268} ly={578} />
      <Box x={150} y={590} w={200} h={60} title="CURRENT" lines={["validity 1.0"]} color={ST.CURRENT} bold />
      <text x="560" y="600" fill={MUTED} fontSize="14">Pairwise, not transitive: one false conflict cannot</text>
      <text x="560" y="620" fill={MUTED} fontSize="14">drag unrelated documents into a shared cluster.</text>
      <text x="560" y="646" fill={MUTED} fontSize="14">Dropping FUTURE is what makes <tspan fill={INK} fontWeight="700">as-of</tspan> answers possible.</text>
    </svg>
  );
}

// ---------- Slide: benchmark construction ----------
function BenchBuild() {
  return (
    <svg viewBox="0 0 1400 400">
      <Box x={20} y={130} w={230} h={120} title="Reversal item" lines={["question · old / new answer", "+ aliases · change date", "undated_old flag · t_past"]} color={GREY} />
      <Arrow x1={250} y1={170} x2={298} y2={120} />
      <Arrow x1={250} y1={210} x2={298} y2={262} />
      <Box x={300} y={60} w={250} h={100} title="Stale document" lines={["dated before the change", "7 rendered undated"]} color={GOLD} />
      <Box x={300} y={220} w={250} h={100} title="Current document" lines={["dated at / after the change", "optional effective date"]} color={GREEN} />
      <Arrow x1={550} y1={110} x2={608} y2={160} />
      <Arrow x1={550} y1={270} x2={608} y2={222} />
      <Box x={610} y={120} w={260} h={140} title="Renderer" lines={["7 header date formats", "3 effective-date formats", "undated variant strips every cue"]} color={VIO} bold />
      <Arrow x1={870} y1={170} x2={918} y2={118} />
      <Arrow x1={870} y1={210} x2={918} y2={262} />
      <Box x={920} y={60} w={190} h={100} title="Mixed corpus" lines={["162 documents"]} color={ACC2} />
      <Box x={920} y={220} w={190} h={100} title="Stale-only corpus" lines={["91 documents", "current docs removed"]} color={ROSE} />
      <Arrow x1={1110} y1={95} x2={1158} y2={62} />
      <Arrow x1={1110} y1={125} x2={1158} y2={168} />
      <Arrow x1={1110} y1={270} x2={1158} y2={290} />
      <Box x={1160} y={20} w={220} h={80} title="t = 2026-01-01" lines={["gold = current answer"]} color={ACC} />
      <Box x={1160} y={125} w={220} h={90} title="t = t_past" lines={["midpoint of stale date and", "change date · gold = old answer"]} color={ACC} />
      <Box x={1160} y={255} w={220} h={70} title="20 control queries" lines={["gold = stable fact"]} color={GREY} />
      <text x="700" y="378" textAnchor="middle" fill={MUTED} fontSize="16">71 reversals → 142 dated documents; 20 controls add 20 more. Two settings × two reference dates = <tspan fill={INK} fontWeight="700">162 (mixed)</tspan> and <tspan fill={INK} fontWeight="700">91 (stale-only)</tspan> queries per system.</text>
    </svg>
  );
}

// ---------- Slide: experimental grid ----------
function GridDiag() {
  return (
    <svg viewBox="0 0 1400 300">
      <Box x={20} y={90} w={270} h={120} title="4 generators" lines={["llama3.2:3b · llama3.1:8b", "qwen2.5:7b · qwen3.5:35b", "Ollama · temperature 0 · fixed seed"]} color={ACC} />
      <Arrow x1={290} y1={130} x2={338} y2={88} />
      <Arrow x1={290} y1={170} x2={338} y2={212} />
      <Box x={340} y={30} w={310} h={100} title="Mixed corpus" lines={["5 modes × 162 queries", "71 now · 71 past · 20 control"]} color={ACC2} />
      <Box x={340} y={170} w={310} h={100} title="Stale-only corpus" lines={["3 modes × 91 queries", "71 now · 20 control"]} color={ROSE} />
      <Arrow x1={650} y1={90} x2={718} y2={132} />
      <Arrow x1={650} y1={210} x2={718} y2={168} />
      <Box x={720} y={90} w={300} h={120} title="Labelling" lines={["alias match 85.8 %", "+ cached LLM judge 14.2 %", "(qwen3.5:35b)"]} color={VIO} bold />
      <Arrow x1={1020} y1={150} x2={1078} y2={150} />
      <Box x={1080} y={90} w={300} h={120} title="Metrics · figures" lines={["accuracy at t · stale-answer rate", "flip rate · abstention · validity window", "component metrics"]} color={GREEN} />
      <text x="700" y="292" textAnchor="middle" fill={ACC2} fontSize="15" className="mono" fontWeight="700">4 × (5 × 162 + 3 × 91) = 4,332 generations · zero failures</text>
    </svg>
  );
}
