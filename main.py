import os
import sys
import time
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, user: str, password:str):
        print("usr =", user)
        print("psw =", password)
        self.driver.get(r'https://ponisha.ir/users/login')

        def get_ready_state() -> bool:
            ready_state = self.driver.execute_script("return document.readyState")
            return ready_state == "complete"
    
        # Wait until the page's readyState is 'complete'
        self.wait.until(ec.presence_of_element_located((By.ID, 'input-username')))
        self.wait.until(lambda _: get_ready_state())
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
    def grab_first_project(self) -> str:
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-pxmsqw')))
        time.sleep(5)
        main_wrapper = self.driver.find_element(By.CLASS_NAME, 'main')
        projects = main_wrapper.find_element(By.CLASS_NAME, 'css-79elbk')
        first_project = projects.find_element(By.CLASS_NAME, 'css-pxmsqw')
        first_project_url = first_project.find_element(By.TAG_NAME, 'a').get_attribute('href')
        if not first_project_url:
            raise NoSuchElementException
        return first_project_url

    def get_price_range(self):
        time.sleep(5)
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-pxmsqw')))
        main_wrapper = self.driver.find_element(By.CLASS_NAME, 'main')
        projects = main_wrapper.find_element(By.CLASS_NAME, 'css-79elbk')
        first_project = projects.find_element(By.CLASS_NAME, 'css-pxmsqw')
        time.sleep(5)
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-1sp2kcx')))
        info_section = first_project.find_elements(By.CLASS_NAME, 'css-1sp2kcx')
        budget_section = info_section[2]
        _ = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-l23rzi')))
        price_range = budget_section.find_element(By.CLASS_NAME, 'css-l23rzi')
        price_range = price_range.text
        price_range_list = price_range.split('تا')
        price_range_list = [price.replace(',', '').strip('از').strip() for price in price_range_list]
        return price_range_list
    
    # FIX: Add pressing the send button but test it fully first. how ? idk figure it out
    def auto_send_request(self, message: str, project) -> None:
        message = message.strip()
        time.sleep(5)
        price_range = self.get_price_range()

        price = int((int(price_range[0]) + int(price_range[1])) / 2)

        self.driver.get(project)
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div[class="css-dbb1rg"]')))
        button_wrapper = self.driver.find_element(By.CSS_SELECTOR, 'div[class="css-dbb1rg"]')
        time.sleep(5)
        button_wrapper.find_element(By.TAG_NAME, "button").click()
        self.wait.until(ec.element_to_be_clickable((By.ID, 'input-amount')))
        self.driver.find_element(By.ID, 'input-amount').send_keys(str(price))
        self.driver.find_element(By.ID, 'input-days').send_keys('7')
        self.driver.find_element(By.ID, 'input-payments.0.title').send_keys('انجام پروژه')
        self.driver.find_element(By.ID, 'input-payments.0.amount').send_keys(str(price))
        self.driver.find_element(By.ID, 'input-description').send_keys(message)

# check if two projects are the same or not
def compare_projects(previous_project_url: str, new_project_url: str) -> bool:
    print("previous_project_url: ", previous_project_url)
    print("new_project_url: ", new_project_url)
    if previous_project_url != new_project_url:
        return False
    return True

