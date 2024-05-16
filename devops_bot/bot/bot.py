import logging
import re
import paramiko
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


load_dotenv()
host = os.getenv('HOSTA')
port = os.getenv('PORTA')
username = os.getenv('USERA')
password = os.getenv('PASSWORDA')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')
db_host_pass = os.getenv('DB_HOST_PASS') 

user_db = os.getenv('USER_DB')
pass_db = os.getenv('PASS_DB')
database = os.getenv('DB')
port_db = os.getenv('PORT_DB')

TOKEN = os.getenv('TOKEN')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    logger.info("User %s started the conversation.", update.message.from_user)
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!\nВведи /help - для просмотра всех команд бота')


def helpCommand(update: Update, context):
    logger.info("User %s asked for help.", update.message.from_user)
    update.message.reply_text('EMAIL:\n/find_email - для поиска email в тексте\n/get_emails - для вывода сохраненных почт\nPHONE-NUMBER:\n/find_phone_number - для поиска номеров в тексте\n\
/get_phone_numbers - для вывода сохраненных номеров\nPASSWORD:\n/verify_password - проверка сложности пароля\nMONITORING:\n/get_release - o релизе\n\
/get_uname - oб архитектуры процессора, имени хоста системы и версии ядра\n/get_uptime - o времени работы\n/get_df - о состоянии файловой системы\n\
/get_free - о состоянии оперативной памяти\n/get_mpstat - о производительности системы\n/get_w - о работающих в данной системе пользователях\n/get_auths - последние 10 входов в систему\n\
/get_critical - последние 5 критических событияx\n/get_ps - о запущенных процессах\n/get_ss - об используемых портах\n/get_apt_list - об установленных пакетах\n/get_services - о запущенных сервисах\n\
/get_repl_logs - логи о репликации бд\n/help - справка')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text 
    logger.info("User %s try to find phone in text: %s.", update.message.from_user, user_input)
    phoneNumRegex = re.compile(r'\+?\d{1}?[-\s]?\(?\d{3}?\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}') 
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList: 
        logger.info("%s user's phone not found in text", update.message.from_user)
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    
    context.user_data['numbers'] = phoneNumberList
    phoneNumbers = '' 
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' 
    logger.info("%s user's phone found in text: %s", update.message.from_user, phoneNumbers)    
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Вы хотите сохранить найденные телефоны в базе данных? (yes/no): ')
    return 'addPhoneNumbers'

