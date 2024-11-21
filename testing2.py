import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController
from PyQt5.Qt3DCore import QEntity
from PyQt5.Qt3DExtras import QPhongMaterial
from PyQt5.Qt3DRender import QMesh
from PyQt5.QtCore import QUrl, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D-Viewer: Правила дорожнього руху")

        # Основний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Створюємо 3D-вікно
        self.view3d = Qt3DWindow()
        self.container = self.create_3d_scene()

        # Створюємо текстовий лейбл
        label = QLabel("""
        Правила дорожнього руху для дітей:
        1. Переходь дорогу тільки на зелене світло.
        2. Завжди використовуй пішохідний перехід.
        3. Не грайся біля дороги.
        4. Дивись ліворуч і праворуч перед переходом.
        """)
        label.setStyleSheet("font-size: 16px; padding: 10px;")

        # Кнопка для завантаження файлу
        load_button = QPushButton("Завантажити модель (.obj)")
        load_button.clicked.connect(self.load_obj_file)

        # Розташування елементів у вікні
        right_layout = QVBoxLayout()
        right_layout.addWidget(label)
        right_layout.addWidget(load_button)

        layout = QHBoxLayout()
        layout.addWidget(self.container, 2)  # 3D-сцена
        layout.addLayout(right_layout, 1)  # Текст і кнопка

        central_widget.setLayout(layout)

    def create_3d_scene(self):
        # Контейнер для 3D-сцени
        container = QWidget.createWindowContainer(self.view3d)

        # Створюємо 3D-сцену
        self.scene_root = QEntity()

        # Камера
        camera = self.view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000)
        camera.setPosition(Qt.vector3D(0, 0, 10))
        camera.setViewCenter(Qt.vector3D(0, 0, 0))

        # Камера-контролер
        cam_controller = QOrbitCameraController(self.scene_root)
        cam_controller.setCamera(camera)

        # Прив'язуємо сцену до вікна
        self.view3d.setRootEntity(self.scene_root)
        return container

    def load_obj_file(self):
        # Вибір файлу через діалогове вікно
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Завантажити 3D-модель", "", "OBJ Files (*.obj);;All Files (*)", options=options)
        if file_name:
            # Створюємо QMesh для завантаження об'єкта
            obj_mesh = QMesh()
            obj_mesh.setSource(QUrl.fromLocalFile(file_name))

            # Створюємо сутність для об'єкта
            obj_entity = QEntity(self.scene_root)
            obj_entity.addComponent(obj_mesh)

            # Додаємо матеріал
            material = QPhongMaterial()
            material.setDiffuse(Qt.blue)
            obj_entity.addComponent(material)

            print(f"Файл {file_name} завантажено успішно!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
