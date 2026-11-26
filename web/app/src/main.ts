// The AAOC planner's web view. Every number on the page comes from the Rust core (core.ts); this file only keeps the
// accounts, reads the inputs and draws.
import { aaocDays, aaocDaysWithNew, ageFormat, dayOf, earliestNewAccount, loadCore, timeToTarget, wasmBytes, ymdOf, type Day, type Span } from './core.js';
import { exportCode, importCode, type Row } from './code.js';

const STORE = 'aaoc-planner:v1';
const EXAMPLE: Row[] = [
  { name: 'First card', type: 'Credit card', opened: '2019-03-01', closed: '' },
  { name: 'Auto loan', type: 'Loan', opened: '2021-08-15', closed: '2024-08-15' },
  { name: 'Travel card', type: 'Credit card', opened: '2023-06-15', closed: '' },
];

let portfolioName = 'My credit';
let rows: Row[] = [];

const $ = <T extends HTMLElement>(id: string): T => document.getElementById(id) as T;
const pad = (n: number): string => String(n).padStart(2, '0');
const isoToday = (): string => { const d = new Date(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; };
const dayFromIso = (iso: string): Day | null => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? dayOf(Number(m[1]), Number(m[2]), Number(m[3])) : null;
};
const isoFromDay = (day: Day): string => { const [y, m, d] = ymdOf(day); return `${y}-${pad(m)}-${pad(d)}`; };
const fmtDay = (day: Day): string => {
  const [y, m, d] = ymdOf(day);
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }).format(new Date(Date.UTC(y, m - 1, d)));
};
const plural = (n: number, word: string): string => `${n} ${word}${n === 1 ? '' : 's'}`;
const fmtAge = (days: number): string => { const { years, months } = ageFormat(days); return `${plural(years, 'year')} ${plural(months, 'month')}`; };
// "5 months", "2 years", "1 year 3 months": a span without its zero parts.
const fmtSpan = (years: number, months: number): string => (years && months ? `${plural(years, 'year')} ${plural(months, 'month')}` : years ? plural(years, 'year') : plural(months, 'month'));
const escape = (s: string): string => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] as string);

function save(): void {
  try { localStorage.setItem(STORE, JSON.stringify({ name: portfolioName, rows })); } catch { /* storage off: the page still works */ }
}
function restore(): void {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) ?? 'null');
    if (saved && Array.isArray(saved.rows)) { portfolioName = String(saved.name ?? portfolioName); rows = saved.rows; return; }
  } catch { /* fall through to the example */ }
  rows = EXAMPLE.map((r) => ({ ...r }));
}

// The rows the math can use, and a problem for each row it can't.
function accounts(today: Day): { spans: Span[]; used: Row[]; problems: Map<number, string> } {
  const spans: Span[] = [];
  const used: Row[] = [];
  const problems = new Map<number, string>();
  rows.forEach((r, i) => {
    const opened = dayFromIso(r.opened);
    const closed = r.closed ? dayFromIso(r.closed) : null;
    if (!r.name.trim()) problems.set(i, 'Give it a name.');
    else if (opened === null) problems.set(i, 'Pick the date it opened.');
    else if (opened > today) problems.set(i, 'The open date is in the future.');
    else if (r.closed && closed === null) problems.set(i, 'Pick the date it closed, or leave it empty.');
    else if (closed !== null && closed <= opened) problems.set(i, 'It must close after it opened.');
    else if (closed !== null && closed > today) problems.set(i, 'The close date is in the future.');
    else { spans.push({ opened, closed }); used.push(r); }
  });
  return { spans, used, problems };
}

function renderRows(problems: Map<number, string>): void {
  const body = $('rows');
  body.innerHTML = rows.map((r, i) => `
    <tr class="${problems.has(i) ? 'has-problem' : ''}">
      <td data-label="Name"><input aria-label="Account name" data-i="${i}" data-k="name" value="${escape(r.name)}" placeholder="e.g. First card"></td>
      <td data-label="Type"><input aria-label="Account type" data-i="${i}" data-k="type" value="${escape(r.type)}" placeholder="Credit card"></td>
      <td data-label="Opened"><input aria-label="Date opened" type="date" data-i="${i}" data-k="opened" value="${escape(r.opened)}"></td>
      <td data-label="Closed (empty if open)"><input aria-label="Date closed (empty if open)" type="date" data-i="${i}" data-k="closed" value="${escape(r.closed)}"></td>
      <td class="row-end"><button type="button" class="icon" data-remove="${i}" aria-label="Remove ${escape(r.name || 'account')}">×</button></td>
    </tr>${problems.has(i) ? `<tr class="problem"><td colspan="5">${escape(problems.get(i) as string)}</td></tr>` : ''}`).join('');
}

