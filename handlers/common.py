from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram.fsm.context import FSMContext

from database.models import User
from keyboards.reply import get_role_keyboard, get_seeker_main_keyboard, get_employer_main_keyboard, get_lang_keyboard
from locales import LEXICON

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            tg_id=message.from_user.id,
            name=message.from_user.full_name
        )
        session.add(user)
        await session.commit()
        await message.answer("Тілді таңдаңыз / Выберите язык / Choose language:", reply_markup=get_lang_keyboard())
    else:
        lang = user.language
        if not user.role:
            await message.answer(LEXICON[lang]["welcome"], reply_markup=get_role_keyboard(lang))
        else:
            if user.role == "seeker":
                await message.answer(LEXICON[lang]["welcome_back"], reply_markup=get_seeker_main_keyboard(lang))
            else:
                await message.answer(LEXICON[lang]["welcome_back"], reply_markup=get_employer_main_keyboard(lang))

@router.callback_query(F.data.startswith("lang_"))
async def process_lang(callback: CallbackQuery, session: AsyncSession):
    lang_code = callback.data.split("_")[1]
    
    result = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
    user = result.scalar_one_or_none()
    
    if user:
        user.language = lang_code
        await session.commit()
        
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(LEXICON[lang_code]["welcome"], reply_markup=get_role_keyboard(lang_code))
    await callback.answer()

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_seeker"], LEXICON["kk"]["btn_seeker"], LEXICON["en"]["btn_seeker"]])
async def register_seeker(message: Message, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user:
        user.role = "seeker"
        await session.commit()
        lang = user.language
        await message.answer(LEXICON[lang]["role_seeker_set"], reply_markup=get_seeker_main_keyboard(lang))

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_employer"], LEXICON["kk"]["btn_employer"], LEXICON["en"]["btn_employer"]])
async def register_employer(message: Message, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    if user:
        user.role = "employer"
        await session.commit()
        lang = user.language
        await message.answer(LEXICON[lang]["role_employer_set"], reply_markup=get_employer_main_keyboard(lang))

@router.message(lambda msg: msg.text in [LEXICON["ru"]["btn_send_photo"], LEXICON["kk"]["btn_send_photo"], LEXICON["en"]["btn_send_photo"]])
async def send_photo_instruction(message: Message, session: AsyncSession):
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    lang = user.language if user else "ru"
    await message.answer(LEXICON[lang]["photo_inst"])

# ID вашей группы для сбора объявлений
ADMIN_GROUP_ID = -5177804602

@router.message(F.photo)
async def handle_photo(message: Message, session: AsyncSession):
    import os
    from datetime import datetime
    
    # Сохраняем локально (на всякий случай)
    if not os.path.exists("photos"):
        os.makedirs("photos")
        
    photo_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(photo_id)
    file_path = file_info.file_path
    
    filename = f"photos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{message.from_user.id}.jpg"
    await message.bot.download_file(file_path, filename)
    
    # Пересылаем фото в вашу группу
    user_info = f"📸 Новое фото объявления!\n" \
                f"👤 От: {message.from_user.full_name}\n" \
                f"🆔 ID: {message.from_user.id}\n" \
                f"🔗 Username: @{message.from_user.username if message.from_user.username else 'нет'}"
    
    try:
        await message.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_id,
            caption=user_info
        )
    except Exception as e:
        print(f"Ошибка при отправке в группу: {e}")

    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()
    lang = user.language if user else "ru"
    
    await message.answer(LEXICON[lang]["photo_saved"])
