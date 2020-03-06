from channels.testing import ChannelsLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from app.tests import create_config, create_temp_data, create_runnings

TIMEOUT = 2


class WSTests(ChannelsLiveServerTestCase):
    serve_static = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username='phpusr', password='pass123', is_staff=True)
        create_config()
        create_temp_data()
        create_runnings()

        try:
            cls.driver = webdriver.Chrome()
        except:  # noqa
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_when_post_edited_then_seen_by_everyone(self):
        try:
            self._enter_index_page()

            self._open_new_window()
            self._enter_index_page()

            self._switch_to_window(0)
            self._edit_post()

            self._switch_to_window(1)
            WebDriverWait(self.driver, TIMEOUT).until(lambda _:
                                                      '123' in self._post_distance_value,
                                                      'Message was not received by window 2 from window 1')
        finally:
            self._close_all_new_windows()

    # === Utility ===

    def _enter_index_page(self):
        self.driver.get(self.live_server_url + '/')
        WebDriverWait(self.driver, TIMEOUT).until(lambda _:
                                                  '/' in self.driver.current_url)

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

    def _edit_post(self):
        ActionChains(self.driver).send_keys('test').perform()

    @property
    def _post_distance_value(self):
        selector = self.driver.find_element_by_css_selector('.v-card__text > div')
        print('text', selector.text)
        return self.driver.find_element_by_css_selector('.v-card__text > div').text
