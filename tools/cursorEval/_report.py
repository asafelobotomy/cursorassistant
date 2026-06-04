"""HTML report from check results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.cursorEval._static import check_surface


def cmd_report(paths: list[str], output: str | None, fmt: str) -> int:
    records: list[dict] = []
    for raw in paths:
        target = Path(raw)
        if not target.is_file():
            print(f"cursorEval report: skip missing {raw}", file=sys.stderr)
            continue
        try:
            spec_rows, advisory_rows, level = check_surface(target)
        except SystemExit:
            continue
        surface_id = (
            target.stem if target.parent.name == "agents" else target.parent.name
        )
        for item_id, passed, detail in spec_rows:
            records.append(
                {
                    "surface": surface_id,
                    "check": item_id,
                    "pass": passed,
                    "detail": detail,
                    "type": "spec",
                    "compliance": level,
                }
            )
        for item_id, passed, detail in advisory_rows:
            records.append(
                {
                    "surface": surface_id,
                    "check": item_id,
                    "pass": passed,
                    "detail": detail,
                    "type": "advisory",
                    "compliance": level,
                }
            )

    if not records:
        print("cursorEval report: no check results", file=sys.stderr)
        return 1

    passed = sum(1 for row in records if row["pass"])
    total = len(records)

    if fmt == "json":
        print(json.dumps({"records": records, "passed": passed, "total": total}, indent=2))
        return 0

    data_json = json.dumps(records, indent=2).replace("</", "<\\/")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>cursorEval Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; padding: 1rem; background: #fafafa; }}
  h1 {{ margin-bottom: 0.25rem; }}
  #summary {{ margin-bottom: 1rem; color: #555; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
  th {{ background: #1e293b; color: #fff; padding: 0.4rem 0.8rem; text-align: left; }}
  td {{ border: 1px solid #ddd; padding: 0.35rem 0.8rem; }}
  tr:nth-child(even) {{ background: #f8fafc; }}
  .pass {{ color: #15803d; font-weight: 600; }}
  .fail {{ color: #b91c1c; font-weight: 600; }}
  .spec td:first-child {{ border-left: 3px solid #3b82f6; }}
</style>
</head>
<body>
<h1>cursorEval check report</h1>
<div id="summary"></div>
<table><thead>
  <tr><th>Surface</th><th>Type</th><th>Check</th><th>Pass</th><th>Detail</th></tr>
</thead><tbody id="tbody"></tbody></table>
<script>
const data = {data_json};
let pass = 0;
data.forEach(r => {{
  const tr = document.createElement('tr');
  if (r.type === 'spec') tr.className = 'spec';
  ['surface', 'type', 'check'].forEach(k => {{
    const td = document.createElement('td');
    td.textContent = r[k];
    tr.appendChild(td);
  }});
  const tdPass = document.createElement('td');
  tdPass.className = r.pass ? 'pass' : 'fail';
  tdPass.textContent = r.pass ? '\\u2713' : '\\u2717';
  tr.appendChild(tdPass);
  const tdDetail = document.createElement('td');
  tdDetail.textContent = r.detail;
  tr.appendChild(tdDetail);
  document.getElementById('tbody').appendChild(tr);
  if (r.pass) pass++;
}});
document.getElementById('summary').textContent =
  `${{pass}} passed, ${{data.length - pass}} failed (${{data.length}} checks)`;
</script>
</body></html>"""

    out_path = Path(output or "cursorEval-report.html")
    try:
        out_path.write_text(html, encoding="utf-8")
    except OSError as exc:
        print(f"cursorEval report: cannot write {out_path}: {exc}", file=sys.stderr)
        return 2
    print(f"Written: {out_path}  ({passed}/{total} checks passing)")
    return 0
