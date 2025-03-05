from time import sleep
from typing import Any, List, Optional

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    ElementNotVisibleException,
    ElementNotSelectableException,
    InvalidSelectorException,
    NoSuchFrameException,
    WebDriverException,
    TimeoutException)

from infrastructure.Infra.dal.data_reposetory.data_rep import DataRep


def ignore_exception_types():
    return [
        NoSuchElementException,
        ElementNotInteractableException,
        ElementNotVisibleException,
        ElementNotSelectableException,
        InvalidSelectorException,
        NoSuchFrameException,
        WebDriverException
    ]

class SearchElement:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> Optional[WebElement]:
        try:
            element = driver.find_element(*self.by)
            if element is not None:
                if element.is_displayed() and element.is_enabled():
                    return element
            return None
        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except Exception as e:
            self.last_exception = e
            return None


class SwitchToIframe:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> bool:
        try:
            element = DriverEX.search_element(driver, self.by)

            if element is None:
                return False

            driver.switch_to.frame(element)
            sleep(0.3)
            return True
        except StaleElementReferenceException:
            sleep(0.3)
            return False
        except Exception as e:
            self.last_exception = e
            return False


class SwitchToContent:
    def __init__(self):
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> bool:
        try:
            driver.switch_to.default_content()
            return True
        except Exception as e:
            self.last_exception = e
            return False


class SearchElements:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> Optional[list[WebElement]]:
        try:
            return driver.find_elements(*self.by)
        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except Exception as e:
            self.last_exception = e
            return None


class SelectElementFromDropDownByValue:
    def __init__(self, by: tuple, list_item_value: str):
        self.by = by
        self.list_item_value = list_item_value
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> Any:
        try:
            element = driver.find_element(*self.by)
            Select(element).select_by_value(self.list_item_value)
            return element
        except ElementClickInterceptedException:
            ScrollToElement(self.by)(driver)
            return None
        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except Exception as e:
            self.last_exception = e
            return None


class NavigateToUrl:
    def __init__(self, url: str):
        self.url = url
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> None:
        try:
            driver.get(self.url)
        except StaleElementReferenceException:
            sleep(0.3)
        except Exception as e:
            self.last_exception = e


class ScrollToElement:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> Any:
        try:
            element = driver.find_element(*self.by)
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            sleep(0.5)
            return element
        except Exception as e:
            self.last_exception = e
            return None


class ForceClick:
    def __init__(self, by: tuple, element: WebElement = None):
        self.by = by
        self.element = element
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> Optional[WebElement]:
        try:
            # Use the provided element if available, otherwise find it using the locator
            if self.element is not None:
                element = self.element
            else:
                element = driver.find_element(*self.by)

            if element.is_enabled():
                element.click()
            return element
        except StaleElementReferenceException:
            sleep(0.3)
            return None
        except ElementClickInterceptedException:
            ScrollToElement(self.by)(driver)
            return None
        except Exception as e:
            self.last_exception = e
            return None


class GetElementText:
    def __init__(self, by: tuple):
        self.by = by
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> str:
        try:
            element = driver.find_element(*self.by)
            vv = existing_text = element.text
            text = element.get_attribute("innerText") or element.get_attribute("value") or ""
            return text.strip()
        except StaleElementReferenceException:
            sleep(0.3)
            return ""
        except Exception as e:
            self.last_exception = e
            return ""


class SendKeysAuto:
    def __init__(self, by: tuple, input_text: str):
        self.by = by
        self.input_text = input_text
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> bool:
        try:
            element = DriverEX.search_element(driver, self.by)
            existing_text = element.get_attribute("value") or element.text

            if self.input_text != existing_text:
                element.clear()
                element.send_keys(self.input_text)
                return False
            return True
        except StaleElementReferenceException:
            sleep(0.3)
            return False
        except Exception as e:
            self.last_exception = e
            return False


class UploadFile:
    def __init__(self, by: tuple, input_text: str):
        self.by = by
        self.input_text = input_text
        self.last_exception = None

    def __call__(self, driver: WebDriver) -> bool:
        try:
            element = driver.find_element(*self.by)
            element.send_keys(self.input_text)
            sleep(0.015)
            return True
        except StaleElementReferenceException:
            sleep(0.3)
            return False
        except Exception as e:
            self.last_exception = e
            return False


