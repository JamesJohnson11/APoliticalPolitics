from rcp import get_poll_data
from prettytable import PrettyTable

x = PrettyTable()

td = get_poll_data(
    "https://www.realclearpolitics.com/epolls/2020/president/us/general_election_trump_vs_biden-6247.html"
)

x.field_names = list(td[0]["data"][0].keys())
x.align = "l"

for row in td[0]["data"]:
    x.add_row(row.values())

print(x.field_names)