# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 19:34:56 2026

@author: Boboxon
"""

# yangi_uz_trans.py - ODDIY VERSIYA
import re

def to_cyrillic(text):
    """Lotin matnni kirillga o'tkazish (soddalashtirilgan)"""
    # Lotin -> Kirill lug'ati
    mapping = {
        'a': 'а', 'A': 'А',
        'b': 'б', 'B': 'Б',
        'd': 'д', 'D': 'Д',
        'e': 'е', 'E': 'Е',
        'f': 'ф', 'F': 'Ф',
        'g': 'г', 'G': 'Г',
        'h': 'ҳ', 'H': 'Ҳ',
        'i': 'и', 'I': 'И',
        'j': 'ж', 'J': 'Ж',
        'k': 'к', 'K': 'К',
        'l': 'л', 'L': 'Л',
        'm': 'м', 'M': 'М',
        'n': 'н', 'N': 'Н',
        'o': 'о', 'O': 'О',
        'p': 'п', 'P': 'П',
        'q': 'қ', 'Q': 'Қ',
        'r': 'р', 'R': 'Р',
        's': 'с', 'S': 'С',
        't': 'т', 'T': 'Т',
        'u': 'у', 'U': 'У',
        'v': 'в', 'V': 'В',
        'x': 'х', 'X': 'Х',
        'y': 'й', 'Y': 'Й',
        'z': 'з', 'Z': 'З',
        'oʻ': 'ў', 'Oʻ': 'Ў', "o'": 'ў', "O'": 'Ў',
        'gʻ': 'ғ', 'Gʻ': 'Ғ', "g'": 'ғ', "G'": 'Ғ',
        'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш',
        'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
        'yo': 'ё', 'Yo': 'Ё', 'YO': 'Ё',
        'yu': 'ю', 'Yu': 'Ю', 'YU': 'Ю',
        'ya': 'я', 'Ya': 'Я', 'YA': 'Я',
        'ye': 'е', 'Ye': 'Е', 'YE': 'Е',
    }
    
    # Avval kombinatsiyalarni (sh, ch, oʻ, gʻ, etc.)
    for latin, kirill in mapping.items():
        if len(latin) > 1:  # Faqat kombinatsiyalar
            text = text.replace(latin, kirill)
    
    # Keyin bitta harflarni
    for latin, kirill in mapping.items():
        if len(latin) == 1:  # Faqat bitta harflar
            text = text.replace(latin, kirill)
    
    return text

def to_latin(text):
    """Kirill matnni lotinga o'tkazish (soddalashtirilgan)"""
    # Kirill -> Lotin lug'ati
    mapping = {
        'а': 'a', 'А': 'A',
        'б': 'b', 'Б': 'B',
        'в': 'v', 'В': 'V',
        'г': 'g', 'Г': 'G',
        'д': 'd', 'Д': 'D',
        'е': 'e', 'Е': 'E',
        'ё': 'yo', 'Ё': 'Yo',
        'ж': 'j', 'Ж': 'J',
        'з': 'z', 'З': 'Z',
        'и': 'i', 'И': 'I',
        'й': 'y', 'Й': 'Y',
        'к': 'k', 'К': 'K',
        'л': 'l', 'Л': 'L',
        'м': 'm', 'М': 'M',
        'н': 'n', 'Н': 'N',
        'о': 'o', 'О': 'O',
        'п': 'p', 'П': 'P',
        'р': 'r', 'Р': 'R',
        'с': 's', 'С': 'S',
        'т': 't', 'Т': 'T',
        'у': 'u', 'У': 'U',
        'ф': 'f', 'Ф': 'F',
        'х': 'x', 'Х': 'X',
        'ц': 'ts', 'Ц': 'Ts',
        'ч': 'ch', 'Ч': 'Ch',
        'ш': 'sh', 'Ш': 'Sh',
        'ъ': "'", 'Ъ': "'",
        'ь': '', 'Ь': '',
        'э': 'e', 'Э': 'E',
        'ю': 'yu', 'Ю': 'Yu',
        'я': 'ya', 'Я': 'Ya',
        'ў': 'oʻ', 'Ў': 'Oʻ',
        'қ': 'q', 'Қ': 'Q',
        'ғ': 'gʻ', 'Ғ': 'Gʻ',
        'ҳ': 'h', 'Ҳ': 'H',
    }
    
    # Avval kombinatsiyalarni
    for kirill, latin in mapping.items():
        if len(latin) > 1:  # Faqat kombinatsiyalar
            text = text.replace(kirill, latin)
    
    # Keyin bitta harflarni
    for kirill, latin in mapping.items():
        if len(latin) == 1:  # Faqat bitta harflar
            text = text.replace(kirill, latin)
    
    return text

# Test qilish uchun
if __name__ == "__main__":
    test = "Salom O'zbekiston"
    print("Test:", test)
    print("Kirill:", to_cyrillic(test))
    print("Qayta lotin:", to_latin(to_cyrillic(test)))