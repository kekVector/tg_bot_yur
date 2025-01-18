import telebot
from telebot import types  # buttons
from congi import bot_token
from datetime import datetime
from google_sheet_class import GoogleSheetAccounting, GoogleSheetEating

price_sheet = GoogleSheetAccounting()
eat_sheet = GoogleSheetEating()
bot = telebot.TeleBot(bot_token)
add_price = False
add_food = False
entered_date = ''

price_category = ''
price_sum_val = 0
price_add_info_val = ''

food_character_val = ''
food_eating_val = ''
food_add_info_val = ''


@bot.message_handler(commands=['start'])
def main(message):
    global add_price, add_food, entered_date, price_category, price_sum_val, price_add_info_val
    global food_character_val, food_eating_val, food_add_info_val
    add_price = False
    add_food = False
    entered_date = ''

    price_category = ''
    price_sum_val = 0
    price_add_info_val = ''

    food_character_val = ''
    food_eating_val = ''
    food_add_info_val = ''
    # bot.delete_message(message.chat.id, message.id)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Ввести данные', callback_data='enter')
    btn2 = types.InlineKeyboardButton('Редактировать данные', callback_data='edit')
    btn3 = types.InlineKeyboardButton('Вывести данные', callback_data='load')
    btn4 = types.InlineKeyboardButton('GoogleDock по тратам',
                                      url='https://docs.google.com/spreadsheets/d/1JGY5rMLUvQkHQXyotVoxXx2Rfg1As_pSjrZGinOBdG4/edit?pli=1&gid=0#gid=0')
    btn5 = types.InlineKeyboardButton('GoogleDock по еде', url='http://google.com')
    markup.row(btn1)
    markup.row(btn3)
    markup.row(btn2)
    markup.row(btn4, btn5)
    bot.send_message(message.chat.id, 'Menu', reply_markup=markup)


@bot.callback_query_handler(func=lambda cb: True)
def callback_message(cb):
    if cb.data == 'enter':
        enter_f(cb)
    elif cb.data == 'price':
        price_f(cb)
    elif cb.data == 'food':
        food_f(cb)


def enter_f(cb):
    # bot.delete_message(cb.message.chat.id, cb.message.id, timeout=0)
    markup = types.InlineKeyboardMarkup()
    prices = types.InlineKeyboardButton('Ввести данные по покупкам', callback_data='price')
    food = types.InlineKeyboardButton('Ввести данные по еде', callback_data='food')
    back = types.InlineKeyboardButton('Назад', callback_data='back')
    markup.row(prices)
    markup.row(food)
    markup.row(back)
    # bot.edit_message_text(text='menu2', chat_id=cb.message.chat.id, message_id=cb.message.id)
    bot.edit_message_text('menu2', cb.message.chat.id, cb.message.id)
    bot.edit_message_reply_markup(cb.message.chat.id, cb.message.id, reply_markup=markup)
    # bot.send_message(cb.message.chat.id, 'Menu2', reply_markup=markup)


def price_f(cb):
    global add_price
    add_price = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Покупка в магазине')
    btn2 = types.KeyboardButton('Доставка из ресторана')
    btn3 = types.KeyboardButton('Ресторан')
    btn4 = types.KeyboardButton('Другое')
    markup.add(btn1, btn2, btn3, btn4)

    bot.edit_message_text('Категория', cb.message.chat.id, cb.message.id)
    bot.send_message(cb.message.chat.id, 'Введите категорию или выберите из списка', reply_markup=markup)

    bot.register_next_step_handler(cb.message, enter_date)


