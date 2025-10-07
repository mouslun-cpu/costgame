import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 頁面基本設定 ---
st.set_page_config(
    page_title="咖啡廳老闆就是你!",
    page_icon="☕",
    layout="wide"
)

# --- 2. 初始化 Session State ---
def initialize_game():
    st.session_state.clear()
    st.session_state.game_stage = 0
    st.session_state.teams_data = {}

if 'game_stage' not in st.session_state:
    initialize_game()

# --- 3. 定義遊戲資料 & 輔助函式 ---
direct_cost_options = {
    '咖啡豆': {'普通商用豆': 15, '中級莊園豆': 25, '頂級藝妓豆': 40},
    '牛奶': {'一般鮮乳': 5, '燕麥奶': 8, '不加奶': 0},
    '耗材': {'紙杯+杯蓋': 3}
}

def get_formatted_label(item, options):
    """產生選項標籤，附加價格 e.g., '普通商用豆 ($15)'"""
    return [f"{name} (${price})" for name, price in options.items()]

def parse_choice(selection):
    """從選擇的標籤中解析出原始名稱"""
    return selection.split(" ($")[0]

# --- 4. 側邊欄：角色選擇 ---
role = st.sidebar.radio("☕ 選擇你的角色", ["老師 (Instructor)", "學生 (Student)"], index=1)
st.sidebar.markdown("---")

# --- 5. 老師介面 (Instructor View) ---
if role == "老師 (Instructor)":
    st.title("👨‍🏫 咖啡廳老闆就是你! - 老師控制台")
    st.markdown("---")
    col1, col2, col3 = st.columns([1.2, 1.2, 2])
    with col1:
        if st.button("▶️ 開始第一關 (直接成本)"): st.session_state.game_stage = 1
        if st.button("▶️ 開始第二關 (間接成本)"): st.session_state.game_stage = 2
    with col2:
        if st.button("▶️ 開始第三關 (定價策略)"): st.session_state.game_stage = 3
    with col3:
        if st.button("🔄 重置遊戲", help="這將會清除所有隊伍的進度！"):
            initialize_game()
            st.rerun()

    st.header(f"目前遊戲進度：第 {st.session_state.game_stage} 關")
    st.markdown("---")
    st.header("📊 各隊伍進度與結果")

    if not st.session_state.teams_data:
        st.warning("目前還沒有任何隊伍提交資料。")
    else:
        display_data = []
        for team, data in st.session_state.teams_data.items():
            team_info = {"隊伍名稱": team}
            team_info.update(data)
            if 'estimated_indirect_costs' in data:
                team_info.update(data['estimated_indirect_costs'])
            display_data.append(team_info)

        df = pd.DataFrame(display_data).set_index("隊伍名稱")
        
        column_order_rename = {
            "direct_cost": "直接成本($)",
            "total_indirect_cost": "間接成本加總($)",
            "sales_forecast": "預估銷量(杯)",
            "profit_margin": "期望利潤率(%)",
            "final_price": "最終定價($)",
            "break_even_point": "損益兩平點(杯)",
            "forecast_bep_difference": "預估與損益差值(杯)"
        }
        
        display_columns = [col for col in column_order_rename.keys() if col in df.columns]
        df_display = df[display_columns].rename(columns=column_order_rename)
        
        st.dataframe(df_display, use_container_width=True)
        with st.expander("查看各隊間接成本估算詳情"):
            indirect_cost_cols = [col for col in ["租金","人事費用","營業費用","設備折舊","行銷費用"] if col in df.columns]
            if indirect_cost_cols:
                st.dataframe(df[indirect_cost_cols], use_container_width=True)

