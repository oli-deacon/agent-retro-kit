#!/usr/bin/env python3
"""Generate a self-contained, source-backed retro dashboard."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from retro_core import (
    KIT_DIR,
    evidence_confidence,
    effective_outcome,
    evaluate_experiments,
    flags,
    load_experiments,
    load_exposures,
    load_runs,
    root_cause,
    row_week,
    validate_runs,
    verification_status,
    weekly_summaries,
)


DEFAULT_OUTPUT = KIT_DIR / "output" / "retro-dashboard" / "index.html"


def dashboard_payload() -> dict:
    runs = load_runs()
    experiments = evaluate_experiments(load_experiments(), load_exposures(), runs)
    public_runs = [
        {
            "run_id": row.get("run_id", ""),
            "week": row_week(row),
            "task_title": row.get("task_title", ""),
            "team_or_repo": row.get("team_or_repo", ""),
            "agent_platform": row.get("agent_platform", ""),
            "task_type": row.get("task_type_inferred", ""),
            "outcome": effective_outcome(row),
            "retries": row.get("retry_count_inferred", ""),
            "verification": verification_status(row),
            "root_cause": root_cause(row),
            "confidence": evidence_confidence(row),
            "flags": flags(row),
        }
        for row in runs
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weekly": weekly_summaries(runs),
        "quality": validate_runs(runs),
        "experiments": experiments,
        "runs": public_runs,
    }


HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Retro Dashboard</title>
  <style>
    :root { --ink:#172031; --muted:#667085; --line:#dce2ea; --paper:#f4f6f8; --card:#fff; --blue:#3157d5; --teal:#087f70; --amber:#ad6500; --red:#b42318; --navy:#18233b; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:var(--paper); font:14px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    header { background:var(--navy); color:#fff; padding:32px max(24px, calc((100vw - 1240px)/2)); }
    header p { margin:6px 0 0; color:#c9d2e4; }
    h1 { margin:0; font-size:clamp(25px, 4vw, 38px); letter-spacing:-.035em; }
    h2 { margin:0 0 16px; font-size:19px; letter-spacing:-.015em; }
    h3 { margin:0; font-size:15px; }
    main { max-width:1240px; margin:0 auto; padding:24px; }
    .toolbar,.section-head { display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
    .toolbar { margin-bottom:20px; }
    .status { display:inline-flex; align-items:center; gap:7px; padding:6px 10px; background:#fff; border:1px solid var(--line); border-radius:999px; font-weight:700; }
    .dot { width:8px; height:8px; border-radius:50%; background:var(--teal); }
    .status.partial .dot { background:var(--amber); } .status.needs_attention .dot { background:var(--red); }
    .muted { color:var(--muted); }
    .grid { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px; box-shadow:0 1px 2px rgba(16,24,40,.04); }
    .metric { grid-column:span 3; min-height:124px; }
    .metric .value { font-size:32px; line-height:1.1; font-weight:760; margin:20px 0 4px; letter-spacing:-.04em; }
    .wide { grid-column:span 8; } .side { grid-column:span 4; } .full { grid-column:1/-1; }
    .eyebrow { color:var(--muted); font-size:12px; font-weight:750; letter-spacing:.06em; text-transform:uppercase; }
    section { margin-top:24px; }
    svg { display:block; width:100%; min-height:220px; overflow:visible; }
    .legend { display:flex; gap:18px; color:var(--muted); font-size:12px; }
    .key { display:inline-block; width:16px; height:3px; margin-right:6px; vertical-align:middle; background:var(--blue); }
    .key.teal { background:var(--teal); }
    .experiment { padding:14px 0; border-top:1px solid var(--line); }
    .experiment:first-child { border-top:0; padding-top:0; }
    .tag { display:inline-flex; padding:3px 8px; border-radius:999px; background:#eef2ff; color:#344bc0; font-size:11px; font-weight:750; }
    .variant-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:8px; margin-top:10px; }
    .variant { background:var(--paper); border-radius:8px; padding:9px; }
    .quality-list { list-style:none; margin:12px 0 0; padding:0; }
    .quality-list li { display:flex; justify-content:space-between; padding:8px 0; border-top:1px solid var(--line); }
    .controls { display:flex; gap:8px; flex-wrap:wrap; }
    input,select { min-height:38px; border:1px solid #c9d1dc; border-radius:8px; background:#fff; padding:8px 10px; color:var(--ink); font:inherit; }
    input { min-width:230px; }
    .table-wrap { overflow:auto; margin-top:14px; border:1px solid var(--line); border-radius:9px; }
    table { width:100%; border-collapse:collapse; min-width:800px; }
    th,td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }
    th { position:sticky; top:0; background:#f8fafc; color:#475467; font-size:11px; letter-spacing:.04em; text-transform:uppercase; }
    tbody tr:last-child td { border-bottom:0; }
    .outcome-success { color:var(--teal); font-weight:700; } .outcome-failure { color:var(--red); font-weight:700; } .outcome-partial,.outcome-uncertain { color:var(--amber); font-weight:700; }
    .empty { padding:28px; border:1px dashed #b8c1cc; border-radius:9px; color:var(--muted); text-align:center; }
    footer { max-width:1240px; margin:0 auto; padding:12px 24px 36px; color:var(--muted); font-size:12px; }
    @media (max-width:900px) { .metric { grid-column:span 6; } .wide,.side { grid-column:1/-1; } }
    @media (max-width:540px) { main { padding:16px; } header { padding:24px 16px; } .metric { grid-column:1/-1; } input { min-width:100%; } }
  </style>
</head>
<body>
  <header><h1>Agent delivery health</h1><p>Weekly outcomes, verification discipline, experiment evidence, and the runs behind every number.</p></header>
  <main>
    <div class="toolbar"><div id="qualityStatus"></div><div class="muted" id="generated"></div></div>
    <div class="grid" id="metrics"></div>
    <section class="grid">
      <article class="card wide"><div class="section-head"><h2>Weekly signal</h2><div class="legend"><span><i class="key"></i>Success</span><span><i class="key teal"></i>Verified</span></div></div><div id="trend"></div></article>
      <aside class="card side"><h2>Data confidence</h2><div id="quality"></div></aside>
    </section>
    <section class="card"><div class="section-head"><div><h2>Experiments</h2><div class="muted">Only explicitly recorded exposures count toward evaluation.</div></div></div><div id="experiments"></div></section>
    <section class="card">
      <div class="section-head"><div><h2>Run evidence</h2><div class="muted" id="runCount"></div></div><div class="controls"><input id="search" type="search" placeholder="Search run, task, repo…" aria-label="Search runs"><select id="outcome" aria-label="Filter outcome"><option value="">All outcomes</option><option>success</option><option>partial</option><option>failure</option><option>abandoned</option><option>uncertain</option></select></div></div>
      <div id="runs"></div>
    </section>
  </main>
  <footer>Generated locally from <code>data/run-log.csv</code>, <code>experiments.json</code>, and <code>data/experiment-exposures.csv</code>. No data leaves the machine.</footer>
  <script id="dashboard-data" type="application/json">__PAYLOAD__</script>
  <script>
    const data=JSON.parse(document.getElementById('dashboard-data').textContent);
    const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const pct=v=>v==null?'—':`${Number(v).toFixed(v%1?1:0)}%`;
    const latest=data.weekly.at(-1)||{runs:0,outcomes:{},confidence:{}};
    const prior=data.weekly.at(-2);
    const delta=(value,key)=>{if(!prior||value==null||prior[key]==null)return 'No comparison yet';const d=value-prior[key];return `${d>0?'+':''}${d.toFixed(1)} pp vs prior week`;};
    const cards=[
      ['Runs',latest.runs??0,latest.week||'No completed week'],
      ['Success rate',pct(latest.success_rate),delta(latest.success_rate,'success_rate')],
      ['Verified outcomes',pct(latest.verification_completed_rate),delta(latest.verification_completed_rate,'verification_completed_rate')],
      ['Median retries',latest.median_retries??'—',latest.needs_review?`${latest.needs_review} flagged for review`:'No review flags'],
    ];
    document.getElementById('metrics').innerHTML=cards.map(([label,value,note])=>`<article class="card metric"><div class="eyebrow">${esc(label)}</div><div class="value">${esc(value)}</div><div class="muted">${esc(note)}</div></article>`).join('');
    const q=data.quality; document.getElementById('qualityStatus').innerHTML=`<span class="status ${esc(q.status)}"><i class="dot"></i>${esc(q.status.replace('_',' '))}</span>`;
    document.getElementById('generated').textContent=`Refreshed ${new Date(data.generated_at).toLocaleString()}`;
    document.getElementById('quality').innerHTML=`<div class="eyebrow">Evidence status</div><div style="font-size:28px;font-weight:760;margin:8px 0">${esc(q.status.replace('_',' '))}</div><ul class="quality-list"><li><span>Rows</span><strong>${q.rows}</strong></li><li><span>Duplicate IDs</span><strong>${q.duplicate_run_ids.length}</strong></li><li><span>Schema issues</span><strong>${q.issues.length}</strong></li><li><span>Newest capture</span><strong>${q.stale_days==null?'—':`${q.stale_days}d ago`}</strong></li><li><span>High confidence</span><strong>${latest.confidence?.high||0}</strong></li></ul>`;
    function renderTrend(){const weeks=data.weekly;if(!weeks.length){document.getElementById('trend').innerHTML='<div class="empty">Add run-log rows to see weekly trends.</div>';return;}const W=720,H=220,p=35,x=i=>weeks.length===1?W/2:p+i*(W-2*p)/(weeks.length-1),y=v=>H-p-(v??0)*(H-2*p)/100;const line=(key,color)=>`<polyline fill="none" stroke="${color}" stroke-width="3" points="${weeks.map((w,i)=>`${x(i)},${y(w[key])}`).join(' ')}"/>${weeks.map((w,i)=>`<circle cx="${x(i)}" cy="${y(w[key])}" r="4" fill="${color}"><title>${esc(w.week)}: ${pct(w[key])}</title></circle>`).join('')}`;document.getElementById('trend').innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Weekly success and verification rates"><line x1="${p}" y1="${y(100)}" x2="${W-p}" y2="${y(100)}" stroke="#e6eaf0"/><line x1="${p}" y1="${y(50)}" x2="${W-p}" y2="${y(50)}" stroke="#e6eaf0"/><line x1="${p}" y1="${y(0)}" x2="${W-p}" y2="${y(0)}" stroke="#e6eaf0"/>${line('success_rate','#3157d5')}${line('verification_completed_rate','#087f70')}${weeks.map((w,i)=>`<text x="${x(i)}" y="214" text-anchor="middle" fill="#667085" font-size="11">${esc(w.week.replace(/^\d{4}-/,''))}</text>`).join('')}</svg>`;}renderTrend();
    function renderExperiments(){const root=document.getElementById('experiments');if(!data.experiments.length){root.innerHTML='<div class="empty">No experiments configured. Add one to <code>experiments.json</code>.</div>';return;}root.innerHTML=data.experiments.map(exp=>{const variants=Object.entries(exp.variant_metrics||{}).map(([name,m])=>`<div class="variant"><strong>${esc(name)}</strong><div>${m.exposures} exposures</div><div class="muted">${pct(m.success_rate)} success · ${m.median_retries??'—'} retries</div></div>`).join('');return `<article class="experiment"><div class="section-head"><h3>${esc(exp.id)} · ${esc(exp.title)}</h3><span class="tag">${esc(exp.evaluation_status)}</span></div><p class="muted">${esc(exp.hypothesis||'No hypothesis recorded.')}</p><div><strong>${exp.explicit_exposures}</strong> explicit exposures · minimum ${exp.minimum_exposures||5}</div>${variants?`<div class="variant-grid">${variants}</div>`:'<div class="muted" style="margin-top:8px">No linked exposures yet.</div>'}</article>`;}).join('');}renderExperiments();
    function renderRuns(){const term=document.getElementById('search').value.toLowerCase(),outcome=document.getElementById('outcome').value;const rows=data.runs.filter(r=>(!outcome||r.outcome===outcome)&&(!term||Object.values(r).join(' ').toLowerCase().includes(term))).slice().reverse().slice(0,100);document.getElementById('runCount').textContent=`Showing ${rows.length} of ${data.runs.length} runs`;if(!rows.length){document.getElementById('runs').innerHTML='<div class="empty" style="margin-top:14px">No runs match these filters.</div>';return;}document.getElementById('runs').innerHTML=`<div class="table-wrap"><table><thead><tr><th>Week</th><th>Run</th><th>Task</th><th>Outcome</th><th>Verified</th><th>Retries</th><th>Root cause</th><th>Confidence</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.week)}</td><td><code>${esc(r.run_id)}</code></td><td>${esc(r.task_title||'Untitled')}</td><td class="outcome-${esc(r.outcome)}">${esc(r.outcome)}</td><td>${esc(r.verification)}</td><td>${esc(r.retries||'0')}</td><td>${esc(r.root_cause)}</td><td>${esc(r.confidence)}</td></tr>`).join('')}</tbody></table></div>`;}document.getElementById('search').addEventListener('input',renderRuns);document.getElementById('outcome').addEventListener('change',renderRuns);renderRuns();
  </script>
</body>
</html>'''


def render_dashboard(output: Path = DEFAULT_OUTPUT) -> Path:
    payload = json.dumps(dashboard_payload(), ensure_ascii=False).replace("<", "\\u003c")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HTML.replace("__PAYLOAD__", payload), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"Dashboard: {render_dashboard(args.output)}")


if __name__ == "__main__":
    main()
