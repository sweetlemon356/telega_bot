from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
import json_work
from collections import defaultdict

user_data = defaultdict()

FILEPATH = "english.json"

TOKEN = '1799668459:AAEXL4NlxnDWPaDS3q-gKA-5TBikQlQgINc'
REC = range(1)
SHOW = range(1)
TEST = range(1)

keyboard_menu = [["/make_case", "/show_case"], ["/show_my_cases", "/show_all_cases"], ["/close"]]

menu_markup = ReplyKeyboardMarkup(keyboard_menu, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text(
        "Привет! У меня есть несколько функций.\n Ты можешь проходить тесты, созданные другими пользователями, "
        "либо создать свой тест. Обратите внимание на команды на клавиатуре", reply_markup=menu_markup)


def show_case(update, context):
    update.message.reply_text("Введите имя нужного вам кейса")
    return SHOW


def open_menu_keyboard(update, context):
    update.message.reply_text("закрыл", reply_markup=menu_markup)


def close_menu_keyboard(update, context):
    update.message.reply_text(reply_markup=False)


def show_by_casename(update, context):
    name = update.message.text
    update.message.reply_text("Ищу ваш кейс...")
    array = json_work.open_and_convert(FILEPATH)
    cases = json_work.search_for_args(array, {"name": name})
    # здесь будет функция сортровки.
    case = cases[0]
    if case:
        update.message.reply_text(f"Вот ваш кейс: {case['name']}")
        words_n_answers = "\n".join([f"{word} - {answer}" for word, answer in case['words_through'].items()])
        update.message.reply_text(words_n_answers)
    else:
        update.message.reply_text("Увы, я ничего не нашли")
    return ConversationHandler.END


def show_my_cases(update, context):
    userid = update.message.from_user.id

    array = json_work.open_and_convert(FILEPATH)
    cases = json_work.search_for_args(array, {"userid": userid})
    res = '\n'.join([f"{case['name']}({case['len']})" for case in cases])
    update.message.reply_text(res)


def show_all_cases(update, context):
    cases = json_work.open_and_convert(FILEPATH)
    res = '\n'.join([f"{case['name']}({case['len']})" for case in cases])
    update.message.reply_text(res)


def do_test(update, context):
    name = context.args[0]
    userid = update.message.from_user.id

    array = json_work.open_and_convert(FILEPATH)
    case = json_work.search_for_args(array, {"name": name})[0]
    words = [el for el in case["words_through"].keys()]
    answers = [el for el in case["reversed"].keys()]

    # для обратного теста
    """if context.args[1]:
        words, answers = answers, words"""

    user_data[userid] = {"name": name, "words": words, "answers": answers}
    words = '\n'.join(words)
    update.message.reply_text(f"{words}\nдалее введите перевод слов через пробел")
    return TEST


def check_answers(update, context):
    userid = update.message.from_user.id
    answers = user_data[userid]["answers"]
    user_answers = update.message.text.split()
    print(answers)
    print(user_answers)
    if len(answers) != len(user_answers):
        update.message.reply_text("Кол-во ответов не совпадает с кол-вом показанных вам слов")
        return ConversationHandler.END
    counter = 0
    maxx = len(answers)
    for i in range(len(answers)):
        if user_answers[i] == answers[i]:
            counter += 1
    update.message.reply_text(f"Ваш результат: {counter}/{maxx}\nСейчас Покажу вам правильные ответы")
    res = '\n'.join([f"{answers[i]}(Вы ответили: {user_answers[i]})" for i in range(maxx)])
    update.message.reply_text(res)
    del user_data[userid]
    return ConversationHandler.END




def make_case(update, context):
    update.message.reply_text("Так, создаем новый кейс..\n"
        "Теперь вы должны сообщить мне название кейса и слова в нём, а также язык.\n"
        "Сделайте всё это в формате 'name.lang.word_1,word_2.answer_1,answer_2'\n"
                              "Пожалуйста сделайте всё правильно)")
    return REC


def rec(update, context):
    update.message.reply_text('Обрабатываю...')
    user_id = update.message.from_user.id
    #print(update.message.from_user.username)
    text = update.message.text
    array = text.split('.')
    array = [el.split(',') for el in array]
    print(array)
    name, lang, words, answers = array[0][0], array[1][0], array[2], array[3]
    json_work.add_d(lang, [lang, name, user_id, words, answers])
    update.message.reply_text('Кейс создан.')
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text("Привет, я бот для изучения иностранных слов, для начала работы введите /start")



def stop(update, context):
    update.message.reply_text("остановлено")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    make_file_conv = ConversationHandler(
        entry_points=[CommandHandler("make_case", make_case)],

        states={REC: [MessageHandler(Filters.text, rec)]},

        fallbacks=[CommandHandler("stop", stop)]
    )

    show_case_conv = ConversationHandler(
        entry_points=[CommandHandler("show_case", show_case)],

        states={SHOW: [MessageHandler(Filters.text, show_by_casename)]},

        fallbacks=[CommandHandler("stop", stop)]
    )

    test_conv = ConversationHandler(
        entry_points=[CommandHandler("do_test", do_test)],

        states={TEST: [MessageHandler(Filters.text, check_answers)]},

        fallbacks=[CommandHandler("stop", stop)]
    )


    dp = updater.dispatcher
    dp.add_handler(make_file_conv)
    dp.add_handler(show_case_conv)
    dp.add_handler(test_conv)
    dp.add_handler(CommandHandler("open_keys", open_menu_keyboard))
    dp.add_handler(CommandHandler("close", close_menu_keyboard))
    dp.add_handler(CommandHandler("do_test", do_test, pass_args=True))
    dp.add_handler(CommandHandler("show_all_cases", show_all_cases))
    dp.add_handler(CommandHandler("show_my_cases", show_my_cases))
    dp.add_handler(CommandHandler("make_case", make_case))
    dp.add_handler(CommandHandler("show_case", show_case))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    updater.start_polling()

    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()