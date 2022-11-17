import re
from bs4 import BeautifulSoup
import requests
from openpyxl import Workbook
from datetime import date
from dataclasses import dataclass
from get_urls import get_volleyball_urls


class VolleyBallPage:
    """Class to get data off a volleyball webpage

    Raises:
        TypeError: Couldn't find something
        ValueError: Couldn't find something
        ValueError: couldn't find something
        TypeError: couldn't find something
        TypeError: couldn't find something

    Returns:
        VolleyBallPage: VolleyBallPage Object
    """

    DEFAULT_DATA_SIZE = 4

    def __init__(self, url):
        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.result_data_re = re.compile(r"\((\w)\).*(\d).*(\d)")

    def _format_default(self, match_result, our_team, other_team, score1, score2):
        """
        Helper method to format a regular data row on the volleyball website
        """
        if match_result == "W":
            our_score = max(score1, score2)
            other_score = min(score1, score2)
            return (our_team, our_score, other_team, other_score)
        elif match_result == "L":
            our_score = min(score1, score2)
            other_score = max(score1, score2)
            return (other_team, other_score, our_team, our_score)
        else:
            raise TypeError("Game result is not a win or a loss")

    def _format_match_TBD(self, our_team, other_team):
        """Formats a match that is pending and has not currently happened

        Args:
            our_team (str): the name of the main team
            other_team (str): the name of the other team

        Returns:
            tuple: formatted in the format: winning team / score / other team / score; scores are placeholders
        """
        return (our_team, "Not yet determined", other_team, "Not yet determined")

    def _get_table_rows(self):
        """Gets the row elements from the volleyball web page

        Returns:
            Array[Tag]: list of all rows from a table, including incomplete entries.
        """
        table = self.soup.find("tbody")
        return table.find_all("tr", recursive=False)

    def get_main_team_name(self):
        """Gets the name of the main team for tbe website

        Raises:
            ValueError: Cannot find the name of the team on the website

        Returns:
            str: Name of the team
        """
        try:
            return re.match(
                "(.*) Volleyball", self.soup.find(id="Team_highlight_info1_Header").text
            ).group(1)
        except AttributeError as a_e:
            raise ValueError("Cannot find main team's name") from a_e

    def _get_other_team_name(self, trow):
        """Gets the name of the other team from a row

        Args:
            trow (Tag): A row tag from the volleyball website table

        Raises:
            ValueError: Cannot find other team's name

        Returns:
            str: Other team's name
        """
        try:
            return trow.select_one(".contest-type-indicator").find(text=True, recursive=False)
        except AttributeError as a_e:
            raise ValueError("Cannot find other team's name") from a_e

    def _get_score_data(self, trow):
        """Gets the score data from a table row from the volleyball website

        Args:
            trow (Tag): table row from volleyball website

        Raises:
            TypeError: If that data could not be found
            TypeError: If the data could not be extracted

        Returns:
            Returns None if a match is pending
            tuple(str, int, int): Tuple containing: result (Win, loss, tie) of a team, score of the first team, score of the second team
        """
        result = trow.select_one(".score")
        if result is None:
            if "In Progress" in trow.select_one(".last").text or "Preview Match" in trow.select_one(".last").text:
                return None
            else:
                raise TypeError("Data could not be found")

        data = self.result_data_re.match(result.text)
        if not data:
            raise TypeError("Data could not be extracted")

        match_result = data.group(1)
        score1 = int(data.group(2))
        score2 = int(data.group(3))
        return match_result, score1, score2

    def get_volleyball_data(self):
        """Returns a list of data from the volleyball website in the format: Winning team / score / Losing team / score

        Returns:
            Array[tuple()]: volleyball data in the format: Winning team / score / Losing team / score
        """
        our_team = self.get_main_team_name()
        return_data = []

        for trow in self._get_table_rows():
            other_team = self._get_other_team_name(trow)
            row_data = self._get_score_data(trow)
            if row_data is not None:
                match_result, score1, score2 = row_data
                return_data.append(
                    self._format_default(match_result, our_team, other_team, score1, score2)
                )
            else:
                return_data.append(self._format_match_TBD(our_team, other_team))
        return return_data
    

class DataWriter:
    """Represents an excel workbook and has specialized methods for writing volleyball data
    """
    def __init__(self) -> None:
        self.book = Workbook()
        self.book.remove(self.book.active)
    
    
    def add_volleyball_data(self, sheet_name, data):
        """Adds volleyball data to an excel sheet named sheet_name in the format: Winner / score / loser / score

        Args:
            sheet_name (str): Name of the main team
            data (Array(tuple(str, int, str, int))): Volleyball data formatted: Winner / score / loser / score
        """
        ws = self.book.create_sheet(sheet_name)
        for i, row in enumerate(ws.iter_rows(min_row=1,max_row=len(data),max_col=VolleyBallPage.DEFAULT_DATA_SIZE)):
            for j, cell in enumerate(row):
                cell.value = data[i][j]
    
    
    def save(self):
        """Saves the excel file to disk
        """
        book_file_name = f"VolleyballData{date.today().isoformat()}.xlsx"
        self.book.save(book_file_name)


def main():
    scores = set()
    writer = DataWriter()
    for url in get_volleyball_urls():
        page = VolleyBallPage(url)
        for element in page.get_volleyball_data():
            if isinstance(element, tuple):
                scores.add(element)
            else:
                print(f"invalid value added {element}")
    writer.add_volleyball_data("VolleyballData", scores)
    writer.save()


def test():
    URL = "https://www.maxpreps.com/print/schedule.aspx?schoolid=d2a54a52-b1ac-4588-98de-94edd98a7d85&ssid=3a7d2ebb-2ff5-4795-bdaa-58047958bbe9&print=1"
    URL2 = "https://www.maxpreps.com/print/schedule.aspx?schoolid=773627bf-68b2-4c1b-8e1f-d4a6d2513905&ssid=3a7d2ebb-2ff5-4795-bdaa-58047958bbe9&print=1"
    page = VolleyBallPage(URL)
    # print(get_volleyball_data(page))
    # for datapoint in page.get_volleyball_data():
    #     print(datapoint)
    writer = DataWriter()
    writer.add_volleyball_data(page.get_main_team_name(), page.get_volleyball_data())
    writer.save()

if __name__ == "__main__":
    test()
