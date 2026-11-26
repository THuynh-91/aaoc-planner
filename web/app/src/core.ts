// The Rust core (web/core) loaded as WebAssembly, behind typed functions. The boundary is hand-written: accounts go
// into the module's memory as pairs of i32 (day opened, day closed or NO_CLOSE), and results come back as numbers.

export type Day = number;
export interface Span { opened: Day; closed: Day | null }

const NO_CLOSE = -2147483648;
const ALREADY = -2147483648;
const NEVER = -2147483647;
const NO_ACCOUNTS = -2147483646;

interface Exports {
  memory: WebAssembly.Memory;
  alloc(count: number): number;
  dealloc(ptr: number, count: number): void;
  wasm_days_from_civil(y: number, m: number, d: number): number;
  wasm_civil_from_days(day: number): number;
  wasm_add_months(day: number, months: number): number;
  wasm_aaoc_days(ptr: number, count: number, asOf: number): number;
  wasm_aaoc_days_with_new_account(ptr: number, count: number, openedNew: number, asOf: number): number;
  wasm_age_format(days: number): number;
  wasm_time_to_target(ptr: number, count: number, today: number, years: number, months: number): number;
  wasm_wait(today: number, day: number): number;
  wasm_earliest_new_account(ptr: number, count: number, today: number, years: number, months: number): number;
}

let core: Exports;
export let wasmBytes = 0;

export async function loadCore(url: string): Promise<void> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load the calculator (${response.status}).`);
  const bytes = await response.arrayBuffer();
  wasmBytes = bytes.byteLength;
  const { instance } = await WebAssembly.instantiate(bytes, {});
  core = instance.exports as unknown as Exports;
}

// Runs `fn` with the accounts written into the module's memory, then frees it.
function withAccounts<T>(spans: Span[], fn: (ptr: number, count: number) => T): T {
  const words = Math.max(1, spans.length * 2);
  const ptr = core.alloc(words);
  try {
    const view = new Int32Array(core.memory.buffer, ptr, words);
    spans.forEach((s, i) => { view[2 * i] = s.opened; view[2 * i + 1] = s.closed ?? NO_CLOSE; });
    return fn(ptr, spans.length);
  } finally {
    core.dealloc(ptr, words);
  }
}

export const dayOf = (y: number, m: number, d: number): Day => core.wasm_days_from_civil(y, m, d);
export function ymdOf(day: Day): [number, number, number] {
  const packed = core.wasm_civil_from_days(day);
  return [Math.floor(packed / 10000), Math.floor(packed / 100) % 100, packed % 100];
}
export const addMonths = (day: Day, months: number): Day => core.wasm_add_months(day, months);

/** The average age in days on `asOf` of the accounts opened by then, or null if none was. */
export function aaocDays(spans: Span[], asOf: Day): number | null {
  const v = withAccounts(spans, (p, n) => core.wasm_aaoc_days(p, n, asOf));
  return Number.isNaN(v) ? null : v;
}

export function aaocDaysWithNew(spans: Span[], openedNew: Day, asOf: Day): number | null {
  const v = withAccounts(spans, (p, n) => core.wasm_aaoc_days_with_new_account(p, n, openedNew, asOf));
  return Number.isNaN(v) ? null : v;
}

/** Whole years and months, as the Python package prints them. */
export function ageFormat(days: number): { years: number; months: number } {
  const packed = core.wasm_age_format(days);
  return { years: Math.floor(packed / 100), months: packed % 100 };
}

export type Reach = { kind: 'already' } | { kind: 'never' } | { kind: 'none' } | { kind: 'on'; day: Day; waitYears: number; waitMonths: number };

export function timeToTarget(spans: Span[], today: Day, years: number, months: number): Reach {
  const day = withAccounts(spans, (p, n) => core.wasm_time_to_target(p, n, today, years, months));
  if (day === ALREADY) return { kind: 'already' };
  if (day === NEVER) return { kind: 'never' };
  if (day === NO_ACCOUNTS) return { kind: 'none' };
  const wait = core.wasm_wait(today, day);
  return { kind: 'on', day, waitYears: Math.floor(wait / 100), waitMonths: wait % 100 };
}

export function earliestNewAccount(spans: Span[], today: Day, years: number, months: number): Day | null {
  const day = withAccounts(spans, (p, n) => core.wasm_earliest_new_account(p, n, today, years, months));
  return day === NEVER ? null : day;
}
