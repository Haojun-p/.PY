import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import io
from datetime import datetime
from data_storage import UserMark, add_mark, get_all_marks, get_marks_by_type
from vision_api import analyze_image_with_ai
from chat import chat_once
from roles import get_role_prompt
import importlib.util
import os

HANGZHOU_CENTER = [30.2741, 120.1551]


def init_state():
    if "screen" not in st.session_state:
        st.session_state.screen = "main"
    if "user_location" not in st.session_state:
        st.session_state.user_location = None
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
    if "image_analysis" not in st.session_state:
        st.session_state.image_analysis = None
    if "npc_discussion" not in st.session_state:
        st.session_state.npc_discussion = {}
    if "current_mark" not in st.session_state:
        st.session_state.current_mark = None


def create_hangzhou_map(marks=None):
    m = folium.Map(
        location=HANGZHOU_CENTER,
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    
    if marks:
        for mark in marks:
            color_map = {
                "road": "blue",
                "river": "cyan",
                "bridge": "green",
                "overpass": "orange",
                "crosswalk": "red"
            }
            color = color_map.get(mark.get("location_type", "road"), "blue")
            
            folium.CircleMarker(
                location=[mark["lat"], mark["lng"]],
                radius=8,
                popup=f"{mark.get('location_type', '未知')}\n{mark.get('timestamp', '')}",
                color=color,
                fill=True,
                fillColor=color
            ).add_to(m)
    
    return m


def main_screen():
    st.title("🏙️ 城市改造数据收集平台")
    st.markdown("**基于社会5.0理念 · 收集市民意愿 · 优化城市设计**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 杭州地图")
        marks = get_all_marks()
        m = create_hangzhou_map(marks)
        
        map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])
        
        if map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lng = map_data["last_clicked"]["lng"]
            st.session_state.user_location = {"lat": lat, "lng": lng}
            st.success(f"已选择位置: {lat:.6f}, {lng:.6f}")
    
    with col2:
        st.subheader("📊 数据统计")
        total_marks = len(marks)
        st.metric("总标记数", total_marks)
        
        type_counts = {}
        for mark in marks:
            loc_type = mark.get("location_type", "未知")
            type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
        
        for loc_type, count in type_counts.items():
            st.metric(loc_type, count)
        
        if st.button("📈 查看数据分析", use_container_width=True):
            st.session_state.screen = "analysis"
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("🎯 开始标记")
    st.markdown("""
    1. **获取定位**：在地图上点击选择位置，或手动输入坐标
    2. **拍摄照片**：使用摄像头拍摄需要标记的地点
    3. **AI识别**：系统自动识别道路、河流等
    4. **NPC讨论**：
       - **第一步**：与专家讨论如何用风筝过街/过河（社会5.0想象性方案）
       - **第二步**：讨论实际可行的改造方案（天桥/桥梁/斑马线等）
    5. **提交标记**：保存您的建议和讨论内容
    """)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("**获取定位方式：**\n1. 点击地图选择位置\n2. 或使用浏览器定位（需要授权）")
        
        lat_input = st.number_input("纬度", value=HANGZHOU_CENTER[0], format="%.6f", step=0.000001)
        lng_input = st.number_input("经度", value=HANGZHOU_CENTER[1], format="%.6f", step=0.000001)
        
        if st.button("📍 使用输入的位置", use_container_width=True):
            st.session_state.user_location = {"lat": lat_input, "lng": lng_input}
            st.success(f"已设置位置: {lat_input:.6f}, {lng_input:.6f}")
    
    with col_b:
        if st.button("📷 打开摄像头", use_container_width=True):
            st.session_state.screen = "camera"
            st.rerun()
    
    with col_c:
        if st.button("💬 查看所有标记", use_container_width=True):
            st.session_state.screen = "marks"
            st.rerun()


