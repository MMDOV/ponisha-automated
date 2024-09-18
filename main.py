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

        _ = self.wait.until(ec.presence_of_element_located((By.ID, 'input-username')))
        time.sleep(20)
        self.driver.find_element(By.ID, 'input-username').send_keys(user)
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

def save_to_yaml(file_name: str, message: str, username: str, password: str):
    base_data = dict (
        message = message,
        user_name = username,
        password = password,
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
    return config_yaml, request_message, username, pass_word

# TODO: UI or make the terminal version look better at least maybe some ascii art ? idk
# TODO: save settings
# TODO: Add AI generating request message
# TODO: Add some sort of remote functionallity (sms, android app, etc)
# TODO: Add check for new messages
if __name__ == "__main__":
    run_app = str(input('Do you want the app to run right now ?(y/n): \n'))
    if run_app == "n":
        sys.exit()
    game_mode = str(input('Would you like to turn on game mode?(error sound only)(y/n): \n'))
    #what_type_of_url_needed = str(input('Do you want all of projects of only the python ones?(p for python): \n'))
    price_filter = str(input('Pick a price in millions (1 for 1,000,000 etc): \n'))
    user_picked_price = int(price_filter + '000000')
    input_username = str(input('Please enter your Email(leave empty for default): \n'))
    input_pass_word = str(input('Please enter your Password(leave empty for default): \n'))
    selenium = Selenium()
    try:
        try:
            config_yaml, request_message, username, pass_word = load_yaml_file("data.yml")
        except FileNotFoundError:
            save_to_yaml("data.yml", "", "", "")
            config_yaml, request_message, username, pass_word = load_yaml_file("data.yml")
        if input_username:
            username = input_username
            save_to_yaml("data.yml", request_message, username, pass_word)
        if input_pass_word:
            pass_word = input_pass_word
            save_to_yaml("data.yml", request_message, username, pass_word)
        selenium.login(user=username, password=pass_word)
        previous_p = selenium.grab_first_project()
        price_range = selenium.get_price_range()
        price_low = int(price_range[0])
        price_high = int(price_range[1])
        price = int(price_low + (price_high - price_low) // 2)
        keep_going = True
        while keep_going:
            new_p = selenium.grab_first_project()
            projects_are_same = compare_projects(previous_p, new_p)

            if not projects_are_same:
                if not game_mode == 'y':
                    selenium.driver.maximize_window()
                if CURRENT_OS == "Windows":
                    # HACK: idk why this is happening maaaaaybe try and fix it but honestly who cares
                    winsound.Beep(500, 1000)
                else:
                    _ = os.system('spd-say "new project detected"')
                # TODO: move this to the start maybe if remote is on or smt idk figure it out
                auto_request_send = input('Do you want me to automatically send requests to new projects? (y/n):\n')
                if auto_request_send == 'y':
                    _ = selenium.auto_send_request(request_message, new_p)
                keep_going_str = input("Would you like to keep going? (y/n): ")
                if keep_going_str == 'y' and auto_request_send == 'y':
                    selenium.driver.get(selenium.picked_url)
                    keep_going = True
                elif keep_going_str == 'y' and not auto_request_send == 'y':
                    keep_going = True
                else:
                    keep_going = False
                    break
            previous_p = new_p
            selenium.driver.refresh()
            time.sleep(10)
    except Exception as e:
        print(e)
        if not game_mode == 'y':
            selenium.driver.maximize_window()
        if CURRENT_OS == "Windows":
            winsound.Beep(500, 1000)
        else:
            _ = os.system('spd-say "Error"')
