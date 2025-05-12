import logging
import random
import asyncio

import sqlite3
from sqlalchemy import func

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message, PollAnswer
from aiogram.enums import ParseMode
from data.users import check_password_hash

import matplotlib.pyplot as plt
from io import BytesIO

from config import BOT_TOKEN
from data import db_session
from data.questions import Questions
from data.users import Users


logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_states = {}
conn = sqlite3.connect(f'db/1234')
cursor = conn.cursor()


stickers_right = ['CAACAgIAAxkBAAEOZsloFPIFk8BSkb3Qx3ubxJKwEGLeVwAC_gADVp29CtoEYTAu-df_NgQ',
                 'CAACAgIAAxkBAAEOZstoFPJE--WKRJTSGAi10RDqOHu7VgACLgEAAvcCyA89lj6kwiWnGjYE',
                 'CAACAgIAAxkBAAEOZs1oFPJy_cVPJxHrkKsFeWnSqeCwMgACoAAD9wLID8NHHQGgm8AaNgQ',
                 'CAACAgIAAxkBAAEOZtloFPVbt3eAmQABtW1L-2hqm3tdIVIAAg8PAAJ7YNBL2E7KMnD7CuI2BA',
                 'CAACAgIAAxkBAAEOZvRoFRxB4Mj7h1-2MusjtSPTeuIw1wACFQADwDZPE81WpjthnmTnNgQ',
                 'CAACAgIAAxkBAAEOZvZoFRxziYvkxMm501H7sa-mr4RAVwACZAADWbv8JToS9CchlsxoNgQ',
                 'CAACAgIAAxkBAAEOZvhoFRy8YflHVwWwXc6hwPSLheqUAwAC9wAD9wLID9CX3j-K0TwONgQ',
                 'CAACAgIAAxkBAAEOZwRoFR1tOTANvBBglbxwlg7x8kMd1gACcgUAAj-VzAoR4VZdHmW_cDYE',
                 'CAACAgIAAxkBAAEObtloHLMpoogiBkAp9ybQjG7lYXj3XgACTQADJHFiGj9If4Mjut6dNgQ',
                 'CAACAgIAAxkBAAEObuBoHLNho7bgCTn6ftNqYaALlf2meAAC6w4AAqwaWUh7Bdoy6pPI_TYE',
                 'CAACAgIAAxkBAAEObsdoHLJI13c8hMY6DhWECJPYNd0U0AACDW0AAhxuyUlF4LqIJmqJeDYE',
                 'CAACAgQAAxkBAAEObsloHLJoxP-xlkUnnGndIBp1fZv_8wAClxcAAlNTOFP5By2Mihj_oTYE',
                  ]

stickers_bad = ['CAACAgIAAxkBAAEOZs9oFPQprBT87uGboy3ts2_MbVedtwAC8wADVp29Cmob68TH-pb-NgQ',
                'CAACAgIAAxkBAAEOZtFoFPQyxARfUsaJFbFCSIj3o5zz-gAC9QADVp29Cq5uEBf1pScoNgQ',
                'CAACAgIAAxkBAAEOZtNoFPRF7eGR2sov0Tt6iQvZvm-KuQACpwAD9wLID8uYNkDdR2BBNgQ',
                'CAACAgIAAxkBAAEOZtVoFPRcr0ajRtjELXFWfHReLPsl-wACJwEAAvcCyA_vR4RKHXMGLDYE',
                'CAACAgIAAxkBAAEOZtdoFPRuGnjDmnzyB_zmXWacrNcI2AAC_BIAAsXS4EiIWp-Qdhf1nzYE',
                'CAACAgIAAxkBAAEOZvxoFRzSjfJXD7WJBqXMKgFQo42WkwACDwwAAuKOOUotFzfMTUK3UDYE',
                'CAACAgIAAxkBAAEOZv5oFRzjt0oJ6JFwuSXudxcJvSfFowACYQADWbv8JUh0znlMNhLJNgQ',
                'CAACAgIAAxkBAAEObuJoHLNv0OFl7YD_m3tq1cBtlTNIfgAClw0AAm-K8EtwIBpzwV7QdDYE',
                'CAACAgIAAxkBAAEObs9oHLKsKKumL_eXPIzfE3gUSg7diwAChw0AAm2hmEuryN-j1WLeMTYE',
                'CAACAgIAAxkBAAEObtNoHLL-HIJduITnM7LGvpy1qhLO1wACvQAD9wLIDx2aqkRb2DeaNgQ',
                'CAACAgIAAxkBAAEObtVoHLMT2GcaPI1ltLpY7jBU6PoSeAACDg0AAlkAAZhL3larpAvx_n82BA',
                'CAACAgIAAxkBAAEObtdoHLMXZNT6sTiYlLjieIOcRYAY4wACvAsAAv0XmUtFBR2JSwp5RzYE',
                'CAACAgIAAxkBAAEObsVoHLJEgHpmMMNf6d4aAbRpM_hHSQACCmkAAhtgyUkyw03ptqmO3DYE'
                ]


