"""
顏色分析器 - HSV 顏色範圍調整工具
"""
import cv2
import numpy as np
from typing import Callable, Tuple, Optional


class ColorAnalyzer:
    """HSV 顏色範圍互動式調整工具"""
    
    def __init__(self, image_path: str):
        """
        初始化顏色分析器
        
        Args:
            image_path: 圖像檔案路徑
        """
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"無法載入圖像: {image_path}")
        
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        self.window_name = 'HSV Adjustment'
        
    def adjust_range_interactive(self, 
                                initial_lower: Tuple[int, int, int] = (0, 0, 180),
                                initial_upper: Tuple[int, int, int] = (100, 75, 255),
                                callback: Optional[Callable] = None) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        互動式調整 HSV 範圍
        
        Args:
            initial_lower: 初始下限
            initial_upper: 初始上限
            callback: 像素數量變化時的回調函數
            
        Returns:
            調整後的 (lower, upper) HSV 範圍
        """
        cv2.namedWindow(self.window_name)
        
        # 創建滑桿
        cv2.createTrackbar('H_min', self.window_name, initial_lower[0], 179, lambda x: None)
        cv2.createTrackbar('S_min', self.window_name, initial_lower[1], 255, lambda x: None)
        cv2.createTrackbar('V_min', self.window_name, initial_lower[2], 255, lambda x: None)
        cv2.createTrackbar('H_max', self.window_name, initial_upper[0], 179, lambda x: None)
        cv2.createTrackbar('S_max', self.window_name, initial_upper[1], 255, lambda x: None)
        cv2.createTrackbar('V_max', self.window_name, initial_upper[2], 255, lambda x: None)
        
        while True:
            # 取得滑桿值
            h_min = cv2.getTrackbarPos('H_min', self.window_name)
            s_min = cv2.getTrackbarPos('S_min', self.window_name)
            v_min = cv2.getTrackbarPos('V_min', self.window_name)
            h_max = cv2.getTrackbarPos('H_max', self.window_name)
            s_max = cv2.getTrackbarPos('S_max', self.window_name)
            v_max = cv2.getTrackbarPos('V_max', self.window_name)
            
            # 創建遮罩
            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])
            mask = cv2.inRange(self.hsv, lower, upper)
            
            # 顯示結果
            result = cv2.bitwise_and(self.image, self.image, mask=mask)
            display = np.hstack([self.image, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), result])
            display = cv2.resize(display, (1200, 400))
            
            cv2.imshow(self.window_name, display)
            
            # 統計像素並執行回調
            pixels = cv2.countNonZero(mask)
            if callback:
                callback(pixels)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        return (h_min, s_min, v_min), (h_max, s_max, v_max)