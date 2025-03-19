import telebot
from telebot import types
import requests
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import quotation_to_decimal

import datetime

BOT_TOKEN = 'BOT_TOKEN'
TOKEN = "TOKEN"
stock_figis = {
    'Rosneft': 'BBG004731354',
    'Gazprom': 'BBG004730RP0',
    'Sberbank': 'BBG0047315Y7',
    'Magnit': 'BBG004RVFCY3',
    'LUKOIL': 'BBG004731032',
    'Beluga': 'BBG000TY1CD1',
    'TATNEFT': 'BBG004RVFFC0',
    'Mail.Ru': 'BBG00178PGX3'
}


class FinanceAPI:  # тут я работаю с биржей

    def __init__(self, token):
        self.token = token

    def get_rate(self, base_currency, target_currency):
        url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
        response = requests.get(url)
        data = response.json()
        return data['rates'][target_currency]

    def get_tinkoff_quotes(self, figi):
        if not TOKEN:
            return "Не удалось получить котировки."
        try:
            with Client(TOKEN) as client:
                quotes = []
                trade_day = False
                days_ago = 0
                while not trade_day:
                    for candle in client.get_all_candles(
                            figi=figi,
                            from_=datetime.datetime.now() - datetime.timedelta(days=days_ago),
                            to=datetime.datetime.now(),
                            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
                    ):
                        if candle.close:
                            trade_day = True
                            quotes.append(
                                f"{candle.time:%Y-%m-%d %H:%M}: {float(quotation_to_decimal(candle.close))} RUB")
                    days_ago += 1
                return "\n".join(quotes)
        except Exception as e:
            return f"Произошла ошибка при получении котировок: {str(e)}"


class FinanceBot:  # тут я работаю непосредственно с самим ботом в тг
    def __init__(self, bot_token, api_token):
        self.bot = telebot.TeleBot(bot_token)
        self.api = FinanceAPI(api_token)
        self.section = None
        self.base_currency = None

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.section = None
            self.base_currency = None
            markup = self.create_keyboard(['Валюты', 'Акции'])
            self.bot.send_message(message.chat.id,
                                  "Привет, этот бот подскажет тебе курс валют и стоимость некоторых акций! Выбери интересующий раздел:",
                                  reply_markup=markup)

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            if message.text == 'Назад':
                self.section = None
                self.base_currency = None
                markup = self.create_keyboard(['Валюты', 'Акции'])
                self.bot.send_message(message.chat.id,
                                      "Выберите интересующий раздел:",
                                      reply_markup=markup)
            elif self.section is None:
                self.section = message.text
                self.handle_section_selection(message)
            elif self.section == 'Валюты':
                self.handle_currency(message)
            elif self.section == 'Акции':
                self.handle_stocks(message)

    def handle_section_selection(self, message):
        if self.section == 'Валюты':
            markup = self.create_keyboard(['USD', 'EUR', 'JPY', 'KZT', 'UAH', 'RUB'])
            self.bot.send_message(message.chat.id, "Выберите базовую валюту:", reply_markup=markup)
        elif self.section == 'Акции':
            markup = self.create_keyboard(['Rosneft', 'Gazprom', 'Sberbank', 'Magnit', 'LUKOIL', 'Beluga', 'TATNEFT', 'Mail.Ru'])
            self.bot.send_message(message.chat.id, "Выберите акции:", reply_markup=markup)

    def handle_currency(self, message):
        if not self.base_currency:
            self.base_currency = message.text
            markup = self.create_keyboard(['USD', 'EUR', 'JPY', 'KZT', 'UAH', 'RUB'])
            self.bot.send_message(message.chat.id, "Выберите валюту для конвертации:", reply_markup=markup)
        else:
            target_currency = message.text
            try:
                rate = self.api.get_rate(self.base_currency, target_currency)
                self.bot.reply_to(message, f"Курс {self.base_currency}/{target_currency}: {rate}")
            except KeyError:
                self.bot.reply_to(message, "Извините, я не могу найти эту валюту.")
            self.base_currency = None

    def handle_stocks(self, message):
        stock_name = message.text
        try:
            figi = stock_figis.get(stock_name)
            if figi:
                tinkoff_quotes = self.api.get_tinkoff_quotes(figi)
                self.bot.reply_to(message, tinkoff_quotes)
            else:
                self.bot.reply_to(message, "Извините, не удалось получить информацию о цене акций.")
        except KeyError:
            self.bot.reply_to(message, "Извините, я не могу найти информацию по этой акции.")
        finally:
            self.section = None

    def create_keyboard(self, options_list):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for option in options_list:
            markup.add(types.KeyboardButton(option))
        markup.add(types.KeyboardButton('Назад'))
        return markup

    def run(self):
        self.bot.polling(none_stop=True)


finance_bot = FinanceBot(BOT_TOKEN, TOKEN)
finance_bot.run()