class Form(StatesGroup):
    start = State()
    auth_login = State()
    auth_password = State()
    guest_mode = State()
    main_menu = State()
    subject_selection = State()
    topic_selection = State()
    answering = State()
    question_mode = State()
    quiz_subject_selection = State()
    quiz_topic_selection = State()
    quiz_grade_selection = State()
    quiz_question_mode = State()
    quiz_answering = State()


# 🟥 блок клавиатур
async def branch_selection_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Авторизация 🔐", callback_data="auth"),
        InlineKeyboardButton(text="Гостевой режим 👤", callback_data="guest"),
        InlineKeyboardButton(text="Наш сайт 🌐", url="http://127.0.0.1:5000"),
    )
    builder.adjust(1)
    return builder.as_markup()


async def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Решать 🧠", callback_data="start_test"),
    InlineKeyboardButton(text="◀ Вернуться", callback_data="return_start")
    )
    builder.adjust(1)
    return builder.as_markup()


# 🟥 блок проверки кнопочек
@dp.callback_query(F.data == "back")
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    idishnik = data.get("idishnik")

    if current_state == Form.topic_selection:
        await state.set_state(Form.subject_selection)
        builder = InlineKeyboardBuilder()

        db_session.global_init(f"db/Quizi.db")
        db_sess = db_session.create_session()
        b = []
        for i in db_sess.query(Questions.subject).filter(Questions.user_id == idishnik).all():
            if i not in b:
                b.append(i)

        print(b)

        for item in b:
            builder.add(InlineKeyboardButton(
                text=item[0],
                callback_data=f"subj_{item[0]}"
            ))
        builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))

        builder.adjust(2)

        await callback.message.edit_text(
            "📚 Выберите предмет:",
            reply_markup=builder.as_markup()
        )
        await callback.answer()

    elif current_state == Form.subject_selection:
        await state.set_state(Form.main_menu)
        await callback.message.edit_text(
            "🏠 Главное меню:",
            reply_markup=await main_menu_kb()
        )

    await callback.answer()


@dp.callback_query(F.data == "return_to_menu")
async def return_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.main_menu)
    await callback.message.answer(
        "🏠 Главное меню:",
        reply_markup=await main_menu_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "return_start")
async def return_to_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.start)
    await callback.message.edit_text(
        "Выберите режим:",
        reply_markup=await branch_selection_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "return_quiz_home")
