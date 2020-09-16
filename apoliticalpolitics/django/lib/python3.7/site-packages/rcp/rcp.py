# -*- coding: utf-8 -*-

import csv

import urllib3
from bs4 import BeautifulSoup

base = "https://www.realclearpolitics.com"


def _html(url):
    with urllib3.PoolManager() as manager:
        res = manager.request("GET", url)
        if res.status is not 200:
            raise Exception(res.status)
        soup = BeautifulSoup(res.data, "html.parser")
        return soup


def get_polls(url="%s/epolls/latest_polls/" % base, candidate=None, pollster=None, state=None):
    """
    :param state: The state to get polling data for.
    :param url: The URL of the polls. By default this function will search the latest polls on RCP.
    :param candidate: The election candidate.
    :param pollster: The pollster, i.e. Fox, CNN, Politico, etc.
    :return: arr
    """
    soup = _html(url)

    fp = soup.find_all("div", {"class": "table-races"})

    polling_data = []

    for l in fp:
        cols = l.find_all("tr")
        for col in cols:
            race = col.find("td", {"class": "lp-race"})
            result = col.find("td", {"class": "lp-results"})

            if not race:
                continue

            t = race.find("a").text
            n = col.find("td", {"class": "lp-poll"}).find("a").text

            if (
                    (candidate and candidate.lower() not in t.lower())
                    or (pollster and pollster.lower() not in n.lower())
                    or (state and state.lower() not in t.lower())
            ):
                continue

            v = {
                "url": base + race.find("a")["href"],
                "title": t,
                "poll": n,
                "result": result.text
            }
            polling_data.append(v)

    return polling_data


def get_poll_data(poll, csv_output=False):
    """
    :param poll: The URL of the poll.
    :param csv_output: Set to True to return a table like data structure if writing to CSV.
    :return: arr
    """
    if base not in poll:
        return

    soup = _html(poll)
    fp = soup.find("div", {"id": "polling-data-full"})

    if not fp:
        return

    rows = fp.find("table", {"class": "data"})

    p = []

    for row in rows:
        cols = row.find_all(["th", "td"])
        p.append([ele.text.strip() for ele in cols])

    if csv_output:
        return p

    arr = [{"poll": poll, "data": []}]

    keys = p[0]

    for k in p[1:]:
        b = {}
        for i, n in enumerate(keys):
            b[n] = k[i]
        arr[0]["data"].append(b)

    return arr


def to_csv(filename, poll_data):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(poll_data)
    print("CSV created.")
