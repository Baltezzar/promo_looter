# Обработчик на моей стороне

import requests
import pyperclip
import keyboard
import threading
import time
import win32con
import win32api
from collections import deque # deque - двусторонняя очередь и быстрее чем list

SERVER_PYTHON = "https://Baltezar.eu.pythonanywhere.com"

SERVER_RENDER = "https://promo-looter.onrender.com"

SERVER_URL = SERVER_PYTHON # бесплатный Render сервер

char_count = 1 # кол-во символом при разовом выводе, сейчас 1 символ 

char_queue = deque() # создаем объект очереди где каждый объект внутри знает своего соседа 
                     # очередь deque отличается от обычного list списка тем, что list при pop(0) при удалении сдвигает весь список влево что очень долго, а этот объектная очередь сдвигает указатель а не физический объект что быстрее в разы

is_active = False # флаг активности программы

is_pasting = False # флаг для замка чтобы выполнялось сначала копирование а потом вставка


# Функция получения символов от основного сервера
def fetch_chars():
    global sent_at
    try:
        response = requests.get(f"{SERVER_URL}/get")
        data = response.json()
        chars = data["chars"]
        if len(chars) > 0:
            for item in chars: # перебираем все символы
                char_queue.append({ # заполняем словарь очереди символов
                    "char": item["char"] # непосредственно сам символ
                })
            received = [item["char"] for item in chars] # создаем список item["char"] перебирая каждый item в chars
            print(f"Получено: {', '.join(received)} | В очереди: {len(char_queue)}") # и через join() склеиваем через запятую с пробелом каждый символ который пришел    
    except Exception as e:
        print(f"Ошибка получения: {e}")      

def on_ctrl_v():
    global is_pasting

    if not is_active or is_pasting or not char_queue: # если прога выключена (флаг is_active == False), нет очереди (список пустой char_queue = [] == False) и замок на вставку False (is_pasting == False) то не выполняем тело функции
        return

    is_pasting = True

    item = char_queue.popleft()
    result = item["char"]

    print(f"Вставляю: {result} | Осталось: {len(char_queue)}")

    threading.Thread(target=_do_paste, args=(result,), daemon=True).start() # создаем поток (хотя можно и без него) чтобы другие клавишы если нажать одновременно не зависали
 

def _do_paste(result):
    global is_pasting
    try:
        pyperclip.copy(result)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
    finally:
        is_pasting = False


# Нажимаем f2 и включаем/выключаем скрипт
def on_f2():
    global is_active, is_pasting
    is_active = not is_active
    is_pasting = False # 
    status = "включен" if is_active else "выключен"
    print(f"Скрипт {status}")
    if status == "включен":
        print("Ожидаю символы...")

    
    keyboard.remove_hotkey("ctrl+v") # выключаем скрипт и удаляем кнопки чтобы переназначить супрессор заново сгенерировав

    if is_active: # если прога активная, то супрессор включен
        keyboard.add_hotkey("ctrl+v", on_ctrl_v, suppress=True)
    else: # если прога выключена, то супресор выключен и ctrl+v работает штатно
        keyboard.add_hotkey("ctrl+v", on_ctrl_v, suppress=False)    

# Функция нажатия на end - очистка буфера обмена и буфер сервера
def on_scrolllock():
    char_queue.clear()
    pyperclip.copy("")
    try:
       requests.post(f"{SERVER_URL}/clear")
       print("Буфер очищен (локально + сервер)")
    except Exception as e:
       print(f"Ошибка очистки сервера: {e}")
       

# Функция-опросник, раз в секунду запрашивает данные вызывая метод fentch_chars()
def start_polling():
    print("Прога запущена но скрипт не работает. Нажми на F2...")
    while True:
        if is_active:
            fetch_chars()
        time.sleep(0.1)   


threading.Thread(target=start_polling, daemon=True).start()
keyboard.add_hotkey('scroll lock', on_scrolllock) # supress=True поставил чтобы при нажатии не открывался браузер (там каккая-то вкладка вечно открывалась)
keyboard.add_hotkey('f2', on_f2)

keyboard.add_hotkey(
    "ctrl+v",
    on_ctrl_v,
    suppress=False # supress=True - это игнорирование нажатия на ctrl + v. То есть при нажатии сработает эта конструкция и вызоветься on_ctrl_v но физически ничего не вставиться
)                  # по умолчанию супрессор выключен так как программа при запуске первом выключена

keyboard.wait()               