class DriverEX:
    @staticmethod
    def switch_to_iframe(driver: WebDriver, by: tuple) -> bool:
        iframe = SwitchToIframe(by)
        try:
            return WebDriverWait(driver, DataRep.time_to_wait_from_seconds,
                                 ignored_exceptions=ignore_exception_types())\
                .until(iframe)

        except TimeoutException:
            if iframe.last_exception:
                raise iframe.last_exception
            raise

    @staticmethod
    def switch_to_default_content(driver: WebDriver) -> None:
        switch = SwitchToContent()
        try:
            WebDriverWait(driver,
                                 DataRep.time_to_wait_from_seconds,
                                 ignored_exceptions=ignore_exception_types())\
                .until(switch)

        except TimeoutException:
            if switch.last_exception:
                raise switch.last_exception
            raise

    @staticmethod
    def search_element(driver: WebDriver, by: tuple) -> WebElement:
        search = SearchElement(by)
        try:
            return WebDriverWait(driver, DataRep.time_to_wait_from_seconds,
                                 ignored_exceptions=ignore_exception_types())\
                .until(search)

        except TimeoutException:
            if search.last_exception:
                raise search.last_exception
            raise

    @staticmethod
    def upload_file(driver: WebDriver, by: tuple, input_text: str) -> None:
        upload_file = UploadFile(by, input_text)
        try:
            WebDriverWait(driver,
                          DataRep.time_to_wait_from_seconds,
                          ignored_exceptions=ignore_exception_types())\
                .until(upload_file)

        except TimeoutException:
            if upload_file.last_exception:
                raise upload_file.last_exception
            raise

    @staticmethod
    def send_keys_auto(driver: WebDriver, by: tuple, input_text: str) -> None:
        send_keys = SendKeysAuto(by, input_text)
        try:
            WebDriverWait(driver,
                          DataRep.time_to_wait_from_seconds,
                          ignored_exceptions=ignore_exception_types())\
                .until(send_keys)

        except TimeoutException:
            if send_keys.last_exception:
                raise send_keys.last_exception
            raise

    @staticmethod
    def navigate_to_url(driver: WebDriver, url: str) -> None:
        nav = NavigateToUrl(url)
        try:
            WebDriverWait(driver, 30, ignored_exceptions=ignore_exception_types()).until(nav)
        except TimeoutException:
            if nav.last_exception:
                raise nav.last_exception
            raise

    @staticmethod
    def search_elements(driver: WebDriver, by: tuple) -> List[WebElement]:
        search = SearchElements(by)
        try:
            return WebDriverWait(driver,
                                 DataRep.time_to_wait_from_seconds,
                                 ignored_exceptions=ignore_exception_types())\
                .until(search)

        except TimeoutException:
            if search.last_exception:
                raise search.last_exception
            raise

    @staticmethod
    def force_click(driver: WebDriver, by: tuple, element: WebElement = None) -> bool:
        click = ForceClick(by, element)
        try:
            element = WebDriverWait(driver,
                                    DataRep.time_to_wait_from_seconds,
                                    ignored_exceptions=ignore_exception_types())\
                .until(click)

            return element is not None
        except TimeoutException:
            if click.last_exception:
                raise click.last_exception
            raise

    @staticmethod
    def select_element_from_dropdown_by_value(driver: WebDriver, by: tuple, list_item_value: str) -> None:
        select = SelectElementFromDropDownByValue(by, list_item_value)
        try:
            WebDriverWait(driver,
                          DataRep.time_to_wait_from_seconds,
                          ignored_exceptions=ignore_exception_types())\
                .until(select)

        except TimeoutException:
            if select.last_exception:
                raise select.last_exception
            raise

    @staticmethod
    def get_element_text(driver: WebDriver, by: tuple) -> str:
        get_text = GetElementText(by)
        try:
            return WebDriverWait(driver,
                                 DataRep.time_to_wait_from_seconds,
                                 ignored_exceptions=ignore_exception_types())\
                .until(get_text)

        except TimeoutException:
            if get_text.last_exception:
                raise get_text.last_exception
            raise

