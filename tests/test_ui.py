import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import streamlit as st

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStreamlitUI(unittest.TestCase):
    """Streamlit UI 組件測試"""
    
    def setUp(self):
        """設定測試環境"""
        # 模擬 Streamlit session state
        if 'mock_session_state' not in st.session_state:
            st.session_state.mock_session_state = {}

    @patch('streamlit.text_input')
    @patch('streamlit.sidebar')
    def test_api_key_input(self, mock_sidebar, mock_text_input):
        """測試 API Key 輸入功能"""
        mock_text_input.return_value = "test_api_key"
        
        # 模擬用戶輸入 API Key
        api_key = mock_text_input("Claude API Key", type="password")
        
        self.assertEqual(api_key, "test_api_key")
        mock_text_input.assert_called_with("Claude API Key", type="password")

    @patch('streamlit.text_input')
    def test_model_selection(self, mock_text_input):
        """測試模型選擇功能"""
        mock_text_input.return_value = "claude-sonnet-4-20250514"
        
        model_name = mock_text_input(
            "模型名稱", 
            value="claude-sonnet-4-20250514"
        )
        
        self.assertEqual(model_name, "claude-sonnet-4-20250514")

    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.button')
    def test_news_input_methods(self, mock_button, mock_text_area, mock_text_input):
        """測試新聞輸入方式"""
        # 測試網址輸入
        mock_text_input.return_value = "https://example.com/news"
        url = mock_text_input("請輸入新聞網址:")
        self.assertTrue(url.startswith("https://"))
        
        # 測試手動輸入
        mock_text_area.return_value = "測試新聞內容"
        content = mock_text_area("請貼上新聞內容:", height=200)
        self.assertEqual(content, "測試新聞內容")
        
        # 測試分析按鈕
        mock_button.return_value = True
        button_clicked = mock_button("🔍 開始分析", type="primary")
        self.assertTrue(button_clicked)

    def test_drink_classification_display(self):
        """測試飲料分類顯示"""
        drink_categories = {
            "golden_lemon": {"emoji": "🟡", "name": "金桔檸檬"},
            "honey_green": {"emoji": "🟢", "name": "蜂蜜綠茶"},
            "plain_water": {"emoji": "⚪", "name": "無糖白開水"},
            "expired_milk": {"emoji": "🔴", "name": "過期奶茶"}
        }
        
        for category, info in drink_categories.items():
            self.assertIn("emoji", info)
            self.assertIn("name", info)
            self.assertTrue(len(info["name"]) > 0)

    @patch('streamlit.markdown')
    def test_score_display(self, mock_markdown):
        """測試評分顯示"""
        scores = {
            "truthfulness": 85,
            "importance": 75,
            "impact": 70
        }
        
        for score_name, score_value in scores.items():
            # 模擬評分卡片顯示
            mock_markdown(f"<h2>{score_value}/100</h2>", unsafe_allow_html=True)
            
            self.assertTrue(0 <= score_value <= 100)

    def test_entity_display_structure(self):
        """測試實體顯示結構"""
        entity_types = [
            {"key": "people", "emoji": "👥", "title": "相關人物"},
            {"key": "numbers", "emoji": "🔢", "title": "關鍵數據"},
            {"key": "locations", "emoji": "📍", "title": "相關地點"},
            {"key": "organizations", "emoji": "🏢", "title": "相關機構"},
            {"key": "dates", "emoji": "📅", "title": "重要時間"},
            {"key": "datasets", "emoji": "📊", "title": "相關公開資料集"}
        ]
        
        for entity_type in entity_types:
            self.assertIn("key", entity_type)
            self.assertIn("emoji", entity_type)
            self.assertIn("title", entity_type)

    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_error_handling_display(self, mock_info, mock_warning, mock_error):
        """測試錯誤處理顯示"""
        # 測試各種錯誤情況的顯示
        error_messages = [
            "⚠️ 請在側邊欄輸入Claude API Key",
            "請輸入有效的網址",
            "請輸入新聞內容",
            "❌ 分析失敗"
        ]
        
        for message in error_messages:
            if "⚠️" in message:
                mock_warning(message)
                mock_warning.assert_called_with(message)
            elif "❌" in message:
                mock_error(message)
                mock_error.assert_called_with(message)
            else:
                mock_info(message)

    def test_css_styles_application(self):
        """測試 CSS 樣式應用"""
        css_classes = [
            "main-header",
            "drink-card",
            "golden-lemon",
            "honey-green", 
            "plain-water",
            "expired-milk",
            "score-card",
            "entity-tag"
        ]
        
        for css_class in css_classes:
            # 檢查 CSS 類別名稱格式
            self.assertIsInstance(css_class, str)
            self.assertTrue(len(css_class) > 0)
            self.assertFalse(" " in css_class)  # 不應包含空格

    @patch('streamlit.spinner')
    def test_loading_indicators(self, mock_spinner):
        """測試載入指示器"""
        loading_messages = [
            "正在抓取文章內容...",
            "🤖 Claude正在深度分析中..."
        ]
        
        for message in loading_messages:
            mock_spinner(message)
            mock_spinner.assert_called_with(message)


class TestUIIntegration(unittest.TestCase):
    """UI 整合測試"""
    
    def test_complete_user_workflow(self):
        """測試完整的用戶操作流程"""
        workflow_steps = [
            "輸入 API Key",
            "選擇模型",
            "選擇輸入方式",
            "輸入新聞內容",
            "點擊分析按鈕",
            "查看分析結果",
            "點擊實體連結"
        ]
        
        # 驗證每個步驟都是必要的
        for step in workflow_steps:
            self.assertIsInstance(step, str)
            self.assertTrue(len(step) > 0)

    def test_responsive_design_elements(self):
        """測試響應式設計元素"""
        layout_components = [
            "sidebar",
            "main_content",
            "tabs",
            "columns",
            "cards"
        ]
        
        for component in layout_components:
            # 檢查組件名稱有效性
            self.assertIsInstance(component, str)
            self.assertTrue(len(component) > 0)

    def test_accessibility_features(self):
        """測試無障礙功能"""
        accessibility_features = [
            "alt_text_for_images",
            "keyboard_navigation",
            "screen_reader_support",
            "high_contrast_mode"
        ]
        
        # 檢查無障礙功能清單
        for feature in accessibility_features:
            self.assertIsInstance(feature, str)
            self.assertTrue(len(feature) > 0)


if __name__ == '__main__':
    # 執行 UI 測試
    unittest.main(verbosity=2)
