"""
麵團檢測器單元測試
"""
import pytest
import numpy as np
import cv2
from unittest.mock import patch
from src.dough_monitor.core.detector import DoughDetector


class TestDoughDetector:
    """DoughDetector 類別的測試"""
    
    def setup_method(self):
        """每個測試方法前的設定"""
        self.detector = DoughDetector()
        
        # 建立測試用的假圖像
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 在中心創建一個白色正方形 (模擬麵團)
        self.test_image[25:75, 25:75] = [255, 255, 255]
    
    def test_init_default_parameters(self):
        """測試預設參數初始化"""
        detector = DoughDetector()
        
        np.testing.assert_array_equal(detector.lower_hsv, [0, 0, 180])
        np.testing.assert_array_equal(detector.upper_hsv, [100, 75, 255])
    
    def test_init_custom_parameters(self):
        """測試自定義參數初始化"""
        lower = (10, 20, 30)
        upper = (40, 50, 60)
        detector = DoughDetector(lower, upper)
        
        np.testing.assert_array_equal(detector.lower_hsv, [10, 20, 30])
        np.testing.assert_array_equal(detector.upper_hsv, [40, 50, 60])
    
    def test_detect_dough_pixels_valid_image(self):
        """測試有效圖像的麵團檢測"""
        result = self.detector.detect_dough_pixels(self.test_image)
        
        # 檢查返回的字典包含必要的鍵
        expected_keys = ['total_pixels', 'dough_pixels', 'dough_percentage', 'mask', 'original_mask']
        for key in expected_keys:
            assert key in result
        
        # 檢查總像素數
        assert result['total_pixels'] == 10000  # 100x100
        
        # 檢查百分比計算
        expected_percentage = (result['dough_pixels'] / result['total_pixels']) * 100
        assert abs(result['dough_percentage'] - expected_percentage) < 0.01
    
    def test_detect_dough_pixels_none_image(self):
        """測試 None 圖像應該拋出異常"""
        with pytest.raises(ValueError, match="輸入圖像不能為 None"):
            self.detector.detect_dough_pixels(None)
    
    @patch('cv2.imread')
    def test_detect_from_file_success(self, mock_imread):
        """測試成功從檔案檢測"""
        mock_imread.return_value = self.test_image
        
        result = self.detector.detect_from_file("fake_path.jpg")
        
        assert result is not None
        assert 'total_pixels' in result
        mock_imread.assert_called_once_with("fake_path.jpg")
    
    @patch('cv2.imread')
    def test_detect_from_file_failure(self, mock_imread):
        """測試檔案載入失敗"""
        mock_imread.return_value = None
        
        result = self.detector.detect_from_file("non_existent.jpg")
        
        assert result is None
        mock_imread.assert_called_once_with("non_existent.jpg")
    
    def test_clean_mask(self):
        """測試遮罩清理功能"""
        # 建立有雜訊的遮罩
        noisy_mask = np.zeros((50, 50), dtype=np.uint8)
        noisy_mask[10:40, 10:40] = 255  # 主要區域
        noisy_mask[5, 5] = 255  # 小雜訊點
        
        cleaned_mask = self.detector._clean_mask(noisy_mask)
        
        # 確保返回的是同樣大小的遮罩
        assert cleaned_mask.shape == noisy_mask.shape
        # 雜訊點應該被清除（不是完全精確，但應該大幅減少）
        assert np.sum(cleaned_mask) <= np.sum(noisy_mask)
    
    def test_update_hsv_range(self):
        """測試 HSV 範圍更新"""
        new_lower = (5, 10, 15)
        new_upper = (50, 60, 70)
        
        self.detector.update_hsv_range(new_lower, new_upper)
        
        np.testing.assert_array_equal(self.detector.lower_hsv, [5, 10, 15])
        np.testing.assert_array_equal(self.detector.upper_hsv, [50, 60, 70])
    
    def test_detect_white_dough(self):
        """測試白色麵團檢測"""
        # 建立包含白色區域的圖像
        white_image = np.zeros((100, 100, 3), dtype=np.uint8)
        white_image[30:70, 30:70] = [255, 255, 255]  # 白色正方形
        
        result = self.detector.detect_dough_pixels(white_image)
        
        # 應該檢測到一些像素（具體數量取決於 HSV 轉換）
        assert result['dough_pixels'] > 0
        assert result['dough_percentage'] > 0
    
    def test_detect_no_dough(self):
        """測試沒有麵團的圖像"""
        # 建立純黑圖像
        black_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = self.detector.detect_dough_pixels(black_image)
        
        # 應該檢測不到任何像素
        assert result['dough_pixels'] == 0
        assert result['dough_percentage'] == 0.0


class TestDoughDetectorIntegration:
    """DoughDetector 整合測試"""
    
    def test_full_detection_pipeline(self):
        """測試完整的檢測流程"""
        # 建立更真實的測試圖像
        detector = DoughDetector()
        
        # 建立模擬發酵箱內的圖像
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 50  # 暗灰色背景
        
        # 添加白色麵團區域
        cv2.circle(test_image, (100, 100), 30, (255, 255, 255), -1)  # 白色圓形麵團
        
        result = detector.detect_dough_pixels(test_image)
        
        # 驗證結果
        assert result['total_pixels'] == 40000  # 200x200
        assert result['dough_pixels'] > 0
        assert 0 < result['dough_percentage'] < 100
        
        # 驗證遮罩
        assert result['mask'].shape == (200, 200)
        assert result['original_mask'].shape == (200, 200)