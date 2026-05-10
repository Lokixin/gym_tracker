import logging
import random
import sys
import csv
import time
from typing import Generator

import requests
from bs4 import BeautifulSoup

from gym_tracker.config import settings

BASE_URL = "https://www.strengthlog.com/exercise-directory/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
COOKIE = settings.strengthlog_cookie
ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
SELECTOR = "wp-block-list"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_exercise_name_and_href(
    response_text: str,
) -> Generator[tuple[str, str], None, None]:
    soup = BeautifulSoup(response_text, "html.parser")
    ordered_lists = soup.find_all("ol", class_=SELECTOR)
    for _ol in ordered_lists:
        exercises_list = _ol.find_all("li")
        new_exercises = [
            (_exercise.find_next("a").get("href"), _exercise.text)
            for _exercise in exercises_list
        ]
        yield from new_exercises


def extract_muscle_groups_from_exercise(
    response_text: str,
) -> tuple[list[str], list[str]]:
    soup = BeautifulSoup(response_text, "html.parser")
    unordered_lists = soup.find_all("ul", class_=SELECTOR)
    primary_muscle_groups = (
        [_link.text for _link in unordered_lists[0].find_all("a")]
        if len(unordered_lists) > 0
        else []
    )
    secondary_muscle_groups = (
        [_link.text for _link in unordered_lists[1].find_all("a")]
        if len(unordered_lists) > 1
        else []
    )
    return primary_muscle_groups, secondary_muscle_groups


if __name__ == "__main__":
    with requests.Session() as client:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": ACCEPT,
        }
        if COOKIE:
            headers["Cookie"] = COOKIE
        res = client.get(BASE_URL, headers=headers)
        if res.status_code != 200:
            logger.error("Error scraping: ", res.status_code, res.content)
            sys.exit(1)
        exercise_iter = extract_exercise_name_and_href(res.text)
        with open("temp_db.csv", "a+", encoding="utf-8", newline="") as fp:
            writer = csv.writer(fp)
            writer.writerow(["name", "primary_groups", "secondary_groups"])
            must_scrape = False
            starting_point = (
                "https://www.strengthlog.com/band-external-shoulder-rotation/"
            )
            for exercise_href, exercise_name in exercise_iter:
                if exercise_href == starting_point:
                    must_scrape = True
                if must_scrape:
                    logger.info(
                        f"Extracting info for {exercise_name} from {exercise_href}"
                    )
                    res = client.get(exercise_href, headers=headers)
                    primary_groups, secondary_groups = (
                        extract_muscle_groups_from_exercise(res.text)
                    )
                    writer.writerow([exercise_name, primary_groups, secondary_groups])
                    time.sleep(random.randint(1, 6))
