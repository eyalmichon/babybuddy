# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from babybuddy.models import Settings
from core import models
from dashboard.templatetags import cards

from unittest import mock


class MockUserRequest:
    def __init__(self, user):
        self.user = user


class TemplateTagsTestCase(TestCase):
    fixtures = ["tests.json"]

    @classmethod
    def setUpClass(cls):
        super(TemplateTagsTestCase, cls).setUpClass()
        cls.child = models.Child.objects.first()
        cls.context = {"request": MockUserRequest(get_user_model().objects.first())}

        # Ensure timezone matches the one defined by fixtures.
        user_timezone = Settings.objects.first().timezone
        timezone.activate(user_timezone)

        # Test file data uses a basis date of 2017-11-18.
        date = timezone.localtime().strptime("2017-11-18", "%Y-%m-%d")
        cls.date = timezone.make_aware(date)

    def test_hide_empty(self):
        request = MockUserRequest(get_user_model().objects.first())
        request.user.settings.dashboard_hide_empty = True
        context = {"request": request}
        hide_empty = cards._hide_empty(context)
        self.assertTrue(hide_empty)

    def test_filter_data_age_none(self):
        request = MockUserRequest(get_user_model().objects.first())
        request.user.settings.dashboard_hide_age = None
        context = {"request": request}
        filter_data_age = cards._filter_data_age(context)
        self.assertFalse(len(filter_data_age))

    @mock.patch("dashboard.templatetags.cards.timezone")
    def test_filter_data_age_one_day(self, mocked_timezone):
        request = MockUserRequest(get_user_model().objects.first())
        request.user.settings.dashboard_hide_age = timezone.timedelta(days=1)
        context = {"request": request}
        mocked_timezone.localtime.return_value = timezone.localtime().strptime(
            "2017-11-18", "%Y-%m-%d"
        )

        filter_data_age = cards._filter_data_age(context, keyword="time")

        self.assertIn("time__range", filter_data_age)
        self.assertEqual(
            filter_data_age["time__range"][0],
            timezone.localtime().strptime("2017-11-17", "%Y-%m-%d"),
        )
        self.assertEqual(
            filter_data_age["time__range"][1],
            timezone.localtime().strptime("2017-11-18", "%Y-%m-%d"),
        )

    def test_card_diaperchange_last(self):
        data = cards.card_diaperchange_last(self.context, self.child)
        self.assertEqual(data["type"], "diaperchange")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["change"], models.DiaperChange)
        self.assertEqual(data["change"], models.DiaperChange.objects.first())

    @mock.patch("dashboard.templatetags.cards.timezone")
    def test_card_diaperchange_last_filter_age(self, mocked_timezone):
        request = MockUserRequest(get_user_model().objects.first())
        request.user.settings.dashboard_hide_age = timezone.timedelta(days=1)
        context = {"request": request}
        time = timezone.localtime().strptime("2017-11-10", "%Y-%m-%d")
        mocked_timezone.localtime.return_value = timezone.make_aware(time)

        data = cards.card_diaperchange_last(context, self.child)
        self.assertTrue(data["empty"])

    def test_card_diaperchange_types(self):
        data = cards.card_diaperchange_types(self.context, self.child, self.date)
        self.assertEqual(data["type"], "diaperchange")
        stats = {
            0: {
                "wet_pct": 50.0,
                "solid_pct": 50.0,
                "empty_pct": 0.0,
                "solid": 1,
                "wet": 1,
                "empty": 0.0,
                "changes": 2.0,
            },
            1: {
                "wet_pct": 0.0,
                "solid_pct": 100.0,
                "empty_pct": 0.0,
                "solid": 2,
                "wet": 0,
                "empty": 0.0,
                "changes": 2.0,
            },
            2: {
                "wet_pct": 100.0,
                "solid_pct": 0.0,
                "empty_pct": 0.0,
                "solid": 0,
                "wet": 2,
                "empty": 0.0,
                "changes": 2.0,
            },
            3: {
                "wet_pct": 75.0,
                "solid_pct": 25.0,
                "empty_pct": 0.0,
                "solid": 1,
                "wet": 3,
                "empty": 0.0,
                "changes": 4.0,
            },
            4: {
                "wet_pct": 100.0,
                "solid_pct": 0.0,
                "empty_pct": 0.0,
                "solid": 0,
                "wet": 1,
                "empty": 0.0,
                "changes": 1.0,
            },
            5: {
                "wet_pct": 100.0,
                "solid_pct": 0.0,
                "empty_pct": 0.0,
                "solid": 0,
                "wet": 2,
                "empty": 0.0,
                "changes": 2.0,
            },
            6: {
                "wet_pct": 100.0,
                "solid_pct": 0.0,
                "empty_pct": 0.0,
                "solid": 0,
                "wet": 1,
                "empty": 0.0,
                "changes": 1.0,
            },
        }
        self.assertEqual(data["stats"], stats)

    def test_card_feeding_recent(self):
        data = cards.card_feeding_recent(self.context, self.child, self.date)

        self.assertEqual(data["type"], "feeding")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])

        # most recent day
        self.assertEqual(data["feedings"][0]["total"], 2.5)
        self.assertEqual(data["feedings"][0]["count"], 3)

        # yesterday
        self.assertEqual(data["feedings"][1]["total"], 0.25)
        self.assertEqual(data["feedings"][1]["count"], 1)

        # last day
        self.assertEqual(data["feedings"][-1]["total"], 20.0)
        self.assertEqual(data["feedings"][-1]["count"], 2)

    def test_card_feeding_last(self):
        data = cards.card_feeding_last(self.context, self.child)
        self.assertEqual(data["type"], "feeding")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["feeding"], models.Feeding)
        self.assertEqual(data["feeding"], models.Feeding.objects.first())

    def test_card_feeding_last_method(self):
        data = cards.card_feeding_last_method(self.context, self.child)
        self.assertEqual(data["type"], "feeding")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertEqual(len(data["feedings"]), 3)
        for feeding in data["feedings"]:
            self.assertIsInstance(feeding, models.Feeding)
        self.assertEqual(
            data["feedings"][2].method, models.Feeding.objects.first().method
        )

    def test_card_pumping_last(self):
        data = cards.card_pumping_last(self.context, self.child)
        self.assertEqual(data["type"], "pumping")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["pumping"], models.Pumping)
        self.assertEqual(data["pumping"], models.Pumping.objects.first())

    def test_card_sleep_last(self):
        data = cards.card_sleep_last(self.context, self.child)
        self.assertEqual(data["type"], "sleep")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["sleep"], models.Sleep)
        self.assertEqual(data["sleep"], models.Sleep.objects.first())

    def test_card_sleep_last_empty(self):
        models.Sleep.objects.all().delete()
        data = cards.card_sleep_last(self.context, self.child)
        self.assertEqual(data["type"], "sleep")
        self.assertTrue(data["empty"])
        self.assertFalse(data["hide_empty"])

    def test_card_sleep_day(self):
        data = cards.card_sleep_recent(self.context, self.child, self.date)
        self.assertEqual(data["type"], "sleep")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertEqual(data["sleeps"][0]["total"], timezone.timedelta(seconds=43200))
        self.assertEqual(data["sleeps"][0]["count"], 3)

        self.assertEqual(data["sleeps"][1]["total"], timezone.timedelta(seconds=30600))
        self.assertEqual(data["sleeps"][1]["count"], 1)

    def test_card_sleep_naps_day(self):
        data = cards.card_sleep_naps_day(self.context, self.child, self.date)
        self.assertEqual(data["type"], "sleep")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertEqual(data["total"], timezone.timedelta(0, 7200))
        self.assertEqual(data["count"], 1)

    def test_card_statistics(self):
        data = cards.card_statistics(self.context, self.child)
        stats = [
            # Statistics date basis is not particularly strong to these diaper change
            # examples.
            # TODO: Improve testing of diaper change frequency statistics.
            {
                "type": "duration",
                "stat": 0.0,
                "title": "Diaper change frequency (past 3 days)",
            },
            {
                "type": "duration",
                "stat": 0.0,
                "title": "Diaper change frequency (past 2 weeks)",
            },
            {
                "title": "Diaper change frequency",
                "stat": timezone.timedelta(0, 44228, 571429),
                "type": "duration",
            },
            # Statistics date basis is not particularly strong to these feeding
            # examples.
            # TODO: Improve testing of feeding frequency statistics.
            {
                "type": "duration",
                "stat": 0.0,
                "title": "Feeding frequency (past 3 days)",
            },
            {
                "type": "duration",
                "stat": 0.0,
                "title": "Feeding frequency (past 2 weeks)",
            },
            {
                "type": "duration",
                "stat": timezone.timedelta(days=1, seconds=39780),
                "title": "Feeding frequency",
            },
            {
                "title": "Average nap duration",
                "stat": timezone.timedelta(0, 6300),
                "type": "duration",
            },
            {"title": "Average naps per day", "stat": 1.0, "type": "float"},
            {
                "title": "Average sleep duration",
                "stat": timezone.timedelta(0, 19800),
                "type": "duration",
            },
            {
                "title": "Average awake duration",
                "stat": timezone.timedelta(0, 18000),
                "type": "duration",
            },
            {"title": "Weight change per week", "stat": 1.0, "type": "float"},
            {"title": "Height change per week", "stat": 1.0, "type": "float"},
            {
                "title": "Head circumference change per week",
                "stat": 1.0,
                "type": "float",
            },
            {"title": "BMI change per week", "stat": 1.0, "type": "float"},
        ]

        self.assertEqual(data["stats"], stats)
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])

    def test_card_timer_list(self):
        user = get_user_model().objects.first()
        child = models.Child.objects.first()
        child_two = models.Child.objects.create(
            first_name="Child", last_name="Two", birth_date=timezone.localdate()
        )
        timers = {
            "no_child": models.Timer.objects.create(
                user=user, start=timezone.localtime() - timezone.timedelta(hours=3)
            ),
            "child": models.Timer.objects.create(
                user=user,
                child=child,
                start=timezone.localtime() - timezone.timedelta(hours=2),
            ),
            "child_two": models.Timer.objects.create(
                user=user,
                child=child_two,
                start=timezone.localtime() - timezone.timedelta(hours=1),
            ),
        }

        data = cards.card_timer_list(self.context)
        self.assertIsInstance(data["instances"][0], models.Timer)
        self.assertEqual(len(data["instances"]), 4)

        data = cards.card_timer_list(self.context, child)
        self.assertIsInstance(data["instances"][0], models.Timer)
        self.assertTrue(timers["no_child"] in data["instances"])
        self.assertTrue(timers["child"] in data["instances"])
        self.assertFalse(timers["child_two"] in data["instances"])

        data = cards.card_timer_list(self.context, child_two)
        self.assertIsInstance(data["instances"][0], models.Timer)
        self.assertTrue(timers["no_child"] in data["instances"])
        self.assertTrue(timers["child_two"] in data["instances"])
        self.assertFalse(timers["child"] in data["instances"])

    def test_card_tummytime_last(self):
        data = cards.card_tummytime_last(self.context, self.child)
        self.assertEqual(data["type"], "tummytime")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["tummytime"], models.TummyTime)
        self.assertEqual(data["tummytime"], models.TummyTime.objects.first())

    def test_card_tummytime_day(self):
        data = cards.card_tummytime_day(self.context, self.child, self.date)
        self.assertEqual(data["type"], "tummytime")
        self.assertFalse(data["empty"])
        self.assertFalse(data["hide_empty"])
        self.assertIsInstance(data["instances"].first(), models.TummyTime)
        self.assertIsInstance(data["last"], models.TummyTime)
        stats = {"count": 3, "total": timezone.timedelta(0, 300)}
        self.assertEqual(data["stats"], stats)

    def test_card_medication_last_empty(self):
        data = cards.card_medication_last(self.context, self.child)
        self.assertEqual(data["type"], "medication")
        self.assertTrue(data["empty"])
        self.assertIsNone(data["medication"])
        self.assertEqual(len(data["pending"]), 0)

    def test_card_medication_last_with_entry(self):
        models.Medication.objects.create(
            child=self.child,
            name="Vitamin D",
            amount=400,
            amount_unit="IU",
            time=timezone.localtime(),
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertEqual(data["type"], "medication")
        self.assertFalse(data["empty"])
        self.assertIsInstance(data["medication"], models.Medication)
        self.assertEqual(data["medication"].name, "Vitamin D")

    def test_card_medication_last_with_pending(self):
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Vitamin D",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            active=True,
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertFalse(data["empty"])
        self.assertEqual(len(data["pending"]), 1)
        self.assertEqual(data["pending"][0]["schedule"], schedule)

    def test_card_medication_last_multiple_pending(self):
        models.MedicationSchedule.objects.create(
            child=self.child,
            name="Vitamin D",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            active=True,
        )
        models.MedicationSchedule.objects.create(
            child=self.child,
            name="Ibuprofen",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=timezone.datetime.strptime("08:00", "%H:%M").time(),
            active=True,
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertEqual(len(data["pending"]), 2)

    def test_card_medication_last_given_clears_pending(self):
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Vitamin D",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            active=True,
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Vitamin D",
            time=timezone.localtime(),
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertFalse(data["empty"])
        self.assertIsInstance(data["medication"], models.Medication)
        self.assertEqual(len(data["pending"]), 0)

    def test_card_medication_last_interval_stays_after_given(self):
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Ibuprofen",
            frequency=models.MedicationSchedule.FREQUENCY_INTERVAL,
            interval_hours=6,
            active=True,
        )
        # Give the medication now.
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Ibuprofen",
            time=timezone.localtime(),
        )
        data = cards.card_medication_last(self.context, self.child)
        # Interval schedule should still appear in pending with next due time.
        self.assertEqual(len(data["pending"]), 1)
        self.assertEqual(data["pending"][0]["schedule"], schedule)
        self.assertFalse(data["pending"][0]["overdue"])

    def test_card_medication_last_inactive_excluded(self):
        models.MedicationSchedule.objects.create(
            child=self.child,
            name="Inactive Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            active=False,
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertTrue(data["empty"])
        self.assertEqual(len(data["pending"]), 0)

    def test_medication_midnight_boundary_daily(self):
        """A daily 23:59 dose given at 00:01 the next day should still
        show as pending for that day's 23:59 occurrence."""
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Late Night Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=datetime.time(23, 59),
            active=True,
        )
        tz = timezone.get_current_timezone()
        # Simulate: dose given at 00:01 today (meant for yesterday's 23:59).
        today = timezone.localdate()
        dose_time = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(0, 1)), tz
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Late Night Med",
            time=dose_time,
        )
        # At 10:00 the same day, the 23:59 dose should still be pending.
        fake_now = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(10, 0)), tz
        )
        with mock.patch("dashboard.templatetags.cards.timezone") as m_tz:
            m_tz.localtime.return_value = fake_now
            pending = cards._medication_pending(self.child)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["schedule"], schedule)
        self.assertFalse(pending[0]["overdue"])

    def test_medication_normal_daily_dose_clears(self):
        """A daily 08:00 dose given at 08:05 should NOT show as pending
        for the rest of the day."""
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Morning Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=datetime.time(8, 0),
            active=True,
        )
        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        dose_time = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(8, 5)), tz
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Morning Med",
            time=dose_time,
        )
        # At 09:00 the same day, it should not be pending.
        fake_now = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(9, 0)), tz
        )
        with mock.patch("dashboard.templatetags.cards.timezone") as m_tz:
            m_tz.localtime.return_value = fake_now
            pending = cards._medication_pending(self.child)
        self.assertEqual(len(pending), 0)

    def test_medication_weekly_late_dose(self):
        """A Friday 23:00 weekly dose given at Saturday 00:01 should not
        suppress the next scheduled weekday occurrence."""
        # Schedule: every Friday at 23:00.
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Weekly Med",
            frequency=models.MedicationSchedule.FREQUENCY_WEEKLY,
            schedule_time=datetime.time(23, 0),
            friday=True,
            active=True,
        )
        tz = timezone.get_current_timezone()
        # Find the next Friday from today and set the dose on the following Saturday 00:01.
        today = timezone.localdate()
        days_until_friday = (4 - today.weekday()) % 7
        friday = today + datetime.timedelta(days=days_until_friday)
        saturday = friday + datetime.timedelta(days=1)
        dose_time = timezone.make_aware(
            datetime.datetime.combine(saturday, datetime.time(0, 1)), tz
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Weekly Med",
            time=dose_time,
        )
        # On the following Friday, the dose should show as pending again.
        next_friday = friday + datetime.timedelta(weeks=1)
        fake_now = timezone.make_aware(
            datetime.datetime.combine(next_friday, datetime.time(10, 0)), tz
        )
        with mock.patch("dashboard.templatetags.cards.timezone") as m_tz:
            m_tz.localtime.return_value = fake_now
            pending = cards._medication_pending(self.child)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["schedule"], schedule)

    def test_medication_first_dose_shows_pending(self):
        """A schedule with no previous doses should show as pending."""
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="New Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=datetime.time(9, 0),
            active=True,
        )
        data = cards.card_medication_last(self.context, self.child)
        self.assertEqual(len(data["pending"]), 1)
        self.assertEqual(data["pending"][0]["schedule"], schedule)

    def test_medication_no_schedule_time_daily(self):
        """A daily schedule without a specific time: given today, it should
        not show as pending until tomorrow."""
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Anytime Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=None,
            active=True,
        )
        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        dose_time = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(14, 0)), tz
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Anytime Med",
            time=dose_time,
        )
        # Later the same day it should not be pending.
        fake_now = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(18, 0)), tz
        )
        with mock.patch("dashboard.templatetags.cards.timezone") as m_tz:
            m_tz.localtime.return_value = fake_now
            pending = cards._medication_pending(self.child)
        self.assertEqual(len(pending), 0)

    def test_medication_no_schedule_time_next_day(self):
        """A daily schedule without a specific time: given yesterday, it should
        show as pending today."""
        schedule = models.MedicationSchedule.objects.create(
            child=self.child,
            name="Anytime Med",
            frequency=models.MedicationSchedule.FREQUENCY_DAILY,
            schedule_time=None,
            active=True,
        )
        tz = timezone.get_current_timezone()
        today = timezone.localdate()
        yesterday = today - datetime.timedelta(days=1)
        dose_time = timezone.make_aware(
            datetime.datetime.combine(yesterday, datetime.time(15, 0)), tz
        )
        models.Medication.objects.create(
            child=self.child,
            medication_schedule=schedule,
            name="Anytime Med",
            time=dose_time,
        )
        fake_now = timezone.make_aware(
            datetime.datetime.combine(today, datetime.time(8, 0)), tz
        )
        with mock.patch("dashboard.templatetags.cards.timezone") as m_tz:
            m_tz.localtime.return_value = fake_now
            pending = cards._medication_pending(self.child)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["schedule"], schedule)
