import math
import re
import logging
from django.core.management.base import BaseCommand, CommandError
from exponent_server_sdk import (DeviceNotRegisteredError, PushClient, PushMessage,
                                 PushTicketError, PushServerError)
from search.read_csv_data_from_file import read_csv_data_from_file
from urllib.error import HTTPError

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Send push notifications to a set of users identified by their expo push notification tokens')

    def add_arguments(self, parser):
        parser.add_argument('title',
                    metavar='title',
                    help=('path to file containing title text for notification, '
                            'comma separated, locale in first column, title in second column'))
        parser.add_argument('message',
                            metavar='message',
                            help=('path to file containing message text for notification, '
                                  'comma separated, locale in first column, message in second column'))
        parser.add_argument('users',
                            metavar='users',
                            help=('path to file containing users, comma separated, expo push notification '
                                  'token in first column, locale in second column'))
        parser.add_argument('url',
                            metavar='url',
                            nargs='?',
                            help=('optional url to route to in the app, can be "store", "welcome" or '
                                  '"/task/<task id>". "store" is disabled and doesn\'t do anything until '
                                  'we decide what the UX should be around that.'),
                            default=None)

    def handle(self, *args, **options):
        users = options['users']
        users_csv = read_csv_data_from_file(users)
        valid_users = validate_users(users_csv)

        title = options['title']
        notification_titles = read_csv_data_from_file(title)
        valid_notification_titles = validate_localized_notifications(notification_titles)

        message = options['message']
        notifications = read_csv_data_from_file(message)
        valid_notifications = validate_localized_notifications(notifications)

        url = options['url']

        send_push_notifications(valid_users, valid_notification_titles, valid_notifications, url)


def validate_users(users):
    result = []
    for line in users:
        result.append(validate_user(line))
    return result


def validate_user(user):
    locale = validate_locale(user[1])
    token = validate_token(user[0])
    return {'token': token, 'locale': locale}


def validate_locale(locale):
    if not locale in ['ar', 'en', 'fr', 'ko', 'pa', 'tl', 'zh_CN', 'zh_TW']:
        raise CommandError('{}: Invalid locale'.format(locale))
    return locale


def validate_token(token):
    match = re.search(r'^ExponentPushToken\[.*\]$', token)
    if not match:
        raise CommandError('{}: Invalid token'.format(token))
    return token


def validate_localized_notifications(notifications):
    result = {}
    for line in notifications:
        locale = validate_locale(line[0])
        result[locale] = line[1]
    return result


def send_push_notifications(users, localized_notification_titles, localized_notification_messages, url):
    for i in range(0, len(users)):
        user = users[i]
        token = user['token']
        locale = user['locale']
        title = localized_notification_titles[locale]
        message = localized_notification_messages[locale]
        extra = build_extra_data(url)
        send_push_message(token, title, message, extra)
        print_progress(i, len(users))


def print_progress(index, max_index):
    if max_index < 1:
        return
    last_fraction = math.floor(20 * (index - 1)/max_index)
    current_fraction = math.floor(20 * index/max_index)
    if (last_fraction < current_fraction):
        print(f'{5*current_fraction}% done')


def build_extra_data(url):
    if url:
        return {'navigateToRoute': url}
    return None


def send_push_message(token, title, message, extra):
    try:
        response = PushClient().publish(PushMessage(to=token, title=title, body=message, data=extra))

    except PushServerError:
        LOGGER.error('Error pushing notification: PushServerError for %s', token)

    except (ConnectionError, HTTPError):
        LOGGER.error('Error pushing notification: ConnectionError for %s', token)

    try:
        response.validate_response()

    except DeviceNotRegisteredError:
        # According to https://github.com/expo/expo-server-sdk-python this error is
        # thrown when users no longer want to receive push notifications.
        LOGGER.warning('DeviceNotRegisteredError, remove this token from our database: %s', token)

    except PushTicketError:
        LOGGER.error('Error pushing notification: PushResponseError for %s', token)
