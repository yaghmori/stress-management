"""
Font Manager for loading and managing custom fonts.
"""

from pathlib import Path
from PySide6.QtGui import QFontDatabase, QFont


class FontManager:
    """Manages loading and access to custom fonts."""
    
    _fonts_loaded = False
    _font_family = "Vazirmatn"
    
    @classmethod
    def load_fonts(cls) -> bool:
        """
        Load custom fonts from the fonts directory.
        
        Returns:
            True if fonts were loaded successfully, False otherwise
        """
        if cls._fonts_loaded:
            return True
        
        fonts_dir = Path(__file__).parent / "fonts"
        
        # Try to load TTF font first (more compatible)
        ttf_font_path = fonts_dir / "Vazirmatn[wght].ttf"
        woff2_font_path = fonts_dir / "Vazirmatn[wght].woff2"
        
        font_loaded = False
        
        # Load TTF font
        if ttf_font_path.exists():
            try:
                font_id = QFontDatabase.addApplicationFont(str(ttf_font_path))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        cls._font_family = families[0]
                        font_loaded = True
            except Exception as e:
                print(f"Failed to load TTF font: {e}")
        
        # Fallback to WOFF2 if TTF failed
        if not font_loaded and woff2_font_path.exists():
            try:
                font_id = QFontDatabase.addApplicationFont(str(woff2_font_path))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        cls._font_family = families[0]
                        font_loaded = True
            except Exception as e:
                print(f"Failed to load WOFF2 font: {e}")
        
        cls._fonts_loaded = font_loaded
        return font_loaded
    
    @classmethod
    def get_font(cls, point_size: int = 10, bold: bool = False, weight: int = None) -> QFont:
        """
        Get a QFont instance with the loaded custom font.
        
        Args:
            point_size: Font point size (default: 10)
            bold: Whether font should be bold (default: False)
            weight: Font weight (100-900, default: None uses normal weight)
            
        Returns:
            QFont instance configured with the custom font
        """
        font = QFont(cls._font_family, point_size)
        
        if bold:
            font.setBold(True)
        elif weight is not None:
            font.setWeight(weight)
        
        return font
    
    @classmethod
    def get_font_family(cls) -> str:
        """
        Get the loaded font family name.
        
        Returns:
            Font family name string
        """
        return cls._font_family
    
    @classmethod
    def is_font_loaded(cls) -> bool:
        """
        Check if fonts have been loaded.
        
        Returns:
            True if fonts are loaded, False otherwise
        """
        return cls._fonts_loaded

