import streamlit as st
import time
from game import (
    MAPS, COMPONENTS, GameState, npc_advice, simulate_cross,
    build_world_map, build_river_scene, draw_person_with_kite,
    draw_component_icon, draw_splash, EXPERTS
)


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


def menu_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 4em;'>🪁</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 3em;'>风筝渡河</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.5em; color: #666;'>像素风 · 挑战各大河流</p>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("开始游戏", use_container_width=True, type="primary"):
            st.session_state.screen = "map"
            st.rerun()


def map_screen():
    st.title("🌍 选择河流")
    world_img = build_world_map()
    if world_img is not None:
        st.image(world_img, use_container_width=True)
    st.markdown("---")
    cols = st.columns(4)
    for idx, (key, data) in enumerate(MAPS.items()):
        with cols[idx % 4]:
            if st.button(f"📍 {key}", key=f"map-{key}", use_container_width=True):
                st.session_state.state.map_key = key
                st.session_state.screen = "game"
                st.rerun()
            st.caption(f"风速:{data['wind']}m/s 水流:{data['flow']}")


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
        question = st.text_input("问题", "优化方案")
        col1, col2 = st.columns(2)
        if col1.button("付费-20￥", disabled=state.chats >= 3):
            if state.pay_for_chat(expert, True):
                tips, acc = npc_advice(state, expert, question)
                st.success(f"{expert}({int(acc*100)}%): {tips[0]}")
        if col2.button("白嫖", disabled=state.chats >= 3):
            if state.pay_for_chat(expert, False):
                tips, acc = npc_advice(state, expert, question)
                st.info(f"{expert}({int(acc*100)}%): {tips[0]}")
        st.caption(f"咨询: {state.chats}/3")
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
        assembled = ", ".join(state.assembled) if state.assembled else "无"
        st.info(f"已组装: {assembled}")
        if st.button("🚀 开始渡河", type="primary", use_container_width=True):
            st.session_state.game_running = True
            st.session_state.kite_pos = [300, 100]
            st.session_state.person_pos = [50, 250]
            st.session_state.splash_frame = -1
            st.rerun()
    else:
        scene = build_river_scene(state.map_key, 600, 300)
        if scene is not None:
            has_kite = "碳纤维骨架" in state.assembled or "轻质面料" in state.assembled
            draw_person_with_kite(
                scene, st.session_state.person_pos[0], st.session_state.person_pos[1],
                st.session_state.kite_pos[0], st.session_state.kite_pos[1], has_kite
            )
            if "高架" in state.assembled:
                for y in range(200, 250):
                    if 0 <= y < 300 and 0 <= 50 < 600:
                        scene[y, 50] = (139, 69, 19)
            if st.session_state.splash_frame >= 0:
                draw_splash(scene, st.session_state.person_pos[0], st.session_state.person_pos[1], st.session_state.splash_frame)
            st.image(scene, use_container_width=True)
        
        if st.session_state.result is None:
            st.markdown("**控制风筝 (AWSD)**")
            col1, col2, col3, col4 = st.columns(4)
            moved = False
            if col1.button("A 左"):
                st.session_state.kite_pos[0] = max(0, st.session_state.kite_pos[0] - 10)
                moved = True
            if col2.button("W 上"):
                st.session_state.kite_pos[1] = max(0, st.session_state.kite_pos[1] - 10)
                moved = True
            if col3.button("S 下"):
                st.session_state.kite_pos[1] = min(300, st.session_state.kite_pos[1] + 10)
                moved = True
            if col4.button("D 右"):
                st.session_state.kite_pos[0] = min(600, st.session_state.kite_pos[0] + 10)
                moved = True
            
            if moved:
                st.rerun()
            
            if st.button("✅ 完成渡河"):
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
                if st.session_state.splash_frame < 5:
                    st.session_state.splash_frame += 1
                    time.sleep(0.3)
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
