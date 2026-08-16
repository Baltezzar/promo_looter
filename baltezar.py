# Обработчик на моей стороне

import requests
import pyperclip
import keyboard
import threading
import time

SERVER_URL = "https://мой-адрес.onrender.com"
char_count = 1
buffer = [] # накапливаем символы пока не наберём нужное кол-во
# Флаги
is_pasted = False # флаг чтобы один раз вставлялся ctrl + v при спаме 

# Функция получения символов от основного сервера
def fetch_chars():
    global buffer, is_pasted
    try:
        response = requests.get(f"{SERVER_URL}/get")
        data = response.json()
        chars = data["chars"]
        if len(chars) > 0:
            buffer.extend(chars) # extend в отличии от append добавляет не один элемент, а сразу список 
            if len(buffer) >= char_count:
                result = "".join(buffer[:char_count]) # берём только нужное кол-во символов
                                                      # символ ":" - означает от начала и до char_count, а join() склеивает символы типа 'a', 'b' в одну строку - 'ab' потому что "" стоит пере join, "".join()... если поставить так: "-".join(['a', 'b']) -> a-b 
                buffer.clear()
                pyperclip.copy(result) # кладем в буфер обмена
                is_pasted = False # сбрасываем флаг - новый символ пришёл, можно вставлять
                print(f"В буфере: {result}")
    except Exception as e:
        print(f"Ошибка получения: {e}")      


def on_ctrl_v():
    global is_pasted
    if is_pasted:
        return False # Блокируем повторное нажатие
    if pyperclip.paste() != "":
        is_pasted = True


# Функция нажатия на f1 - очистка буфера обмена
def on_f1():
    global buffer, is_pasted
    buffer.clear()
    is_pasted = False
    pyperclip.copy("") # Очищаем буфер обмена копируя пустоту

# Функция-опросник, раз в секунду запрашивает данные вызывая метод fentch_chars()
def start_polling():
    print("Ожидаю символы...")
    while True:
        fetch_chars()
        time.sleep(1)   

threading.Thread(target=start_polling, daemon=True).start()
keyboard.add_hotkey('f1', on_f1)
keyboard.add_hotkey('ctrl+v', on_ctrl_v, suppress=True) # suppress=True - перехватываем ctrl+v и решаем сами пускать его или нет  
keyboard.wait()               