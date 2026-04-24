from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Resume, Vacancy, Application, User
from keyboards.inline import get_apply_keyboard
from services.ai_matcher import get_top_vacancies_for_resume
from locales import LEXICON

router = Router()

class ResumeForm(StatesGroup):
    age = State()
    skills = State()
    experience = State()
    microdistrict = State()
    expected_salary = State()
    schedule = State()
    time_available = State()
    languages = State()

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_my_resume"], LEXICON["kk"]["btn_my_resume"], LEXICON["en"]["btn_my_resume"]])
async def cmd_my_resume(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result_user.scalar_one_or_none()
    lang = user.language if user else "ru"
    
    result = await session.execute(select(Resume).where(Resume.user_id == message.from_user.id))
    resume = result.scalar_one_or_none()
    
    if resume:
        text = (f"Возраст/Жасы/Age: {resume.age}\n"
                f"Навыки/Дағдылар/Skills: {resume.skills}\n"
                f"Опыт/Тәжірибе/Experience: {resume.experience}\n"
                f"Район/Аудан/District: {resume.microdistrict}\n"
                f"ЗП/Жалақы/Salary: {resume.expected_salary}\n"
                f"График/Кесте/Schedule: {resume.schedule}\n"
                f"Свободное время/Бос уақыт/Free time: {resume.time_available}\n"
                f"Языки/Тілдер/Languages: {resume.languages}\n")
        
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=LEXICON[lang]["btn_update_resume"], callback_data="update_resume")]])
        await message.answer(text, reply_markup=markup)
    else:
        await message.answer(LEXICON[lang]["ask_age"])
        await state.set_state(ResumeForm.age)

