import os
import sys

def resource_path(relative_path):
    """Dosya yolunu belirler."""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller geçici dosya dizini
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
