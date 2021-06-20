import requests
from bs4 import BeautifulSoup  # type: ignore


def extract_news(parser):
    """ Extract news from a given web page """

    def extract_first_integer_from_tag(tag, separator):
        try:
            return 0 if tag is None else int(tag.text.split(separator)[0])
        except ValueError:
            return 0

    news = []

    links = parser.findAll("a", {"class": "storylink"})
    subtexts = parser.findAll("td", {"class": "subtext"})

    for yi in range(len(links)):
        author = subtexts[yi].find("a", {"class": "hnuser"})
        comments = extract_first_integer_from_tag(subtexts[yi].find_all("a")[-1], "\xa0")
        points = extract_first_integer_from_tag(
            subtexts[yi].find("span", {"class": "score"}), " "
        )

        news.append(
            {
                "author": None if author is None else author.text,
                "comments": comments,
                "points": points,
                "title": links[yi].text,
                "url": links[yi]["href"],
            }
        )
    return news


def extract_next_page(parser):
    """ Extract next page URL """
    return parser.find("a", {"class": "morelink"})["href"]


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        current_news = extract_news(soup)
        next_url = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_url
        news.extend(current_news)
        n_pages -= 1
    return news