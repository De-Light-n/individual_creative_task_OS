import random
import socket
import threading
import winreg
import sys
import os
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsTextItem

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

def load_model_and_texture_from_registry():
    model_path = load_from_registry("last_model_path")
    texture_path = load_from_registry("last_texture_path")
    return model_path, texture_path

class VTKWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.vtkWidget)
        self.setLayout(layout)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

    def load_model_with_texture(self, model_path, texture_path=None):
        # Перевірка шляху до моделі
        if not model_path:
            print("Шлях до моделі не передано.")
            return
        # Очищення сцени перед додаванням нової моделі
        self.renderer.RemoveAllViewProps()

        # Читання моделі
        reader = vtk.vtkOBJReader()
        reader.SetFileName(model_path)

        # Відображення моделі
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Якщо шлях до текстури передано, додаємо текстуру
        if texture_path and os.path.exists(texture_path):
            texture_reader = vtk.vtkJPEGReader() if texture_path.endswith(".jpg") else vtk.vtkPNGReader()
            texture_reader.SetFileName(texture_path)

            texture = vtk.vtkTexture()
            texture.SetInputConnection(texture_reader.GetOutputPort())
            texture.InterpolateOn()  # Гладке накладання текстури

            actor.SetTexture(texture)
        else:
            print("Текстуру не передано або файл текстури не існує. Модель буде відображена без текстури.")

        # Додавання до сцени
        self.renderer.AddActor(actor)
        self.renderer.SetBackground(0.2, 0.2, 0.2)  # Темно-синій фон
        self.vtkWidget.GetRenderWindow().Render()

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
        self.model_path = None
        self.texture_path = None
        self.model_texture_dict = {
            "Models_2/Radcar.obj": "Models_2/Radcar.png",
            "Models_2/Sign.obj": "Models_2/Sign.jpg",
            "Models_2/Sign02.obj": "Models_2/Sign02.jpg",  # Модель без текстури
        }
        self.current_model_index = 0  # Індекс поточної моделі
        
        # Ініціалізація VTKWidget
        self.vtk_widget = VTKWidget(self.ui.WidgetFor3d)
        layout = QtWidgets.QVBoxLayout(self.ui.WidgetFor3d)
        layout.addWidget(self.vtk_widget)

        # Підключення кнопки для завантаження моделі
        self.ui.ButtonToStopMusic.clicked.connect(self.load_vtk_model)

        self.model_timer = QtCore.QTimer(self)
        self.model_timer.timeout.connect(self.load_next_model)
        self.model_timer.start(10000)  # Інтервал 10 секунд
        
        # Автоматичне завантаження останньої моделі
        self.load_last_model()
        
        # Завантаження моделі та текстури
        self.vtk_widget.load_model_with_texture(self.model_path, self.texture_path)
        
        self.setStyleSheet(
            "MainWindow { background-image: url('background6.jpg'); background-repeat: no-repeat; background-position: center; }"
        )
        
        # Форматування текстового віджета
        self.ui.LabelForText.setWordWrap(True)  # Увімкнути перенос слів
        self.ui.LabelForText.setStyleSheet(
            """
            QLabel {
                padding: 10px;  /* Внутрішні відступи */
                color: white;  /* Колір тексту */
                font-size: 20px;  /* Розмір тексту */
                background-color: rgba(0, 0, 0, 0.6);  /* Напівпрозорий фон */
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
        # Налаштовуємо анімацію тексту
        self.setup_rotating_text()
        
        # Таймер для автоматичної зміни тексту
        self.text_timer = QtCore.QTimer(self)
        self.text_timer.timeout.connect(self.change_text)  # Виклик зміни тексту
        self.text_timer.start(10000)  # Інтервал 10 секунд (10000 мс)
    
    def load_next_model(self):
        """Завантажує наступну модель із словника."""
        if not self.model_texture_dict:
            print("Словник моделей порожній.")
            return

        # Отримуємо список ключів (шляхів до моделей)
        model_paths = list(self.model_texture_dict.keys())

        # Отримуємо поточний шлях до моделі та текстури
        self.model_path = model_paths[self.current_model_index]
        self.texture_path = self.model_texture_dict[self.model_path]

        # Завантажуємо модель з текстурою (або без текстури)
        self.vtk_widget.load_model_with_texture(self.model_path, self.texture_path)

        # Переходимо до наступного індексу
        self.current_model_index = (self.current_model_index + 1) % len(model_paths)
        
    def closeEvent(self, event):
        """
        Зберігає шлях до останньої завантаженої моделі та текстури перед закриттям програми.
        """
        if self.model_path:
            save_to_registry("last_model_path", self.model_path)
        if self.texture_path:
            save_to_registry("last_texture_path", self.texture_path)
        print("Шляхи до моделі та текстури успішно збережено перед закриттям.")
        event.accept()
        
    def change_text(self):
        """Змінює текст на інше рандомне речення."""
        if self.rules:
            new_text = random.choice(self.rules)
            self.ui.LabelForText.setText(new_text)

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

    def load_vtk_model(self):
        self.model_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Виберіть .obj файл", "", "OBJ Files (*.obj)"
        )
        if not self.model_path:
            print("Шлях до моделі не вибрано.")
            return

        # Діалог для вибору текстури (необов’язковий)
        self.texture_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Виберіть текстуру (опціонально)", "", "Image Files (*.jpg *.png)"
        )

        # Завантаження моделі з або без текстури
        self.vtk_widget.load_model_with_texture(self.model_path, self.texture_path if self.texture_path else None)
    
    def load_last_model(self):
        self.model_path, self.texture_path = load_model_and_texture_from_registry()
        if not self.model_path or not os.path.exists(self.model_path):
            print("Шлях до моделі не знайдено або файл відсутній.")
            return
        if not self.texture_path or not os.path.exists(self.texture_path):
            print("Шлях до текстури не знайдено або файл відсутній.")
            return

        self.vtk_widget.load_model_with_texture(self.model_path, self.texture_path)

    
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
