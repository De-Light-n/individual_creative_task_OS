from getRules import getRules
import socket
import os
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

# Основна функція
def play_random_music(folder):
    while True:
        song = get_random_song(folder)
        if not song:
            print("Немає mp3 файлів у папці.")
            break
        
        print(f"Зараз грає: {os.path.basename(song)}")
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        
        # Чекаємо завершення пісні
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Перевірка кожні 100 мс



if __name__=="__main__":
    rules = getRules()
    print("\n\n\n\n\n")
    print(rules)
    try:
        play_random_music(MUSIC_FOLDER)
    except KeyboardInterrupt:
        print("\nВідтворення зупинено.")
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
