# -*- coding: utf-8 -*-
"""Central registry of activity-type visual metadata.

Every colour and HA icon string lives here -- the web dashboard reads
colours via a context-processor / CSS custom properties, and the HA
discovery endpoint reads colours, icons, and sensor groups via direct
import.  Changing a value here propagates everywhere automatically.
"""

from django.utils.translation import gettext_lazy as _

# ── Activity types ──────────────────────────────────────────────────
#
# Keys match the template `type` strings used by dashboard card tags
# (e.g. "diaperchange", "feeding") so that `icon-{{ type }}` still
# resolves the correct Fontello web icon without a Python lookup.
#
# `color`   – hex colour used for both the dashboard card chrome
#             and the HA entity colour.  None = no dashboard card.
# `mdi_icon` – Material Design Icons string for Home Assistant.

ACTIVITY_TYPES = {
    "diaperchange": {
        "label": _("Diaper Change"),
        "color": "#a72431",
        "mdi_icon": "mdi:paper-roll-outline",
    },
    "feeding": {
        "label": _("Feeding"),
        "color": "#37abe9",
        "mdi_icon": "mdi:baby-bottle-outline",
    },
    "pumping": {
        "label": _("Pumping"),
        "color": "#37abe9",
        "mdi_icon": "mdi:water-pump",
    },
    "sleep": {
        "label": _("Sleep"),
        "color": "#ff8f00",
        "mdi_icon": "mdi:sleep",
    },
    "medication": {
        "label": _("Medication"),
        "color": "#7c4dff",
        "mdi_icon": "mdi:pill",
    },
    "tummytime": {
        "label": _("Tummy Time"),
        "color": "#239556",
        "mdi_icon": "mdi:human-child",
    },
    "timer": {
        "label": _("Timer"),
        "color": None,
        "mdi_icon": "mdi:timer-outline",
    },
    "bmi": {
        "label": _("BMI"),
        "color": None,
        "mdi_icon": "mdi:human",
    },
    "head_circumference": {
        "label": _("Head Circumference"),
        "color": None,
        "mdi_icon": "mdi:tape-measure",
    },
    "height": {
        "label": _("Height"),
        "color": None,
        "mdi_icon": "mdi:human-male-height",
    },
    "temperature": {
        "label": _("Temperature"),
        "color": None,
        "mdi_icon": "mdi:thermometer",
    },
    "weight": {
        "label": _("Weight"),
        "color": None,
        "mdi_icon": "mdi:scale-bathroom",
    },
    "note": {
        "label": _("Note"),
        "color": None,
        "mdi_icon": "mdi:note-text",
    },
}


# ── Sensor-key → activity-type mapping ──────────────────────────────
#
# HA sensor keys (e.g. "changes") don't always match the activity-type
# key (e.g. "diaperchange").  This dict bridges the two.

SENSOR_KEY_TO_ACTIVITY = {
    "changes": "diaperchange",
    "feedings": "feeding",
    "pumping": "pumping",
    "sleep": "sleep",
    "medications": "medication",
    "tummy-times": "tummytime",
    "timers": "timer",
    "bmi": "bmi",
    "head-circumference": "head_circumference",
    "height": "height",
    "temperature": "temperature",
    "weight": "weight",
    "notes": "note",
}


# ── Sensor groups (issue #8) ───────────────────────────────────────
#
# Categorise sensors into collapsible UI groups for the HA integration.

SENSOR_GROUPS = [
    {
        "id": "activity",
        "title": "Recent Activity",
        "icon": "mdi:clock-outline",
        "order": 1,
        "default_collapsed": False,
        "color": "#1E88E5",
    },
    {
        "id": "today",
        "title": "Today's Summary",
        "icon": "mdi:calendar-today",
        "order": 2,
        "default_collapsed": False,
        "color": "#43A047",
    },
    {
        "id": "measurements",
        "title": "Body Measurements",
        "icon": "mdi:tape-measure",
        "order": 3,
        "default_collapsed": True,
        "color": "#8E24AA",
    },
    {
        "id": "since",
        "title": "Time Since",
        "icon": "mdi:timer-sand",
        "order": 4,
        "default_collapsed": True,
        "color": "#FB8C00",
    },
    {
        "id": "status",
        "title": "Status",
        "icon": "mdi:alert-circle-outline",
        "order": 5,
        "default_collapsed": False,
        "color": "#E53935",
    },
]


# ── Per-sensor group assignment ─────────────────────────────────────
#
# Maps every sensor key (across SENSORS, STATS_SENSORS, BINARY_SENSORS)
# to its group id above.

SENSOR_GROUP_MAP = {
    # activity
    "changes": "activity",
    "feedings": "activity",
    "medications": "activity",
    "notes": "activity",
    "pumping": "activity",
    "sleep": "activity",
    "tummy-times": "activity",
    "timers": "activity",
    # today
    "feedings_today": "today",
    "diaper_changes_today": "today",
    "sleep_total_today_minutes": "today",
    "medications_overdue_count": "today",
    # measurements
    "bmi": "measurements",
    "head-circumference": "measurements",
    "height": "measurements",
    "temperature": "measurements",
    "weight": "measurements",
    # since
    "last_feeding_minutes_ago": "since",
    "last_diaper_change_minutes_ago": "since",
    # status
    "medication_overdue": "status",
}
