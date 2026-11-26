// Portfolio codes shared with the command-line tool: base64 of the JSON that `Portfolio.export_to_code` writes, with
// dates as MM-DD-YYYY. A code made here imports in the CLI, and one made there imports here.

export interface Row { name: string; type: string; opened: string; closed: string } // dates as YYYY-MM-DD ('' = open)

interface CodeAccount { name: string; date_opened: string; is_open: boolean; closed_date: string | null; type: string | null }

const toMdy = (iso: string): string => { const [y, m, d] = iso.split('-'); return `${m}-${d}-${y}`; };
const toIso = (mdy: string): string => {
  const m = /^(\d{2})-(\d{2})-(\d{4})$/.exec(mdy.trim());
  if (!m) throw new Error(`"${mdy}" is not an MM-DD-YYYY date`);
  return `${m[3]}-${m[1]}-${m[2]}`;
};

export function exportCode(name: string, rows: Row[]): string {
  const accounts: CodeAccount[] = rows.map((r) => ({
    name: r.name, date_opened: toMdy(r.opened), is_open: !r.closed,
    closed_date: r.closed ? toMdy(r.closed) : null, type: r.type || null,
  }));
  const json = JSON.stringify({ name, accounts });
  const bytes = new TextEncoder().encode(json);
  let binary = '';
  bytes.forEach((b) => { binary += String.fromCharCode(b); });
  return btoa(binary);
}

export function importCode(code: string): { name: string; rows: Row[] } {
  let data: unknown;
  try {
    const binary = atob(code.trim());
    data = JSON.parse(new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0))));
  } catch {
    throw new Error('That code is not a portfolio code.');
  }
  const d = data as { name?: unknown; accounts?: unknown };
  if (!d || typeof d !== 'object' || typeof d.name !== 'string' || !Array.isArray(d.accounts)) throw new Error('That code is missing the portfolio name or accounts.');
  const rows = (d.accounts as CodeAccount[]).map((a) => {
    if (!a || typeof a.name !== 'string' || typeof a.date_opened !== 'string') throw new Error('An account in the code is missing its name or date opened.');
    return { name: a.name, type: a.type ?? '', opened: toIso(a.date_opened), closed: a.is_open === false && a.closed_date ? toIso(a.closed_date) : '' };
  });
  return { name: d.name, rows };
}
