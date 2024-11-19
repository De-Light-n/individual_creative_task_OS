import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def load_obj(filename):
    vertices = []
    texture_coords = []
    normals = []  # Додамо список для нормалей
    faces = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                if parts[0] == 'v':
                    vertices.append(list(map(float, parts[1:])))
                elif parts[0] == 'vt':
                    texture_coords.append(list(map(float, parts[1:])))
                elif parts[0] == 'vn':
                    normals.append(list(map(float, parts[1:])))  # Обробка нормалей
                elif parts[0] == 'f':
                    face = []
                    tex_coords = []
                    norm_indices = []  # Список для індексів нормалей
                    for part in parts[1:]:
                        vals = part.split('/')
                        face.append(int(vals[0]) - 1)
                        if len(vals) > 1 and vals[1]:
                            tex_coords.append(int(vals[1]) - 1)
                        if len(vals) > 2 and vals[2]:
                            norm_indices.append(int(vals[2]) - 1)
                    faces.append((face, tex_coords, norm_indices))  # Збережемо індекси нормалей

    return np.array(vertices, dtype='float32'), np.array(texture_coords, dtype='float32'), np.array(normals, dtype='float32'), faces


def load_texture(filename):
    texture_surface = pygame.image.load(filename)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

def draw_model(vertices, texture_coords, normals, faces):
    glBindTexture(GL_TEXTURE_2D, 1)
    glBegin(GL_TRIANGLES)
    for face, tex_coords, norm_indices in faces:
        for i in range(3):
            if norm_indices:  # Якщо є нормалі, встановимо їх
                glNormal3fv(normals[norm_indices[i]])
            if tex_coords:
                glTexCoord2fv(texture_coords[tex_coords[i]])
            glVertex3fv(vertices[face[i]])
    glEnd()
    
# def draw_model(vertices, texture_coords, normals, faces):
#     glBindTexture(GL_TEXTURE_2D, 1)
#     glBegin(GL_TRIANGLES)
#     for face, tex_coords, norm_indices in faces:
#         for i in range(3):
#             if norm_indices:  # Якщо є нормалі, встановимо їх
#                 glNormal3fv(normals[norm_indices[i]])
#             if tex_coords:
#                 # Інвертуємо Y-координату текстури (якщо текстура перевернута)
#                 u, v = texture_coords[tex_coords[i]]
#                 glTexCoord2f(u, 1 - v)
#             glVertex3fv(vertices[face[i]])
#     glEnd()
    
def draw_background(texture_id):
    glDisable(GL_DEPTH_TEST)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-5, -5, -0.9)
    glTexCoord2f(1, 0)
    glVertex3f(5, -5, -0.9)
    glTexCoord2f(1, 1)
    glVertex3f(5, 5, -0.9)
    glTexCoord2f(0, 1)
    glVertex3f(-5, 5, -0.9)
    glEnd()
    glEnable(GL_DEPTH_TEST)