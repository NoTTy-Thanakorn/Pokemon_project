"""
data_manager.py
Saves ALL stats needed for the proposal's graphs:
  • steps walked per run (line graph)
  • encounters per run (histogram)
  • elemental move usage total (pie chart)
  • HP remaining at battle end (bar chart)
  • battle duration per battle (boxplot)
  • run history list (for History screen)
"""
import json, os, time


class DataManager:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path

    # ── default structure ─────────────────────────────────────────────
    def default_data(self):
        return {
            # aggregate totals
            "runs": 0, "wins": 0, "losses": 0,
            "total_catches": 0, "best_team_size": 0,
            "starter_usage": {}, "boss_usage": {}, "pokemon_caught": {},
            # per-run series  (list of values, one per run)
            "steps_per_run":      [],   # Graph 3: line graph
            "encounters_per_run": [],   # Graph 1: histogram
            # battle-level series (accumulated across all runs)
            "move_type_usage": {},      # Graph 2: pie chart
            "hp_remaining":    [],      # Graph 4: bar / scatter
            "battle_durations": [],     # Graph 5: boxplot  (seconds)
            # history: list of run-summary dicts
            "history": [],
        }

    # ── load / save ───────────────────────────────────────────────────
    def load(self):
        if not os.path.exists(self.file_path):
            return self.default_data()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return self.default_data()
        # backfill any missing keys
        for k, v in self.default_data().items():
            if k not in data:
                data[k] = v
        return data

    def save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ── per-session helpers ────────────────────────────────────────────
    def new_session(self):
        """Call at the start of each run to get a fresh session dict."""
        return {
            "steps": 0,
            "encounters": 0,
            "start_time": time.time(),
            "move_types": {},   # move_type -> count  (this run)
            "battle_start": None,
        }

    # ── aggregate updaters ────────────────────────────────────────────
    def add_run(self, data):       data["runs"] += 1
    def add_win(self, data):       data["wins"] += 1
    def add_loss(self, data):      data["losses"] += 1

    def add_starter(self, data, name):
        data["starter_usage"][name] = data["starter_usage"].get(name, 0) + 1

    def add_boss(self, data, name):
        data["boss_usage"][name] = data["boss_usage"].get(name, 0) + 1

    def add_catch(self, data, name):
        data["total_catches"] += 1
        data["pokemon_caught"][name] = data["pokemon_caught"].get(name, 0) + 1

    def update_best_team(self, data, size):
        if size > data["best_team_size"]:
            data["best_team_size"] = size

    # ── session-level tracking ────────────────────────────────────────
    def record_step(self, session):
        session["steps"] += 1

    def record_encounter(self, session):
        session["encounters"] += 1

    def record_move_use(self, session, move_type):
        session["move_types"][move_type] = session["move_types"].get(move_type, 0) + 1

    def start_battle_timer(self, session):
        session["battle_start"] = time.time()

    def end_battle_timer(self, session, data, hp_left):
        if session["battle_start"] is not None:
            dur = round(time.time() - session["battle_start"], 2)
            data["battle_durations"].append(dur)
            session["battle_start"] = None
        data["hp_remaining"].append(hp_left)

    # ── finalise run ──────────────────────────────────────────────────
    def finish_run(self, data, session, outcome, boss_name, party_size, starter_name):
        """Call when a run ends (win or loss). Appends to all series."""
        data["steps_per_run"].append(session["steps"])
        data["encounters_per_run"].append(session["encounters"])

        # accumulate move type usage into global dict
        for mt, cnt in session["move_types"].items():
            data["move_type_usage"][mt] = data["move_type_usage"].get(mt, 0) + cnt

        # run summary for history screen
        run_num = data["runs"]
        summary = {
            "run":       run_num,
            "outcome":   outcome,          # "WIN" / "LOSS"
            "starter":   starter_name,
            "boss":      boss_name,
            "steps":     session["steps"],
            "encounters":session["encounters"],
            "catches":   party_size - 1,   # exclude starter
            "duration":  round(time.time() - session["start_time"], 1),
        }
        data["history"].append(summary)
        # keep last 50 runs only
        data["history"] = data["history"][-50:]