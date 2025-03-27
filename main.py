import os
import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementNotInteractableException,
    InvalidSessionIdException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
import platform
import yaml

CURRENT_OS = platform.system()
if CURRENT_OS == "Windows":
    import winsound


# TODO: add chrome support
class Selenium:
    def __init__(self):
        self.picked_url = ""
        self.option = Options()
        self.option.page_load_strategy = "none"
        self.driver = Firefox(options=self.option)
        self.wait = WebDriverWait(self.driver, 60)
        self.all_projects = []
        self.new_projects = []

    def get_ready_state(self) -> bool:
        ready_state = self.driver.execute_script("return document.readyState")
        return ready_state == "complete"

    def login(self, user: str, password: str) -> None:
        print("usr =", user)
        print("psw =", password)
        self.driver.get(r"https://ponisha.ir/users/login")

        # Wait until the page's readyState is 'complete'
        self.wait.until(ec.presence_of_element_located((By.ID, "input-username")))
        self.wait.until(lambda _: self.get_ready_state())
        input_username = self.driver.find_element(By.ID, "input-username")
        input_username.send_keys(user)
        _ = self.wait.until(ec.element_to_be_clickable((By.TAG_NAME, "button")))
        if input_username.get_attribute("value"):
            login_button = self.driver.find_element(By.TAG_NAME, "button")
            login_button.click()

        # # logging in via phone number requires this step
        # self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-198qifb')))
        # button = self.driver.find_element(By.CLASS_NAME, 'css-198qifb')
        # button.click()

        _ = self.wait.until(ec.presence_of_element_located((By.ID, "input-password")))
        password_input = self.driver.find_element(By.ID, "input-password")
        password_input.send_keys(password)
        self.wait.until(lambda _: self.get_ready_state())
        password_action_container = self.driver.find_element(
            By.ID, "auth__action-button-container"
        )
        password_action_container.find_element(By.TAG_NAME, "button").click()
        self.go_to_projects_page()

    def go_to_projects_page(self):
        self.wait.until(lambda _: self.get_ready_state())
        _ = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href^='/search/projects?filter']")
            )
        )
        search_link = self.driver.find_element(
            By.CSS_SELECTOR, "a[href^='/search/projects?filter']"
        )
        search_page_link = str(search_link.get_attribute("href"))
        self.driver.get(search_page_link)
        self.wait.until(lambda _: self.get_ready_state())
        # TODO: add skill picking

        # python_url = (r'https://ponisha.ir/dashboard/find-projects?skills[0]'
        #              r'[id]=102&skills[0][title]=%D9%BE%D8%A7%DB%8C%D8%AA%D9%88%D9%86%20(Python)')
        # all_url = r'https://ponisha.ir/dashboard/find-projects?filterSkillsByUserId=1071865'
        # if self.project_type == 'p':
        #    self.picked_url = python_url
        # else:
        #    self.picked_url = all_url
        # self.driver.get(python_url)

    # grabs first project
    def grab_first_project(self):
        tries = 10
        first_project = None
        errors = []
        delay = 10
        self.all_projects = []
        self.new_projects = []
        while tries > 0:
            try:
                _ = self.wait.until(
                    ec.presence_of_element_located((By.ID, "input-query"))
                )
                self.wait.until(lambda _: self.get_ready_state())
                all_project_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "a[href^='/project/']"
                )

                all_url_elements = [
                    project
                    for project in all_project_elements
                    if project.is_displayed()
                    and project.is_enabled()
                    and not (project.find_elements(By.TAG_NAME, "button"))
                ]
                all_project_parents = [
                    project.find_element(By.XPATH, "./../../../..")
                    for project in all_url_elements
                ]
                for i in range(len(all_project_parents)):
                    project_parent = all_project_parents[i]
                    project_price_range = self.get_price_range(project_parent)
                    project_title = project_parent.find_element(
                        By.TAG_NAME, "span"
                    ).text
                    project_data = {
                        "title": project_title,
                        "link": all_url_elements[i].get_attribute("href"),
                        "price_range": project_price_range,
                    }
                    self.all_projects.append(project_data)
                first_project = self.all_projects[0]
                break
            except TimeoutException as error:
                errors.append(error)
                tries = tries - 1
                print("there was a problem refreshing page...")
                self.all_projects = []
                self.driver.refresh()
                continue
            except (
                NoSuchElementException,
                StaleElementReferenceException,
                IndexError,
            ) as error:
                errors.append(error)
                tries = tries - 1
                print(f"there was a problem refreshing page after {delay} seconeds...")
                time.sleep(delay)
                self.all_projects = []
                self.driver.refresh()
                delay = delay + 1
                continue
        if tries <= 0:
            self.notify_user("error", False, "just_notify")
            print(errors)
            raise TimeoutException

        return first_project

    def get_price_range(self, project) -> list:
        price_range_list = []
        budget_section = project.find_element(
            By.CSS_SELECTOR, 'div[aria-label="بودجه کارفرما"]'
        )
        price_range = budget_section.find_element(By.TAG_NAME, "span")
        price_range = price_range.text
        price_range_list = price_range.split("تا")
        price_range_list = [
            price.replace(",", "").strip("از").strip("بیش از").strip("تومان").strip()
            for price in price_range_list
        ]
        return price_range_list

    def get_messages(self) -> str:
        tries = 4
        chat_number = ""
        last_error = Exception
        while tries > 0:
            try:
                self.wait.until(lambda _: self.get_ready_state())
                _ = self.wait.until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button[aria-label="Chats"]')
                    )
                )
                chat_wrapper = self.driver.find_element(
                    By.CSS_SELECTOR, 'button[aria-label="Chats"]'
                )
                chat_number = (
                    chat_wrapper.find_element(By.TAG_NAME, "span")
                    .find_element(By.TAG_NAME, "span")
                    .text
                )
                break
            except (
                TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException,
            ) as error:
                tries = tries - 1
                print("there was a problem refreshing page...")
                last_error = error
                self.driver.refresh()
                continue
        if tries <= 0:
            raise last_error
        return chat_number

    def auto_send_request(self, message: str, project) -> None:
        tries = 4
        message = message.strip()
        price_range = project["price_range"]
        if len(price_range) >= 2:
            price = int((int(price_range[0]) + int(price_range[-1])) / 2)
        else:
            price = int(price_range[-1])

        self.driver.get(project["link"])
        while tries > 0:
            try:
                button_span = self.wait.until(
                    ec.presence_of_element_located(
                        (By.XPATH, "//span[text()='ارسال پیشنهاد']")
                    )
                )
                self.wait.until(lambda _: self.get_ready_state())
                button_span.find_element(By.XPATH, "./..").click()
                self.wait.until(ec.element_to_be_clickable((By.ID, "input-amount")))
                self.driver.find_element(By.ID, "input-amount").send_keys(str(price))
                self.driver.find_element(By.ID, "input-days").send_keys("7")
                self.driver.find_element(By.ID, "input-payments.0.title").send_keys(
                    "انجام پروژه"
                )
                self.driver.find_element(By.ID, "input-payments.0.amount").send_keys(
                    str(price)
                )
                self.driver.find_element(By.ID, "input-description").send_keys(message)
                submit_button = self.driver.find_element(
                    By.CSS_SELECTOR, 'button[type="submit"]'
                )
                submit_button.click()
                break
            except (
                TimeoutException,
                NoSuchElementException,
                StaleElementReferenceException,
                ElementNotInteractableException,
            ):
                tries = tries - 1
                print("there was a problem refreshing page...")
                self.driver.refresh()
                continue

        if tries <= 0:
            raise TimeoutException

    def handle_auto_requests(self, auto_req_state):
        auto_send_req_bool = True
        picked_project = self.new_projects[0]
        auto_send_request_input = "1"
        if auto_req_state == "ask_for_permission_everytime":
            auto_send_request_input = menu_generator(
                "Would you like the bot to send a request automatically to one of these projects ?",
                ["YES", "NO"],
                False,
                clear=False,
            )
        if auto_send_request_input == "1":
            if len(self.new_projects) > 1:
                if auto_req_state == "ask_for_permission_everytime":
                    picked_project_str = menu_generator(
                        "Which project do you want to send a request to ?",
                        [project["title"] for project in self.new_projects],
                        False,
                        clear=False,
                    )
                    picked_project = self.new_projects[(int(picked_project_str) - 1)]

                elif auto_req_state == "auto_send_without_asking":
                    picked_project = self.new_projects[0]
                else:
                    auto_send_req_bool = False
        else:
            auto_send_req_bool = False
        return auto_send_req_bool, picked_project

    def notify_user(
        self,
        message: str,
        game_mode: bool,
        state: str,
        auto_request_send: str = "dont_send_requests_automatically",
    ) -> tuple:
        keep_going = True
        auto_send_request_bool = False
        picked_project = None
        if state == "just_notify":
            if CURRENT_OS == "Windows":
                winsound.Beep(500, 1000)
            else:
                _ = os.system(f'spd-say "{message}"')
            if (
                auto_request_send == "ask_for_permission_everytime"
                or auto_request_send == "auto_send_without_asking"
            ):
                auto_send_request_bool, picked_project = self.handle_auto_requests(
                    auto_request_send
                )
        elif state == "notify_and_stop":
            if not game_mode:
                self.driver.maximize_window()
            if CURRENT_OS == "Windows":
                winsound.Beep(500, 1000)
            else:
                _ = os.system(f'spd-say "{message}"')
            if (
                auto_request_send == "ask_for_permission_everytime"
                or auto_request_send == "auto_send_without_asking"
            ):
                auto_send_request_bool, picked_project = self.handle_auto_requests(
                    auto_request_send
                )
            keep_going_str = menu_generator(
                header="Would you like to keep going?",
                content_list=["YES", "NO"],
                is_main_menu=False,
                clear=False,
            )
            if keep_going_str == "1":
                keep_going = True
            else:
                keep_going = False
        return keep_going, auto_send_request_bool, picked_project

    def compare_projects(self, old_project, new_project, price_filter):
        is_same = True
        old_project_link = old_project["link"]
        new_project_link = new_project["link"]
        if old_project_link != new_project_link:
            try:
                index_of_old_project = self.all_projects.index(old_project)
                new_projects = self.all_projects[:index_of_old_project]
            except ValueError:
                new_projects = self.all_projects
            self.new_projects = [
                project
                for project in new_projects
                if int(project["price_range"][-1]) >= price_filter
            ]
            if self.new_projects:
                is_same = False
        return is_same, self.new_projects