async def return_quiz_home(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.guest_mode)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="В начало 🏠", callback_data="return_start"))
    builder.add(InlineKeyboardButton(text="Решать 🧠", callback_data="go"))
    builder.adjust(1)
    await callback.message.edit_text(
        "Главное меню 🏠:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.callback_query(Form.main_menu, F.data == "about")
async def about_bot(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "О боте:\nЭто учебный бот",
        reply_markup=await main_menu_kb()
    )
    await callback.answer()



#🟥 блок отправки и проверки
# Функция для отправки вопросов (для авторизованных пользователей)
async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current = data['current_question']
    question = data['question']
    cnt = data['quest_lst']
    vernyx = data['correct_answers']
    builder = InlineKeyboardBuilder()

    if current >= cnt:
        builder.add(InlineKeyboardButton(text="В главное меню 🏠", callback_data="return_to_menu"))
        builder.add(InlineKeyboardButton(text="Результаты", callback_data="results"))

        builder.adjust(2)

        await message.answer('Тест завершён 🎉',
                             reply_markup=builder.as_markup())
        return
    else:
        await message.answer(question)
        await state.set_state(Form.answering)


# Функция для отправки вопросов викторины
async def send_quiz_question(chat_id: int, question_data: dict):
    options = question_data["options"]
    correct_option_id = question_data["correct_option_id"]
    explanation = question_data["explanation"]
    question = question_data["question"]
    builder = InlineKeyboardBuilder()

    await bot.send_poll(
        chat_id=chat_id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False,
        explanation=explanation
    )
    builder.add(InlineKeyboardButton(text="Стоп 🟥", callback_data="return_quiz_home"))
    await bot.send_message(chat_id, 'Закончить:', reply_markup=builder.as_markup())


@dp.message(Form.answering)
async def handle_answer(message: types.Message, state: FSMContext):
    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()
    data = await state.get_data()
    question = data['question']
    answer = data['answer'].lower()
    current = data['current_question']
    idishnik = data.get("idishnik")
    subject = data.get("current_subject")
    topic = data.get("topic")

    user_answer = message.text.lower()

    if user_answer == answer:
        await message.answer_sticker(sticker=random.choice(stickers_right))
        await state.update_data(correct_answers=data['correct_answers'] + 1)
    else:
        await message.answer_sticker(sticker=random.choice(stickers_bad))
        await message.answer(
            f"Неправильно: правильный ответ ||{answer}||",
            parse_mode="MarkdownV2"
        )

    await state.update_data(current_question=current + 1)
    random_question = (db_sess.query(Questions.questions, Questions.answers)
                       .filter(Questions.user_id == idishnik, Questions.subject == subject,
                               Questions.topic == topic).order_by(func.random()).limit(1).first())

    await state.update_data(question=random_question[0], answer=random_question[1])
    await send_question(message, state)



@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext):
    user_id = poll_answer.user.id
    data = await state.get_data()
    quiz_questions = data.get("quiz_questions")
    quiz_current_index = data.get("quiz_current_index")
    quiz_score = data.get("quiz_score")
    builder = InlineKeyboardBuilder()

    if quiz_questions is None or quiz_current_index is None:
        return

    current_question = quiz_questions[quiz_current_index]
    correct_option_id = current_question["correct_option_id"]

    # Проверка правильности ответа
    if poll_answer.option_ids[0] == correct_option_id:
        quiz_score += 1
        await bot.send_sticker(user_id, sticker=random.choice(stickers_right))
    else:
        await bot.send_sticker(user_id, sticker=random.choice(stickers_bad))

    # Переход к следующему вопросу
    quiz_current_index += 1
    if quiz_current_index < len(quiz_questions):
        next_question = quiz_questions[quiz_current_index]
        await send_quiz_question(user_id, next_question)
        await state.update_data(quiz_current_index=quiz_current_index, quiz_score=quiz_score)
    else:
        # Завершение викторины
        await bot.send_message(user_id, f"Викторина окончена! Ваш счёт: {quiz_score} из {len(quiz_questions)}")
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="В начало 🏠", callback_data="return_quiz_home"))
        await bot.send_message(user_id,
                               "Выберите действие:",
                               reply_markup=builder.as_markup()
                               )
        #await state.clear()


@dp.callback_query(F.data == "results")
async def results(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cnt = data['quest_lst']
    vernyx = data['correct_answers']
    labels = ['Верных', 'Неверных']
    sizes = [vernyx, cnt - vernyx]
    colors = ['#34C924', '#ff001f']

    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        shadow=False,
        explode=(0, 0)
    )
    plt.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()

    chart_image = BufferedInputFile(buffer.getvalue(), filename="pie_chart.png")
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="В главное меню 🏠", callback_data="return_to_menu"))

    await callback.message.answer_photo(chart_image, caption="Результаты:", reply_markup=builder.as_markup())
    await callback.answer()



#🟥 старт и авториз. ветка

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.start)
    await message.answer(
        "Добро пожаловать! Выберите режим:",
        reply_markup=await branch_selection_kb()
    )


