#!/usr/bin/env python3

import sys
import glob
import re
from bs4 import BeautifulSoup

def main():
    fps = glob.glob("data/*.html")
    for fp in sorted(fps):
        date_string = fp[len("data/"):-len(".html")]
        listing = get_listing(date_string)
        print(listing)

def get_listing(date_string):
    team_members = []
    with open(f"data/{date_string}.html", "r") as f:
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