def save_to_yaml(
    file_name: str,
    message: str,
    username: str,
    password: str,
    game_mode: bool,
    price_filter: int,
    auto_request_send: str,
    message_state: str,
    project_state: str,
) -> None:
    base_data = dict(
        message=message,
        user_name=username,
        password=password,
        game_mode=game_mode,
        price_filter=price_filter,
        auto_send_req=auto_request_send,
        message_state=message_state,
        project_state=project_state,
    )
    pathname = os.path.dirname(os.path.abspath(__file__))
    with open(pathname + "/" + file_name, "w", encoding="utf8") as f:
        yaml.dump(base_data, f, default_flow_style=False)


def load_yaml_file(file_name: str) -> tuple:
    pathname = os.path.dirname(os.path.abspath(__file__))
    with open(pathname + "/" + file_name, "r", encoding="utf8") as f:
        config_yaml = yaml.safe_load(f)
        request_message = config_yaml.get("message")
        username = config_yaml.get("user_name")
        pass_word = config_yaml.get("password")
        game_mode = config_yaml.get("game_mode")
        price_filter = config_yaml.get("price_filter")
        auto_send_req = config_yaml.get("auto_send_req")
        messages_state = config_yaml.get("message_state")
        project_state = config_yaml.get("project_state")
    return (
        config_yaml,
        request_message,
        username,
        pass_word,
        game_mode,
        price_filter,
        auto_send_req,
        messages_state,
        project_state,
    )


