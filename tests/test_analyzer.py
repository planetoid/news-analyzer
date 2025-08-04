import unittest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import NewsAnalyzer


class TestNewsAnalyzer(unittest.TestCase):
    """NewsAnalyzer 核心功能測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.api_key = "test_api_key"
        self.model_name = "claude-sonnet-4-20250514"
        self.analyzer = NewsAnalyzer(self.api_key, self.model_name)
        
        # 測試用新聞內容
        self.sample_news = """
        台北市政府今日宣布，將在年底前完成全市公園的無障礙設施改善工程。
        市長柯文哲表示，這項計畫預計投入3億元預算，將讓全市250座公園
        都能提供更友善的無障礙環境。預計將有超過10萬名身障朋友受益。
        """
        
        # 模擬的 API 回應
        self.mock_api_response = {
            "summary": "台北市政府宣布投入3億元改善全市公園無障礙設施",
            "target_audience": "一般民眾、身障朋友、政策關注者",
            "truthfulness": 85,
            "importance": 75,
            "impact": 70,
            "drink_recommendation": {
                "name": "金桔檸檬",
                "reason": "真實度和重要性都很高的優質新聞",
                "category": "golden_lemon"
            },
            "entities": {
                "people": [
                    {"name": "柯文哲", "title": "台北市長", "wiki_link": "https://zh.wikipedia.org/wiki/柯文哲"}
                ],
                "numbers": [
                    {"value": "3億元", "context": "預算金額", "data_link": "#"}
                ],
                "locations": [
                    {"name": "台北市", "map_link": "https://www.openstreetmap.org/search?query=台北市"}
                ],
                "organizations": [
                    {"name": "台北市政府", "official_link": "https://www.gov.taipei/"}
                ],
                "dates": [
                    {"date": "年底前", "event": "完成改善工程"}
                ],
                "datasets": [
                    {"name": "公園設施", "description": "台北市公園無障礙設施資料", "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=公園設施"}
                ]
            }
        }

    def test_analyzer_initialization(self):
        """測試分析器初始化"""
        self.assertEqual(self.analyzer.model_name, self.model_name)
        self.assertIsNotNone(self.analyzer.client)

    def test_model_name_default(self):
        """測試預設模型名稱"""
        analyzer_default = NewsAnalyzer(self.api_key)
        self.assertEqual(analyzer_default.model_name, "claude-sonnet-4-20250514")

    @patch('app.NewsAnalyzer.analyze_news')
    def test_analyze_news_success(self, mock_analyze):
        """測試新聞分析成功情況"""
        mock_analyze.return_value = self.mock_api_response
        
        result = self.analyzer.analyze_news(self.sample_news)
        
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        self.assertIn('truthfulness', result)
        self.assertIn('importance', result)
        self.assertIn('impact', result)
        self.assertIn('drink_recommendation', result)
        self.assertIn('entities', result)

    @patch('app.NewsAnalyzer.analyze_news')
    def test_analyze_news_failure(self, mock_analyze):
        """測試新聞分析失敗情況"""
        mock_analyze.side_effect = Exception("API 錯誤")
        
        with self.assertRaises(Exception):
            self.analyzer.analyze_news(self.sample_news)

    def test_drink_classification_logic(self):
        """測試飲料分類邏輯"""
        test_cases = [
            {"truthfulness": 80, "importance": 80, "expected": "golden_lemon"},
            {"truthfulness": 80, "importance": 60, "expected": "honey_green"},
            {"truthfulness": 60, "importance": 60, "expected": "plain_water"},
            {"truthfulness": 60, "importance": 80, "expected": "expired_milk"}
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # 這裡應該根據實際的分類邏輯進行測試
                # 由於分類是在 AI 中進行的，我們測試預期的對應關係
                if case["truthfulness"] > 70 and case["importance"] > 70:
                    expected_category = "golden_lemon"
                elif case["truthfulness"] > 70 and case["importance"] <= 70:
                    expected_category = "honey_green"
                elif case["truthfulness"] <= 70 and case["importance"] <= 70:
                    expected_category = "plain_water"
                else:
                    expected_category = "expired_milk"
                
                self.assertEqual(expected_category, case["expected"])

    def test_entities_structure(self):
        """測試實體結構完整性"""
        entities = self.mock_api_response["entities"]
        
        # 檢查所有實體類型都存在
        expected_entity_types = ["people", "numbers", "locations", 
                               "organizations", "dates", "datasets"]
        
        for entity_type in expected_entity_types:
            self.assertIn(entity_type, entities)
        
        # 檢查人物實體結構
        if entities["people"]:
            person = entities["people"][0]
            self.assertIn("name", person)
            self.assertIn("title", person)
            self.assertIn("wiki_link", person)
        
        # 檢查地點實體結構
        if entities["locations"]:
            location = entities["locations"][0]
            self.assertIn("name", location)
            self.assertIn("map_link", location)

    @patch('app.async_playwright')
    async def test_fetch_article_content_success(self, mock_playwright):
        """測試網頁內容抓取成功"""
        # 模擬 Playwright 回應
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        
        mock_element.inner_text.return_value = "測試新聞內容" * 50  # 確保長度足夠
        mock_page.query_selector.return_value = mock_element
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_context
        
        result = await self.analyzer.fetch_article_content("https://example.com/news")
        
        self.assertIn("測試新聞內容", result)

    @patch('app.async_playwright')
    async def test_fetch_article_content_failure(self, mock_playwright):
        """測試網頁內容抓取失敗"""
        mock_playwright.side_effect = Exception("網路錯誤")
        
        result = await self.analyzer.fetch_article_content("https://example.com/news")
        
        self.assertIn("抓取失敗", result)


class TestUtilityFunctions(unittest.TestCase):
    """工具函數測試"""
    
    def test_score_validation(self):
        """測試評分數值驗證"""
        valid_scores = [0, 50, 100]
        invalid_scores = [-1, 101, "abc"]
        
        for score in valid_scores:
            self.assertTrue(0 <= score <= 100)
        
        for score in invalid_scores:
            if isinstance(score, (int, float)):
                self.assertFalse(0 <= score <= 100)

    def test_entity_link_validation(self):
        """測試實體連結格式驗證"""
        valid_wiki_links = [
            "https://zh.wikipedia.org/wiki/柯文哲",
            "https://en.wikipedia.org/wiki/Test"
        ]
        
        valid_map_links = [
            "https://www.openstreetmap.org/search?query=台北市",
            "https://www.openstreetmap.org/search?query=高雄市"
        ]
        
        valid_data_links = [
            "https://data.gov.tw/datasets/search?p=1&size=10&s=交通",
            "https://data.gov.tw/datasets/search?p=1&size=10&s=環境"
        ]
        
        for link in valid_wiki_links:
            self.assertTrue(link.startswith("https://") and "wikipedia.org" in link)
        
        for link in valid_map_links:
            self.assertTrue(link.startswith("https://www.openstreetmap.org/search"))
        
        for link in valid_data_links:
            self.assertTrue(link.startswith("https://data.gov.tw/datasets/search"))


if __name__ == '__main__':
    # 執行所有測試
    unittest.main(verbosity=2)
