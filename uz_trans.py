# uz_trans.py - Kirill-Lotin transliteratsiya

# 1. LOTIN -> KIRILL (o'zbek lotinidan)
def to_cyrillic(text):
    """Lotin matnni Kirillga o'giradi"""
    if not text:
        return ""
    
    # Kichik harflar
    latin_to_cyrillic = {
        'sh': 'ш', 'ch': 'ч', 'yo': 'ё', "yo'": 'ё', 'yo\'': 'ё',
        'yu': 'ю', 'ya': 'я', 'ye': 'е', 
        'o\'': 'ў', "o'": 'ў',
        'g\'': 'ғ', "g'": 'ғ',
        
        # Bitta harflar
        'a': 'а', 'b': 'б', 'd': 'д', 'e': 'е', 'f': 'ф',
        'g': 'г', 'h': 'ҳ', 'i': 'и', 'j': 'ж', 'k': 'к',
        'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
        'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
        'v': 'в', 'x': 'х', 'y': 'й', 'z': 'з',
        
        # Katta harflar
        'A': 'А', 'B': 'Б', 'D': 'Д', 'E': 'Е', 'F': 'Ф',
        'G': 'Г', 'H': 'Ҳ', 'I': 'И', 'J': 'Ж', 'K': 'К',
        'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П',
        'Q': 'Қ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
        'V': 'В', 'X': 'Х', 'Y': 'Й', 'Z': 'З',
        
        # Maxsus belgilar (lotinda bo'lsa)
        "'": 'ъ',  # apostrof -> qattiqlik belgisi
        "`": 'ъ',  # backtick ham
        '"': 'ъ',  # qo'shtirnoq
    }
    
    result = []
    i = 0
    text_len = len(text)
    
    while i < text_len:
        matched = False
        
        # Uzun kombinatsiyalarni birinchi tekshirish
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
    """Kirill matnni Lotinga o'giradi"""
    if not text:
        return ""
    
    # ASOSIY LUG'AT - Kichik harflar
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'j', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 
        'щ': 'shch',  # Щ harfi uchun to'liq "shch"
        'ъ': '',      # QATTIQLIK BELGISI - O'TKAZILMAYDI
        'ы': 'i',     # O'zbek tilida "ы" yo'q, "i" deb o'tkaziladi
        'ь': '',      # YUMSHATISH BELGISI - O'TKAZILMAYDI
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'ў': 'o\'', 'қ': 'q', 'ҳ': 'h', 'ғ': 'g\'',
        
        # Katta harflar
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'J', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 
        'Щ': 'Shch',  # Katta Щ harfi
        'Ъ': '',      # KATTA QATTIQLIK BELGISI
        'Ы': 'I',     # KATTA Ы harfi
        'Ь': '',      # KATTA YUMSHATISH BELGISI
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'Ў': 'O\'', 'Қ': 'Q', 'Ҳ': 'H', 'Ғ': 'G\'',
    }
    
    # QO'SHIMCHA: "с" va "х" alohida kombinatsiyalari
    special_combinations = {
        'сх': 'sx', 'Сх': 'Sx', 'сХ': 'sX', 'СХ': 'SX',
    }
    
    result = []
    i = 0
    text_len = len(text)
    
    while i < text_len:
        # 1. Maxsus kombinatsiyalarni tekshirish (2 belgi)
        if i + 1 < text_len:
            two_chars = text[i:i+2]
            if two_chars in special_combinations:
                result.append(special_combinations[two_chars])
                i += 2
                continue
        
        # 2. Oddiy bitta belgini o'tkazish
        char = text[i]
        
        if char in cyrillic_to_latin:
            # Harfning holatiga qarab
            if i + 1 < text_len:
                next_char = text[i+1]
                # Kichik harf bo'lsa, kichik lotin harf
                if char.islower():
                    result.append(cyrillic_to_latin[char])
                # Katta harf bo'lsa
                elif char.isupper():
                    # Agar keyingi harf ham katta bo'lsa
                    if next_char.isupper():
                        result.append(cyrillic_to_latin[char])
                    else:
                        # Faqat birinchi harf katta bo'lsa
                        trans = cyrillic_to_latin[char]
                        if len(trans) > 1:
                            # "Shch", "Yo" kabi kombinatsiyalar
                            result.append(trans[0].upper() + trans[1:])
                        else:
                            result.append(trans.upper())
                else:
                    result.append(cyrillic_to_latin[char])
            else:
                result.append(cyrillic_to_latin[char])
        else:
            # Lug'atda yo'q belgilar
            result.append(char)
        
        i += 1
    
    return ''.join(result)

# 3. ALTERNATIV VERSIYA: Soddaroq
def to_latin_simple(text):
    """Soddaroq versiya - faqat asosiy harflar"""
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'j', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'i', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'ў': 'o\'', 'қ': 'q', 'ҳ': 'h', 'ғ': 'g\'',
        
        # Katta harflar
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'Yo', 'Ж': 'J', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'I', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'Ў': 'O\'', 'Қ': 'Q', 'Ҳ': 'H', 'Ғ': 'G\'',
    }
    
    result = []
    for char in text:
        if char in mapping:
            result.append(mapping[char])
        else:
            result.append(char)
    
    return ''.join(result)

# 4. TEKSHIRISH FUNKSIYASI
def test_specific_chars():
    """Maxsus harflarni test qilish"""
    print("🔍 MAXSUS HARFLAR TESTI:")
    print("=" * 50)
    
    test_cases = [
        ("ь", "", "Yumshatish belgisi"),
        ("ъ", "", "Qattiqlik belgisi"),
        ("щ", "shch", "Щ harfi"),
        ("ы", "i", "Ы harfi"),
        ("Ь", "", "Katta yumshatish"),
        ("Ъ", "", "Katta qattiqlik"),
        ("Щ", "Shch", "Katta Щ"),
        ("Ы", "I", "Katta Ы"),
    ]
    
    for kirill, expected_latin, description in test_cases:
        # to_latin funksiyasi bilan
        result1 = to_latin(kirill)
        # to_latin_simple funksiyasi bilan
        result2 = to_latin_simple(kirill)
        
        passed1 = result1 == expected_latin
        passed2 = result2 == expected_latin
        
        print(f"Kirill: '{kirill}'")
        print(f"Kutilgan: '{expected_latin}'")
        print(f"to_latin: '{result1}' {'✅' if passed1 else '❌'}")
        print(f"to_latin_simple: '{result2}' {'✅' if passed2 else '❌'}")
        print(f"Izoh: {description}")
        print("-" * 40)
    
    # Qo'shimcha test
    print("\n📝 QO'SHIMCHA MATNLAR:")
    print("=" * 40)
    
    sentences = [
        ("вьетнам", "vyetnam", "ь belgisi bilan"),
        ("подъезд", "podezd", "ъ belgisi bilan"),
        ("щука", "shchuka", "щ harfi bilan"),
        ("мышь", "mysh", "ы va ь bilan"),
    ]
    
    for kirill, expected, izoh in sentences:
        result = to_latin(kirill)
        print(f"{kirill} → {result} (kutilgan: {expected}) {izoh}")

# Fayl bajarilganda testni o'tkazish
if __name__ == "__main__":
    test_specific_chars()
    
    # Qaysi funksiyani ishlatishni so'rash
    print("\n💡 Maslahat: Agar to_latin ishlamasa, main.py da to_latin_simple dan foydalaning")