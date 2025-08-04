"""
圖像處理工具
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple


class ImageProcessor:
    """圖像處理工具類別"""
    
    @staticmethod
    def display_analysis_results(image: np.ndarray, 
                               hsv: np.ndarray, 
                               original_mask: np.ndarray, 
                               cleaned_mask: np.ndarray,
                               show_plot: bool = True) -> None:
        """
        顯示分析結果
        
        Args:
            image: 原始圖像 (BGR)
            hsv: HSV 圖像
            original_mask: 原始遮罩
            cleaned_mask: 清理後的遮罩
            show_plot: 是否顯示圖表
        """
        if not show_plot:
            return
        
        # 轉換為 RGB 顯示
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 4, 1)
        plt.imshow(img_rgb)
        plt.title('Original Image')
        plt.axis('off')
        
        plt.subplot(1, 4, 2)
        plt.imshow(hsv_rgb)
        plt.title('HSV Image')
        plt.axis('off')
        
        plt.subplot(1, 4, 3)
        plt.imshow(original_mask, cmap='gray')
        plt.title('Initial Mask')
        plt.axis('off')
        
        plt.subplot(1, 4, 4)
        plt.imshow(cleaned_mask, cmap='gray')
        plt.title('Cleaned Mask')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def validate_image(image: np.ndarray) -> bool:
        """驗證圖像是否有效"""
        return image is not None and len(image.shape) == 3
    
    @staticmethod
    def calculate_image_stats(image: np.ndarray) -> dict:
        """計算圖像統計資訊"""
        if not ImageProcessor.validate_image(image):
            raise ValueError("無效的圖像")
        
        return {
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2],
            'total_pixels': image.shape[0] * image.shape[1]
        }