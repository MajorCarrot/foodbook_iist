"""Tool to automate booking on https://events.iist.ac.in/foodbook
"""

import argparse
import copy
import re
import sys
from datetime import date, datetime, timedelta
from pprint import pprint

import requests
import yaml

from meal import *


DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def fix_date_config(week_config):
    global DAYS_OF_WEEK

    all_days = week_config["all_days"]
    for day in DAYS_OF_WEEK:
        day_config = week_config[day] if day in week_config else {}
        week_config[day] = copy.deepcopy(all_days)
        for meal in day_config:
            for meal_item, status in day_config[meal].items():
                week_config[day][meal][meal_item] = status

    return week_config


def fixer(week_config, check_days, check_meal, check_item):
    for d in check_days:
        if check_item in week_config[d][check_meal]:
            del week_config[d][check_meal][check_item]
    return week_config


def verify_breakfast(week_config):
    check_days = [
        "Monday",
        "Wednesday",
        "Friday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Breakfast", "steamed_banana")
    return week_config


def verify_lunch(week_config):
    check_days = [
        "Monday",
        "Wednesday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Lunch", "chicken_dish")
    check_days = [
        "Tuesday",
        "Thursday",
        "Saturday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Lunch", "fish_dish")
    return week_config


def verify_dinner(week_config):
    check_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Saturday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Dinner", "fish_fry")
    check_days = [
        "Tuesday",
        "Wednesday",
        "Saturday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Dinner", "veg_special")
    check_days = [
        "Monday",
        "Tuesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    week_config = fixer(week_config, check_days, "Dinner", "paneer_dish")
    check_days = [
        "Tuesday",
        "Wednesday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Dinner", "non_veg_chicken")
    check_days = [
        "Monday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Sunday",
    ]
    week_config = fixer(week_config, check_days, "Dinner", "egg_dish")
    return week_config


def verify(week_config):
    week_config = verify_breakfast(week_config)
    week_config = verify_lunch(week_config)
    week_config = verify_dinner(week_config)
    return week_config


def login_get_cookie(instid, pin):
    login_credentials = {
        "instid": instid,
        "pin": pin,
    }
    # Get the session cookie
    k = requests.get("https://events.iist.ac.in/foodbook")
    cookies = k.cookies
    for cookie in cookies:
        print(f"Using cookie {cookie.name} - {cookie.value}")

    # Login
    k = requests.post(
        "https://events.iist.ac.in/foodbook/index.php?option=login&task=login",
        data=login_credentials,
        cookies=cookies,
    )

    if k.status_code != 200:
        print("Could not login! Exiting!")
        sys.exit(1)

    return cookies


def get_current_balance(cookies, print_name=False):
    # To get the current balance, fetch the main booking page
    k = requests.get(
        "https://events.iist.ac.in/foodbook/index.php?option=booking&task=book",
        cookies=cookies,
    )
    matches = re.findall(r"([a-zA-Z' ]*)\<br\>Available Balance:([0-9\.]*)", k.text)
    name = str(matches[0][0]).strip()
    current_balance = float(matches[0][1])
    if print_name:
        print(f"Logged in as {name}")
    print(f"Current balance is {current_balance}")

    return current_balance


def verify_get_config(config_file_obj):
    try:
        config = yaml.safe_load(config_file_obj)
        config_file_obj.close()
    except:
        print("Couldn't load the config")
        raise

    # Override the all_days config with user specified one and clean
    # it to match the original data
    week_1 = fix_date_config(config["Week1"])
    week_1 = verify(week_1)

    week_2 = fix_date_config(config["Week2"])
    week_2 = verify(week_2)

    return week_1, week_2


def daterange(start_date, end_date):
    for i in range(0, (end_date - start_date).days + 1):
        yield start_date + timedelta(days=i)


def get_bookdates(args, cur_time):
    book_dates = []

    min_start_date = datetime(cur_time.year, cur_time.month, cur_time.day)
    max_end_date = min_start_date + timedelta(days=14)  # Two weeks in advance

    if args.book_dates:
        print("book_dates being used")
        for book_date in args.book_dates:
            if book_date < min_start_date or book_date > max_end_date:
                print(
                    f"{book_date} is not within the range of {min_start_date} to {max_end_date}, so skipping"
                )
                continue
            book_dates.append(book_date)
        if not book_dates:
            print("No valid dates to book")
            sys.exit(1)

    elif args.skip_dates:
        print("skip_dates being used")
        for date in daterange(min_start_date, max_end_date):
            if date in args.skip_dates:
                continue
            book_dates.append(date)

    elif args.book_from:
        print("book_from and book_till being used")
        if args.book_from > max_end_date:
            print(
                f"book_from date {args.book_from} is not within the range of {min_start_date} to {max_end_date}, so can't book"
            )
            sys.exit(1)

        args.book_from = max(args.book_from, min_start_date)

        if args.book_till < args.book_from:
            print(
                f"book_till date {args.book_till} is below start_date of {args.book_from}, so can't book"
            )
            sys.exit(1)

        args.book_till = min(args.book_till, max_end_date)

        print("Booking from ", args.book_from.strftime("%Y-%m-%d"), " to ", args.book_till.strftime("%Y-%m-%d"))

        for date in daterange(args.book_from, args.book_till):
            book_dates.append(date)

    elif args.skip_from:
        print("skip_from and skip_till being used")
        if args.skip_till < min_start_date:
            print(
                f"skip_till date {args.skip_till} is below start_date of {min_start_date}, so not skipping anything"
            )

        args.skip_till = min(args.skip_till, max_end_date)

        if args.skip_from > args.skip_till:
            print(
                f"skip_from date {args.skip_from} is above skip_till date {args.skip_till}, which does not make sense, so can't book"
            )
            sys.exit(1)

        args.skip_from = max(args.skip_from, min_start_date)

        print("Skipping from " + args.skip_from.strftime("%Y-%m-%d") + " to " + args.skip_till.strftime("%Y-%m-%d"))

        if min_start_date < args.skip_from:
            for date in daterange(min_start_date, args.skip_from - timedelta(days=1)):
                book_dates.append(date)

        if max_end_date > args.skip_till:
            for date in daterange(args.skip_till + timedelta(days=1), max_end_date):
                book_dates.append(date)

    else:
        for date in daterange(min_start_date, max_end_date):
            book_dates.append(date)

    return book_dates


def get_booking_request(week_1, week_2, book_dates, cur_time):
    # Till 8 pm the previous day, breakfast and lunch for next day
    # can be booked
    if cur_time.hour < 20:
        offset_1 = 1
    else:
        offset_1 = 2

    # Till 10 am, tea/snacks and dinner for that day can be booked
    if cur_time.hour < 10:
        offset_2 = 0
    else:
        offset_2 = 1

    req_breakfast = {}
    req_lunch = {}
    req_dinner = {}
    req_tea = {}

    today = datetime(cur_time.year, cur_time.month, cur_time.day)

    # Breakfast and lunch
    for i in range(14):
        cur_day = today + timedelta(days=i + offset_1)
        if cur_day not in book_dates:
            req_breakfast[cur_day] = {}
            req_lunch[cur_day] = {}
            continue

        week = cur_day.isocalendar().week
        dayname = cur_day.strftime("%A")
        cur_week = week_1 if week % 2 == 1 else week_2

        req_breakfast[cur_day] = cur_week[dayname]["Breakfast"]
        req_lunch[cur_day] = cur_week[dayname]["Lunch"]

    # Tea/Snacks and Dinner
    for i in range(14):
        cur_day = today + timedelta(days=i + offset_2)
        if cur_day not in book_dates:
            req_dinner[cur_day] = {}
            req_tea[cur_day] = {}
            continue

        week = cur_day.isocalendar().week
        dayname = cur_day.strftime("%A")
        cur_week = week_1 if week % 2 == 1 else week_2

        req_dinner[cur_day] = cur_week[dayname]["Dinner"]
        req_tea[cur_day] = cur_week[dayname]["Tea_Snacks"]

    return req_breakfast, req_lunch, req_dinner, req_tea


def book_breakfast(req_breakfast, cookies, current_balance):
    print("Booking Breakfast")
    request = BreakFast(req_breakfast, current_balance=current_balance).get_request()

    k = requests.post(
        "https://events.iist.ac.in/foodbook/index.php?option=booking&task=saveBook",
        data=request,
        cookies=cookies,
    )

    if "Saved Successfully" in k.text:
        print("Breakfast booked succesfully")
    else:
        print("Booking error!!!! Please try later!")
        sys.exit(2)


def book_lunch(req_lunch, cookies, current_balance):
    print("Booking Lunch")
    request = Lunch(req_lunch, current_balance=current_balance).get_request()

    k = requests.post(
        "https://events.iist.ac.in/foodbook/index.php?option=booking&task=saveBook",
        data=request,
        cookies=cookies,
    )

    if "Saved Successfully" in k.text:
        print("Lunch booked succesfully")
    else:
        print("Booking error!!!! Please try later!")
        sys.exit(2)


def book_dinner(req_dinner, cookies, current_balance):
    print("Booking Dinner")
    request = Dinner(req_dinner, current_balance=current_balance).get_request()

    k = requests.post(
        "https://events.iist.ac.in/foodbook/index.php?option=booking&task=saveBook",
        data=request,
        cookies=cookies,
    )

    if "Saved Successfully" in k.text:
        print("Dinner booked succesfully")
    else:
        print("Booking error!!!! Please try later!")
        sys.exit(2)


def book_tea_snacks(req_tea, cookies, current_balance):
    print("Booking Tea/Snacks")
    request = Tea(req_tea, current_balance=current_balance).get_request()

    k = requests.post(
        "https://events.iist.ac.in/foodbook/index.php?option=booking&task=saveBook",
        data=request,
        cookies=cookies,
    )

    if "Saved Successfully" in k.text:
        print("Tea/Snacks booked succesfully")
    else:
        print("Booking error!!!! Please try later!")
        sys.exit(2)


def book_all_meals(
    req_breakfast, req_lunch, req_dinner, req_tea, cookies, current_balance
):
    book_breakfast(req_breakfast, cookies, current_balance)
    current_balance = get_current_balance(cookies, print_name=False)

    book_lunch(req_lunch, cookies, current_balance)
    current_balance = get_current_balance(cookies, print_name=False)

    book_dinner(req_dinner, cookies, current_balance)
    current_balance = get_current_balance(cookies, print_name=False)

    book_tea_snacks(req_tea, cookies, current_balance)
    current_balance = get_current_balance(cookies, print_name=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="foodbook", description="IIST food booking tool"
    )

    parser.add_argument(
        "-s",
        "--skip_dates",
        nargs="+",
        required=False,
        help="Dates to skip",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )

    parser.add_argument(
        "--skip_from",
        required="--skip_till" in sys.argv,
        help="Starting date for days to skip (--skip_till is required while using this)",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )
    parser.add_argument(
        "--skip_till",
        required="--skip_from" in sys.argv,
        help="Ending date for days to skip (--skip_from is required while using this)",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )

    parser.add_argument(
        "-b",
        "--book_dates",
        nargs="+",
        required=False,
        help="Dates to book",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )

    parser.add_argument(
        "--book_from",
        required="--book_till" in sys.argv,
        help="Starting date for days to book (--book_till is required while using this)",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )
    parser.add_argument(
        "--book_till",
        required="--book_from" in sys.argv,
        help="Ending date for days to book (--book_from is required while using this)",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )

    parser.add_argument(
        "-c", "--config", required=True, help="Config file", type=argparse.FileType("r")
    )

    parser.add_argument("-p", "--pin", required=True, help="PIN")
    parser.add_argument("-i", "--id", required=True, help="ID")

    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

    args = parser.parse_args()

    print("Got arguments:")
    pprint(vars(args))
    print()

    cur_time = datetime.now()

    week_1, week_2 = verify_get_config(args.config)
    cookies = login_get_cookie(args.id, args.pin)
    current_balance = get_current_balance(cookies, print_name=True)
    print()

    book_dates = get_bookdates(args, cur_time)

    print("Booking for dates:")
    for book_date in book_dates:
        print("\t" + book_date.strftime("%Y-%m-%d"))
    print()

    req = get_booking_request(week_1, week_2, book_dates, cur_time)
    book_all_meals(
        *req,
        cookies=cookies,
        current_balance=current_balance,
    )

