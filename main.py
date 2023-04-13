# Импорты
import requests
import bs4
import random

# Словарик для перевода звуков (Пригодится для создания ссылки на стих)
translate = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
             'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
             'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': '', 'ы': 'y', 'э': '', 'ю': 'yu',
             'я': 'ya'}

# Глобальные словари\списки для дебага и хранения информации в сессии

users = {}
errors = {}
stih = ['']
cant_find = [False]
listen = [False]
end = [0]


# Делает из списка строку, вставляя между элементами сепаратор
def mk_str(lst, sep):
    output = ''
    # Проходимся по индексам списка
    for i in range(len(lst)):
        # Добавляем в строку элемент списка
        output += lst[i]
        # Проверка на конец списка
        if i != len(lst) - 1:
            output += sep
    return output


# Переводит текст, введённый пользователем в ссылку
def trans(text_link):
    output = ''
    # Перевод спомощью словаря translate
    for i in text_link:
        if i in translate.keys():
            output += translate[i]
        elif i == ' ':
            output += i

    # Убираем лишние пробелы
    text_link = output
    text_link = text_link.split()
    for i in text_link:
        i = i.replace(' ', '')
    # Переводим в строку
    output = mk_str(text_link, '-')
    # Проверка на ссылку (На сайте название и ссылка отличаются)
    if f"https://rustih.ru/{output}/" == 'https://rustih.ru/aleksandr-pushkin-u-lukomorya-dub-zelenyj/' or \
            f"https://rustih.ru/{output}/" == 'https://rustih.ru/aleksandr-pushkin-u-lukomorya-dub-zelyonyj/':
        return f'https://rustih.ru/aleksandr-pushkin-v-lukomorya-dub-zelenyj-iz-ruslan-i-lyudmila/'
    else:
        return f"https://rustih.ru/{output}/"


# По ссылке достаёт текст стиха и очищает от "Шелухи"
def parse(text_link):
    # Тут парсинг
    response = requests.get(trans(text_link))
    page = bs4.BeautifulSoup(response.content, 'html.parser')
    textt = page.find('div', 'entry-content poem-text').text
    text = ''
    # Проверяем на "Шелуху"
    for i in range(len(textt)):
        if i + 5 < len(textt):
            if textt[i] + textt[i + 1] + textt[i + 2] + textt[i + 3] + textt[i + 4] + textt[i + 5] == 'Анализ' or \
                    textt[i] + textt[i + 1] + textt[i + 2] + textt[i + 3] + textt[i + 4] + textt[i + 5] == "Читать":
                text = textt[:i]
                break
            else:
                text = textt
    return text