@dp.callback_query(Form.start, F.data.in_(["auth", "guest"]))
async def select_branch(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_auth = data.get("is_auth")
    if callback.data == "auth":
        if is_auth:
            await state.set_state(Form.main_menu)
            await callback.message.answer(
                "🏠 Главное меню:",
                reply_markup=await main_menu_kb()
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="В начало 🏠", callback_data="return_start"))
            await state.set_state(Form.auth_login)
            await callback.message.edit_text("👤 Введите ваш логин:", reply_markup=builder.as_markup())
    else:
        await state.set_state(Form.guest_mode)
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="В начало 🏠", callback_data="return_start"))
        builder.add(InlineKeyboardButton(text="Решать 🧠", callback_data="go"))
        builder.adjust(1)
        await callback.message.edit_text(
            "Гостевой режим",
            reply_markup=builder.as_markup()
        )
    await callback.answer()


@dp.message(Form.auth_login)
async def process_login(message: types.Message, state: FSMContext):
    user_login = message.text.strip()
    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()
    flag = False

    logins = db_sess.query(Users.id, Users.login).all()
    for i in logins:
        if i[1] == user_login.lower():
            flag = True
            await state.update_data(idishnik=i[0])
            await state.set_state(Form.auth_password)

    if flag:
        await state.set_state(Form.auth_password)
        await state.update_data(login=user_login)
        await message.answer(
            f"Введите пароль 🔑"
        )
    else:
        await message.answer("❌ Неверный логин. Попробуйте еще раз:")


@dp.message(Form.auth_password)
async def process_password(message: types.Message, state: FSMContext):
    user_password = message.text
    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()
    data = await state.get_data()
    idishnik = data.get("idishnik")
    login = data.get("login")
    flag = False

    passwords = db_sess.query(Users.password).filter(Users.id == idishnik).all()
    for i in passwords:
        if check_password_hash(i[0], user_password):
            flag = True
            await state.set_state(Form.main_menu)

    if flag :
        await state.set_state(Form.main_menu)
        await state.update_data(is_auth=True)
        await message.answer(
            f"✅ Добро пожаловать {login}",
            reply_markup=await main_menu_kb()
        )
    else:
        await message.answer("❌ Неверный пароль. Попробуйте еще раз:")


