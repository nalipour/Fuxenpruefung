import argparse
import requests

import tabulate

import version

URL_READ = 'https://fuxenserver.herokuapp.com/highscore'
URL_POST = 'https://fuxenserver.herokuapp.com/scores'
URL_NEWS = 'https://fuxenserver.herokuapp.com/daily'
URL_MESSAGES = 'https://fuxenserver.herokuapp.com/messages'

VERBOSE = False


def print_table(dictionary):
    if not VERBOSE:
        return
    try:
        keys = sorted(dictionary[0].keys())
    except IndexError:
        print('No entry present')
        return
    table = []
    for d in dictionary:
        table.append([d[key] for key in keys])
    print(tabulate.tabulate(table, headers=keys, tablefmt='grid'))


def get_response_json(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        print('Connection error. Return None.')
        return None

    if not response:
        print('Got no response from server. Return None.')
        return None
    print('Got response from server')
    resonseJson = response.json()
    return resonseJson


def read_highscore():
    print('Retrieving info from', URL_READ, '...')
    scores = get_response_json(URL_READ)
    if scores is None:
        return None
    print_table(scores)
    return scores


def post_score(username, score, message=''):
    print('Posting info to', URL_POST, '...')
    try:
        requests.post(URL_POST,
                      json={'username': username,
                            'score': score,
                            'message': message,
                            }
                      )
    except requests.exceptions.RequestException as e:
        print(e)
        print('Connection error. Return None.')
        return None


def read_news():
    print('Retrieving info from', URL_NEWS, '...')
    news = get_response_json(URL_NEWS)
    if news is None:
        return None
    print_table(news)
    return news[0]


def read_alerts():
    print('Retrieving info from', URL_MESSAGES, '...')
    messages = get_response_json(URL_MESSAGES)
    if messages is None:
        return None
    alerts = []
    for message in messages:
        messageFits = ((message['version'] == 'all') or (float(message['version']) >= version.version))
        messageHigher = ((message['version'] == 'all') or (float(message['version']) > version.version))
        categoryCheck = (message['category'] == 'alert') and messageFits
        versionCheck = (message['category'] == 'release') and messageHigher
        if not categoryCheck and not versionCheck:
            continue
        alerts.append(message)
    print_table(alerts)
    return alerts


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('task', choices=['read', 'post', 'news', 'alerts'], help='Type of server interaction')
    parser.add_argument('--name', default='', help='Name of user')
    parser.add_argument('--msg', default='', help='Optional message')
    parser.add_argument('--score', default=0, type=int, help='Achieved score')
    args = parser.parse_args()

    if args.task == 'post':
        post_score(username=args.name, score=args.score, message=args.msg)
    elif args.task == 'read':
        read_highscore()
    elif args.task == 'news':
        read_news()
    elif args.task == 'alerts':
        read_alerts()


if __name__ == '__main__':
    main()
