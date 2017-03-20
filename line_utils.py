import csv
import re
import numpy as np
from dateutil import parser
from collections import defaultdict
from itertools import groupby
import datetime
from operator import itemgetter
import scipy.sparse as sp
import matplotlib.pyplot as plt

def get_line_chat_dicts(file_name):
    """
    Given Line chat history, return chat dictionary which has following keys
    count, chats, total_chats
    """
    lines = csv.reader(open(file_name))
    chats = list(lines)
    chats = [c[0] for c in chats if len(c) > 0]
    chats_dict = defaultdict(list)
    chats_dict['count'] = 0
    for chat in chats:
        date = re.findall(r'\d+\.\d+\.\d+', chat)
        if len(date) >= 1:
            chats_dict['date'] = date
            d = date
        else:
            chats_dict['chats'].append([d[0], chat])
            chats_dict['count'] += 1
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

def plot_chat_per_day(chats_dict):
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

def plot_chat_users_per_day(chats_dict, users=['user_name_1', 'user_name_2']):
    """
    Plot number of chats per users
    """
    chat_users = []
    for date, chatlog in chats_dict['chats']:
        time, u, chat = split_chat(chatlog, users)
        if all((time, u, chat)):
            chat_users.append({'date': date,
                               'time': time,
                               'user': u,
                               'chat': chat})

    grouper = itemgetter("date", "user")
    chats_per_day = []
    for key, group in groupby(sorted(chat_users, key=grouper), grouper):
        temp_dict = dict(zip(["date", "user"], key))
        temp_dict["n_chat"] = len([item for item in group])
        chats_per_day.append(temp_dict)

    n_chats_all = []
    n_chats_user_all = []
    for user in users:
        n_chats = []
        for c in chats_per_day:
            if user in c['user']:
                n_chats.append([parser.parse(c['date']), c['n_chat'], user])
        n_chats_all.append(n_chats)
        n_chats_user_all.append([v[1] for v in n_chats])
    dates = [d[0] for d in n_chats_all[0]]

    # for two users
    ax = plt.subplot(111)
    ax.bar(dates, n_chats_user_all[0], width=0.5, color='#ffc0cb')
    ax.bar([d + datetime.timedelta(hours=12)  for d in dates], n_chats_user_all[1], width=0.5, color='#007e8c')
    ax.xaxis_date()
    plt.xlabel('date')
    plt.xticks(rotation=60)
    plt.ylabel('number of chats')
    plt.legend(users)
    plt.show(block=False)

def plot_punch_card_activities(chats_dict, users=['user_name_1', 'user_name_2']):
    """
    Punch card activities, plot in matrix format
    """
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