@dp.callback_query(Form.main_menu, F.data == "start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.subject_selection)
    data = await state.get_data()
    idishnik = data.get("idishnik")
    builder = InlineKeyboardBuilder()

    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()
    b = []
    for i in db_sess.query(Questions.subject).filter(Questions.user_id == idishnik).all():
        if i not in b:
            b.append(i)

    print(b)

    for item in b:
        builder.add(InlineKeyboardButton(
            text=item[0],
            callback_data=f"subj_{item[0]}",
        ))



    builder.adjust(2)

    await callback.message.edit_text(
        "📚 Выберите предмет:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(Form.subject_selection, F.data.startswith("subj_"))
async def select_subject(callback: types.CallbackQuery, state: FSMContext):
    subject = callback.data.split("_")[1]

    await state.update_data(current_subject=subject)
    await state.set_state(Form.topic_selection)

    data = await state.get_data()
    idishnik = data.get("idishnik")

    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()

    topics = db_sess.query(Questions.topic).filter(Questions.user_id == idishnik, Questions.subject == subject).all()
    print(topics)
    tmp = []
    builder = InlineKeyboardBuilder()
    for item in topics:
        if item not in tmp:
            tmp.append(item)
            builder.add(InlineKeyboardButton(
                text=item[0],
                callback_data=f"topic_{item[0]}"))

    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
    builder.adjust(2)
    await callback.message.edit_text(
        "📖 Выберите тему:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(Form.topic_selection, F.data.startswith("topic_"))
async def select_topic(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.question_mode)
    topic = callback.data.split("_")[1]
    data = await state.get_data()
    idishnik = data.get("idishnik")
    subject = data.get("current_subject")
    await state.update_data(topic=topic)

    db_session.global_init(f"db/Quizi.db")
    db_sess = db_session.create_session()

    random_question = (db_sess.query(Questions.questions, Questions.answers)
                       .filter(Questions.user_id == idishnik, Questions.subject == subject,
                               Questions.topic == topic).order_by(func.random()).limit(1).first())
    tmp = (db_sess.query(Questions.questions)
           .filter(Questions.user_id == idishnik, Questions.subject == subject,
                   Questions.topic == topic).all())
    question_lst = []

    for d in tmp:
        question_lst.append(d[0])

    await state.update_data(question=random_question[0], answer=random_question[1], quest_lst=len(question_lst))

    await state.update_data(
        current_question=0,
        correct_answers=0)
    await send_question(callback.message, state)
    await callback.answer()


# 🟥 гостевая ветка

@dp.callback_query(Form.guest_mode, F.data == "go")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.quiz_subject_selection)
    builder = InlineKeyboardBuilder()


    b = []
    for i in cursor.execute('Select subject from quizzes').fetchall():
        if i not in b:
            b.append(i)

    print(b)

    for item in b:
        builder.add(InlineKeyboardButton(
            text=item[0],
            callback_data=f"subj_quiz_{item[0]}",
        ))

    builder.adjust(2)

    await callback.message.edit_text(
        "📚 Выберите предмет:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(Form.quiz_subject_selection, F.data.startswith("subj_quiz_"))
async def quiz_select_subject(callback: types.CallbackQuery, state: FSMContext):
    subject = callback.data.split("_")[2]

    await state.update_data(current_quiz_subject=subject)
    await state.set_state(Form.quiz_topic_selection)



    topics = cursor.execute('SELECT topic FROM quizzes WHERE subject = ?', (subject,))
    tmp = []
    builder = InlineKeyboardBuilder()
    for item in topics:
        if item not in tmp:
            tmp.append(item)
            builder.add(InlineKeyboardButton(
                text=item[0],
                callback_data=f"topic_quiz_{item[0]}"))

    builder.adjust(2)
    await callback.message.edit_text(
        "📖 Выберите тему:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.callback_query(Form.quiz_topic_selection, F.data.startswith("topic_quiz_"))
async def quiz_select_topic(callback: types.CallbackQuery, state: FSMContext):
    topic = callback.data.split("_")[2]
    data = await state.get_data()
    subject = data.get("current_quiz_subject")
    await state.update_data(quiz_topic=topic)

    await state.set_state(Form.quiz_grade_selection)



    grades = cursor.execute('SELECT grade FROM quizzes WHERE subject = ? AND topic = ?', (subject,topic))
    tmp = []
    builder = InlineKeyboardBuilder()
    for item in grades:
        if item not in tmp:
            tmp.append(item)
            builder.add(InlineKeyboardButton(
                text=item[0],
                callback_data=f"grade_quiz_{item[0]}"))

    builder.adjust(2)
    await callback.message.edit_text(
        "📖 Выберите класс:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()



@dp.callback_query(Form.quiz_grade_selection, F.data.startswith("grade_quiz_"))
async def quiz_select_grade(callback: types.CallbackQuery, state: FSMContext):
    grade = callback.data.split('_')[2]
    data = await state.get_data()
    topic = data.get('quiz_topic')
    subject = data.get("current_quiz_subject")

    # Получаем вопросы
    random_questions = cursor.execute('''
        SELECT id, question, explanation 
        FROM quizzes 
        WHERE subject = ? AND topic = ? AND grade = ?
        ORDER BY RANDOM()
    ''', (subject, topic, grade)).fetchall()

    quiz_data = []
    for q in random_questions:
        # Получаем варианты ответов
        answers = cursor.execute('''
            SELECT text, is_correct 
            FROM options 
            WHERE quiz_id = ?
        ''', (q[0],)).fetchall()

        options = [a[0] for a in answers]
        correct_option_id = None

        # Ищем правильный ответ
        for idx, answer in enumerate(answers):
            if answer[1] == 1:
                correct_option_id = idx
                break

        if correct_option_id is None:
            continue

        quiz_data.append({
            "question": q[1],
            "options": options,
            "correct_option_id": correct_option_id,
            "explanation": q[2]
        })

    if not quiz_data:
        await callback.message.answer("❌ В этой теме нет вопросов с правильными ответами!")
        return

    await state.update_data(
        quiz_questions=quiz_data,
        quiz_current_index=0,
        quiz_score=0
    )

    # Отправляем первый вопрос
    await send_quiz_question(callback.message.chat.id, quiz_data[0])
    await callback.answer()

# 🟥 запуск
if __name__ == "__main__":
    logging.info("Бот запущен")
    dp.run_polling(bot)