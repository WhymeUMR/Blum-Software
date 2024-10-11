import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import random
import json
from pynput.mouse import Button, Controller
import pygetwindow as gw
from tkinter import simpledialog
import threading
import keyboard
from tkinter import PhotoImage
from tkinter import font  # Импорт font

mouse = Controller()
time.sleep(0.5)

def click(xs, ys):
    mouse.position = (xs, ys + random.randint(1, 3))
    mouse.press(Button.left)
    mouse.release(Button.left)


def choose_window_gui():
    root = tk.Tk()
    root.withdraw()

    windows = gw.getAllTitles()
    if not windows:
        return None

    choice = simpledialog.askstring("Выбор окна Telegram", "Введите номер окна:\n" + "\n".join(
        f"{i}: {window}" for i, window in enumerate(windows)))

    if choice is None or not choice.isdigit():
        return None

    choice = int(choice)
    if 0 <= choice < len(windows):
        return windows[choice]
    else:
        return None


def check_white_color(scrnb, window_rectb):
    widthb, heightb = scrnb.size
    for xb in range(0, widthb, 20):
        yb = heightb - heightb / 7
        rb, gb, bb = scrnb.getpixel((xb, yb))
        if (rb, gb, bb) == (255, 255, 255):
            screen_xb = window_rectb[0] + xb
            screen_yb = window_rectb[1] + yb
            click(screen_xb, screen_yb)
            write_to_log('Начинаю новую игру')
            time.sleep(0.001)
            return True
    return False


def check_blue_color(scrnq, window_rectq):
    widthq, heightq = scrnq.size
    for xq in range(0, widthq, 5):
        for yq in range(200, heightq, 5):
            rq, gq, bq = scrnq.getpixel((xq, yq))

            # Проверка цвета пикселя на соответствие заданному цвету (RGB: 161, 238, 249)
            if (rq in range(155, 165)) and (gq in range(235, 245)) and (bq in range(245, 255)):
                screen_xq = window_rectq[0] + xq
                screen_yq = window_rectq[1] + yq
                click(screen_xq, screen_yq)
                return True
    return False


def run_bot():
    global paused, telegram_window, last_check_time, last_pause_time, speed, speed_variation
    while True:
        if not paused:
            window_rect = (
                telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
            )

            if telegram_window != []:
                try:
                    telegram_window.activate()
                except:
                    telegram_window.minimize()
                    telegram_window.restore()

            scrn = pyautogui.screenshot(region=(window_rect[0], window_rect[1], window_rect[2], window_rect[3]))

            width, height = scrn.size
            pixel_found = False

            for x in range(0, width, 20):
                for y in range(130, height, 20):
                    r, g, b = scrn.getpixel((x, y))
                    if (b in range(0, 125)) and (r in range(102, 220)) and (g in range(200, 255)):
                        screen_x = window_rect[0] + x + 3
                        screen_y = window_rect[1] + y + 5
                        click(screen_x, screen_y)
                        time.sleep(0.002)
                        pixel_found = True
                        break

            current_time = time.time()
            if current_time - last_check_time >= 10:
                if check_white_color(scrn, window_rect):
                    last_check_time = current_time

            if current_time - last_pause_time >= speed:
                time.sleep(random.uniform(speed - speed_variation, speed + speed_variation))
                last_pause_time = current_time

            # Проверка на кристаллы
            check_blue_color(scrn, window_rect)

        time.sleep(0.1)


def start():
    global start_pressed, telegram_window, paused, last_pause_time, last_check_time
    # Disable Start button and enable Stop button
    start_button["state"] = "disabled"
    stop_button["state"] = "normal"

    # Check if Start button is now disabled (to handle F4)
    if start_button["state"] == "disabled":
        write_to_log("Программа уже запущена\n")
        start_pressed = True
        return  # Выход из функции, если она уже запущена

    # Find Telegram window
    window_name = "TelegramDesktop"
    check = gw.getWindowsWithTitle(window_name)
    if not check:
        write_to_log(f"\nОкно {window_name} не найдено!\nПожалуйста, выберите другое окно.")
        window_name = choose_window_gui()

    if not window_name or not gw.getWindowsWithTitle(window_name):
        write_to_log("\nНе удалось найти указанное окно!\nЗапустите Telegram, после чего перезапустите бота!")
    else:
        telegram_window = gw.getWindowsWithTitle(window_name)[0]
        paused = False  # Start the program unpaused
        last_check_time = time.time()
        last_pause_time = time.time()
        write_to_log("Программа запущена\n")
        write_to_log("Для паузы нажмите 'Stop' \n")

        # Start the bot
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True  # Make the bot thread a daemon (exit when the main thread exits)
        bot_thread.start()


def stop():
    global paused
    # Enable Start button and disable Stop button
    start_button["state"] = "normal"
    stop_button["state"] = "disabled"

    paused = True  # Set paused flag to True
    write_to_log("Программа приостановлена\n")
    write_to_log("Для возобновления нажмите 'Start'\n")

    # Reset flags
    start_pressed = False
    stop_pressed = False


