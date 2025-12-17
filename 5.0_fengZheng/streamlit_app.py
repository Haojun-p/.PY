import streamlit as st
import time
import importlib.util
import os

try:
    from streamlit_keyup import streamlit_keyup
    HAS_KEYUP = True
except ImportError:
    HAS_KEYUP = False

game_path = os.path.join(os.path.dirname(__file__), "game.py")
spec = importlib.util.spec_from_file_location("game", game_path)
game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)

MAPS = game.MAPS
COMPONENTS = game.COMPONENTS
GameState = game.GameState
npc_advice = game.npc_advice
simulate_cross = game.simulate_cross
build_world_map = game.build_world_map
build_river_scene = game.build_river_scene
draw_person_with_kite = game.draw_person_with_kite
draw_component_icon = game.draw_component_icon
draw_splash = game.draw_splash
EXPERTS = game.EXPERTS

def get_kite_stats(state):
    base = {"area": 6.0, "stability": 22, "control": 15, "weight": 10, "height": 0}
    for name in state.assembled:
        comp = next((c for c in COMPONENTS if c["name"] == name), None)
        if not comp:
            continue
        for k in ["area", "stability", "control", "height", "weight"]:
            base[k] += comp.get(k, 0)
    base["lift"] = base["area"] * 1.4 - base["weight"]
    return base


def init_state():
    if "state" not in st.session_state:
        st.session_state.state = GameState()
    if "screen" not in st.session_state:
        st.session_state.screen = "menu"
    if "game_running" not in st.session_state:
        st.session_state.game_running = False
    if "kite_pos" not in st.session_state:
        st.session_state.kite_pos = [300, 100]
    if "person_pos" not in st.session_state:
        st.session_state.person_pos = [50, 250]
    if "splash_frame" not in st.session_state:
        st.session_state.splash_frame = -1
    if "result" not in st.session_state:
        st.session_state.result = None
    if "move_speed" not in st.session_state:
        st.session_state.move_speed = 15
    if "last_key" not in st.session_state:
        st.session_state.last_key = None


