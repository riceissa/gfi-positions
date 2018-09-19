#!/usr/bin/env python3

import sys
from bs4 import BeautifulSoup

def main():
    team_members = []
    with open("gfi.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for biorow in soup.find_all("div", {"class": "bioRow"}):
            if biorow.find("div", {"class": "staff"}):
                name = biorow.find("h1", {"class": "staffName"}).text
                title = biorow.find("h3", {"class": "staffTitle"}).text
                team_members.append((name, title))
            elif biorow.find("div", {"class": "board"}):
                for div in biorow.find_all("div", {"class": "board"}):
                    name = div.find("h3", {"class": "boardName"}).text
                    title = "Advisor"
                    team_members.append((name, title))
            else:
                print("Cannot find name in biorow", file=sys.stderr)

    print(team_members)


if __name__ == "__main__":
    main()
