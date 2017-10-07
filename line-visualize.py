import argparse
import jinja2
import os
import base64
import shutil
import line_utils
import matplotlib.pyplot as plt


def generator(input, output):

    if os.path.exists(input) == False:
        print("File {} not exist".format(input))
        quit()

    directory = 'tmp'

    if not os.path.exists(directory):
        os.makedirs(directory)

    chats_dict = line_utils.read_line_chat(input)

    # Chat per day
    chat_per_day_path = directory + "/chat_per_day.png"
    plt.figure(figsize=(10, 5))
    line_utils.plot_chat_per_day(chats_dict, chat_per_day_path)

    # User chat per day
    user_chat_per_day_path = directory + "/user_chat_per_day.png"
    plt.figure(figsize=(10, 5))
    line_utils.plot_chat_users_per_day(chats_dict, user_chat_per_day_path)

    # Punch card activities
    punch_card_activities_path = directory + "/punch_card_activities.png"
    plt.figure(figsize=(15, 10))
    line_utils.plot_punch_card_activities(chats_dict, punch_card_activities_path)

    # Response rate
    response_rate_path = directory + "/response_rate.png"
    plt.figure(figsize=(15, 10))
    response_rate_users = line_utils.plot_response_rate(chats_dict, response_rate_path)

    data = {
        "chat_per_day": convert_img_to_base64(chat_per_day_path),
        "user_chat_per_day": convert_img_to_base64(user_chat_per_day_path),
        "punch_card_activities": convert_img_to_base64(punch_card_activities_path),
        "response_rate": convert_img_to_base64(response_rate_path),
        "response_rate_users": response_rate_users,
    }

    result = render('./template/visualize.html', data)

    with open(output, "w") as html_file:
        html_file.write(result)

    # Remove genrate image directory
    shutil.rmtree(directory)

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

def convert_img_to_base64(file):
    with open(file, "rb") as image_file:
        encoded = base64.b64encode(image_file.read())
        return encoded.decode("utf-8")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input',
        help='input chat file to visualize')

    parser.add_argument(
        '-o',
        '--output',
        help='HTML output file',
        default='output.html')

    args = parser.parse_args()
    arguments = args.__dict__
    generator(**arguments)
