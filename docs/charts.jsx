// SVG chart components fed from window.DATA
const D0 = window.DATA;
const MODE_SERIES = (vals, keys = D0.modes) => keys.map((k, i) => ({key: k, label: D0.modeLabel[k], color: D0.colors[k], values: vals.map(v => v[i])}));

// Vertical grouped bars: cats on x, one bar per series.
function GroupedBars({cats, series, width = 780, height = 400, ymax = 1.08, title, fmt = v => v.toFixed(2), hl = "tva", legend = true, ticks = [0, .25, .5, .75, 1]}) {
  const L = 54, R = 14, T = (title ? 40 : 14) + (legend ? 26 : 0), B = 44;
  const W = width - L - R, H = height - T - B;
  const gw = W / cats.length, n = series.length, bw = Math.min(38, (gw * 0.82) / n), inner = bw * n;
  const y = v => T + H * (1 - v / ymax);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{width: "100%", height: "auto"}}>
      {title && <text x={L} y={18} fill="#9ba6c9" fontSize="14" className="mono">{title}</text>}
      {legend && series.map((s, k) => { const x = L + k * (W / series.length); const ly = title ? 40 : 14; return (
        <g key={s.key}><rect x={x} y={ly - 10} width="12" height="12" rx="3" fill={s.color} /><text x={x + 18} y={ly + 1} fill="#9ba6c9" fontSize="13">{s.label}</text></g>); })}
      {ticks.filter(t => t <= ymax).map(t => (
        <g key={t}><line x1={L} x2={width - R} y1={y(t)} y2={y(t)} stroke="rgba(255,255,255,.08)" />
          <text x={L - 8} y={y(t) + 4} fill="#6b7598" fontSize="12" textAnchor="end" className="mono">{t.toFixed(2)}</text></g>))}
      {cats.map((c, i) => { const x0 = L + i * gw + (gw - inner) / 2; return (
        <g key={c}>
          {series.map((s, k) => { const v = s.values[i]; if (v == null) return null; const x = x0 + k * bw, top = y(v), h = T + H - top; const isHl = s.key === hl; return (
            <g key={s.key}>
              <rect x={x + 1.5} y={top} width={bw - 3} height={Math.max(h, 1.5)} rx="4" fill={s.color} opacity={isHl ? 1 : .78}>
                <animate attributeName="height" from="0" to={Math.max(h, 1.5)} dur="0.7s" fill="freeze" />
                <animate attributeName="y" from={T + H} to={top} dur="0.7s" fill="freeze" />
              </rect>
              <text x={x + bw / 2} y={top - 6} textAnchor="middle" fill={isHl ? "#e9edf9" : "#9ba6c9"} fontSize={n > 4 ? 11 : 12.5} fontWeight={isHl ? 800 : 500} className="mono">{fmt(v)}</text>
            </g>); })}
          <text x={L + i * gw + gw / 2} y={height - 16} textAnchor="middle" fill="#e9edf9" fontSize="15" fontWeight="600">{c}</text>
        </g>); })}
    </svg>
  );
}

// Horizontal bar chart. rows: [{name, v, color?, note?}]
function HBar({rows, max, fmt = (v) => v.toFixed(3), width = 760, barH = 30, labelW = 170, title, star = true, lowerBetter = false, hl = []}) {
  const H = rows.length * (barH + 8) + 40;
  const best = lowerBetter ? Math.min(...rows.map(r => r.v)) : Math.max(...rows.map(r => r.v));
  const W = width - labelW - 110;
  const mx = max ?? Math.max(...rows.map(r => r.v)) * 1.08;
  return (
    <svg viewBox={`0 0 ${width} ${H}`} style={{width: "100%", height: "auto"}}>
      {title && <text x={labelW} y={18} fill="#9ba6c9" fontSize="14" className="mono">{title}</text>}
      {rows.map((r, i) => {
        const y = 32 + i * (barH + 8); const w = Math.max(2, (r.v / mx) * W); const isHl = hl.includes(r.name);
        return (
          <g key={r.name}>
            <text x={labelW - 12} y={y + barH / 2 + 5} textAnchor="end" fill={isHl ? "#c084fc" : "#e9edf9"} fontSize="15" fontWeight={isHl ? 800 : 500}>{r.name}</text>
            <rect x={labelW} y={y} width={W} height={barH} rx="7" fill="rgba(255,255,255,.04)" />
            <rect x={labelW} y={y} width={w} height={barH} rx="7" fill={r.color || "#8b97ff"} opacity={isHl ? 1 : .8}>
              <animate attributeName="width" from="0" to={w} dur="0.7s" fill="freeze" />
            </rect>
            <text x={labelW + w + 10} y={y + barH / 2 + 5} fill={star && r.v === best ? "#3dd6c6" : "#9ba6c9"} fontSize="14" fontWeight={star && r.v === best ? 800 : 500} className="mono">{fmt(r.v)}{star && r.v === best ? " ★" : ""}{r.note ? `  ${r.note}` : ""}</text>
          </g>
        );
      })}
    </svg>
  );
}

