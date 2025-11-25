"""
Date utility functions for Shamsi (Persian/Iranian) calendar conversion.
All dates in the application should be displayed in Shamsi format.
"""

from datetime import date, datetime
from typing import Optional, Union
import jdatetime


def gregorian_to_shamsi(gregorian_date: Union[date, datetime, str]) -> jdatetime.datetime:
    """
    Convert Gregorian date to Shamsi (Persian) date.
    
    Args:
        gregorian_date: Gregorian date as date, datetime, or ISO string
        
    Returns:
        jdatetime.datetime object in Shamsi calendar
    """
    if isinstance(gregorian_date, str):
        # Try to parse ISO format
        if 'T' in gregorian_date:
            gregorian_date = datetime.fromisoformat(gregorian_date.replace('Z', '+00:00'))
        elif ' ' in gregorian_date:
            try:
                gregorian_date = datetime.strptime(gregorian_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                gregorian_date = datetime.strptime(gregorian_date.split(' ')[0], "%Y-%m-%d")
        else:
            gregorian_date = date.fromisoformat(gregorian_date)
    
    if isinstance(gregorian_date, datetime):
        return jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    elif isinstance(gregorian_date, date):
        return jdatetime.date.fromgregorian(date=gregorian_date)
    
    return gregorian_date


def format_shamsi_date(shamsi_date: Union[jdatetime.datetime, jdatetime.date], 
                       format_str: str = "%Y/%m/%d") -> str:
    """
    Format Shamsi date as string.
    
    Args:
        shamsi_date: Shamsi date object
        format_str: Format string (default: "%Y/%m/%d")
        
    Returns:
        Formatted date string
    """
    if isinstance(shamsi_date, jdatetime.datetime):
        return shamsi_date.strftime(format_str)
    elif isinstance(shamsi_date, jdatetime.date):
        return shamsi_date.strftime(format_str)
    return str(shamsi_date)


def format_date_for_display(gregorian_date: Union[date, datetime, str], 
                            format_str: str = "%Y/%m/%d") -> str:
    """
    Convert Gregorian date to Shamsi and format for display.
    
    Args:
        gregorian_date: Gregorian date as date, datetime, or ISO string
        format_str: Format string (default: "%Y/%m/%d")
        
    Returns:
        Formatted Shamsi date string
    """
    try:
        shamsi_date = gregorian_to_shamsi(gregorian_date)
        return format_shamsi_date(shamsi_date, format_str)
    except (ValueError, AttributeError, TypeError) as e:
        # Fallback to original string if conversion fails
        if isinstance(gregorian_date, str):
            return gregorian_date[:10] if len(gregorian_date) > 10 else gregorian_date
        return str(gregorian_date)


def get_current_shamsi_date() -> jdatetime.date:
    """
    Get current date in Shamsi calendar.
    
    Returns:
        Current Shamsi date
    """
    return jdatetime.date.today()


def get_current_shamsi_datetime() -> jdatetime.datetime:
    """
    Get current date and time in Shamsi calendar.
    
    Returns:
        Current Shamsi datetime
    """
    return jdatetime.datetime.now()


def shamsi_to_gregorian(shamsi_date: Union[jdatetime.date, jdatetime.datetime]) -> date:
    """
    Convert Shamsi date to Gregorian date.
    
    Args:
        shamsi_date: Shamsi date object
        
    Returns:
        Gregorian date object
    """
    if isinstance(shamsi_date, jdatetime.datetime):
        return shamsi_date.togregorian()
    elif isinstance(shamsi_date, jdatetime.date):
        return shamsi_date.togregorian()
    return shamsi_date



