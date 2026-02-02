# -*- coding: cp1251 -*-
import telebot
import json
import requests
import datetime
import re
import setting
from bs4 import BeautifulSoup
version = setting.VERSION
separator = '@'
bot = telebot.TeleBot(setting.TOKEN, parse_mode=None)

@bot.message_handler(commands=['version'])
def start_message(message):
  bot.send_chat_action(message.chat.id, action='typing')
  bot.send_message(message.chat.id, version)

@bot.message_handler(commands=['setting'])
def start_message(message):
    bot.send_chat_action(message.chat.id, action='typing')
    with open('help.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Необходимо скопировать url адрес как на изображении")
    msg = bot.send_message(message.chat.id, "Отправьте url страницы вашего расписания \nДля отмены используйте /e")
    bot.register_next_step_handler(msg, url_update, message.chat.id, message.chat.username, message.chat.title)

def get_url(message):
    with open('users.json', 'r') as file:
        users_list = json.load(file)
    for i in range (0,  users_list["count"]):
        if (users_list["users"][i]["id"] == message.chat.id):
            url = users_list["users"][i]["url"]
    return url

def url_update(message, chat_id, username, title):
    url = message.text
    if url == '/e':
        bot.send_message(message.chat.id, "Отменено!")
        return 0
    with open('users.json', 'r') as file:
        users_list = json.load(file)
    q = 0
    for i in range (0,  users_list["count"]):
        if (users_list["users"][i]["id"] == chat_id):
            temp = {"id": users_list["users"][i]["id"], "username": users_list["users"][i]["username"], "title": users_list["users"][i]["title"], "url": url}
            users_list["users"][i] = temp
            q+=1
            break
    if q == 0:
        temp = {"id": chat_id, "username": username, "title": title, 'url': url}
        users_list["users"].append(temp)
        users_list["count"] += 1
            
    with open('users.json', "w", encoding="utf-8") as file:
        json.dump(users_list, file, indent=4)
        bot.send_message(message.chat.id, "Сохранено!")

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_chat_action(message.chat.id, action='typing')
    bot.send_message(message.chat.id, "Расписание ПензГТУ \nИспользуйте /setting, чтобы добавить url расписания \nИспользуйте /help для получения подсказки")

@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_chat_action(message.chat.id, action='typing')
    bot.send_message(message.chat.id, "Расписание ПензГТУ \n/setting - настройки \n/shedule_today - расписание на сегодня \n/shedule_tomorrow - расписание на завтра \n/shedule_monday - расписание на понедельник \n/shedule_tuesday - расписание на вторник \n/shedule_wednesday - расписание на среду \n/shedule_thursday - расписание на четверг \n/shedule_friday - расписание на пятницу \n/shedule_saturday - расписание на субботу")

def current_day_of_week_today():
    date = datetime.date.today()
    day_of_week = date.isoweekday()
    return day_of_week

def date_today():
    date = datetime.date.today()
    date1 = {'day': date.day, 'month': date.month, 'year': date.year}
    return date1

def current_week_today(message):
    url = get_url(message)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    curweek_div = soup.find('div', class_='curweek-div')
    if curweek_div:
        curweek_text = curweek_div.find('p', class_='curweek-p').text.strip()
        we = re.search(r'(первой|второй)', curweek_text)
        if we:
            current_week = we.group(1)
        else:
            current_week = None
    else:
        current_week = None
    return current_week


@bot.message_handler(commands=['shedule_today'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Monday = None
    Tuesday = None
    Wednesday = None
    Thursday = None
    Friday = None
    Saturday = None
    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Понедельник':
            Monday = table
        elif day_title == 'Вторник':
            Tuesday = table
        elif day_title == 'Среда':
            Wednesday = table
        elif day_title == 'Четверг':
            Thursday = table
        elif day_title == 'Пятница':
            Friday = table
        elif day_title == 'Суббота':
            Saturday = table

    c_w = current_week_today(message)
    c_d_of_w = current_day_of_week_today()
    d_t = date_today()

    if c_d_of_w == 1:
        text3 = 'Понедельник'
    elif c_d_of_w == 2:
        text3 = 'Вторник'
    elif c_d_of_w == 3:
        text3 = 'Среда'
    elif c_d_of_w == 4:
        text3 = 'Четверг'
    elif c_d_of_w == 5:
        text3 = 'Пятница'
    elif c_d_of_w == 6:
        text3 = 'Суббота'
    elif c_d_of_w == 7:
        text3 = 'Воскресенье'

    day = d_t['day']
    month = d_t['month']
    year = d_t['year']

    text1 = f'Сегодня {day}-{month}-{year} \n' + text3
    text2 = f'Занятия сегодня проходят по {c_w} неделе \n'
    try:
        if c_d_of_w == 1:
            out = text2 + text1 + Monday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 2:
            out = text2 + text1 + Tuesday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 3:
            out = text2 + text1 + Wednesday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 4:
            out = text2 + text1 + Thursday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 5:
            out = text2 + text1 + Friday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 6:
            out = text2 + text1 + Saturday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 7:
            out = "Сегодня выходной"
            bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_tomorrow'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Monday = None
    Tuesday = None
    Wednesday = None
    Thursday = None
    Friday = None
    Saturday = None
    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Понедельник':
            Monday = table
        elif day_title == 'Вторник':
            Tuesday = table
        elif day_title == 'Среда':
            Wednesday = table
        elif day_title == 'Четверг':
            Thursday = table
        elif day_title == 'Пятница':
            Friday = table
        elif day_title == 'Суббота':
            Saturday = table

    c_w = current_week_today(message)
    c_d_of_w = current_day_of_week_today()
    c_d_of_w += 1
    if c_d_of_w > 7:
        c_d_of_w = 1
        if c_w == 'первой':
            c_w = 'второй'
        else:
            c_w = 'первой'
    d_t = date_today()

    if c_d_of_w == 1:
        text3 = 'Понедельник'
    elif c_d_of_w == 2:
        text3 = 'Вторник'
    elif c_d_of_w == 3:
        text3 = 'Среда'
    elif c_d_of_w == 4:
        text3 = 'Четверг'
    elif c_d_of_w == 5:
        text3 = 'Пятница'
    elif c_d_of_w == 6:
        text3 = 'Суббота'
    elif c_d_of_w == 7:
        text3 = 'Воскресенье'

    text4 =  f'Завтра {text3}'
    text2 = f'Занятия завтра проходят по {c_w} неделе \n' + text4

    try:
        if c_d_of_w == 1:
            out = text2 + Monday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 2:
            out = text2 + Tuesday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 3:
            out = text2 + Wednesday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 4:
            out = text2 + Thursday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 5:
            out = text2 + Friday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 6:
            out = text2 + Saturday.get_text()
            bot.send_message(message.chat.id, out)
        elif c_d_of_w == 7:
            out = "Сегодня выходной"
            bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_monday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Monday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Понедельник':
            Monday = table

    try:
        out = 'Расписание на Понедельник:\n' + Monday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_tuesday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Tuesday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Вторник':
            Tuesday = table

    try:
        out = 'Расписание на Вторник:\n' + Tuesday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_wednesday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Wednesday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Среда':
            Wednesday = table

    try:
        out = 'Расписание на Среду:\n' + Wednesday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_thursday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Thursday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Четверг':
            Thursday = table

    try:
        out = 'Расписание на Четверг:\n' + Thursday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_friday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Friday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Пятница':
            Friday = table

    try:
        out = 'Расписание на Пятницу:\n' + Friday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

@bot.message_handler(commands=['shedule_saturday'])
def shedule_todays(message):
    bot.send_chat_action(message.chat.id, action='typing')
    url = get_url(message)
    try:
        page = requests.get(url)
    except:
        bot.send_message(message.chat.id, 'некоректный url! \nИзмените url при помощи /setting')
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    day_divs = soup.find_all('div', class_='day-div')
    Saturday = None

    for day_div in day_divs:
        day_title = day_div.find('p', class_='day-title').text.strip()
        table = day_div.find('table', class_='day-table')
        if day_title == 'Суббота':
            Saturday = table

    try:
        out = 'Расписание на Субботу:\n' + Saturday.get_text()
        bot.send_message(message.chat.id, out)
    except:
        bot.send_message(message.chat.id, 'Данные недоступны!')

bot.infinity_polling()

