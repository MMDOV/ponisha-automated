import os
import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import platform
import yaml
CURRENT_OS = platform.system()
if CURRENT_OS == "Windows":
    import winsound

class Selenium:
    def __init__(self):
        self.picked_url = ''
        self.option = Options()
        self.option.page_load_strategy = 'none'
        self.driver = Firefox(options=self.option)
        self.wait = WebDriverWait(self.driver, 60)

    def get_ready_state(self) -> bool:
        ready_state = self.driver.execute_script("return document.readyState")
        return ready_state == "complete"

    def login(self, user: str, password:str) -> None:
        print("usr =", user)
        print("psw =", password)
        self.driver.get(r'https://ponisha.ir/users/login')

        # Wait until the page's readyState is 'complete'
        self.wait.until(ec.presence_of_element_located((By.ID, 'input-username')))
        self.wait.until(lambda _: self.get_ready_state())
        input_username = self.driver.find_element(By.ID, 'input-username')
        input_username.send_keys(user)
        _ = self.wait.until(ec.element_to_be_clickable((By.TAG_NAME, 'button')))
        if input_username.get_attribute("value"):
            login_button = self.driver.find_element(By.TAG_NAME, 'button')
            login_button.click()

        # # logging in via phone number requires this step
        # self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-198qifb')))
        # button = self.driver.find_element(By.CLASS_NAME, 'css-198qifb')
        # button.click()

        _ = self.wait.until(ec.presence_of_element_located((By.ID, 'input-password')))
        password_input = self.driver.find_element(By.ID, 'input-password')
        password_input.send_keys(password)
        _ = self.wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'css-egod06')))
        self.driver.find_element(By.CLASS_NAME, 'css-egod06').click()

        _ = self.wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'css-11hbav8')))
        self.wait.until(lambda _: self.get_ready_state())
        search_button = self.driver.find_element(By.CLASS_NAME, 'css-11hbav8')
        search_button.click()
        # TODO: add skill picking

        #python_url = (r'https://ponisha.ir/dashboard/find-projects?skills[0]'
        #              r'[id]=102&skills[0][title]=%D9%BE%D8%A7%DB%8C%D8%AA%D9%88%D9%86%20(Python)')
        #all_url = r'https://ponisha.ir/dashboard/find-projects?filterSkillsByUserId=1071865'
        #if self.project_type == 'p':
        #    self.picked_url = python_url
        #else:
        #    self.picked_url = all_url
        #self.driver.get(self.picked_url)

    # grabs first project
    def grab_first_project(self) -> str | None:
        tries = 4
        first_project_url = ""
        while tries > 0:
            try:
                _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-pxmsqw')))
                self.wait.until(lambda _: self.get_ready_state())
                main_wrapper = self.driver.find_element(By.CLASS_NAME, 'main')
                projects = main_wrapper.find_element(By.CLASS_NAME, 'css-79elbk')
                first_project = projects.find_element(By.CLASS_NAME, 'css-pxmsqw')
                first_project_url = first_project.find_element(By.TAG_NAME, 'a').get_attribute('href')
                break
            except (TimeoutException, NoSuchElementException):
                tries = tries - 1
                print("there was a problem refreshing page...")
                self.driver.refresh()
                continue
        if tries <= 0:
            raise TimeoutException
        return first_project_url

    def get_price_range(self) -> list:
        self.wait.until(lambda _: self.get_ready_state())
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-pxmsqw')))
        main_wrapper = self.driver.find_element(By.CLASS_NAME, 'main')
        projects = main_wrapper.find_element(By.CLASS_NAME, 'css-79elbk')
        first_project = projects.find_element(By.CLASS_NAME, 'css-pxmsqw')
        self.wait.until(lambda _: self.get_ready_state())
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-1sp2kcx')))
        info_section = first_project.find_elements(By.CLASS_NAME, 'css-1sp2kcx')
        budget_section = info_section[2]
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-l23rzi')))
        price_range = budget_section.find_element(By.CLASS_NAME, 'css-l23rzi')
        price_range = price_range.text
        price_range_list = price_range.split('تا')
        price_range_list = [price.replace(',', '').strip('از').strip() for price in price_range_list]
        return price_range_list

    def get_messages(self) -> str:
        tries = 4
        chat_number = ""
        while tries > 0:
            try:
                self.wait.until(lambda _: self.get_ready_state())
                _ = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Chats"]')))
                chat_wrapper = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Chats"]')
                chat_number = chat_wrapper.find_element(By.TAG_NAME, 'span').find_element(By.TAG_NAME, 'span').text
                break
            except (TimeoutException, NoSuchElementException):
                tries = tries - 1
                print("there was a problem refreshing page...")
                self.driver.refresh()
                continue
        if tries <= 0:
            raise TimeoutException
        return chat_number
    
    def auto_send_request(self, message: str, project) -> None:
        message = message.strip()
        self.wait.until(lambda _: self.get_ready_state())
        price_range = self.get_price_range()

        price = int((int(price_range[0]) + int(price_range[1])) / 2)

        self.driver.get(project)
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div[class="css-dbb1rg"]')))
        button_wrapper = self.driver.find_element(By.CSS_SELECTOR, 'div[class="css-dbb1rg"]')
        self.wait.until(lambda _: self.get_ready_state())
        button_wrapper.find_element(By.TAG_NAME, "button").click()
        self.wait.until(ec.element_to_be_clickable((By.ID, 'input-amount')))
        self.driver.find_element(By.ID, 'input-amount').send_keys(str(price))
        self.driver.find_element(By.ID, 'input-days').send_keys('7')
        self.driver.find_element(By.ID, 'input-payments.0.title').send_keys('انجام پروژه')
        self.driver.find_element(By.ID, 'input-payments.0.amount').send_keys(str(price))
        self.driver.find_element(By.ID, 'input-description').send_keys(message)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

    def notify_user(self, message:str, game_mode: bool, state: str) -> bool:
        keep_going = True
        if state == "just_notify":
            if CURRENT_OS == "Windows":
                # HACK: idk why this is happening maaaaaybe try and fix it but honestly who cares
                winsound.Beep(500, 1000)
            else:
                _ = os.system(f'spd-say "{message}"')
        elif state == "notify_and_stop":
            if not game_mode:
                self.driver.maximize_window()
            if CURRENT_OS == "Windows":
                winsound.Beep(500, 1000)
            else:
                _ = os.system(f'spd-say "{message}"')
            keep_going_str = menu_generator("Would you like to keep going?", ["YES", "NO"], False)
            if keep_going_str == '1':
                keep_going = True
            else:
                keep_going = False
        return keep_going