def menu_generator(
    header: str,
    content_list: list[str | None],
    is_main_menu: bool,
    pre_messages: list = [],
    clear: bool = True,
) -> str:
    if clear:
        os.system("cls" if os.name == "nt" else "clear")
        start_ascii = r"""
         _____            _     _                           _                        _           _ 
        |  __ \          (_)   | |               /\        | |                      | |         | |
        | |__) |__  _ __  _ ___| |__   __ _     /  \  _   _| |_ ___  _ __ ___   __ _| |_ ___  __| |
        |  ___/ _ \| '_ \| / __| '_ \ / _` |   / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __/ _ \/ _` |
        | |  | (_) | | | | \__ \ | | | (_| |  / ____ \ |_| | || (_) | | | | | | (_| | ||  __/ (_| |
        |_|   \___/|_| |_|_|___/_| |_|\__,_| /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__\___|\__,_|

        """
        print(start_ascii)
    if pre_messages:
        for message in pre_messages:
            print(message)
        print("----------------------------------------")
    print(header)
    if len(content_list) > 0:
        print("----------------------------------------")
    idx = 1
    for row in content_list:
        print(f"{idx} - {row}")
        idx = idx + 1
    if is_main_menu:
        print("0 - Exit")
    else:
        if content_list:
            if not content_list[-1] == "NO":
                print("0 - Back")
        else:
            print("0 - Back")
    user_answer = str(input("----------------------------------------\n"))
    return user_answer


