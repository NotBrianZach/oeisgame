from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from oeisgame import battle_timeline, play_battle, starter_enemies, starter_deck


HTML = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>OEISGame Web Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 24px; background:#0f172a; color:#e2e8f0; }
    .row { display:flex; gap:16px; align-items:flex-start; }
    .panel { background:#1e293b; padding:12px; border-radius:8px; min-width:260px; }
    button { background:#38bdf8; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; }
    pre { white-space:pre-wrap; }
  </style>
</head>
<body>
  <h1>OEISGame battle timeline</h1>
  <p>Thin web UI over shared combat engine.</p>
  <button id=\"run\">Run Demo Battle</button>
  <div class=\"row\" style=\"margin-top:12px\"> 
    <div class=\"panel\"><h3>Hand / Plays</h3><pre id=\"plays\"></pre></div>
    <div class=\"panel\"><h3>Enemy intent</h3><pre id=\"intent\"></pre></div>
    <div class=\"panel\"><h3>Sequence timeline</h3><pre id=\"timeline\"></pre></div>
  </div>
  <script>
    async function runDemo(){
      const res = await fetch('/api/demo-battle?enemy=0');
      const data = await res.json();
      document.getElementById('plays').textContent = data.timeline.map(t =>
        `Turn ${t.turn}: ${t.cards.join(', ')} (pass=${t.passed_constraint})`).join('\n');
      document.getElementById('intent').textContent = data.timeline.map(t =>
        `Turn ${t.turn}: ${t.phase || 'Base'} / ${t.intent || 'None'}`).join('\n');
      document.getElementById('timeline').textContent = data.timeline.map(t =>
        `Turn ${t.turn}: ${JSON.stringify(t.sequence)}\n  ${t.note || ''}`).join('\n');
    }
    document.getElementById('run').addEventListener('click', runDemo);
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/demo-battle":
            query = parse_qs(parsed.query)
            enemy_idx = int(query.get("enemy", ["0"])[0])
            enemies = starter_enemies()
            enemy = enemies[max(0, min(enemy_idx, len(enemies) - 1))]
            battle = play_battle(deck=starter_deck(), enemy=enemy, turns=6)
            self._json({"enemy": enemy.name, "timeline": battle_timeline(battle)})
            return

        self.send_response(404)
        self.end_headers()


def run_server(port: int = 8080) -> None:
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"OEISGame web demo listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
