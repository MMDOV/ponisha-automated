import winsound
import time
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
def login(path):
    global driver, wait
    option = Options()
    option.page_load_strategy = "none"
    option.binary_location = path
    driver = Firefox(options=option, service=service.Service(GeckoDriverManager().install()))
    wait = WebDriverWait(driver, 20)
    driver.get(r'https://ponisha.ir/dashboard/find-projects')
    return None


# TODO: grabs first project
def grab_first_project():
    wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'css-pxmsqw')))
    first_project = driver.find_element(By.CLASS_NAME, 'css-pxmsqw')
    return first_project


# TODO: check if two projects are the same or not
def compare_projects(previous_project, new_project):
    if previous_project != new_project:
        return False
    return True


# TODO: main operation(combining all the functions)
#       login
#       grab first project an save it in a variable
#       compare project to the previous one and act accordingly
#       set new project as previous project
#       refresh the page
def main():
    login(r"C:\Program Files\Firefox Developer Edition\firefox.exe")
    previous_p = grab_first_project()
    project_are_the_same = True
    while project_are_the_same:
        new_p = grab_first_project()
        project_are_the_same = compare_projects(previous_p, new_p)
        driver.refresh()
        previous_p = new_p
        time.sleep(10)
    winsound.PlaySound('*', winsound.SND_ASYNC)
    driver.maximize_window()


# temporary until ui is added
main()

# TODO: UI
if __name__ == "__main__":
    pass
