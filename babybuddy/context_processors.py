# -*- coding: utf-8 -*-
from core.metadata import ACTIVITY_TYPES


def activity_metadata(request):
    """Inject activity-type visual metadata into every template context.

    Templates use these values to render CSS custom properties in
    ``base.html`` so that compiled SCSS can reference them via
    ``var(--bb-<type>-color)`` instead of hard-coding hex values.
    """
    return {"activity_types": ACTIVITY_TYPES}
