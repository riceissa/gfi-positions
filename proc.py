#!/usr/bin/env python3

import sys
import glob
import re
from bs4 import BeautifulSoup

NAME = 0
TITLE = 1
START_DATE = 2
FIRST_PRINT = True

def main():

    # Keeps track of the current positions state. Each element of state is a
    # 3-tuple (name, title, start_date). The idea is to add tuples to state
    # when a new position appears, and to remove from state (and print the SQL
    # insert line) when a position disappears.
    state = []

    for fp in sorted(glob.glob("data/*.html")):
        date_string = fp[len("data/"):-len(".html")]
        listing = get_listing(fp)

        new_state = []
        for name, title, start_date in state:
            if person_in_list(name, listing):
                if position_title_same(name, title, listing):
                    # This person is still at the org and their position
                    # title hasn't changed, so keep them
                    new_state.append((name, title, start_date))
                else:
                    # This person is still at the org, but their position
                    # title has changed, so print the old position
                    # information and add the new position to state.
                    print_sql_line(name, title, start_date, date_string)
                    new_state.append((name, position_title(name, listing), date_string))
            else:
                # The person left the org, so print the position
                # information.
                print_sql_line(name, title, start_date, date_string)
        state = new_state

        for name, title in listing:
            if not person_in_list(name, state):
                # This person is new to the organization, so record them in
                # state.
                state.append((name, title, date_string))

            # There is no else-case because the case of a position title
            # change is already handled in the loop over the state above.

    # Now we print everyone still at the org
    for name, title, start_date in state:
        print_sql_line(name, title, start_date, "")
    print(";")


def print_sql_line(name, title, start_date, end_date):
    global FIRST_PRINT
    if FIRST_PRINT:
        print("# SQL file generated using script at "
              "# https://github.com/riceissa/gfi-positions/")
        print()
        print("insert into positions(person, organization, title, start_date, "
              "start_date_precision, end_date, end_date_precision, urls, notes, "
              "employment_type, cause_area) values")
    if end_date:
        urls = f"https://github.com/riceissa/gfi-positions/blob/master/data/{start_date}.html https://github.com/riceissa/gfi-positions/blob/master/data/{end_date}.html"
    else:
        urls = f"https://github.com/riceissa/gfi-positions/blob/master/data/{start_date}.html"
    print(("    " if FIRST_PRINT else "    ,") + "(" + ",".join([
        mysql_quote(name),  # person
        mysql_quote("The Good Food Institute"),  # organization
        mysql_quote(title),  # title
        mysql_quote(start_date),  # start_date
        mysql_quote("month"),  # start_date_precision
        mysql_quote(end_date),  # end_date
        mysql_quote("month" if end_date else ""),  # end_date_precision
        mysql_quote(urls),  # urls
        mysql_quote(""),  # notes
        mysql_quote(""),  # employment_type
        mysql_quote("Animal welfare"),  # cause_area
    ]) + ")")
    FIRST_PRINT = False

def position_title(name, lst):
    for item in lst:
        if item[NAME] == name:
            return item[TITLE]

def person_in_list(name, lst):
    return any(t[NAME] == name for t in lst)

def position_title_same(name, title, lst):
    for item in lst:
        if item[NAME] == name:
            return item[TITLE] == title
    raise ValueError("Person not found in list")


def get_listing(filepath):
    """Get a single team member listing given the snapshot filepath."""
    team_members = []
    with open(filepath, "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for biorow in soup.find_all("div", {"class": "bioRow"}):
            if biorow.find("div", {"class": "staff"}):
                name = normalized_string(biorow.find("h1", {"class": "staffName"}).text)
                title = normalized_string(biorow.find("h3", {"class": "staffTitle"}).text)
                team_members.append((name, title))
            elif biorow.find("div", {"class": "board"}):
                for div in biorow.find_all("div", {"class": "board"}):
                    name = normalized_string(div.find("h3", {"class": "boardName"}).text)
                    title = "Advisor"
                    team_members.append((name, title))
            else:
                print("Cannot find name in biorow", file=sys.stderr)

    return team_members


def normalized_string(string):
    return re.sub(r"\s+", " ", string)


def mysql_quote(x):
    """Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    our input is fixed and from a basically trustable source."""
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)

if __name__ == "__main__":
    main()
