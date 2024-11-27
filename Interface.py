import random
import socket
import threading
import winreg
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QGraphicsTextItem
import OpenGL.GL as gl
from pywavefront import Wavefront

from getRules import getRules
from music import play_random_music



# Шлях до розділу реєстру
REG_PATH = r"Software/My3DViewerApp"

def save_to_registry(key, value):
    """
    Зберігає значення в реєстр Windows.
    """
    try:
        # Відкрити або створити ключ у реєстрі
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        # Зберегти значення
        winreg.SetValueEx(reg_key, key, 0, winreg.REG_SZ, str(value))
        winreg.CloseKey(reg_key)
        print(f"Успішно збережено в реєстр: {key} = {value}")
    except Exception as e:
        print(f"Помилка збереження в реєстр: {e}")


def load_from_registry(key):
    """
    Завантажує значення з реєстру Windows.
    """
    try:
        # Відкрити ключ у реєстрі
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        # Прочитати значення
        value, _ = winreg.QueryValueEx(reg_key, key)
        winreg.CloseKey(reg_key)
        print(f"Успішно завантажено з реєстру: {key} = {value}")
        return value
    except FileNotFoundError:
        print(f"Ключ '{key}' не знайдено в реєстрі.")
        return None
    except Exception as e:
        print(f"Помилка завантаження з реєстру: {e}")
        return None

def load_3d_model(self):
    # Відкриття діалогу для вибору файлу
    file_dialog = QtWidgets.QFileDialog(self)
    file_path, _ = file_dialog.getOpenFileName(
        self, "Виберіть .obj файл", "", "3D Model Files (*.obj)"
    )
    if file_path:
        self.opengl_widget.load_model(file_path)
        save_to_registry("last_model_path", file_path)  # Зберігаємо шлях у реєстр