# check if two projects are the same or not
def compare_projects(previous_project_url: str, new_project_url: str) -> bool:
    print("previous_project_url: ", previous_project_url)
    print("new_project_url: ", new_project_url)
    if previous_project_url != new_project_url:
        return False
    return True

def save_to_yaml(
    file_name: str,
    message: str,
    username: str,
    password: str,
    game_mode: bool,
    price_filter:int,
    auto_request_send: str,
    message_state: str,
    project_state: str ) -> None:
    base_data = dict (
        message = message,
        user_name = username,
        password = password,
        game_mode = game_mode,
        price_filter = price_filter,
        auto_send_req = auto_request_send,
        message_state = message_state,
        project_state = project_state,
    )
    pathname = os.path.dirname(sys.argv[0])        
    with open(pathname + "/" + file_name, "w", encoding='utf8') as f:
        yaml.dump(base_data, f, default_flow_style=False)

def load_yaml_file(file_name: str) -> tuple:
    pathname = os.path.dirname(sys.argv[0])        
    with open(pathname + "/" + file_name, 'r', encoding='utf8') as f:
        config_yaml = yaml.safe_load(f)
        request_message = config_yaml.get("message")
        username = config_yaml.get("user_name")
        pass_word = config_yaml.get("password")
        game_mode = config_yaml.get("game_mode")
        price_filter = config_yaml.get("price_filter")
        auto_send_req = config_yaml.get("auto_send_req")
        messages_state = config_yaml.get("message_state")
        project_state = config_yaml.get("project_state")
    return config_yaml, request_message, username, pass_word, game_mode, price_filter, auto_send_req, messages_state, project_state

        


