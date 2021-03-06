# sorts players based on day 2 - day 1 position ratio on every state tournament for the past 8 years (32 tournaments)

import requests
from bs4 import BeautifulSoup


class Player:
    def __init__(self, current_pos, name, schl, class_, year, day_one, day_two):
        self.name = name
        self.school = schl
        self.class_ = class_
        self.year = year
        self.day_one = int(day_one)
        self.day_two = int(day_two)

        self.day_one_pos = None  # will get later
        self.day_two_pos = int(current_pos)

        # variables that will determine how to sort and display leaderboard
        self.ratio = None
        self.rank = None

# will contain list of player objects
leaderboard = []

for year in range(2010, 2018):

    for class_ in range(1,5):

        section = []  # list for each state tournament (so we can determine day one rank locally within the class tournament and not globally)

        # load html
        page = requests.get('https://www.mshsaa.org/Activities/DistrictWinnersResult.aspx?alg=23&class=' + str(class_) + '&year=' + str(year))
        html = BeautifulSoup(page.text, 'html.parser')  # make BS object
        table = html.find(id='ctl00_contentMain_dgIndResults').find_all('tr')[1:]  # individual results (skip header)

        for row in table:
            try:
                # make player object
                pos, name, school, day1, day2 = [val.text.strip() for val in row.find_all('td')][:5]
                section.append(Player(pos, name, school, class_, year + 1, day1, day2))
            except ValueError:  # if MSHSAA messed up inputting the scores/names somehow, just ignore player
                pass

        # find day one position (MSHSAA only gives day two rank), then the difference between day one and two
        section.sort(key= lambda p: p.day_one)
        for index, person in enumerate(section):
            # ties have same rank -- could be one liner, but it would be extremely unreadable
            if index > 0 and person.day_one == section[index - 1].day_one:
                person.day_one_pos = section[index - 1].day_one_pos
            else:
                person.day_one_pos = index + 1

            person.ratio = person.day_two_pos / person.day_one_pos

        leaderboard.append(section)


# convert 2D leaderboard to 1D list
# only worry about players who finished in top 15
leaderboard = [player for section in leaderboard for player in section]

# rank based on difference
leaderboard.sort(key= lambda p: p.ratio)
for index, person in enumerate(leaderboard):
    # give golfers a rank (for viewing purposes), those with same difference have same rank
    if index > 0 and person.ratio == leaderboard[index - 1].ratio:
        person.rank = leaderboard[index-1].rank
    else:
        person.rank = index + 1

    print("{}. {}: {} ({} to {}) ---- Score: {}-{} ---- Class {} in {}".format(person.rank, person.name, 
                                                                               round(person.ratio, 3), 
                                                                               person.day_one_pos, person.day_two_pos, 
                                                                               person.day_one, person.day_two, 
                                                                               person.class_, person.year))
    