def menu_screen():
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 4.5em;
        margin: 0.3em 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    .sub-title {
        text-align: center;
        font-size: 2em;
        color: #444;
        margin: 0.5em 0;
    }
    .desc {
        text-align: center;
        font-size: 1.3em;
        color: #666;
        margin: 1em 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("<div class='main-title'>🪁</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>风筝渡河</div>", unsafe_allow_html=True)
        st.markdown("<div class='desc'>像素风 · 挑战各大河流</div>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚀 开始游戏", use_container_width=True, type="primary"):
            st.session_state.screen = "map"
            st.rerun()


def map_screen():
    st.title("🌍 选择河流")
    world_img = build_world_map()
    if world_img is not None:
        st.image(world_img, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📍 点击选择挑战的河流")
    
    cols = st.columns(4)
    for idx, (key, data) in enumerate(MAPS.items()):
        with cols[idx % 4]:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                if st.button(f"📍 {key}", key=f"map-{key}", use_container_width=True):
                    st.session_state.state.map_key = key
                    st.session_state.screen = "game"
                    st.rerun()
            with col_b:
                st.caption(f"💰{data['bounty'][0]}-{data['bounty'][1]}￥")
            st.caption(f"🌬️{data['wind']}m/s | 💧{data['flow']} | ☁️{data['weather']}")


def game_screen():
    state = st.session_state.state
    env = MAPS[state.map_key]
    
    with st.sidebar:
        st.header("💰 资金")
        st.metric("", f"{state.money}￥")
        st.markdown("---")
        st.subheader("🛒 商店")
        for comp in COMPONENTS:
            icon = draw_component_icon(comp["name"])
            col1, col2 = st.columns([1, 3])
            with col1:
                if icon is not None:
                    st.image(icon, width=40)
            with col2:
                st.text(f"{comp['name']}\n￥{comp['price']}")
                if st.button("买", key=f"buy-{comp['name']}"):
                    if state.buy(comp["name"]):
                        st.success("购买成功")
                    else:
                        st.error("资金不足")
        st.markdown("---")
        st.subheader("🎒 背包")
        for idx, item in enumerate(list(state.inventory)):
            icon = draw_component_icon(item)
            col1, col2 = st.columns([1, 3])
            with col1:
                if icon is not None:
                    st.image(icon, width=30)
            with col2:
                if st.button(f"装/卸 {item}", key=f"asm-{idx}-{item}"):
                    state.assemble(item)
        st.markdown("---")
        st.subheader("👥 NPC专家")
        expert = st.selectbox("选择", EXPERTS)
        mood_icon = "😊" if state.npc_mood[expert] >= 70 else "😐" if state.npc_mood[expert] >= 40 else "😞"
        st.caption(f"心情: {mood_icon} {state.npc_mood[expert]}/100")
        question = st.text_input("问题", "帮我优化渡河方案")
        col1, col2 = st.columns(2)
        if col1.button("付费-20￥", disabled=state.chats >= 3):
            if state.pay_for_chat(expert, True):
                tips, acc = npc_advice(state, expert, question)
                st.success(f"**{expert}** (准确度{int(acc*100)}%):\n\n{tips[0]}")
        if col2.button("白嫖", disabled=state.chats >= 3):
            if state.pay_for_chat(expert, False):
                tips, acc = npc_advice(state, expert, question)
                st.info(f"**{expert}** (准确度{int(acc*100)}%):\n\n{tips[0]}")
        st.caption(f"咨询次数: {state.chats}/3")
        st.markdown("---")
        if st.button("🏠 回主菜单"):
            st.session_state.clear()
            init_state()
            st.session_state.screen = "menu"
            st.rerun()
    
    st.title(f"🌊 {state.map_key} · 渡河挑战")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("天气", env["weather"])
    col2.metric("风速", f"{env['wind']} m/s")
    col3.metric("水流", env["flow"])
    col4.metric("湿度", f"{env['humidity']*100:.0f}%")
    
    if not st.session_state.game_running:
        stats = get_kite_stats(state)
        assembled = ", ".join(state.assembled) if state.assembled else "无"
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"**已组装组件**: {assembled}")
        with col_b:
            st.info(f"**性能预览**: 升力{stats['lift']:.1f} | 稳定{stats['stability']:.0f} | 控制{stats['control']:.0f}")
        
        if st.button("🚀 开始渡河", type="primary", use_container_width=True):
            st.session_state.game_running = True
            st.session_state.kite_pos = [300, 100]
            st.session_state.person_pos = [50, 250]
            st.session_state.splash_frame = -1
            st.rerun()
    else:
        scene = build_river_scene(state.map_key, 900, 450)
        if scene is not None:
            has_kite = "碳纤维骨架" in state.assembled or "轻质面料" in state.assembled
            draw_person_with_kite(
                scene, st.session_state.person_pos[0], st.session_state.person_pos[1],
                st.session_state.kite_pos[0], st.session_state.kite_pos[1], has_kite
            )
            if "高架" in state.assembled:
                for y in range(300, 380):
                    if 0 <= y < 450 and 0 <= 50 < 900:
                        scene[y, 50] = (139, 69, 19)
                        if 0 <= 50 + 1 < 900:
                            scene[y, 50 + 1] = (101, 50, 15)
            if st.session_state.splash_frame >= 0:
                draw_splash(scene, st.session_state.person_pos[0], st.session_state.person_pos[1], st.session_state.splash_frame)
            
            st.image(scene, use_container_width=True)
        
        if st.session_state.result is None:
            stats = get_kite_stats(state)
            progress = min(100, int((st.session_state.kite_pos[0] / 900) * 100))
            
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("渡河进度", f"{progress}%")
            with col_info2:
                st.metric("当前位置", f"({st.session_state.kite_pos[0]}, {st.session_state.kite_pos[1]})")
            with col_info3:
                st.metric("升力", f"{stats['lift']:.1f}")
            
            if HAS_KEYUP:
                st.markdown("**控制风筝 (键盘 AWSD 或点击按钮)**")
            else:
                st.markdown("**控制风筝 (点击按钮)**")
            
            moved = False
            
            if HAS_KEYUP:
                key_pressed = streamlit_keyup(key="game_control", debounce=50)
                if key_pressed:
                    key = key_pressed.lower()
                    if key == 'a':
                        st.session_state.kite_pos[0] = max(0, st.session_state.kite_pos[0] - st.session_state.move_speed)
                        moved = True
                    elif key == 'w':
                        st.session_state.kite_pos[1] = max(0, st.session_state.kite_pos[1] - st.session_state.move_speed)
                        moved = True
                    elif key == 's':
                        st.session_state.kite_pos[1] = min(450, st.session_state.kite_pos[1] + st.session_state.move_speed)
                        moved = True
                    elif key == 'd':
                        st.session_state.kite_pos[0] = min(900, st.session_state.kite_pos[0] + st.session_state.move_speed)
                        moved = True
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
            if col1.button("⬅ A", use_container_width=True):
                st.session_state.kite_pos[0] = max(0, st.session_state.kite_pos[0] - st.session_state.move_speed)
                moved = True
            if col2.button("⬆ W", use_container_width=True):
                st.session_state.kite_pos[1] = max(0, st.session_state.kite_pos[1] - st.session_state.move_speed)
                moved = True
            if col3.button("⬇ S", use_container_width=True):
                st.session_state.kite_pos[1] = min(450, st.session_state.kite_pos[1] + st.session_state.move_speed)
                moved = True
            if col4.button("➡ D", use_container_width=True):
                st.session_state.kite_pos[0] = min(900, st.session_state.kite_pos[0] + st.session_state.move_speed)
                moved = True
            
            if moved:
                st.rerun()
            
            if col5.button("✅ 完成渡河", use_container_width=True, type="primary"):
                result = simulate_cross(state)
                st.session_state.result = result
                if not result["success"]:
                    st.session_state.splash_frame = 0
                st.rerun()
        else:
            result = st.session_state.result
            if result["success"]:
                st.balloons()
                st.success(f"🎉 成功! 得分:{result['score']} 赏金:{result['bounty']}￥ 星星:{'⭐' * result['stars']}")
            else:
                if st.session_state.splash_frame < 8:
                    st.session_state.splash_frame += 1
                    time.sleep(0.2)
                    st.rerun()
                st.error(f"❌ 失败! 得分:{result['score']} 落水了💧")
            st.json(result)
            if st.button("🔄 重新开始"):
                st.session_state.game_running = False
                st.session_state.result = None
                st.session_state.splash_frame = -1
                st.rerun()


def main():
    st.set_page_config(page_title="风筝渡河", page_icon="🪁", layout="wide")
    init_state()
    screen = st.session_state.screen
    
    if screen == "menu":
        menu_screen()
    elif screen == "map":
        map_screen()
    elif screen == "game":
        game_screen()
    else:
        st.session_state.screen = "menu"
        st.rerun()


if __name__ == "__main__":
    main()
