import json
import os

def load_translations():
    translations = {}
    i18n_path = "i18n"
    if not os.path.exists(i18n_path):
        return translations
    
    for filename in os.listdir(i18n_path):
        if filename.endswith(".json"):
            lang_code = filename[:-5]
            with open(os.path.join(i18n_path, filename), "r", encoding="utf-8") as f:
                translations[lang_code] = json.load(f)
    return translations

TRANSLATIONS = load_translations()

def get_text(locale: str, key: str, **kwargs) -> str:
    text = TRANSLATIONS.get(locale, {}).get(key)
    
    if text is None:
        text = TRANSLATIONS.get("en", {}).get(key, key)
        
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
            
    return text