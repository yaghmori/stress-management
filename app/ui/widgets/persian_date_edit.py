"""
Persian (Jalali/Shamsi) date picker widget.
"""

from PySide6.QtWidgets import QDateEdit, QLineEdit
from PySide6.QtCore import Qt, QDate, Signal, QDateTime
from PySide6.QtGui import QFont
import jdatetime
from datetime import date, datetime
from typing import Optional
import re

from app.config.date_utils import (
    gregorian_to_shamsi,
    shamsi_to_gregorian,
    format_shamsi_date,
    get_current_shamsi_date
)


class PersianDateEdit(QDateEdit):
    """
    Date picker widget that displays and handles Persian (Jalali/Shamsi) dates.
    
    Internally uses Gregorian dates for Qt compatibility, but displays
    and accepts Persian dates from the user.
    """
    
    shamsiDateChanged = Signal(jdatetime.date)
    
    def __init__(self, parent=None):
        """Initialize Persian date edit widget."""
        super().__init__(parent)
        
        # Set display format - we'll override text display
        self.setDisplayFormat("yyyy/MM/dd")
        self.setCalendarPopup(True)
        
        # Set current date to today in Persian calendar
        self._updating = False
        self.setShamsiDate(get_current_shamsi_date())
        
        # Connect to date changed signal to update display
        super().dateChanged.connect(self._on_internal_date_changed)
        
        # Connect to line edit to handle text input
        line_edit = self.lineEdit()
        if line_edit:
            line_edit.editingFinished.connect(self._on_text_edited)
    
    def setShamsiDate(self, shamsi_date: jdatetime.date) -> None:
        """
        Set the date using a Persian (Shamsi) date.
        
        Args:
            shamsi_date: Persian date as jdatetime.date
        """
        if isinstance(shamsi_date, jdatetime.datetime):
            shamsi_date = shamsi_date.date()
        
        # Convert to Gregorian for internal storage
        gregorian_date = shamsi_date.togregorian()
        qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        self._updating = True
        super().setDate(qdate)
        self._updating = False
        self._update_display()
    
    def getShamsiDate(self) -> jdatetime.date:
        """
        Get the current date as a Persian (Shamsi) date.
        
        Returns:
            Persian date as jdatetime.date
        """
        qdate = super().date()
        gregorian_date = date(qdate.year(), qdate.month(), qdate.day())
        return jdatetime.date.fromgregorian(date=gregorian_date)
    
    def getGregorianDate(self) -> date:
        """
        Get the current date as a Gregorian date (for database storage).
        
        Returns:
            Gregorian date as datetime.date
        """
        qdate = super().date()
        return date(qdate.year(), qdate.month(), qdate.day())
    
    def _on_internal_date_changed(self, qdate: QDate) -> None:
        """Handle internal date change and update display."""
        if not self._updating:
            self._update_display()
            shamsi_date = self.getShamsiDate()
            self.shamsiDateChanged.emit(shamsi_date)
    
    def _update_display(self) -> None:
        """Update the display to show Persian date format."""
        shamsi_date = self.getShamsiDate()
        # Format as Persian date string
        date_str = format_shamsi_date(shamsi_date, "%Y/%m/%d")
        
        # Update the line edit text directly
        line_edit = self.lineEdit()
        if line_edit:
            # Temporarily disconnect to avoid recursion
            line_edit.blockSignals(True)
            line_edit.setText(date_str)
            line_edit.blockSignals(False)
    
    def setDate(self, date_or_qdate) -> None:
        """
        Set date - accepts QDate, date, or jdatetime.date.
        
        Args:
            date_or_qdate: Date as QDate, datetime.date, or jdatetime.date
        """
        if isinstance(date_or_qdate, jdatetime.date) or isinstance(date_or_qdate, jdatetime.datetime):
            self.setShamsiDate(date_or_qdate)
        elif isinstance(date_or_qdate, (date, datetime)):
            # Convert Gregorian to Persian first, then set
            shamsi_date = gregorian_to_shamsi(date_or_qdate)
            if isinstance(shamsi_date, jdatetime.datetime):
                shamsi_date = shamsi_date.date()
            self.setShamsiDate(shamsi_date)
        else:
            # Assume it's a QDate
            self._updating = True
            super().setDate(date_or_qdate)
            self._updating = False
            self._update_display()
    
    def date(self) -> QDate:
        """Get the date as QDate (Gregorian)."""
        return super().date()
    
    def _on_text_edited(self) -> None:
        """Handle text editing - try to parse Persian date input."""
        line_edit = self.lineEdit()
        if not line_edit:
            return
        
        text = line_edit.text().strip()
        if not text:
            return
        
        # Try to parse Persian date format (YYYY/MM/DD or YYYY-MM-DD)
        persian_date_pattern = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
        match = re.match(persian_date_pattern, text)
        
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                
                # Validate Persian date
                if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                    shamsi_date = jdatetime.date(year, month, day)
                    self.setShamsiDate(shamsi_date)
                    return
            except (ValueError, jdatetime.JalaliDateError):
                pass
        
        # If parsing failed, try to let QDateEdit handle it (Gregorian)
        # The display will be updated by _on_internal_date_changed
    
    def textFromDateTime(self, dt: QDateTime) -> str:
        """Override to show Persian date in text."""
        qdate = dt.date()
        gregorian_date = date(qdate.year(), qdate.month(), qdate.day())
        try:
            shamsi_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return format_shamsi_date(shamsi_date, "%Y/%m/%d")
        except Exception:
            return super().textFromDateTime(dt)