@router.callback_query(F.data == "update_resume")
async def process_update_resume(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = result_user.scalar_one_or_none()
    lang = user.language if user else "ru"
    
    await callback.message.answer(LEXICON[lang]["ask_age"])
    await state.set_state(ResumeForm.age)
    await callback.answer()

@router.message(ResumeForm.age)
async def process_age(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result_user.scalar_one_or_none()
    lang = user.language if user else "ru"
    
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer(LEXICON[lang]["ask_skills"])
        await state.set_state(ResumeForm.skills)
    except ValueError:
        await message.answer(LEXICON[lang]["need_number"])

@router.message(ResumeForm.skills)
async def process_skills(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(skills=message.text)
    await message.answer(LEXICON[lang]["ask_experience"])
    await state.set_state(ResumeForm.experience)

@router.message(ResumeForm.experience)
async def process_experience(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(experience=message.text)
    await message.answer(LEXICON[lang]["ask_district"])
    await state.set_state(ResumeForm.microdistrict)

@router.message(ResumeForm.microdistrict)
async def process_microdistrict(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(microdistrict=message.text)
    await message.answer(LEXICON[lang]["ask_salary"])
    await state.set_state(ResumeForm.expected_salary)

@router.message(ResumeForm.expected_salary)
async def process_salary(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(expected_salary=message.text)
    await message.answer(LEXICON[lang]["ask_schedule"])
    await state.set_state(ResumeForm.schedule)

@router.message(ResumeForm.schedule)
async def process_schedule(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(schedule=message.text)
    await message.answer(LEXICON[lang]["ask_time"])
    await state.set_state(ResumeForm.time_available)

@router.message(ResumeForm.time_available)
async def process_time_available(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(time_available=message.text)
    await message.answer(LEXICON[lang]["ask_s_lang"])
    await state.set_state(ResumeForm.languages)

@router.message(ResumeForm.languages)
async def process_languages(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    data = await state.get_data()
    data['languages'] = message.text
    
    result = await session.execute(select(Resume).where(Resume.user_id == message.from_user.id))
    resume = result.scalar_one_or_none()
    
    if resume:
        resume.age = data['age']
        resume.skills = data['skills']
        resume.experience = data['experience']
        resume.microdistrict = data['microdistrict']
        resume.expected_salary = data['expected_salary']
        resume.schedule = data['schedule']
        resume.time_available = data['time_available']
        resume.languages = data['languages']
    else:
        resume = Resume(
            user_id=message.from_user.id,
            **data
        )
        session.add(resume)
    
    await session.commit()
    await state.clear()
    await message.answer(LEXICON[lang]["resume_saved"])

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_find_vacancies"], LEXICON["kk"]["btn_find_vacancies"], LEXICON["en"]["btn_find_vacancies"]])
async def cmd_find_vacancies(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    result = await session.execute(select(Resume).where(Resume.user_id == message.from_user.id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        await message.answer(LEXICON[lang]["resume_not_found"])
        return
        
    await message.answer(LEXICON[lang]["analyzing"])
    
    matches = await get_top_vacancies_for_resume(session, resume.id)
    
    if not matches:
        await message.answer(LEXICON[lang]["no_vacancies"])
        return
        
    for match in matches:
        v = match['vacancy']
        percent = match['match_percent']
        text = (f"🔥 {percent}%\n\n"
                f"📌 {v.title}\n"
                f"📍 {v.microdistrict}\n"
                f"💰 {v.salary}\n"
                f"⏰ {v.schedule}\n"
                f"📝 {v.description}\n"
                f"🎯 {v.skills_required}\n"
                f"🗣 {v.languages_required}")
                
        await message.answer(text, reply_markup=get_apply_keyboard(v.id, lang))

@router.callback_query(F.data.startswith("apply_"))
async def process_apply(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    result_user = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    lang = result_user.scalar_one().language
    
    vacancy_id = int(callback.data.split("_")[1])
    
    result = await session.execute(select(Resume).where(Resume.user_id == callback.from_user.id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        await callback.answer(LEXICON[lang]["resume_not_found"], show_alert=True)
        return
        
    result = await session.execute(
        select(Application).where(Application.resume_id == resume.id, Application.vacancy_id == vacancy_id)
    )
    existing_app = result.scalar_one_or_none()
    
    if existing_app:
        await callback.answer(LEXICON[lang]["already_applied"], show_alert=True)
        return
        
    app = Application(resume_id=resume.id, vacancy_id=vacancy_id)
    session.add(app)
    await session.commit()
    
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    
    if vacancy:
        from keyboards.inline import get_employer_decision_keyboard
        employer_tg_id = vacancy.employer_id
        
        # Получаем данные соискателя
        seeker_user = callback.from_user
        seeker_contact = f"@{seeker_user.username}" if seeker_user.username else f"<a href='tg://user?id={seeker_user.id}'>Профиль</a>"
        
        # Получаем язык работодателя и проверяем его
        result_emp = await session.execute(select(User).where(User.tg_id == employer_tg_id))
        emp_user = result_emp.scalar_one_or_none()
        emp_lang = emp_user.language if (emp_user and emp_user.language in ["ru", "kk", "en"]) else "ru"
        
        text = (f"🎉 <b>Новый отклик на вакансию '{vacancy.title}'!</b>\n\n"
                f"👤 Соискатель: {seeker_user.full_name}\n"
                f"🔗 Контакт: {seeker_contact}\n"
                f"🆔 ID: <code>{seeker_user.id}</code>\n"
                f"🎂 Возраст: {resume.age}\n"
                f"🛠 Навыки: {resume.skills}\n"
                f"💼 Опыт: {resume.experience}\n"
                f"🗣 Языки: {resume.languages}")
        try:
            await callback.bot.send_message(
                employer_tg_id, 
                text, 
                parse_mode="HTML",
                reply_markup=get_employer_decision_keyboard(app.id, emp_lang)
            )
        except Exception as e:
            print(f"Не удалось уведомить работодателя: {e}")
            
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(LEXICON[lang]["applied_success"])
    except:
        pass
    await callback.answer()
