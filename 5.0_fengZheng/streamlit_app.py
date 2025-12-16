import streamlit as st
from game import MAPS, COMPONENTS, GameState, npc_advice, simulate_cross, build_map_image, EXPERTS


def init_state():
    if "state" not in st.session_state:
        st.session_state.state = GameState()
    if "pos" not in st.session_state:
        st.session_state.pos = [0, 0]
    if "screen" not in st.session_state:
        st.session_state.screen = "menu"
    if "result" not in st.session_state:
        st.session_state.result = None


def money_row():
    st.subheader("资金与状态")
    st.metric("资金(￥)", st.session_state.state.money)
    cols = st.columns(len(EXPERTS))
    for i, name in enumerate(EXPERTS):
        cols[i].progress(st.session_state.state.npc_mood[name] / 100, text=f"{name}心情")
    st.caption(f"已咨询 {st.session_state.state.chats}/3 次")


def map_picker():
    state = st.session_state.state
    st.subheader("地图选择")
    key = st.selectbox("选择河流", list(MAPS.keys()), index=list(MAPS.keys()).index(state.map_key))
    state.map_key = key
    env = MAPS[key]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("天气", env["weather"])
    c2.metric("湿度", env["humidity"])
    c3.metric("风速", f"{env['wind']} m/s")
    c4.metric("水流", env["flow"])
    img = build_map_image(key)
    if img is not None:
        st.image(img, caption=f"{key} 像素河流")


def shop_and_assemble():
    state = st.session_state.state
    st.subheader("商店与组装")
    cols = st.columns(2)
    with cols[0]:
        for comp in COMPONENTS:
            col_a, col_b, col_c = st.columns([2, 1, 1])
            col_a.text(f"{comp['name']}  ￥{comp['price']}")
            col_b.text(f"+面积{comp.get('area',0)} 稳定{comp.get('stability',0)} 控制{comp.get('control',0)} 高度{comp.get('height',0)}")
            if col_c.button("购买", key=f"buy-{comp['name']}"):
                ok = state.buy(comp["name"])
                if not ok:
                    st.warning("资金不足")
    with cols[1]:
        st.text("背包")
        for idx, item in enumerate(list(state.inventory)):
            if st.button(f"装配/卸下 {item}", key=f"asm-{idx}-{item}"):
                state.assemble(item)
        st.text(f"已组装: {', '.join(state.assembled) or '无'}")


def controls():
    st.subheader("飞行按键")
    c1, c2, c3 = st.columns(3)
    if c1.button("A 左"):
        st.session_state.pos[0] -= 1
    if c2.button("W 上"):
        st.session_state.pos[1] += 1
    if c3.button("D 右"):
        st.session_state.pos[0] += 1
    c4, c5, c6 = st.columns(3)
    if c4.button("S 下"):
        st.session_state.pos[1] -= 1
    st.caption(f"当前位置(x,y): {tuple(st.session_state.pos)}")


def expert_zone():
    state = st.session_state.state
    st.subheader("NPC 专家")
    expert = st.selectbox("选择专家", EXPERTS)
    question = st.text_input("你的问题", "帮我优化渡河方案")
    col1, col2 = st.columns(2)
    if col1.button("付费咨询 -20￥", disabled=state.chats >= 3):
        ok = state.pay_for_chat(expert, True)
        if ok:
            tips, acc = npc_advice(state, expert, question)
            st.success(f"{expert} (准确度{int(acc*100)}%): {' | '.join(tips)}")
        else:
            st.warning("咨询失败，检查次数或资金")
    if col2.button("白嫖问", disabled=state.chats >= 3):
        ok = state.pay_for_chat(expert, False)
        if ok:
            tips, acc = npc_advice(state, expert, question)
            st.info(f"{expert} (准确度{int(acc*100)}%): {' | '.join(tips)}")
        else:
            st.warning("已达次数上限")
    st.caption(f"记忆片段: {state.memory[expert][-2:]}")


def run_trial():
    state = st.session_state.state
    if st.button("起飞渡河"):
        st.session_state.result = simulate_cross(state)
    if st.session_state.result:
        result = st.session_state.result
        if result["success"]:
            st.balloons()
            st.success(f"成功! 得分{result['score']} 获得赏金{result['bounty']}￥ 星星{result['stars']}颗")
        else:
            st.error(f"失败，得分{result['score']}，落水动画：💧💦💦💦")
        st.json(result)
        if st.button("回主菜单"):
            st.session_state.clear()
            init_state()


def main():
    st.set_page_config(page_title="风筝渡河", page_icon="🪁", layout="wide")
    init_state()
    screen = st.session_state.screen

    if screen == "menu":
        st.title("🪁 风筝渡河")
        st.markdown("`像素风` · 挑战各大河流")
        st.markdown("▇▆▅▄▃▂▁ 河流彼岸在召唤 ▁▂▃▄▅▆▇")
        if st.button("开始游戏"):
            st.session_state.screen = "map"
    elif screen == "map":
        st.header("选择地图")
        map_picker()
        if st.button("进入装备与准备"):
            st.session_state.screen = "build"
    elif screen == "build":
        st.header("装备准备 · 像素工坊")
        money_row()
        map_picker()
        shop_and_assemble()
        controls()
        expert_zone()
        run_trial()
    else:
        st.session_state.screen = "menu"
        st.experimental_rerun()


if __name__ == "__main__":
    main()