// Horizontal stacked bars. rows: [{name, parts:[{v, color, label}]}]
function Stacked({rows, width = 760, barH = 36, labelW = 150, title, legend = [], fmt = v => v.toFixed(2)}) {
  const W = width - labelW - 30; const top = title ? 36 : 14; const H = top + rows.length * (barH + 14) + (legend.length ? 36 : 10);
  return (
    <svg viewBox={`0 0 ${width} ${H}`} style={{width: "100%", height: "auto"}}>
      {title && <text x={labelW} y={18} fill="#9ba6c9" fontSize="14" className="mono">{title}</text>}
      {rows.map((r, i) => { const y = top + i * (barH + 14); let x = labelW; return (
        <g key={r.name}>
          <text x={labelW - 12} y={y + barH / 2 + 5} textAnchor="end" fill="#e9edf9" fontSize="15" fontWeight="600">{r.name}</text>
          <rect x={labelW} y={y} width={W} height={barH} rx="7" fill="rgba(255,255,255,.04)" />
          {r.parts.map((p, k) => { const w = p.v * W; const seg = <g key={k}>
              <rect x={x} y={y} width={Math.max(0, w)} height={barH} fill={p.color} opacity=".9" />
              {w > 46 && <text x={x + w / 2} y={y + barH / 2 + 5} textAnchor="middle" fill="#07101f" fontSize="13" fontWeight="700" className="mono">{fmt(p.v)}</text>}
            </g>; x += w; return seg; })}
        </g>); })}
      {legend.map((l, k) => { const stepX = Math.min(190, W / legend.length); return <g key={l.label}><rect x={labelW + k * stepX} y={H - 22} width="12" height="12" rx="3" fill={l.color} /><text x={labelW + 18 + k * stepX} y={H - 11} fill="#9ba6c9" fontSize="12.5">{l.label}</text></g>; })}
    </svg>
  );
}

// Small histogram of change years
function YearHist({data, width = 640, height = 230}) {
  const L = 30, R = 10, T = 30, B = 36; const W = width - L - R, H = height - T - B;
  const years = []; for (let y = 2006; y <= 2025; y++) years.push(y);
  const m = Object.fromEntries(data); const mx = Math.max(...data.map(d => d[1])) * 1.15; const bw = W / years.length;
  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{width: "100%", height: "auto"}}>
      <text x={L} y={16} fill="#9ba6c9" fontSize="14" className="mono">change dates of the 71 reversals, by year</text>
      {years.map((yr, i) => { const v = m[yr] || 0; const h = (v / mx) * H; const recent = yr >= 2022; return (
        <g key={yr}>
          <rect x={L + i * bw + 2} y={T + H - h} width={bw - 4} height={h} rx="3" fill={recent ? "#3dd6c6" : "#8b97ff"} opacity={v ? .9 : 0} />
          {v > 0 && <text x={L + i * bw + bw / 2} y={T + H - h - 5} textAnchor="middle" fill="#9ba6c9" fontSize="11" className="mono">{v}</text>}
          {(yr % 3 === 0 || yr === 2025) && <text x={L + i * bw + bw / 2} y={height - 12} textAnchor="middle" fill="#6b7598" fontSize="11" className="mono">{yr}</text>}
        </g>); })}
      <text x={width - R} y={16} textAnchor="end" fill="#3dd6c6" fontSize="12" className="mono">42 of 71 changed in 2022–2025</text>
    </svg>
  );
}
