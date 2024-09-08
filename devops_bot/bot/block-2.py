import logging, re, paramiko, psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from psycopg2 import Error

TOKEN = "7421669519:AAGpP5L-9aidNbF0ulNRBvCKTNCRqlhjAKA"

# Этапы диалога
FIRST, SECOND, THIRD, FOURTH = range(4)

host = "172.17.0.1"
db_host = "block-3-postgres_primary-1"
db_user = "user"
db_pass = "password"
database = "postgres"
username = "py-ssh"
password = "py-ssh"
phoneNumberList = ""
mailAddressList = ""

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)
logger = logging.getLogger(__name__)

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('❔ Введите текст для поиска телефонных номеров: ')
    return FIRST

def findMailAddressCommand(update: Update, context):
    update.message.reply_text('❔ Введите текст для поиска адресов email: ')
    return THIRD

def verifyPasswdCommand(update: Update, context):
    update.message.reply_text('❔ Введите пароль для проверки: ')
    return 'verifyPasswd'

def aptListCommand(update: Update, context):
    update.message.reply_text('❔ Введите название программы: ')
    return 'aptList'

def findPhoneNumbers(update: Update, context):
    global phoneNumberList
    user_input = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+)?(?:[7,8])(?:\ |\-|\(){,2}(?:[0-9]{3})(?:\ |\-|\)){,2}(?:[0-9]{3})(?:\ |\-){,1}(?:[0-9]{2})(?:\ |\-){,1}(?:[0-9]{2})')  # форматы номеров

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('🚫 Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем работу обработчика диалога

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text("❔ Добавить телефоны в БД? (yes/no)")
    return SECOND  # переход ко второму диалогу

def savePhoneNumbers(update: Update, context):
    user_input_save = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

    if user_input_save == "yes":    # проверка ответа
        connection = None

        try:    # описываем подключение к БД
            connection = psycopg2.connect(user=db_user,
                                          password=db_pass,
                                          host=db_host,
                                          port="5432",
                                          database=database)

            cursor = connection.cursor()
            for i in range(len(phoneNumberList)):   # цикл записи в БД
                cursor.execute(f"INSERT INTO phone (phone) VALUES ('{phoneNumberList[i]}');")
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text("✅ Телефоны добавлены в БД.")  # Отправляем сообщение пользователю
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text("🚫 Ошибка при работе с PostgreSQL, телефоны не добавлены.")  # Отправляем сообщение пользователю
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

    else:
        update.message.reply_text("🚫 Телефоны не добавлены в БД.")  # Отправляем сообщение пользователю

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def findMailAddress(update: Update, context):
    global mailAddressList
    user_input = update.message.text  # Получаем текст, содержащий (или нет) адреса email

    passwdRegex = re.compile(r'[\w.-]+@[\w.-]+\.[\w+]{2,10}')  # форматы email

    mailAddressList = passwdRegex.findall(user_input)  # Ищем email

    if not mailAddressList:  # Обрабатываем случай, когда адресов email нет
        update.message.reply_text('🚫 Адреса email не найдены')
        return ConversationHandler.END  # Завершаем работу обработчика диалога

    mailAddress = ''  # Создаем строку, в которую будем записывать адреса email
    for i in range(len(mailAddressList)):
        mailAddress += f'{i + 1}. {mailAddressList[i]}\n'  # Записываем очередной email

    update.message.reply_text(mailAddress)  # Отправляем сообщение пользователю
    update.message.reply_text("❔ Добавить адреса почты в БД? (yes/no)")
    return FOURTH  # 2nd dialog

def saveMailAddress(update: Update, context):
    user_input_save = update.message.text  # Получаем текст, содержащий (или нет) номера телефонов

    if user_input_save == "yes":
        connection = None

        try:
            connection = psycopg2.connect(user=db_user,
                                          password=db_pass,
                                          host=db_host,
                                          port="5432",
                                          database=database)

            cursor = connection.cursor()
            for i in range(len(mailAddressList)):
                cursor.execute(f"INSERT INTO email (email) VALUES ('{mailAddressList[i]}');")
            connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text("✅ Адреса электронной почты добавлены в БД.")  # Отправляем сообщение пользователю
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text("🚫 Ошибка при работе с PostgreSQL, адреса электронной почты не добавлены.")  # Отправляем сообщение пользователю
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

    else:
        update.message.reply_text("🚫 Адреса электронной почты не добавлены в БД.")  # Отправляем сообщение пользователю

    return ConversationHandler.END  # Завершаем работу обработчика диалога

def verifyPasswd(update: Update, context):
    user_input = update.message.text  # Получаем пароль

    passwdRegex = re.compile(r'(?=\S*[A-Z])(?=\S*[a-z])(?=\S*\d)(?=\S*[!@#$%^&*()])\S{8,}')  # формат пароля

    verifyPasswdList = passwdRegex.findall(user_input)  # Проверяем формат пароля

    if not verifyPasswdList:  # Обрабатываем случай, когда пароль не соответствует требованиям
        update.message.reply_text('🚫 Пароль простой')
        return  # Завершаем выполнение функции

    update.message.reply_text('✅ Пароль сложный')  # Пароль соответствует требованиям
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def aptList(update: Update, context):
    user_input = update.message.text  # Получаем название программы

    command = "apt show " + user_input + " | head -n 7" # формируем команду запроса

    # подключаемся к хосту
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    output = ""
    stdin, stdout, stderr = client.exec_command(command)

    stdout = stdout.readlines()
    client.close()

    for line in stdout:
        output = output + line
    if output != "":
        print(output)
    else:
        output = "🚫 Софт не найден."

    update.message.reply_text(output)  # Пароль соответствует требованиям
    return ConversationHandler.END  # Завершаем работу обработчика диалога

def menu(update, _):
    keyboard = [
        [
            InlineKeyboardButton("🔢 Релиз", callback_data='get_release'),
            InlineKeyboardButton("⏳ Время работы", callback_data='get_uptime'),
        ],
        [InlineKeyboardButton("⚡ ЦПУ, имя хоста и ядро", callback_data='get_uname'),],
        [
            InlineKeyboardButton("💾 Состояние ФС", callback_data='get_df'),
            InlineKeyboardButton("💻 Состояние ОЗУ", callback_data='get_free'),
        ],
        [
            InlineKeyboardButton("💪 Производительность", callback_data='get_mpstat'),
            InlineKeyboardButton("👨‍💻 Пользователи", callback_data='get_w'),
        ],
        [InlineKeyboardButton("🚪 Последние 10 входов в систему", callback_data='get_auths')],
        [InlineKeyboardButton("🛑 Последние 5 критических событий", callback_data='get_critical')],
        [
            InlineKeyboardButton("🧬 Процессы", callback_data='get_ps'),
            InlineKeyboardButton("😈 Сервисы", callback_data='get_services'),
            InlineKeyboardButton("🛜 Порты", callback_data='get_ss'),
        ],
        [InlineKeyboardButton("💿 Информация об установленных пакетах", callback_data='get_apt_list_all')],
        [InlineKeyboardButton("🔄️ Вывод логов о репликации", callback_data='get_repl_logs')],
        [
            InlineKeyboardButton("📧 Таблица с почтой", callback_data='get_emails'),
            InlineKeyboardButton("☎️ Таблица с телефонами", callback_data='get_phone_numbers'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Мониторинг Linux-системы:', reply_markup=reply_markup)

    # # Example of using a dictionary
    # dictionary = {'apple': 2, 'banana': 3, 'cherry': 5}
    #
    # for key, value in dictionary.items():
    #     print(f'The fruit {key} has {value} items.')


def button(update, _):
    query = update.callback_query
    variant = query.data
    query.answer()
    output = ""

    # формируем кейсы выбора кнопок
    if variant == "get_release":
        command = "cat /etc/*-release"
    elif variant == "get_uptime":
        command = "uptime"
    elif variant == "get_uname":
        command = "uname -a"
    elif variant == "get_df":
        command = "df -h"
    elif variant == "get_free":
        command = "free -h"
    elif variant == "get_mpstat":
        command = "mpstat"
    elif variant == "get_w":
        command = "w"
    elif variant == "get_auths":
        command = "last -10"
    elif variant == "get_critical":
        command = "journalctl -n 5 -p 2"
    elif variant == "get_ps":
        command = "ps aux | wc -l && echo && ps aux | head"
    elif variant == "get_services":
        command = "systemctl list-unit-files | wc -l && echo && systemctl list-unit-files | head"
    elif variant == "get_ss":
        command = "ss -tulpan"
    elif variant == "get_apt_list_all":
        command = "dpkg --list | wc --lines && echo && dpkg --list | head"
    elif variant == "get_repl_logs":
#        command = "cat /var/log/postgresql/postgresql-15-main.log | grep repl_user | tail"
        command = "docker logs block-3-postgres_primary-1 |& grep replica | tail"
    elif variant == "get_emails":
        command = "email"
    elif variant == "get_phone_numbers":
        command = "phone"
    else:
        print("Unknown command.")

    if command not in ['email', 'phone']:   # если кнопка не относится к работе с БД
        # подключаемся к хосту
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)

        stdout = stdout.readlines()
        client.close()

        for line in stdout:
            output = output + line
        if output != "":
            print(output)
        else:
            print("There was no output for this command")

        output = "```\n" + output + "```"
        query.message.reply_text(text=output, parse_mode='Markdown')

    else:   # если кнопка относится к рааботе с БД
        connection = None

        try:    # подключаемся к БД
            connection = psycopg2.connect(user=db_user,
                                          password=db_pass,
                                          host=db_host,
                                          port="5432",
                                          database=database)

            cursor = connection.cursor()    # получаем данные из таблиц
            cursor.execute(f"SELECT * FROM {command};")
            data = cursor.fetchall()
            for row in data:    # выводим в консоль и телегу
                print(row)
                output += str(row) + '\n'
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()

        output = "```\n" + output + "```"
        query.message.reply_text(text=output, parse_mode='Markdown')

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога phones
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            FIRST: [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            SECOND: [MessageHandler(Filters.text & ~Filters.command, savePhoneNumbers)],
        },
        fallbacks=[]
    )

    # Обработчик диалога email
    convHandlerFindMailAddress = ConversationHandler(
        entry_points=[CommandHandler('find_email', findMailAddressCommand)],
        states={
            THIRD: [MessageHandler(Filters.text & ~Filters.command, findMailAddress)],
            FOURTH: [MessageHandler(Filters.text & ~Filters.command, saveMailAddress)],
        },
        fallbacks=[]
    )

    # Обработчик диалога passwd
    convHandlerVerifyPasswd = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswdCommand)],
        states={
            'verifyPasswd': [MessageHandler(Filters.text & ~Filters.command, verifyPasswd)],
        },
        fallbacks=[]
    )

    # Обработчик диалога aptlist
    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', aptListCommand)],
        states={
            'aptList': [MessageHandler(Filters.text & ~Filters.command, aptList)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindMailAddress)
    dp.add_handler(convHandlerVerifyPasswd)
    dp.add_handler(convHandlerAptList)

    dp.add_handler(CommandHandler('menu', menu))
    dp.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
