import requests
import bs4
import random

translate = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
             'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
             'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': '', 'ы': 'y', 'э': '', 'ю': 'yu',
             'я': 'ya'}


def mk_str(lst, sep):
    output = ''
    for i in range(len(lst)):
        output += lst[i]
        if i != len(lst) - 1:
            output += sep
    return output


def trans(text_link):
    output = ''
    for i in text_link.lower():
        if i in translate:
            output += translate[i]
        elif i == ' ' or i == '-':
            output += ' '
    words = output.split()
    link_part = "-".join(words)
    if "lukomor" in link_part:
        return 'https://rustih.ru/aleksandr-pushkin-v-lukomorya-dub-zelenyj-iz-ruslan-i-lyudmila/'
    return f"https://rustih.ru/{link_part}/"


def parse(text_link):
    url = trans(text_link)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""
        page = bs4.BeautifulSoup(response.content, 'html.parser')
        container = (
                page.find('div', class_='poem-text') or
                page.find('div', class_='entry-content') or
                page.find('article')
        )
        if not container:
            return ""
        full_text = container.get_text(separator='\n', strip=True)
        stop_words = ["Анализ", "Читать", "Слушать", "Другие", "Поделиться"]
        clean_text = full_text
        for word in stop_words:
            idx = clean_text.find(word)
            if idx != -1:
                clean_text = clean_text[:idx]
        return clean_text.strip()
    except Exception as e:
        return ""


def check(utterance, prev):
    symbols = ('а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и',
               'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
               'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь',
               'э', 'ю', 'я')
    utterance_output = ''
    prev_output = ''
    utterance = utterance.lower()
    prev = prev.lower()
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
    if utterance_output == prev_output:
        return True
    else:
        return False


def razdel(text, step):
    if not text:
        return ""
    lines = text.split('\n')
    # Очищаем от пустых строк и лишних пробелов
    filtered_lines = [line.strip() for line in lines if line.strip()]
    offset = 4
    start_index = offset + (step - 1) * 2
    if start_index >= len(filtered_lines):
        return ""  # Стих закончился
    result_slice = filtered_lines[start_index: start_index + 2]
    return "\n".join(result_slice)


def handler(event, context):
    # создание session state
    state = event.get('state', {}).get('session', {})
    if event.get('session', {}).get('new') or not state:
        state = {
            'stih': '',
            'study_step': 1,
            'errors': {},
            'users': {},
            'cant_find': False
        }
    errors = state['errors']
    users = state['users']
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
    response = {
        "version": event["version"],
        "session": event["session"],
        "response": {"end_session": False},
        "session_state": state
    }
    logic_step = event['session']['message_id'] - len(errors)
    if logic_step == 0:
        response["response"][
            "text"] = "Привет, хочешь выучить стих? Я помогу с этим! Чтобы узнать, как пользоваться навыком, скажи помощь! Чтобы начать, скажи начать."
        response["response"]["buttons"] = [{"title": "Начать", "hide": True}, {"title": "Помощь", "hide": True}]
    elif logic_step == 1:
        utterance = event['request']['original_utterance'].lower()
        if utterance == 'помощь':
            response["response"][
                "text"] = 'Для того, чтобы начать, назовите имя и фамилию автора, затем название произведения!\nНапример: Александр Пушкин - У лукоморья дуб зелёный.'
        elif utterance in start:
            response["response"]["text"] = 'Хорошо, теперь введите имя и фамилию автора, а затем название произведения.'
        elif utterance == 'что ты умеешь?':
            response["response"]["text"] = 'Я могу помочь выучить твой стих! Просто назови мне автора и название!'
        else:
            errors[str(len(errors) + 1)] = 'Ошибка шага 1'
            response["response"]["text"] = 'Я вас не поняла!'
    elif logic_step == 2:
        text_link = event['request']['original_utterance'].lower()
        if text_link == 'помощь':
            response["response"]["text"] = 'Введите пожалуйста имя и фамилию автора, а затем название стихотворения'
            errors[str(len(errors) + 1)] = 'Помощь'
        else:
            users[event['session']['user_id']] = text_link
            try:
                poem_text = parse(text_link)
                if poem_text:
                    state['stih'] = poem_text  # СОХРАНЯЕМ ТЕКСТ В STATE
                    lines_to_show = razdel(poem_text, 1)
                    response["response"]["text"] = f"Нашла! Этот стих?\n{lines_to_show}"
                    response["response"]["buttons"] = [{"title": "Да", "hide": True}, {"title": "Нет", "hide": True}]
                else:
                    response["response"]["text"] = "Не нашла такой стих. Попробуй еще раз."
            except:
                response["response"]["text"] = 'Извините, возникла ошибка, пожалуйста, введите текст заново!'
                errors[str(len(errors) + 1)] = 'Ошибка парсинга'
    elif logic_step == 3:
        utterance = event['request']['original_utterance'].lower()
        poem = state['stih']  # Достаем стих из памяти
        if utterance == 'помощь':
            response["response"]["text"] = 'Ответь да, если имел ввиду этот стих\n' + razdel(poem, 2)
            errors[str(len(errors) + 1)] = 'Помощь'
        else:
            if state['cant_find']:
                if utterance != 'всё':
                    state['stih'] += utterance + '\n'
                    response["response"]["text"] = random.choice(continues)
                    errors[str(len(errors) + 1)] = 'Ручной ввод'
                else:
                    response["response"]["text"] = 'Я всё запомнила! Повторяйте:\n' + razdel(state['stih'], 2)
            elif utterance == 'ещё раз':
                response["response"]["text"] = 'Хорошо, слушаю!'
                errors[str(len(errors) + 2)] = 'Повтор поиска'
            elif utterance == 'всё правильно':
                response["response"]["text"] = 'Тогда продиктуйте мне стих по строчкам, а в конце скажите "всё"!'
                state['cant_find'] = True
                errors[str(len(errors) + 1)] = 'Переход на ручной ввод'
            elif utterance in otkaz:
                response["response"][
                    "text"] = 'Проверьте название и скажите "Ещё раз" или "Всё правильно" для ручного ввода.'
                errors[str(len(errors) + 1)] = 'Отказ'
            utterance = event['request']['original_utterance'].lower()
            if utterance in sogl:
                poem = state.get('stih', '')  # Достаем из памяти
                state['study_step'] = 1
                lines = razdel(poem, 1)
                res_buttons = [{"title": "Пропустить", "hide": True}]
                response["response"]["text"] = "Отлично, начинаем учить!\n" + lines
            else:
                response["response"]["text"] = 'Извините, я вас не поняла!'
                errors[str(len(errors) + 1)] = 'Непонятный ввод'
    else:
        poem = state.get('stih', '')
        current_step = state.get('study_step', 1)
        expected_lines = razdel(poem, current_step)
        if utterance == "пропустить" or check(utterance, expected_lines):
            next_step = current_step + 1
            next_lines = razdel(poem, next_step)
            if next_lines:
                state['study_step'] = next_step
                res_text = random.choice(lucky) + ' Давай дальше!\n' + next_lines
            else:
                res_text = 'Вы молодец! Стих закончился.'
                state['study_step'] = 1
        else:
            res_text = random.choice(unlucky) + '\n' + expected_lines
        res_buttons = [{"title": "Пропустить", "hide": True}]
    return {
        "version": event["version"],
        "session": event["session"],
        "response": {
            "text": res_text,
            "end_session": False,
            "buttons": res_buttons
        },
        "session_state": state
    }
