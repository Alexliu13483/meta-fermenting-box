import cv2
import numpy as np
import time
import os

# --- 全局參數設定 (請根據您的實際校準結果修改) ---
# 這個值非常重要，需要在實際硬體上校準！
# 例如：如果您測量到 100 像素代表實際 1 公分，則設置為 1 / 100 = 0.01
PIXEL_TO_CM_RATIO = 0.0225

# 影像處理的閾值 (可能需要根據您的麵糰顏色和光照條件調整)
# 這是二值化處理的下限值。OTSU 方法會自動找尋最佳閾值，但手動調整也可能有用。
THRESHOLD_VALUE = 100

# QEMU 模擬模式下使用的預載影像路徑
SIMULATED_IMAGE_PATH = "/usr/bin/sample_dough_image.jpg"
# 實際硬體模式下儲存擷取影像的路徑
CAPTURE_OUTPUT_PATH = "dough_snapshot.jpg"

# 影像擷取函數
def capture_image(camera_index=0, output_path="dough_snapshot.jpg"):
    """
    從攝影機擷取一張影像。
    camera_index: 攝影機索引 (0 為預設)。
                  在 Raspberry Pi 上，通常為 0。
    output_path: 儲存影像的路徑。
    """
    print(f"嘗試從攝影機 {camera_index} 擷取影像...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"錯誤：無法開啟攝影機 {camera_index}。請確認攝影機連接和權限。")
        cap.release()
        return False

    # 設置解析度 (可選，根據您的攝影機和需求調整)
    # 較高的解析度會增加處理時間，但提供更精確的測量
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 讀取多幀以等待攝影機穩定 (可選，對於某些攝影機可能有效)
    for _ in range(5):
        ret, frame = cap.read()
        if not ret:
            print("警告：初始化讀取幀失敗。")
            break

    ret, frame = cap.read() # 讀取最終幀

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"影像已儲存至：{output_path}")
    else:
        print("錯誤：無法讀取影像幀。")

    cap.release() # 釋放攝影機資源
    return ret

# 麵糰尺寸測量函數
def measure_dough_size(image_path, pixel_to_cm_ratio=PIXEL_TO_CM_RATIO):
    """
    從影像中測量麵糰的大小（面積）。
    image_path: 麵糰影像的路徑。
    pixel_to_cm_ratio: 像素到公分的轉換比例 (需要預先校準)。
                       例如，如果 100 像素代表 1 公分，則比例為 0.01。
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"錯誤：無法載入影像 {image_path}。請確認檔案是否存在。")
        return None, None, None

    # 1. 灰度轉換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 高斯模糊 (減少噪點，使邊緣更平滑)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. 閾值處理：將麵糰從背景中分離
    # 使用 OTSU 自動閾值處理，或手動設置 THRESHOLD_VALUE
    # THRESH_BINARY_INV：將麵糰區域變為白色 (255)，背景變為黑色 (0)。
    # 如果麵糰比背景亮，可能需要改用 THRESH_BINARY。
    _, thresh = cv2.threshold(blurred, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 4. 形態學操作 (可選，但常用於去除噪點和連接斷裂的輪廓)
    # 開運算 (OPEN)：先侵蝕後膨脹，去除小塊噪點。
    # 閉運算 (CLOSE)：先膨脹後侵蝕，連接小的斷裂。
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 5. 輪廓檢測 (RETR_EXTERNAL 只會檢測外層輪廓)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("未檢測到任何輪廓。請檢查閾值或影像質量。")
        return None, None, None

    # 6. 找到最大的輪廓（通常是麵糰）
    max_contour = max(contours, key=cv2.contourArea)

    # 7. 計算輪廓面積 (像素單位)
    pixel_area = cv2.contourArea(max_contour)

    # 8. 計算包圍盒 (Bounding Box) 用於估計高度
    x, y, w, h = cv2.boundingRect(max_contour)
    pixel_height = h # 麵糰在影像中的像素高度

    # 9. 將像素面積和高度轉換為實際面積和高度
    actual_area_cm2 = pixel_area * (pixel_to_cm_ratio ** 2)
    actual_height_cm = pixel_height * pixel_to_cm_ratio

    # 10. 可視化結果 (繪製輪廓和顯示數據) - 僅用於除錯或有顯示器時
    output_img = img.copy()
    cv2.drawContours(output_img, [max_contour], -1, (0, 255, 0), 2) # 綠色輪廓
    cv2.rectangle(output_img, (x, y), (x + w, y + h), (255, 0, 0), 2) # 藍色包圍盒

    cv2.putText(output_img, f"Area: {actual_area_cm2:.2f} cm^2", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2) # 紅色文字
    cv2.putText(output_img, f"Height: {actual_height_cm:.2f} cm", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 為了在 Yocto QEMU 環境下方便除錯，你可以將帶有標示的影像儲存起來
    # 而不是直接顯示 (因為 QEMU 環境可能沒有 X11 顯示)
    debug_output_path = "dough_detection_debug.jpg"
    cv2.imwrite(debug_output_path, output_img)
    print(f"偵測結果影像已儲存至：{debug_output_path}")

    print(f"麵糰像素面積：{pixel_area:.2f} 像素")
    print(f"麵糰實際面積：{actual_area_cm2:.2f} cm^2")
    print(f"麵糰像素高度：{pixel_height:.2f} 像素")
    print(f"麵糰實際高度：{actual_height_cm:.2f} cm")

    return actual_area_cm2, actual_height_cm, debug_output_path

# --- 主程式運行邏輯 ---
if __name__ == "__main__":
    # 判斷當前運行環境：QEMU 模擬模式還是實際硬體模式
    # 我們假設在 QEMU 模擬環境中，會將 sample_dough_image.jpg 檔案安裝到 /usr/bin/
    # 實際硬體上則不會有這個檔案。
    is_qemu_simulation = os.path.exists(SIMULATED_IMAGE_PATH)

    if is_qemu_simulation:
        print("偵測到在 QEMU 模擬模式下運行。將使用預載影像進行分析。")
        image_to_process = SIMULATED_IMAGE_PATH
        # 在 QEMU 中，你無法直接擷取影像，所以跳過 capture_image
    else:
        print("偵測到在實際硬體模式下運行。將嘗試擷取攝影機影像。")
        # 嘗試從攝影機擷取影像
        if capture_image(camera_index=0, output_path=CAPTURE_OUTPUT_PATH):
            image_to_process = CAPTURE_OUTPUT_PATH
        else:
            print("影像擷取失敗，無法進行麵糰尺寸分析。")
            exit() # 結束程式

    # 進行麵糰尺寸測量
    area, height, debug_img_path = measure_dough_size(image_to_process, PIXEL_TO_CM_RATIO)

    if area is not None and height is not None:
        print(f"\n--- 最終測量結果 ---")
        print(f"麵糰面積：{area:.2f} cm^2")
        print(f"麵糰高度：{height:.2f} cm")
        print(f"偵測結果圖已儲存為：{debug_img_path}")
    else:
        print("麵糰尺寸測量失敗。")
