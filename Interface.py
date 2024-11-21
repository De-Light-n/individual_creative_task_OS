from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import QGLWidget
import OpenGL.GL as gl
import sys
from pywavefront import Wavefront


class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.scale_factor = 1.0
        self.scale_min = 0.1
        self.scale_max = 10.0
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_mouse_position = None

    def initializeGL(self):
        gl.glClearColor(0.2, 0.2, 0.2, 1.0)  # Сірий фон
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_NORMALIZE)

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect_ratio = w / h if h > 0 else 1
        gl.glOrtho(-aspect_ratio, aspect_ratio, -1, 1, -10, 10)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # Обертання моделі
        gl.glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        gl.glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Масштабування моделі
        gl.glScalef(self.scale_factor, self.scale_factor, self.scale_factor)

        # Відображення моделі
        if self.model:
            for name, mesh in self.model.meshes.items():
                gl.glBegin(gl.GL_TRIANGLES)
                for face in mesh.faces:
                    for vertex_index in face:
                        vertex = self.model.vertices[vertex_index]
                        gl.glVertex3f(*vertex)
                gl.glEnd()

    def load_model(self, file_path):
        try:
            self.model = Wavefront(file_path, collect_faces=True, create_materials=True)
            self.update()
        except Exception as e:
            print(f"Помилка завантаження моделі: {e}")

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.scale_factor += delta * 0.1
        self.scale_factor = max(self.scale_min, min(self.scale_factor, self.scale_max))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position:
            dx = event.x() - self.last_mouse_position.x()
            dy = event.y() - self.last_mouse_position.y()
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.last_mouse_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.last_mouse_position = None



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 605)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # OpenGL віджет
        self.WidgetFor3d = QtWidgets.QWidget(self.centralwidget)
        self.WidgetFor3d.setGeometry(QtCore.QRect(10, 10, 431, 541))
        self.WidgetFor3d.setObjectName("WidgetFor3d")

        # Графічний віджет
        self.graphicsViewForRotatingName = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsViewForRotatingName.setGeometry(QtCore.QRect(790, 450, 171, 101))
        self.graphicsViewForRotatingName.setObjectName("graphicsViewForRotatingName")

        # Текстовий віджет
        self.LabelForText = QtWidgets.QLabel(self.centralwidget)
        self.LabelForText.setGeometry(QtCore.QRect(450, 10, 511, 431))
        font = QtGui.QFont()
        font.setFamily("Sitka Heading Semibold")
        font.setPointSize(16)
        self.LabelForText.setFont(font)
        self.LabelForText.setTextFormat(QtCore.Qt.AutoText)
        self.LabelForText.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelForText.setObjectName("LabelForText")

        # Кнопка для зміни тексту
        self.ButtonForTextChange = QtWidgets.QPushButton(self.centralwidget)
        self.ButtonForTextChange.setGeometry(QtCore.QRect(640, 470, 141, 81))
        self.ButtonForTextChange.setObjectName("ButtonForTextChange")

        # Кнопка для вибору моделі
        self.ButtonToStopMusic = QtWidgets.QPushButton(self.centralwidget)
        self.ButtonToStopMusic.setGeometry(QtCore.QRect(460, 470, 151, 81))
        self.ButtonToStopMusic.setObjectName("ButtonToStopMusic")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "3D Viewer"))
        self.LabelForText.setText(_translate("MainWindow", "ПРИВІТ"))
        self.ButtonForTextChange.setText(_translate("MainWindow", "Змінити текст"))
        self.ButtonToStopMusic.setText(_translate("MainWindow", "Вибрати модель"))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Ініціалізація OpenGLWidget
        self.opengl_widget = OpenGLWidget(self.ui.WidgetFor3d)
        layout = QtWidgets.QVBoxLayout(self.ui.WidgetFor3d)
        layout.addWidget(self.opengl_widget)

        # Налаштовуємо початковий текст
        self.ui.LabelForText.setText("ПРИВІТ")

        # Підключаємо кнопки
        self.ui.ButtonForTextChange.clicked.connect(self.change_text)
        self.ui.ButtonToStopMusic.clicked.connect(self.load_3d_model)

    def change_text(self):
        self.ui.LabelForText.setText("Текст змінено!")

    def load_3d_model(self):
        # Відкриття діалогу для вибору файлу
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Виберіть .obj файл", "", "3D Model Files (*.obj)")
        if file_path:
            self.opengl_widget.load_model(file_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
