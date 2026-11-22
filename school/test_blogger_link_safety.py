"""No network or ad impressions: regression checks for Facebook destinations."""
import unittest
from blogger_link_safety import validate_blogger_links


class BloggerLinkSafetyTests(unittest.TestCase):
    def test_home_article_and_campaign(self):
        for tail in ('/', '/2026/11/lesson.html', '/?utm_source=facebook&utm_medium=social'):
            with self.subTest(tail=tail):
                self.assertTrue(validate_blogger_links('පාඩම්: https://punchinanamaga.blogspot.com' + tail))

    def test_rejects_missing_spoofed_and_extra_destinations(self):
        for text in (
            'no lesson link',
            'http://punchinanamaga.blogspot.com/',
            'https://punchinanamaga.blogspot.com.evil.example/',
            'https://punchinanamaga.blogspot.com@evil.example/',
            'https://evil.example/?next=https://punchinanamaga.blogspot.com/',
            'https://punchinanamaga.blogspot.com/ https://gamingpoddagames.github.io/',
            'https://punchinanamaga.blogspot.com/ //evil.example/ad',
            'https://punchinanamaga.blogspot.com/ www.evil.example',
            'https://punchinanamaga.blogspot.com/?redirect=https%3A%2F%2Fevil.example',
            'https://punchinanamaga.blogspot.com/?next=%2F%2Fevil.example',
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_blogger_links(text)


if __name__ == '__main__':
    unittest.main()
