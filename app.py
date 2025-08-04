import streamlit as st
import requests
from datetime import datetime
import re
import json
from urllib.parse import urlparse
import asyncio
from playwright.async_api import async_playwright
import anthropic

# 頁面配置
st.set_page_config(
    page_title="🥤 新聞手搖飲分析器",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .drink-card {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .golden-lemon { background: linear-gradient(135deg, #FFD700, #FFA500); }
    .honey-green { background: linear-gradient(135deg, #32CD32, #228B22); }
    .plain-water { background: linear-gradient(135deg, #E0E0E0, #B0B0B0); color: #333; }
    .expired-milk { background: linear-gradient(135deg, #FF6B6B, #CC0000); }
    
    .score-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem;
        text-align: center;
    }
    .entity-tag {
        display: inline-block;
        background: #E8F4FD;
        color: #2E86AB;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 20px;
        font-size: 0.9rem;
        text-decoration: none;
    }
    .entity-tag:hover {
        background: #2E86AB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class NewsAnalyzer:
    def __init__(self, api_key, model_name="claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
    
    async def fetch_article_content(self, url):
        """使用Playwright抓取網頁內容"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url, wait_until='networkidle')
                
                # 嘗試多種選擇器抓取文章內容
                selectors = [
                    'article', '.article-content', '.content', '.post-content',
                    '.entry-content', '#article', '.article-body', 'main'
                ]
                
                content = ""
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            content = await element.inner_text()
                            if len(content) > 200:  # 確保內容足夠長
                                break
                    except:
                        continue
                
                await browser.close()
                return content if content else "無法抓取文章內容"
                
        except Exception as e:
            return f"抓取失敗: {str(e)}"
    
    def analyze_news(self, content):
        """使用Claude API分析新聞"""
        prompt = f"""
        請分析以下新聞內容，並以JSON格式回應：

        新聞內容：
        {content}

        請提供以下分析：
        {{
            "summary": "100-150字的重點摘要",
            "target_audience": "預期讀者群體",
            "truthfulness": 真實度分數(0-100),
            "importance": 重要性分數(0-100),
            "impact": 影響力分數(0-100),
            "drink_recommendation": {{
                "name": "推薦飲料名稱",
                "reason": "推薦理由",
                "category": "golden_lemon/honey_green/plain_water/expired_milk"
            }},
            "entities": {{
                "people": ["{{"name": "姓名", "title": "職位", "wiki_link": "維基百科連結"}}"],
                "numbers": ["{{"value": "數字", "context": "背景說明", "data_link": "相關資料連結"}}"],
                "locations": ["{{"name": "地點", "map_link": "https://www.openstreetmap.org/search?query=地點名稱"}}"],
                "organizations": ["{{"name": "機構名稱", "official_link": "官方連結"}}"],
                "dates": ["{{"date": "日期時間", "event": "相關事件"}}],
                "datasets": ["{{"name": "資料集關鍵字", "description": "說明", "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=資料集關鍵字"}}]
            }}
        }}

        特別注意：
        - 對於locations，請將map_link設為：https://www.openstreetmap.org/search?query=實際地點名稱
        - 例如：{{"name": "台北市", "map_link": "https://www.openstreetmap.org/search?query=台北市"}}
        - 對於datasets，請根據新聞主題提取相關的政府資料集關鍵字，並設定搜尋連結
        - 例如：{{"name": "交通事故", "description": "道路交通事故統計", "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=交通事故"}}

        飲料分類標準：
        - golden_lemon (金桔檸檬): 真實度>70且重要性>70
        - honey_green (蜂蜜綠茶): 真實度>70但重要性≤70
        - plain_water (無糖白開水): 真實度≤70且重要性≤70
        - expired_milk (過期奶茶): 真實度≤70但重要性>70
        """
        
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 提取JSON內容
            response_text = response.content[0].text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "無法解析分析結果"}
                
        except Exception as e:
            return {"error": f"分析失敗: {str(e)}"}

def display_drink_result(drink_info):
    """顯示飲料推薦結果"""
    drink_styles = {
        "golden_lemon": ("🟡 金桔檸檬", "golden-lemon"),
        "honey_green": ("🟢 蜂蜜綠茶", "honey-green"), 
        "plain_water": ("⚪ 無糖白開水", "plain-water"),
        "expired_milk": ("🔴 過期奶茶", "expired-milk")
    }
    
    drink_name, css_class = drink_styles.get(drink_info["category"], ("❓ 未知飲料", "plain-water"))
    
    st.markdown(f"""
    <div class="drink-card {css_class}">
        <h2>{drink_name}</h2>
        <h3>{drink_info["name"]}</h3>
        <p>{drink_info["reason"]}</p>
    </div>
    """, unsafe_allow_html=True)

def display_scores(analysis):
    """顯示評分卡片"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="score-card">
            <h3>🎯 真實度</h3>
            <h2>{analysis['truthfulness']}/100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h3>⭐ 重要性</h3>
            <h2>{analysis['importance']}/100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="score-card">
            <h3>📈 影響力</h3>
            <h2>{analysis['impact']}/100</h2>
        </div>
        """, unsafe_allow_html=True)

def display_entities(entities):
    """顯示實體提取結果"""
    if entities.get("people"):
        st.subheader("👥 相關人物")
        for person in entities["people"]:
            link = person.get("wiki_link", "#")
            st.markdown(f'<a href="{link}" class="entity-tag" target="_blank">{person["name"]} ({person["title"]})</a>', 
                       unsafe_allow_html=True)
    
    if entities.get("numbers"):
        st.subheader("🔢 關鍵數據")
        for num in entities["numbers"]:
            link = num.get("data_link", "")
            value_context = f'{num["value"]} - {num["context"]}'
            
            # 如果有有效連結且不是預設的 "#"，則使用連結
            if link and link != "#":
                st.markdown(f'<a href="{link}" class="entity-tag" target="_blank">{value_context}</a>', 
                           unsafe_allow_html=True)
            else:
                # 沒有連結時只顯示純文字標籤
                st.markdown(f'<span class="entity-tag">{value_context}</span>', 
                           unsafe_allow_html=True)
    
    if entities.get("locations"):
        st.subheader("📍 相關地點")
        for loc in entities["locations"]:
            link = loc.get("map_link", "")
            
            # 如果有有效連結且不是預設的 "#"，則使用連結
            if link and link != "#":
                st.markdown(f'<a href="{link}" class="entity-tag" target="_blank">{loc["name"]}</a>', 
                           unsafe_allow_html=True)
            else:
                # 沒有連結時只顯示純文字標籤
                st.markdown(f'<span class="entity-tag">{loc["name"]}</span>', 
                           unsafe_allow_html=True)
    
    if entities.get("organizations"):
        st.subheader("🏢 相關機構")
        for org in entities["organizations"]:
            link = org.get("official_link", "#")
            st.markdown(f'<a href="{link}" class="entity-tag" target="_blank">{org["name"]}</a>', 
                       unsafe_allow_html=True)
    
    if entities.get("dates"):
        st.subheader("📅 重要時間")
        for date in entities["dates"]:
            st.markdown(f'<span class="entity-tag">{date["date"]} - {date["event"]}</span>', 
                       unsafe_allow_html=True)
    
    if entities.get("datasets"):
        st.subheader("📊 相關公開資料集")
        for dataset in entities["datasets"]:
            link = dataset.get("data_link", "")
            
            # 如果有有效連結且不是預設的 "#"，則使用連結
            if link and link != "#":
                st.markdown(f'<a href="{link}" class="entity-tag" target="_blank">{dataset["name"]}</a>', 
                           unsafe_allow_html=True)
            else:
                # 沒有連結時只顯示純文字標籤
                st.markdown(f'<span class="entity-tag">{dataset["name"]}</span>', 
                           unsafe_allow_html=True)def main():
    # 主標題
    st.markdown('<h1 class="main-header">🥤 新聞手搖飲分析器</h1>', unsafe_allow_html=True)
    
    # 側邊欄 - API Key設定
    with st.sidebar:
        st.header("🔑 設定")
        api_key = st.text_input("Claude API Key", type="password", 
                               help="請輸入您的Anthropic API密鑰")
        
        model_name = st.text_input("模型名稱", 
                                  value="claude-sonnet-4-20250514",
                                  help="請輸入要使用的Claude模型名稱\n常用選項:\n• claude-sonnet-4-20250514\n• claude-3-5-sonnet-20241022\n• claude-3-opus-20240229")
        
        st.markdown("---")
        st.markdown("""
        ### 🥤 飲料分類系統
        - **🟡 金桔檸檬**: 優質真實新聞
        - **🟢 蜂蜜綠茶**: 真實但不重要
        - **⚪ 無糖白開水**: 平淡普通內容
        - **🔴 過期奶茶**: 危險假新聞
        """)
    
    if not api_key:
        st.warning("⚠️ 請在側邊欄輸入Claude API Key")
        return
    
    # 輸入區域
    tab1, tab2 = st.tabs(["🔗 網址輸入", "✍️ 手動輸入"])
    
    with tab1:
        url = st.text_input("🌐 請輸入新聞網址:")
        if st.button("📥 抓取並分析", type="primary"):
            if url:
                with st.spinner("正在抓取文章內容..."):
                    analyzer = NewsAnalyzer(api_key, model_name)
                    
                    # 執行異步抓取
                    try:
                        content = asyncio.run(analyzer.fetch_article_content(url))
                        if "無法抓取" in content or "抓取失敗" in content:
                            st.error(content)
                            st.info("💡 請嘗試使用「手動輸入」功能")
                        else:
                            analyze_content(analyzer, content)
                    except Exception as e:
                        st.error(f"抓取失敗: {str(e)}")
            else:
                st.warning("請輸入有效的網址")
    
    with tab2:
        content = st.text_area("📝 請貼上新聞內容:", height=200)
        if st.button("🔍 開始分析", type="primary"):
            if content:
                analyzer = NewsAnalyzer(api_key, model_name)
                analyze_content(analyzer, content)
            else:
                st.warning("請輸入新聞內容")

def analyze_content(analyzer, content):
    """執行內容分析並顯示結果"""
    with st.spinner("🤖 Claude正在深度分析中..."):
        analysis = analyzer.analyze_news(content)
        
        if "error" in analysis:
            st.error(f"❌ {analysis['error']}")
            return
        
        # 顯示飲料推薦
        st.markdown("## 🥤 您的新聞是...")
        display_drink_result(analysis["drink_recommendation"])
        
        # 顯示詳細分析
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("## 📋 分析摘要")
            st.write(analysis["summary"])
            
            st.markdown("## 👥 目標讀者")
            st.write(analysis["target_audience"])
        
        with col2:
            st.markdown("## 📊 評分結果")
            display_scores(analysis)
        
        # 顯示實體信息
        if analysis.get("entities"):
            st.markdown("## 🔍 關鍵資訊擷取")
            display_entities(analysis["entities"])

if __name__ == "__main__":
    main()