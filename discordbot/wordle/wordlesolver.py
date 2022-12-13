import asyncio
import copy
import datetime
import os
import time
import random
import re
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.firefox import GeckoDriverManager

from discordbot.wordle.constants import WORDLE_GDPR_ACCEPT_ID, WORDLE_TUTORIAL_CLOSE_CLASS_NAME, WORDLE_SHARE_ID
from discordbot.wordle.constants import WORDLE_BOARD_CLASS_NAME, WORDLE_ROWS_CLASS_NAME, WORDLE_URL, WORDLE_FOOTNOTE
from discordbot.wordle.constants import WORDLE_STARTING_WORDS, WORDLE_SETTINGS_BUTTON


@dataclass
class WordleSolve:
    solved: bool
    guesses: list
    starting_word: str
    guess_count: int
    actual_word: str
    game_state: dict
    timestamp: datetime.datetime
    share_text: str
    wordle_num: int


class WordleSolver():
    def __init__(self, logger) -> None:
        self.firefox_opts = Options()
        self.firefox_opts.headless = True
        self.words = self._get_words()
        self.driver = None
        self.action_chain = None
        self.possible_words = []
        self.logger = logger

    async def get_driver(self) -> None:
        """
        Gets the necessary driver using the driver manager (downloads and installs if necessary)
        Creates a WebDriver object
        Navigates to wordle web page
        Clears GDPR and tutorial

        Returns:
            webdriver.Firefox: the instantiated driver
        """
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=self.firefox_opts
        )
        driver.get(WORDLE_URL)
        await asyncio.sleep(2)
        try:
            accept_button = driver.find_element(By.ID, WORDLE_GDPR_ACCEPT_ID)
            accept_button.click()
        except (ElementNotInteractableException, StaleElementReferenceException):
            pass

        try:
            close_button = driver.find_element(By.CLASS_NAME, WORDLE_TUTORIAL_CLOSE_CLASS_NAME)
            close_button.click()
        except (ElementNotInteractableException, StaleElementReferenceException):
            pass
        
        self.driver = driver
        self.action_chain = ActionChains(self.driver)

    @staticmethod
    def _get_words() -> list[str]:
        """
        Returns a list of possible words

        Returns:
            _type_: Returns the list of possible words we can guess
        """
        fp = os.path.abspath(__file__)
        path = os.path.join(os.path.dirname(fp), "wordle_guesses")
        with open(path) as f:
            words = [line.rstrip() for line in f]
        return sorted(words)

    @staticmethod
    def _pick_starting_word() -> str:
        """
        Returns a random starting word

        Returns:
            str: the word to start the guesses with
        """
        starting_worde = random.choice(WORDLE_STARTING_WORDS)
        return starting_worde

    def _pick_word_from_list(self) -> str:
        """Picks a word at random from the word list

        Returns:
            str: _description_
        """
        word = random.choice(self.possible_words)
        return word

    def _filter_word_list(self, game_state: dict, present_letters: list, correct_letters: list) -> None:
        """Filters the possible word list based on our current game state

        Args:
            game_state (dict): the current game state
        """
        new_possible_words = []

        answer_regex = "[{letter}]"
        not_letters = "[^{letters}]"

        if not self.possible_words:
            _word_list = copy.deepcopy(self.words)
        else:
            _word_list = copy.deepcopy(self.possible_words)

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
                    if not word.count(letter) >= (present_letters.count(letter) + correct_letters.count(letter)):
                        break
                else:
                    new_possible_words.append(word)
        self.possible_words = new_possible_words

    @staticmethod
    def _get_rows(board: WebElement) -> list[WebElement]:
        rows = board.find_elements(By.CLASS_NAME, WORDLE_ROWS_CLASS_NAME)
        return rows

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
        board = self.driver.find_element(By.CLASS_NAME, WORDLE_BOARD_CLASS_NAME)
        return board
    
    async def _get_wordle_number(self) -> str:
        """Gets the wordle number from the footnote

        Returns:
            str: the wordle number
        """
        settings_button = self.driver.find_element(By.ID, WORDLE_SETTINGS_BUTTON)
        settings_button.click()
        await asyncio.sleep(1)
        footnote = self.driver.find_element(By.CLASS_NAME, WORDLE_FOOTNOTE)
        div_children = footnote.find_elements(By.TAG_NAME, "div")
        number_div = div_children[1]
        wordle_number = number_div.text.strip().strip("#")
        self.action_chain.send_keys(Keys.ESCAPE).perform()
        await asyncio.sleep(1)
        return wordle_number

    async def _submit_word(self, word: str) -> None:
        self.action_chain.send_keys(word).perform()
        self.action_chain.send_keys(Keys.ENTER).perform()
        # wait for animations
        await asyncio.sleep(3)

    async def solve(self) -> WordleSolve:
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
            4: {"answer": None, "cannot": []}
        }
        guesses = []
        emoji_str = ""
        wordle_number = await self._get_wordle_number()

        board = self._get_board()
        rows = self._get_rows(board)
        # doing a click to focus the stuff
        board.click()
        
        while not solved:
            self.logger.info(f"Guess number: {row + 1}")

            # iterate until we solve the wordle
            if row == 0:
                word = self._pick_starting_word()
            else:
                word = self._pick_word_from_list()

            guesses.append(word)

            self.logger.info(f"Selected {word}")

            await self._submit_word(word)
            state = self._get_row_state(rows[row])
            idx = 0
            possible_denies = []
            present_letters = []
            correct_letters = []
            for tile in state:
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
                idx += 1
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
                self.logger.info(f"We got it right - {actual_word}")
                solved = True
                continue

            self._filter_word_list(game_state, present_letters, correct_letters)
            self.logger.debug(f"After: {word} - there are {len(self.possible_words)} possible words remaining")

            if row == 5:
                # we failed
                self.logger.debug(f"We failed to do the wordle...")
                break
            row += 1

        await asyncio.sleep(1)
        guess_num = "X" if not solved else len(guesses)
        share_text = (
            f"Wordle {wordle_number} {guess_num}/6\n\n"
            f"{emoji_str}"
        )

        self.logger.info(f"Got share text to be: {share_text}")
        self._terminate()

        data_class = WordleSolve(
            solved,
            guesses,
            guesses[0],
            len(guesses),
            actual_word,
            game_state,
            datetime.datetime.now(),
            share_text,
            int(wordle_number)
        )

        return data_class