function renderSummary(spans: Span[], today: Day): number | null {
  const days = aaocDays(spans, today);
  $('aaoc').textContent = days === null ? '—' : fmtAge(days);
  $('aaoc-note').textContent = days === null
    ? 'Add an account to see your average age of credit.'
    : `Average age today across ${plural(spans.length, 'account')} (${days.toFixed(1)} days). Closed accounts stop aging on the day they closed.`;
  return days;
}

function renderTimeline(used: Row[], spans: Span[], today: Day, average: number | null): void {
  const svg = $('timeline');
  if (!spans.length || average === null) { svg.innerHTML = ''; svg.setAttribute('viewBox', '0 0 640 40'); return; }
  const items = spans.map((s, i) => ({ row: used[i], age: (Math.min(today, s.closed ?? today) - s.opened) / 365.25, closed: s.closed !== null }))
    .sort((a, b) => b.age - a.age);
  const avgYears = average / 365.25;
  const W = Math.max(300, Math.round(svg.getBoundingClientRect().width) || 640);
  const left = Math.min(150, Math.round(W * 0.3)), right = 56, rowH = 30, top = 10;
  const max = Math.max(avgYears, ...items.map((x) => x.age)) * 1.05 || 1;
  const x = (years: number): number => left + (years / max) * (W - left - right);
  const H = top + items.length * rowH + 26;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const nameChars = Math.max(8, Math.floor((left - 14) / 7.2));
  const bars = items.map((it, i) => {
    const y = top + i * rowH;
    const above = it.age >= avgYears;
    return `<g class="bar ${above ? 'is-above' : 'is-below'}">
      <title>${escape(it.row.name)}: ${it.age.toFixed(1)} years${it.closed ? ' (closed)' : ''}, ${above ? 'raises' : 'lowers'} the average</title>
      <text class="bar-name" x="${left - 10}" y="${y + 19}" text-anchor="end">${escape(it.row.name.length > nameChars ? `${it.row.name.slice(0, nameChars - 1)}…` : it.row.name)}</text>
      <rect x="${left}" y="${y + 6}" width="${Math.max(2, x(it.age) - left)}" height="${rowH - 12}" rx="4"${it.closed ? ' class="is-closed"' : ''}></rect>
      <text class="bar-value" x="${x(it.age) + 6}" y="${y + 19}">${it.age.toFixed(1)} y</text>
    </g>`;
  }).join('');
  const ax = x(avgYears);
  svg.innerHTML = `${bars}
    <line class="avg" x1="${ax}" x2="${ax}" y1="${top}" y2="${H - 22}"></line>
    <text class="avg-label" x="${ax}" y="${H - 6}" text-anchor="middle">average ${avgYears.toFixed(1)} y</text>`;
}

const num = (id: string): number => Math.max(0, Math.floor(Number(($(id) as HTMLInputElement).value) || 0));

function renderPlans(spans: Span[], today: Day): void {
  const say = (id: string, html: string): void => { $(id).innerHTML = html; };
  if (!spans.length) { for (const id of ['plan-future', 'plan-new', 'plan-target', 'plan-earliest']) say(id, '<span class="muted">Add an account first.</span>'); return; }

  const on = dayFromIso(($('future-date') as HTMLInputElement).value);
  const future = on === null ? null : aaocDays(spans, on);
  say('plan-future', on === null ? 'Pick a date.' : future === null ? 'No account is open by then.' : `On <b>${fmtDay(on)}</b>: <b>${fmtAge(future)}</b>.`);

  const opened = dayFromIso(($('new-opened') as HTMLInputElement).value);
  const measured = dayFromIso(($('new-measured') as HTMLInputElement).value);
  if (opened === null || measured === null) say('plan-new', 'Pick both dates.');
  else if (measured < opened) say('plan-new', 'Measure on or after the day it opens.');
  else {
    const withNew = aaocDaysWithNew(spans, opened, measured) as number;
    const without = aaocDays(spans, measured);
    const delta = without === null ? null : (withNew - without) / 365.25;
    const change = delta === null || Math.abs(delta) < 0.05 ? '' : ` (${Math.abs(delta).toFixed(1)} years ${delta < 0 ? 'lower' : 'higher'})`;
    say('plan-new', `On <b>${fmtDay(measured)}</b>: <b>${fmtAge(withNew)}</b> with it${without === null ? '' : `, ${fmtAge(without)} without it${change}`}.`);
  }

  const ty = num('target-years'), tm = Math.min(11, num('target-months'));
  const reach = timeToTarget(spans, today, ty, tm);
  say('plan-target', reach.kind === 'already' ? `Already there: you're at or above ${fmtSpan(ty, tm)}.`
    : reach.kind === 'on' ? `On <b>${fmtDay(reach.day)}</b>, in about ${fmtSpan(reach.waitYears, reach.waitMonths)}.`
      : 'Not reachable within the planner\'s horizon (closed accounts stop aging).');

  const my = num('min-years'), mm = Math.min(11, num('min-months'));
  const earliest = earliestNewAccount(spans, today, my, mm);
  say('plan-earliest', earliest === null ? 'Not within the planner\'s horizon.'
    : earliest === today ? `<b>Today</b>: a new account now keeps you at or above ${fmtSpan(my, mm)}.`
      : `<b>${fmtDay(earliest)}</b>: from then a new account keeps you at or above ${fmtSpan(my, mm)}.`);
}

