# D:\Python\django\myLibrary\app\app\utilities.py

import re

def translit_re(input_str):
    ''' Обеспечение транслитерации кириллицы (и другие символы - непотребности) в латиницу,
    re (регулярные выражения):
    Преимущества:
    Гибкость и контроль над процессом транслитерации с использованием регулярных выражений.
    Полный контроль над символами, которые подлежат замене.
    Недостатки:
    Требует более длинного кода, особенно если нужно обработать много разных символов.
    '''
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya', 'ґ': 'g', 'є': 'ie', 'ї': 'i', 'і': 'i',
        'ç': 'c', 'ş': 's', 'ğ': 'g', 'ı': 'i',
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'à': 'a', 'è': 'e', 'é': 'e', 'ê': 'e', 'ô': 'o', 'û': 'u', 'â': 'a',
        'а̑': 'a', 'э̑': 'e', 'и̑': 'i', 'о̑': 'o', 'у̑': 'u', 'ĭ': 'y',
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    }

    # Добавим символы, подлежащие замене
    translit_dict.update({
        '?': '_', '<': '_', '>': '_', ' ': '_', '~': '_', '@': '_', '"': '_', "'": '_', ':': '_',
        ';': '_', '#': '_', '$': '_', '&': '_', '*': '_', '(': '_', ')': '_', '\\': '_', '|': '_',
        '/': '_', '.': '_',
        '«': '_', '»': '_',
        ',': '_', '!': '_',
        '‐': '-', '−': '-', '–': '-', '—': '-', '-': '-',
        '“': '_', '”': '_', '„': '_',
        '…': '_', '№': '_', '+': '_',
    })

    # Заменяем все символы, кроме латинских букв и "-"
    output_str = ''.join([translit_dict.get(char.lower(), char) for char in input_str])

    # Заменяем множественные подчеркивания на одно
    output_str = re.sub('_+', '_', output_str)

    # Удаление подчеркиваний в начале и конце строки
    output_str = output_str.strip('_')

    # Заменяем множественные дефисы на одно
    output_str = re.sub('-+', '-', output_str)

    # Удаление дефисов в начале и конце строки
    output_str = output_str.strip('-')

    return output_str.lower()


'''Метод формирования имен загружаемых медио-файлов'''
def generate_file_name(instance, filename, file_type):
    if hasattr(instance, 'book'):
        # Это TorrentFile
        book = instance.book
    else:
        # Это ModelBooks
        book = instance

    authors = book.authors.all()
    author_slugs = '-'.join(author.slug for author in authors) if authors.exists() else "unknown"

    ext = filename.split('.')[-1]

    if book.work_type == 'cycle' and book.cycle:
        cycle_slug = book.cycle.slug
        if book.cycle_number:
            cycle_number = translit_re(book.cycle_number)
        else:
            cycle_number = "00"
        base_name = f"{book.slug}-{cycle_slug}-{cycle_number}-{author_slugs}"
    else:
        base_name = f"{book.slug}-{author_slugs}"

    if file_type == 'audio':
        count = book.audio_files.count() + 1
        new_name = f"{count:02d}-{base_name}.{ext}"
    elif file_type == 'image':
        count = book.book_images_set.count() + 1
        new_name = f"{count:02d}-{base_name}.{ext}"
    elif file_type == 'torrent':
        reader_slug = instance.reader.slug if hasattr(instance, 'reader') else "unknown-reader"
        new_name = f"{base_name}-({reader_slug}).{ext}"
    else:  # 'additional'
        new_name = f"{base_name}.{ext}"

    return new_name