def camera_screen():
    st.title("📷 拍摄地点照片")
    
    if st.button("← 返回主界面"):
        st.session_state.screen = "main"
        st.rerun()
    
    st.markdown("**请拍摄需要标记的地点照片（道路、河流等）**")
    
    uploaded_file = st.camera_input("拍摄照片", label_visibility="visible")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state.captured_image = image
        st.image(image, caption="拍摄的照片", use_container_width=True)
        
        if st.button("🔍 AI识别图像", type="primary"):
            with st.spinner("AI正在分析图像..."):
                analysis = analyze_image_with_ai(image)
                st.session_state.image_analysis = analysis
                
                if analysis.get("success"):
                    st.success("识别完成！")
                    st.markdown("**AI分析结果：**")
                    st.text_area("", analysis.get("analysis", ""), height=200, disabled=True)
                else:
                    st.error(f"识别失败: {analysis.get('error', '未知错误')}")
        
        if st.session_state.image_analysis and st.session_state.user_location:
            st.markdown("---")
            st.subheader("💬 与NPC专家讨论")
            
            expert = st.selectbox("选择专家", ["物理学家", "工程师", "历史学家"])
            
            tab1, tab2 = st.tabs(["🪁 风筝方案讨论", "🏗️ 实际改造方案"])
            
            with tab1:
                st.markdown("**第一步：讨论如何用风筝过街/过河（社会5.0想象性方案）**")
                
                kite_context = f"""用户拍摄了一张城市地点的照片，位置在杭州 ({st.session_state.user_location['lat']:.6f}, {st.session_state.user_location['lng']:.6f})。

AI图像识别结果：
{st.session_state.image_analysis.get('analysis', '')}

这是一个基于社会5.0理念的想象性讨论。请根据你的专业背景，详细讨论：

**核心问题：如何用"风筝"作为过街/过河的创新方案？**

请从以下角度分析：
1. 这个地点的物理环境是否适合风筝方案？（考虑风速、地形、障碍物等）
2. 风筝系统的技术可行性（升力、控制、安全等）
3. 从历史或工程角度，是否有类似案例或启发？
4. 这个想象性方案的意义和价值

请用你的专业风格，详细、生动地讨论这个创新方案。"""
                
                if st.button(f"🪁 与{expert}讨论风筝方案", type="primary", key="kite_discuss"):
                    with st.spinner(f"正在与{expert}讨论风筝方案..."):
                        history = []
                        reply = chat_once(history, kite_context, role_name=expert)
                        if "kite_discussion" not in st.session_state.npc_discussion:
                            st.session_state.npc_discussion["kite_discussion"] = {}
                        st.session_state.npc_discussion["kite_discussion"][expert] = reply
                        st.success(f"**{expert}关于风筝方案的讨论：**")
                        st.markdown(reply)
                
                if "kite_discussion" in st.session_state.npc_discussion and expert in st.session_state.npc_discussion["kite_discussion"]:
                    st.markdown("**之前的讨论：**")
                    st.info(st.session_state.npc_discussion["kite_discussion"][expert])
            
            with tab2:
                st.markdown("**第二步：讨论实际可行的改造方案**")
                
                if "kite_discussion" not in st.session_state.npc_discussion or expert not in st.session_state.npc_discussion.get("kite_discussion", {}):
                    st.warning("⚠️ 请先完成第一步：风筝方案讨论")
                else:
                    kite_discussion = st.session_state.npc_discussion["kite_discussion"][expert]
                    
                    practical_context = f"""基于刚才关于"风筝过街/过河"的想象性讨论，现在请从实际角度分析：

刚才的风筝方案讨论：
{kite_discussion}

当前地点信息：
- 位置：杭州 ({st.session_state.user_location['lat']:.6f}, {st.session_state.user_location['lng']:.6f})
- AI识别：{st.session_state.image_analysis.get('analysis', '')}

请根据你的专业背景，讨论实际可行的改造方案：
1. 这里更适合建造什么设施？（天桥/桥梁/斑马线/其他）
2. 为什么这个方案更合适？（从技术、成本、实用性等角度）
3. 设计要点和注意事项
4. 与刚才讨论的风筝方案相比，实际方案的优势

请用你的专业风格，给出详细、实用的建议。"""
                    
                    if st.button(f"🏗️ 与{expert}讨论改造方案", type="primary", key="practical_discuss"):
                        with st.spinner(f"正在与{expert}讨论改造方案..."):
                            history = []
                            reply = chat_once(history, practical_context, role_name=expert)
                            if "practical_discussion" not in st.session_state.npc_discussion:
                                st.session_state.npc_discussion["practical_discussion"] = {}
                            st.session_state.npc_discussion["practical_discussion"][expert] = reply
                            st.success(f"**{expert}关于改造方案的建议：**")
                            st.markdown(reply)
                    
                    if "practical_discussion" in st.session_state.npc_discussion and expert in st.session_state.npc_discussion["practical_discussion"]:
                        st.markdown("**之前的讨论：**")
                        st.info(st.session_state.npc_discussion["practical_discussion"][expert])
            
            st.markdown("---")
            st.subheader("💾 提交标记")
            
            location_type = st.selectbox(
                "地点类型",
                ["road", "river", "bridge", "overpass", "crosswalk"]
            )
            
            suggestion = st.text_area("您的建议", placeholder="例如：这里需要建一座天桥...")
            
            if st.button("✅ 提交标记", type="primary"):
                if st.session_state.user_location:
                    kite_disc = ""
                    practical_disc = ""
                    
                    if "kite_discussion" in st.session_state.npc_discussion:
                        kite_disc = "\n\n".join([f"{k}: {v}" for k, v in st.session_state.npc_discussion["kite_discussion"].items()])
                    if "practical_discussion" in st.session_state.npc_discussion:
                        practical_disc = "\n\n".join([f"{k}: {v}" for k, v in st.session_state.npc_discussion["practical_discussion"].items()])
                    
                    npc_discussion_text = f"【风筝方案讨论】\n{kite_disc}\n\n【实际改造方案讨论】\n{practical_disc}"
                    
                    mark = UserMark(
                        lat=st.session_state.user_location["lat"],
                        lng=st.session_state.user_location["lng"],
                        timestamp=datetime.now().isoformat(),
                        location_type=location_type,
                        image_analysis=st.session_state.image_analysis.get("analysis") if st.session_state.image_analysis else None,
                        npc_discussion=npc_discussion_text,
                        suggestion=suggestion
                    )
                    add_mark(mark)
                    st.success("✅ 标记已保存！")
                    st.balloons()
                    st.session_state.screen = "main"
                    st.rerun()
                else:
                    st.error("请先选择位置")


