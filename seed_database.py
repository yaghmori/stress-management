"""
Database seeder script.
Seeds the database with exercises and anxiety tests.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config.config import setup_logging
from app.data.database import get_database
import logging

logger = logging.getLogger(__name__)


def seed_exercises(db) -> None:
    """Seed exercises table."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if exercises already exist
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] > 0:
        logger.info("Exercises already exist, skipping seed")
        return
    
    exercises = [
        ('تنفس عمیق ۴-۷-۸', 'تکنیک تنفس آرام‌ساز برای کاهش سریع استرس.', 5, 'breathing', 1),
        ('تنفس دیافراگمی', 'تنفس آرام با تمرکز بر دیافراگم جهت کنترل اضطراب.', 4, 'breathing', 1),
        ('مدیتیشن ذهن‌آگاهی', 'تمرکز بر لحظه حال برای کاهش حواس‌پرتی و اضطراب.', 10, 'meditation', 1),
        ('مدیتیشن اسکن بدن', 'آگاه‌سازی از تنش‌های بدنی و رهاسازی آن.', 12, 'meditation', 1),
        ('ریلکسیشن عضلانی تدریجی', 'انقباض و رهاسازی عضلات برای کاهش تنش.', 8, 'relaxation', 1),
        ('نوشتن نگرانی‌ها', 'ثبت نگرانی‌ها روی کاغذ برای تخلیه ذهن.', 7, 'journaling', 1),
        ('پیاده‌روی سبک', 'حرکت ملایم برای بهبود خلق و سطح استرس.', 15, 'activity', 1),
        ('کشش‌های سبک', 'حرکات کششی برای رهاسازی تنش فیزیکی.', 6, 'stretching', 1),
    ]
    
    cursor.executemany(
        "INSERT INTO exercises (name, description, duration, type, is_active) VALUES (?, ?, ?, ?, ?)",
        exercises
    )
    conn.commit()
    logger.info(f"Seeded {len(exercises)} exercises")


