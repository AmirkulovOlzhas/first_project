import telebot
import config
import sqlcode
import sys
import traceback

from telebot import types

bot = telebot.TeleBot(config.TOKEN)


class Gen:  # general
    lang: str = "En"  # language
    # keyboard
    cmnkb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Language")
    item2 = types.KeyboardButton("/Search")
    item3 = types.KeyboardButton("Help")
    s_resultlen = 0  # количество рейсов
    all_places_in_str = []
    cmnkb.add(item1, item2, item3)  # обычная клавиатура (язык, поиск, помощь)
    rplaces = [[], []]  # все места в рейсе cо статусами
    rstasus = []  # статусы этих мест
    places_status = []  # места и статусы
    chose_places = []  # выбранные места пользователя
    client_name = ''  # имя покупателся
    search_result = []
    selected_search_result = ''
    travel_index = []  # индексы для работы в sql
    selected_travel_index = ''  # выбранный индекс


class Messages:  # messages
    help = 'This bot has 2 functions. Change the language, buy a ticket. ' \
           'The first one is designated as the Language button, ' \
           'and the second function starts after clicking the Search button.'  # информация для кнопки
    search_city1 = 'Enter the name of the city where you are staying. ' \
                   '(in Latin with a capital letter. For example, Almaty)'  # сообщение перед начатием поиска по бд
    search_city2 = 'Enter the name of the city where you are going. ' \
                   '(in Latin with a capital letter. For example, Almaty)'
    search_set_date = 'set date'
    search_all_date = "do you wanna see all travels?"
    search_show_alldate = 'All flights to the specified destination'
    error = 'I dont understand you. Pleas, press /help'  # неизвестное сообщение/команда
    setlang = 'Language selected - "En"'
    show_all = "Show all"
    choose_date = "Choose date"
    yes_ill_buy = "yes, i will buy"
    no_ill_not_buy = "no, thx"
    l1 = 'Ru'
    l2 = 'Kz'
    city1 = '1'
    city2 = '1'
    traveldate = '1'

    @staticmethod
    def refreshlang():  # обновление фраз, при смене языка
        if Gen.lang == 'En':
            Messages.help = "This bot has 2 functions. Change the language, buy a ticket. " \
                            "The first one is designated as the Language button, " \
                            "and the second function starts after clicking the Search button."
            Messages.search_city1 = "Enter the name of the city where you are staying. " \
                                    "(in Latin with a capital letter. For example, Almaty)"
            Messages.search_city2 = "Enter the name of the city where you are going. " \
                                    "(in Latin with a capital letter. For example, Almaty)"
            Messages.error = "I dont understand you. Pleas, press /help"
            Messages.setlang = 'Language selected - "En"'
            Messages.show_all = "Show all"
            Messages.search_all_date = "do you wanna see all travels?"
            Messages.choose_date = "Choose date"
            Messages.yes_ill_buy = "yes, i will buy"
            Messages.no_ill_not_buy = "no, thx"
            Messages.l1 = 'Ru'
            Messages.l2 = 'Kz'
        elif Gen.lang == 'Ru':
            Messages.help = "У этого бота есть 2 функций. Менять язык, покупка билета. " \
                            "Первый обозначен как кнопка Language, " \
                            "а вторая функция начинается после нажатия кнопки Search."
            Messages.search_city1 = "Введите название города откуда вы направляетесь. " \
                                    "(на латинице с заглавной. На пример Almaty)"
            Messages.search_city2 = "Введите название города куда вы направляетесь. " \
                                    "(на латинице с заглавной. На пример Almaty)"
            Messages.search_set_date = "Напишите дату когда вы хотите выйти в путь в следующем формате **.**.****"
            Messages.error = "Вы ввели недоступную команду, пожалуйста нажмите " \
                             "на кнопку help что бы прочитать инструкцию"
            Messages.setlang = 'Выбран язык - "Ru"'
            Messages.show_all = "Показать все"
            Messages.search_show_alldate = 'Все рейсы по указанному направлению'
            Messages.yes_ill_buy = "Да"
            Messages.no_ill_not_buy = "Нет"
            Messages.choose_date = "Выбрать дату"
            Messages.search_all_date = "Вы хотите увидеть рейсы по указанному направлению?"
            Messages.l1 = 'En'
            Messages.l2 = 'Kz'
        else:
            Messages.help = "Бұл боттың 2 функциясы бар. Тілді өзгерту, билет сатып алу. " \
                            "Біріншісі Language батырмасы ретінде белгіленеді, " \
                            "ал екінші функция іздеу түймесін басқаннан кейін басталады."
            Messages.search_city1 = "Сіз орналасқан қаланың атын енгізіңіз. (латын с заглавной. Almaty мысалы)"
            Messages.search_city2 = "Сіз баратын қаланың атын енгізіңіз. (латын с заглавной. Almaty мысалы)"
            Messages.error = "Вы ввели недоступную команду, пожалуйста напишити /home и " \
                             "на кнопку help что бы прочитать инструкцию"
            Messages.setlang = 'Таңдалынып тұрған тіл - "Kz"'
            Messages.l1 = 'Ru'
            Messages.l2 = 'En'