# --- 6. 學生介面 (Student View) ---
elif role == "學生 (Student)":
    st.title("☕ 咖啡廳老闆就是你!")
    team_name = st.text_input("首先，請輸入你的隊伍名稱：")

    if not team_name:
        st.info("請先輸入隊伍名稱以開始遊戲。")
        st.stop()
        
    if team_name not in st.session_state.teams_data:
        st.session_state.teams_data[team_name] = {}

    st.markdown(f"--- \n ### 歡迎你， **{team_name}** 隊！")

    if st.session_state.game_stage == 0:
        st.info("⏳ 請等待老師開始遊戲...")

    if st.session_state.game_stage >= 1:
        with st.form("stage1_form", border=False):
            st.header("第一關：打造你的咖啡 (直接成本)")
            choices = {}
            choices['咖啡豆'] = st.radio("1. 選擇咖啡豆", get_formatted_label('咖啡豆', direct_cost_options['咖啡豆']), horizontal=True)
            choices['牛奶'] = st.radio("2. 選擇牛奶", get_formatted_label('牛奶', direct_cost_options['牛奶']), horizontal=True)
            submitted1 = st.form_submit_button("計算並提交第一關")
            if submitted1:
                cost = 0
                cost += direct_cost_options['咖啡豆'][parse_choice(choices['咖啡豆'])]
                cost += direct_cost_options['牛奶'][parse_choice(choices['牛奶'])]
                cost += direct_cost_options['耗材']['紙杯+杯蓋']
                st.session_state.teams_data[team_name]['direct_cost'] = cost
                st.success(f"第一關提交成功！你選擇的咖啡每杯直接成本為：${cost} 元")

    if st.session_state.game_stage >= 2:
        with st.form("stage2_form", border=False):
            st.header("第二關：咖啡廳攻防戰 (間接成本)")
            st.info("利用你所有搜尋工具，在以下共同背景條件下，估算開店一個月的總花費吧！")
            
            costs = {}
            costs["租金"] = st.number_input("校園店面月租金", min_value=0, step=1000, help="地點：校園周邊、坪數：10坪")
            costs["人事費用"] = st.number_input("每月總人事費用", min_value=0, step=1000, help="正職1名、兼職2名")
            costs["營業費用"] = st.number_input("每月營業費用", min_value=0, step=500, help="水電、瓦斯、網路等")
            costs["設備折舊"] = st.number_input("每月設備折舊攤提", min_value=0, step=500, help="攤提時間統一設定3年")
            costs["行銷費用"] = st.number_input("每月行銷費用", min_value=0, step=500, help="開幕活動、社群廣告、傳單等")
            
            submitted2 = st.form_submit_button("提交成本估算")
            if submitted2:
                if any(c == 0 for c in costs.values()):
                    st.error("所有欄位都必須填寫一個大於0的估算值！")
                else:
                    total_indirect = sum(costs.values())
                    st.session_state.teams_data[team_name]['estimated_indirect_costs'] = costs
                    st.session_state.teams_data[team_name]['total_indirect_cost'] = total_indirect
                    st.success(f"成本估算提交成功！你估算的每月總間接成本為：${total_indirect:,.0f} 元")

    if st.session_state.game_stage >= 3:
        st.header("第三關：定價策略與風險評估")
        
        if 'direct_cost' not in st.session_state.teams_data[team_name]:
            st.error("⚠️ 錯誤：找不到您的第一關資料！請務必先完成並提交第一關（直接成本）的選擇。")
        elif 'total_indirect_cost' not in st.session_state.teams_data[team_name]:
            st.warning("⚠️ 請先完成並提交第二關（間接成本）的成本估算。")
        else:
            with st.form("stage3_part1_form", border=False):
                st.subheader("Part 1: 策略擬定")
                sales_forecast = st.number_input("1. 你預估一個月能賣出幾杯咖啡？", min_value=1, value=1000, step=100)
                profit_margin = st.slider("2. 你期望每杯咖啡的利潤率是多少？", min_value=0, max_value=200, value=50, step=5, format="%d%%")
                submitted3_part1 = st.form_submit_button("完成策略擬定，查看建議售價")
                
                if submitted3_part1:
                    direct_cost = st.session_state.teams_data[team_name]['direct_cost']
                    total_indirect = st.session_state.teams_data[team_name]['total_indirect_cost']
                    
                    allocated_indirect = total_indirect / sales_forecast
                    total_cost_per_cup = direct_cost + allocated_indirect
                    suggested_price = total_cost_per_cup * (1 + profit_margin / 100)
                    
                    st.session_state.teams_data[team_name].update({
                        'sales_forecast': sales_forecast, 'profit_margin': profit_margin,
                        'suggested_price': round(suggested_price)
                    })
            
            if 'suggested_price' in st.session_state.teams_data[team_name]:
                st.subheader("Part 2: 風險評估與最終定價")
                
                # =========== ✨ 更新後的策略回顧區塊 START ✨ ===========
                st.markdown("##### 你的策略回顧：")
                review_cols = st.columns(5)
                team_data = st.session_state.teams_data[team_name]
                
                # 計算需要的值
                allocated_indirect_cost = team_data['total_indirect_cost'] / team_data['sales_forecast']
                total_cost_per_cup = team_data['direct_cost'] + allocated_indirect_cost

                review_cols[0].metric("每杯直接成本", f"${team_data['direct_cost']}")
                review_cols[1].metric("每杯間接成本", f"${allocated_indirect_cost:.1f}", help="總間接成本 / 預估月銷量")
                review_cols[2].metric("每杯總成本", f"${total_cost_per_cup:.1f}", help="每杯直接成本 + 每杯間接成本")
                review_cols[3].metric("預估月銷量", f"{team_data['sales_forecast']:,} 杯")
                review_cols[4].metric("期望利潤率", f"{team_data['profit_margin']}%")
                st.markdown("---")
                # =========== ✨ 更新後的策略回顧區塊 END ✨ ===========

                suggested_price = st.session_state.teams_data[team_name]['suggested_price']
                
                with st.form("stage3_part2_form", border=False):
                    st.info(f"根據你的策略，系統計算出的建議售價為 ${suggested_price} 元。")
                    st.caption(f"計算方式：(每杯總成本) * (1 + 利潤率)")
                    
                    final_price = st.number_input("請決定你的最終售價（可修改）", min_value=1, value=suggested_price)
                    submitted3_part2 = st.form_submit_button("提交最終定價，進行損益分析")

                    if submitted3_part2:
                        direct_cost = st.session_state.teams_data[team_name]['direct_cost']
                        total_indirect = st.session_state.teams_data[team_name]['total_indirect_cost']
                        sales_forecast = st.session_state.teams_data[team_name]['sales_forecast']
                        
                        contribution_margin = final_price - direct_cost
                        break_even_point = total_indirect / contribution_margin if contribution_margin > 0 else float('inf')
                        forecast_bep_difference = sales_forecast - break_even_point

                        st.session_state.teams_data[team_name].update({
                            'final_price': final_price,
                            'break_even_point': round(break_even_point),
                            'forecast_bep_difference': round(forecast_bep_difference)
                        })

                        st.success("最終定價完成！這是你的損益分析：")
                        cols = st.columns(2)
                        cols[0].metric("損益兩平點 (杯)", f"{round(break_even_point):,}")
                        cols[1].metric("預估與損益差值 (杯)", f"{round(forecast_bep_difference):,}", 
                                       help="正數代表你的預估銷量高於損益兩平點，為獲利安全區；負數則為虧損風險區。")

                        st.subheader("損益兩平視覺化分析圖")
                        max_cups = max(int(break_even_point * 1.5), sales_forecast + 200)
                        cups_sold = list(range(0, max_cups, max(1, max_cups // 100)))
                        if max_cups not in cups_sold: cups_sold.append(max_cups)
                        
                        total_revenue = [final_price * c for c in cups_sold]
                        total_cost = [total_indirect + direct_cost * c for c in cups_sold]
                        
                        chart_data = pd.DataFrame({'銷售杯數': cups_sold, '總收入': total_revenue, '總成本': total_cost})
                        
                        fig = px.line(chart_data, x='銷售杯數', y=['總收入', '總成本'],
                                      title='總收入 vs 總成本分析圖',
                                      labels={'value': '金額 ($)', 'variable': '項目'},
                                      color_discrete_map={'總收入': '#1f77b4', '總成本': '#2ca02c'})

                        fig.add_vline(x=round(break_even_point), line_dash="dash", line_color="grey", 
                                      annotation_text=f"損益兩平點: {round(break_even_point)} 杯")
                        fig.add_vline(x=sales_forecast, line_dash="dash", line_color="red",
                                      annotation_text=f"你的預估銷量: {sales_forecast} 杯")

                        fig.update_layout(legend_title_text='')
                        st.plotly_chart(fig, use_container_width=True)
                        st.info(
                            """
                            **如何看懂這張圖：**
                            - **藍線 (總收入):** 你賣得越多，總收入越高。
                            - **綠線 (總成本):** 即使一杯都沒賣，你也要負擔固定的間接成本，所以起點較高。
                            - **灰色虛線 (損益兩平點):** 兩線交叉點，在此之前虧損，在此之後盈利。
                            - **紅色虛線 (你的預估銷量):** 這是你設定的目標，看看它落在安全區還是風險區！
                            """
                        )