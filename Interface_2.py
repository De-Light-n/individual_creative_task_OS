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
        for mesh in self.model.mesh_list:
            for material in mesh.materials:
                # Завантаження текстури, якщо вона є
                if material.texture:
                    self.bind_texture(material.texture.image_name)

                gl.glBegin(gl.GL_TRIANGLES)
                for i in range(0, len(material.vertices), 3):
                    # Текстурні координати
                    if material.texture and i + 2 < len(material.vertices):
                        tex_coords = material.vertices[i:i+2]
                        gl.glTexCoord2f(*tex_coords)

                    # Нормалі (якщо доступні)
                    if len(material.vertices) > i + 5:
                        normal = material.vertices[i+3:i+6]
                        gl.glNormal3f(*normal)

                    # Вершини
                    vertex = material.vertices[i:i+3]
                    gl.glVertex3f(*vertex)
                gl.glEnd()


def bind_texture(self, texture_path):
    from PIL import Image
    import os

    # Повний шлях до текстури
    model_dir = os.path.dirname(self.model.file_name)
    full_texture_path = os.path.join(model_dir, texture_path)

    try:
        image = Image.open(full_texture_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()

        # Генерація текстури
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.width, image.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)

        # Параметри текстури
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glEnable(gl.GL_TEXTURE_2D)
    except Exception as e:
        print(f"Помилка завантаження текстури: {e}")
