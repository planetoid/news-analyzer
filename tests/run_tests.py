#!/usr/bin/env python3
"""
NewsAnalyzer 測試執行腳本

用於執行各種測試套件的主要腳本
"""

import unittest
import sys
import os
import time
import argparse
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 匯入測試模組
from tests.test_analyzer import TestNewsAnalyzer, TestUtilityFunctions
from tests.test_ui import TestStreamlitUI, TestUIIntegration
from tests.test_integration import TestIntegration, TestDataFlowIntegration
from tests.test_config import TEST_CONFIG, get_test_env, validate_analysis_result


class TestRunner:
    """測試執行器"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.test_env = get_test_env()
        
    def run_unit_tests(self):
        """執行單元測試"""
        print("🧪 執行單元測試...")
        suite = unittest.TestSuite()
        
        # 添加分析器測試
        suite.addTest(unittest.makeSuite(TestNewsAnalyzer))
        suite.addTest(unittest.makeSuite(TestUtilityFunctions))
        
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    def run_ui_tests(self):
        """執行 UI 測試"""
        print("🎨 執行 UI 測試...")
        suite = unittest.TestSuite()
        
        # 添加 UI 測試
        suite.addTest(unittest.makeSuite(TestStreamlitUI))
        suite.addTest(unittest.makeSuite(TestUIIntegration))
        
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    def run_integration_tests(self):
        """執行整合測試"""
        print("🔗 執行整合測試...")
        suite = unittest.TestSuite()
        
        # 添加整合測試
        suite.addTest(unittest.makeSuite(TestIntegration))
        suite.addTest(unittest.makeSuite(TestDataFlowIntegration))
        
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 執行所有測試...")
        print(f"測試環境: {self.test_env}")
        print("-" * 60)
        
        start_time = time.time()
        results = []
        
        # 執行各類測試
        test_types = [
            ("單元測試", self.run_unit_tests),
            ("UI 測試", self.run_ui_tests), 
            ("整合測試", self.run_integration_tests)
        ]
        
        for test_name, test_func in test_types:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                results.append((test_name, success))
                status = "✅ 通過" if success else "❌ 失敗"
                print(f"{test_name}: {status}")
            except Exception as e:
                print(f"{test_name}: ❌ 執行錯誤 - {e}")
                results.append((test_name, False))
        
        # 總結報告
        end_time = time.time()
        self.print_summary(results, end_time - start_time)
        
        return all(result[1] for result in results)
    
    def print_summary(self, results, duration):
        """印出測試總結"""
        print("\n" + "="*60)
        print("📊 測試總結報告")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for _, success in results if success)
        
        print(f"總測試類型: {total_tests}")
        print(f"通過測試: {passed_tests}")
        print(f"失敗測試: {total_tests - passed_tests}")
        print(f"執行時間: {duration:.2f} 秒")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n詳細結果:")
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有測試都通過了！")
        else:
            print(f"\n⚠️  有 {total_tests - passed_tests} 個測試失敗")
    
    def run_specific_test(self, test_name):
        """執行特定測試"""
        test_classes = {
            "analyzer": TestNewsAnalyzer,
            "utils": TestUtilityFunctions,
            "ui": TestStreamlitUI,
            "ui_integration": TestUIIntegration,
            "integration": TestIntegration,
            "data_flow": TestDataFlowIntegration
        }
        
        if test_name not in test_classes:
            print(f"❌ 找不到測試: {test_name}")
            print(f"可用的測試: {', '.join(test_classes.keys())}")
            return False
        
        print(f"🎯 執行特定測試: {test_name}")
        suite = unittest.makeSuite(test_classes[test_name])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="NewsAnalyzer 測試執行器")
    parser.add_argument(
        "--type", 
        choices=["unit", "ui", "integration", "all"],
        default="all",
        help="要執行的測試類型"
    )
    parser.add_argument(
        "--specific",
        help="執行特定的測試類別"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="詳細輸出"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="安靜模式"
    )
    
    args = parser.parse_args()
    
    # 設定詳細程度
    verbose = args.verbose and not args.quiet
    
    runner = TestRunner(verbose=verbose)
    
    # 執行測試
    success = False
    
    if args.specific:
        success = runner.run_specific_test(args.specific)
    elif args.type == "unit":
        success = runner.run_unit_tests()
    elif args.type == "ui":
        success = runner.run_ui_tests()
    elif args.type == "integration":
        success = runner.run_integration_tests()
    else:  # all
        success = runner.run_all_tests()
    
    # 設定退出碼
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
