"""
麵團檢測器 - 核心檢測邏輯
"""
import cv2
import numpy as np
from typing import Dict, Optional, Tuple
from ..utils.image_processor import ImageProcessor


class DoughDetector:
    """麵團檢測器類別"""
    
    def __init__(self, 
                 lower_hsv: Tuple[int, int, int] = (0, 0, 180),
                 upper_hsv: Tuple[int, int, int] = (100, 75, 255)):
        """
        初始化檢測器
        
        Args:
            lower_hsv: HSV 下限
            upper_hsv: HSV 上限
        """
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)
        self.image_processor = ImageProcessor()
    
    def detect_dough_pixels(self, image: np.ndarray) -> Dict:
        """
        檢測麵團像素數量
        
        Args:
            image: 輸入圖像 (BGR 格式)
            
        Returns:
            包含檢測結果的字典
        """
        if image is None:
            raise ValueError("輸入圖像不能為 None")
        
        # 轉換為 HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 創建遮罩
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # 清理雜訊
        mask_cleaned = self._clean_mask(mask)
        
        # 統計像素
        dough_pixels = cv2.countNonZero(mask_cleaned)
        total_pixels = image.shape[0] * image.shape[1]
        dough_percentage = (dough_pixels / total_pixels) * 100
        
        return {
            'total_pixels': total_pixels,
            'dough_pixels': dough_pixels,
            'dough_percentage': dough_percentage,
            'mask': mask_cleaned,
            'original_mask': mask
        }
    
    def detect_from_file(self, image_path: str) -> Optional[Dict]:
        """
        從檔案檢測麵團
        
        Args:
            image_path: 圖像檔案路徑
            
        Returns:
            檢測結果字典，若載入失敗則返回 None
        """
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        return self.detect_dough_pixels(image)
    
    def _clean_mask(self, mask: np.ndarray) -> np.ndarray:
        """清理遮罩雜訊"""
        kernel = np.ones((3, 3), np.uint8)
        # 開運算：去除小雜訊
        mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        # 閉運算：填補小洞
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)
        return mask_cleaned
    
    def update_hsv_range(self, lower_hsv: Tuple[int, int, int], upper_hsv: Tuple[int, int, int]):
        """更新 HSV 範圍"""
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)