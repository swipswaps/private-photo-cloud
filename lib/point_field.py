import functools
import re

from django.core.exceptions import FieldError
from django.db import models

_FLOAT_RE = r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'


def require_postgres(fn):
    """
    Decorator that checks if the target backend engine is a PostgreSQL instance
    :raises: FieldError
    """

    def wrapper(self, connection):
        engine = connection.settings_dict['ENGINE']

        if 'psycopg2' not in engine and 'postgis' not in engine:
            raise FieldError("Current database is not a PostgreSQL instance")

        return fn(self, connection)

    return wrapper


@functools.total_ordering
class Point(object):
    """
    Describe a point in the space.
    """

    POINT_RE = re.compile(r'\((?P<x>{0}),(?P<y>{0})\)'.format(_FLOAT_RE))

    @staticmethod
    def from_string(value):
        """
        Convert a string describing a point into a `Point` instance.
        The representation of a point as a string:
            (x, y)
        where `x` and `y` can be signed or unsigned integers or floats
        :param value: The string representation of the point
        :rtype: Point
        :raise: ValueError if the given string is not a valid point's
                representation
        """
        match = Point.POINT_RE.match(value)

        if not match:
            raise ValueError("Value {} is not a valid point".format(value))

        values = match.groupdict()

        return Point(float(values['x']), float(values['y']))

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return '<Point({0.x},{0.y})>'.format(self)

    def __str__(self):
        return '({0.x},{0.y})'.format(self)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.x == other.x
                and self.y == other.y)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return (isinstance(other, self.__class__)
                and self.x <= other.x
                and self.y <= other.y)


class PointField(models.Field):
    """
    Field to store a single point in space
    """

    @require_postgres
    def db_type(self, connection):
        return 'point'

    def to_python(self, value):
        if isinstance(value, Point) or value is None:
            return value

        return Point.from_string(value)

    def get_prep_value(self, value):
        return '({0.x},{0.y})'.format(value) if value else None

    def get_prep_lookup(self, lookup_type, value):
        return NotImplementedError(self)
