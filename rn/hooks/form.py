"""Checks 1 to 3 together: the record keeps its form. They run after a record file is written,
before the first user is called, and when the conductor ends its turn."""
from checks import open_names, steering_form, trace
from record import steering


def check(top, sdir):
    return steering_form.check(steering(sdir)) + open_names.check(sdir) + trace.check(top, sdir)