def main_menu(pre_messages: list = []) -> tuple:
    main_menu = ["Start", "Settings"]
    run_app = menu_generator("Select one:", main_menu, True, pre_messages)
    if run_app == "1":
        try:
            (
                _,
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml(
                "data.yml",
                "",
                "",
                "",
                False,
                0,
                "dont_send_requests_automatically",
                "just_notify",
                "notify_and_stop",
            )
            (
                _,
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = load_yaml_file("data.yml")
        run_main_app(
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
    elif run_app == "2":
        (
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = simple_settings_menu()
    else:
        sys.exit()
    return (
        request_message,
        username,
        pass_word,
        game_mode,
        price_filter,
        auto_request_send,
        messages_state,
        project_state,
    )


def simple_settings_menu() -> tuple:
    try:
        (
            _,
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = load_yaml_file("data.yml")
    except FileNotFoundError:
        save_to_yaml(
            "data.yml",
            "",
            "",
            "",
            False,
            0,
            "dont_send_requests_automatically",
            "just_notify",
            "notify_and_stop",
        )
        (
            _,
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = load_yaml_file("data.yml")
    simple_settings_menu_list = ["Automatic Mode", "Manual Mode", "Advanced Settings"]
    user_picked_setting = menu_generator(
        "Pick a preset or change what you want in advanced settings:",
        simple_settings_menu_list,
        False,
        [],
    )
    if user_picked_setting == "1":
        auto_mode_head = "Automatic mode is for when you are not actively looking at the bot and want it to just send requests to all the available projects\n\
                          This mode still uses your filters just does not notify you or ask for you permission for anything"
        user_pick = menu_generator(auto_mode_head, ["Use Auto Mode"], False, [])
        if user_pick == "1":
            game_mode = False
            auto_request_send = "auto_send_without_asking"
            messages_state = "ignore"
            project_state = "ignore"
            changes_list = [
                "Automatic Mode is ON",
                'Game Mode was chnaged to "OFF"',
                'Auto Send was changed to "Auto Send Without Asking"',
                'Project Notification was changed to "Ignore"',
                'Messages Notification was changed to "Ignore"',
            ]
            save_to_yaml(
                "data.yml",
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
            main_menu(changes_list)
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = simple_settings_menu()
    elif user_picked_setting == "2":
        manual_mode_head = "Manual mode is for when you ARE actively looking at the bot and want it to ask you for permission and notify you for almost everything\n\
                            You can still just have the bot in the background and the bot notifies you when there is a new project but you need to give permission everytime"
        user_pick = menu_generator(manual_mode_head, ["Use Manual Mode"], False, [])
        if user_pick == "1":
            auto_request_send = "dont_send_requests_automatically"
            messages_state = "just_notify"
            project_state = "notify_and_stop"
            changes_list = [
                "Manual Mode is ON",
                'Auto Send was changed to "Dont Send Requests Automatically"',
                'Project Notification was changed to "Notify And Stop"',
                'Messages Notification was changed to "Notify Only"',
            ]
            save_to_yaml(
                "data.yml",
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
            main_menu(changes_list)
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = simple_settings_menu()
    elif user_picked_setting == "3":
        (
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = advanced_settings_menu()
    else:
        main_menu()
    return (
        request_message,
        username,
        pass_word,
        game_mode,
        price_filter,
        auto_request_send,
        messages_state,
        project_state,
    )


def advanced_settings_menu() -> tuple:
    try:
        (
            _,
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = load_yaml_file("data.yml")
    except FileNotFoundError:
        save_to_yaml(
            "data.yml",
            "",
            "",
            "",
            False,
            0,
            "dont_send_requests_automatically",
            "just_notify",
            "notify_and_stop",
        )
        (
            _,
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        ) = load_yaml_file("data.yml")
    if game_mode:
        game_mode_setting = "ON"
    else:
        game_mode_setting = "OFF"
    if price_filter:
        price_filter_setting = str(price_filter) + "000000"
    else:
        price_filter_setting = price_filter
    auto_request_setting = auto_request_send.replace("_", " ").title()
    if request_message:
        message_setting = "SET"
    else:
        message_setting = "EMPTY"
    messages_state_setting = messages_state.replace("_", " ").title()
    project_state_setting = project_state.replace("_", " ").title()
    settings_menu_list = [
        f"Username       |      {username}",
        f"Password       |      {pass_word}",
        f"Game Mode      |      {game_mode_setting}",
        f"Price Filter   |      {price_filter_setting}",
        f"Auto Send Req  |      {auto_request_setting}",
        f"Message        |      {message_setting}",
        f"Messages Notif |      {messages_state_setting}",
        f"Projects Notif |      {project_state_setting}",
    ]
    user_picked_setting = menu_generator(
        "Pick a setting to change:", settings_menu_list, False, []
    )
    if user_picked_setting == "1":
        input_username = menu_generator("Please enter your Email:", [], False)
        if input_username == "0":
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        prev_username = username
        username = input_username
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [f'Username was changed from "{prev_username}" to "{input_username}"']
        )
    elif user_picked_setting == "2":
        input_pass_word = menu_generator("Please enter your Password:", [], False)
        if input_pass_word == "0":
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        prev_password = pass_word
        pass_word = input_pass_word
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [f'Password was changed from "{prev_password}" to "{input_pass_word}"']
        )
    elif user_picked_setting == "3":
        input_game_mode = menu_generator(
            "Would you like to turn on game mode?(error sound only):",
            ["ON", "OFF"],
            False,
        )
        game_mode_setting_prev = game_mode_setting
        if input_game_mode == "1":
            game_mode = True
            game_mode_setting = "ON"
        elif input_game_mode == "2":
            game_mode = False
            game_mode_setting = "OFF"
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [
                f'Game Mode was changed from "{game_mode_setting_prev}" to "{game_mode_setting}"'
            ]
        )
    elif user_picked_setting == "4":
        input_price_filter = menu_generator(
            'Pick a price in millions (1 for 1,000,000 etc) for 0 enter "00":',
            [],
            False,
        )
        if input_price_filter == "0":
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        try:
            prev_price_filter = price_filter
            price_filter = int(input_price_filter)
        except ValueError:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [f'Price Filter was changed from "{prev_price_filter}" to "{price_filter}"']
        )
    elif user_picked_setting == "5":
        input_auto_request = menu_generator(
            "Would you like the bot to automatically send requests to projects or just norify you ?",
            [
                "Auto Send Without Asking",
                "Ask For Permission Everytime",
                "Dont Send Requests Automatically",
            ],
            False,
        )
        auto_request_setting_prev = auto_request_setting
        if input_auto_request == "1":
            auto_request_send = "auto_send_without_asking"
        elif input_auto_request == "2":
            auto_request_send = "ask_for_permission_everytime"
        elif input_auto_request == "3":
            auto_request_send = "dont_send_requests_automatically"
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        auto_request_setting = auto_request_send.replace("_", " ").title()
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [
                f'Auto send was changed from "{auto_request_setting_prev}" to "{auto_request_setting}"'
            ]
        )
    elif user_picked_setting == "6":
        input_request_message = menu_generator(
            "Enter your request message(note that it is recommended to edit the message directly in data.yml):",
            [],
            False,
        )
        if input_request_message == "0":
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        request_message = input_request_message
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(["request message has been changed"])
    elif user_picked_setting == "7":
        input_message_state = menu_generator(
            "What do you want the bot to do when you get a new message?:",
            ["Just Notify", "Notify And Stop", "Ignore"],
            False,
        )
        messages_state_setting_prev = messages_state_setting
        if input_message_state == "1":
            messages_state = "just_notify"
        elif input_message_state == "2":
            messages_state = "notify_and_stop"
        elif input_message_state == "3":
            messages_state = "ignore"
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        messages_state_setting = messages_state.replace("_", " ").title()
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [
                f'Messages Notification was changed from "{messages_state_setting_prev}" to "{messages_state_setting}"'
            ]
        )
    elif user_picked_setting == "8":
        input_project_state = menu_generator(
            "What do you want the bot to do when there is a new project?:",
            ["Just Notify", "Notify And Stop", "Ignore"],
            False,
        )
        project_state_setting_prev = project_state_setting
        if input_project_state == "1":
            project_state = "just_notify"
        elif input_project_state == "2":
            project_state = "notify_and_stop"
        elif input_project_state == "3":
            project_state = "ignore"
        else:
            (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            ) = advanced_settings_menu()
            return (
                request_message,
                username,
                pass_word,
                game_mode,
                price_filter,
                auto_request_send,
                messages_state,
                project_state,
            )
        project_state_setting = project_state.replace("_", " ").title()
        save_to_yaml(
            "data.yml",
            request_message,
            username,
            pass_word,
            game_mode,
            price_filter,
            auto_request_send,
            messages_state,
            project_state,
        )
        main_menu(
            [
                f'Project Notification was changed from "{project_state_setting_prev}" to "{project_state_setting}"'
            ]
        )
    else:
        simple_settings_menu()
    return (
        request_message,
        username,
        pass_word,
        game_mode,
        price_filter,
        auto_request_send,
        messages_state,
        project_state,
    )


def run_main_app(
    request_message: str,
    username: str,
    pass_word: str,
    game_mode: bool,
    price_filter: int,
    auto_request_send: str,
    messages_state: str,
    project_state: str,
):
    os.system("cls" if os.name == "nt" else "clear")
    selenium = Selenium()
    try:
        selenium.login(user=username, password=pass_word)
        previous_p = selenium.grab_first_project()
        previous_messages_len = 0
        price_filter = int(str(price_filter) + "000000")
        keep_going = True
        while keep_going:
            print("Grabbing First Project...")
            new_p = selenium.grab_first_project()
            print("Checking For New Messages...")
            new_messages_len = selenium.get_messages()
            if new_messages_len:
                new_messages_len = int(new_messages_len)
            else:
                new_messages_len = 0
            if new_messages_len > previous_messages_len:
                print("New Message Detected")
                keep_going = selenium.notify_user(
                    "new message detected", game_mode, messages_state
                )
                if not keep_going:
                    break
            else:
                print("No New Message Detected")
            previous_messages_len = new_messages_len
            send_request_automaticaly = False
            if new_p and previous_p:
                print("Comparing Project Urls...")
                is_same, new_projects = selenium.compare_projects(
                    previous_p, new_p, price_filter
                )
                if not is_same:
                    print(f"{len(new_projects)} New Projects Detected")
                    for project in new_projects:
                        print(
                            f"Project {new_projects.index(project) + 1} = {project['title']}"
                        )
                    keep_going, send_request_automaticaly, picked_project = (
                        selenium.notify_user(
                            "new project detected",
                            game_mode,
                            project_state,
                            auto_request_send=auto_request_send,
                        )
                    )
                    if send_request_automaticaly:
                        print("send request automatically is true")
                        _ = selenium.auto_send_request(request_message, picked_project)
                        if keep_going:
                            _ = selenium.wait.until(
                                ec.invisibility_of_element_located(
                                    (By.ID, "input-amount")
                                )
                            )
                            selenium.go_to_projects_page()
                    if not keep_going:
                        break

                else:
                    print("No New Projects")
                previous_p = new_p
            if not send_request_automaticaly:
                print("Refreshing...")
                selenium.driver.refresh()
            else:
                print("Request sent automatically")
            print("Waiting for 10 seconds")
            time.sleep(10)
            os.system("cls" if os.name == "nt" else "clear")
    except Exception as e:
        _ = selenium.notify_user("Error", game_mode, "just_notify")
        if e is not InvalidSessionIdException:
            raise e
        else:
            print("browser window has been closed")
            os._exit(0)


# TODO: Add AI generating request message
# TODO: Add some sort of remote functionallity (sms, android app, etc)
# TODO: Make it so the app remebers the first project from the last time it ran
if __name__ == "__main__":
    main_menu()
