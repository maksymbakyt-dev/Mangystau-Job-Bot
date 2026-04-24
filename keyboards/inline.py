from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import LEXICON

def get_apply_keyboard(vacancy_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=LEXICON[lang]["btn_apply"], callback_data=f"apply_{vacancy_id}")]
        ]
    )

def get_employer_decision_keyboard(application_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON[lang]["btn_accept"], callback_data=f"accept_{application_id}"),
                InlineKeyboardButton(text=LEXICON[lang]["btn_reject"], callback_data=f"reject_{application_id}")
            ]
        ]
    )
