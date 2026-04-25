from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Vacancy, Application, Resume, User
from locales import LEXICON
from services.moderator import is_content_safe
from datetime import datetime, timedelta
from sqlalchemy import delete

router = Router()

class VacancyForm(StatesGroup):
    title = State()
    description = State()
    skills_required = State()
    type = State()
    microdistrict = State()
    schedule = State()
    salary = State()
    languages_required = State()

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_create_vac"], LEXICON["kk"]["btn_create_vac"], LEXICON["en"]["btn_create_vac"]])
async def cmd_create_vacancy(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    
    # ПРОВЕРКА ЛИМИТА: 2 вакансии в неделю
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    result_count = await session.execute(
        select(Vacancy).where(
            Vacancy.employer_id == message.from_user.id,
            Vacancy.created_at >= one_week_ago
        )
    )
    vac_count = len(result_count.scalars().all())
    
    if vac_count >= 2:
        await message.answer("⚠️ <b>Лимит исчерпан! / Лимит толы!</b>\n\nВы можете создавать не более 2 вакансий в неделю. / Аптасына 2-ден артық бос орын құра алмайсыз.", parse_mode="HTML")
        return

    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await message.answer(LEXICON[lang]["ask_v_title"])
    await state.set_state(VacancyForm.title)

# Обработчик перенесен вниз для полноты логики

@router.message(VacancyForm.title)
async def process_title(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(title=message.text)
    await message.answer(LEXICON[lang]["ask_v_desc"])
    await state.set_state(VacancyForm.description)

@router.message(VacancyForm.description)
async def process_description(message: Message, session: AsyncSession, state: FSMContext):
    # Мгновенная проверка описания
    if not is_content_safe(message.text):
        await message.answer("🚫 <b>Описание не прошло модерацию!</b>\n\nТекст содержит недопустимые выражения. Исправьте его.", parse_mode="HTML")
        return

    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(description=message.text)
    await message.answer(LEXICON[lang]["ask_v_skills"])
    await state.set_state(VacancyForm.skills_required)

@router.message(VacancyForm.skills_required)
async def process_skills_required(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(skills_required=message.text)
    await message.answer(LEXICON[lang]["ask_v_type"])
    await state.set_state(VacancyForm.type)

@router.message(VacancyForm.type)
async def process_type(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(type=message.text)
    await message.answer(LEXICON[lang]["ask_v_district"])
    await state.set_state(VacancyForm.microdistrict)

@router.message(VacancyForm.microdistrict)
async def process_v_microdistrict(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(microdistrict=message.text)
    await message.answer(LEXICON[lang]["ask_v_schedule"])
    await state.set_state(VacancyForm.schedule)

@router.message(VacancyForm.schedule)
async def process_v_schedule(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(schedule=message.text)
    await message.answer(LEXICON[lang]["ask_v_salary"])
    await state.set_state(VacancyForm.salary)

@router.message(VacancyForm.salary)
async def process_v_salary(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    await state.update_data(salary=message.text)
    await message.answer(LEXICON[lang]["ask_v_lang"])
    await state.set_state(VacancyForm.languages_required)

@router.message(VacancyForm.languages_required)
async def process_v_languages(message: Message, session: AsyncSession, state: FSMContext):
    result_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    lang = result_user.scalar_one().language
    
    data = await state.get_data()
    data['languages_required'] = message.text
    
    # ИИ-ЦЕНЗУРА: Проверка контента
    full_text = f"{data.get('title', '')} {data.get('description', '')}"
    if not is_content_safe(full_text):
        await message.answer("🚫 <b>Ошибка модерации! / Модерация қатесі!</b>\n\nВаш текст содержит подозрительный или запрещенный контент. Пожалуйста, измените описание.", parse_mode="HTML")
        await state.clear()
        return

    vacancy = Vacancy(
        employer_id=message.from_user.id,
        **data
    )
    session.add(vacancy)
    await session.commit()
    await state.clear()
    
    await message.answer(LEXICON[lang]["vac_saved"])

@router.message(F.text.in_([LEXICON["ru"]["btn_my_vac"], LEXICON["kk"]["btn_my_vac"], LEXICON["en"]["btn_my_vac"]]))
async def cmd_my_vacancies_full(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    result = await session.execute(select(Vacancy).where(Vacancy.employer_id == message.from_user.id))
    vacancies = result.scalars().all()
    
    if not vacancies:
        await message.answer("У вас пока нет активных вакансий / Белсенді бос орындарыңыз жоқ / No active vacancies.")
        return
        
    for v in vacancies:
        app_result = await session.execute(select(Application).where(Application.vacancy_id == v.id))
        apps = app_result.scalars().all()
        
        text = (f"📌 <b>{v.title}</b>\n"
                f"💰 {v.salary}\n"
                f"👥 Откликов: {len(apps)}\n"
                f"📅 Дата: {v.created_at.strftime('%d.%m.%y')}")
        
        # Кнопка удаления (теперь она всегда есть)
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🗑 Удалить вакансию", callback_data=f"confirm_del_{v.id}")
        ]])
            
        await message.answer(text, reply_markup=markup, parse_mode="HTML")

# Функция просмотра откликов удалена по запросу пользователя

@router.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def process_decision(callback: CallbackQuery, session: AsyncSession):
    data_parts = callback.data.split("_")
    action = data_parts[0]
    app_id = int(data_parts[1])
    
    result_app = await session.execute(select(Application).where(Application.id == app_id))
    app = result_app.scalar_one_or_none()
    
    if not app:
        await callback.answer("Ошибка: отклик не найден", show_alert=True)
        return

    result_vac = await session.execute(select(Vacancy).where(Vacancy.id == app.vacancy_id))
    vacancy = result_vac.scalar_one_or_none()
    
    result_res = await session.execute(select(Resume).where(Resume.id == app.resume_id))
    resume = result_res.scalar_one_or_none()
    
    if not resume or not vacancy:
        await callback.answer("Ошибка: данные вакансии или резюме удалены", show_alert=True)
        return
    
    app.status = action
    await session.commit()
    
    if action == "accept":
        try:
            await callback.message.edit_text(callback.message.text + "\n\n✅ Принят / Қабылданды / Accepted!")
        except:
            pass
        
        employer_contact = f"@{callback.from_user.username}" if callback.from_user.username else f"<a href='tg://user?id={callback.from_user.id}'>Профиль</a>"
        
        try:
            await callback.bot.send_message(
                resume.user_id,
                f"🎉 <b>Вас пригласили на вакансию! / Сізді жұмысқа шақырды! / You were invited!</b>\n\n"
                f"📌 Вакансия: '{vacancy.title}'\n"
                f"🔗 Контакт работодателя: {employer_contact}",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка при уведомлении соискателя: {e}")
    else:
        try:
            await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонен / Бас тартылды / Rejected.")
        except:
            pass
            
        try:
            await callback.bot.send_message(
                resume.user_id,
                f"😔 Отказ по вакансии / Бос орын бойынша бас тарту / Rejection for: '{vacancy.title}'."
            )
        except Exception as e:
            print(f"Ошибка при уведомлении соискателя (отказ): {e}")
            
    await callback.answer()

# --- УДАЛЕНИЕ ВАКАНСИИ (ПОДТВЕРЖДЕНИЕ) ---
@router.callback_query(F.data.startswith("confirm_del_"))
async def confirm_delete_vacancy(callback: CallbackQuery):
    vac_id = callback.data.split("_")[2]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"delete_vac_{vac_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_del")
        ]
    ])
    await callback.message.edit_text(callback.message.text + "\n\n⚠️ Вы уверены, что хотите удалить эту вакансию?", reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data == "cancel_del")
async def cancel_delete(callback: CallbackQuery):
    # Убираем текст вопроса
    text = callback.message.text.split("\n\n⚠️ Вы уверены")[0]
    await callback.message.edit_text(text)
    await callback.answer("Удаление отменено")

@router.callback_query(F.data.startswith("delete_vac_"))
async def delete_vacancy(callback: CallbackQuery, session: AsyncSession):
    vac_id = int(callback.data.split("_")[2])
    
    # Сначала удаляем отклики (важно для базы)
    await session.execute(delete(Application).where(Application.vacancy_id == vac_id))
    # Затем саму вакансию
    await session.execute(delete(Vacancy).where(Vacancy.id == vac_id))
    await session.commit()
    
    await callback.message.edit_text("🗑 Вакансия успешно удалена!")
    await callback.answer()
