import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class UserMark:
    lat: float
    lng: float
    timestamp: str
    location_type: str
    image_analysis: Optional[str] = None
    npc_discussion: Optional[str] = None
    suggestion: str = ""
    user_id: Optional[str] = None


DATA_FILE = os.path.join(os.path.dirname(__file__), "user_marks.json")


def load_marks() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_marks(marks: List[Dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(marks, f, ensure_ascii=False, indent=2)


def add_mark(mark: UserMark):
    marks = load_marks()
    marks.append(asdict(mark))
    save_marks(marks)


def get_marks_by_type(location_type: str) -> List[Dict]:
    marks = load_marks()
    return [m for m in marks if m.get("location_type") == location_type]


def get_all_marks() -> List[Dict]:
    return load_marks()

