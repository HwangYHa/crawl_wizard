import os, sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import urllib.request
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
import logging

options = Options()
# VGA 가속화를 끔.
options.add_argument('disable-gpu')
# 브라우저 창을 숨김(백그라운드 실행 옵션)
options.add_argument('--headless')  # options.headless = True
# --headless 상태에서, agent 정보를 표기하기 위해 필요하다고 함.
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/3.12.129.46 Safari/537.36')
# 불필요한 로그를 출력하지 않도록 함.
os.environ['WDM_LOG_LEVEL'] = '0'


caps = DesiredCapabilities().CHROME
caps['pageLoadStrategy'] = "none"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(2)
driver.get("https://www.google.co.kr/imghp?hl=ko&tab=wi&authuser=0&ogbl")
elem = driver.find_element(By.NAME, "q")

main_directory = "downloads"

date_strftime_format = "%d-%b-%y %H:%M:%S"
message_format = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(filename='log.log', level=logging.INFO, format=message_format, datefmt=date_strftime_format, encoding='utf-8')

# form_class = uic.loadUiType("crawling_ui.ui")[0]

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setFixedHeight(150)
        self.widget.verticalScrollBar().setValue(
        self.widget.verticalScrollBar().maximum())

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.ensureCursorVisible()
        self.widget.viewport().update()

