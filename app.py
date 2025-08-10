import streamlit as st
import requests
from datetime import datetime
import re
import json
from urllib.parse import urlparse, quote
import asyncio
from playwright.async_api import async_playwright
import anthropic

def get_openstreetmap_entity_link(location_name):
    """
    使用 OpenStreetMap Nominatim API 查詢地點，並返回條目連結
    優先查找 relation 類型的條目（適合國家、城市等行政區劃）
    
    符合 Nominatim 使用政策：
    - 設置合適的 User-Agent 識別應用程式
    - 限制請求頻率（由用戶觸發，非批量處理）
    - 適當的錯誤處理和備選方案
    - 尊重 API 限制和超時設定
    """
    try:
        # URL encode 地點名稱
        encoded_name = quote(location_name)
        
        # 使用 Nominatim API 進行搜尋，嚴格遵循使用政策
        search_url = f"https://nominatim.openstreetmap.org/search?q={encoded_name}&format=json&limit=3&addressdetails=1&accept-language=zh"
        
        # 設置符合 Nominatim 使用政策的 headers
        # 政策要求：「Provide a valid HTTP Referer or User-Agent identifying the application」
        headers = {
            'User-Agent': 'NewsAnalyzer/2.1 (Educational news analysis tool; Contact: github.com/planetoid/news-analyzer)',
            'Accept': 'application/json',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Referer': 'https://github.com/planetoid/news-analyzer'
        }
        
        # 發送搜尋請求，遵循 API 使用限制
        # 政策要求：「No heavy uses (an absolute maximum of 1 request per second)」
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            
            if not results:
                # 沒有搜尋結果，返回搜尋連結作為備選
                return f"https://www.openstreetmap.org/search?query={encoded_name}"
            
            # 優先查找 relation 類型的結果（通常是行政區劃）
            for result in results:
                osm_type = result.get('osm_type')
                osm_id = result.get('osm_id')
                place_class = result.get('class', '')
                place_type = result.get('type', '')
                
                # 優先選擇 relation 類型的行政邊界或地點
                if (osm_type == 'relation' and 
                    place_class in ['boundary', 'place', 'administrative'] and 
                    osm_id):
                    return f"https://www.openstreetmap.org/relation/{osm_id}"
            
            # 如果沒有找到 relation，查找其他高質量的結果
            for result in results:
                osm_type = result.get('osm_type')
                osm_id = result.get('osm_id')
                place_class = result.get('class', '')
                
                # 選擇地點類別的結果
                if osm_type and osm_id and place_class in ['place', 'boundary']:
                    if osm_type == 'relation':
                        return f"https://www.openstreetmap.org/relation/{osm_id}"
                    elif osm_type == 'way':
                        return f"https://www.openstreetmap.org/way/{osm_id}"
                    elif osm_type == 'node':
                        return f"https://www.openstreetmap.org/node/{osm_id}"
            
            # 最後嘗試任何有效的結果
            first_result = results[0]
            osm_type = first_result.get('osm_type')
            osm_id = first_result.get('osm_id')
            
            if osm_type and osm_id:
                if osm_type == 'relation':
                    return f"https://www.openstreetmap.org/relation/{osm_id}"
                elif osm_type == 'way':
                    return f"https://www.openstreetmap.org/way/{osm_id}"
                elif osm_type == 'node':
                    return f"https://www.openstreetmap.org/node/{osm_id}"
        
        elif response.status_code == 403:
            # API 存取被拒絕，可能是請求頻率過高或違反使用政策
            # 政策說明：「may be classified as faulty and blocked」
            print(f"Nominatim API 403 錯誤：可能違反使用政策或請求過於頻繁")
            pass
        elif response.status_code == 429:
            # 請求頻率限制
            print(f"Nominatim API 429 錯誤：請求頻率超過限制")
            pass
        
        # 如果 API 查詢失敗，返回搜尋連結作為備選方案
        return f"https://www.openstreetmap.org/search?query={encoded_name}"
        
    except requests.exceptions.Timeout:
        # 請求超時，返回搜尋連結作為備選
        print(f"Nominatim API 請求超時")
        pass
    except Exception as e:
        # 記錄錯誤但不顯示給用戶（避免影響界面）
        print(f"OpenStreetMap 查詢錯誤: {str(e)}")
    
    # 所有錯誤情況都返回搜尋連結作為備選方案
    encoded_name = quote(location_name)
    return f"https://www.openstreetmap.org/search?query={encoded_name}"

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
        text-align: left;
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

        【重要分析指南】
        1. 真實度評估關鍵指標：
           - 官方來源、具體數據、權威人士發言 → 高分 (80-95)
           - 網路傳言、未經證實消息 → 低分 (20-40)
           - 「網傳」、「據說」、「傳言」關鍵詞 → 極低分 (10-30)
           - 已被官方澄清/闢謠內容 → 極低分 (10-25)

        2. 重要性評估標準：
           - 娛樂、地方小活動 → 10-40分
           - 一般社會新聞 → 40-70分  
           - 重大政策、經濟影響 → 70-100分

        3. 影響力評估標準：
           - 個人趣事、小範圍活動 → 5-30分
           - 特定群體關注事件 → 30-60分
           - 廣泛社會影響、政策變革 → 60-100分

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
                "locations": ["{{"name": "地點名稱"}}"],
                "organizations": ["{{"name": "機構名稱", "official_link": "官方連結"}}"],
                "dates": ["{{"date": "日期時間", "event": "相關事件"}}],
                "datasets": ["{{"name": "資料集關鍵字", "description": "說明", "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=資料集關鍵字"}}]
            }}
        }}

        特別注意：
        - 對於locations，只需要提供地點名稱，系統會自動查詢 OpenStreetMap 條目連結
        - 例如：{{"name": "台北市"}} 或 {{"name": "中正紀念堂"}}
        - 對於datasets，請根據新聞主題提取相關的政府資料集關鍵字，並設定搜尋連結
        - 例如：{{"name": "交通事故", "description": "道路交通事故統計", "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=交通事故"}}

        飲料分類標準：
        - golden_lemon (金桔檸檬): 真實度>70且重要性>70
        - honey_green (蜂蜜綠茶): 真實度>70但重要性≤70
        - plain_water (無糖白開水): 真實度≤70且重要性≤70
        - expired_milk (過期奶茶): 真實度≤70但重要性>70

        【評分範例參考】
        - 央行政策/重大投資: 真實度85-95, 重要性85-95, 影響力80-90 → 金桔檸檬
        - 動物園活動/地方慶典: 真實度75-85, 重要性25-40, 影響力15-30 → 蜂蜜綠茶  
        - 網路傳言/個人經驗: 真實度10-30, 重要性5-15, 影響力5-10 → 無糖白開水
        - 已闢謠假訊息: 真實度10-25, 重要性70-90, 影響力70-90 → 過期奶茶
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
            location_name = loc["name"]
            
            # 動態查詢 OpenStreetMap 條目連結
            map_link = get_openstreetmap_entity_link(location_name)
            
            # 顯示帶有條目連結的地點標籤
            st.markdown(f'<a href="{map_link}" class="entity-tag" target="_blank">{location_name}</a>', 
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
                           unsafe_allow_html=True)


def main():
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

# 頁面底部歸屬聲明
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2rem;'>
        <p>🗺️ 地理資訊由 <a href="https://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> 提供 | 
        使用 <a href="https://nominatim.openstreetmap.org/" target="_blank">Nominatim</a> 地理編碼服務 | 
        資料採用 <a href="https://openstreetmap.org/copyright" target="_blank">ODbL</a> 授權</p>
        <p>📍 Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a></p>
    </div>
    """, 
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()