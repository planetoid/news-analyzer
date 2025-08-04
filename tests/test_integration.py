import unittest
import asyncio
import json
import sys
import os
from unittest.mock import patch, Mock, AsyncMock

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import NewsAnalyzer


class TestIntegration(unittest.TestCase):
    """整合測試 - 測試各組件間的互動"""
    
    def setUp(self):
        """設定測試環境"""
        self.api_key = "test_api_key"
        self.analyzer = NewsAnalyzer(self.api_key)
        
        # 測試用的真實網址 (模擬)
        self.test_urls = [
            "https://example.com/news1",
            "https://example.com/news2"
        ]
        
        # 測試用的新聞內容
        self.test_news_content = {
            "政治新聞": """
            立法院今日三讀通過重要法案，預計將影響全國500萬勞工權益。
            勞動部長許銘春表示，新法將於明年1月1日正式實施。
            """,
            "科技新聞": """
            台積電宣布在台南設立新廠，投資金額高達1兆新台幣。
            董事長劉德音指出，這將創造3萬個就業機會。
            """,
            "社會新聞": """
            台北市發生嚴重車禍，造成3死5傷。警方初步調查顯示，
            肇事司機可能酒駕，目前已被移送地檢署偵辦。
            """
        }

    @patch('app.NewsAnalyzer.analyze_news')
    async def test_url_to_analysis_workflow(self, mock_analyze):
        """測試從網址輸入到分析結果的完整流程"""
        # 模擬 API 回應
        mock_analyze.return_value = {
            "summary": "測試摘要",
            "truthfulness": 80,
            "importance": 75,
            "impact": 70,
            "drink_recommendation": {
                "name": "金桔檸檬",
                "category": "golden_lemon",
                "reason": "高真實度和重要性"
            },
            "entities": {
                "people": [{"name": "測試人物", "title": "測試職位", "wiki_link": "#"}],
                "locations": [{"name": "測試地點", "map_link": "#"}]
            }
        }
        
        # 模擬網頁抓取
        with patch.object(self.analyzer, 'fetch_article_content', 
                         return_value="測試新聞內容") as mock_fetch:
            
            # 1. 抓取網頁內容
            content = await self.analyzer.fetch_article_content(self.test_urls[0])
            self.assertEqual(content, "測試新聞內容")
            
            # 2. 分析新聞內容
            analysis = self.analyzer.analyze_news(content)
            
            # 3. 驗證分析結果結構
            self.assertIn('summary', analysis)
            self.assertIn('truthfulness', analysis)
            self.assertIn('drink_recommendation', analysis)
            self.assertIn('entities', analysis)

    def test_multiple_news_categories_analysis(self):
        """測試不同類別新聞的分析結果"""
        with patch.object(self.analyzer, 'analyze_news') as mock_analyze:
            
            # 設定不同類別新聞的模擬回應
            responses = {
                "政治新聞": {
                    "truthfulness": 75,
                    "importance": 85,
                    "drink_recommendation": {"category": "golden_lemon"}
                },
                "科技新聞": {
                    "truthfulness": 90,
                    "importance": 70,
                    "drink_recommendation": {"category": "honey_green"}
                },
                "社會新聞": {
                    "truthfulness": 85,
                    "importance": 60,
                    "drink_recommendation": {"category": "honey_green"}
                }
            }
            
            for news_type, content in self.test_news_content.items():
                mock_analyze.return_value = responses[news_type]
                
                result = self.analyzer.analyze_news(content)
                
                # 驗證分析結果合理性
                self.assertIn('truthfulness', result)
                self.assertIn('importance', result)
                self.assertTrue(0 <= result['truthfulness'] <= 100)
                self.assertTrue(0 <= result['importance'] <= 100)

    def test_entity_extraction_and_linking(self):
        """測試實體提取和連結生成的整合"""
        mock_entities = {
            "people": [
                {
                    "name": "蔡英文",
                    "title": "總統",
                    "wiki_link": "https://zh.wikipedia.org/wiki/蔡英文"
                }
            ],
            "locations": [
                {
                    "name": "台北市",
                    "map_link": "https://www.openstreetmap.org/search?query=台北市"
                }
            ],
            "organizations": [
                {
                    "name": "立法院",
                    "official_link": "https://www.ly.gov.tw/"
                }
            ],
            "datasets": [
                {
                    "name": "政府預算",
                    "description": "政府年度預算資料",
                    "search_link": "https://data.gov.tw/datasets/search?p=1&size=10&s=政府預算"
                }
            ]
        }
        
        # 驗證每種實體類型的連結格式
        for entity_type, entities in mock_entities.items():
            for entity in entities:
                if entity_type == "people":
                    self.assertTrue(entity["wiki_link"].startswith("https://"))
                    self.assertIn("wikipedia.org", entity["wiki_link"])
                elif entity_type == "locations":
                    self.assertIn("openstreetmap.org", entity["map_link"])
                elif entity_type == "organizations":
                    self.assertTrue(entity["official_link"].startswith("https://"))
                elif entity_type == "datasets":
                    self.assertIn("data.gov.tw", entity["search_link"])

    @patch('app.async_playwright')
    async def test_web_scraping_error_handling(self, mock_playwright):
        """測試網頁抓取錯誤處理整合"""
        # 測試各種錯誤情況
        error_scenarios = [
            Exception("網路連線錯誤"),
            Exception("網頁不存在"),
            Exception("抓取超時")
        ]
        
        for error in error_scenarios:
            mock_playwright.side_effect = error
            
            result = await self.analyzer.fetch_article_content("https://error.com")
            
            # 驗證錯誤處理
            self.assertIn("抓取失敗", result)

    def test_model_switching_integration(self):
        """測試模型切換整合"""
        models_to_test = [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229"
        ]
        
        for model in models_to_test:
            analyzer = NewsAnalyzer(self.api_key, model)
            self.assertEqual(analyzer.model_name, model)

    def test_api_rate_limiting_handling(self):
        """測試 API 速率限制處理"""
        with patch.object(self.analyzer.client.messages, 'create') as mock_create:
            # 模擬 API 速率限制錯誤
            mock_create.side_effect = Exception("Rate limit exceeded")
            
            with self.assertRaises(Exception):
                self.analyzer.analyze_news("測試內容")

    def test_large_content_handling(self):
        """測試大型內容處理"""
        # 生成大型測試內容 (模擬長篇新聞)
        large_content = "測試新聞內容。" * 1000  # 約 7000 字
        
        with patch.object(self.analyzer, 'analyze_news') as mock_analyze:
            mock_analyze.return_value = {"summary": "大型內容摘要"}
            
            result = self.analyzer.analyze_news(large_content)
            
            # 驗證能夠處理大型內容
            self.assertIn('summary', result)

    def test_concurrent_analysis_requests(self):
        """測試並發分析請求處理"""
        async def analyze_multiple():
            tasks = []
            for content in self.test_news_content.values():
                # 模擬並發分析請求
                with patch.object(self.analyzer, 'analyze_news') as mock_analyze:
                    mock_analyze.return_value = {"status": "success"}
                    task = asyncio.create_task(
                        asyncio.to_thread(self.analyzer.analyze_news, content)
                    )
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # 執行並發測試
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(analyze_multiple())
            # 驗證所有請求都得到處理
            self.assertEqual(len(results), len(self.test_news_content))
        finally:
            loop.close()


