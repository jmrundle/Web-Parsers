from selenium import webdriver
from bs4 import BeautifulSoup


class Handicap:

    def __init__(self):
        self.base_url = "https://ncrdb.usga.org/NCRDB/"

        self.browser = None  # selenium webdriver object
        self.course_name = ""
        self.course_links = []
        self.link = ""
        self.tees = []
        self.tee = None  # Tee object
        self.score = 0
        self.handicap = 0.0

        self.get_browser()
        self.course_search()
        self.get_course_info()
        self.calculate_handicap()

    def get_browser(self):
        print("Loading Database...")
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.browser = webdriver.Chrome(
                        executable_path=r"INSERT PATH HERE",
                        chrome_options=options)
        self.browser.get(self.base_url)

    def get_course_name(self):
        self.course_name = input("\nCourse Name (part or whole):\n>>> ").strip()

    def print_course_table(self):
        html = BeautifulSoup(self.browser.page_source, 'lxml')

        # ignore table head, and only list first 10 courses
        courses = html.find_all('tr')[1:11]

        if not courses:
            print("No Courses found with name: {}.  Please try again with a different name.\n".format(self.course_name))
            self.course_search()
        else:
            print()
            for i, course_info in enumerate(courses):
                course, link, city, state = course_info.find_all('td')
                self.course_links.append(link.a['href'])
                print("{}. {} ({}, {})".format(i + 1, course.text.upper(), city.text.upper(), state.text.upper()))

    def course_search(self):
        self.get_course_name()
        course_search = self.browser.find_element_by_name("txtClubName")
        course_search.clear()
        course_search.send_keys(self.course_name)
        course_search.submit()
        self.print_course_table()

    def get_course_info(self):
        choice_index = int(input("\nSelect Course.  If not in menu, Enter 0.\n>>> "))
        if 1 <= choice_index <= len(self.course_links):
            self.link = self.base_url + self.course_links[choice_index - 1]
        else:
            self.course_search()
            self.get_course_info()
        print("\nLoading Course Info...\n")
        self.browser.get(self.link)
        self.print_course_info()

    def print_course_info(self):
        html = BeautifulSoup(self.browser.page_source, 'lxml')
        table = html.find("table", id="gvTee")

        # Gender print formatting
        men = True
        print("Men's:")

        self.tees = []
        for i, row in enumerate(table.find_all("tr")[1:]):
            tee, course_rating, slope_rating, tmp1, tmp2, tmp3, gender = map(lambda info: info.text, row.find_all("td"))
            self.tees.append(Tee(tee, course_rating, slope_rating))
            if men and gender == "F":
                men = False
                print("Women's:")
            print("{}. {}: {} {}".format(i + 1, tee, course_rating, slope_rating))

    def calculate_handicap(self):
        self.tee = self.tees[int(input('\n>>> ')) - 1]
        self.score = int(input("\n\nScore:\n>>> "))
        self.handicap = round((self.score - self.tee.cr) * (113.0 / self.tee.sr), 1)
        print("Handicap is:", self.handicap)


class Tee:
    def __init__(self, tee_col, cr, sr):
        self.tee_col = tee_col
        self.cr = float(cr)
        self.sr = float(sr)


if __name__ == '__main__':
    Handicap()