class WindowClass(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.search_btn.clicked.connect(self.googleImageCrawling)

    def googleImageCrawling(self):
        self.log_tb.clear()
        keyword = self.keyword_te.text()
        limit = int(self.imgCnt_te.text())
        size = self.size_cb.currentText().replace(" X ", ',')


        if size == "해상도 설정":
            QMessageBox.about(self, '해상도 설정', '해상도를 선택해주세요')
        else:
            elem.send_keys(keyword)
            elem.send_keys(Keys.RETURN)
            last_height = driver.execute_script("return document.body.scrollHeight")    # 스크롤 높이 가져옴

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    # 끝까지 스크롤 다운
                new_height = driver.execute_script("return document.body.scrollHeight")     # 스크롤 다운 후 스크롤 높이 다시 가져옴
                if new_height == last_height:
                    try:
                        driver.find_element(By.CSS_SELECTOR, ".mye4qd").click()
                    except:
                        break
                last_height = new_height

            images = driver.find_elements(By.CSS_SELECTOR, ".rg_i.Q4LuWd")

            if not os.path.isdir(main_directory):  # 없으면 새로 생성하는 조건문
                os.mkdir(main_directory)

            if not os.path.isdir(main_directory+'/'+keyword):  # 없으면 새로 생성하는 조건문
                os.mkdir(main_directory+'/'+keyword)

            count = 1
            for image in images:
                image.click()
                # imgUrl = driver.find_element(By.XPATH, '/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div/div/div[2]/div[2]/div[2]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/a/img').get_attribute("src")
                imgUrl = driver.find_element(By.CLASS_NAME, 'n3VNCb.KAlRDb').get_attribute("src")
                qmark = imgUrl.rfind('?')
                slash = imgUrl.rfind('/', 0, qmark) + 1
                imageNm = str(imgUrl[slash:qmark]).lower()
                fileNm = keyword + "_{}.jpg".format(count)
                fileNm_Msg = "Completed Image ====> " + fileNm
                imageUrl_Msg = "Image URL: " + imgUrl
                self.log_tb.append(str(fileNm_Msg))
                self.log_tb.append(str(imageUrl_Msg))


                print("Completed Image  ===> ", str(count) + "." + imageNm)
                print("Image URL: ", imgUrl)

                img = urllib.request.urlretrieve(imgUrl, f"./downloads/%s/" % (keyword) + keyword + "_" + str(count) + ".jpg")
                resolution = size.replace(",", "")
                if resolution == "6464":
                    img = Image.open(f"./downloads/%s/" % (keyword)+fileNm)
                    resize = img.resize((64, 64))
                elif resolution == "128128":
                    img = Image.open(f"./downloads/%s/" % (keyword)+fileNm)
                    resize = img.resize((128, 128))
                elif resolution == "256256":
                    img = Image.open(f"./downloads/%s/" % (keyword)+fileNm)
                    resize = img.resize((256, 256))
                else:
                    img = Image.open(f"./downloads/%s/" % (keyword)+fileNm)
                    resize = img.resize((512, 512))
                resize.save(f"./downloads/%s/" % (keyword) + fileNm)

                if count == limit:
                    self.keyword_te.clear()
                    self.imgCnt_te.clear()
                    driver.quit()
                    break;


                count = count + 1


    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(430, 399)
        self.search_btn = QtWidgets.QPushButton(dialog)
        self.search_btn.setGeometry(QtCore.QRect(320, 350, 80, 30))
        self.search_btn.setObjectName("search_btn")
        self.keyword_lbl = QtWidgets.QLabel(dialog)
        self.keyword_lbl.setGeometry(QtCore.QRect(50, 27, 90, 40))
        self.keyword_lbl.setObjectName("keyword_lbl")
        self.developerNm_lbl = QtWidgets.QLabel(dialog)
        self.developerNm_lbl.setGeometry(QtCore.QRect(10, 370, 81, 21))
        self.developerNm_lbl.setObjectName("developerNm_lbl")
        self.cnt_lbl = QtWidgets.QLabel(dialog)
        self.cnt_lbl.setGeometry(QtCore.QRect(50, 60, 80, 40))
        self.cnt_lbl.setObjectName("cnt_lbl")
        self.version_lbl = QtWidgets.QLabel(dialog)
        self.version_lbl.setGeometry(QtCore.QRect(380, 0, 40, 21))


        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.version_lbl.setFont(font)
        self.version_lbl.setObjectName("version_lbl")
        self.log_tb = QtWidgets.QTextBrowser(dialog)
        self.log_tb.setGeometry(QtCore.QRect(25, 140, 380, 200))
        self.log_tb.setAutoFillBackground(False)
        self.log_tb.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.log_tb.setObjectName("log_tb")
        self.size_cb = QtWidgets.QComboBox(dialog)
        self.size_cb.setGeometry(QtCore.QRect(180, 350, 101, 31))
        self.size_cb.setObjectName("size_cb")
        self.size_cb.addItem("")
        self.size_cb.addItem("")
        self.size_cb.addItem("")
        self.size_cb.addItem("")
        self.size_cb.addItem("")
        self.keyword_te = QtWidgets.QLineEdit(dialog)
        self.keyword_te.setGeometry(QtCore.QRect(160, 30, 180, 30))
        self.keyword_te.setObjectName("keyword_te")
        self.imgCnt_te = QtWidgets.QLineEdit(dialog)
        self.imgCnt_te.setGeometry(QtCore.QRect(160, 70, 180, 30))
        self.imgCnt_te.setObjectName("imgCnt_te")

        self.retranslateUi(dialog)
        self.imgCnt_te.returnPressed.connect(self.search_btn.click)
        QtCore.QMetaObject.connectSlotsByName(dialog)
        dialog.setTabOrder(self.keyword_te, self.imgCnt_te)
        dialog.setTabOrder(self.imgCnt_te, self.size_cb)
        dialog.setTabOrder(self.size_cb, self.search_btn)
        dialog.setTabOrder(self.search_btn, self.log_tb)

    def retranslateUi(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("dialog", "크롤링 마법사"))
        self.search_btn.setText(_translate("dialog", "검색"))
        self.keyword_lbl.setText(_translate("dialog", "키 워 드   입 력:"))
        self.developerNm_lbl.setText(_translate("dialog", "by. 황용하"))
        self.cnt_lbl.setText(_translate("dialog", "이미지 수 입력:"))
        self.version_lbl.setText(_translate("dialog", "V 1.2"))
        self.size_cb.setItemText(0, _translate("dialog", "해상도 설정"))
        self.size_cb.setItemText(1, _translate("dialog", "64 X 64"))
        self.size_cb.setItemText(2, _translate("dialog", "128 X 128"))
        self.size_cb.setItemText(3, _translate("dialog", "256 X 256"))
        self.size_cb.setItemText(4, _translate("dialog", "512 X 512"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    # app.exec_()

    # dialog = QtWidgets.QDialog()
    # ui = Ui_dialog()
    # myWindow.setupUi(dialog)
    # dialog.show()
    sys.exit(app.exec_())