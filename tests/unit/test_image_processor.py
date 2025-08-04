"""
圖像處理工具單元測試
"""
import pytest
import numpy as np
from unittest.mock import patch
from src.dough_monitor.utils.image_processor import ImageProcessor


class TestImageProcessor:
    """ImageProcessor 類別的測試"""
    
    def test_validate_image_valid(self):
        """測試有效圖像驗證"""
        valid_image = np.zeros((100, 100, 3), dtype=np.uint8)
        assert ImageProcessor.validate_image(valid_image) is True
    
    def test_validate_image_none(self):
        """測試 None 圖像驗證"""
        assert ImageProcessor.validate_image(None) is False
    
    def test_validate_image_wrong_dimensions(self):
        """測試錯誤維度的圖像"""
        wrong_dim_image = np.zeros((100, 100), dtype=np.uint8)  # 只有 2 維
        assert ImageProcessor.validate_image(wrong_dim_image) is False
    
    def test_calculate_image_stats(self):
        """測試圖像統計資訊計算"""
        test_image = np.zeros((150, 200, 3), dtype=np.uint8)
        
        stats = ImageProcessor.calculate_image_stats(test_image)
        
        expected_stats = {
            'height': 150,
            'width': 200,
            'channels': 3,
            'total_pixels': 30000
        }
        
        assert stats == expected_stats
    
    def test_calculate_image_stats_invalid_image(self):
        """測試無效圖像的統計計算"""
        with pytest.raises(ValueError, match="無效的圖像"):
            ImageProcessor.calculate_image_stats(None)
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    def test_display_analysis_results_show(self, mock_figure, mock_show):
        """測試顯示分析結果"""
        image = np.zeros((50, 50, 3), dtype=np.uint8)
        hsv = np.zeros((50, 50, 3), dtype=np.uint8)
        mask1 = np.zeros((50, 50), dtype=np.uint8)
        mask2 = np.zeros((50, 50), dtype=np.uint8)
        
        ImageProcessor.display_analysis_results(image, hsv, mask1, mask2, show_plot=True)
        
        # 驗證 matplotlib 函數被呼叫
        mock_figure.assert_called_once()
        mock_show.assert_called_once()
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    def test_display_analysis_results_no_show(self, mock_figure, mock_show):
        """測試不顯示分析結果"""
        image = np.zeros((50, 50, 3), dtype=np.uint8)
        hsv = np.zeros((50, 50, 3), dtype=np.uint8)
        mask1 = np.zeros((50, 50), dtype=np.uint8)
        mask2 = np.zeros((50, 50), dtype=np.uint8)
        
        ImageProcessor.display_analysis_results(image, hsv, mask1, mask2, show_plot=False)
        
        # 驗證 matplotlib 函數沒有被呼叫
        mock_figure.assert_not_called()
        mock_show.assert_not_called()