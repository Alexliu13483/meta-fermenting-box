#!/bin/sh

# run_monitor.sh
# 啟動麵糰發酵監控應用程式的腳本

# 定義你的 Python 腳本的路徑
# 在 Yocto recipe 的 do_install 步驟中，我們將 dough_monitor.py 安裝到了 /usr/bin/
DOUGH_MONITOR_SCRIPT="/usr/bin/dough_monitor.py"

# 定義日誌檔案的路徑
LOG_DIR="/var/log/dough_monitor"
LOG_FILE="${LOG_DIR}/dough_monitor_$(date +%Y%m%d_%H%M%S).log"
ERROR_LOG_FILE="${LOG_DIR}/dough_monitor_error_$(date +%Y%m%d_%H%M%S).log"

# 確保日誌目錄存在
mkdir -p "$LOG_DIR"

echo "[$DOUGH_MONITOR_SCRIPT] 啟動麵糰監控服務..." | tee -a "$LOG_FILE"
echo "日誌將儲存至：$LOG_FILE" | tee -a "$LOG_FILE"

# 使用 nohup 和 & 在後台運行 Python 腳本，並將輸出重定向到日誌檔案
# nohup: 防止在終端關閉後進程終止
# &: 在後台運行
# >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE": 將標準輸出追加到 LOG_FILE，標準錯誤追加到 ERROR_LOG_FILE
nohup python3 "$DOUGH_MONITOR_SCRIPT" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE" &

# 獲取剛啟動的進程的 PID
PID=$!
echo "麵糰監控應用程式已在後台啟動，PID 為 $PID" | tee -a "$LOG_FILE"

# 可選：等待一小段時間確保進程啟動，然後檢查其狀態
sleep 2

# 檢查進程是否仍在運行
if ps -p $PID > /dev/null
then
   echo "PID $PID 正在運行中。" | tee -a "$LOG_FILE"
else
   echo "錯誤：PID $PID 未能啟動或已終止。" | tee -a "$LOG_FILE"
   echo "請檢查錯誤日誌檔：$ERROR_LOG_FILE" | tee -a "$LOG_FILE"
   exit 1
fi

exit 0