def seed_anxiety_tests(db) -> None:
    """Seed anxiety tests with PSS10 and PSS5."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if tests already exist
    cursor.execute("SELECT COUNT(*) FROM anxiety_tests")
    count = cursor.fetchone()[0]
    logger.info(f"Current test count: {count}")
    if count > 0:
        logger.info("Anxiety tests already exist, skipping seed")
        return
    
    # PSS10 Test
    pss10_interpretation = json.dumps({
        "method": "reverse",
        "reverse_questions": [3, 5],
        "max_option_value": 3,
        "thresholds": [
            {"max_score": 13, "interpretation": "سطح استرس پایین"},
            {"max_score": 26, "interpretation": "سطح استرس متوسط"},
            {"max_score": 40, "interpretation": "سطح استرس بالا"}
        ]
    })
    
    cursor.execute(
        """INSERT INTO anxiety_tests (test_code, test_name, description, question_count, max_score, interpretation_rules)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("PSS10", "مقیاس استرس ادراک شده (PSS-10)", 
         "این آزمون شامل 10 سوال است که سطح استرس شما را در ماه گذشته ارزیابی می‌کند.", 
         10, 40, pss10_interpretation)
    )
    pss10_id = cursor.lastrowid
    
    # PSS10 Questions
    pss10_options = json.dumps(["هرگز", "تقریباً هرگز", "گاهی اوقات", "تقریباً همیشه"])
    pss10_questions = [
        (pss10_id, 1, "در ماه گذشته چند بار احساس کرده‌اید نمی‌توانید کنترل کارهای مهم زندگی‌تان را در دست بگیرید؟", pss10_options),
        (pss10_id, 2, "در ماه گذشته چند بار احساس کرده‌اید عصبی و تحت فشار هستید؟", pss10_options),
        (pss10_id, 3, "در ماه گذشته چند بار احساس کرده‌اید همه چیز مطابق میل شما پیش می‌رود؟", pss10_options),
        (pss10_id, 4, "در ماه گذشته چند بار احساس کرده‌اید نمی‌توانید بر مشکلات انباشته شده غلبه کنید؟", pss10_options),
        (pss10_id, 5, "در ماه گذشته چند بار احساس کرده‌اید اوضاع تحت کنترل شماست؟", pss10_options),
        (pss10_id, 6, "در ماه گذشته چند بار احساس کرده‌اید از توانایی مقابله با مشکلات برخوردارید؟", pss10_options),
        (pss10_id, 7, "در ماه گذشته چند بار احساس کرده‌اید نمی‌توانید آرام شوید؟", pss10_options),
        (pss10_id, 8, "در ماه گذشته چند بار احساس کرده‌اید مواردی پیش می‌آید که شما را از کوره به در می‌برد؟", pss10_options),
        (pss10_id, 9, "در ماه گذشته چند بار احساس کرده‌اید قادر نیستید همه چیز را کنترل کنید؟", pss10_options),
        (pss10_id, 10, "در ماه گذشته چند بار احساس کرده‌اید مشکلات آنقدر زیاد هستند که قادر به انجام کارها نیستید؟", pss10_options),
    ]
    
    cursor.executemany(
        "INSERT INTO anxiety_test_questions (test_id, question_number, question_text, options) VALUES (?, ?, ?, ?)",
        pss10_questions
    )
    logger.info(f"Seeded PSS10 test with {len(pss10_questions)} questions")
    
    # PSS5 Test
    pss5_interpretation = json.dumps({
        "method": "reverse",
        "reverse_questions": [3, 4],
        "max_option_value": 3,
        "thresholds": [
            {"max_score": 7, "interpretation": "سطح استرس پایین"},
            {"max_score": 11, "interpretation": "سطح استرس متوسط"},
            {"max_score": 20, "interpretation": "سطح استرس بالا"}
        ]
    })
    
    cursor.execute(
        """INSERT INTO anxiety_tests (test_code, test_name, description, question_count, max_score, interpretation_rules)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("PSS5", "مقیاس استرس ادراک شده (PSS-5)", 
         "این آزمون شامل 5 سوال است که سطح استرس شما را در ماه گذشته ارزیابی می‌کند.", 
         5, 20, pss5_interpretation)
    )
    pss5_id = cursor.lastrowid
    
    # PSS5 Questions
    pss5_options = json.dumps(["هرگز", "تقریباً هرگز", "گاهی اوقات", "تقریباً همیشه"])
    pss5_questions = [
        (pss5_id, 1, "در ماه گذشته چند بار احساس کرده‌اید کارها از کنترل شما خارج شده‌اند؟", pss5_options),
        (pss5_id, 2, "در ماه گذشته چند بار احساس کرده‌اید نمی‌توانید با تمام کارهایی که باید انجام دهید کنار بیایید؟", pss5_options),
        (pss5_id, 3, "در ماه گذشته چند بار احساس کرده‌اید آرام و راحت بوده‌اید؟", pss5_options),
        (pss5_id, 4, "در ماه گذشته چند بار احساس کرده‌اید اوضاع را تحت کنترل دارید؟", pss5_options),
        (pss5_id, 5, "در ماه گذشته چند بار احساس کرده‌اید مشکلات شما بیش از حد توانتان بوده است؟", pss5_options),
    ]
    
    cursor.executemany(
        "INSERT INTO anxiety_test_questions (test_id, question_number, question_text, options) VALUES (?, ?, ?, ?)",
        pss5_questions
    )
    logger.info(f"Seeded PSS5 test with {len(pss5_questions)} questions")
    
    conn.commit()


def main() -> None:
    """Main seeder function."""
    setup_logging()
    logger.info("Starting database seeding...")
    
    db = get_database()
    
    try:
        seed_exercises(db)
        seed_anxiety_tests(db)
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