def enter_date(message):
    # global add_price, add_food
    del_rows(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    today = types.KeyboardButton(f'{datetime.now().day}.'
                                 f'{datetime.now().month if datetime.now().month > 9 else "0" + str(datetime.now().month)}.'
                                 f'{datetime.now().year}')
    yesterday = types.KeyboardButton(f'{datetime.now().day - 1}.'
                                     f'{datetime.now().month if datetime.now().month > 9 else "0" + str(datetime.now().month)}.'
                                     f'{datetime.now().year}')
    markup.add(yesterday, today)
    bot.send_message(message.chat.id, 'Введите дату:', reply_markup=markup)
    bot.send_message(message.chat.id, 'В формате "День.Месяц" или "День.Месяц.Год"', reply_markup=markup)
    if add_price:
        global price_category
        price_category = message.text
        bot.register_next_step_handler(message, price_sum)
    elif add_food:
        global food_character_val
        food_character_val = message.text
        bot.register_next_step_handler(message, food_eating)


def price_sum(message):
    global entered_date
    try:
        if '.' in message.text:
            date = message.text.split('.')
            day = int(date[0])
            month = int(date[1])
            year = int(date[2]) if len(date) > 3 else int(datetime.now().year)
        else:
            date = message.text
            day = int(date[0:1])
            month = int(date[2:4])
            year = int(date[4:]) if len(message.text) > 5 else int(datetime.now().year)
        if (day > 32) or (month > 12) or (year > 9999):
            raise ValueError
        entered_date = f'{day}.{month}.{year}' if month > 9 else f'{day}.0{month}.{year}'

        del_rows(message)

        bot.send_message(message.chat.id, 'Введите сумму:')
        bot.register_next_step_handler(message, price_add_info)
    except ValueError:
        del_rows(message)

        bot.send_message(message.chat.id, 'Ошибка!')
        bot.send_message(message.chat.id, 'Введите дату в  формате "День.Месяц" или "День.Месяц.Год"')

        bot.register_next_step_handler(message, price_sum)


def price_add_info(message):
    global price_sum_val
    try:
        price_sum_val = int(message.text)

        del_rows(message)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Дополнительной информации нет')

        markup.add(btn1)
        bot.send_message(message.chat.id, 'Введите дополнительную информацию при необходимости', reply_markup=markup)
        bot.register_next_step_handler(message, price_result)

    except ValueError:
        del_rows(message)

        bot.send_message(message.chat.id, 'Ошибка ввода \nВведите сумму покупки:')
        bot.register_next_step_handler(message, price_add_info)


# Result price
def price_result(message):
    global price_add_info_val, add_price
    price_add_info_val = message.text
    add_price = False

    del_rows(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/start')
    markup.add(btn1)

    price_write_result(price_category, entered_date, price_sum_val,
                       price_add_info_val, message.from_user.username, message.date)
    # bot.send_message(message.chat.id, message)
    bot.send_message(message.chat.id, 'Вы великолепны!', reply_markup=markup)
    # print(
    #    f'price_add_info_val {price_add_info_val}\nprice_sum_val {price_sum_val}\nentered_date {entered_date}\nprice_category {price_category} ')


def food_f(cb):
    global add_food
    add_food = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton('Юрий М.')
    btn2 = types.KeyboardButton('Юлия С.')
    btn3 = types.KeyboardButton('Общее')
    markup.row(btn1, btn2)
    markup.row(btn3)

    bot.edit_message_text('Кто совершал прием пищи', cb.message.chat.id, cb.message.id)
    bot.send_message(cb.message.chat.id, 'Если оба ели одно и то же, то категория Общее', reply_markup=markup)

    bot.register_next_step_handler(cb.message, enter_date)


def food_eating(message):
    global entered_date
    try:
        if '.' in message.text:
            date = message.text.split('.')
            day = int(date[0])
            month = int(date[1])
            year = int(date[2]) if len(date) > 3 else int(datetime.now().year)
        else:
            date = message.text
            day = int(date[0:1])
            month = int(date[2:4])
            year = int(date[4:]) if len(message.text) > 5 else int(datetime.now().year)
        if (day > 32) or (month > 12) or (year > 9999):
            raise ValueError
        entered_date = f'{day}.{month}.{year}' if month > 9 else f'{day}.0{month}.{year}'

        del_rows(message)

        bot.send_message(message.chat.id, 'Введите что ели:')
        bot.register_next_step_handler(message, food_add_info)

    except ValueError:
        del_rows(message)

        bot.send_message(message.chat.id, 'Ошибка!')
        bot.send_message(message.chat.id, 'Введите дату в  формате "День.Месяц" или "День.Месяц.Год"')

        bot.register_next_step_handler(message, price_sum)


def food_add_info(message):
    global food_eating_val
    food_eating_val = message.text
    del_rows(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Дополнительной информации нет')

    markup.add(btn1)
    bot.send_message(message.chat.id,
                     'Введите дополнительную информацию при необходимости(ссылка на рецепт, или другую)'
                     , reply_markup=markup)
    bot.register_next_step_handler(message, food_result)


def food_result(message):
    global food_add_info_val, add_food
    food_add_info_val = message.text
    add_food = False

    del_rows(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/start')
    markup.add(btn1)

    eat_write_result(entered_date, food_character_val, food_eating_val,
                     food_add_info_val, message.from_user.username, message.date)

    bot.send_message(message.chat.id, 'Вы великолепны!', reply_markup=markup)
    # print(
    #    f'food_add_info_val {food_add_info_val}\nfood_eating_val {food_eating_val}\nentered_date'
    #   f' {entered_date}\nfood_character_val {food_character_val} ')


def del_rows(message, n=10):
    try:
        for i in range(n):
            bot.delete_message(message.chat.id, message.id - i)
    except Exception as e:
        pass


def price_write_result(category, date, price, info, user, time):
    dt_time = str(datetime.fromtimestamp(time))
    price_sheet.enter_values_to_end(category, date, price, info, user, dt_time)


def eat_write_result(date, char, food, info, user, time):
    dt_time = str(datetime.fromtimestamp(time))
    eat_sheet.enter_values_to_end(date, char, food, info, user, dt_time)


# start
#
#
def run_module(fatigue_msg=None, chat_id='742630935'):
    if fatigue_msg == 'Error':
        bot.send_message(chat_id, 'Was exception')
    bot.polling(none_stop=True)


if __name__ == '__main__':
    #bot.send_message('742630935', 'bot started')
    err_msg = ''
    while True:
        try:
            run_module(err_msg)
        except Exception as e:
            print(e)
            err_msg = 'Error'

