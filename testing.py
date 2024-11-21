import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from load3d import *
from music import *
from threading import Thread, Event

WEIGHT = 1100
HEIGHT = 600

def draw_text_box(text, font, bg_color, text_color, position, size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(bg_color)
    text_surface = font.render(text, True, text_color)
    surface.blit(
        text_surface, 
        ((size[0] - text_surface.get_width()) // 2, 
         (size[1] - text_surface.get_height()) // 2)
    )
    texture_data = pygame.image.tostring(surface, "RGBA", True)
    glRasterPos2f(position[0] / WEIGHT * 2 - 1, position[1] / HEIGHT * -2 + 1)
    glDrawPixels(size[0], size[1], GL_RGBA, GL_UNSIGNED_BYTE, texture_data)


def draw_rotating_logo(text, font, bg_color, text_color, position, angle):
    surface = pygame.Surface((150, 150), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Прозорий фон
    rotated_surface = pygame.Surface((150, 150), pygame.SRCALPHA)

    text_surface = font.render(text, True, text_color)
    rotated_surface.blit(text_surface, ((150 - text_surface.get_width()) // 2, (150 - text_surface.get_height()) // 2))
    rotated_surface = pygame.transform.rotate(rotated_surface, angle)
    texture_data = pygame.image.tostring(rotated_surface, "RGBA", True)
    glRasterPos2f(position[0] / WEIGHT * 2 - 1, position[1] / HEIGHT * -2 + 1)
    glDrawPixels(rotated_surface.get_width(), rotated_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, texture_data)



def play_random_music_with_control(music_directory, stop_event):
    """Програє випадкову музику, поки не встановлено stop_event."""
    while not stop_event.is_set():
        play_random_music(music_directory)
        pygame.time.wait(1000)

def main():
    pygame.init()
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
    background_texture_file = 'background3.jpg'

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
            (100, 100, 100, 20),  # Прозорий має бути
            (255, 255, 0),
            (WEIGHT / 2 - WEIGHT / 7, HEIGHT - 90),
            (WEIGHT / 3, HEIGHT / 7)
        )

        draw_rotating_logo(
            "Nazar",
            font,
            (100, 100, 100, 20), 
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
