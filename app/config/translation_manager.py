"""
Translation Manager for loading and accessing translated strings.

All UI text must come from translation JSON files.
No Persian characters should appear in Python source code.
"""

import json
from pathlib import Path
from typing import Dict, Optional


class TranslationManager:
    """
    Manages translation loading and retrieval.
    
    Loads translations from JSON files and provides a simple
    interface to get translated strings by key.
    """
    
    def __init__(self, language: str = "fa") -> None:
        """
        Initialize translation manager.
        
        Args:
            language: Language code (default: "fa" for Persian)
        """
        self.language = language
        self.translations: Dict[str, str] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translations from JSON file."""
        translations_dir = Path(__file__).parent.parent.parent / "translations"
        translation_file = translations_dir / f"{self.language}.json"
        
        if not translation_file.exists():
            raise FileNotFoundError(
                f"Translation file not found: {translation_file}"
            )
        
        try:
            with open(translation_file, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in translation file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load translations: {e}")
    
    def t(self, key: str) -> str:
        """
        Get translated string by key.
        
        Args:
            key: Translation key (English identifier)
            
        Returns:
            Translated string, or key itself if not found
        """
        return self.translations.get(key, key)
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get translated string with optional default.
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string, default, or key if no default provided
        """
        return self.translations.get(key, default or key)

