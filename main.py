import winsound
from selenium.webdriver import Firefox
from selenium.webdriver.firefox import service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoSuchWindowException, \
    ElementNotInteractableException, ElementClickInterceptedException
from webdriver_manager.firefox import GeckoDriverManager


# TODO: login and go to project list
def login():
    option = Options()
    option.page_load_strategy = "none"
    driver = Firefox(options=option, service=service.Service(GeckoDriverManager().install()))
    return None


# TODO: grabs first project
def grab_first_project():
    first_project = None
    return first_project


# TODO: check if two projects are the same or not
def compare_projects(previous_project, new_project):
    return True or False


# TODO: main operation(combining all the functions)
#       login
#       grab first project an save it in a variable
#       compare project to the previous one and act accordingly
#       set new project as previous project
#       refresh the page


# TODO: UI
if __name__ == "__main__":
    pass
