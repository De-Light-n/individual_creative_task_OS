import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from load3d import *
from music import *
from threading import Thread, Event

def draw_text_box(text, font, bg_color, text_color, position, size):
    """Малює текстове поле з прозорим фоном у 2D."""
    text_surface = font.render(text, True, text_color)
    width, height = size

    # Створення прозорого фону для текстового поля
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    bg_surface.fill(bg_color)  # bg_color має включати альфа-канал
    bg_surface.blit(text_surface, ((width - text_surface.get_width()) // 2, (height - text_surface.get_height()) // 2))
    text_data = pygame.image.tostring(bg_surface, "RGBA", True)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1100, 650, 0, -1, 1)  # Переключення в 2D-режим
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(position[0], position[1])  # Позиція текстового поля
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_rotating_logo(text, font, bg_color, text_color, position, angle):
    """Малює обертовий текст-логотип з прозорим фоном у 2D."""
    text_surface = font.render(text, True, text_color)
    width, height = text_surface.get_size()

    # Створення прозорого фону для логотипа
    logo_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
    logo_surface.fill(bg_color)  # bg_color має включати альфа-канал
    logo_surface.blit(text_surface, (10, 10))
    text_data = pygame.image.tostring(logo_surface, "RGBA", True)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1100, 650, 0, -1, 1)  # Переключення в 2D-режим
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Центрування й обертання логотипа
    glTranslatef(position[0] + (width + 20) / 2, position[1] + (height + 20) / 2, 0)
    glRotatef(angle, 0, 0, 1)  # Обертання
    glTranslatef(-(width + 20) / 2, -(height + 20) / 2, 0)

    glRasterPos2f(0, 0)
    glDrawPixels(width + 20, height + 20, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def play_random_music_with_control(music_directory, stop_event):
    """Програє випадкову музику, поки не встановлено stop_event."""
    while not stop_event.is_set():
        play_random_music(music_directory)
        pygame.time.wait(1000)

def main():
    pygame.init()
    WEIGHT = 1100
    HEIGHT = 600
    display = (WEIGHT, HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))

    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

    font = pygame.font.Font(None, 36)
    model_scale = 0.01
    model_rotation_x = 0
    model_rotation_y = 0
    rotation_angle = 0
    last_mouse_pos = None

    obj_file = 'Models_2/Radcar.obj'
    texture_file = 'Models_2/Rad car.png'
    background_texture_file = 'background.jpg'

    vertices, texture_coords, normals, faces = load_obj(obj_file)
    texture_id = load_texture(texture_file)
    background_texture_id = load_texture(background_texture_file)

    clock = pygame.time.Clock()
    rotation_speed_x = 0.05
    rotation_speed_y = 0.3
    rotation_damping = 0.95

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    model_scale += 0.002
                elif event.button == 5:
                    model_scale -= 0.002
                    model_scale = max(model_scale, 0.002)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                last_mouse_pos = pygame.mouse.get_pos()

            if event.type == MOUSEBUTTONUP and event.button == 1:
                last_mouse_pos = None

            if event.type == MOUSEMOTION and last_mouse_pos:
                current_mouse_pos = pygame.mouse.get_pos()
                dx = current_mouse_pos[0] - last_mouse_pos[0]
                dy = current_mouse_pos[1] - last_mouse_pos[1]
                rotation_speed_x = dy * 0.5
                rotation_speed_y = dx * 0.5
                last_mouse_pos = current_mouse_pos

        model_rotation_y += rotation_speed_y
        model_rotation_x += rotation_speed_x
        rotation_speed_x *= rotation_damping
        rotation_speed_y *= rotation_damping
        rotation_angle += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Draw background
        draw_background(background_texture_id)

        # Draw model
        glPushMatrix()
        glScalef(model_scale, model_scale, model_scale)
        glRotatef(model_rotation_x, 1, 0, 0)
        glRotatef(model_rotation_y, 0, 1, 0)
        draw_model(vertices, texture_coords, normals, faces)
        glPopMatrix()

        # Draw UI
        draw_text_box(
            "Текст перед камерою",
            font,
            (0, 0, 0, 20),  # Прозорий має бути
            (255, 255, 0),
            (WEIGHT / 2 - WEIGHT / 7, HEIGHT - 90),
            (WEIGHT / 3, HEIGHT / 7)
        )

        draw_rotating_logo(
            "Nazar",
            font,
            (0, 0, 0, 20), 
            (255, 255, 255),
            (50, HEIGHT - 150),
            rotation_angle
        )

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    AUTHORIZED_HOSTNAME = "DESKTOP-PLP53PH"

    if socket.gethostname() != AUTHORIZED_HOSTNAME:
        print("Ця програма може запускатися тільки на ноутбуці Назара!")
        exit()

    print("Програма успішно запущена!")
    
    stop_event = Event()
    
    main_thread = Thread(target=main, daemon=True)
    music_thread = Thread(target=play_random_music_with_control, args=("Music", stop_event), daemon=True)
    
    main_thread.start()
    music_thread.start()
    
    try:
        main_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        music_thread.join()
