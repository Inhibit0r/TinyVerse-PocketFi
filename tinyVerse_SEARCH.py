from asyncio import timeout

import requests
import os
import time
import logging
import json
import random
from forall import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

debug = True

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


class BrowserManager:

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.driver = None

    def check_browser_status(self):
        try:
            response = requests.get(
                'http://local.adspower.net:50325/api/v1/browser/active',
                params={'serial_number': self.serial_number}
            )
            data = response.json()
            if data['code'] == 0 and data['data']['status'] == 'Active':
                logging.info(f"Account {self.serial_number}: Browser is already active.")
                return True
            else:
                return False
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in checking browser status: {str(e)}")
            return False

    def start_browser(self):
        try:
            if self.check_browser_status():
                logging.info(f"Account {self.serial_number}: Browser already open. Closing the existing browser.")
                self.close_browser()
                time.sleep(5)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            requestly_extension_path = os.path.join(script_dir, 'blum_unlocker_extension')

            if debug:
                launch_args = json.dumps([f"--load-extension={requestly_extension_path}"])
                headless_param = "0"
            else:
                launch_args = json.dumps(["--headless=new", f"--load-extension={requestly_extension_path}"])
                headless_param = "1"

            request_url = (
                f'http://local.adspower.net:50325/api/v1/browser/start?'
                f'serial_number={self.serial_number}&ip_tab=1&headless={headless_param}&launch_args={launch_args}'
            )

            response = requests.get(request_url)
            data = response.json()
            if data['code'] == 0:
                selenium_address = data['data']['ws']['selenium']
                webdriver_path = data['data']['webdriver']
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", selenium_address)

                service = Service(executable_path=webdriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_window_size(600, 900)
                logging.info(f"Account {self.serial_number}: Browser started successfully.")
                return True
            else:
                logging.warning(f"Account {self.serial_number}: Failed to start the browser. Error: {data['msg']}")
                return False
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in starting browser: {str(e)}")
            return False

    def close_browser(self):
        try:
            if self.driver:
                try:
                    self.driver.close()
                    self.driver.quit()
                    self.driver = None
                    logging.info(f"Account {self.serial_number}: Browser closed successfully.")
                except WebDriverException as e:
                    logging.info(f"Account {self.serial_number}: exception, Browser should be closed now")
        except Exception as e:
            logging.exception(
                f"Account {self.serial_number}: General Exception occurred when trying to close the browser: {str(e)}")
        finally:
            try:
                response = requests.get(
                    'http://local.adspower.net:50325/api/v1/browser/stop',
                    params={'serial_number': self.serial_number}
                )
                data = response.json()
                if data['code'] == 0:
                    logging.info(f"Account {self.serial_number}: Browser closed successfully.")
                else:
                    logging.info(f"Account {self.serial_number}: exception, Browser should be closed now")
            except Exception as e:
                logging.exception(
                    f"Account {self.serial_number}: Exception occurred when trying to close the browser: {str(e)}")


class TelegramBotAutomation:
    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.browser_manager = BrowserManager(serial_number)
        logging.info(f"Initializing automation for account {serial_number}")
        self.browser_manager.start_browser()
        self.driver = self.browser_manager.driver

    def sleep(self, a, b):
        sleep_time = random.randrange(a, b)
        logging.info(f"Account {self.serial_number}: {sleep_time}sec sleep...")
        time.sleep(sleep_time)

    def navigate_to_bot(self):
        try:
            self.driver.get('https://web.telegram.org/k/')
            logging.info(f"Account {self.serial_number}: Navigated to Telegram web.")
            # Сохраняем текущий URL основной вкладки
            self.main_tab_url = self.driver.current_url
        except Exception as e:
            logging.exception(f"Account {self.serial_number}: Exception in navigating to Telegram bot: {str(e)}")
            self.browser_manager.close_browser()

    def send_message(self, message):
        chat_input_area = self.wait_for_element(By.XPATH,
                                                '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/input[1]')
        chat_input_area.click()
        chat_input_area.send_keys(message)

        search_area = self.wait_for_element(By.XPATH,
                                            '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/ul[1]/a[1]/div[1]')
        search_area.click()
        logging.info(f"Account {self.serial_number}: Group searched.")
        self.sleep(2, 3)

    def click_link(self):
        link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='https://t.me/TVerse?startapp=galaxy-0001d27add0002dfcc1f0000a93a7a']")
        link.click()

        logging.info(f"Account {self.serial_number}: TINY STARTED")
        sleep_time = random.randrange(4, 8)
        logging.info(f"Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        if not self.switch_to_iframe():
            logging.info(f"Account {self.serial_number}: No iframes found")
            return

    def switch_to_iframe(self):
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            self.driver.switch_to.frame(iframes[0])
            return True
        return False


    def back(self):
        self.driver.switch_to.default_content()
        self.wait_for_element(By.XPATH,
                              '/html/body/div[6]/div/div[1]/button[1]'
                              ).click()
        time.sleep(2)
        self.switch_to_iframe()

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def wait_for_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located((by, value))
        )

    def click_launch_button(self):
        logging.info(f"Account {self.serial_number}: Trying to click Launch button.")
        launch_button = self.wait_for_element(
            By.XPATH,
            "//body/div[@class='popup popup-peer popup-confirmation active']/div[@class='popup-container z-depth-1']/div[@class='popup-buttons']/button[1]/div[1]"
        )
        launch_button.click()
        logging.info(f"Account {self.serial_number}: Clicked Launch button.")
        self.sleep(5, 7)

    def click_begin_your_own_journey_button(self):
        logging.info(f"Account {self.serial_number}: Trying to click 'Begin your own journey' button.")
        begin_journey_button = self.wait_for_element(
            By.XPATH,
            "/html[1]/body[1]/div[2]/div[1]/div[1]/div[4]/a[1]"
            ,timeout=10
        )

        button_text = begin_journey_button.text.strip()
        logging.info(f"Account {self.serial_number}: Found button with text: '{button_text}'")
        self.sleep(2, 5)

        if button_text == "Begin your own journey":
            begin_journey_button.click()
            self.sleep(2, 5)
            logging.info(f"Account {self.serial_number}: Clicked 'Begin your own journey' button.")
        else:
            logging.info(
                f"Account {self.serial_number}: Button text '{button_text}' does not match 'Begin your own journey', skipping click.")

    def click_begin_button(self):
        logging.info(f"Account {self.serial_number}: Trying to click 'Begin' button.")
        begin_button = self.wait_for_element(
            By.XPATH,
            "/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/div[3]/button",timeout=10
        )

        button_text = begin_button.text.strip()
        self.sleep(1, 3)

        if button_text == "Begin Journey":
            begin_button.click()
            logging.info(f"Account {self.serial_number}: Clicked 'Begin' button.")
            self.sleep(2, 4)
        else:
            logging.info(
                f"Account {self.serial_number}: Button text '{button_text}' does not match 'Begin', skipping click.")

    def first_try(self):
        # Шаг 1: Launch Button
        try:
            self.click_launch_button()
            self.switch_to_iframe()
            self.sleep(1, 2)
        except TimeoutException:
            logging.info(f"Account {self.serial_number}: Launch button not found due to timeout.")
        except NoSuchElementException:
            logging.info(f"Account {self.serial_number}: Launch button not found.")
        except WebDriverException as e:
            logging.info(f"Account {self.serial_number}: WebDriverException while clicking Launch button: {e}")
        except Exception as e:
            logging.info(f"Account {self.serial_number}: Unexpected error while clicking Launch button: {e}")

        # Шаг 2: Begin your own journey
        try:
            self.click_begin_your_own_journey_button()
        except TimeoutException:
            logging.info(f"Account {self.serial_number}: 'Begin your own journey' button not found due to timeout.")
        except NoSuchElementException:
            logging.info(f"Account {self.serial_number}: 'Begin your own journey' button not found.")
        except WebDriverException as e:
            logging.info(
                f"Account {self.serial_number}: WebDriverException while clicking 'Begin your own journey': {e}")
        except Exception as e:
            logging.info(f"Account {self.serial_number}: Unexpected error while clicking 'Begin your own journey': {e}")

        # Шаг 3: Begin Button
        try:
            self.click_begin_button()
        except TimeoutException:
            logging.info(f"Account {self.serial_number}: 'Begin' button not found due to timeout.")
        except NoSuchElementException:
            logging.info(f"Account {self.serial_number}: 'Begin' button not found.")
        except WebDriverException as e:
            logging.info(f"Account {self.serial_number}: WebDriverException while clicking 'Begin': {e}")
        except Exception as e:
            logging.info(f"Account {self.serial_number}: Unexpected error while clicking 'Begin': {e}")

    def click_home(self):
        try:
            # Ищем SVG path внутри кнопки Home
            home_path = self.wait_for_element(
                By.XPATH,
                "/html[1]/body[1]/div[2]/div[1]/div[1]/div[3]/a[1]/*[name()='svg'][1]/*[name()='path'][1]"
            )

            # Получаем атрибут d из path
            path_d = home_path.get_attribute("d")
            logging.info(f"Account {self.serial_number}: Home path 'd' attribute = {path_d}")

            expected_d = "M4 7L10 2L16 7V16H4V7Z"
            if path_d == expected_d:
                # Если атрибут совпадает с ожидаемым, кликаем по кнопке Home
                home_button = self.wait_for_element(
                    By.XPATH,
                    "/html[1]/body[1]/div[2]/div[1]/div[1]/div[3]/a[1]"
                )
                home_button.click()
                logging.info(f"Account {self.serial_number}: Clicked Home button.")
                self.sleep(2, 4)
            else:
                # Если атрибут не совпадает, пропускаем клик
                logging.info(f"Account {self.serial_number}: Home icon does not match expected shape, skipping click.")

        except TimeoutException:
            logging.info(f"Account {self.serial_number}: Home button not found, skipping.")
        except NoSuchElementException:
            logging.info(f"Account {self.serial_number}: Home button not found, skipping.")
        except Exception as e:
            logging.info(f"Account {self.serial_number}: Error in click_home: {e}")

    def set_slider_to_zero(self):
        try:

            search_button = self.wait_for_element(
                By.XPATH,
                "/html[1]/body[1]/div[2]/div[1]/div[1]/div[4]/a[3]"
            )
            search_button.click()
            logging.info(f"Account {self.serial_number}: clicked search.")

            self.sleep(5, 6)

            text_element = self.wait_for_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/div[2]/div/div[1]/div[1]/h1/span"
            )
            found_text = text_element.text.strip()

            if found_text in ["Ничего...", "Поиск"]:
                logging.info(f"Account {self.serial_number}: text is 'Ничего...', proceeding with slider adjustment.")
            else:
                logging.info(f"Account {self.serial_number}: text is '{found_text}', stopping work on slider.")
                return

            slider_xpath = "/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/input"
            slider = self.wait_for_element(By.XPATH, slider_xpath)

            self.driver.execute_script("arguments[0].value = 0;", slider)

            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                slider
            )

            logging.info(f"Account {self.serial_number}: Slider set to 0%.")
            self.sleep(2, 4)

            scan_button = self.wait_for_element(
                By.XPATH,
                "/html[1]/body[1]/div[2]/div[3]/div[2]/div[1]/div[1]/div[3]/button[1]"
            )
            scan_button.click()
            logging.info(f"Account {self.serial_number}: pressed scan.")
            self.sleep(3, 5)

        except Exception as e:
            logging.info(f"Account {self.serial_number}: Error while setting slider to 0: {e}")


