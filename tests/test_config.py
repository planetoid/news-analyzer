# 測試配置檔案
"""
NewsAnalyzer 測試配置

包含測試執行的各種配置選項和設定
"""

import os

# 測試環境設定
TEST_CONFIG = {
    # API 測試設定
    "api": {
        "mock_api_key": "test_api_key_12345",
        "timeout": 30,
        "retry_attempts": 3
    },
    
    # 測試資料設定
    "test_data": {
        "sample_urls": [
            "https://example.com/news1",
            "https://example.com/news2", 
            "https://example.com/news3"
        ],
        "sample_content": {
            "short": "短新聞內容測試。",
            "medium": "中等長度的新聞內容測試。" * 10,
            "long": "長篇新聞內容測試。" * 100
        }
    },
    
    # 測試閾值設定
    "thresholds": {
        "min_content_length": 20,
        "max_content_length": 50000,
        "score_range": {"min": 0, "max": 100},
        "analysis_timeout": 30
    },
    
    # 測試模型設定
    "models": {
        "default": "claude-sonnet-4-20250514",
        "alternatives": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229"
        ]
    },
    
    # 預期的實體類型
    "entity_types": [
        "people",
        "numbers", 
        "locations",
        "organizations",
        "dates",
        "datasets"
    ],
    
    # 飲料分類設定
    "drink_categories": {
        "golden_lemon": {
            "truthfulness_min": 70,
            "importance_min": 70,
            "emoji": "🟡",
            "name": "金桔檸檬"
        },
        "honey_green": {
            "truthfulness_min": 70,
            "importance_max": 70,
            "emoji": "🟢", 
            "name": "蜂蜜綠茶"
        },
        "plain_water": {
            "truthfulness_max": 70,
            "importance_max": 70,
            "emoji": "⚪",
            "name": "無糖白開水"
        },
        "expired_milk": {
            "truthfulness_max": 70,
            "importance_min": 70,
            "emoji": "🔴",
            "name": "過期奶茶"
        }
    },
    
    # 外部連結模式
    "link_patterns": {
        "wikipedia": "https://zh.wikipedia.org/wiki/",
        "openstreetmap": "https://www.openstreetmap.org/search?query=",
        "data_gov_tw": "https://data.gov.tw/datasets/search?p=1&size=10&s="
    }
}

# 測試環境變數
def get_test_env():
    """取得測試環境變數"""
    return {
        "TESTING": True,
        "TEST_API_KEY": os.getenv("TEST_API_KEY", TEST_CONFIG["api"]["mock_api_key"]),
        "TEST_TIMEOUT": int(os.getenv("TEST_TIMEOUT", TEST_CONFIG["api"]["timeout"])),
        "VERBOSE": os.getenv("VERBOSE", "1") == "1"
    }

# 測試資料產生器
def generate_test_news(category="general", length="medium"):
    """產生測試用新聞內容"""
    templates = {
        "political": "政府今日宣布新政策，預計影響{number}萬人。部長{person}表示將在{location}推動相關措施。",
        "technology": "科技公司{company}發布新產品，投資金額達{number}億元。執行長{person}指出這將改變{location}的科技生態。",
        "social": "今日在{location}發生重大事件，造成{number}人受影響。相關部門{organization}已介入處理。",
        "general": "最新消息顯示，{location}將實施新措施，預估有{number}人參與。負責人{person}表示樂觀其成。"
    }
    
    base_content = templates.get(category, templates["general"])
    
    # 根據長度要求調整內容
    if length == "short":
        return base_content.format(
            number="10", person="張三", location="台北市", 
            company="ABC公司", organization="相關單位"
        )
    elif length == "long":
        return (base_content + " " + "詳細內容說明。" * 50).format(
            number="100", person="李四", location="高雄市",
            company="XYZ集團", organization="主管機關"
        )
    else:  # medium
        return (base_content + " " + "補充說明內容。" * 5).format(
            number="50", person="王五", location="台中市",
            company="DEF企業", organization="負責機構"
        )

# 驗證函數
def validate_analysis_result(result):
    """驗證分析結果的有效性"""
    required_fields = [
        "summary", "target_audience", "truthfulness", 
        "importance", "impact", "drink_recommendation", "entities"
    ]
    
    for field in required_fields:
        if field not in result:
            return False, f"缺少必要欄位: {field}"
    
    # 驗證評分範圍
    scores = ["truthfulness", "importance", "impact"]
    for score in scores:
        if not (0 <= result[score] <= 100):
            return False, f"評分超出範圍: {score} = {result[score]}"
    
    # 驗證飲料推薦
    if "category" not in result["drink_recommendation"]:
        return False, "缺少飲料分類"
    
    valid_categories = list(TEST_CONFIG["drink_categories"].keys())
    if result["drink_recommendation"]["category"] not in valid_categories:
        return False, f"無效的飲料分類: {result['drink_recommendation']['category']}"
    
    return True, "驗證通過"

# 效能測試設定
PERFORMANCE_CONFIG = {
    "max_analysis_time": 10,  # 秒
    "max_scraping_time": 15,  # 秒
    "concurrent_requests": 5,
    "memory_limit_mb": 512
}