def analysis_screen():
    st.title("📊 数据分析")
    
    if st.button("← 返回主界面"):
        st.session_state.screen = "main"
        st.rerun()
    
    marks = get_all_marks()
    
    if not marks:
        st.info("暂无数据")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("地点类型分布")
        type_counts = {}
        for mark in marks:
            loc_type = mark.get("location_type", "未知")
            type_counts[loc_type] = type_counts.get(loc_type, 0) + 1
        
        st.bar_chart(type_counts)
    
    with col2:
        st.subheader("时间分布")
        st.info(f"总标记数: {len(marks)}")
        st.info(f"最新标记: {marks[-1].get('timestamp', '未知') if marks else '无'}")
    
    st.markdown("---")
    st.subheader("📍 所有标记点")
    
    m = create_hangzhou_map(marks)
    st_folium(m, width=900, height=600)
    
    st.markdown("---")
    st.subheader("📋 标记详情")
    
    for idx, mark in enumerate(marks[-10:], 1):
        with st.expander(f"标记 #{len(marks)-10+idx}: {mark.get('location_type', '未知')} - {mark.get('timestamp', '')[:19]}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**位置**: {mark['lat']:.6f}, {mark['lng']:.6f}")
                st.write(f"**类型**: {mark.get('location_type', '未知')}")
            with col_b:
                if mark.get('suggestion'):
                    st.write(f"**建议**: {mark['suggestion']}")
                if mark.get('npc_discussion'):
                    st.write("**NPC讨论**: 已记录")


def marks_screen():
    st.title("📋 所有标记")
    
    if st.button("← 返回主界面"):
        st.session_state.screen = "main"
        st.rerun()
    
    marks = get_all_marks()
    
    if not marks:
        st.info("暂无标记")
        return
    
    for idx, mark in enumerate(reversed(marks), 1):
        with st.expander(f"标记 #{len(marks)-idx+1}: {mark.get('location_type', '未知')} - {mark.get('timestamp', '')[:19]}"):
            st.write(f"**位置**: {mark['lat']:.6f}, {mark['lng']:.6f}")
            st.write(f"**类型**: {mark.get('location_type', '未知')}")
            if mark.get('suggestion'):
                st.write(f"**建议**: {mark['suggestion']}")
            if mark.get('image_analysis'):
                st.write("**AI分析**:")
                st.text(mark['image_analysis'][:500] + "..." if len(mark.get('image_analysis', '')) > 500 else mark.get('image_analysis', ''))
            if mark.get('npc_discussion'):
                st.write("**NPC讨论**: 已记录")


def main():
    st.set_page_config(
        page_title="城市改造数据收集",
        page_icon="🏙️",
        layout="wide"
    )
    
    init_state()
    screen = st.session_state.screen
    
    if screen == "main":
        main_screen()
    elif screen == "camera":
        camera_screen()
    elif screen == "analysis":
        analysis_screen()
    elif screen == "marks":
        marks_screen()
    else:
        st.session_state.screen = "main"
        st.rerun()


if __name__ == "__main__":
    main()

