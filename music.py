
import os
import keyboard
import random
import pygame


# Ініціалізація Pygame Mixer
pygame.mixer.init()

# Шлях до папки з музикою
MUSIC_FOLDER = "Music"

# Функція для отримання випадкової пісні
def get_random_song(folder):
    songs = [f for f in os.listdir(folder) if f.endswith('.mp3')]
    return os.path.join(folder, random.choice(songs)) if songs else None


def play_random_music(folder):
    is_paused = False  # Стан музики (чи вона на паузі)

    while True:
        if not is_paused:  # Завантажуємо та граємо наступну пісню
            song = get_random_song(folder)
            if not song:
                print("Немає mp3 файлів у папці.")
                break

            print(f"Зараз грає: {os.path.basename(song)}")
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()

        while True:  # Цикл для керування поточною піснею
            if keyboard.is_pressed("S"):
                if is_paused:
                    print("Музику відновлено.")
                    pygame.mixer.music.unpause()
                else:
                    print("Музику призупинено.")
                    pygame.mixer.music.pause()

                is_paused = not is_paused  # Перемикаємо стан паузи
                keyboard.wait("S")  # Чекаємо, поки пробіл відпустять
                break  # Вихід із внутрішнього циклу, щоб оновити стан
            elif not pygame.mixer.music.get_busy():
                break  # Якщо пісня закінчилася, вийти з внутрішнього циклу

            pygame.time.Clock().tick(10)  # Перевірка кожні 100 мс






if __name__=="__main__":
    try:
        play_random_music(MUSIC_FOLDER)
    except KeyboardInterrupt:
        print("\nВідтворення зупинено.")
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
