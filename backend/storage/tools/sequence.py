import re

from django.db import IntegrityError, ProgrammingError, connection

RE_SEQUENCE = re.compile(r'^[a-z0-9_-]+$')


def get_next_value(sequence_name):
    if not RE_SEQUENCE.search(sequence_name):
        raise ValueError(f'Invalid sequence: {sequence_name!r}')

    def inner():
        cursor.execute(f"SELECT nextval('{sequence_name}')")

    with connection.cursor() as cursor:
        try:
            inner()
        except ProgrammingError:
            try:
                cursor.execute(f"CREATE SEQUENCE {sequence_name}")
            except IntegrityError:
                # Race condition -- another process already created the sequence
                pass
            inner()
        return cursor.fetchone()[0]