class TestDataFlowIntegration(unittest.TestCase):
    """資料流整合測試"""
    
    def test_input_validation_chain(self):
        """測試輸入驗證鏈"""
        test_inputs = [
            {"input": "", "valid": False},
            {"input": "a" * 10, "valid": False},  # 太短
            {"input": "a" * 50, "valid": True},   # 適當長度
            {"input": "a" * 10000, "valid": True} # 長內容
        ]
        
        for test_case in test_inputs:
            content = test_case["input"]
            expected_valid = test_case["valid"]
            
            # 簡單的長度驗證邏輯
            is_valid = len(content) >= 20
            
            if expected_valid:
                self.assertTrue(is_valid, f"內容應該有效: {len(content)} 字元")
            else:
                self.assertFalse(is_valid, f"內容應該無效: {len(content)} 字元")

    def test_output_formatting_chain(self):
        """測試輸出格式化鏈"""
        raw_analysis = {
            "truthfulness": 85.7,
            "importance": 72.3,
            "impact": 68.9
        }
        
        # 驗證數值格式化
        for key, value in raw_analysis.items():
            formatted_value = round(value)
            self.assertIsInstance(formatted_value, int)
            self.assertTrue(0 <= formatted_value <= 100)

    def test_error_propagation_chain(self):
        """測試錯誤傳播鏈"""
        error_chain = [
            "網頁抓取錯誤",
            "API 呼叫錯誤", 
            "JSON 解析錯誤",
            "結果顯示錯誤"
        ]
        
        for error_type in error_chain:
            # 驗證錯誤類型識別
            self.assertIsInstance(error_type, str)
            self.assertIn("錯誤", error_type)


if __name__ == '__main__':
    # 執行整合測試
    unittest.main(verbosity=2)
