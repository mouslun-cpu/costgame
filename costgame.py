import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random

# --- 1. 遊戲參數設定 ---
GAME_CONFIG = {
    'styles': {
        'A': {'label': 'A. 校門口黃金店面 (旗艦店)', 'rent': 50000, 'depreciation': 20000, 'base_traffic': 3000},
        'B': {'label': 'B. 側門舒適店面 (標準店)', 'rent': 25000, 'depreciation': 12000, 'base_traffic': 1500},
        'C': {'label': 'C. 巷弄老宅咖啡 (風格店)', 'rent': 10000, 'depreciation': 5000, 'base_traffic': 500}
    },
    'beans': {'普通商用豆': 15, '中級莊園豆': 25, '頂級藝妓豆': 40},
    'milks': {'一般鮮乳': 5, '燕麥奶': 8, '不加奶': 0},
    'material': 3
}

# --- 2. 初始化 Session State (單人模式) ---
st.set_page_config(page_title="咖啡廳老闆就是你!", page_icon="☕")

if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 1
if 'my_cafe_data' not in st.session_state:
    st.session_state.my_cafe_data = {}
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

def reset_game():
    st.session_state.current_stage = 1
    st.session_state.my_cafe_data = {}
    st.session_state.game_started = False
    if 'my_cafe_name' in st.session_state:
        del st.session_state.my_cafe_name

# --- 3. 輔助函式 ---
def get_style_label(key): return GAME_CONFIG['styles'][key]['label']
def get_bean_label(key): return f"{key} (${GAME_CONFIG['beans'][key]})"
def get_milk_label(key): return f"{key} (${GAME_CONFIG['milks'][key]})"

def predict_sales(style_key, price, marketing_budget):
    base = GAME_CONFIG['styles'][style_key]['base_traffic']
    price_factor = (150 - price) * 18 
    if style_key == 'A':   marketing_effect = np.sqrt(marketing_budget) * 1
    elif style_key == 'B': marketing_effect = np.sqrt(marketing_budget) * 5
    else:
        if marketing_budget < 3000: marketing_effect = -300 + (marketing_budget / 3000) * 300
        else: marketing_effect = np.sqrt(marketing_budget) * 10
    predicted = base + price_factor + marketing_effect
    min_guarantee = int(marketing_budget / 500)
    return int(max(min_guarantee, min(10000, predicted)))

# =========================================
#      學生單人遊玩介面
# =========================================

if not st.session_state.game_started:
    st.title("☕ 咖啡廳老闆就是你!")
    st.image("https://images.unsplash.com/photo-1511920181103-101a03da40f2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wzNTg5fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA&ixlib=rb-4.0.3&q=80&w=1080", caption="準備好成為咖啡大亨了嗎？")
    
    cafe_name_input = st.text_input("請輸入你的「咖啡廳」名稱：")
    if st.button("創立我的咖啡廳！", use_container_width=True):
        if cafe_name_input:
            st.session_state.my_cafe_name = cafe_name_input
            st.session_state.game_started = True
            st.session_state.current_stage = 1
            st.session_state.my_cafe_data = {}
            st.rerun()
        else:
            st.error("請給你的咖啡廳一個響亮的名號！")
    st.stop()

team_data = st.session_state.my_cafe_data
team_name = st.session_state.my_cafe_name
st.title(f"☕ {team_name} (營運中)")

if st.button("🔄 重新開一家店 (重置遊戲)", type="primary"):
    reset_game()
    st.rerun()

st.markdown("---")

# --- S1: 定位 ---
s1_completed = 'style' in team_data
s1_label = f"第一關：打造你的咖啡廳 {'(已完成)' if s1_completed else ''}"
is_current_s1 = (st.session_state.current_stage == 1)

