# uz_trans.py - Kirill-Lotin transliteratsiya

# 1. LOTIN -> KIRILL (o'zbek lotinidan)
def to_cyrillic(text):
    if not text:
        return ""
    
    # Lug'atni to'g'ri tartibda (uzun kombinatsiyalar birinchi)
    latin_to_cyrillic = {
        'sh': 'ш', 'ch': 'ч', 'yo': 'ё', 'yo\'': 'ё', "yo'": 'ё',
        'yu': 'ю', 'ya': 'я', 'ye': 'е', 
        'o\'': 'ў', "o'": 'ў',
        'g\'': 'ғ', "g'": 'ғ',
        '\'': 'ъ',  # apostrof -> qattiqlik belgisi (ixtiyoriy)
        
        'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф',
        'g': 'г', 'h': 'ҳ', 'i': 'и', 'j': 'ж', 'k': 'к',
        'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
        'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
        'v': 'в', 'x': 'х', 'y': 'й', 'z': 'з',
        'A': 'А', 'B': 'Б', 'D': 'Д', 'E': 'Е', 'F': 'Ф',
        'G': 'Г', 'H': 'Ҳ', 'I': 'И', 'J': 'Ж', 'K': 'К',
        'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П',
        'Q': 'Қ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
        'V': 'В', 'X': 'Х', 'Y': 'Й', 'Z': 'З',
    }
    
    result = []
    i = 0
    text_len = len(text)
    
    while i < text_len:
        matched = False
        
        # 2 yoki 3 belgili kombinatsiyalarni tekshirish
        for length in [3, 2, 1]:
            if i + length <= text_len:
                segment = text[i:i+length]
                if segment in latin_to_cyrillic:
                    result.append(latin_to_cyrillic[segment])
                    i += length
                    matched = True
                    break
        
        if not matched:
            # Belgilarni o'zgartirmasdan qoldirish
            result.append(text[i])
            i += 1
    
    return ''.join(result)

# 2. KIRILL -> LOTIN (kirillidan o'zbek lotiniga)
def to_latin(text):
    if not text:
        return ""
    
    # Kirill -> Lotin lug'ati
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'j', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sh',  # "щ" harfi "sh" deb o'tkaziladi
        'ъ': '',   # QATTIQLIK BELGISI - O'TKAZILMAYDI
        'ы': 'i',  # O'zbek tilida "ы" yo'q, "i" deb o'tkaziladi
        'ь': '',   # YUMSHATISH BELGISI - O'TKAZILMAYDI
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'ў': 'o\'', 'қ': 'q', 'ҳ': 'h', 'ғ': 'g\'',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'J', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Sh',
        'Ъ': '',   # KATTA QATTIQLIK BELGISI - O'TKAZILMAYDI
        'Ы': 'I',  # KATTA "Ы" harfi
        'Ь': '',   # KATTA YUMSHATISH BELGISI - O'TKAZILMAYDI
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'Ў': 'O\'', 'Қ': 'Q', 'Ҳ': 'H', 'Ғ': 'G\'',
    }
    
    result = []
    i = 0
    text_len = len(text)
    
    while i < text_len:
        char = text[i]
        
        # Maxsus kombinatsiyalar uchun tekshirish
        if i + 1 < text_len:
            two_chars = text[i:i+2]
            
            # "с" dan keyin "h" bo'lsa
            if two_chars.lower() in ['сх', 'Сх', 'сХ', 'СХ']:
                if two_chars.isupper():
                    result.append('Sh')
                elif two_chars[0].isupper():
                    result.append('Sh')
                else:
                    result.append('sh')
                i += 2
                continue
        
        # Oddiy lug'at orqali o'tkazish
        if char in cyrillic_to_latin:
            result.append(cyrillic_to_latin[char])
        else:
            # O'zgarmagan belgilar
            result.append(char)
        
        i += 1
    
    return ''.join(result)

# 3. TEKSHIRISH FUNKSIYASI
def test_transliteration():
    """Transliteratsiyani test qilish"""
    
    # Test holatlari
    test_cases = [
        ("salom", "салом"),
        ("o'zbek", "ўзбек"),
        ("g'alaba", "ғалаба"),
        ("shahar", "шаҳар"),
        ("choy", "чой"),
        ("yo'l", "ёл"),
        ("kitob", "китоб"),
        ("ь", ""),  # "ь" o'tkazilmasin
        ("ъ", ""),  # "ъ" o'tkazilmasin
        ("ы", "i"), # "ы" -> "i"
        ("щ", "sh"), # "щ" -> "sh"
    ]
    
    print("🔍 Transliteratsiya testi:")
    print("=" * 40)
    
    all_passed = True
    
    for latin, expected_kirill in test_cases:
        # Lotin -> Kirill
        result_kirill = to_cyrillic(latin)
        passed = result_kirill == expected_kirill
        
        # Kirill -> Lotin (teskari)
        result_latin = to_latin(expected_kirill)
        
        print(f"Test: '{latin}' -> '{result_kirill}'")
        print(f"Kutilgan: '{expected_kirill}'")
        print(f"Teskari: '{result_latin}'")
        print(f"✅ O'tdi" if passed else f"❌ Yiqildi")
        print("-" * 30)
        
        if not passed:
            all_passed = False
    
    return all_passed

# Fayl bajarilganda testni o'tkazish
if __name__ == "__main__":
    if test_transliteration():
        print("\n🎉 Barcha testlar muvaffaqiyatli o'tdi!")
    else:
        print("\n⚠️ Ba'zi testlar yiqildi, kodni tekshiring.")