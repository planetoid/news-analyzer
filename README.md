# 🥤 NewsAnalyzer - 新聞手搖飲分析器

使用Claude AI將新聞內容轉化為直觀的手搖飲料評級系統！

## ✨ 專案特色

### 🎯 **核心功能**
- **AI深度分析**: 使用Claude AI進行多維度新聞分析，具備強化的假新聞檢測能力
- **飲料分類系統**: 四種手搖飲料評級分費
- **實體識別**: 自動粹取人物、地點、數字等關鍵資訊
- **外部連結整合**: 連接維基百科、地圖、政府資料等外部資源
- **模型選擇**: 支援多種Claude模型，可自訂分析引擎
- **資料集整合**: 自動推薦相關政府公開資料集
- **完整測試框架**: 包含12個測試案例的綜合評估系統

### 🏆 **系統性能**
- **測試準確率**: 100% (經過最新最佳化)
- 評分精確度**: ±15分誤差容忍範圍內的精準評估
- **多模型支援**: claude-sonnet-4-20250514, claude-3-5-sonnet-20241022, claude-3-opus-20240229

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

### 2. 設定API金鑰
- 前往 [Anthropic Console](https://console.anthropic.com/) 取得Claude API Key
- 在應用程式側邊欄輸入您的API金鑰

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
- **前端**: Streamlit + 自訂CSS
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
│   ├── run_tests.py        # 測試執行器
│   ├── test_runner.py      # 完整測試執行器(含視覺化)
│   ├── simple_test_runner.py # 簡化版測試執行器
│   ├── test_data_generator.py # 測試資料生成器
│   └── test_compatibility.py # 相容性檢查
├── README.md          # 說明文件
├── PRD.md             # 產品需求文件
└── .gitignore         # Git忽略檔案
```

## 📊 分析維度

### 三大評分指標
1. **🎯 真實度 (0-100分)**
   - 內容的事實準確性，強化假新聞檢測
   - 資料來源可信度評估
   - 「網傳」、「謠言」、「已闢謠」內容識別

2. **⭐ 重要性 (0-100分)**
   - 新聞的社會影響範圍
   - 娛樂性質 (10-40分) vs 重大政策 (70-100分)
   - 與讀者的相關程度

3. **📈 影響力 (0-100分)**
   - 個人趣事 (5-30分) vs 廣泛社會影響 (60-100分)
   - 政策或社會變革潛力
   - 討論熱度和後續效應預測

### 💡 **AI最佳化特色**
- **智慧關鍵字檢測**: 自動識別「網傳」、「據說」、「專家闢謠」等假新聞標識
- **分級評分指導**: 提供具體評分範圍，確保評估一致性
- **範例導向學習**: 內建評分參考標準，提升分析精確度

### 實體提取功能 ✨ **最新升級**
- **👥 人物識別**: 姓名、職位 + 維基百科連結
- **🔢 數據提取**: 統計數字 + 政府開放資料連結
- **📍 地點定位**: 地名識別 + **OpenStreetMap 條目連結** ⭐ (新功能!)
  - 使用 Nominatim API 智慧查詢
  - 優先顯示 relation 條目連結 (如: `台灣` → `/relation/7219605`)
  - 支援國家、城市、行政區劃的精確定位
- **🏢 機構組織**: 機構名稱 + 官方網站連結
- **📅 時間資訊**: 日期事件時間線
- **📊 資料集推薦**: 自動推薦相關政府公開資料集 (data.gov.tw)

## 🎨 界面設計

### 視覺特色
- **響應式設計**: 支援桌面和行動裝置
- **漸層色彩**: 四種飲料專屬配色方案
- **卡片式布局**: 清晰的資訊層次結構
- **互動式連結**: 點擊實體標籤開啟外部資源

## 🔧 進階設定

### 模型選擇
在側邊欄的「模型名稱」欄位中，您可以選擇不同的Claude模型：

- **claude-sonnet-4-20250514** (預設)

### 自訂分析提示詞
在 `app.py` 中的 `analyze_news` 方法，您可以修改提示詞來調整分析重點：

```python
def analyze_news(self, content):
    prompt = f"""
    # 在這裡自訂您的分析邏輯
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

# 🆕 執行AI系統測試
# 簡化版測試執行器 (建議用於快速驗證)
python tests/simple_test_runner.py

# 完整測試執行器 (含視覺化圖表，需要matplotlib和seaborn)
python tests/test_runner.py

# 相容性檢查
python tests/test_compatibility.py

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

### Q: 相關資料集功能如何運作？
A: 系統會根據新聞主題自動推薦相關的政府公開資料集，點擊即可前往 data.gov.tw 搜尋。

### Q: 如何選擇不同的AI模型？
A: 在左側設定面板的「模型名稱」欄位中輸入想要使用的Claude模型名稱。

### Q: 如何執行測試？
A: 使用 `python tests/simple_test_runner.py` 執行快速測試，或使用 `python tests/test_runner.py` 執行完整測試（需要安裝視覺化套件）。

### Q: 系統的準確率如何？
A: 經過最新最佳化，系統在標準測試案例中達到100%準確率，包括假新聞檢測和評分精確度。

### Q: 如何改善分析結果？
A: 系統已內建最佳化的提示詞和評分標準，如需客製化可修改 `app.py` 中的 `analyze_news` 方法。

### Q: 地點連結如何運作？
A: 系統使用 OpenStreetMap Nominatim API 智慧查詢地點資訊，優先提供精確的條目連結（如台灣→relation/7219605）而非搜尋連結，讓用戶直接查看完整的地理資訊和邊界資料。

### Q: 測試覆蓋了哪些情境？
A: 測試包含4個類別共12個案例：重要真實新聞(金桔檸檬)、真實但不重要(蜂蜜綠茶)、不實且不重要(無糖白開水)、危險假訊息(過期奶茶)。
A: 使用 `python tests/run_tests.py` 執行所有測試，或使用 `pytest` 進行更詳細的測試。

### Q: 如何貢獻代碼？
A: 請先執行測試確保功能正常，使用 `black` 格式化程式碼，然後提交 Pull Request。

---

**🥤 讓每一則新聞都變成一杯有味道的飲料！**

Made with ❤️ using Streamlit & Claude AI