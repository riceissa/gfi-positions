#!/usr/bin/env python3

import sys
import glob
import re
from bs4 import BeautifulSoup

NAME = 0
TITLE = 1
START_DATE = 2

def main():

    # Keeps track of the current positions state. Each element of state is a
    # 3-tuple (name, title, start_date). The idea is to add tuples to state
    # when a new position appears, and to remove from state (and print the SQL
    # insert line) when a position disappears.
    state = []

    prev_listing = None
    for fp in sorted(glob.glob("data/*.html")):
        date_string = fp[len("data/"):-len(".html")]
        listing = get_listing(fp)
        if prev_listing is None:
            # This is the first snapshot, so add everyone
            for name, title in listing:
                state.append((name, title, date_string))
        else:
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

        prev_listing = listing

    # Now we print everyone still at the org
    for name, title, start_date in state:
        print_sql_line(name, title, start_date, "NULL")

def print_sql_line(name, title, start_date, end_date):
    print("(" + f"{name}, {title}, {start_date}--{end_date}" + ")")

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



if __name__ == "__main__":
    main()
