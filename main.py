import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#Токін
bot = telebot.TeleBot('7684408093:AAEg_aOWNdJmHVGKFeNG2pF7oCqeFkDitKo')

#клавіши для гри
keyboard = InlineKeyboardMarkup()
keyboard.row(InlineKeyboardButton('←', callback_data='left'),
             InlineKeyboardButton('↑', callback_data='up'),
             InlineKeyboardButton('↓', callback_data='down'),
             InlineKeyboardButton('→', callback_data='right'))

#Пустий масив в який згодом буде передано матрицю
maps = {}

#побудова карти
def get_map_str(matrix, player):
    map_str = ""
    for y in range(len(matrix)):
        for x in range(len(matrix[0])):
            if matrix[y][x] == 1:
                map_str += "⬛"  # Стіна
            elif (x, y) == player:
                map_str += "🔴"  # Гравець
            else:
                map_str += "⬜"  # Прохід
        map_str += "\n"
    return map_str

#команда старт
@bot.message_handler(commands=['start'])
def output_start(message):
    with open('technical_textes/text_description.txt', 'r') as file1:
        read_content = file1.read()
    bot.send_message(message.from_user.id, read_content)

#команда передачі матриці
@bot.message_handler(commands=['take_matrix'])
def take_matrix(message):
    bot.send_message(message.from_user.id, "Введіть матрицю схожу на ту як у прикладі")
    bot.register_next_step_handler(message, process_matrix)

#переробка данних у підходящі для гри
def process_matrix(message):
    try:
        # Перетворюємо текстове повідомлення на матрицю
        matrix = eval(message.text)
        if not all(isinstance(row, list) for row in matrix) or not all(isinstance(el, int) for row in matrix for el in row):
            raise ValueError

        # Зберігаємо матрицю для користувача
        user_data = {
            'map': matrix,
            'x': 0,
            'y': 0
        }
        maps[message.chat.id] = user_data

        # Відправляємо карту з початковим положенням гравця
        bot.send_message(message.from_user.id, get_map_str(matrix, (0, 0)), reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message.from_user.id, "Неправильний формат. Спробуйте знову.")

#механізм руху
@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
    user_data = maps.get(query.message.chat.id)
    if not user_data:
        return

    matrix = user_data['map']
    new_x, new_y = user_data['x'], user_data['y']

    # Зміна координат залежно від напрямку
    if query.data == 'left':
        new_x -= 1
    elif query.data == 'right':
        new_x += 1
    elif query.data == 'up':
        new_y -= 1
    elif query.data == 'down':
        new_y += 1

    # Перевірка на вихід за межі матриці
    if new_x < 0 or new_x >= len(matrix[0]) or new_y < 0 or new_y >= len(matrix):
        return None

    # Перевірка на стіну
    if matrix[new_y][new_x] == 1:
        return None

    # Оновлюємо координати гравця
    user_data['x'], user_data['y'] = new_x, new_y

    # Перевірка на виграшну умову
    if new_x == len(matrix[0]) - 1 and new_y == len(matrix) - 1:
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.id,
                              text="Ви перемогли!")
        return

    # Оновлюємо карту з новою позицією гравця
    bot.edit_message_text(chat_id=query.message.chat.id,
                          message_id=query.message.id,
                          text=get_map_str(matrix, (new_x, new_y)),
                          reply_markup=keyboard)

#Запуск
bot.polling(none_stop=True, interval=0)
