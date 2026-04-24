from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from locales import LEXICON

def get_role_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LEXICON[lang]["btn_seeker"])],
            [KeyboardButton(text=LEXICON[lang]["btn_employer"])]
        ],
        resize_keyboard=True
    )

def get_seeker_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LEXICON[lang]["btn_my_resume"])],
            [KeyboardButton(text=LEXICON[lang]["btn_find_vacancies"])],
            [KeyboardButton(text=LEXICON[lang]["btn_send_photo"])]
        ],
        resize_keyboard=True
    )

def get_employer_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LEXICON[lang]["btn_create_vac"])],
            [KeyboardButton(text=LEXICON[lang]["btn_my_vac"])],
            [KeyboardButton(text=LEXICON[lang]["btn_send_photo"])]
        ],
        resize_keyboard=True
    )

def get_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Қазақша 🇰🇿", callback_data="lang_kk")],
            [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
            [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
        ]
    )
