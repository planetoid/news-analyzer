# 🥤 NewsAnalyzer - 新聞手搖飲分析器

一個創新的新聞分析工具，使用Claude AI將新聞內容轉化為直觀的手搖飲料評級系統！

## ✨ 專案特色

### 🎯 **核心功能**
- **智能網頁抓取**: 自動從新聞網站提取文章內容
- **AI深度分析**: 使用Claude AI進行多維度新聞分析
- **飲料分類系統**: 創新的四象限手搖飲料評級方式
- **實體識別**: 自動提取人物、地點、數字等關鍵信息
- **外部連結整合**: 連接維基百科、地圖、政府資料等外部資源
- **模型選擇**: 支援多種Claude模型，可自訂分析引擎
- **資料集整合**: 自動推薦相關政府公開資料集

### 🥤 **飲料分類標準**
| 飲料 | 真實度 | 重要性 | 適用情境 |
|------|--------|--------|----------|
| 🟡 **金桔檸檬** | 高 (>70) | 高 (>70) | 優質真實的重要新聞 |
| 🟢 **蜂蜜綠茶** | 高 (>70) | 低 (≤70) | 真實但不太重要的資訊 |
| ⚪ **無糖白開水** | 低 (≤70) | 低 (≤70) | 平淡無味的普通內容 |
| 🔴 **過期奶茶** | 低 (≤70) | 高 (>70) | 危險的假新聞或誤導資訊 |

## 🚀 快速開始

### 1. 環境準備
```bash
# 複製專案
git clone <repository-url>
cd news-analyzer

# 安裝Python依賴
pip install -r requirements.txt

# 安裝Playwright瀏覽器
playwright install chromium
```

### 2. 設定API密鑰
- 前往 [Anthropic Console](https://console.anthropic.com/) 取得Claude API Key
- 在應用程式側邊欄輸入您的API密鑰

### 3. 啟動應用
```bash
streamlit run app.py
```

### 4. 開始使用
1. 在瀏覽器中打開 `http://localhost:8501`
2. 在側邊欄輸入Claude API Key
3. 選擇要使用的Claude模型（預設：claude-sonnet-4-20250514）
4. 選擇輸入方式：
   - 🔗 **網址輸入**: 貼上新聞連結自動抓取
   - ✍️ **手動輸入**: 直接貼上新聞內容
5. 點擊分析按鈕
6. 查看您的新聞變成了什麼飲料！

## 🛠 技術架構

### 核心技術棧
- **前端**: Streamlit + 自定義CSS
- **AI分析**: Anthropic Claude API
- **網頁抓取**: Playwright
- **資料處理**: Python + JSON

### 主要模組
```
NewsAnalyzer/
├── app.py              # 主應用程式
├── requirements.txt    # 生產依賴套件
├── requirements-dev.txt # 開發測試依賴
├── tests/              # 測試套件
│   ├── __init__.py     # 測試初始化
│   ├── test_analyzer.py    # 核心功能測試
│   ├── test_ui.py          # UI 組件測試
│   ├── test_integration.py # 整合測試
│   ├── test_config.py      # 測試配置
│   └── run_tests.py        # 測試執行器
├── README.md          # 說明文件
├── PRD.md             # 產品需求文件
└── .gitignore         # Git忽略檔案
```

## 📊 分析維度

### 三大評分指標
1. **🎯 真實度 (0-100分)**
   - 內容的事實準確性
   - 資料來源可信度
   - 邏輯一致性

2. **⭐ 重要性 (0-100分)**
   - 新聞的社會影響力
   - 與讀者的相關程度
   - 時效性和新鮮度

3. **📈 影響力 (0-100分)**
   - 可能產生的後續效應
   - 政策或社會變革潛力
   - 討論熱度預測

### 實體提取功能
- **👥 人物識別**: 姓名、職位 + 維基百科連結
- **🔢 數據提取**: 統計數字 + 政府開放資料連結
- **📍 地點定位**: 地名識別 + OpenStreetMap 搜尋連結
- **🏢 機構組織**: 機構名稱 + 官方網站連結
- **📅 時間信息**: 日期事件時間線
- **📊 資料集推薦**: 自動推薦相關政府公開資料集 (data.gov.tw)

## 🎨 界面設計

### 視覺特色
- **響應式設計**: 支援桌面和行動裝置
- **漸層色彩**: 四種飲料專屬配色方案
- **卡片式布局**: 清晰的信息層次結構
- **互動式連結**: 點擊實體標籤開啟外部資源

### 用戶體驗
- **即時反饋**: 分析過程進度顯示
- **錯誤處理**: 友善的錯誤提示和建議
- **多重輸入**: 網址抓取 + 手動輸入雙模式
- **結果分享**: 易於截圖分享的視覺化結果

## 🔧 進階設定

### 模型選擇
在側邊欄的「模型名稱」欄位中，您可以選擇不同的Claude模型：

- **claude-sonnet-4-20250514** (預設)

### 自定義分析提示詞
在 `app.py` 中的 `analyze_news` 方法，您可以修改提示詞來調整分析重點：

```python
def analyze_news(self, content):
    prompt = f"""
    # 在這裡自定義您的分析邏輯
    請分析以下新聞內容...
    """
```

### 擴展實體識別
在 `display_entities` 函數中添加更多實體類型：

```python
def display_entities(entities):
    # 添加新的實體類型
    if entities.get("companies"):
        st.subheader("🏢 相關公司")
        # 處理公司實體...
```

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

### 開發環境設置
```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 執行所有測試
python tests/run_tests.py

# 執行特定類型測試
python tests/run_tests.py --type unit        # 單元測試
python tests/run_tests.py --type ui          # UI 測試  
python tests/run_tests.py --type integration # 整合測試

# 執行特定測試類別
python tests/run_tests.py --specific analyzer

# 使用 pytest 執行測試
pytest tests/ -v

# 生成測試覆蓋率報告
pytest tests/ --cov=app --cov-report=html

# 代碼格式化
black app.py tests/

# 代碼風格檢查
flake8 app.py tests/
```

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 🙋‍♂️ 常見問題

### Q: 網頁抓取失敗怎麼辦？
A: 某些網站有反爬蟲機制，請使用「手動輸入」功能直接貼上內容。

### Q: API Key安全嗎？
A: API Key僅在當前會話中使用，不會被儲存或傳輸到第三方。

### Q: 支援哪些新聞網站？
A: 支援大部分新聞網站，包括主流媒體和部落格平台。

### Q: 可以批次分析嗎？
A: 目前版本支援單篇分析，批次功能將在未來版本中加入。

### Q: 相關資料集功能如何運作？
A: 系統會根據新聞主題自動推薦相關的政府公開資料集，點擊即可前往 data.gov.tw 搜尋。

### Q: 如何選擇不同的AI模型？
A: 在左側設定面板的「模型名稱」欄位中輸入想要使用的Claude模型名稱。

### Q: 如何執行測試？
A: 使用 `python tests/run_tests.py` 執行所有測試，或使用 `pytest` 進行更詳細的測試。

### Q: 如何貢獻代碼？
A: 請先執行測試確保功能正常，使用 `black` 格式化代碼，然後提交 Pull Request。

---

**🥤 讓每一則新聞都變成一杯有味道的飲料！**

Made with ❤️ using Streamlit & Claude AI