class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.texture_id = None  # Ідентифікатор текстури
        self.scale_factor = 1.0
        self.scale_min = 0.1
        self.scale_max = 10.0
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_mouse_position = None
        self.current_model_path = None

    def initializeGL(self):
        gl.glClearColor(0.0, 1.0, 0.0, 1.0)  # Зелений фон
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_TEXTURE_2D)  # Увімкнення текстур

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect_ratio = w / h if h > 0 else 1
        gl.glOrtho(-aspect_ratio, aspect_ratio, -1, 1, -10, 10)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def load_model(self, file_path):
        """
        Завантаження моделі з автоматичним пошуком текстури.
        """
        try:
            print(f"Завантаження моделі: {file_path}")
            # Завантаження моделі
            self.model = Wavefront(file_path, collect_faces=True, create_materials=True)
            self.current_model_path = file_path
            # Автоматичний пошук текстури
            obj_dir = os.path.dirname(file_path)
            obj_name = os.path.splitext(os.path.basename(file_path))[
                0
            ]  # Ім'я без розширення
            texture_path = os.path.join(
                obj_dir, f"{obj_name}.png"
            )  # Очікувана текстура

            # Завантаження текстури, якщо вона існує
            if os.path.exists(texture_path):
                self.texture_map = {obj_name: self.bind_texture(texture_path)}
                print(f"Текстура завантажена: {texture_path}")
            else:
                print(
                    f"Текстура {texture_path} не знайдена. Використовується стандартний матеріал."
                )
                self.texture_map = {}  # Порожній мап текстур

            self.update()
        except Exception as e:
            print(f"Помилка завантаження моделі: {e}")

    def paintGL(self):
        """
        Рендеринг моделі з автоматичною прив'язкою текстури.
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # Обертання моделі
        gl.glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        gl.glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # Масштабування
        gl.glScalef(self.scale_factor, self.scale_factor, self.scale_factor)

        # Рендеринг моделі
        if self.model:
            for mesh_name, mesh in self.model.meshes.items():
                # Прив'язка текстури (якщо вона є)
                obj_name = os.path.splitext(os.path.basename(self.model.file_name))[0]
                texture_id = self.texture_map.get(obj_name, None)
                if texture_id:
                    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
                else:
                    gl.glBindTexture(
                        gl.GL_TEXTURE_2D, 0
                    )  # Відключити текстуру, якщо вона відсутня

                # Рендеринг мешів
                gl.glBegin(gl.GL_TRIANGLES)
                for face in mesh.faces:
                    for vertex_index in face:
                        vertex = self.model.vertices[vertex_index]
                        if len(vertex) >= 6:
                            gl.glNormal3f(vertex[3], vertex[4], vertex[5])  # Нормалі
                        if len(vertex) >= 8:
                            gl.glTexCoord2f(
                                vertex[6], vertex[7]
                            )  # Текстурні координати
                        gl.glVertex3f(vertex[0], vertex[1], vertex[2])  # Вершини
                gl.glEnd()

    def bind_texture(self, texture_path):
        from PIL import Image

        try:
            image = Image.open(texture_path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
            width, height = image.size

            texture_id = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D,
                0,
                gl.GL_RGBA,
                width,
                height,
                0,
                gl.GL_RGBA,
                gl.GL_UNSIGNED_BYTE,
                img_data,
            )
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            return texture_id
        except Exception as e:
            print(f"Помилка завантаження текстури: {e}")
            return None

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
        # Встановлення фону головного вікна

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
        font.setPointSize(20)
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
        MainWindow.setWindowTitle(_translate("MainWindow", "ПДР для початківців)"))
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

        last_model_path = load_from_registry("last_model_path")
        if last_model_path and os.path.exists(last_model_path):
            self.opengl_widget.load_model(last_model_path)
        elif last_model_path:
            print(f"Файл '{last_model_path}' не знайдено.")
        
        self.setStyleSheet(
            "MainWindow { background-image: url('background5.jpg'); background-repeat: no-repeat; background-position: center; }"
        )
        
        # Форматування текстового віджета
        self.ui.LabelForText.setWordWrap(True)  # Увімкнути перенос слів
        self.ui.LabelForText.setStyleSheet(
            """
            QLabel {
                padding: 10px;  /* Внутрішні відступи */
                color: white;  /* Колір тексту */
                font-size: 20px;  /* Розмір тексту */
                background-color: rgba(0, 0, 0, 0.3);  /* Напівпрозорий фон */
                border-radius: 10px;  /* Закруглені кути */
            }
            """
        )
        
        # Налаштовуємо початковий текст
        self.ui.LabelForText.setText("ПРИВІТ!\n Тута будуть показуватися правила дорожнього руху для початківців)")
        self.rules = []
        self.load_rules_async()

        # Підключаємо кнопки
        self.ui.ButtonForTextChange.clicked.connect(self.change_text)
        self.ui.ButtonToStopMusic.clicked.connect(self.load_3d_model)
        # Налаштовуємо анімацію тексту
        self.setup_rotating_text()
        
        # Таймер для автоматичної зміни тексту
        self.text_timer = QtCore.QTimer(self)
        self.text_timer.timeout.connect(self.change_text)  # Виклик зміни тексту
        self.text_timer.start(10000)  # Інтервал 10 секунд (10000 мс)
        
    def closeEvent(self, event):
        if self.opengl_widget.current_model_path:
            save_to_registry("last_model_path", self.opengl_widget.current_model_path)
        event.accept()
        
    def change_text(self):
        """Змінює текст на інше рандомне речення."""
        if self.rules:
            new_text = random.choice(self.rules)
            self.ui.LabelForText.setText(new_text)

    def load_3d_model(self):
        # Відкриття діалогу для вибору файлу
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Виберіть .obj файл", "", "3D Model Files (*.obj)"
        )
        if file_path:
            self.opengl_widget.load_model(file_path)

    def setup_rotating_text(self):
        # Створення сцени для графічного виду
        self.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsViewForRotatingName.setScene(self.scene)

        # Додавання тексту до сцени
        self.rotating_text = QGraphicsTextItem("Яйко Назар")
        font = QtGui.QFont("Sitka Heading Semibold", 8)
        self.rotating_text.setFont(font)
        self.rotating_text.setDefaultTextColor(
            QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        self.scene.addItem(self.rotating_text)

        self.scene.setSceneRect(-30, -50, 200, 100)
        self.rotating_text.setTransformOriginPoint(self.rotating_text.boundingRect().center())
        # Таймер для обертання тексту
        self.rotation_angle = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.rotate_text)
        self.timer.start(50) 

    def rotate_text(self):
        self.rotation_angle += 5
        self.rotating_text.setRotation(self.rotation_angle)

    def load_rules_async(self):
            """Завантаження правил у фоновому потоці."""
            def fetch_rules():
                rules = getRules()
                self.rules = rules or ["Правила відсутні або не завантажилися."]
                self.ui.LabelForText.setText(self.rules[0])  # Показуємо перше правило, коли вони завантажаться.
            
            threading.Thread(target=fetch_rules, daemon=True).start()

if __name__ == "__main__":
    AUTHORIZED_HOSTNAME = "DESKTOP-PLP53PH"

    if socket.gethostname() != AUTHORIZED_HOSTNAME:
        print("Ця програма може запускатися тільки на ноутбуці Назара!")
        exit()

    print("Програма успішно запущена!")
    app = QtWidgets.QApplication(sys.argv)

    # Запуск вікна
    window = MainWindow()
    window.show()

    # Запуск музики в окремому потоці
    music_thread = threading.Thread(target=play_random_music, args=("Music",), daemon=True)
    music_thread.start()

    sys.exit(app.exec())
