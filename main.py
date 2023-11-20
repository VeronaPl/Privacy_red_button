# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor, BaseStateGroup, Callback, GroupEventType, GroupTypes, CtxStorage
from vkbottle_types.objects import MessagesForward
from loguru import logger

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import creds

logger.disable('vkbottle')
load_dotenv()

VK_TOKEN = os.getenv('TOKEN')
ID_ADMIN = os.getenv('ADMIN_ID')

bot = Bot(VK_TOKEN)
ctx = CtxStorage()


class RegData(BaseStateGroup):
    COMMAND = 0
    NAME = 1
    LINK = 2
    COURSE = 3
    GROUP = 4
    FORM = 5
    KIND_OF_PROBLEM = 6
    QUESTION = 7


class RegError(BaseStateGroup):
    ACTION = 8
    ERROR = 9


KEYBOARD = {
    "education": (
        Keyboard(inline=True)
            .add(Callback('Повышенная стипендия', {'cmd': 'increased_scholarship'}))
            .row()
            .add(Callback('Перевод на бюджет', {'cmd': 'budget'}))
            .row()
            .add(Callback('Академический отпуск', {'cmd': 'academic_holidays'}))
            .row()
            .add(Callback('Перевод на другое отделение ЭМИТ', {'cmd': 'transfer_program'}))
            .row()
            .add(Callback('Не устраивает преподаватель', {'cmd': 'problem_teacher'}))
            .row()
            .add(Callback('Скидка на обучение', {'cmd': 'discount'}))
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "extracurricular": (
        Keyboard(inline=True)
            .add(Callback('Отбор в СС ЭМИТ', {'cmd': 'selection_ss_emit'}))
            .row()
            .add(Callback('Вступить в СМИ ЭМИТ', {'cmd': 'smi_emit'}))
            .row()
            .add(Callback('Как получить чёрный бомбер', {'cmd': 'black_bomber'}))
            .row()
            .add(Callback('Стать частью рабочих групп', {'cmd': 'work_rg'}))
            .row()
            .add(Callback('Центры СС ЭМИТ', {'cmd': 'centers_ss_emit'}))
            .add(Callback('Актив СС ЭМИТ', {'cmd': 'active_ss_emit'}))
            .row()
            .add(Callback('Начало внеучебки', {'cmd': 'start_extracurricular'}))
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "hostel": (
        Keyboard(inline=True)
            .add(Callback('Проблемы с общежитием', {'cmd': 'problem_hostel'}))
            .row()
            .add(Callback('Заселение в общежитие', {'cmd': 'check_in_hostel'}))
            .row()
            .add(Callback('Заселение в ГЖК', {'cmd': 'check_in_house'}))
            .row()
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "medicine": (
        Keyboard(inline=True)
            .add(Callback('Где находится медицинский центр', {'cmd': 'where_medicine'}))
            .row()
            .add(Callback('Как прикрепиться к медицинскому центру', {'cmd': 'register_in_medicine'}))
            .row()
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "infrastructure": (
        Keyboard(inline=True)
            .add(Callback('Расположение библиотеки', {'cmd': 'where_library'}))
            .row()
            .add(Callback('Расположение копировального центра', {'cmd': 'where_copy_center'}))
            .row()
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "documents": (
        Keyboard(inline=True)
            .add(Callback('Материальная помощь', {'cmd': 'material_help'}))
            .row()
            .add(Callback('Отсрочка от военной службы', {'cmd': 'army'}))
            .row()
            .add(Callback('Учебный план', {'cmd': 'study'}))
            .row()
            .add(Callback('Назад', {'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_education": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'education'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_extracurricular": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'extracurricular'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_hostel": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'hostel'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_medicine": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'medicine'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_infrastructure": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'infrastructure'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "home_documents": (
        Keyboard(one_time=False, inline=True)
            .add(Callback('Назад к вопросам', {'cmd': 'documents'}), color=KeyboardButtonColor.PRIMARY)
    ),
    "recent_question": (
        Keyboard(one_time=False, inline=True)
            .add(Callback("Образовательный процесс", {'cmd': 'education'}))
            .row()
            .add(Callback("Внеучебная деятельность", {'cmd': 'extracurricular'}))
            .row()
            .add(Callback("Общежитие", {'cmd': 'hostel'}))
            .add(Callback("Медицина", {'cmd': 'medicine'}))
            .row()
            .add(Callback("Инфраструктура", {'cmd': 'infrastructure'}))
            .row()
            .add(Callback("Документы и другие вопросы", {'cmd': 'documents'}))
            .row()
            .add(Text("Другое", {'cmd': 'other'}))
    ),
    "main_menu": (
        Keyboard(inline=False)
            .add(Text('Задать вопрос'), color=KeyboardButtonColor.PRIMARY)
            .add(Text('Частые вопросы'), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Text('Настройки'), color=KeyboardButtonColor.SECONDARY)
    ),
    "settings": (
        Keyboard(inline=False)
            .add(Text('Назад', {'cmd': 'main_menu'}), color=KeyboardButtonColor.PRIMARY)
            .add(Text('Об авторе', {'cmd': 'developer'}), color=KeyboardButtonColor.POSITIVE)
            .row()
            .add(Text('Оставить обратную связь', {'cmd': 'find_error'}), color=KeyboardButtonColor.NEGATIVE)
    )
}

MESSAGES = {
    "increased_scholarship": "✨Как получить повышенную стипендию?✨\n\nНа ПГАС (повышенная государственная академическая стипендия) может претендовать студент, обучающейся по очной форме обучения на бюджетной основе по образовательным программам бакалавриата, специалитета, магистратуры. Студент не должен иметь академических задолженностей и оценок «удовлетворительно». Институт уведомляет студентов о проведении конкурса и предоставляет им информацию об условиях подачи документов для участия в конкурсе.\n\nРешение о выдвижении кандидатов на получение ПГАС принимается стипендиальной комиссией института/факультета Академии с участием представителей органов студенческого самоуправления и передается в виде комплекта документов в стипендиальную комиссию Академии. Подробнее с информацией можно ознакомиться на сайте РАНХиГС в разделе «Повышенная государственная академическая стипендия»:\n\nhttps://www.ranepa.ru/sveden/grants/?utm_source=google.com&utm_medium=organic&utm_campaign=google.com&utm_referrer=google.com",
    "budget": "✨Как перевестись с платной формы обучения на бюджет?✨\n\nПереход с платного обучения на бесплатное осуществляется при наличии свободных мест, финансируемых за счет бюджетных ассигнований федерального бюджета по соответствующей образовательной программе по специальности, направлению подготовки и форме обучения на соответствующем курсе.\nЗаявления о переходе подаются обучающимися в деканат своего факультета с момента размещения информации о количестве вакантных бюджетных мест. Порядок приоритетности перехода студентов с платного обучения на бесплатное:\n\n- в порядке первой очереди – по результатам промежуточной аттестации, а также особых достижений в учебной, научно-исследовательской, общественной, культурно-творческой, спортивной деятельности;\n- в порядке второй очереди – студенты, предоставившие документы, подтверждающие их принадлежность к льготным категориям подпункта «б» (женщины, родившие ребенка в период обучения, дети-сироты);\n- в порядке третьей очереди – студенты, предоставившие документы, подтверждающие их принадлежность к льготной категории подпункта «в» (утрата одного или обоих родителей в период обучения).\n\nПодробнее можешь ознакомиться:\n\nhttps://www.ranepa.ru/images/docs/prikazy-ranhigs/Pologenie_o_perevode_na_budget.pdf",
    "academic_holidays": "✨Как взять академический отпуск?✨\n\nАкадемический отпуск предоставляется обучающимся в связи с невозможностью освоения образовательной программы в Академии по медицинским показаниям, семейным и иным обстоятельствам на период времени, не превышающий двух лет. Решение о предоставлении академического отпуска принимается в десятидневный срок со дня получения от обучающегося заявления и прилагаемых к нему документов. Решение о предоставлении академического отпуска оформляется приказом Академии, который подписывается проректором Академии.",
    "transfer_program": "✨Как мне перевестись на другое отделение внутри ЭМИТ?✨\n\nПеревод осуществляется при отсутствии у студента академической задолженности и просрочки оплаты стоимости обучения. Заявление о переводе рассматривается Аттестационной комиссией ЭМИТ. Аттестационная комиссия не позднее 14 календарных дней со дня подачи заявления о переводе определяет перечень изученных учебных дисциплин, пройденных практик, выполненных научных исследований, которые в случае перевода студента будут перезачтены или переаттестованы.\n\nПодробнее можешь ознакомиться:\n\nhttps://www.ranepa.ru/images/docs/prikazy-ranhigs/Poryadok_perevoda.pdf",
    "problem_teacher": "✨Что делать, если не устраивает преподаватель?✨\n\nВ этой ситуации приходится находить пути решения конфликта, финальным из которых может стать жалоба на преподавателя. Если ты понимаешь, что учебный план, методы работы или сам преподаватель некомпетентные, ты должен обсудить это с вашей группой. В случае, когда вся группа разделяет твое мнение по данному вопросу, вы должны написать коллективную жалобу на преподавателя, прописывая подробно все претензии по отношению к нему (предвзятое отношение в данной ситуации, необъективное оценивание в этой ситуации и тд).\n\nВ конце жалобы должен быть предложен адекватный запрос к деканату – что именно вы хотите этой жалобой (например, смена преподавателя или отмена результатов n-ного количества работ). На отдельном листе должны быть приложены подписи вашей группы, тем самым подтверждая серьезность ваших намерений. После этого вы можете со своей жалобой обращаться в деканат и рассчитывать на дальнейшее решение данной проблемы.",
    "discount": "✨Как получить скидку на обучение?✨\n\nДля того чтобы получить скидку, тебе необходимо обратиться в деканат. Узнать, предоставляется ли скидка студентам твоего отделения или направления. Если да, то ты пишешь заявление о получение скидки на имя директора института ЭМИТ. Далее твое заявление будет рассмотрено и ты будешь проинформирован о результате.",
    "selection_ss_emit": "✨Когда будет отбор в СС ЭМИТ и как он будет проходить?✨\n\nОтбор в СС ЭМИТ проходит в конце мая, обычно после выбора председателя СС ЭМИТ. Он проходит в 4 этапа - заполнение заявки, тест на знания положения СС ЭМИТ, деловая игра, собеседование.",
    "smi_emit": "✨Как попасть в СМИ ЭМИТ?✨\n\nОсенью проходит школа GLITCH, где ты можешь познакомиться с работой СМИ ЭМИТ и по итогам которой можно попасть в состав СМИ. Помимо этого летом также проводят отбор, который анонсируют в самой группе. Подпишись и следи внимательно за обновлениями!\n\nДля более подробной информации напиши главе СМИ ЭМИТ Веронике Моисеевой:\n\nhttps://vk.com/veronicamoi",
    "black_bomber": "✨Как получить черный бомбер?✨\n\nЧтобы получить бомбер как у членов Студенческого совета ЭМИТ, нужно пройти в созыв. Условия попадания в него ты можешь посмотреть в ответе на вопрос «Когда будет отбор в СС ЭМИТ и как он будет проходить?».",
    "work_rg": "✨Как стать частью рабочих групп?✨\n\nВ группе СМИ ЭМИТ появляется запись об отборе в рабочие группы. Тебе нужно будет заполнить форму и ждать ответа от главы рабочей группы.",
    "centers_ss_emit": "✨Чем занимаются центры СС ЭМИТ?✨\n\nВ СС ЭМИТ есть 4 центра:\n- Центр Внешних Коммуникаций;\n- Центр Внутренних Коммуникаций;\n- Центр Маркетинга и Анализа;\n- Центр Цифровых Коммуникаций.\n\nЦВК отвечает за внешнее взаимодействие, ЦВНуК занимается правозащитной, корпоративной культурой, связью с абитуриентами, в ЦЦК работают программисты, дизайнеры и моушн-дизайнеры, ЦМА отвечает за сбор и анализ обратной связи.\n\nДля более подробной информации можешь обратиться к главам центров:\nГлава ЦЦК - https://vk.com/pbabaeva\nГлава ЦВНуК - https://vk.com/parapanchik\nГлава ЦВК - https://vk.com/gus_rabotyaga\nГлава ЦМА - https://vk.com/stasia_key",
    "active_ss_emit": "✨Что такое Актив СС ЭМИТ и как туда попасть?✨\n\nАктив СС ЭМИТ -  это мастер-классы, проекты, новые знакомства и яркие впечатления. Актив создан, чтобы показать, как работает каждый центр СС ЭМИТ. Чтобы попасть туда, нужно заполнить форму, которая появится в СМИ ЭМИТ и пройти отбор.",
    "start_extracurricular": "✨Как начать свой путь во внеучебной деятельности?✨\n\nНачать свой внеучебный путь можно с любого мероприятия на институте или академическом уровне. Ты можешь быть участником, волонтером, членом рабочей группы, даже зрителем. Следи за новостями в группе СМИ ЭМИТ и заполняй заявку.",
    "problem_hostel": "✨Что делать, если появились проблемы с проживанием в общежитии?✨\n\nТебе следует обратиться к Председателю Коллегии проживающих в общежитии РАНХиГС https://vk.com/id274791439 и выяснить, какие данные по этому вопросу есть у него и чем он может помочь.\n\nКроме того, можно обратиться к администрации общежития и ЕДРО:\n\nhttps://www.ranepa.ru/ob-akademii/infrastruktura/obshchezhitiya-i-gostinitsy/",
    "check_in_hostel": "✨Как заселиться в общежитие?✨\n\nЧтобы заселиться в общежитие, нужно встать в очередь на сайте ЕДРО РАНХиГС (Единая дирекция развития общежитий). Это можно сделать через личный кабинет на официальном сайте Академии, или же прийти лично к главе ЕДРО в Академии.\n\nДалее следует обратиться в деканат своего института, узнать какой перечень документов нужно предоставить. Стоит отметить, что обычно в приоритете у деканата на заселение в общежитие стоят студенты, обучающиеся на бюджетной основе.",
    "check_in_house": "✨Как заселиться в ГЖК?✨\n\nУзнай в деканате отделения, предоставляется ли ГЖК отделению, если да, то напиши заявление. Заселение в гостинично-жилой комплекс происходит согласно спискам, предоставленным институтами Академии.",
    "where_medicine": "✨Где находится медицинский центр РАНХиГС?✨\n\nМедицинский центр РАНХиГС находится в 7 корпусе.",
    "register_in_medicine": "✨Как прикрепиться к медицинскому центру РАНХиГС?✨\n\nПрикрепиться к мед. центру на территории РАНХиГС достаточно просто. Тебе предложат это сделать на первом медицинском осмотре, который необходим для посещения занятий по физкультуре. При себе необходимо иметь московский ПОЛИС и паспорт, далее нужно будет просто написать заявление о прикреплении в самом мед. центре. После прикрепления ты получаешь возможность записи на прием к врачу в электронном виде.",
    "where_library": "✨Где находится библиотека?✨\n\n1 корпус: 8 этаж – Научная литература.\n1 корпус: 9 этаж – Читальные и компьютерный залы.\n5 корпус: 2 этаж – Учебная литература.",
    "where_copy_center": "✨Есть ли в Академии копировальный центр?✨\n\nОтделы копировально-множительной техники расположены в корпусе 5 , ком. 109, корпус 9, ком. 204.",
    "material_help": "✨Как получить материальную помощь?✨\n\nЕсть много условий получения материальной помощи от Академии - в основном касающиеся тяжелого финансового и семейного положения (потеря родителя, создание семьи, инвалидность и пр.). Для того, чтобы получить материальную помощь, нужно подать документ, подтверждающий ее необходимость, в администрацию института. При решении оказания материальной помощи учитывается мнение факультета и администрации учебного подразделения.",
    "army": "✨Как получить отсрочку от военной службы?✨\n\nОтсрочка от службы в Вооруженных Силах РФ предоставляется студентам (бакалавриат, магистратура) и аспирантам очной формы обучения на время учебы. Выдается справка об отсрочке (форма № 26). При любом обращении в военно-учетный стол необходимо иметь при себе удостоверение призывника. Документы, необходимые для предоставления отсрочки и постановки на учет:\n\n · Паспорт;\n · Приписное удостоверение;\n · Повестка (при наличии);\n · Регистрация;\n · Магистрам и аспирантам при себе иметь копию диплома о высшем образовании (бакалавриат или специалитет).",
    "study": "✨Где можно найти учебный план?✨\n\nНа данном сайте можно найти учебные планы всех отделений и направлений:\n\nhttps://emit.ranepa.ru/programs/",
    "developer": "Разработчиком данного бота по правозащите является студентка 3 курса Прикладной информатики, ЭМИТ, РАНХиГС:\n\n@ragazza_verona (Плешакова Вероника)\n\nПо вопросам дальнейшего сотрудничества просьба обращаться в лс"
}




@bot.on.private_message(text=['/start', 'Начать', 'Старт'])
async def main(message: Message):
    user = await bot.api.users.get(message.from_id)
    await message.answer(
        message=f'Привет, {user[0].first_name}!✨\n\nНа связи Студенческий совет ЭМИТ. Ты можешь обратиться к нам через эту форму с любым вопросом или проблемой, а мы сделаем все возможное, чтобы помочь тебе!',
        keyboard=KEYBOARD['main_menu']
    )


@bot.on.private_message(payload={'cmd': 'main_menu'})
async def menu(message: Message):
    await message.answer(
        message='Что тебя интересует?',
        keyboard=KEYBOARD['main_menu']
    )
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.private_message(text=['Настройки'])
async def settings(message: Message):
    await message.answer(
        message='Здесь ты можешь узнать информацию о разработчике или оставить обратную связь при обнаружении неточности',
        keyboard=KEYBOARD['settings']
    )
    await bot.state_dispenser.delete(message.peer_id)

@bot.on.private_message(payload={'cmd': 'developer'})
async def developer(message: Message):
    await message.answer(
        message=MESSAGES['developer']
    )
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.private_message(text='Оставить обратную связь')
@bot.on.private_message(payload={'cmd': 'find_error'})
async def find_error(message: Message):
    await message.answer(
        message="В чём заключается неточность или обратная связь по боту, которую Вы хотите передать?\n\nНапишите в ответ на это сообщение своё мнение о боте, и оно обязательно будет передано разработчику",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegError.ERROR)
    if "Назад к" not in message.text:
        ctx.set("action", message.text)

@bot.on.private_message(payload={'cmd': 'throw'})
@bot.on.private_message(state=RegError.ERROR)
async def throw(message: Message):
    await message.answer(
        message="Нажимая кнопку «Отправить», я даю свое согласие на отправку моей обратной связи разработчику в анонимном порядке",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Отправить', payload={'cmd': 'finish'}), color=KeyboardButtonColor.POSITIVE)
                .add(Text('Назад к заявке', payload={'cmd': 'find_error'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}))
        )
    )
    if "Назад к" not in message.text:
        ctx.set("error", message.text)
    await bot.state_dispenser.delete(message.peer_id)

@bot.on.private_message(payload={'cmd': 'finish'})
async def finish_error(message: Message):
    error = ctx.get("error")
    await message.answer(
        message="Ваша заявка отправлена разработчику.\n\nСпасибо за обратную связь! Вы помогаете нам стать лучше)"
    )
    target_chat_id = ID_ADMIN  # замените на ID вашего чата
    await bot.api.messages.send(
        peer_id=target_chat_id,
        message=f"‼Обратная связь по боту по правозащите‼\n\n<{error}>",
        random_id=0
    )
    await menu(message)



@bot.on.private_message(payload={'cmd': 'recent_question'})
@bot.on.private_message(text='Частые вопросы')
@bot.on.private_message(text='Назад к выбору темы')
async def resent_questions(message: Message):
    await message.answer(
        message='Выбери интересующую тебя тему вопроса:',
        keyboard=KEYBOARD['recent_question']
    )
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.private_message(text='Задать вопрос')
@bot.on.private_message(payload={'cmd': 'ask_question'})
async def resent_questions(message: Message):
    await message.answer(
        message="Напиши, пожалуйста, свое ФИО:",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.NAME)
    if "Назад к" not in message.text:
        ctx.set("command", message.text)


# @bot.on.private_message(state=RegData.COMMAND, payload={'cmd': 'start_question'})
# async def command_handler(message: Message):
#     ctx.set("command", message.text)
#     await bot.state_dispenser.set(message.peer_id, RegData.NAME)

@bot.on.private_message(payload={'cmd': 'ask_link'})
@bot.on.private_message(state=RegData.NAME)
async def link_handler(message: Message):
    await message.answer(
        message="Отправь, пожалуйста, ссылку на свой ВК:",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Назад к ФИО', {'cmd': 'ask_question'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.LINK)
    if "Назад к" not in message.text:
        ctx.set("name", message.text)


@bot.on.private_message(payload={'cmd': 'ask_course'})
@bot.on.private_message(state=RegData.LINK)
async def course_handler(message: Message):
    await message.answer(
        message="Твой курс?",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('1 курс'))
                .add(Text('2 курс'))
                .row()
                .add(Text('3 курс'))
                .add(Text('4 курс'))
                .row()
                .add(Text('Магистратура'))
                .row()
                .add(Text('Назад к ссылке на вк', payload={'cmd': 'ask_link'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.COURSE)
    if "Назад к" not in message.text:
        ctx.set("link", message.text)


@bot.on.private_message(payload={'cmd': 'ask_group'})
@bot.on.private_message(state=RegData.COURSE)
async def group_handler(message: Message):
    await message.answer(
        message="Твое отделение?",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('ОНЭ'))
                .add(Text('ОЭ'))
                .row()
                .add(Text('БИ'))
                .add(Text('ПИ'))
                .row()
                .add(Text('Школа IT-менеджмента'))
                .row()
                .add(Text('Назад к курсу', payload={'cmd': 'ask_course'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.GROUP)
    if "Назад к" not in message.text:
        ctx.set("course", message.text)


@bot.on.private_message(payload={'cmd': 'ask_form'})
@bot.on.private_message(state=RegData.GROUP)
async def form_handler(message: Message):
    await message.answer(
        message="Какая у тебя форма обучения?",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Очная'))
                .row()
                .add(Text('Очно-заочная'))
                .row()
                .add(Text('Заочная'))
                .row()
                .add(Text('Назад к отделению', payload={'cmd': 'ask_group'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.FORM)
    if "Назад к" not in message.text:
        ctx.set("group", message.text)


@bot.on.private_message(payload={'cmd': 'ask_kind_of_problem'})
@bot.on.private_message(state=RegData.FORM)
async def kind_of_problem_handler(message: Message):
    await message.answer(
        message="С чем связана твоя проблема?",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Образование'))
                .add(Text('Внеучебка'))
                .row()
                .add(Text('Общежитие'))
                .add(Text('Медицина'))
                .row()
                .add(Text('Инфраструктура'))
                .add(Text('Документы'))
                .row()
                .add(Text('Другое (открытый вариант ответа)'))
                .row()
                .add(Text('Назад к форме', payload={'cmd': 'ask_form'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.KIND_OF_PROBLEM)
    if "Назад к" not in message.text:
        ctx.set("form", message.text)


@bot.on.private_message(payload={'cmd': 'ask_problem'})
@bot.on.private_message(state=RegData.KIND_OF_PROBLEM)
async def question_handler(message: Message):
    await message.answer(
        message="Напиши вопросы, предложение или опиши сложившуюся ситуацию подробно",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Назад к типу проблемы', payload={'cmd': 'ask_kind_of_problem'}),
                     color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    await bot.state_dispenser.set(message.peer_id, RegData.QUESTION)
    if "Назад к" not in message.text:
        ctx.set("kind_of_problem", message.text)


@bot.on.private_message(payload={'cmd': 'deliver'})
@bot.on.private_message(state=RegData.QUESTION)
async def deliver(message: Message):
    await message.answer(
        message="Нажимая кнопку «Отправить», я даю свое согласие на обработку моих персональных данных, в соответствии с Федеральным законом от 27.07.2006 года №152-ФЗ «О персональных данных», на условиях и для целей, определенных в Согласии на обработку персональных данных",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Отправить', payload={'cmd': 'send'}), color=KeyboardButtonColor.POSITIVE)
                .add(Text('Назад к проблеме', payload={'cmd': 'ask_problem'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}))
        )
    )
    if "Назад к" not in message.text:
        ctx.set("question", message.text)
    await bot.state_dispenser.delete(message.peer_id)


@bot.on.private_message(payload={'cmd': 'send'})
async def send_question(message: Message):
    name = ctx.get("name")
    link = ctx.get("link")
    course = ctx.get("course")
    group = ctx.get("group")
    form = ctx.get("form")
    kind_of_problem = ctx.get("kind_of_problem")
    question = ctx.get("question")
    await message.answer(
        message="Твое обращение скоро рассмотрят специалисты Центра Внутренних Коммуникаций!"
    )

    creds_json = os.path.dirname(__file__) + "/creds/sacc1.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    service = build('sheets', 'v4', http=creds_service)
    sheet = service.spreadsheets()
    sheet_id = "1ryjuQlnEVMKrSu3BRz3SO1GDQG7PVQrIcZzzxc9A_qo"

    resp = sheet.values().append(
        spreadsheetId=sheet_id,
        range="Лист1!A2",
        valueInputOption="RAW",
        body={'values': [[name, link, course, group, form, kind_of_problem, question]]}).execute()
    print(resp)
    await menu(message)

@bot.on.private_message(payload={'cmd': 'other'})
async def resent_questions(message: Message):
    await message.answer(
        message="Напиши, пожалуйста, свое ФИО:",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text('Назад к выбору темы', payload={'cmd': 'recent_question'}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('В главное меню', payload={'cmd': 'main_menu'}), color=KeyboardButtonColor.POSITIVE)
        )
    )
    if "Назад к" not in message.text:
        await bot.state_dispenser.set(message.peer_id, RegData.NAME)
        ctx.set("command", message.text)


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def message_event_handler(event: GroupTypes.MessageEvent):
    if event.object.payload['cmd'] == 'recent_question':
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message='Выбери интересующую тебя тему вопроса:',
            keyboard=KEYBOARD[event.object.payload['cmd']]
        )
    elif event.object.payload['cmd'] in ['increased_scholarship', 'budget', 'academic_holidays', 'transfer_program',
                                         'problem_teacher', 'discount']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_education']
        )
    elif event.object.payload['cmd'] in ['selection_ss_emit', 'smi_emit', 'black_bomber', 'work_rg', 'centers_ss_emit',
                                         'active_ss_emit', 'start_extracurricular']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_extracurricular']
        )
    elif event.object.payload['cmd'] in ['problem_hostel', 'check_in_hostel', 'check_in_house']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_hostel']
        )
    elif event.object.payload['cmd'] in ['where_medicine', 'register_in_medicine']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_medicine']
        )
    elif event.object.payload['cmd'] in ['where_library', 'where_copy_center']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_infrastructure']
        )
    elif event.object.payload['cmd'] in ['material_help', 'army', 'study']:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message=MESSAGES[event.object.payload['cmd']],
            keyboard=KEYBOARD['home_documents']
        )
    else:
        await bot.api.messages.edit(
            event_id=event.object.event_id,
            peer_id=event.object.peer_id,
            user_id=event.object.user_id,
            conversation_message_id=event.object.conversation_message_id,
            message='Выбери вопрос, который тебя интересует!',
            keyboard=KEYBOARD[event.object.payload['cmd']]
        )


@bot.on.private_message()
async def spam(message: Message):
    """Функция-заглушка на остальные сообщения от пользователя"""
    await message.answer(
        message='Я тебя не понимаю, воспользуйся моей клавиатурой с кнопками :)'
    )


bot.run_forever()