with st.expander(s1_label, expanded=is_current_s1):
    with st.form("stage1_form"):
        st.subheader("📍 選擇店面風格")
        style = st.radio("店址決定你的基本客群", GAME_CONFIG['styles'].keys(), format_func=get_style_label, index=list(GAME_CONFIG['styles'].keys()).index(team_data.get('style', 'A')))
        st.subheader("☕ 設計招牌咖啡")
        bean_idx = list(GAME_CONFIG['beans'].keys()).index(team_data.get('bean', '普通商用豆'))
        milk_idx = list(GAME_CONFIG['milks'].keys()).index(team_data.get('milk', '一般鮮乳'))
        bean = st.radio("選擇咖啡豆", GAME_CONFIG['beans'].keys(), format_func=get_bean_label, index=bean_idx)
        milk = st.radio("選擇搭配乳品", GAME_CONFIG['milks'].keys(), format_func=get_milk_label, index=milk_idx)
        
        if st.form_submit_button("確認/更新打造", use_container_width=True, disabled=not is_current_s1):
            dc = GAME_CONFIG['beans'][bean] + GAME_CONFIG['milks'][milk] + GAME_CONFIG['material']
            team_data.update({'style': style, 'bean': bean, 'milk': milk, 'direct_cost': dc})
            st.success(f"打造完成！每杯直接成本 ${dc}")
            if st.session_state.current_stage == 1:
                st.session_state.current_stage = 2
            st.rerun()

# --- S2: 成本 ---
if 'style' in team_data:
    s2_completed = 'total_indirect_cost' in team_data
    s2_label = f"第二關：成本估算 {'(已完成)' if s2_completed else ''}"
    is_current_s2 = (st.session_state.current_stage == 2)
    
    with st.expander(s2_label, expanded=is_current_s2):
        style_cfg = GAME_CONFIG['styles'][team_data['style']]
        with st.form("stage2_form"):
            st.info(f"已鎖定 **【{style_cfg['label']}】** 的租金與折舊。")
            rent = st.number_input("店面租金", value=style_cfg['rent'], disabled=True)
            dep = st.number_input("設備折舊", value=style_cfg['depreciation'], disabled=True)
            est = team_data.get('estimated_indirect', {})
            staff = st.number_input("人事費用", min_value=0, step=5000, value=est.get('人事', 30000))
            op = st.number_input("營業費用", min_value=0, step=1000, value=est.get('營業', 10000))
            mkt = st.number_input("行銷費用", min_value=0, step=1000, value=est.get('行銷', 5000))
            
            if st.form_submit_button("提交/更新預算", use_container_width=True, disabled=not is_current_s2):
                total = rent + dep + staff + op + mkt
                team_data.update({'estimated_indirect': {'租金': rent, '折舊': dep, '人事': staff, '營業': op, '行銷': mkt}, 'total_indirect_cost': total})
                st.success(f"預算完成！每月固定成本 ${total:,}")
                if st.session_state.current_stage == 2:
                    st.session_state.current_stage = 3
                st.rerun()

