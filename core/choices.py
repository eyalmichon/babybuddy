from django.db import models
from django.utils.translation import gettext_lazy as _


class DiaperColor(models.TextChoices):
    BLACK = "black", _("Black")
    BROWN = "brown", _("Brown")
    GREEN = "green", _("Green")
    YELLOW = "yellow", _("Yellow")


class FeedingType(models.TextChoices):
    BREAST_MILK = "breast milk", _("Breast milk")
    FORMULA = "formula", _("Formula")
    FORTIFIED_BREAST_MILK = "fortified breast milk", _("Fortified breast milk")
    SOLID_FOOD = "solid food", _("Solid food")


class FeedingMethod(models.TextChoices):
    BOTTLE = "bottle", _("Bottle")
    LEFT_BREAST = "left breast", _("Left breast")
    RIGHT_BREAST = "right breast", _("Right breast")
    BOTH_BREASTS = "both breasts", _("Both breasts")
    PARENT_FED = "parent fed", _("Parent fed")
    SELF_FED = "self fed", _("Self fed")


class Sex(models.TextChoices):
    GIRL = "girl", _("Girl")
    BOY = "boy", _("Boy")


class MedicationUnit(models.TextChoices):
    ML = "ml", _("ml")
    MG = "mg", _("mg")
    DROPS = "drops", _("drops")
    IU = "IU", _("IU")
    OZ = "oz", _("oz")
    TBSP = "tbsp", _("tbsp")
    TSP = "tsp", _("tsp")
    PUFFS = "puffs", _("puffs")


class MedicationFrequency(models.TextChoices):
    DAILY = "daily", _("Daily")
    INTERVAL = "interval", _("Every X hours")
    WEEKLY = "weekly", _("Specific days of week")


# ---------------------------------------------------------------------------
# Color metadata registry -- keyed by enum members.
# Since TextChoices members ARE strings (DiaperColor.BLACK == "black"),
# lookups by raw string value also work: _CHOICE_COLORS.get("black").
# ---------------------------------------------------------------------------
_CHOICE_COLORS = {
    DiaperColor.BLACK: "#1B1B1B",
    DiaperColor.BROWN: "#A0522D",
    DiaperColor.GREEN: "#228B22",
    DiaperColor.YELLOW: "#DAA520",
}


def get_color(value):
    """Return hex color for a choice value, or None."""
    return _CHOICE_COLORS.get(value)


def get_color_map(choices_cls):
    """Return {value: hex_color} for members of choices_cls that have colors."""
    return {m.value: _CHOICE_COLORS[m] for m in choices_cls if m in _CHOICE_COLORS}


def get_choice_detail(choices_cls):
    """Return list of {value, label, color?} dicts for API/HA consumption."""
    return [
        {
            "value": m.value,
            "label": str(m.label),
            **({"color": _CHOICE_COLORS[m]} if m in _CHOICE_COLORS else {}),
        }
        for m in choices_cls
    ]
