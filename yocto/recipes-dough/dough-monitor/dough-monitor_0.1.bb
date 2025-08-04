SUMMARY = "Dough Fermentation Monitor Application"
DESCRIPTION = "A Python application for monitoring dough fermentation using OpenCV."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# 1. 設置 S 變數指向實際的檔案來源目錄。
# 當 SRC_URI 只有 file:// 並且沒有壓縮包時，檔案會被複製到 ${WORKDIR} 的根目錄。
# Bitbake 確實會將 `file://` 的內容直接放置到 `S` 指向的目錄。
# 但因為我們沒有解壓縮步驟，S 預設指向的目錄可能不存在，導致警告。
# 最簡單且推薦的做法是，對於只有 file:// 且沒有實際「原始碼」概念的 recipes，
# 讓 S 指向 WORKDIR。雖然你之前嘗試過，但可能與其他配置衝突。
# 讓我們再試一次，並確保 install 路徑正確。

# 正確設置 S 變數：這會告訴 Bitbake 你的「源代碼」位於工作目錄的根。
S = "${WORKDIR}/sources-unpack"


# 指定原始檔
# 這些檔案將在 do_fetch 階段被複製到 ${S} (即 ${WORKDIR})。
SRC_URI = "file://dough_monitor.py \
           file://run_monitor.sh \
           file://sample_dough_image.jpg \
          "

# Build-time 依賴
DEPENDS += "python3-native"

# Runtime 依賴 (確保映像檔中包含這些套件)
RDEPENDS:${PN} += "python3 python3-pip opencv python3-opencv"


do_install() {
    # 建立目標目錄
    install -d ${D}${bindir}

    # 安裝 Python 腳本為可執行檔
    # 現在，因為 S=${WORKDIR}，這些檔案將在 ${WORKDIR} 的根目錄下。
    install -m 0755 ${S}/dough_monitor.py ${D}${bindir}

    # 安裝啟動腳本為可執行檔
    install -m 0755 ${S}/run_monitor.sh ${D}${bindir}

    # 安裝模擬圖片到指定路徑，供 QEMU 模式使用
    install -m 0644 ${S}/sample_dough_image.jpg ${D}${bindir}/sample_dough_image.jpg
}
