import streamlit as st
import pandas as pd

# 初始化session_state变量
if 'blue_prob' not in st.session_state:
    st.session_state.blue_prob = 0.5
    st.session_state.red_prob = 0.5
    st.session_state.learning_rate = 0.15
    st.session_state.transition_counts = {
        '红': {'红': 1, '蓝': 1},
        '蓝': {'红': 1, '蓝': 1},
    }
    st.session_state.trend_table = pd.DataFrame(columns=[
        '期号', '开出颜色', '蓝概率', '红概率', '马尔可夫推荐', '系统综合推荐'])
    st.session_state.period = 1
    st.session_state.prev_color = None

st.title("🔴🔵 红蓝球预测器（网页版）")

# 用户选择输入颜色
latest_color = st.radio("请选择最新一期的颜色：", ['红', '蓝'])
if st.button("提交颜色并预测下一期"):
    blue_prob = st.session_state.blue_prob
    red_prob = st.session_state.red_prob
    learning_rate = st.session_state.learning_rate

    # ===== 贝叶斯更新 =====
    if latest_color == '蓝':
        blue_prob = blue_prob + learning_rate * red_prob
        red_prob = red_prob * (1 - learning_rate)
    else:
        red_prob = red_prob + learning_rate * blue_prob
        blue_prob = blue_prob * (1 - learning_rate)

    # 归一化
    total = blue_prob + red_prob
    blue_prob /= total
    red_prob /= total

    # ===== 马尔可夫 =====
    prev_color = st.session_state.prev_color
    transition_counts = st.session_state.transition_counts
    if prev_color is not None:
        transition_counts[prev_color][latest_color] += 1

    if prev_color is None:
        markov_recommend = '无'
    else:
        trans = transition_counts[prev_color]
        markov_recommend = '红' if trans['红'] > trans['蓝'] else '蓝'

    # ===== 综合推荐 =====
    if markov_recommend == '红':
        markov_red_prob = 1
        markov_blue_prob = 0
    elif markov_recommend == '蓝':
        markov_red_prob = 0
        markov_blue_prob = 1
    else:
        markov_red_prob = markov_blue_prob = 0.5

    combined_red = (red_prob + markov_red_prob) / 2
    combined_blue = (blue_prob + markov_blue_prob) / 2
    combined_recommend = '蓝' if combined_blue > combined_red else '红'

    # 添加新记录
    new_row = pd.DataFrame({
        '期号': [st.session_state.period],
        '开出颜色': [latest_color],
        '蓝概率': [round(blue_prob * 100, 2)],
        '红概率': [round(red_prob * 100, 2)],
        '马尔可夫推荐': [markov_recommend],
        '系统综合推荐': [combined_recommend]
    })
    st.session_state.trend_table = pd.concat([
        st.session_state.trend_table, new_row], ignore_index=True)

    # 更新状态
    st.session_state.period += 1
    st.session_state.prev_color = latest_color
    st.session_state.blue_prob = blue_prob
    st.session_state.red_prob = red_prob

# 显示预测结果表格
st.subheader("📊 历史走势与预测记录")
st.dataframe(st.session_state.trend_table, use_container_width=True)

# 显示当前预测值
if st.session_state.trend_table.shape[0] > 0:
    last_row = st.session_state.trend_table.iloc[-1]
    st.markdown(f"**当前贝叶斯蓝概率：{last_row['蓝概率']}%，红概率：{last_row['红概率']}%**")
    st.markdown(f"**马尔可夫推荐：{last_row['马尔可夫推荐']}**")
    st.markdown(f"### 🔮 系统预测下一期开出：{last_row['系统综合推荐']} 🔮")