def menu_generator(header:str, content_list:list[str], is_main_menu: bool, pre_messages: list = []) -> str:
    os.system('cls' if os.name=='nt' else 'clear')
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
    run_app = menu_generator('Select one:', main_menu, True, pre_messages)
    if run_app == "1":
        try:
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml("data.yml", "", "", "", False, 0, "dont_send_requests_automatically" , "notify_only", "notify_and_stop")
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
        run_main_app(request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
    elif run_app == "2":
        request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = simple_settings_menu()
    else:
        sys.exit()
    return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state

def simple_settings_menu() -> tuple:
    try:
        _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
    except FileNotFoundError:
        save_to_yaml("data.yml", "", "", "", False, 0, "dont_send_requests_automatically", "notify_only", "notify_and_stop")
        _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
    simple_settings_menu_list = ["Automatic Mode", "Manual Mode", "Advanced Settings"]
    user_picked_setting = menu_generator("Pick a preset or change what you want in advanced settings:", simple_settings_menu_list, False, [])
    if user_picked_setting == "1":
        auto_mode_head = "Automatic mode is for when you are not actively looking at the bot and want it to just send requests to all the available projects\n\
                          This mode still uses your filters just does not notify you or ask for you permission for anything"
        user_pick = menu_generator(auto_mode_head, ["Use Auto Mode"], False, [])
        if user_pick == "1":
            game_mode = False
            auto_request_send = "auto_send_without_asking"
            messages_state = "ignore"
            project_state = "ignore"
            changes_list = ['Automatic Mode is ON',
                            'Game Mode was chnaged to "OFF"',
                            'Auto Send was changed to "Auto Send Without Asking"',
                            'Project Notification was changed to "Ignore"',
                            'Messages Notification was changed to "Ignore"']
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu(changes_list)
        else:
            request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = simple_settings_menu()
    elif user_picked_setting == "2":
        manual_mode_head = "Manual mode is for when you ARE actively looking at the bot and want it to ask you for permission and notify you for almost everything\n\
                            You can still just have the bot in the background and the bot notifies you when there is a new project but you need to give permission everytime"
        user_pick = menu_generator(manual_mode_head, ["Use Manual Mode"], False, [])
        if user_pick == "1":
            auto_request_send = "dont_send_requests_automatically"
            messages_state = "notify_only"
            project_state = "notify_and_stop"
            changes_list = ['Manual Mode is ON',
                            'Auto Send was changed to "Dont Send Requests Automatically"',
                            'Project Notification was changed to "Notify And Stop"',
                            'Messages Notification was changed to "Notify Only"']
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu(changes_list)
        else:
            request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = simple_settings_menu()
    elif user_picked_setting == "3":
        request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
    else:
        main_menu()
    return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state

# TODO: add a mode where it auto sends requests without needing confirmation for when there is no one checking on the bot
def advanced_settings_menu() -> tuple:
        try:
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml("data.yml", "", "", "", False, 0, "dont_send_requests_automatically", "notify_only", "notify_and_stop")
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = load_yaml_file("data.yml")
        if game_mode:
            game_mode_setting = "ON"
        else:
            game_mode_setting = "OFF"
        if price_filter:
            price_filter_setting = str(price_filter) + '000000'
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
        user_picked_setting = menu_generator("Pick a setting to change:", settings_menu_list, False, [])
        if user_picked_setting == "1":
            input_username = menu_generator('Please enter your Email:', [], False)
            if input_username == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            prev_username = username
            username = input_username
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Username was changed from "{prev_username}" to "{input_username}"'])
        elif user_picked_setting == "2":
            input_pass_word = menu_generator('Please enter your Password:', [], False)
            if input_pass_word == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            prev_password = pass_word
            pass_word = input_pass_word
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Password was changed from "{prev_password}" to "{input_pass_word}"'])
        elif user_picked_setting == "3":
            input_game_mode = menu_generator('Would you like to turn on game mode?(error sound only):', ["ON", "OFF"], False)
            game_mode_setting_prev = game_mode_setting
            if input_game_mode == "1":
                game_mode = True
                game_mode_setting = "ON"
            elif input_game_mode == "2":
                game_mode = False
                game_mode_setting = "OFF"
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Game Mode was changed from "{game_mode_setting_prev}" to "{game_mode_setting}"'])
        elif user_picked_setting == "4":
            input_price_filter = menu_generator('Pick a price in millions (1 for 1,000,000 etc) for 0 enter "00":', [], False)
            if input_price_filter == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            try:
                prev_price_filter = price_filter
                price_filter = int(input_price_filter)
            except ValueError:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Price Filter was changed from "{prev_price_filter}" to "{price_filter}"'])
        elif user_picked_setting == "5":
            input_auto_request = menu_generator('Would you like the bot to automatically send requests to projects or just norify you ?', ["Auto Send Without Asking", "Ask For Permission Everytime", "Dont Send Requests Automatically"], False)
            auto_request_setting_prev = auto_request_setting
            if input_auto_request == "1":
                auto_request_send = "auto_send_without_asking"
            elif input_auto_request == "2":
                auto_request_send = "ask_for_permission_everytime"
            elif input_auto_request == "3":
                auto_request_send = "dont_send_requests_automatically"
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            auto_request_setting = auto_request_send.replace("_", " ").title()
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Auto send was changed from "{auto_request_setting_prev}" to "{auto_request_setting}"'])
        elif user_picked_setting == "6":
            input_request_message = menu_generator('Enter your request message(note that it is recommended to edit the message directly in data.yml):', [], False)
            if input_request_message == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            request_message = input_request_message
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu(["request message has been changed"])
        elif user_picked_setting == "7":
            input_message_state = menu_generator('What do you want the bot to do when you get a new message?:', ["Just Notify", "Notify And Stop", "Ignore"], False)
            messages_state_setting_prev = messages_state_setting
            if input_message_state == "1":
                messages_state = "just_notify"
            elif input_message_state == "2":
                messages_state = "notify_and_stop"
            elif input_message_state == "3":
                messages_state = "ignore"
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            messages_state_setting = messages_state.replace("_", " ").title()
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Messages Notification was changed from "{messages_state_setting_prev}" to "{messages_state_setting}"'])
        elif user_picked_setting == "8":
            input_project_state = menu_generator('What do you want the bot to do when there is a new project?:', ["Just Notify", "Notify And Stop", "Ignore"], False)
            project_state_setting_prev = project_state_setting
            if input_project_state == "1":
                project_state = "just_notify"
            elif input_project_state == "2":
                project_state = "notify_and_stop"
            elif input_project_state == "3":
                project_state = "ignore"
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state = advanced_settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state
            project_state_setting = project_state.replace("_", " ").title()
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state)
            main_menu([f'Project Notification was changed from "{project_state_setting_prev}" to "{project_state_setting}"'])
        else:
            simple_settings_menu()
        return request_message, username, pass_word, game_mode, price_filter, auto_request_send, messages_state, project_state

