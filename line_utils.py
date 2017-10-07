import csv
import re
import numpy as np
from dateutil import parser
from collections import defaultdict
from itertools import groupby
import datetime
from operator import itemgetter
from collections import Counter
import scipy.sparse as sp
import matplotlib.pyplot as plt
import random

def read_line_chat(file_name):
    """
    Given Line chat history, return chat dictionary which has following keys
    count, chats, total_chats
    """
    lines = csv.reader(open(file_name))
    chats = list(lines)
    chats = [c[0] for c in chats if len(c) > 0]
    chats_dict = defaultdict(list)
    is_found_first_date = False
    for chat in chats:
        date = re.findall(r'\d+\.\d+\.\d+', chat)

        #Android date format
        if len(date) == 0:
            date = re.findall('^\d+\/\d+\/\d+', chat)

        #Skip line until found date
        if is_found_first_date == False and len(date) == 0:
            continue

        #Empty line
        if len(chat.strip()) == 0:
            continue

        if len(date) >= 1:
            is_found_first_date = True
            d = date[0]
        else:
            chat = re.sub('^24:', '00:', chat)
            chats_dict['chats'].append([d, chat])
    chats_dict['total_chats'] = len(chats_dict['chats'])
    return chats_dict

def get_date_range(chats_dict):
    """
    Get date range out of all chat dictionary
    """
    dates = list(set([c[0] for c in chats_dict['chats']]))
    dates = [parser.parse(d) for d in dates]
    date_range = []
    for d in range((date_max - date_min).days + 1):
        date_range.append(date_min + datetime.timedelta(days=d))
    return date_range

def split_chat(chat, users):
    """Given list of users in conversation,
    split chat in to (time, user, chat text)
    """
    time = chat.split()[0]
    if len(re.findall(r'\d+:\d+',time)) >= 1:
        chat = (' '.join(chat.split()[1::])).strip()
        u = ''
        for user in users:
            if user in chat:
                u = user
                chat = re.sub(u, '', chat).strip()
            else:
                chat = chat
        return (time, u, chat)
    else:
        return (None, None, None)

def bin_time(t, n_bin=8):
    """bin time in the day to number of bins"""
    bin_size = int(24./n_bin)
    h = parser.parse(t).hour
    for i in range(n_bin + 1):
        r = range((i-1)*bin_size, i*bin_size)
        if h in r:
            return i - 1

def day_of_week(day, n_bin=8):
    """
    Turn date string into days of week index
    ['Sunday', 'Monday', ..., 'Saturday']
    """
    return parser.parse(day).weekday()

def gen_hex_colour_code():
    """
    Generate hex color
    """
    return '#' + ''.join([random.choice('0123456789ABCDEF') for x in range(6)])

def avg_response_rate(ls, wait_time=60):
    """
    Weighted response rate of reply in less than 30 mins
    """
    weight_n_chats = 0
    n_chats = 0
    for n_chat, r in Counter(ls).items():
        if r <= wait_time:
            weight_n_chats += n_chat * r
            n_chats += n_chat
    return weight_n_chats/n_chats

def get_users(chats_dict):
    """
    Get all users from chat dictionary
    """
    chats = [c[1] for c in chats_dict['chats']]
    chats = [re.sub('\d+:\d+', '', c).strip() for c in chats]
    count_user = Counter([c.split()[0] for c in chats])
    users = [k for k, v in count_user.items() if v > 10]

    all_profile_names = []
    for user in users:
        user_chats = [chat for chat in chats if chat.split()[0] == user]
        profile_name = [user]
        for i in range(1, 3):
            try:
                next_key = Counter([u.split()[i] for u in user_chats])
                u_next = [k for k, v in next_key.items() if v == len(user_chats)]
                profile_name.extend(u_next)
            except:
                pass
        all_profile_names.append(' '.join(profile_name))
    return all_profile_names

def plot_chat_per_day(chats_dict, save_file=None):
    """
    plot chat per day that from all chats
    """
    # group chat by date
    group_chats = []
    for key, group in groupby(chats_dict['chats'], lambda x: x[0]):
        group_chats.append({'date': key, 'chats': [g[1] for g in group]})

    chats_per_day = []
    for group_chat in group_chats:
        dt = parser.parse(group_chat['date'])
        chats_per_day.append([dt, len(group_chat['chats'])])

    ax = plt.subplot(111)
    ax.bar([c[0] for c in chats_per_day], [c[1] for c in chats_per_day], width=0.5)
    ax.xaxis_date()
    plt.xlabel('date')
    plt.xticks(rotation=60)
    plt.ylabel('number of chats')
    plt.show(block=False)

    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')