def addPhoneNumbers(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'yes':
        phoneNumbers = context.user_data.get('numbers', [])
        connection = None
        try:
            connection = psycopg2.connect(user=user_db,
                                    password=pass_db,
                                    host=db_host,
                                    port=port_db, 
                                    database=database)

            cursor = connection.cursor()
            for row in phoneNumbers:
                cursor.execute("INSERT INTO phone_num (numbers) VALUES (%s)", (row,))
                connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Номера успешно дабавлены в БД!')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('При загрузке данных произошла ошибка. Повторите запрос позже')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    return ConversationHandler.END

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почт(ы): ')
    return 'find_email'

def findEmail(update: Update, context):
    user_input = update.message.text
    logger.info("User %s try to find emails in text: %s.", update.message.from_user, user_input)
    emailRegex = re.compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Почты не найдены')
        return ConversationHandler.END
    
    context.user_data['emails'] = emailList
    emailAddr = '' 
    for i in range(len(emailList)):
        emailAddr += f'{i+1}. {emailList[i]}\n' 
    logger.info("%s user's emails found in text: %s", update.message.from_user, emailAddr)    
    update.message.reply_text(emailAddr) 
    update.message.reply_text('Вы хотите сохранить найденные почты в базу данных? (yes/no): ')
    return 'addEmails'

def addEmails(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'yes':
        emails = context.user_data.get('emails', [])
        connection = None
        try:
            connection = psycopg2.connect(user=user_db,
                                    password=pass_db,
                                    host=db_host,
                                    port=port_db, 
                                    database=database)

            cursor = connection.cursor()
            for row in emails:
                cursor.execute("INSERT INTO emails (email) VALUES (%s)", (row,))
                connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Почта(ы) успешно дабавлена(ы) в БД!')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('При загрузке данных произошла ошибка. Повторите запрос позже')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    return ConversationHandler.END 


def checkPassCommand(update: Update, context):
    update.message.reply_text('Введите свой пароль для проверки его сложности: ')
    return 'checkPassword'

def checkPassword(update: Update, context):
    password = update.message.text
    logger.info("User %s print his password: %s.", update.message.from_user, password)
    passRegex = re.compile(r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*()]).{8,}')
    passList = passRegex.findall(password)

    if not passList:
        update.message.reply_text('Пароль слабый')
        logger.info("%s user's password is simle: %s", update.message.from_user, password)
        return ConversationHandler.END
    else:
        update.message.reply_text('Пароль сильный')
        logger.info("%s user's password is hard: %s", update.message.from_user, password)
        return ConversationHandler.END
    

def get_release(update: Update, context):
    logger.info("User %s want to see system realese.", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /etc/*-release')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_uname(update: Update, context):
    logger.info("User %s want to see lscpu", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('lscpu')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_uptime(update: Update, context):
    logger.info("User %s want to see uptime", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_df(update: Update, context):
    logger.info("User %s want to see df", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_free(update: Update, context):
    logger.info("User %s want to see free", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_mpstat(update: Update, context):
    logger.info("User %s want to see system realese.", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_w(update: Update, context):
    logger.info("User %s want to see w", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_auths(update: Update, context):
    logger.info("User %s want to see 10 auths", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_critical(update: Update, context):
    logger.info("User %s want to see critical errors", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep -i -e fail -e error -e corrupt /var/log/syslog | tail -n 5')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_ps(update: Update, context):
    logger.info("User %s want to see ps", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_ss(update: Update, context):
    logger.info("User %s want to see ss", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss -tulpin')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_apt_list_command(update: Update, context):
    update.message.reply_text('Введите название пакета или ключевое слово all, если хотите увидеть полный список установленных пакетов: ')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    pack = update.message.text
    logger.info("User %s want to see apt list", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    if pack == all:
        stdin, stdout, stderr = client.exec_command('apt list --installed | grep 30')
    else:
        stdin, stdout, stderr = client.exec_command('apt list --installed | grep '+ pack)
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_services(update: Update, context):
    logger.info("User %s want to see services", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type service --state running')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_repl_logs(update: Update, context):
    logger.info("User %s want to see repl_logs", update.message.from_user)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('docker cp db_image:/var/log/postgresql/postgres.log . && cat postgres.log | grep repl')
    data = stdout.read()
    logger.info("%s", data)
    logger.error("%s", stderr.read())
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return ConversationHandler.END

def get_emails(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=user_db,
                                    password=pass_db,
                                    host=db_host,
                                    port=port_db, 
                                    database=database)

        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        data = cursor.fetchall()
        emailData = ''
        for i in range(len(data)):
            d = [*data[i]]
            emailData += f'{i+1}. {d[0]}\n' 
        update.message.reply_text(emailData)  
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    return ConversationHandler.END

def get_phone_numbers(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=user_db,
                                    password=pass_db,
                                    host=db_host,
                                    port=port_db, 
                                    database=database)

        cursor = connection.cursor()
        cursor.execute("SELECT numbers FROM phone_num;")
        data = cursor.fetchall()
        PhoneData = ''
        for i in range(len(data)):
            d = [*data[i]]
            PhoneData += f'{i+1}. {d[0]}\n' 
        update.message.reply_text(PhoneData)  
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    return ConversationHandler.END
        
def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
   
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'addPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, addPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'addEmails': [MessageHandler(Filters.text & ~Filters.command, addEmails)],
        },
        fallbacks=[]
    )

    convHandlerCheckPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPassCommand)],
        states={
            'checkPassword': [MessageHandler(Filters.text & ~Filters.command, checkPassword)],
        },
        fallbacks=[]
    )

    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )



		
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerCheckPass)
    dp.add_handler(convHandlerAptList)
		
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
