from typing import List

from app.services.message_parser import parse
from django.test import TestCase


class MessageParserTests(TestCase):

    def assert_none_result(self, message):
        self.assertIsNone(parse(message))

    def assert_result(self, message: str, start_sum_number, distance_list: List[int], distance: int,
                      end_sum_number: int):
        result = parse(message)

        self.assertEquals(start_sum_number, result.start_sum_number)
        self.assertEquals(distance_list, result.distance_list)
        self.assertEquals(distance, result.distance)
        self.assertEquals(end_sum_number, result.end_sum_number)

    def test_float_distances(self):
        """Test that distances don't be float"""
        self.assert_none_result('321 + 12.8 = 500')
        self.assert_result('321.2 + 12 = 500.12', 2, [12], 12, 500)

    def test_spaces(self):
        """Test that may be spaces between distances"""
        self.assert_result('2345+34=15', 2345, [34], 34, 15)
        self.assert_result('2345 +34=15', 2345, [34], 34, 15)
        self.assert_result('2345 + 34=15', 2345, [34], 34, 15)
        self.assert_result('2345 + 34 =15', 2345, [34], 34, 15)
        self.assert_result('2345 + 34 = 15', 2345, [34], 34, 15)
        self.assert_result('2345 + 34+200 = 15', 2345, [34, 200], 234, 15)
        self.assert_none_result('2345 + 34+200k = 15')

    def test_hash_tag(self):
        """Test that may be hash tag in message"""
        self.assert_result('5145+8=5153\n#дикийзабег', 5145, [8], 8, 5153)

    def test_many_distances_without_spaces(self):
        """Test many distances in message without spaces"""
        self.assert_result('5127+6+12=5145', 5127, [6, 12], 18, 5145)

    def test_many_distances_with_spaces(self):
        """Test many distances with spaces in message"""
        self.assert_result('5106 + 6 + 15 = 5127', 5106, [6, 15], 21, 5127)

    def test_line_break(self):
        """Test line break in message"""
        self.assert_result('5091+4=5095 км\n\n#дикийзабег', 5091, [4], 4, 5095)

    def test_long_message(self):
        """Test long message"""
        self.assert_result('5080+6=5086\n'
                           'Друзья, кто с Уфы заходите на огонёк в следующее воскресенье! 😉😊\n'
                           'Сегодня отлично пробежались! 👍\n'
                           'Правда трекер опять заглючило, в этот раз не в мою пользу 😂😁 3 км/ч\n'
                           '#клуббегаСпарта #клуббегаСпартаУфа #Уфа', 5080, [6], 6, 5086)

    def test_stat_message(self):
        """Test that stat message is not taken"""
        self.assert_none_result('СТАТИСТИКА\n'
                                'Ура! Несмотря на холода и снег 5000 км позади! Мы - молодцы!!\n'
                                'Из новичков в этот раз все приветственные лавры получает Яна Ишмаева - '
                                'Стерлитамак! \n\\n'
                                'Наши итоги в цифрах: \n'
                                '1. Количество дней бега:\n'
                                '- всего - 149 дн.\n'
                                '- отрезок 4000-5000 - 42 дн.\n'
                                '2. Километраж:\n'
                                '- средний в день - 33,5 км/д\n'
                                '- максимум от одного человека - 832 км.\n'
                                '3. Тренировки: \n'
                                '- всего - 727 тр.\n'
                                '- среднее в день - 4,8 тр./д\n'
                                '- максимум от одного человека - 76 тр.\n'
                                '4. Бегуны:\n'
                                '- всего отметилось - 59 чел.\n'
                                '- отметилось на 4000-5000 - 21 чел.\n'
                                '- новых на отрезке 4000-5000 - 1 чел. \n\n'
                                'Пост со статистикой на 4000 км - http://vk.cc/4HAk6E \n'
                                'Следующий отчет на 6000 км.\n'
                                'Всем отличного бега!')

    def test_start_sum(self):
        """Test start sum"""
        self.assert_result('0 + 32768 = 32768', 0, [32768], 32768, 32768)

    def test_big_distances(self):
        """Test that big distances will be normal processing"""
        self.assert_result('999999900 + 100 = 1000000000', 999_999_900, [100], 100, 1_000_000_000)