@bot.message_handler(commands=['start'])  # команда /start
def welcome(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}! Я - <b>{1.first_name}</b>\n"
                     "Welcome, {0.first_name}! Im - <b>{1.first_name}</b>\n"
                     "Қош келдіңіз, {0.first_name}! Мен - <b>{1.first_name}</b>\n".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=Gen.cmnkb)


@bot.message_handler(commands=['Search'])
def askcity(message):
    Messages.refreshlang()
    Gen.s_resultlen = 0
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, Messages.search_city1)
    bot.register_next_step_handler(msg, setcity1)  # связывает сообщение и ответ


def setcity1(message):
    Messages.city1 = str(message.text)
    msg = bot.send_message(message.chat.id, Messages.search_city2)
    bot.register_next_step_handler(msg, setcity2)


def setcity2(message):
    Messages.city2 = str(message.text)
    chose_date_keyboard = types.InlineKeyboardMarkup(row_width=2)
    alldate = types.InlineKeyboardButton(Messages.show_all, callback_data='Show all date')
    select_date = types.InlineKeyboardButton(Messages.choose_date, callback_data='Choose date')
    chose_date_keyboard.add(alldate, select_date)
    bot.send_message(message.chat.id, Messages.search_all_date, reply_markup=chose_date_keyboard)


def showalldate(chatid):  # показать все рейсы
    Gen.search_result, Gen.travel_index = sqlcode.read_sqlite_table(Messages.city1, Messages.city2, '')
    if not Gen.search_result:
        bot.send_message(chat_id=chatid, text='нету в базе')
    else:
        Gen.s_resultlen = 0
        item = []
        result_keyboard = types.InlineKeyboardMarkup(row_width=7)
        for row in Gen.search_result:
            item.append(types.InlineKeyboardButton(row, callback_data=row))
            result_keyboard.add(item[Gen.s_resultlen])  # добавляем каждый найденный результат в инлайн клав
            Gen.s_resultlen += 1
        bot.send_message(chat_id=chatid,
                         text='Все доступные рейсы на \n' + Messages.city1 + ' -> ' +
                              Messages.city2 + ' , ' + Messages.traveldate,
                         reply_markup=result_keyboard)


def settraveldate(message):
    Messages.traveldate = str(message.text)
    Gen.search_result, Gen.travel_index = sqlcode.read_sqlite_table(Messages.city1, Messages.city2, Messages.traveldate)
    if not Gen.search_result:
        bot.send_message(message.chat.id, 'нету в базе')
    else:
        Gen.s_resultlen = 0
        item = []
        result_keyboard = types.InlineKeyboardMarkup(row_width=7)
        for row in Gen.search_result:
            item.append(types.InlineKeyboardButton(row, callback_data=row))
            result_keyboard.add(item[Gen.s_resultlen])  # добавляем каждый найденный результат в инлайн клав
            Gen.s_resultlen += 1
        bot.send_message(message.chat.id,
                         text='Все доступные рейсы на \n' + Messages.city1 + ' -> ' +
                              Messages.city2 + ' , ' + Messages.traveldate,
                         reply_markup=result_keyboard)


