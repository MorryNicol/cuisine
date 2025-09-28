import streamlit as st
from PIL import Image
import argparse
import os
from detect import detect
from search_food import search_food

if 'page' not in st.session_state:
    st.session_state.page = None
    st.skip = False
# 页面标题
st.title(":rice: 菜谱推荐")
# 添加绿色框作为介绍
intro_html = """
<div style="
    background-color: #d4edda; 
    border-left: 5px solid #28a745; 
    padding: 15px; 
    margin-top: 15px; 
    border-radius: 5px; 
    font-size: 16px;
    color: #155724;">
    <strong>使用说明：</strong> 在页面左侧上传食材图片，系统将自动识别食材种类，并为你推荐合适的菜谱。<br>&emsp;&emsp;&emsp;&emsp;&emsp; 食材识别大概需要3-5分钟，如不使用该功能可选择 “跳过图片上传”
</div>
"""
if st.session_state.page != "recipe":
    st.markdown(intro_html, unsafe_allow_html=True)

# 初始化命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str,
                    default='data/images', help='source')
opt = parser.parse_args()

# 文件上传
uploaded_file = st.sidebar.file_uploader(
    "上传图片", type=['png', 'jpeg', 'jpg'])
if uploaded_file is not None:
    is_valid = True
    with st.spinner(text='资源加载中...'):
        st.sidebar.image(uploaded_file)
        picture = Image.open(uploaded_file)
        picture = picture.save(f'data/images/{uploaded_file.name}')
        opt.source = f'data/images/{uploaded_file.name}'
elif st.skip:
    is_valid = True
else:
    if st.sidebar.button('跳过图片上传'):
        st.skip = True
        st.session_state.page = 'main'
        st.rerun()
    is_valid = False

# if  st.session_state.page == None:
#     if st.sidebar.button('跳过图片上传'):
#         is_valid = True
#         st.session_state.page = 'main2'

# if st.session_state.page == 'receipt':
#     is_valid = True

if is_valid:
    if st.session_state.page == None:
        st.session_state.page = "main"
    # 初始化会话状态
    if 'food_type' not in st.session_state:
        st.session_state.food_type = []
    if 'food_list' not in st.session_state:
        st.session_state.food_list = []
    if 'flavors' not in st.session_state:
        st.session_state.flavors = "咸"
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # 主页面逻辑
    if st.session_state.page == "main":
        # st.sidebar.image(uploaded_file)
        st.session_state.click_time = 0
        # 检测按钮和加载动画
        if uploaded_file is not None:
            st.session_state.food_type = ['请点击“开始检测”']
            if st.sidebar.button('开始检测'):
                with st.spinner("正在检测，请稍候..."):
                    st.session_state.food_type = detect(opt.source)  # 调用检测函数
                    st.session_state.food_list = st.session_state.food_type.copy()
                    if len(st.session_state.food_type) == 0:
                        st.session_state.food_type = ['抱歉，没有发现食材']
                        st.session_state.food_list = []
        else:
            st.session_state.food_type = ['未上传图片，请手动输入']


        if st.session_state.food_type:
            # 检测到的食材
            st.markdown("### 检测到的食材")
            st.write(", ".join(st.session_state.food_type))

            # 合并标题
            st.markdown("### 配置您的菜谱")

            # 两个输入框并排显示
            cols = st.columns([3, 2])  # 设置列比例
            with cols[0]:
                food_input = st.text_input(
                    "编辑食材列表（用逗号分隔）",
                    value="，".join(st.session_state.food_list)
                )
            with cols[1]:
                flavors = ["","酸", "甜", "辣", "咸", "苦"]
                selected_flavor = st.selectbox("选择口味", flavors)

            # 更新食材列表逻辑，右对齐按钮
            cols = st.columns([6.1, 1])  # 调整列宽比例
            with cols[1]:  # 将按钮放在右侧较窄的列
                if st.button("查看菜谱", help="点击后进入推荐菜谱页面"):
                    st.session_state.food_list = [
                        item.strip() for item in food_input.split("，") if item.strip()
                    ]
                    st.session_state.flavors = selected_flavor
                    st.session_state.page = "recipe"
                    st.rerun()
                    

    # 菜谱页面逻辑
    if st.session_state.page == "recipe":
        # 返回按钮
        if st.sidebar.button("返回"):
            st.session_state.page = "main"
            st.rerun()

        # 顶部标题和刷新按钮
        cols = st.columns([5, 1, 1])  # 分为两列
        with cols[0]:
            # # 渐变背景
            # # 使用大字体和 Emoji
            # st.markdown("""
            # <div style="
            #     color: #4CAF50; 
            #     text-align: left; 
            #     font-size: 28px; 
            #     font-weight: bold;"
            #     height: 0.5em;">
            #     🍽️ 推荐菜谱
            # </div>
            # """, unsafe_allow_html=True)
            pass
        
        if st.session_state.click_time >0:
            with cols[1]:
                # 刷新按钮使用 Unicode 图标
                # 添加 0.5 行高度的透明内容
                st.write('<div style="height: 0.5em;"></div>', unsafe_allow_html=True)
                if st.button("上一批"):
                    st.session_state.click_time -= 1
                    # recipe_df = search_food(st.session_state.food_list, st.session_state.flavors,st.session_state.click_time)
                    st.rerun()

        with cols[2]:
            # 刷新按钮使用 Unicode 图标
            # 添加 0.5 行高度的透明内容
            st.write('<div style="height: 0.5em;"></div>', unsafe_allow_html=True)
            if st.button("下一批"):
                st.session_state.click_time += 1
                # recipe_df = search_food(st.session_state.food_list, st.session_state.flavors,st.session_state.click_time)
                st.rerun()


        # 获取推荐菜谱数据
        recipe_df = search_food(st.session_state.food_list, st.session_state.flavors,st.session_state.click_time)
        if len(recipe_df) == 0:
            st.write('未匹配到合适菜谱，请点击 “返回” 重新编辑')

        # Display all recipes
        for idx, row in recipe_df.iterrows():
            # Format ingredients as a comma-separated string
            # ingredients = ", ".join(eval(row["ingredients_list"]))
            ingredients = ', '.join(row["ingredients_list"])
            short_steps = row["steps"][:100]
            full_steps = row["steps"]

            # HTML content for the recipe box
            recipe_html = f"""
            <div style="
                background-color: #f9f9f9; 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 20px; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
                display: flex;
                align-items: center;">
                <div style="flex: 1; padding-right: 20px;">
                    <img src="{row['image']}" alt="{row['title']}" style="width: 100%; border-radius: 10px;">
                </div>
                <div style="flex: 2;">
                    <h2 style="margin: 0; font-size: 1.5em;">{row['title']}</h2>
                    <p><strong>所需食材：</strong> {ingredients}</p>
                </div>
            </div>
            """

            # Render the HTML container
            st.html(recipe_html)

            # Add the expander for steps
            with st.expander("展开完整做法"):
                formatted_steps = full_steps.replace("\n", "<br>")
                st.markdown(formatted_steps, unsafe_allow_html=True)


            # Add a divider between recipes
            st.divider()

        # 返回按钮
        # if st.button("返回"):
        #     st.session_state.page = "main"
        #     st.rerun()
