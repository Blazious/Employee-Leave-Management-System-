from django.test import TestCase
from datetime import date
from .utils import get_kenya_holidays, calculate_leave_days, calculate_easter

class HolidayTests(TestCase):
    def test_easter_calculation(self):
        """Test that Easter calculation works correctly"""
        # Known Easter dates for testing
        test_cases = [
            (2024, date(2024, 3, 31)), # Easter 2024 is March 31
            (2025, date(2025, 4, 20)), # Easter 2025 is April 20
            (2026, date(2026, 4, 5)),  # Easter 2026 is April 5
        ]

        for year, expected_date in test_cases:
            with self.subTest(year=year):
                calculated_date = calculate_easter(year)
                self.assertEqual(calculated_date, expected_date,
                               f"Easter calculation failed for {year}")

    def test_mashujaa_day(self):
        """Test that Mashujaa Day (October 20) is recognized as a holiday"""
        year = 2025
        holidays = get_kenya_holidays(year)
        mashujaa_day = date(year, 10, 20)
        
        holiday_dates = [h[0] for h in holidays]
        self.assertIn(mashujaa_day, holiday_dates, 
                     f"Mashujaa Day ({mashujaa_day}) should be in the holiday list")
        
        # Also verify the holiday name
        holiday_dict = dict(holidays)
        self.assertEqual(holiday_dict.get(mashujaa_day), "Mashujaa Day",
                        f"Holiday on {mashujaa_day} should be named 'Mashujaa Day'")
        
    def test_holiday_calculation(self):
        """Test period including Mashujaa Day"""
        # Test period from Oct 10 to Oct 23, 2025
        start = date(2025, 10, 10)
        end = date(2025, 10, 23)
        
        # Calculate days
        working_days = calculate_leave_days(start, end)
        
        # We expect Mashujaa Day (Oct 20) and two weekends to be excluded
        # Oct 11-12 (weekend)
        # Oct 18-19 (weekend)
        # Oct 20 (Mashujaa Day)
        # Total non-working days: 5
        # Total days in period: 14
        # Expected working days: 14 - 5 = 9
        self.assertEqual(working_days, 9, 
                        "Working days calculation should exclude Mashujaa Day and weekends")