def choose_place(message):
    # выбор места
    try:
        i = 0  # test for write place
        j = 0  # test for count
        st = 0  # test for status of place
        Gen.chose_places = []
        selected_place = message.text
        place_list = selected_place.split()
        for row in place_list:
            Gen.chose_places.append(row)
            if (int(row) > 16) | (int(row) < 1):  # проверяем выбранные пользователем места на корректноть
                i += 1
            if place_list.count(row) > 1:
                j += 1
            for k in Gen.rplaces[0]:  # все места в рейсе cо статусами [[0-места],[1-статусы]]
                if int(k) == int(row):
                    calc = 1  # будем считать до к
                    for row1 in Gen.rplaces[1]:
                        if k == calc:
                            if int(row1) == 1:
                                st += 1
                            break
                        calc += 1

        if (i == 0) & (j == 0) & (st == 0):  # если все ок то тут продолжение

            msg = bot.send_message(message.chat.id, 'Отлично вы выбрали эти места: \n' +
                                   str(Gen.chose_places) + "\n Напишите свое имя")
            bot.register_next_step_handler(msg, Set_client_name)

        else:
            if j != 0:
                msg = bot.send_message(message.chat.id,
                                       "Вы можете выбрать одно место только один раз" + str(place_list) + '   ' + str(
                                           j))
                bot.register_next_step_handler(msg, choose_place)
            elif i != 0:
                msg = bot.send_message(message.chat.id, "Вы ввели неправильное место")
                bot.register_next_step_handler(msg, choose_place)
            elif st != 0:
                msg = bot.send_message(message.chat.id, "Это место уже занято")
                bot.register_next_step_handler(msg, choose_place)

    except Exception as e:
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno, fn, text = frame
            print("Error in %s on line %d" % (fname, lineno))
        msg = bot.send_message(message.chat.id, "Вы ввели не правильные данные, Нужно ввести места "
                                                "которые хотите занять цифрами через пробел")
        bot.register_next_step_handler(msg, choose_place)


def Set_client_name(message):
    # Переспрашиваем имя
    Gen.client_name = str(message.text)
    reply_keyboar = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton('Да', callback_data='yes_name')
    item2 = types.InlineKeyboardButton('Нет', callback_data='no_name')
    reply_keyboar.add(item1, item2)
    bot.send_message(message.chat.id, "Вас зовут " + Gen.client_name + '?', reply_markup=reply_keyboar)


def Set_order_in_sql(message):  # бронируем место
    if (not Gen.chose_places) | (Gen.client_name == ''):
        bot.send_message(message.chat.id, "Ошибка, выбраны неверные места либо не указано имя")
    else:
        cods = sqlcode.set_order(Gen.chose_places, Gen.client_name, Gen.selected_travel_index)
        bot.send_message(message.chat.id, "Это ваш код подтверждения, используйте его при посадке: \n"+str(cods))
        # bot.send_invoice(
        #     message.message.chat.id,
        #     title='Оплатите вашу покупку',
        #     description=" Покупка билетов на места: " + str(Gen.chose_places) + " рейса: " + str(
        #         Gen.selected_search_result),
        #     provider_token=config.pay_token,
        #     currency="KZT",
        #     prices=[types.LabeledPrice(label='Билет', amount=10000)],
        #     start_parameter='get_access',
        #     invoice_payload="успех"
        # )