function render(): void {
  const today = dayFromIso(isoToday()) as Day;
  const { spans, used, problems } = accounts(today);
  ($('portfolio-name') as HTMLInputElement).value = portfolioName;
  renderRows(problems);
  const average = renderSummary(spans, today);
  renderTimeline(used, spans, today, average);
  renderPlans(spans, today);
}

// Re-renders without rebuilding the row being typed in, so the cursor stays put.
function update(): void {
  const today = dayFromIso(isoToday()) as Day;
  const { spans, used, problems } = accounts(today);
  const average = renderSummary(spans, today);
  renderTimeline(used, spans, today, average);
  renderPlans(spans, today);
  const current = rows.map((_, i) => problems.get(i) ?? '').join('|');
  if (current !== lastProblems) { lastProblems = current; const focus = document.activeElement as HTMLInputElement | null; const key = focus?.dataset?.i ? `${focus.dataset.i}:${focus.dataset.k}` : ''; renderRows(problems); if (key) { const [i, k] = key.split(':'); (document.querySelector(`[data-i="${i}"][data-k="${k}"]`) as HTMLInputElement | null)?.focus(); } }
}
let lastProblems = '';

function wire(): void {
  $('rows').addEventListener('input', (e) => {
    const t = e.target as HTMLInputElement;
    if (!t.dataset.k) return;
    const row = rows[Number(t.dataset.i)];
    (row as unknown as Record<string, string>)[t.dataset.k] = t.value;
    save();
    update();
  });
  $('rows').addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest('[data-remove]') as HTMLElement | null;
    if (!b) return;
    rows.splice(Number(b.dataset.remove), 1);
    save(); render();
  });
  $('add').addEventListener('click', () => { rows.push({ name: '', type: '', opened: '', closed: '' }); save(); render(); (document.querySelector(`[data-i="${rows.length - 1}"][data-k="name"]`) as HTMLInputElement | null)?.focus(); });
  $('example').addEventListener('click', () => { rows = EXAMPLE.map((r) => ({ ...r })); portfolioName = 'Example'; save(); render(); });
  $('clear').addEventListener('click', () => { rows = []; save(); render(); });
  $('portfolio-name').addEventListener('input', (e) => { portfolioName = (e.target as HTMLInputElement).value; save(); });
  for (const id of ['future-date', 'new-opened', 'new-measured', 'target-years', 'target-months', 'min-years', 'min-months']) $(id).addEventListener('input', update);
  $('export').addEventListener('click', async () => {
    const today = dayFromIso(isoToday()) as Day;
    const { used } = accounts(today);
    const code = exportCode(portfolioName || 'My credit', used);
    ($('code') as HTMLTextAreaElement).value = code;
    try { await navigator.clipboard.writeText(code); $('code-note').textContent = `Copied a code for ${plural(used.length, 'account')}. The command-line tool imports it too.`; }
    catch { ($('code') as HTMLTextAreaElement).select(); $('code-note').textContent = 'Select the code and copy it.'; }
  });
  $('import').addEventListener('click', () => {
    try {
      const { name, rows: imported } = importCode(($('code') as HTMLTextAreaElement).value);
      portfolioName = name; rows = imported; save(); render();
      $('code-note').textContent = `Imported ${plural(imported.length, 'account')} from "${name}".`;
    } catch (error) { $('code-note').textContent = (error as Error).message; }
  });
}

function setDefaults(): void {
  const today = dayFromIso(isoToday()) as Day;
  const [y, m, d] = ymdOf(today);
  ($('future-date') as HTMLInputElement).value = `${y + 2}-${pad(m)}-${pad(Math.min(d, 28))}`;
  ($('new-opened') as HTMLInputElement).value = isoFromDay(today);
  ($('new-measured') as HTMLInputElement).value = `${y + 1}-${pad(m)}-${pad(Math.min(d, 28))}`;
  const { spans } = accounts(today);
  const now = aaocDays(spans, today);
  const years = now === null ? 2 : ageFormat(now).years;
  ($('target-years') as HTMLInputElement).value = String(years + 1);
  ($('min-years') as HTMLInputElement).value = String(Math.max(0, years));
}

async function start(): Promise<void> {
  try {
    await loadCore('./aaoc_core.wasm');
  } catch (error) {
    $('status').textContent = `${(error as Error).message} Reload the page to try again.`;
    return;
  }
  $('status').hidden = true;
  $('app').hidden = false;
  $('wasm-size').textContent = `${Math.round(wasmBytes / 1024)} KB`;
  restore();
  setDefaults();
  wire();
  render();
  let resized = 0;
  window.addEventListener('resize', () => { cancelAnimationFrame(resized); resized = requestAnimationFrame(update); });
}

void start();