# --- S3: 定價 ---
if 'total_indirect_cost' in team_data:
    s3_completed = 'ai_predicted_sales' in team_data
    s3_label = f"第三關：定價策略與市場模擬 {'(已完成)' if s3_completed else ''}"
    is_current_s3 = (st.session_state.current_stage == 3)
    
    with st.expander(s3_label, expanded=is_current_s3):
        # 只有在 S3 未完成時，才顯示表單
        if not s3_completed:
            with st.form("stage3_p1"):
                st.subheader("Part 1: 策略擬定")
                sales_forecast = st.number_input("預估月銷量", min_value=100, value=team_data.get('sales_forecast', 1000), step=100)
                margin = st.slider("期望利潤率 (%)", 0, 200, team_data.get('profit_margin', 50))
                
                if st.form_submit_button("試算建議售價", use_container_width=True, disabled=not is_current_s3):
                    fc = team_data['total_indirect_cost']
                    dc = team_data['direct_cost']
                    suggested = (dc + (fc / sales_forecast)) * (1 + margin / 100)
                    team_data.update({'sales_forecast': sales_forecast, 'profit_margin': margin, 'suggested_price': int(suggested)})
                    st.rerun()

            if 'suggested_price' in team_data:
                st.markdown("---")
                st.subheader("Part 2: 風險評估")
                k1, k2, k3 = st.columns(3)
                dc, fc, sf = team_data['direct_cost'], team_data['total_indirect_cost'], team_data['sales_forecast']
                k1.metric("直接成本", f"${dc}")
                k2.metric("分攤固定", f"${int(fc/sf)}")
                k3.metric("每杯總成本", f"${int(dc + fc/sf)}")
                
                st.info(f"系統建議售價： **${team_data['suggested_price']}**")
                with st.form("stage3_p2"):
                    final_p = st.number_input("決定最終售價 ($/杯)", min_value=1, value=team_data.get('final_price', team_data['suggested_price']))
                    
                    if st.form_submit_button("確認定價，與 AI 對決！", use_container_width=True, disabled=not is_current_s3):
                        mkt = team_data['estimated_indirect']['行銷']
                        ai_sales = predict_sales(team_data['style'], final_p, mkt)
                        revenue = final_p * ai_sales
                        total_cost = int((dc * ai_sales) + fc)
                        actual_profit = revenue - total_cost
                        cm = final_p - dc
                        bep = fc / cm if cm > 0 else float('inf')
                        team_data.update({'final_price': final_p, 'ai_predicted_sales': ai_sales, 'actual_profit': actual_profit, 
                                        's3_revenue': revenue, 's3_cost': total_cost, 'bep': int(bep)})
                        
                        # --- 關鍵修改：不再切換 stage ---
                        # if st.session_state.current_stage == 3:
                        #     st.session_state.current_stage = 4 
                        st.rerun()

        # --- S3 模擬結果 (含圖表) ---
        if 'ai_predicted_sales' in team_data:
            st.subheader("🤖 AI 市場模擬結果 (試營運第一個月)")
            ai_sales, profit, revenue, bep = team_data['ai_predicted_sales'], team_data['actual_profit'], team_data['s3_revenue'], team_data['bep']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("AI 預測銷量", f"{ai_sales:,} 杯", delta=f"{ai_sales - team_data['sales_forecast']:,} (與預估差異)", delta_color="off")
            c2.metric("本月模擬營收", f"${revenue:,}")
            c3.metric("本月模擬損益", f"${profit:,}", delta="-虧損" if profit < 0 else "+獲利", delta_color="inverse" if profit < 0 else "normal")

            st.markdown("### 📉 損益分析圖")
            max_x = max(5000, int(bep * 1.5))
            x_vals = list(range(0, max_x, int(max_x/100)))
            df_chart = pd.DataFrame({
                '銷量': x_vals,
                '總收入': [team_data['final_price'] * i for i in x_vals],
                '總成本': [team_data['total_indirect_cost'] + team_data['direct_cost'] * i for i in x_vals]
            })
            fig = px.line(df_chart, x='銷量', y=['總收入', '總成本'], color_discrete_map={'總收入': '#1f77b4', '總成本': '#d62728'})
            fig.add_vline(x=bep, line_dash="dash", annotation_text="BEP")
            fig.add_trace(px.scatter(x=[ai_sales], y=[team_data['total_indirect_cost'] + team_data['direct_cost'] * ai_sales], color_discrete_sequence=['#00CC96']).data[0])
            fig.add_annotation(x=ai_sales, y=team_data['total_indirect_cost'] + team_data['direct_cost'] * ai_sales, text="AI預測落點", showarrow=True, arrowhead=1, yshift=10)
            st.plotly_chart(fig, use_container_width=True)

            if profit > 0 and is_current_s3: st.balloons()

            # --- S3.5: 生存戰邀請 (新功能) ---
            # 只有在 S4 尚未開始時 (沒有 'capital' 欄位) 才顯示
            if 'capital' not in team_data:
                st.markdown("---")
                st.header("🔥 挑戰！市場風雲三部曲")
                st.info("你已完成試營運！接下來，你必須帶領你的咖啡廳，面對連續三個月的殘酷市場挑戰。")
                
                s3_profit = team_data.get('actual_profit', 0)
                initial_capital = max(30000, s3_profit)
                
                st.markdown(f"#### 你的開局：\n* **試營運損益：** `${s3_profit:,}`")

                if s3_profit < 30000:
                    st.warning(f"⚠️ 你的試營運獲利不足 $30,000... \n\n"
                               f"**媽媽決定贊助你！** 你的起始資金將被補足至 **$30,000**，"
                               f"讓你免於開局即破產的窘境。")
                else:
                    st.success(f"📈 恭喜！你將帶著 `${s3_profit:,}` 的獲利，進入生存戰！")

                if st.button("接受挑戰，進入生存戰！", type="primary", use_container_width=True):
                    # --- M0 初始化 (從 S4 移到這裡) ---
                    event_note = "M0 開局" + (" (媽媽贊Z助)" if s3_profit < 30000 else "")
                    team_data.update({
                        'capital': initial_capital, 'debt': 0, 's4_month': 1,
                        'history': [{
                            'Month': 'M0', 'Event': event_note, 'Sales': team_data.get('ai_predicted_sales', 0),
                            'Revenue': team_data.get('s3_revenue', 0), 'Cost': team_data.get('s3_cost', 0),
                            'Profit': s3_profit, 'Capital': initial_capital
                        }]
                    })
                    st.session_state.current_stage = 4 # *現在*才切換到 Stage 4
                    st.rerun()