# Основная функция
def handler(event, context):
    # кортежи для вариативности ответов
    continues = ('Давай дальше!', 'Записала!', 'Запомнила!', 'Хорошо!', 'Диктуй дальше!', 'Отлично, продолжай!')
    start = (
    'поехали', 'погнали', 'давай', 'начать', 'начнем', 'начнём', 'гоу', 'го', 'стартуем', 'полетели', 'приступим',
    'старт')
    sogl = ('да', 'погнали', 'давай', 'именно', 'конечно')

    lucky = ('Молодец!', 'Отлично!', 'У тебя отлично получается!', 'Супер!', 'Так держать!', 'Ты такой молодец!',
             'Хорошо справляешься!', 'Все правильно!')
    unlucky = (
    'Ой-ой! Давай попробуем еще раз!', 'Почти! Давай повторим!', 'Давай-ка еще разок!', 'Давай-ка исправим ошибки!')
    otkaz = ('нет', 'нет, не он', 'это не этот стих', 'нет, другой', 'другой', 'неа')

    # Имитация response
    response = {
        "version": event["version"],
        "session": event["session"],
        "id": event["session"]["message_id"],
        "buttons": [],
        "response": {
            "end_session": False
        }
    }
    # Основная логика
    if event['session']['message_id'] - len(errors) == 0:
        response["response"][
            "text"] = "Привет, хочешь выучить стих? Я помогу с этим! Чтобы узнать, как пользоваться навыком, скажи помощь! Чтобы начать, скажи начать."
        response['response']['tts'] = response['response']['text']
        response["response"]["buttons"] = [{
            "title": "начать",
            "hide": True
        },
            {
                "title": "помощь",
                "hide": True
            }]
    elif event['session']['message_id'] - len(errors) == 1:
        if event['request']['original_utterance'].lower() in ['помощь']:
            response["response"][
                "text"] = 'Для того, чтобы начать, назовите имя и фамилию автора, затем название произведения!\nНапример: Александр Пушкин - У лукоморья дуб зелёный.'
            response['response']['tts'] = response['response']['text']
        elif event['request']['original_utterance'].lower() in start:
            response["response"]["text"] = 'Хорошо, теперь введите имя и фамилию автора, а затем название произведения.'
            response['response']['tts'] = response['response']['text']
        elif event['request']['original_utterance'].lower() in ['что ты умеешь']:
            response["response"][
                "text"] = 'Я могу помочь выучить твой стих! Просто назови мне имя и фамилию автора, а затем название произведения!'
            response['response']['tts'] = response['response']['text']
        else:
            errors[str(len(errors) + 1)] = 'Пользователь ввёл не да и не нет Ввод: ' + event['request'][
                'original_utterance']
            response["response"]["text"] = 'Я вас не поняла!'
            response['response']['tts'] = response['response']['text']

    elif event['session']['message_id'] - len(errors) == 2:
        text_link = event['request']['original_utterance'].lower()
        if event['request']['original_utterance'].lower() in ['помощь']:
            response["response"]["text"] = 'Введите пожалуйста имя и фамилию автора, а затем название стихотворения'
            response['response']['tts'] = response['response']['text']
            errors[len(errors) + 1] = 'Помощь'
        elif event['request']['original_utterance'].lower() in ['что ты умеешь']:
            response["response"][
                "text"] = 'Я могу помочь выучить твой стих! Просто назови мне имя и фамилию автора, а затем название произведения! Теперь продолжайте'
            response['response']['tts'] = response['response']['text']
            errors[len(errors) + 1] = 'Что ты умеешь?'
        else:
            users[event['session']['user_id']] = text_link
            try:
                response["response"]["text"] = 'Этот стих? ' + '\n' + razdel(parse(text_link), 2) + '\n'
                response['response']['tts'] = response['response']['text']
                response["response"]["buttons"] = [{
                    "title": "Да",
                    "hide": True
                },
                    {
                        "title": "Нет",
                        "hide": True
                    }]
            except:
                response["response"]["text"] = 'Извините, возникла ошибка, пожалуйста, введите текст заново!'
                errors[str(len(errors) + 1)] = 'Не смог запарсить Ввод: ' + event['request'][
                    'original_utterance']
                response['response']['tts'] = response['response']['text']
    elif event['session']['message_id'] - len(errors) == 3:
        if event['request']['original_utterance'].lower() in ['помощь']:
            response["response"]["text"] = 'Ответь да, если имел ввиду этот стих\n' + razdel(
                parse(users[event['session']['user_id']]), 2) + '\n\nИли нет, если другой'
            response['response']['tts'] = response['response']['text']
            response["response"]["buttons"] = [{
                "title": "Да",
                "hide": True
            },
                {
                    "title": "Нет",
                    "hide": True
                }]
            errors[len(errors) + 1] = 'Помощь'
        elif event['request']['original_utterance'].lower() in ['что ты умеешь']:
            response["response"][
                "text"] = 'Я могу помочь выучить твой стих! Просто назови мне имя и фамилию автора, а затем название произведения! Теперь продолжайте'
            response['response']['tts'] = response['response']['text']
            errors[len(errors) + 1] = 'Что ты умеешь?'
        else:
            if cant_find[0]:
                if len(stih[0]) <= 0:
                    stih[0] += '\n'
                line = event['request']['original_utterance'].lower()
                response["response"]["text"] = continues[random.randint(0, len(continues) - 1)]
                response['response']['tts'] = response['response']['text']
                if line.lower() != 'всё':
                    stih[0] += line + '\n'
                    errors[str(len(errors) + 1)] = 'Пользователь вводит стих'
                else:
                    response["response"][
                        "text"] = 'Я всё запомнила и готова вам помогать, повторяйте за мной\n' + razdel(stih[0],
                                                                                                         2) + '\n'
                    response['response']['tts'] = response['response']['text']

            elif event['request']['original_utterance'].lower() == 'ещё раз':
                response["response"]["text"] = 'Хорошо, слушаю!'
                response["response"]["buttons"] = [{
                    "title": "Ещё раз",
                    "hide": True
                }]
                errors[str(len(errors) + 1)] = 'Не смог найти стих'
                errors[str(len(errors) + 1)] = 'Не смог найти стих'
                response['response']['tts'] = response['response']['text']
            elif event['request']['original_utterance'].lower() == 'всё правильно':
                response["response"][
                    "text"] = 'Тогда, пожалуйста, продиктуйте мне стих по строчкам, когда закончите, скажите всё! Только диктуйте правильно, я слушаю!'
                cant_find[0] = True
                errors[str(len(errors) + 1)] = 'Не смог найти стих'
                response['response']['tts'] = response['response']['text']
            elif event['request']['original_utterance'].lower() in otkaz:
                response["response"][
                    "text"] = 'Проверьте пожалуйста правильность написания и скажите "Ещё раз", если написали не правильно, если вы всё написали правильно, скажите "Всё правильно"'
                errors[str(len(errors) + 1)] = 'Не смог найти стих'
                response['response']['tts'] = response['response']['text']
            elif event['request']['original_utterance'].lower() in sogl:
                response["response"]["text"] = 'Отлично, начинаем учить!' + '\n' + razdel(
                    parse(users[event['session']['user_id']]), event['session']['message_id'] - len(errors)) + '\n'
                response['response']['tts'] = response['response']['text']
                response['response']['buttons'] = [{
                    "title": "Пропустить",
                    "hide": True
                }]
            else:
                response["response"]["text"] = 'Извините, я вас не поняла!'
                errors[str(len(errors) + 1)] = 'Пользователь ввёл не да и не нет Ввод: ' + event['request'][
                    'original_utterance'].lower()
                response['response']['tts'] = response['response']['text']
    else:
        if event['request']['original_utterance'].lower() in ['помощь']:
            response["response"]["text"] = 'Сейчас просто повторяйте за мной'
            response['response']['tts'] = response['response']['text']
            errors[len(errors) + 1] = 'Помощь'
        elif event['request']['original_utterance'].lower() in ['что ты умеешь']:
            response["response"][
                "text"] = 'Я могу помочь выучить твой стих! Просто назови мне имя и фамилию автора, а затем название произведения! Теперь продолжайте'
            response['response']['tts'] = response['response']['text']
            errors[len(errors) + 1] = 'Что ты умеешь?'
        else:
            if not cant_find[0]:
                if event['request']['original_utterance'].lower() in sogl:
                    response["response"]["text"] = 'Тогда, пожалуйста, перезапустите навык!'
                    response['response']['tts'] = response['response']['text']
                    event['session']['end_session'] = True

                elif event['request']['original_utterance'].lower() in otkaz:
                    end[0] = 2
                    response["response"]["text"] = 'Пока-пока жду вас снова!'
                    response['response']['tts'] = response['response']['text']
                    event['session']['end_session'] = True
                else:
                    prev = razdel(parse(users[event['session']['user_id']]),
                                  event['session']['message_id'] - 1 - len(errors))
                    accuracy = check(event['request']['original_utterance'].lower(), prev)
                    response['response']['buttons'] = [{
                        "title": "Пропустить",
                        "hide": True
                    }]
                    if event["request"]["original_utterance"].lower() == "пропустить":
                        next = razdel(parse(users[event['session']['user_id']]),
                                      event['session']['message_id'] - len(errors)) + '\n'
                        if next != '\n':
                            response["response"]["text"] = lucky[random.randint(0,
                                                                                len(lucky) - 1)] + 'Давай дальше!' + '\n' + next
                            response['response']['tts'] = response['response']['text']
                            response['response']['buttons'] = [{
                                "title": "Пропустить",
                                "hide": True
                            }]
                        else:
                            response["response"][
                                "text"] = 'Вы большой молодец,справились с этим произведением! Хотите повторить его снова?'
                            response['response']['tts'] = response['response']['text']
                    else:
                        if accuracy:
                            next = razdel(parse(users[event['session']['user_id']]),
                                          event['session']['message_id'] - len(errors)) + '\n'
                            response['response']['buttons'] = [{
                                "title": "Пропустить",
                                "hide": True
                            }]
                            if next != '\n':
                                response["response"]["text"] = lucky[random.randint(0,
                                                                                    len(lucky) - 1)] + 'Давай дальше!' + '\n' + next
                                response['response']['tts'] = response['response']['text']
                            else:
                                response["response"][
                                    "text"] = 'Вы большой молодец,справились с этим произведением! Хотите повторить его снова?'
                                response['response']['tts'] = response['response']['text']
            else:

                if event['request']['original_utterance'].lower() in sogl:
                    response["response"]["text"] = 'Тогда, пожалуйста, перезапустите навык!'
                    response['response']['tts'] = response['response']['text']
                    event['session']['end_session'] = True

                elif event['request']['original_utterance'].lower() in otkaz:
                    end[0] = 2
                    response["response"]["text"] = 'Пока-пока жду вас снова!'
                    response['response']['tts'] = response['response']['text']
                    event['session']['end_session'] = True
                else:

                    prev = razdel(parse(users[event['session']['user_id']]),
                                  event['session']['message_id'] - 1 - len(errors))
                    accuracy = check(event['request']['original_utterance'].lower(), prev)
                    response['response']['buttons'] = [{
                        "title": "Пропустить",
                        "hide": True
                    }]
                    if event["request"]["original_utterance"].lower() == "пропустить":
                        next = razdel(parse(users[event['session']['user_id']]),
                                      event['session']['message_id'] - len(errors)) + '\n'
                        if next != '\n':
                            response["response"]["text"] = 'Давай дальше!' + '\n' + next
                            response['response']['tts'] = response['response']['text']
                            response['response']['buttons'] = [{
                                "title": "Пропустить",
                                "hide": True
                            }]
                        else:
                            response["response"][
                                "text"] = 'Вы большой молодец,справились с этим произведением! Хотите повторить его снова?'
                            response['response']['tts'] = response['response']['text']
                    else:
                        if accuracy:
                            next = razdel(parse(users[event['session']['user_id']]),
                                          event['session']['message_id'] - len(errors)) + '\n'
                            response['response']['buttons'] = [{
                                "title": "Пропустить",
                                "hide": True
                            }]
                            if next != '\n':
                                response["response"]["text"] = 'Давай дальше!' + '\n' + next
                                response['response']['tts'] = response['response']['text']
                            else:
                                response["response"][
                                    "text"] = 'Вы большой молодец,справились с этим произведением! Хотите повторить его снова?'
                                response['response']['tts'] = response['response']['text']
                        else:
                            # Тут прописываем, если пользователь произнёс не правильно
                            response["response"]["text"] = unlucky[random.randint(0, len(unlucky) - 1)] + '\n' + prev
                            errors[str(len(errors) + 1)] = 'Пользователь не смог повторить за Алисой'
                            response['response']['tts'] = response['response']['text']
    return response


# Проверка на правильность повторения за Алисой
def check(utterance, prev):
    # Русский алфавит
    symbols = ('а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
               'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
               'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
               'э', 'ю', 'я')
    utterance_output = ''
    prev_output = ''
    utterance = utterance.lower()
    prev = prev.lower()
    # Проходимся по строкам, если символ из русского алфавита, то записываем в новую строку
    for i in utterance:
        if i in symbols:
            if i == 'ё':
                utterance_output += 'е'
            else:
                utterance_output += i
    for i in prev:
        if i in symbols:
            if i == 'ё':
                prev_output += 'е'
            else:
                prev_output += i
    # Если ответ равен 2 строкам стиха, то возвращаем True иначе False
    if utterance_output == prev_output:
        return True
    else:
        return False


# Выводит по 2 строчки
def razdel(text, id):
    c = 0
    output = ''
    temp = 0
    # Просчитываем c
    if id == 2:
        c = 0
    else:
        c -= 2 * (id - 3)
    # Если встречаем два знака \n, то запоминаем и выводим
    for i in range(len(text)):
        if text[i] == '\n':
            if c == 0:
                temp = i
            if c == 2:
                output = text[temp:i]
                break
            c += 1

    return output