def run_main_app(request_message: str,
                 username: str,
                 pass_word: str,
                 game_mode: bool,
                 price_filter: int,
                 auto_request_send: bool,
                 messages_state: str,
                 project_state: str):
    os.system('cls' if os.name=='nt' else 'clear')
    selenium = Selenium()
    try:
        selenium.login(user=username, password=pass_word)
        previous_p = selenium.grab_first_project()
        previous_messages_len = int(selenium.get_messages())
        price_filter = int(str(price_filter) + "000000")
        keep_going = True
        while keep_going:
            new_p = selenium.grab_first_project()
            new_messages_len = int(selenium.get_messages())
            price_range = selenium.get_price_range()
            price_low = int(price_range[0])
            if new_messages_len > previous_messages_len:
                keep_going = selenium.notify_user("new message detected", game_mode, messages_state)
                if not keep_going:
                    break
            previous_messages_len = new_messages_len
            if new_p and previous_p:
                projects_are_same = compare_projects(previous_p, new_p)

                if not projects_are_same and price_filter <= price_low:
                    keep_going = selenium.notify_user("new project detected", game_mode, project_state)
                    if auto_request_send == "auto_send_without_asking":
                        _ = selenium.auto_send_request(request_message, new_p)
                    elif auto_request_send == "ask_for_permission_everytime":
                        user_answer = menu_generator("Would you like the bot to send a request automatically to this project ?", ["YES", "NO"], False)
                        if user_answer == "1":
                            _ = selenium.auto_send_request(request_message, new_p)
                    if not keep_going:
                        break
                previous_p = new_p
                selenium.driver.refresh()
                time.sleep(10)
    except Exception as e:
        _ = selenium.notify_user("Error", game_mode, "ignore")
        raise e
# TODO: Add AI generating request message
# TODO: Add some sort of remote functionallity (sms, android app, etc)
if __name__ == "__main__":
    main_menu()