def plot_chat_users_per_day(chats_dict, save_file=None):
    """
    Plot number of chats per users over time
    """
    users = get_users(chats_dict)
    n_users = len(users)

    # split chat to time, user, chat string
    chat_users = []
    for date, chatlog in chats_dict['chats']:
        time, u, chat = split_chat(chatlog, users)
        if all((time, u, chat)):
            chat_users.append({'date': date,
                               'time': time,
                               'user': u,
                               'chat': chat})

    chats_per_day = []
    grouper = itemgetter("date", "user")
    for key, group in groupby(sorted(chat_users, key=grouper), grouper):
        temp_dict = dict(zip(["date", "user"], key))
        temp_dict["n_chat"] = len([item for item in group])
        chats_per_day.append(temp_dict)

    n_chats_all = []
    for user in users:
        n_chats = []
        for c in chats_per_day:
            if user in c['user']:
                n_chats.append([parser.parse(c['date']), c['n_chat'], user])
        n_chats_all.append(n_chats)

    colors = ['#007e8c', '#ffc0cb', '#488957'] # first set of colors
    colors.extend([gen_hex_colour_code() for i in range(n_users)]) # random

    ax = plt.subplot(111)
    for i, n_chat in enumerate(n_chats_all):
        date = [v[0] + datetime.timedelta(hours=(i * 24./n_users)) for v in n_chat]
        n_chat_user = [v[1] for v in n_chat]
        ax.bar(date, n_chat_user, width=(1.0/n_users), color=colors[i])
    ax.xaxis_date()
    plt.xlabel('date')
    plt.ylabel('number of chats')
    plt.xticks(rotation=60, ha='right')
    plt.legend(users)
    plt.show(block=False)

    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')

def plot_punch_card_activities(chats_dict, save_file=None):
    """
    Punch card activities, plot in matrix format
    """
    users = get_users(chats_dict)

    chat_users = []
    for date, chatlog in chats_dict['chats']:
        time, u, chat = split_chat(chatlog, users)
        if all((time, u, chat)):
            chat_users.append({'date': date,
                               'time': time,
                               'user': u,
                               'chat': chat}) # list of dict of chat

    for chat in chat_users:
        chat.update({'time_bin': bin_time(chat['time'])})
        chat.update({'day_of_week': day_of_week(chat['date'])})
        chat.update({'n_activity': 1})

    grouper = itemgetter("day_of_week", "time_bin")
    chats_per_day = []
    for key, group in groupby(sorted(chat_users, key=grouper), grouper):
        temp_dict = dict(zip(["day_of_week", "time_bin"], key))
        temp_dict["n_chat"] = len([item for item in group])
        chats_per_day.append(temp_dict)

    vals, rows, cols = [], [], []
    for c in chats_per_day:
        cols.append(c['time_bin'])
        rows.append(c['day_of_week'])
        vals.append(c['n_chat'])
    chat_time_bin = sp.csr_matrix((vals, (rows, cols))).toarray()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(chat_time_bin, interpolation='nearest', cmap=plt.get_cmap('bone'))
    ax.set_yticklabels(['', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    ax.set_xticklabels(['', '12 - 3 am', '3 - 6 am', '6 - 9 am', '9 am - 12 pm', '12 - 3 pm', '3 - 6 pm', '6 - 9 pm', '9 pm - 12 pm'],
                       rotation=60, ha='left')
    plt.show(block=False)

    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')

def plot_response_rate(chats_dict, save_file=None):
    """
    This only works for two users right now.
    Given chat dictionary, plot histogram of response rate
    and find weighted-average response rate of users
    """
    users = get_users(chats_dict)
    n_users = len(users)

    colors = ['#007e8c', '#ffc0cb', '#488957']
    colors.extend([gen_hex_colour_code() for i in range(n_users)])

    chat_users = []
    for date, chatlog in chats_dict['chats']:
        time, u, chat = split_chat(chatlog, users)
        if all((time, u, chat)):
            chat_users.append({'date': date,
                               'time': time,
                               'user': u,
                               'chat': chat})

    grouper = itemgetter("date")
    responses_all = []
    for key, group in groupby(sorted(chat_users, key=grouper), grouper):
        group_date = [[g['date'] + ' ' + g['time'], g['user'] ] for g in group]
        responses_all.append(group_date)

    users_response = []
    for responses in responses_all:
        time_previous, user_previous = responses[0]
        for i in range(1, len(responses)):
            if user_previous == responses[i][1]:
                time_previous, user_previous = responses[i]
            else:
                response_time = int((parser.parse(responses[i][0]) - parser.parse(time_previous)).seconds/60.)
                time_previous, user_previous = responses[i]
                users_response.append([user_previous, response_time])

    users_response_summary = defaultdict(list)
    for key, group in groupby(users_response, lambda x: x[0]):
        for g in group:
            users_response_summary[key].append(g[1])

    ret_data = []
    # plot and print response rate of users
    for i, user in enumerate(users):
        resp = users_response_summary[user]
        plt.hist(resp, bins=range(0, 30), alpha=0.5, color=colors[i])
        avg_rate = str(1./avg_response_rate(resp, wait_time=60))
        ret_data.append({"user": user, "avg_rate": avg_rate})
        print('response rate of %s = %s' % (user, avg_rate))
    plt.legend(users)
    plt.xlabel('response time (mins)')
    plt.ylabel('normalized number of chats ')
    plt.show(block=False)

    if save_file is not None:
        plt.savefig(save_file, bbox_inches='tight')

    return ret_data
