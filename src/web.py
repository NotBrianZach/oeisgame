from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import random
from urllib.parse import parse_qs, urlparse

from oeisgame import (
    Enemy,
    TurnResult,
    initialize_combat_deck,
    play_card,
    resolve_end_turn,
    start_turn,
    starter_enemies,
    starter_deck,
)


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
  <h1>OEISGame card-choice demo</h1>
  <p>Interactive battle turns using the shared combat engine.</p>
  <label>Enemy:
    <select id=\"enemy\"></select>
  </label>
  <button id=\"newRun\">Start Battle</button>
  <div class=\"row\" style=\"margin-top:12px\"> 
    <div class=\"panel\"><h3>State</h3><pre id=\"state\"></pre><div id=\"cards\"></div></div>
    <div class=\"panel\"><h3>Turn log</h3><pre id=\"timeline\"></pre></div>
  </div>
  <script>
    let battleId = null;
    async function loadEnemies(){
      const res = await fetch('/api/enemies');
      const data = await res.json();
      const select = document.getElementById('enemy');
      select.innerHTML = '';
      data.enemies.forEach((name, idx) => {
        const o = document.createElement('option');
        o.value = idx;
        o.textContent = name;
        select.appendChild(o);
      });
    }
    function render(data){
      document.getElementById('state').textContent =
        `Enemy: ${data.enemy}\nTurn: ${data.turn}/${data.max_turns}\nEnergy: ${data.energy}\nEnemy HP: ${data.enemy_hp}\nPlayer HP: ${data.player_hp}\nSequence: ${JSON.stringify(data.sequence)}`;
      const cards = document.getElementById('cards');
      cards.innerHTML = '';
      data.hand.forEach((card, idx) => {
        const b = document.createElement('button');
        b.textContent = `${card.name} (${card.cost})`;
        b.disabled = card.cost > data.energy || data.finished;
        b.onclick = () => playCard(idx);
        cards.appendChild(b);
      });
      const end = document.createElement('button');
      end.textContent = 'End Turn';
      end.disabled = data.finished;
      end.onclick = () => playCard(-1);
      cards.appendChild(end);
      document.getElementById('timeline').textContent = data.timeline.map(t =>
        `T${t.turn} ${t.cards.join(',')} seq=${JSON.stringify(t.sequence)}\n${t.note || ''}`).join('\n\n');
    }
    async function startBattle(){
      const enemy = document.getElementById('enemy').value || '0';
      const res = await fetch(`/api/start-battle?enemy=${enemy}`);
      const data = await res.json();
      battleId = data.battle_id;
      render(data);
    }
    async function playCard(index){
      if (!battleId) return;
      const res = await fetch(`/api/play?battle_id=${battleId}&choice=${index}`);
      const data = await res.json();
      render(data);
    }
    document.getElementById('newRun').addEventListener('click', startBattle);
    loadEnemies();
  </script>
</body>
</html>
"""

SESSIONS: dict[str, dict] = {}


def _timeline(history: list[TurnResult]) -> list[dict]:
    return [
        {
            "turn": t.turn,
            "cards": t.card_names,
            "sequence": t.sequence,
            "note": t.note,
            "intent": t.enemy_intent,
            "phase": t.enemy_phase,
        }
        for t in history
    ]


def _snapshot(session: dict) -> dict:
    hand = [{"name": c.name, "cost": c.cost} for c in session["deck_state"].hand]
    return {
        "battle_id": session["battle_id"],
        "enemy": session["enemy"].name,
        "turn": session["turn"],
        "max_turns": session["max_turns"],
        "energy": session["energy"],
        "enemy_hp": session["enemy_hp"],
        "player_hp": session["player_hp"],
        "sequence": session["sequence"],
        "hand": hand,
        "timeline": _timeline(session["history"]),
        "finished": session["finished"],
    }


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
        if parsed.path == "/api/enemies":
            self._json({"enemies": [enemy.name for enemy in starter_enemies()]})
            return
        if parsed.path == "/api/start-battle":
            query = parse_qs(parsed.query)
            enemy_idx = int(query.get("enemy", ["0"])[0])
            enemies = starter_enemies()
            enemy = enemies[max(0, min(enemy_idx, len(enemies) - 1))]
            battle_id = f"s{random.randrange(1_000_000_000)}"
            deck_state = initialize_combat_deck(starter_deck())
            start_turn(deck_state, hand_size=3)
            SESSIONS[battle_id] = {
                "battle_id": battle_id,
                "enemy": enemy,
                "turn": 1,
                "max_turns": 6,
                "energy": 3,
                "enemy_hp": 30,
                "player_hp": 12,
                "sequence": [1],
                "deck_state": deck_state,
                "history": [],
                "finished": False,
            }
            self._json(_snapshot(SESSIONS[battle_id]))
            return
        if parsed.path == "/api/play":
            query = parse_qs(parsed.query)
            battle_id = query.get("battle_id", [""])[0]
            choice = int(query.get("choice", ["-1"])[0])
            session = SESSIONS.get(battle_id)
            if session is None:
                self._json({"error": "unknown battle_id"})
                return
            if session["finished"]:
                self._json(_snapshot(session))
                return
            enemy: Enemy = session["enemy"]
            if choice >= 0:
                sequence, energy, card, damage, note = play_card(
                    sequence=session["sequence"],
                    enemy=enemy,
                    turn=session["turn"],
                    deck_state=session["deck_state"],
                    energy=session["energy"],
                    chooser=lambda *_args, **_kwargs: choice,
                )
                session["sequence"] = sequence
                session["energy"] = energy
                if card is not None:
                    session["enemy_hp"] -= damage
                if note:
                    session.setdefault("turn_notes", []).append(note)
            if choice == -1 or session["energy"] <= 0 or not session["deck_state"].hand:
                resolve_end_turn(session["deck_state"])
                passed = enemy.constraint(session["sequence"])
                if not passed:
                    session["player_hp"] -= 2
                turn_notes = session.pop("turn_notes", [])
                session["history"].append(
                    TurnResult(
                        turn=session["turn"],
                        card_names=["End Turn"],
                        sequence=list(session["sequence"]),
                        passed_constraint=passed,
                        damage_dealt=0,
                        energy_before=3,
                        energy_after=session["energy"],
                        hand_before=[],
                        enemy_intent=None,
                        telegraphed_intent=None,
                        enemy_phase=None,
                        note=" | ".join(turn_notes),
                    )
                )
                session["turn"] += 1
                if session["turn"] > session["max_turns"] or session["enemy_hp"] <= 0 or session["player_hp"] <= 0:
                    session["finished"] = True
                else:
                    start_turn(session["deck_state"], hand_size=3)
                    session["energy"] = 3
            self._json(_snapshot(session))
            return

        self.send_response(404)
        self.end_headers()


def run_server(port: int = 8080) -> None:
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"OEISGame web demo listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
