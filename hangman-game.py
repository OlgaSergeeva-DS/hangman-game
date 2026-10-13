"""
Игра «Виселица» (Hangman) с визуализацией в стиле «Поля чудес».

Неотгаданные буквы — тёмно-синие прямоугольники.
Угаданные буквы — белые прямоугольники с чёрной буквой.
"""

import random
import sys
from pathlib import Path
from typing import Optional

# ========== ЦВЕТА (colorama) ==========
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # автоматически сбрасывать цвета после каждого print
except ImportError:
    print("Ошибка: библиотека colorama не установлена.")
    print("Установите её командой: pip install colorama")
    sys.exit(1)


# ========== КОНСТАНТЫ ==========
WORDS_FILE = Path("words.txt")
MAX_ATTEMPTS = 6

# Цветовые схемы
HIDDEN_BACK = Back.BLUE                    # тёмно-синий фон (скрытый квадрат)
HIDDEN_CHAR = "   "                        # три пробела для формы поля при закрытой букве 

GUESSED_BACK = Back.WHITE + Fore.BLACK     # белый фон, чёрный текст (открытый квадрат)

RESET_STYLE = Style.RESET_ALL              # сброс стиля, указываем явно для читаемости кода


# ========== 1. РАБОТА С ФАЙЛОМ ==========
def load_words_from_file(file_path: Path) -> list[str]:
    """
    Загружает список слов из текстового файла.
    
    Args:
        file_path: путь к файлу со словами (по одному на строку)
    
    Returns:
        Список слов в нижнем регистре.
    
    Raises:
        FileNotFoundError: если файл не найден
        ValueError: если файл пуст
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл со словами не найден: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]
    
    if not words:
        raise ValueError(f"Файл {file_path} не содержит слов")
    
    return words


# ========== 2. ЛОГИКА ИГРЫ ==========
def pick_random_word(words: list[str]) -> str:
    """Выбирает случайное слово из списка."""
    return random.choice(words)


def render_letter_box(letter: Optional[str]) -> str:
    """
    Рисует один «прямоугольник» для буквы.
    
    Если буква не угадана (None) — синий прямоугольник.
    Если буква угадана — белый прямоугольник с чёрной буквой.
    
    Args:
        letter: буква (str) или None, если ещё не угадана
    
    Returns:
        Строка с ANSI-цветами для отображения одной буквы.
    """
    if letter is None:
        # Не угадана: синий фон, внутри пробел
        return f"{HIDDEN_BACK}{HIDDEN_CHAR}{RESET_STYLE}"
    else:
        # Угадана: белый фон, чёрная буква
        return f"{GUESSED_BACK} {letter.upper()} {RESET_STYLE}"


def display_word(secret_word: str, guessed_letters: set[str]) -> str:
    """
    Формирует строку с прямоугольниками для каждой буквы.
    
    Args:
        secret_word: загаданное слово
        guessed_letters: множество угаданных букв
    
    Returns:
        Строка с прямоугольниками, разделёнными пробелами.
    """
    boxes = []
    for letter in secret_word:
        if letter in guessed_letters:
            boxes.append(render_letter_box(letter))
        else:
            boxes.append(render_letter_box(None))
    return " ".join(boxes)


def get_player_letter(already_guessed: set[str]) -> Optional[str]:
    """
    Запрашивает у игрока одну букву и валидирует ввод.
    
    Args:
        already_guessed: множество уже угаданных букв
    
    Returns:
        Буква (str) или None, если игрок ввёл команду выхода.
    """
    while True:
        user_input = input("Введите букву (или 'exit' для выхода): ").strip().lower()
        
        if user_input == "exit":
            return None
        
        if len(user_input) != 1:
            print("Ошибка: введите ровно одну букву.")
            continue
        
        if not user_input.isalpha():
            print("Ошибка: введите букву (не цифру и не символ).")
            continue
        
        # Проверка на русские буквы (опционально)
        if user_input in already_guessed:
            print(f"Буква '{user_input}' уже была. Попробуйте другую.")
            continue
        
        return user_input


def play_hangman(words: list[str]) -> bool:
    """
    Проводит одну игру в «Виселицу».
    
    Returns:
        True, если игрок выиграл, False — если проиграл.
    """
    secret_word = pick_random_word(words)
    guessed_letters: set[str] = set()
    attempts_left = MAX_ATTEMPTS
    
    print("\n" + "=" * 60)
    print(f"Я загадал слово из {len(secret_word)} букв.")
    print(f"У вас {attempts_left} попыток.")
    print("=" * 60)
    
    while attempts_left > 0:
        # Показываем слово в виде прямоугольников
        print(f"\nСлово: {display_word(secret_word, guessed_letters)}")
        print(f"Осталось попыток: {attempts_left}")
        
        # Проверка победы
        if all(letter in guessed_letters for letter in secret_word):
            print(f"\nПобеда! Вы угадали слово: '{secret_word.upper()}'")
            return True
        
        # Запрос буквы
        letter = get_player_letter(guessed_letters)
        
        if letter is None:
            print(f"\nВы вышли из игры. Загаданное слово: '{secret_word.upper()}'")
            return False
        
        guessed_letters.add(letter)
        
        if letter in secret_word:
            print(f"Буква '{letter.upper()}' есть в слове!")
        else:
            attempts_left -= 1
            print(f"Буквы '{letter.upper()}' нет в слове. Осталось попыток: {attempts_left}")
    
    print(f"\nВы проиграли! Загаданное слово было: '{secret_word.upper()}'")
    return False


# ========== 3. ИНТЕРФЕЙС И ГЛАВНЫЙ ЦИКЛ ==========
def ask_replay() -> bool:
    """Спрашивает игрока, хочет ли он сыграть ещё раз."""
    while True:
        answer = input("\nСыграть ещё раз? (да/нет): ").strip().lower()
        if answer in ("да", "д", "yes", "y"):
            return True
        if answer in ("нет", "н", "no", "n"):
            return False
        print("Пожалуйста, ответьте 'да' или 'нет'.")


def main() -> None:
    """Точка входа в программу."""
    print("=" * 60)
    print("ДОБРО ПОЖАЛОВАТЬ В ИГРУ «ВИСЕЛИЦА»!")
    print("=" * 60)
    
    try:
        words = load_words_from_file(WORDS_FILE)
        print(f"Загружено слов: {len(words)}")
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Создайте файл words.txt со словами (по одному на строку).")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    
    while True:
        play_hangman(words)
        if not ask_replay():
            print("\nСпасибо за игру! До встречи!")
            break


# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем (Ctrl+C).")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        sys.exit(1)