@bot.message_handler(content_types=['text'])
def talking_with_bot(message):
    if message.chat.type == 'private':
        if message.text == 'Language':
            Messages.refreshlang()
            langmarkup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton(Messages.l1, callback_data=Messages.l1)
            item2 = types.InlineKeyboardButton(Messages.l2, callback_data=Messages.l2)
            langmarkup.add(item1, item2)
            bot.send_message(message.chat.id, text=Messages.setlang,
                             reply_markup=langmarkup)

        elif message.text == 'Help':
            Messages.refreshlang()
            bot.send_message(message.chat.id, Messages.help)

        elif message.text == '/Search':
            Messages.refreshlang()

        else:
            Messages.refreshlang()
            bot.send_message(message.chat.id, Messages.error)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(chlang):  # change lang
    try:
        if chlang.message:
            if chlang.data == 'Kz':
                Gen.lang = 'Kz'
                # remove inline buttons
                bot.edit_message_text(chat_id=chlang.message.chat.id, message_id=chlang.message.message_id,
                                      text='Сіз Қазақ тілін таңдадыңыз!',
                                      reply_markup=None)
            elif chlang.data == 'Ru':
                Gen.lang = 'Ru'
                # remove inline buttons
                bot.edit_message_text(chat_id=chlang.message.chat.id, message_id=chlang.message.message_id,
                                      text='Вы выбрали Русский язык!',
                                      reply_markup=None)
            elif chlang.data == 'En':
                Gen.lang = 'En'
                # remove inline buttons
                bot.edit_message_text(chat_id=chlang.message.chat.id, message_id=chlang.message.message_id,
                                      text='You chose English!',
                                      reply_markup=None)
            if Gen.s_resultlen != 0:  # если в инлайн клав были выведены рейсы

                for row in range(Gen.s_resultlen):
                    if chlang.data == str(Gen.search_result[row]):
                        # сохроняем имя выбранного рейса в Gen
                        Gen.selected_search_result = str(Gen.search_result[row])
                        Gen.selected_travel_index = str(Gen.travel_index[row])
                        Gen.rplaces = [[], []]  # for select place [place, status]
                        Gen.rstatus = []
                        Gen.places_status = []  # for show in text message [place - free]
                        places_fromsql, status_fromsql = sqlcode.select_place(
                            Gen.search_result[row])

                        for i in status_fromsql:
                            Gen.rstatus.append(i[0])
                        for i in places_fromsql:
                            for j in i:
                                Gen.rplaces[0].append(i[0])
                                Gen.rplaces[1].append(Gen.rstatus[int(j) - 1])
                                if Gen.rstatus[int(j) - 1] == 0:
                                    Gen.places_status.append(str(i[0]) + ' - Свободно')
                                else:
                                    Gen.places_status.append(str(i[0]) + ' -  Занято')

                        Gen.all_places_in_str = '\n'.join(map(str, Gen.places_status))  # места
                        ask_buy = types.InlineKeyboardMarkup(row_width=2)
                        buy_yes = types.InlineKeyboardButton("Да", callback_data="buy_yes")
                        buy_no = types.InlineKeyboardButton("Нет", callback_data="buy_no")
                        ask_buy.add(buy_yes, buy_no)
                        bot.send_message(chat_id=chlang.message.chat.id,
                                         text='Информация о рейсе - ' + str(
                                             Gen.search_result[
                                                 row]) + '\n' + Gen.all_places_in_str + '\nВы хотите купить билет?',
                                         reply_markup=ask_buy)

            if chlang.data == "Show all date":
                bot.send_message(chat_id=chlang.message.chat.id, text=Messages.search_show_alldate)
                showalldate(chlang.message.chat.id)
            if chlang.data == 'Choose date':
                msg = bot.send_message(chat_id=chlang.message.chat.id, text=Messages.search_set_date)
                bot.register_next_step_handler(msg, settraveldate)
            if chlang.data == 'buy_yes':
                msg1 = bot.send_message(chat_id=chlang.message.chat.id,
                                        text="прекрасно, напишите свободные места через пробел")
                bot.register_next_step_handler(msg1, choose_place)
            if chlang.data == 'buy_no':
                bot.send_message(chat_id=chlang.message.chat.id, text="окей")
            if chlang.data == 'no_name':
                msg1 = bot.send_message(chat_id=chlang.message.chat.id,
                                        text="Напишите свое имя заново")
                bot.register_next_step_handler(msg1, Set_client_name)
            if chlang.data == 'yes_name':
                msg = bot.send_message(chat_id=chlang.message.chat.id,
                                       text="Отправьте любое сообщение для подтверждения заказа")
                bot.register_next_step_handler(msg, Set_order_in_sql)
                # bot.send_invoice(
                #     chlang.message.chat.id,
                #     title='Оплатите вашу покупку',
                #     description=" Покупка билетов на места: " + str(Gen.chose_places) + " рейса: " + str(
                #         Gen.selected_search_result),
                #     provider_token=config.pay_token,
                #     currency="KZT",
                #     prices=[types.LabeledPrice(label='Билет', amount=10000)],
                #     start_parameter='get_access',
                #     invoice_payload="успех"
                # )

    except Exception as e:
        print('Ошибка в коде - ' + repr(e))
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno, fn, text = frame
            print("Error in %s on line %d" % (fname, lineno))


# RUN
bot.polling(none_stop=True)
