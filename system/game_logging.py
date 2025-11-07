import json
import os
import threading
import uuid
from datetime import datetime, timezone


class EpisodeLogger:
    """Logger d'épisodes RL: écrit du JSON Lines pour rejouer/entraîner.

    API:
      - start_episode(meta)
      - log_step(step_dict)
      - log_transition(monster_id, s, a, r, s2, done, tick=None, pos=None)
      - log_event(event_type, **fields)
      - end_episode(outcome, summary=None)
    """

    def __init__(self, base_logs_dir: str = None):
        self._lock = threading.Lock()
        self._fh = None
        self.episode_id = None
        self.base_logs_dir = base_logs_dir or self._default_logs_dir()

    def _default_logs_dir(self) -> str:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target = os.path.join(repo_root, "logs", "episodes")
        os.makedirs(target, exist_ok=True)
        return target

    def _open_file(self):
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        day_dir = os.path.join(self.base_logs_dir, day)
        os.makedirs(day_dir, exist_ok=True)
        fn = os.path.join(day_dir, f"episode_{self.episode_id}.jsonl")
        self._fh = open(fn, "a", encoding="utf-8")

    def _write(self, obj: dict):
        if not self._fh:
            return
        self._fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self._fh.flush()

    def start_episode(self, meta: dict):
        with self._lock:
            if self._fh:
                # close previous
                try:
                    self._fh.close()
                except Exception:
                    pass
                self._fh = None
            self.episode_id = str(uuid.uuid4())
            self._open_file()
            payload = {
                "type": "episode_start",
                "ts": datetime.now(timezone.utc).isoformat(),
                "episode_id": self.episode_id,
                "meta": meta or {},
            }
            self._write(payload)

    def log_step(self, step: dict):
        with self._lock:
            payload = {
                "type": "step",
                "ts": datetime.now(timezone.utc).isoformat(),
                "episode_id": self.episode_id,
                "step": step or {},
            }
            self._write(payload)

    def log_transition(self, monster_id, s, a, r, s2, done, tick=None, pos=None,location=None):
        with self._lock:
            payload = {
                "type": "transition",
                "ts": datetime.now(timezone.utc).isoformat(),
                "episode_id": self.episode_id,
                "monster_id": monster_id,
                "s": s,
                "a": a,
                "r": r,
                "s2": s2,
                "done": bool(done),
            }
            if tick is not None:
                payload["tick"] = tick
            if pos is not None:
                payload["pos"] = pos
            if location is not None:
                payload["location"] = location 

            self._write(payload)

    def log_event(self, event_type: str, **fields):
        with self._lock:
            payload = {
                "type": "event",
                "event": event_type,
                "ts": datetime.now(timezone.utc).isoformat(),
                "episode_id": self.episode_id,
            }
            if fields:
                payload.update(fields)
            self._write(payload)

    def end_episode(self, outcome: str, summary: dict = None):
        with self._lock:
            payload = {
                "type": "episode_end",
                "ts": datetime.now(timezone.utc).isoformat(),
                "episode_id": self.episode_id,
                "outcome": outcome,
                "summary": summary or {},
            }
            self._write(payload)
            if self._fh:
                try:
                    self._fh.close()
                except Exception:
                    pass
            self._fh = None


_EPISODE_LOGGER = EpisodeLogger()


def get_episode_logger() -> EpisodeLogger:
    return _EPISODE_LOGGER