def open_config_window():
    global config_window, speed_entry, speed_variation_entry
    config_window = tk.Toplevel(window)
    config_window.title("Настройки")
    config_window.resizable(False, False)

    speed_label = tk.Label(config_window, text="Скорость (сек):")
    speed_label.pack()

    global speed_entry
    speed_entry = tk.Entry(config_window)
    speed_entry.pack()

    speed_variation_label = tk.Label(config_window, text="Вариация скорости (сек):")
    speed_variation_label.pack()

    global speed_variation_entry
    speed_variation_entry = tk.Entry(config_window)
    speed_variation_entry.pack()

    save_button = ttk.Button(config_window, text="Сохранить", command=save_config)
    save_button.pack(pady=10)

    cancel_button = ttk.Button(config_window, text="Отмена", command=config_window.destroy)
    cancel_button.pack()

    # Загрузить настройки из файла при открытии окна
    load_config()


def save_config():
    global speed_entry, speed, speed_variation_entry, speed_variation
    speed = float(speed_entry.get())
    speed_variation = float(speed_variation_entry.get())

    # Сохранить настройки в файл
    with open("config.json", "w") as f:
        json.dump({"speed": speed, "speed_variation": speed_variation}, f)

    write_to_log("Настройки сохранены\n")
    config_window.destroy()


def load_config():
    global speed_entry, speed, speed_variation_entry, speed_variation
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            speed = config["speed"]
            speed_variation = config["speed_variation"]

            # Access config_window conditionally
            if config_window is not None:
                # Create speed_entry if it doesn't exist
                if speed_entry is None:
                    speed_entry = tk.Entry(config_window)
                    speed_entry.pack()

                speed_entry.insert(0, speed)

                if speed_variation_entry is None:
                    speed_variation_entry = tk.Entry(config_window)
                    speed_variation_entry.pack()

                speed_variation_entry.insert(0, speed_variation)
    except FileNotFoundError:
        write_to_log("Файл настроек не найден\n")
        # Обработка отсутствия файла
    except Exception as e:
        write_to_log("Ошибка при загрузке конфигурации:", e)
        # Обработка других ошибок


def open_help_window():
    help_window = tk.Toplevel(window)
    help_window.title("Помощь")
    help_window.resizable(False, False)

    help_text = tk.Label(help_window, text="""
Быстрая скорость:
speed = 0.5 (проверка каждые 0.5 секунды)
speed_variation = 0.1 (вариация от 0.4 до 0.6 секунд)

Средняя скорость:
speed = 1.0 (проверка каждые 1 секунду)
speed_variation = 0.2 (вариация от 0.8 до 1.2 секунд)

Медленная скорость:
speed = 2.0 (проверка каждые 2 секунды)
speed_variation = 0.4 (вариация от 1.6 до 2.4 секунд)
    """)
    help_text.pack(pady=10)

    ok_button = ttk.Button(help_window, text="OK", command=help_window.destroy)
    ok_button.pack(pady=10)


# Global variables
config_window = None
speed_entry = None
speed_variation_entry = None
speed = 0.5  # Default speed
speed_variation = 0.2  # Default speed variation

# Create Tkinter window
window = tk.Tk()
window.title("Blum Clicker by Why_me")
window.resizable(False, False)
icon = PhotoImage(file="Blum.png")
window.iconphoto(False, icon)

# Get the screen width
screen_width = window.winfo_screenwidth()

# Создаем кастомный шрифт
custom_font = font.Font(family="Fixedsys", size=34, weight="bold")

# Создаем метку с текстом "Blum Software" с кастомным шрифтом
name_label_custom = tk.Label(window, text="BLUM SOFTWARE", font=custom_font, fg="#222222", bg="#FFFFFF")
name_label_custom.pack(side="top", fill="x") # Растягиваем по всей ширине

# Create a frame for the left side (Name and Buttons)
left_frame = tk.Frame(window, width=screen_width // 2)  # Set width to half the screen width
left_frame.pack(side="left", fill="both", expand=True)

# Create a frame for the right side (Log)
right_frame = tk.Frame(window, width=screen_width // 8)  # Set width to an eighth of the screen width
right_frame.pack(side="right", fill="both", expand=True)

# Left side elements
name_label = tk.Label(left_frame, text="Functions")
name_label.pack(side="top", pady=10)

start_button = ttk.Button(left_frame, text="Start (F4)", command=start)
start_button.pack(side="top", pady=10)

stop_button = ttk.Button(left_frame, text="Stop (F2)", command=stop, state="disabled")
stop_button.pack(side="top", pady=10)

# Add Config button
config_button = ttk.Button(left_frame, text="Config", command=open_config_window)
config_button.pack(side="top", pady=10)

# Add Help button
help_button = ttk.Button(left_frame, text="Help", command=open_help_window)
help_button.pack(side="top", pady=10)

# Right side elements (Log)
log_label = tk.Label(right_frame, text="Log")
log_label.pack(side="top", pady=10)

# Create a scrollable text widget for the log
log_text = tk.Text(right_frame, height=10, width=screen_width // 50, wrap="word", state="disabled")
log_text.pack(fill="both", expand=True)

# Create a scrollbar and link it to the Text widget
scrollbar = tk.Scrollbar(right_frame, command=log_text.yview)
scrollbar.pack(side="right", fill="y")
log_text.config(yscrollcommand=scrollbar.set)


# Function to write to the Log
def write_to_log(message):
    log_text.config(state="normal")
    log_text.insert(tk.END, message + "\n")
    log_text.config(state="disabled")
    # Ensure the scrollbar is updated after writing
    log_text.see(tk.END)


# Load default config (if no config file exists)
load_config()

# Start listening for key presses
keyboard.add_hotkey('f4', start)
keyboard.add_hotkey('f2', stop)
keyboard.add_hotkey('esc', lambda: window.destroy())

window.mainloop()

# Keep keyboard listener running in the background
keyboard.wait()
