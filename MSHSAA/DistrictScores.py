# ranks players on score to par from all 32 of the 2018 MSHSAA district tournaments

import requests
from bs4 import BeautifulSoup


class Player:
    def __init__(self, name, schl, class_, district, score):
        self.name = name
        self.school = schl
        self.class_ = class_
        self.district = district
        self.score = int(score)
        self.rank = None


leaderboard = []

for c in range(1,5):  # each class (1-4)
    for d in range(1,9):  # each district (1-8)
        page = requests.get('https://www.mshsaa.org/Activities/DistrictResult.aspx?alg=23&class=' + str(c) + '&district=' + str(d) + '&year=2017')
        html = BeautifulSoup(page.text, 'html.parser')
        table = html.find(id='ctl00_contentMain_dgIndividuals').find_all('tr')[1:]  # individual results (skip header)

        for row in table:
            try:
                _, name, school, _, score = [val.text.strip() for val in row.find_all('td')[1:]]  # unpack info (skip position)
                if int(score) < 999:  # ignore players who MSHSAA DQ'ed or WD'ed
                    leaderboard.append(Player(name, school, c, d, score))
            except ValueError:
                pass

leaderboard.sort(key = lambda p: p.score)

for index, player in enumerate(leaderboard):
    # rank golfers.  Those with same score have same rank
    if index > 0 and player.score == leaderboard[index - 1].score:
        player.rank = leaderboard[index - 1].rank
    else:
        player.rank = index + 1

    print("{}. {}: {}  ({} - Class {} - District {})".format(player.rank, player.name, player.score, player.school, player.class_, player.district))
