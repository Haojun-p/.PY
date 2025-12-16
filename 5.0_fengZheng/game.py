
from dataclasses import dataclass, field
from typing import Dict, List


MAPS = {
    "长江": {"weather": "多云", "humidity": 0.7, "wind": 8, "flow": 6, "bounty": (650, 900), "pos": (0.75, 0.45)},
    "黄河": {"weather": "大风", "humidity": 0.4, "wind": 10, "flow": 7, "bounty": (700, 950), "pos": (0.72, 0.38)},
    "尼罗河": {"weather": "晴朗", "humidity": 0.5, "wind": 7, "flow": 5, "bounty": (600, 850), "pos": (0.52, 0.55)},
    "亚马逊河": {"weather": "雨", "humidity": 0.9, "wind": 6, "flow": 8, "bounty": (750, 1000), "pos": (0.28, 0.65)},
    "密西西比河": {"weather": "多云", "humidity": 0.6, "wind": 9, "flow": 7, "bounty": (680, 920), "pos": (0.22, 0.42)},
    "多瑙河": {"weather": "晴朗", "humidity": 0.5, "wind": 8, "flow": 5, "bounty": (620, 880), "pos": (0.48, 0.32)},
    "恒河": {"weather": "雨", "humidity": 0.8, "wind": 7, "flow": 6, "bounty": (640, 900), "pos": (0.68, 0.52)},
    "伏尔加河": {"weather": "大风", "humidity": 0.4, "wind": 11, "flow": 6, "bounty": (720, 980), "pos": (0.58, 0.28)},
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


def build_world_map():
    try:
        np = __import__("numpy")
    except ImportError:
        return None
    w, h = 800, 500
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:] = (20, 60, 120)
    for y in range(h):
        for x in range(w):
            if 50 < y < h - 50 and 50 < x < w - 50:
                arr[y, x] = (34, 90, 34)
            if (x + y) % 40 < 2:
                arr[y, x] = (200, 200, 180)
    for key, data in MAPS.items():
        px, py = int(data["pos"][0] * w), int(data["pos"][1] * h)
        for dy in range(-8, 9):
            for dx in range(-8, 9):
                if 0 <= px + dx < w and 0 <= py + dy < h:
                    if dx * dx + dy * dy < 64:
                        arr[py + dy, px + dx] = (180, 60, 60)
    return arr


def build_river_scene(key: str, width: int = 600, height: int = 300):
    try:
        np = __import__("numpy")
    except ImportError:
        return None
    env = MAPS[key]
    seed = int(env["wind"] * 13 + env["flow"] * 7)
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    arr[:] = (135, 206, 235)
    sky_h = height // 3
    arr[:sky_h, :] = (135, 206, 250)
    for y in range(sky_h, height):
        for x in range(width):
            if abs(y - height * 0.6) < 30 + (x % 40) * 0.3:
                arr[y, x] = (24, 80, 180)
            elif y > height * 0.7:
                arr[y, x] = (34, 90, 34)
    for x in range(0, width, 3):
        wave_y = int(height * 0.6 + (x * 0.1 + seed) % 8 - 4)
        if 0 <= wave_y < height:
            arr[wave_y, x] = (200, 220, 255)
    return arr


def draw_person_with_kite(arr, x: int, y: int, kite_x: int, kite_y: int, has_kite: bool = True):
    try:
        np = __import__("numpy")
    except ImportError:
        return
    h, w, _ = arr.shape
    if 0 <= y < h and 0 <= x < w:
        arr[y, x] = (139, 69, 19)
        if 0 <= y + 1 < h:
            arr[y + 1, x] = (255, 220, 177)
        if 0 <= y + 2 < h:
            arr[y + 2, x] = (50, 50, 50)
    if has_kite and 0 <= kite_y < h and 0 <= kite_x < w:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 <= kite_y + dy < h and 0 <= kite_x + dx < w:
                    if abs(dx) + abs(dy) < 4:
                        arr[kite_y + dy, kite_x + dx] = (255, 100, 100)
        if abs(kite_x - x) + abs(kite_y - y) > 5:
            mid_x, mid_y = (x + kite_x) // 2, (y + kite_y) // 2
            if 0 <= mid_y < h and 0 <= mid_x < w:
                arr[mid_y, mid_x] = (200, 200, 200)


def draw_component_icon(name: str, size: int = 32):
    try:
        np = __import__("numpy")
    except ImportError:
        return None
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:] = (240, 240, 240)
    if "骨架" in name:
        for i in range(size):
            arr[i, i] = (100, 100, 100)
            arr[i, size - 1 - i] = (100, 100, 100)
    elif "面料" in name:
        arr[size//4:3*size//4, size//4:3*size//4] = (200, 150, 150)
    elif "拉线" in name:
        for i in range(0, size, 4):
            arr[i, size//2] = (150, 150, 150)
    elif "尾翼" in name:
        arr[size//2:, size//2:] = (255, 150, 150)
    elif "滑轮" in name:
        arr[size//2-2:size//2+2, size//2-2:size//2+2] = (100, 100, 100)
    elif "高架" in name:
        arr[size-4:, size//2-2:size//2+2] = (139, 69, 19)
        arr[size//2:, size//2-1:size//2+1] = (139, 69, 19)
    return arr


def draw_splash(arr, x: int, y: int, frame: int = 0):
    try:
        np = __import__("numpy")
    except ImportError:
        return
    h, w, _ = arr.shape
    splash_size = 8 + frame * 2
    for dy in range(-splash_size, splash_size + 1):
        for dx in range(-splash_size, splash_size + 1):
            if 0 <= y + dy < h and 0 <= x + dx < w:
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < splash_size and (dx + dy + frame) % 3 == 0:
                    arr[y + dy, x + dx] = (200, 220, 255)


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

