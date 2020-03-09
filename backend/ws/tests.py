from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from app.models import User
from app.tests import create_config, create_temp_data, create_runnings

TIMEOUT = 2


class WSTests(ChannelsLiveServerTestCase):
    serve_static = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        try:
            cls.driver = webdriver.Chrome()
        except WebDriverException:
            return
        except:  # noqa
            super().tearDownClass()
            raise

        cls.user = {'username': 'test', 'password': '123', 'is_staff': True}
        User.objects.create_user(**cls.user)
        create_config()
        create_temp_data()
        create_runnings()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()

    def test_when_post_edited_then_seen_by_everyone(self):
        if not hasattr(self, 'driver'):
            self.skipTest(f'{self.__class__.__name__} doesn\'t have driver')

        try:
            self._enter_index_page(self.user)

            self._open_new_window()
            self._enter_index_page()

            self._switch_to_window(0)
            new_post = {'distance': '123'}
            self._edit_post(new_post)
            WebDriverWait(self.driver, TIMEOUT).until(lambda _:
                                                      new_post['distance'] in self._post_distance_value,
                                                      'Message was not received by window 1 from window 1')

            self._switch_to_window(1)
            WebDriverWait(self.driver, TIMEOUT).until(lambda _:
                                                      new_post['distance'] in self._post_distance_value,
                                                      'Message was not received by window 2 from window 1')
        finally:
            self._close_all_new_windows()

    # === Utility ===

    def _enter_index_page(self, user=None):
        self.driver.get(self.live_server_url + '/')

        if user:
            self._find_by_css('.v-navigation-drawer__content button').click()
            self.driver.find_element_by_name('username').send_keys(user['username'])
            self.driver.find_element_by_name('password').send_keys(user['password'], Keys.RETURN)

        WebDriverWait(self.driver, TIMEOUT).until(lambda _: '/' in self.driver.current_url)

    def _open_new_window(self):
        self.driver.execute_script('window.open("about:blank", "_blank")')
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _close_all_new_windows(self):
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.execute_script('window.close()')
        if len(self.driver.window_handles) == 1:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _switch_to_window(self, window_index):
        self.driver.switch_to.window(self.driver.window_handles[window_index])

    def _edit_post(self, post: dict):
        self._find_by_css('.v-card__title > button').click()
        number_input = self._find_by_css('.v-dialog .v-card__text .v-input:nth-child(3) input')
        number_input.send_keys(Keys.CONTROL + 'a', Keys.DELETE)
        number_input.send_keys(post['distance'])
        self._find_by_css('.v-dialog .v-card__actions button.primary').click()

    @property
    def _post_distance_value(self):
        return self._find_by_css('.v-card__text > .blue--text').text

    def _find_by_css(self, selector):
        return self.driver.find_element_by_css_selector(selector)
