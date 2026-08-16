import requests
import keyboard
import threading
import time

SERVER_URL = "https://promo-looter.onrender.com"
char_count = 1 # кол-во символов которые будут обрабатываться для копирование в буфер обмена и отправка на сервер. Задается на моем сервере через cmd

is_active = False # флаг чтобы включать и выключать скан символов без выключения скрипта

# Метод отправки символа на сервер
def send_char(char):
    try:
        requests.post(f"{SERVER_URL}/send", json={
            "char": char,
            "sent_at": time.time() # время отправки в секундах
        })
        print(f"Отправлен символ: {char}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# по нажатию на f1 включается и выключается скан
def on_f1():
    global is_active
    is_active = not is_active
    status = "включен" if is_active else "выключен"
    print(f"Скрипт {status}")


# heartbeat 
def ping_server():
    while True:
        try:
            requests.get(f"{SERVER_URL}/ping")
        except:
            pass
        time.sleep(480) # 8 минут дилея чтобы сервак не заснул, то есть пинг раз в 8 минут   


# Нажали на кнопку, сюда попадает событие
def on_key(event): 
    if event.name == 'f1':
        on_f1()
        return
    if not is_active: # если скрипт выключен - игнорируем нажатия
        return
    if len(event.name) == 1: # фильтруем служебные клавиши типы shift, ctrl, f1 - у них name длиннее одного символа
        send_char(event.name) # и отправляем нажатую клавишу в метод для отправки на сервер


threading.Thread(target=ping_server, daemon=True).start()
keyboard.on_press(on_key) # keyboard - слушает клавишы глобально, даже когда окно не в фокусе.
keyboard.wait() # держит скрипт живым бесконечно                   