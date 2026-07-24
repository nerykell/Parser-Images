# -*- coding: utf-8 -*-
"""Internationalization for Parser-Images.

Supports Russian and English interfaces.
Usage:
    from parser_images.i18n import set_language, t, get_language
    set_language('en')
    print(t('menu_title'))
"""

TRANSLATIONS = {
    'ru': {
        # General
        'select_language': 'Выберите язык / Select language:',
        'lang_ru': '1. Русский',
        'lang_en': '2. English',
        'invalid_input': 'Неверный ввод, повторите попытку...',
        'press_enter_exit': 'Нажмите Enter, чтобы завершить...',
        'press_enter_back': 'Нажмите Enter, чтобы вернуться...',
        'press_enter_menu': 'Нажмите Enter, чтобы вернуться в меню...',
        'opening_editor': 'Открываю {} в редакторе...',
        'file_not_found': "Файл '{}' не найден.",
        'error': 'Ошибка: {}',

        # Menu
        'integrity_check': 'Проверка целостности файлов:',
        'missing_required': "Файл(ы) '{}' отсутствует(ют).",
        'menu_title': 'Parser-Images',
        'menu_author': 'Made by Nerykell\n',
        'menu_queries': '1. Изменить запросы',
        'menu_start': '2. Начать скачивание',
        'menu_duplicates': '3. Найти дубликаты',
        'menu_settings': '4. Настройки',
        'menu_exit': '5. Выход',
        'menu_choice': 'Выберите пункт (1-5): ',

        # Settings
        'settings_title': 'Настройки',
        'settings_characteristics': '1. Характеристики',
        'settings_image_quality': '2. Качество изображений',
        'settings_language': '3. Сменить язык',
        'settings_back': '4. Назад',
        'settings_choice': 'Выберите пункт (1-4): ',
        'settings_error': 'Ошибка обновления настроек.',
        'language_changed': 'Язык изменён: {}',

        # Image quality
        'image_quality_title': 'Качество Изображений',
        'quality_low': 'Малое',
        'quality_high': 'Высокое',
        'quality_low_option': '1. Малое (Google)',
        'quality_high_option': '2. Высокое (DuckDuckGo)',
        'quality_back': '3. Назад',
        'quality_choice': 'Выберите пункт (1-3): ',
        'quality_set_low': 'Установлен режим: Малое (Google)',
        'quality_set_high': 'Установлен режим: Высокое (DuckDuckGo)',
        'engine_ddg': 'DuckDuckGo',
        'engine_google': 'Google',
        'image_quality_info': 'Качество изображений: {} / {}',

        # Statistics
        'no_folders': 'Нет папок с изображениями.',
        'stored_images': 'На компьютере хранится:',
        'pcs': 'шт.',

        # Parser
        'launching_parser': 'Запуск парсера...',
        'stop_esc': 'Для остановки парсинга нажмите ESC (или Ctrl+C)',
        'stop_user': '\n[STOP] Парсинг остановлен пользователем.',
        'stop_ctrlc': '\n[STOP] Прервано пользователем (Ctrl+C).',
        'parsing_done': '\n[OK] Парсинг завершён.',
        'chrome_start': 'Chrome (качество: {})...',
        'ddg_start': 'DuckDuckGo (качество: {})...',
        'queries_not_found': 'Файл запросов не найден: {}',
        'queries_empty': 'Файл запросов пуст или не найден.',
        'warn_outside_group': "   [WARN] Строка '{}' вне группы, пропускаем.",

        # Query processing
        'single_header': '\n# {} ({})',
        'group_header': '\n# [ГРУППА] {} (цель: {})',
        'found_photos': '   Найдено {} фото на пк.',
        'skip': '   [SKIP] Уже сохранено {} фото (требуется {}). Пропускаю.',
        'base_query': '\n   [база] {} (нужно ещё: {})',
        'extra_query': '\n   [доп] {} (лимит допа: {}, нужно ещё: {})',
        'collecting': '   [{}] {} → сбор {} URL...',
        'no_url': '   [{}] Нет URL',
        'new_added': '   [{}] +{} новых ({}/{})',
        'no_new_extra': '   [доп] Не добавлено новых изображений, переходим к следующему...',
        'downloading_urls': '   Скачивание {} URL...',
        'total_saved': '\n   Уникальных сохранено (всего): {} → {}',
        'no_new': '   [NO] Не найдено ни одного нового изображения.',
        'warn_not_enough': '   [WARN] Не удалось дособрать до {}.',
        'query_time': '   Время обработки запроса: {}',

        # Reverse search
        'reverse_last_file': '\n   [REVERSE] Последний файл: {}',
        'reverse_missing': '   Не хватает {} изображений.',
        'reverse_prompt': '   Искать похожие изображения (reverse search)? [y/n]: ',
        'reverse_skip': '   [REVERSE] Пропускаем.',
        'reverse_launch': '   [REVERSE] Запускаем поиск по изображению...',
        'reverse_open': '   [REVERSE] Открываем Google Images...',
        'reverse_wait': '   [REVERSE] Ждём обработку...',
        'reverse_not_supported': '   [REVERSE] Reverse search не поддерживается для DuckDuckGo.',
        'reverse_error': '   [REVERSE] Ошибка reverse search: {}',
        'reverse_no_files': '   [REVERSE] Нет скачанных файлов для reverse search.',

        # DuckDuckGo
        'ddg_vqd_error': '   [DDG] Не удалось получить vqd-токен',
        'ddg_error': '   [DDG] Ошибка сбора URL: {}',

        # Cleaner
        'launching_cleaner': 'Запуск поиска дубликатов...',
        'cleaner_scan': '[INFO] Сканирование папки: {}',
        'cleaner_found_files': '[INFO] Найдено {} файлов для проверки.',
        'cleaner_no_duplicates': '[OK] Дубликаты не найдены.',
        'cleaner_found_groups': '[FOUND] {} групп дублей, всего файлов: {}',
        'cleaner_done': '\n[DONE] Процесс завершен.',
        'cleaner_unique': '   Уникальных файлов после очистки: {}',
        'cleaner_moved': "   '{}' Дубликатов перемещено в: {}",
        'cleaner_error_folder': "[ERROR] Папка '{}' не существует.",
        'cleaner_error_delete': '[ERROR] Не удалось удалить {}: {}',

        # Easter egg
        'sixty_seven': 'ахахахахахахаха сиксевен 67\n',
    },
    'en': {
        # General
        'select_language': 'Select language / Выберите язык:',
        'lang_ru': '1. Русский',
        'lang_en': '2. English',
        'invalid_input': 'Invalid input, please try again...',
        'press_enter_exit': 'Press Enter to exit...',
        'press_enter_back': 'Press Enter to go back...',
        'press_enter_menu': 'Press Enter to return to menu...',
        'opening_editor': 'Opening {} in editor...',
        'file_not_found': "File '{}' not found.",
        'error': 'Error: {}',

        # Menu
        'integrity_check': 'Checking file integrity:',
        'missing_required': "File(s) '{}' missing.",
        'menu_title': 'Parser-Images',
        'menu_author': 'Made by Nerykell\n',
        'menu_queries': '1. Edit queries',
        'menu_start': '2. Start downloading',
        'menu_duplicates': '3. Find duplicates',
        'menu_settings': '4. Settings',
        'menu_exit': '5. Exit',
        'menu_choice': 'Select option (1-5): ',

        # Settings
        'settings_title': 'Settings',
        'settings_characteristics': '1. Characteristics',
        'settings_image_quality': '2. Image quality',
        'settings_language': '3. Change language',
        'settings_back': '4. Back',
        'settings_choice': 'Select option (1-4): ',
        'settings_error': 'Error updating settings.',
        'language_changed': 'Language changed: {}',

        # Image quality
        'image_quality_title': 'Image Quality',
        'quality_low': 'Low',
        'quality_high': 'High',
        'quality_low_option': '1. Low (Google)',
        'quality_high_option': '2. High (DuckDuckGo)',
        'quality_back': '3. Back',
        'quality_choice': 'Select option (1-3): ',
        'quality_set_low': 'Mode set: Low (Google)',
        'quality_set_high': 'Mode set: High (DuckDuckGo)',
        'engine_ddg': 'DuckDuckGo',
        'engine_google': 'Google',
        'image_quality_info': 'Image quality: {} / {}',

        # Statistics
        'no_folders': 'No image folders found.',
        'stored_images': 'Stored on this computer:',
        'pcs': 'pcs',

        # Parser
        'launching_parser': 'Launching parser...',
        'stop_esc': 'Press ESC to stop parsing (or Ctrl+C)',
        'stop_user': '\n[STOP] Parsing stopped by user.',
        'stop_ctrlc': '\n[STOP] Interrupted by user (Ctrl+C).',
        'parsing_done': '\n[OK] Parsing completed.',
        'chrome_start': 'Chrome (quality: {})...',
        'ddg_start': 'DuckDuckGo (quality: {})...',
        'queries_not_found': 'Query file not found: {}',
        'queries_empty': 'Query file is empty or not found.',
        'warn_outside_group': "   [WARN] Line '{}' outside group, skipping.",

        # Query processing
        'single_header': '\n# {} ({})',
        'group_header': '\n# [GROUP] {} (target: {})',
        'found_photos': '   Found {} photos on pc.',
        'skip': '   [SKIP] Already saved {} photos (need {}). Skipping.',
        'base_query': '\n   [base] {} (still need: {})',
        'extra_query': '\n   [extra] {} (extra limit: {}, still need: {})',
        'collecting': '   [{}] {} → collecting {} URLs...',
        'no_url': '   [{}] No URLs',
        'new_added': '   [{}] +{} new ({}/{})',
        'no_new_extra': '   [extra] No new images added, moving to next...',
        'downloading_urls': '   Downloading {} URLs...',
        'total_saved': '\n   Total unique saved: {} → {}',
        'no_new': '   [NO] No new images found.',
        'warn_not_enough': '   [WARN] Could not collect {}.',
        'query_time': '   Query processing time: {}',

        # Reverse search
        'reverse_last_file': '\n   [REVERSE] Last file: {}',
        'reverse_missing': '   Missing {} images.',
        'reverse_prompt': '   Search for similar images (reverse search)? [y/n]: ',
        'reverse_skip': '   [REVERSE] Skipping.',
        'reverse_launch': '   [REVERSE] Launching image search...',
        'reverse_open': '   [REVERSE] Opening Google Images...',
        'reverse_wait': '   [REVERSE] Waiting for processing...',
        'reverse_not_supported': '   [REVERSE] Reverse search not supported for DuckDuckGo.',
        'reverse_error': '   [REVERSE] Reverse search error: {}',
        'reverse_no_files': '   [REVERSE] No downloaded files for reverse search.',

        # DuckDuckGo
        'ddg_vqd_error': '   [DDG] Failed to get vqd token',
        'ddg_error': '   [DDG] URL collection error: {}',

        # Cleaner
        'launching_cleaner': 'Launching duplicate finder...',
        'cleaner_scan': '[INFO] Scanning folder: {}',
        'cleaner_found_files': '[INFO] Found {} files to check.',
        'cleaner_no_duplicates': '[OK] No duplicates found.',
        'cleaner_found_groups': '[FOUND] {} duplicate groups, total files: {}',
        'cleaner_done': '\n[DONE] Process completed.',
        'cleaner_unique': '   Unique files after cleanup: {}',
        'cleaner_moved': "   '{}' Duplicates moved to: {}",
        'cleaner_error_folder': "[ERROR] Folder '{}' does not exist.",
        'cleaner_error_delete': '[ERROR] Failed to delete {}: {}',

        # Easter egg
        'sixty_seven': 'ahahahahahaha sixseven 67\n',
    }
}

_current_lang = 'en'


def set_language(lang):
    """Set current interface language.

    Args:
        lang: Language code ('ru' or 'en').
    """
    global _current_lang
    _current_lang = lang if lang in TRANSLATIONS else 'en'


def get_language():
    """Get current language code."""
    return _current_lang


def t(key, *args):
    """Get translated string by key.

    Args:
        key: Translation key.
        *args: Format arguments.

    Returns:
        Translated and formatted string.
    """
    text = TRANSLATIONS.get(_current_lang, TRANSLATIONS['en']).get(key, key)
    if args:
        return text.format(*args)
    return text