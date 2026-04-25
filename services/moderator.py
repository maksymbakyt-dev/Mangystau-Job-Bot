import re

# Список запрещенных паттернов (регулярные выражения)
# Сюда входят интим-услуги, наркотики, вебкам и сомнительные финансовые схемы
FORBIDDEN_PATTERNS = [
    r"секс", r"интим", r"массаж.*девуш", r"вебка", r"эскорт", r"эротич",
    r"заклад", r"курьер.*пакет", r"нарко", r"псевдо", r"выплаты.*каждый.*день",
    r"18\+", r"спонсор", r"встреч", r"легкие.*деньги", r"быстрый.*доход"
]

def is_content_safe(text: str) -> bool:
    """
    Проверяет текст на наличие запрещенного контента.
    Возвращает True, если текст безопасен, и False, если найден спам или мат.
    """
    if not text:
        return True
        
    text_lower = text.lower()
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text_lower):
            return False
            
    # Дополнительная проверка на чрезмерное количество капса (признак спама)
    caps_count = sum(1 for char in text if char.isupper())
    if len(text) > 20 and caps_count / len(text) > 0.7:
        return False
        
    return True