def read_accounts_from_file():
    with open('accounts_tinyVerse_search.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]


def write_accounts_to_file(accounts):
    with open('accounts_tinyVerse_search.txt', 'w') as file:
        for account in accounts:
            file.write(f"{account}\n")


def process_accounts():
    last_processed_account = None

    while True:

        accounts = read_accounts_from_file()
        random.shuffle(accounts)
        write_accounts_to_file(accounts)
        i = 0
        while i < len(accounts):
            remove_empty_lines('locked_accounts.txt')
            remove_key_lines('locked_accounts.txt', 'TINY_SEARCH')

            retry_count = 0
            i += 1
            success = False
            if is_account_locked(accounts[i - 1]):
                if i == len(accounts):
                    retry_count = 3
                else:
                    accounts.append(accounts[i - 1])
                    accounts.pop(i - 1)
                    print(accounts)
                    i -= 1


            else:

                while retry_count < 3 and not success:
                    lock_account(accounts[i - 1], 'TINY_SEARCH')
                    bot = TelegramBotAutomation(accounts[i - 1])
                    bot.scrshot = 0  # 0 for no screenshots
                    try:
                        bot.navigate_to_bot()
                        bot.send_message("https://t.me/malenkaygalaktikadao")
                        bot.click_link()
                        bot.click_home()
                        bot.set_slider_to_zero()
                        logging.info(f"Account {accounts[i - 1]}: Processing completed successfully.")
                        success = True
                    except Exception as e:
                        logging.warning(f"Account {accounts[i - 1]}: Error occurred on attempt {retry_count + 1}: {e}")
                        retry_count += 1
                    finally:
                        logging.info("-------------END-----------")
                        bot.browser_manager.close_browser()
                        logging.info("-------------END-----------")
                        unlock_account(accounts[i - 1], "TINY_SEARCH")
                        sleep_time = random.randrange(4, 6)
                        logging.info(f"Sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)

                    if retry_count >= 3:
                        logging.warning(f"Account {accounts[i - 1]}: Failed after 3 attempts.")

            if not success:
                logging.warning(f"Account {accounts[i - 1]}: Moving to next account after 3 failed attempts.")

        wait_minutes = 20
        for minute in range(wait_minutes):
            logging.info(f"Waiting... {wait_minutes - minute} minute(s) left till restart.")
            time.sleep(60)
        logging.info("Shuffling accounts for the next cycle.")


if __name__ == "__main__":
    process_accounts()