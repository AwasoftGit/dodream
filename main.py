from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor, QPalette, QFontDatabase
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QSplitter, QGraphicsScene, QComboBox
from PySide6.QtWidgets import QApplication
from PySide6 import QtCore, QtWidgets
import sys, model, os





class MainUI(QMainWindow):

    def __init__(self, width, height):
        super(MainUI, self).__init__()

        self.ui_w = width * 0.85    # 창 크기 설정
        self.ui_h = height * 0.85   # 창 크기 설정
        self.init_window()  # 윈도우 설정

        self.base_json = {}

        self.property_class_name = None
        self.property_class_dict = {}

        self.base_layout = QVBoxLayout()    # 전체 레이아웃
        self.head_layout = QHBoxLayout()  # 클래스 정보, 파일 열기, 분석 버튼
        self.base_body_layout = QHBoxLayout()  # 몸통 레이아웃 ( 주요 컨텐츠)
        self.base_body_splitter = QSplitter()   # canvas, menu 사이즈 변경


        self.init_base_layout()
        self.init_head_layout()
        self.init_body_layout()  # body 레이아웃 할당

        widget = QWidget()
        widget.setLayout(self.base_layout)
        self.setCentralWidget(widget)
        self.setStyleSheet("QLabel {color: #CCCCCC;}")
        self.open_dir = './'
        self.image_path = ''


    def init_window(self):
        """
        윈도우 창 세팅
        """
        self.resize(self.ui_w, self.ui_h)  # 윈도우 창 사이즈 설정

        background = QPalette()   # 창에 색상 적용 가능하게 팔레트 호출
        # background.setColor(self.backgroundRole(), QColor(255, 255, 255))    # 창 배경에 적용할 색을 저장
        background.setColor(self.backgroundRole(), QColor(24, 88, 88))    # 창 배경에 적용할 색을 저장
        self.setPalette(background)  # 색상 적용

        font_database = QFontDatabase()
        font_database.addApplicationFont('./font/nanum-square-round/NanumSquareRoundR.ttf') # 폰트 추가
        self.setFocusPolicy(Qt.StrongFocus)
        # self.setWindowFlag(Qt.)

    def init_base_layout(self):
        """
        base layout 위젯 및 레이아웃 할당
        """

        self.setLayout(self.base_layout)

  # fuction_layout에 기능 위젯 할당
        self.base_layout.addLayout(self.head_layout, 10)
        self.base_layout.addLayout(self.base_body_layout, 87)
        self.base_layout.setContentsMargins(0, 0, 0, 0)  # 메인 레이아웃 margin은 0으로 설정
        self.base_layout.setSpacing(0)  # 레이아웃 간의 간격은 0으로 설정

    def init_head_layout(self):

        self.setLayout(self.head_layout)

        self.grid_layout = QGridLayout()

        self.label_class = QLabel()
        self.label_class.setText("Classes")
        self.label_class.setScaledContents(True)
        self.label_class.setStyleSheet('font: bold 15px')
        self.label_class.setMargin(0)
        # self.label_class.setAlignment(Qt.AlignCenter)
        # self.head_layout.addWidget(self.label_class)
        self.choice_class = QComboBox()
        self.choice_class.addItems(['Julnun', 'Pothole', 'Crack'])
        # self.head_layout.addWidget(self.choice_class)
        self.open_btn = QPushButton("열기")
        self.open_btn.clicked.connect(self.openBtn)

        self.model_run_btn = QPushButton("분석")
        self.model_run_btn.clicked.connect(self.analyzeBtn)


        self.grid_layout.setSpacing(0)
        self.grid_layout.addWidget(self.label_class, 0, 1)
        self.grid_layout.addWidget(self.choice_class, 1, 1,1,1, Qt.AlignCenter)
        self.grid_layout.addWidget(self.open_btn, 0,2,1,2, Qt.AlignRight)
        self.grid_layout.addWidget(self.model_run_btn, 1,2,1,2, Qt.AlignRight)
        self.space_layout = QLabel()
        self.head_layout.addWidget(self.space_layout, 95)
        self.head_layout.addLayout(self.grid_layout, 5)


    def init_body_layout(self):
        """
        body layout 위젯 할당
        """
        self.origin_frame = QLabel()
        self.origin_frame.setScaledContents(True)
        self.origin_frame.setPixmap(QPixmap("julnun1.jpg").scaled(self.origin_frame.size(), Qt.KeepAspectRatio))
        # self.origin_frame.setFixedSize(800,800)
        self.result_frame = QLabel()
        self.result_frame.setPixmap(QPixmap("julnun2.jpg").scaled(self.result_frame.size(), Qt.KeepAspectRatio))
        self.result_frame.setScaledContents(True)

        self.base_body_layout.addWidget(self.origin_frame, 40)
        self.base_body_layout.addWidget(self.result_frame, 40)
        self.base_body_layout.setContentsMargins(0, 0, 0, 0)  # 메인 레이아웃 margin은 0으로 설정
        self.base_body_layout.setSpacing(10)  # 레이아웃 간의 간격은 0으로 설정

    def openBtn(self):

        self.image_path, _ = QFileDialog.getOpenFileNames(self, "Open Image", '',
                                                              "JPG,PNG(*.jpg *.jpeg *.png *.tif *bmp);;All Files(*.*)")
        self.origin_frame.setPixmap(QPixmap(self.image_path[0]).scaled(self.origin_frame.size(), Qt.KeepAspectRatio))

    def analyzeBtn(self):

        if self.image_path and self.image_path != "":
            subtext = self.choice_class.currentText()
            if subtext in ['Julnun', 'Pothole']:
                result_img = self.runModel(self.image_path[0],subtext)
            else:
                result_img = self.run_mask_Model(self.image_path[0])
            self.result_frame.setPixmap(result_img.scaled(self.origin_frame.size(), Qt.KeepAspectRatio))
        else:
            pass

    def runModel(self, img_path, subtext):
        result_img = model.modelRun(img_path, subtext)
        return result_img

    def run_mask_Model(self, img_path):
        result_img = model.mmodelRun(img_path)
        return result_img

if __name__ == "__main__":

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)

    screen = QApplication.primaryScreen()
    screen_width = screen.availableSize().width() * screen.devicePixelRatio()
    screen_height = screen.availableSize().height() * screen.devicePixelRatio()

    ex = MainUI(screen_width, screen_height)
    ex.show()
    sys.exit(app.exec())

