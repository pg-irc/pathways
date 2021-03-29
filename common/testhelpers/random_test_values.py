import string
import random
from datetime import datetime
from django.contrib.gis.geos import Point
from . import private

private.set_random_seed_at_load_time()


def a_string(length=20, from_character_string=string.ascii_lowercase):
    return ''.join(random.choice(from_character_string) for x in range(length))


def a_website_address():
    return 'http://www.{0}.com'.format(a_string())


def an_email_address():
    return '{0}@{1}.com'.format(a_string(), a_string())


def an_integer(**kwargs):
    min_inclusive = kwargs.get('min', 0)
    max_inclusive = kwargs.get('max', 1000)

    return random.randint(min_inclusive, max_inclusive)


def a_latitude():
    return -90 + 180*random.random()


def a_longitude():
    return -180 + 360*random.random()


def a_float():
    return float(an_integer())


def a_boolean():
    return random.random() < 0.5


def a_point():
    srid = 4326
    return Point(a_longitude(), a_latitude(), srid=srid)


def a_list_of_strings(length=3):
    return [a_string() for x in range(length)]


def a_list_of_integers(length=3):
    return [an_integer() for x in range(length)]


def a_phone_number(dummy_number='xxx-xxx-xxxx'):
    return ''.join([random.choice(string.digits) if char == 'x' else char for char in dummy_number])


def a_date():
    rand_delta = random.randint(0, 1e9)
    now = datetime.timestamp(datetime.now())
    return datetime.fromtimestamp(now - rand_delta)


def a_country_code():
    return a_string(2, string.ascii_uppercase)

def a_region_specific_id(region):
    return '{0}_{1}'.format(a_string(), region.lower())