# --- 🔥 S4: 市場風雲三部曲 (標題已修改) ---
# --- 關鍵修改：觸發條件改為 'capital' ---
if 'capital' in team_data:
    is_current_s4 = (st.session_state.current_stage == 4)
    s4_label = "🔥 市場風雲三部曲 (進行中)"
    
    with st.expander(s4_label, expanded=is_current_s4):
        
        # --- M0 初始化 (已移至 S3.5) ---
        # (這裡原有的 M0 初始化程式碼已被刪除)
        
        # --- 地下錢莊機制 (Loan Shark) ---
        if team_data['capital'] <= 0 and team_data['s4_month'] <= 3:
            loan_amount = 30000
            team_data['capital'] += loan_amount
            team_data['debt'] += loan_amount
            st.toast(f"💸 資金耗盡！已向地下錢莊借款 ${loan_amount:,} 續命！", icon="💀")

        # --- 資金看板 (含負債) ---
        capital, debt = team_data['capital'], team_data['debt']
        c1, c2 = st.columns(2)
        c1.metric("💰 目前營運資金", f"${capital:,}", delta="瀕臨破產" if capital < 30000 else None, delta_color="off")
        if debt > 0:
            c2.metric("💀 累積負債 (高利貸)", f"${debt:,}", delta="+10% 月利息", delta_color="inverse")

        # --- M1 ---
        if team_data['s4_month'] == 1:
            with st.form("m1"):
                st.subheader("📅 Month 1: 通膨來襲")
                st.error("💥 突發事件：全球乳牛集體罷工抗爭，牛奶成本即日起暴漲 100%！")
                options_m1 = ["A. 佛心凍漲", "B. 漲價反映", "C. 我沒賣牛奶~爽!"]
                captions_m1 = ["我是開良心事業的，成本我自己吞！", "抱歉了錢錢，我真的需要那個酷東西。售價+20%！", "哈哈哈哈你們忙，我先走了"]
                choice = st.radio("老闆請選擇對策：", options=options_m1, captions=captions_m1)
                
                if st.form_submit_button("確定決策", use_container_width=True):
                    if choice.startswith("C") and team_data['milk'] == '一般鮮乳':
                        st.error("😡 騙人！你第一關明明就選了要加鮮奶！請誠實面對你的成本！")
                        st.stop()
                    
                    dc, price, milk_cost = team_data['direct_cost'], team_data['final_price'], GAME_CONFIG['milks'][team_data['milk']]
                    milk_cost_increase = 0
                    if team_data['milk'] == '一般鮮乳':
                        if choice.startswith("A"): milk_cost_increase = milk_cost 
                        elif choice.startswith("B"): milk_cost_increase = milk_cost
                    
                    new_dc = dc + milk_cost_increase
                    new_price = int(price * 1.2) if choice.startswith("B") else price
                    
                    sales = predict_sales(team_data['style'], new_price, team_data['estimated_indirect']['行銷'])
                    revenue = int(new_price * sales)
                    interest = int(team_data['debt'] * 0.1)
                    total_cost = int((new_dc * sales) + team_data['total_indirect_cost'] + interest)
                    profit = revenue - total_cost
                    
                    team_data['capital'] += profit
                    team_data['history'].append({'Month': 'M1', 'Event': choice, 'Sales': sales, 'Revenue': revenue, 'Cost': total_cost, 'Profit': profit, 'Capital': team_data['capital']})
                    team_data['s4_month'] = 2
                    st.rerun()
        
        # --- M2 ---
        elif team_data['s4_month'] == 2:
            with st.form("m2"):
                st.subheader("📅 Month 2: 紅海競爭")
                st.warning("⚔️ 突發事件：校長千金在校園正中心開豪華咖啡廳慶開幕全品項咖啡打1折！")
                options_m2 = ["A. 割喉跟進", "B. 品牌固樁", "C. 躺平就好"]
                captions_m2 = ["跟他拚了！售價打5折，保住客流", "追加$3萬買網軍，客流僅-10%", "我就爛！讓他玩一個月，客流-75%"]
                choice = st.radio("老闆請選擇對策：", options=options_m2, captions=captions_m2)
                
                if st.form_submit_button("確定決策", use_container_width=True):
                    base_sales, price, fc = team_data.get('ai_predicted_sales', 1000), team_data['final_price'], team_data['total_indirect_cost']
                    if choice.startswith("A"): new_price, sales, new_fc = int(price * 0.5), base_sales, fc
                    elif choice.startswith("B"): new_price, sales, new_fc = price, int(base_sales * 0.9), fc + 30000
                    else: new_price, sales, new_fc = price, int(base_sales * 0.25), fc
                    
                    revenue = int(new_price * sales)
                    interest = int(team_data['debt'] * 0.1)
                    total_cost = int((team_data['direct_cost'] * sales) + new_fc + interest)
                    profit = revenue - total_cost
                    
                    team_data['capital'] += profit
                    team_data['history'].append({'Month': 'M2', 'Event': choice, 'Sales': sales, 'Revenue': revenue, 'Cost': total_cost, 'Profit': profit, 'Capital': team_data['capital']})
                    team_data['s4_month'] = 3
                    st.rerun()

        # --- M3 ---
        elif team_data['s4_month'] == 3:
            with st.form("m3"):
                st.subheader("📅 Month 3: 營運災難")
                st.error("💣 突發事件：一位生科系同學試圖用你的咖啡機萃取『賢者之石』，引發小規模爆炸！主設備全毀！")
                options_m3 = ["A. 買二手應急", "B. 租賃新機", "C. 手沖硬撐"]
                captions_m3 = ["賭運氣！花$8萬, 維持產能但有30%機率再爆", "穩健！花$4萬, T產能有上限", "守財奴！不花錢, 產能上限低!"]
                choice = st.radio("老闆請選擇對策：", options=options_m3, captions=captions_m3)
                
                if st.form_submit_button("確定決策", use_container_width=True):
                    base_sales, fc = team_data.get('ai_predicted_sales', 1000), team_data['total_indirect_cost']
                    if choice.startswith("A"):
                        new_fc = fc + 80000
                        is_fail = random.random() < 0.3
                        sales = int(base_sales * 0.5) if is_fail else base_sales
                        note = " (💥賭輸爆炸!)" if is_fail else " (✨賭贏了!)"
                    elif choice.startswith("B"): new_fc, sales, note = fc + 40000, min(base_sales, 2000), ""
                    else: new_fc, sales, note = fc, min(base_sales, 800), ""
                    
                    revenue = int(team_data['final_price'] * sales)
                    interest = int(team_data['debt'] * 0.1)
                    total_cost = int((team_data['direct_cost'] * sales) + new_fc + interest)
                    profit = revenue - total_cost
                    
                    team_data['capital'] += profit
                    team_data['history'].append({'Month': 'M3', 'Event': choice + note, 'Sales': sales, 'Revenue': revenue, 'Cost': total_cost, 'Profit': profit, 'Capital': team_data['capital']})
                    team_data['s4_month'] = 4
                    st.rerun()

        # --- 結算 ---
        if team_data.get('s4_month') == 4:
            final_capital = team_data['capital']
            final_debt = team_data['debt']
            net_assets = final_capital - final_debt

            if net_assets > 0:
                st.balloons()
                st.success(f"🎉 恭喜完賽！你的最終淨資產為 ${net_assets:,}")
            else:
                st.error(f"💀 遊戲結束！你雖然撐完了，但資不抵債，淨資產為 -${abs(net_assets):,}")

            df_hist = pd.DataFrame(team_data['history'])
            fig = px.line(df_hist, x='Month', y='Capital', markers=True, title="三個月生存戰-資金變化")
            fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="破產線")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 最終營運戰報")
            df_display = df_hist.copy()
            for col in ['Sales']: df_display[col] = df_display[col].apply(lambda x: f"{x:,}")
            for col in ['Revenue', 'Cost', 'Profit', 'Capital']:
                df_display[col] = df_display[col].apply(lambda x: f"${x:,}")
            st.table(df_display[['Month', 'Sales', 'Revenue', 'Cost', 'Profit', 'Capital', 'Event']])
            
            if final_debt > 0:
                st.warning(f"📢 注意：你目前仍欠地下錢莊 ${final_debt:,}，上述 Capital 尚未扣除此負債。")