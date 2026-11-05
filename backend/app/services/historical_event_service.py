"""
PRAVAH 360 - Historical Event Replay & Cyclone Intelligence Service
Reconstructs verified historical event timelines:
1. Cyclone Murasu (Nov 2026): landfall, de-intensification to deep depression, residual lightning & rain
2. Cyclone Arnab (Historical Archive): Severe storm surge and coastal delta inundation
3. July 2022 Godavari Flood: 25.8 lakh cusecs historical crest
Provides step-by-step replay states without future data leakage for evaluation.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "reference", "historical_flood_events_godavari.json"))

class HistoricalEventService:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"historical_flood_events": []}

    def list_historical_events(self) -> List[Dict[str, Any]]:
        """List summary of available historical replay events."""
        results = []
        for ev in self.data.get("historical_flood_events", []):
            results.append({
                "event_id": ev.get("event_id"),
                "event_name": ev.get("event_name"),
                "river_system": ev.get("river_system"),
                "peak_date": ev.get("peak_date"),
                "steps_count": len(ev.get("timeline_steps", [])),
                "official_sources": ev.get("official_sources", [])
            })
        return results

    def get_event_timeline(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full step-by-step timeline and official bulletin milestones for an event."""
        for ev in self.data.get("historical_flood_events", []):
            if ev.get("event_id").lower() == event_id.lower():
                return ev
        return None

    def get_step_state(self, event_id: str, step_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves the exact state (official bulletin, model advisory, gauge, affected mandals)
        at a specific timestamp during historical replay.
        """
        ev = self.get_event_timeline(event_id)
        if not ev:
            return None
        steps = ev.get("timeline_steps", [])
        for s in steps:
            if s.get("step_id") == step_id:
                return {
                    "event_id": event_id,
                    "event_name": ev.get("event_name"),
                    "step_data": s,
                    "total_steps": len(steps),
                    "is_replay_mode": True,
                    "watermark": "HISTORICAL EVENT REPLAY MODE - RETROSPECTIVE INTELLIGENCE ONLY"
                }
        return None

historical_event_service = HistoricalEventService()