def save_to_yaml(file_name: str, message: str, username: str, password: str, game_mode: bool, price_filter:int, auto_request_send: bool ) -> None:
    base_data = dict (
        message = message,
        user_name = username,
        password = password,
        game_mode = game_mode,
        price_filter = price_filter,
        auto_send_req = auto_request_send,
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
    return config_yaml, request_message, username, pass_word, game_mode, price_filter, auto_send_req

def menu_generator(header:str, content_list:list[str], is_main_menu: bool) -> str:
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
    print()
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
        print("0 - Back")
    user_answer = str(input("----------------------------------------\n"))
    return user_answer

def main_menu() -> tuple:
    main_menu = ["Start", "Settings"]
    run_app = menu_generator('Select one:', main_menu, True)
    if run_app == "1":
        try:
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml("data.yml", "", "", "", False, 0, False)
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send = load_yaml_file("data.yml")
        run_main_app(request_message, username, pass_word, game_mode, price_filter, auto_request_send)
    elif run_app == "2":
        request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
    else:
        sys.exit()
    return request_message, username, pass_word, game_mode, price_filter, auto_request_send

def settings_menu() -> tuple:
        try:
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml("data.yml", "", "", "", False, 0, False)
            _, request_message, username, pass_word, game_mode, price_filter, auto_request_send = load_yaml_file("data.yml")
        if game_mode:
            game_mode_setting = "ON"
        else:
            game_mode_setting = "OFF"
        if price_filter:
            price_filter_setting = str(price_filter) + '000000'
        else:
            price_filter_setting = price_filter
        if auto_request_send:
            auto_request_setting = "ON"
        else:
            auto_request_setting = "OFF"
        if request_message:
            message_setting = "SET"
        else:
            message_setting = "EMPTY"
        settings_menu_list = [
            f"Username       |      {username}",
            f"Password       |      {pass_word}",
            f"Game Mode      |      {game_mode_setting}",
            f"Price Filter   |      {price_filter_setting}",
            f"Auto Send Req  |      {auto_request_setting}",
            f"Message        |      {message_setting}",
        ]
        user_picked_setting = menu_generator("Pick a setting to change:", settings_menu_list, False)
        if user_picked_setting == "1":
            input_username = menu_generator('Please enter your Email:', [], False)
            if input_username == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            username = input_username
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        elif user_picked_setting == "2":
            input_pass_word = menu_generator('Please enter your Password:', [], False)
            if input_pass_word == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            pass_word = input_pass_word
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        elif user_picked_setting == "3":
            input_game_mode = menu_generator('Would you like to turn on game mode?(error sound only):', ["ON", "OFF"], False)
            input_game_mode = input_game_mode.lower()
            if input_game_mode == "1":
                game_mode = True
            elif input_game_mode == "2":
                game_mode = False
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        elif user_picked_setting == "4":
            input_price_filter = menu_generator('Pick a price in millions (1 for 1,000,000 etc):', [], False)
            if input_price_filter == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            try:
                price_filter = int(input_price_filter)
            except ValueError:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        elif user_picked_setting == "5":
            input_auto_request = menu_generator('Would you like the bot to automatically send requests to projects or just norify you ?', ["Auto send", "Just Notify"], False)
            if input_auto_request == "1":
                auto_request_send = True
            elif input_auto_request == "2":
                auto_request_send = False
            else:
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        elif user_picked_setting == "6":
            input_request_message = menu_generator('Enter your request message(note that it is recommended to edit the message directly in data.yml):', [], False)
            if input_request_message == "0":
                request_message, username, pass_word, game_mode, price_filter, auto_request_send = settings_menu()
                return request_message, username, pass_word, game_mode, price_filter, auto_request_send
            request_message = input_request_message
            save_to_yaml("data.yml", request_message, username, pass_word, game_mode, price_filter, auto_request_send)
            main_menu()
        else:
            main_menu()
        return request_message, username, pass_word, game_mode, price_filter, auto_request_send

def run_main_app(request_message, username, pass_word, game_mode, price_filter, auto_request_send):
    os.system('cls' if os.name=='nt' else 'clear')
    selenium = Selenium()
    try:
        selenium.login(user=username, password=pass_word)
        previous_p = selenium.grab_first_project()
        price_range = selenium.get_price_range()
        price_low = int(price_range[0])
        price_filter = int(str(price_filter) + "000000")
        print("price filter = ", price_filter)
        if game_mode:
            print("Game mode = ON")
        else:
            print("Game mode = OFF")
        if auto_request_send:
            print("Auto send request = ON")
        else:
            print("Auto send request = OFF")
        keep_going = True
        while keep_going:
            new_p = selenium.grab_first_project()
            projects_are_same = compare_projects(previous_p, new_p)

            if not projects_are_same and price_filter <= price_low:
                if not game_mode:
                    selenium.driver.maximize_window()
                if CURRENT_OS == "Windows":
                    # HACK: idk why this is happening maaaaaybe try and fix it but honestly who cares
                    winsound.Beep(500, 1000)
                else:
                    _ = os.system('spd-say "new project detected"')
                # TODO: move this to the start maybe if remote is on or smt idk figure it out
                if auto_request_send:
                    _ = selenium.auto_send_request(request_message, new_p)
                keep_going_str = input("Would you like to keep going? (y/n): ")
                if keep_going_str == 'y' and auto_request_send:
                    selenium.driver.get(selenium.picked_url)
                    keep_going = True
                elif keep_going_str == 'y' and not auto_request_send:
                    keep_going = True
                else:
                    keep_going = False
                    break
            previous_p = new_p
            selenium.driver.refresh()
            time.sleep(10)
    except Exception as e:
        print(e)
        if not game_mode:
            selenium.driver.maximize_window()
        if CURRENT_OS == "Windows":
            winsound.Beep(500, 1000)
        else:
            _ = os.system('spd-say "Error"')
# TODO: Add AI generating request message
# TODO: Add some sort of remote functionallity (sms, android app, etc)
# TODO: Add check for new messages
if __name__ == "__main__":
    main_menu()
