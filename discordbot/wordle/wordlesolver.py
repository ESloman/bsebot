"""File for WordleSolver class."""

import asyncio
import copy
import csv
import datetime
import os
import random
import re
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from slomanlogger import SlomanLogger

from discordbot.wordle.constants import (
    WORDLE_BOARD_CLASS_NAME,
    WORDLE_EXCELLENT_GUESS_NUM,
    WORDLE_FOOTNOTE,
    WORDLE_GDPR_ACCEPT_ID,
    WORDLE_PLAY_CLASS_NAME,
    WORDLE_ROWS_CLASS_NAME,
    WORDLE_SETTINGS_BUTTON,
    WORDLE_TUTORIAL_CLOSE_CLASS_NAME,
    WORDLE_URL,
    WORDLE_WORD_LENGTH,
)
from discordbot.wordle.data_type import WordleSolve
from mongo.bsedataclasses import WordleAttempts
from mongo.bsepoints.generic import DataStore

if TYPE_CHECKING:
    from mongo.datatypes.wordle import WordleAttemptDB


class WordleSolver:
    """Wordle solver class."""

    def __init__(self, headless: bool = True) -> None:
        """Initialisation method.

        Args:
            headless (bool, optional): _description_. Defaults to True.
        """
        self.firefox_opts = Options()
        if headless:
            self.firefox_opts.add_argument("--headless")
        self.firefox_opts.add_argument("--no-sandbox")
        self.words = self._get_words()
        self.words_freq = self._get_word_frequency()
        self.driver = None
        self.action_chain = None
        self.possible_words = copy.deepcopy(self.words)
        self.logger = SlomanLogger("bsebot")
        self.wordles = WordleAttempts()
        self.data_store = DataStore()

        words_result = self.data_store.get_starting_words()
        if not words_result:
            self.logger.debug("No words found in database - setting to defaults")
            self._starting_words = ["adieu", "soare"]
        else:
            self._starting_words = words_result["words"]

    async def setup(self) -> None:
        """Setup method.

        Gets the necessary driver using the driver manager. (downloads and installs if necessary)
        Creates a WebDriver object
        Navigates to wordle web page
        Clears GDPR, play screen and tutorial.
        """
        driver = webdriver.Chrome(
            service=FirefoxService("/opt/chromedriver/chromedriver-linux64/chromedriver"),
            options=self.firefox_opts,
        )
        driver.get(WORDLE_URL)
        await asyncio.sleep(2)

        try:
            # updated terms button
            continue_button = driver.find_element(By.CLASS_NAME, "purr-blocker-card__button")
            continue_button.click()
        except (ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException):
            pass

        try:
            accept_button = driver.find_element(By.ID, WORDLE_GDPR_ACCEPT_ID)
            accept_button.click()
        except (ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException):
            pass

        try:
            # sometimes there's a play button now
            play_button = driver.find_element(By.CSS_SELECTOR, f"button[class*='{WORDLE_PLAY_CLASS_NAME}']")
            play_button.click()
            await asyncio.sleep(1)
        except (ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException):
            pass

        try:
            close_button = driver.find_element(By.CSS_SELECTOR, f"button[class*='{WORDLE_TUTORIAL_CLOSE_CLASS_NAME}']")
            close_button.click()
        except (ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException):
            pass

        self.driver = driver
        self.action_chain = ActionChains(self.driver)

    @staticmethod
    def _get_words() -> list[str]:
        """Returns a list of possible words.

        Returns:
            _type_: Returns the list of possible words we can guess
        """
        fp = os.path.abspath(__file__)
        path = os.path.join(os.path.dirname(fp), "wordle_guesses")
        with open(path, encoding="utf-8") as f:
            words = [line.rstrip() for line in f]
        return sorted(words)

    @staticmethod
    def _get_word_frequency() -> dict[str, float]:
        """Returns a list of possible words.

        Returns:
            _type_: Returns the list of possible words we can guess
        """
        fp = os.path.abspath(__file__)
        path = os.path.join(os.path.dirname(fp), "unigram_freq.csv")
        words_f = {}
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "word" and row[1] == "count":
                    continue
                words_f[row[0]] = int(row[1])
        _sum = sum(words_f[i] for i in words_f if len(i) == WORDLE_WORD_LENGTH)
        return {word: float(words_f[word]) / _sum for word in words_f if len(word) == WORDLE_WORD_LENGTH}

    def _pick_starting_word(self) -> str:
        """Returns a random starting word.

        Returns:
            str: the word to start the guesses with
        """
        _default_weight = 2

        # try calculate weights from success rate
        _attempts = {}

        _flag = random.random()
        if _flag < 0.25:  # noqa: PLR2004
            # pick a new starting word to refine our starting word list
            starting_word = self._pick_word_from_list()
            if isinstance(starting_word, list):
                starting_word = starting_word[0]
        else:
            for word in self._starting_words:
                results: list[WordleAttemptDB] = self.wordles.query({"starting_word": word})

                if not results:
                    _attempts[word] = _default_weight
                    continue

                results = sorted(results, key=lambda x: x.timestamp)
                _last_timestamp = None
                _scores = []
                for res in results:
                    # gotta do this as we don't have guild ID here to limit
                    if res.timestamp == _last_timestamp:
                        continue
                    _last_timestamp = res.timestamp
                    _scores.append(res.guess_count)
                _attempts[word] = 6 - (sum(_scores) / len(_scores))

            _sorted_words = sorted(_attempts, key=lambda x: _attempts[x], reverse=True)
            starting_word = random.choices(_sorted_words, weights=[_attempts[w] for w in _sorted_words])[0]

        self.logger.debug("Selected: %s from %s", starting_word, _attempts)
        return starting_word

    def _pick_word_from_list(self) -> str:
        """Picks a word at random from the word list.

        Returns:
            str: _description_
        """
        return random.choices(
            self.possible_words,
            weights=[self.words_freq.get(word, 0) for word in self.possible_words],
        )

    def _filter_word_list(
        self, game_state: dict[str, any], present_letters: list[str], correct_letters: list[str]
    ) -> None:
        """Filters the possible word list based on our current game state.

        Args:
            game_state (dict): the current game state
        """
        new_possible_words = []

        answer_regex = "[{letter}]"
        not_letters = "[^{letters}]"

        _word_list = copy.deepcopy(self.words) if not self.possible_words else copy.deepcopy(self.possible_words)

        regex_search = []
        for index in game_state:
            if game_state[index]["answer"]:
                letter_regex = answer_regex.format(letter=game_state[index]["answer"])
            else:
                cannot = game_state[index]["cannot"]
                _letters = "".join(cannot)
                letter_regex = not_letters.format(letters=_letters)
            regex_search.append(letter_regex)
        pattern = "".join(regex_search)

        for word in _word_list:
            if re.match(pattern, word):
                # still need to filter to match 'present' letters
                for letter in present_letters:
                    if word.count(letter) < (present_letters.count(letter) + correct_letters.count(letter)):
                        break
                else:
                    new_possible_words.append(word)
        self.possible_words = new_possible_words

    @staticmethod
    def _get_rows(board: WebElement) -> list[WebElement]:
        return board.find_elements(By.CSS_SELECTOR, f"div[class*='{WORDLE_ROWS_CLASS_NAME}']")

    @staticmethod
    def _get_row_state(row: WebElement) -> list[str]:
        children = row.find_elements(By.XPATH, ".//*")
        responses = []
        for child in children:
            ds = child.get_attribute("data-state")
            if ds is not None:
                responses.append(ds)
        return responses

    def _terminate(self) -> None:
        self.driver.close()
        self.driver = None

    def _get_board(self) -> WebElement:
        return self.driver.find_element(By.CSS_SELECTOR, f"div[class*='{WORDLE_BOARD_CLASS_NAME}']")

    async def _get_wordle_number(self) -> str:
        """Gets the wordle number from the footnote.

        Returns:
            str: the wordle number
        """
        settings_button = self.driver.find_element(By.ID, WORDLE_SETTINGS_BUTTON)
        settings_button.click()
        await asyncio.sleep(1)
        footnote = self.driver.find_element(By.CSS_SELECTOR, f"div[class*='{WORDLE_FOOTNOTE}']")
        p_children = footnote.find_elements(By.TAG_NAME, "p")
        number_p = p_children[1]
        wordle_number = number_p.text.strip().strip("#")
        self.action_chain.send_keys(Keys.ESCAPE).perform()
        await asyncio.sleep(1)
        return wordle_number

    async def _submit_word(self, word: str) -> None:
        self.action_chain.send_keys(word).perform()
        self.action_chain.send_keys(Keys.ENTER).perform()
        # wait for animations
        await asyncio.sleep(3)

    async def solve(self) -> WordleSolve:  # noqa: C901, PLR0912, PLR0915
        """Main solve method.

        Attempts to solve the wordle.

        Returns:
            WordleSolve: the solve data class
        """
        # wait to load
        await asyncio.sleep(2)
        solved = False
        row = 0
        actual_word = ["", "", "", "", ""]
        game_state = {
            0: {"answer": None, "cannot": []},
            1: {"answer": None, "cannot": []},
            2: {"answer": None, "cannot": []},
            3: {"answer": None, "cannot": []},
            4: {"answer": None, "cannot": []},
        }
        guesses = []
        emoji_str = ""
        wordle_number = await self._get_wordle_number()

        board = self._get_board()
        rows = self._get_rows(board)
        # doing a click to focus the stuff
        try:
            board.click()
        except ElementClickInterceptedException:
            self.logger.debug("Failed to press board - clicking container instead")
            container = self.driver.find_element(By.CSS_SELECTOR, "div[class*='App-module_gameContainer__']")
            container.click()

        _starting_word = None

        while not solved:
            self.logger.info("Guess number: %s", row + 1)

            # iterate until we solve the wordle
            if row == 0:
                word = self._pick_starting_word()
                _starting_word = word
            else:
                word = self._pick_word_from_list()

            if isinstance(word, list):
                word = word[0]

            guesses.append(word)

            self.logger.info("Selected %s", word)

            await self._submit_word(word)
            state = self._get_row_state(rows[row])
            idx = 0
            possible_denies = []
            present_letters = []
            correct_letters = []
            for idx, tile in enumerate(state):
                letter = word[idx]
                if tile == "absent":
                    # this letter isn't anywhere
                    possible_denies.append(letter)
                    emoji_str += "⬛"
                elif tile == "correct":
                    # we found a letter!
                    actual_word[idx] = letter
                    game_state[idx]["answer"] = letter
                    correct_letters.append(letter)
                    emoji_str += "🟩"
                elif tile == "present":
                    # present somewhere but not where we are
                    present_letters.append(letter)
                    game_state[idx]["cannot"].append(letter)
                    emoji_str += "🟨"
            emoji_str += "\n"

            for letter in possible_denies:
                if letter in present_letters:
                    continue
                for index in game_state:
                    if game_state[index]["answer"]:
                        continue
                    game_state[index]["cannot"].append(letter)

            if all(actual_word):
                # solved
                actual_word = "".join(actual_word)
                self.logger.info("We got it right - %s", actual_word)
                solved = True
                continue

            self._filter_word_list(game_state, present_letters, correct_letters)
            self.logger.debug("After: %s - there are %s possible words remaining", word, len(self.possible_words))

            if row == WORDLE_WORD_LENGTH:
                # we failed
                self.logger.debug("We failed to do the wordle...")
                break
            row += 1

        await asyncio.sleep(1)
        guess_num = "X" if not solved else len(guesses)
        share_text = f"Wordle {wordle_number} {guess_num}/6\n\n{emoji_str}"

        self.logger.info("Got share text to be: %s", share_text)
        self._terminate()

        if solved and guess_num <= WORDLE_EXCELLENT_GUESS_NUM and _starting_word not in self._starting_words:
            self.logger.info("Added %s to the list of starting words", _starting_word)
            self.data_store.add_starting_word(_starting_word)

        return WordleSolve(
            solved,
            guesses,
            guesses[0],
            len(guesses),
            actual_word,
            game_state,
            datetime.datetime.now(tz=ZoneInfo("UTC")),
            share_text,
            int(wordle_number),
        )


if __name__ == "__main__":
    solver = WordleSolver(headless=False)
    asyncio.run(solver.setup())
    asyncio.run(solver.solve())
