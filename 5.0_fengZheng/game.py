
from dataclasses import dataclass, field
from typing import Dict, List


MAPS = {
    "长江": {"weather": "多云", "humidity": 0.7, "wind": 8, "flow": 6, "bounty": (650, 900)},
    "黄河": {"weather": "大风", "humidity": 0.4, "wind": 10, "flow": 7, "bounty": (700, 950)},
    "尼罗河": {"weather": "晴朗", "humidity": 0.5, "wind": 7, "flow": 5, "bounty": (600, 850)},
    "亚马逊河": {"weather": "雨", "humidity": 0.9, "wind": 6, "flow": 8, "bounty": (750, 1000)},
}

COMPONENTS = [
    {"name": "碳纤维骨架", "price": 220, "area": 2.0, "stability": 16, "weight": -2},
    {"name": "轻质面料", "price": 150, "area": 3.0, "stability": 5, "weight": -1},
    {"name": "加固拉线", "price": 90, "stability": 12},
    {"name": "尾翼", "price": 120, "control": 12},
    {"name": "滑轮", "price": 80, "control": 6},
    {"name": "高架", "price": 180, "height": 8},
]

EXPERTS = ["物理学家", "工程师", "历史学家"]


@dataclass
class GameState:
    money: int = 1000
    map_key: str = "长江"
    assembled: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    npc_mood: Dict[str, int] = field(default_factory=lambda: {x: 65 for x in EXPERTS})
    chats: int = 0
    memory: Dict[str, List[str]] = field(default_factory=lambda: {x: [] for x in EXPERTS})
    last_reply: str = ""

    def buy(self, name: str):
        comp = next((c for c in COMPONENTS if c["name"] == name), None)
        if not comp or comp["price"] > self.money:
            return False
        self.money -= comp["price"]
        self.inventory.append(name)
        return True

    def assemble(self, name: str):
        if name in self.assembled:
            self.assembled.remove(name)
        elif name in self.inventory:
            self.assembled.append(name)

    def pay_for_chat(self, expert: str, pay: bool):
        if self.chats >= 3:
            return False
        if pay and self.money < 20:
            return False
        if pay:
            self.money -= 20
            self.npc_mood[expert] = min(100, self.npc_mood[expert] + 12)
        else:
            self.npc_mood[expert] = max(10, self.npc_mood[expert] - 10)
        self.chats += 1
        return True


def _kite_stats(state: GameState):
    base = {"area": 6.0, "stability": 22, "control": 15, "weight": 10, "height": 0}
    for name in state.assembled:
        comp = next((c for c in COMPONENTS if c["name"] == name), None)
        if not comp:
            continue
        for k in ["area", "stability", "control", "height", "weight"]:
            base[k] += comp.get(k, 0)
    base["lift"] = base["area"] * 1.4 - base["weight"]
    return base


def npc_advice(state: GameState, expert: str, design: Dict):
    mood = state.npc_mood[expert]
    env = MAPS[state.map_key]
    accuracy = 1.0 if mood >= 70 else 0.75 if mood >= 40 else 0.5
    tips = [
        f"风速 {env['wind']}m/s，面积建议≥{8 + env['flow']*0.3:.1f}㎡",
        "保持骨架和拉线稳固，结构词里尽量含“稳定”",
        "湿度高时选轻质面料，控制要留尾翼或滑轮",
        "起飞高度越高越稳，高架有帮助",
    ]
    if accuracy < 1:
        tips = [t.replace("建议", "可能") for t in tips]
    state.memory[expert].append(f"{design}|{tips[0]}")
    return tips, accuracy


def simulate_cross(state: GameState):
    env = MAPS[state.map_key]
    stats = _kite_stats(state)
    score = stats["lift"] * env["wind"] * 0.6
    score += stats["stability"] * 1.2
    score += stats["control"]
    score += stats["height"] * 2 - env["flow"] * 5
    score -= env["humidity"] * 8
    success = score >= 140
    spent = 1000 - state.money
    bounty = int((env["bounty"][0] + env["bounty"][1]) / 2) if success else 0
    state.money += bounty
    stars = 0
    if success:
        stars += 1
        if state.chats > 0:
            stars += 1
        if spent <= 500:
            stars += 1
    return {"success": success, "score": int(score), "bounty": bounty, "stars": stars, "spent": spent, "stats": stats}


def build_map_image(key: str, size: int = 64):
    try:
        np = __import__("numpy")
    except ImportError:
        return None
    env = MAPS[key]
    seed = int(env["wind"] * 13 + env["flow"] * 7)
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:] = (34, 90, 34)
    for x in range(size):
        river_center = size // 2 + int((seed % 7) - 3)
        width = 12 + (seed % 5) + (x % 6)
        for y in range(size):
            if abs(y - river_center) < width:
                arr[y, x] = (24, 80, 180)
            if (x + y + seed) % 19 == 0:
                arr[y, x] = (200, 200, 180)
    return arr

