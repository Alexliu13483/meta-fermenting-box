"""
顏色分析器單元測試
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.dough_monitor.core.color_analyzer import ColorAnalyzer


class TestColorAnalyzer:
    """ColorAnalyzer 類別的測試"""
    
    @patch('cv2.imread')
    def test_init_success(self, mock_imread):
        """測試成功初始化"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = test_image
        
        analyzer = ColorAnalyzer("test_path.jpg")
        
        assert analyzer.image is not None
        assert analyzer.hsv is not None
        mock_imread.assert_called_once_with("test_path.jpg")
    
    @patch('cv2.imread')
    def test_init_file_not_found(self, mock_imread):
        """測試檔案不存在的情況"""
        mock_imread.return_value = None
        
        with pytest.raises(FileNotFoundError, match="無法載入圖像"):
            ColorAnalyzer("non_existent.jpg")
    
    @patch('cv2.imread')
    @patch('cv2.namedWindow')
    @patch('cv2.createTrackbar')
    @patch('cv2.getTrackbarPos')
    @patch('cv2.imshow')
    @patch('cv2.waitKey')
    @patch('cv2.destroyAllWindows')
    def test_adjust_range_interactive(self, 
                                    mock_destroy, mock_waitkey, mock_imshow,
                                    mock_get_trackbar, mock_create_trackbar,
                                    mock_named_window, mock_imread):
        """測試互動式範圍調整"""
        # 設定 mock
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = test_image
        mock_waitkey.return_value = ord('q')  # 模擬按下 'q' 退出
        
        # 模擬滑桿值
        trackbar_values = [10, 20, 30, 100, 150, 200]
        mock_get_trackbar.side_effect = trackbar_values
        
        analyzer = ColorAnalyzer("test_path.jpg")
        lower, upper = analyzer.adjust_range_interactive()
        
        # 驗證結果
        assert lower == (10, 20, 30)
        assert upper == (100, 150, 200)
        
        # 驗證 OpenCV 函數被呼叫
        mock_named_window.assert_called_once()
        assert mock_create_trackbar.call_count == 6  # 6 個滑桿
        mock_destroy.assert_called_once()