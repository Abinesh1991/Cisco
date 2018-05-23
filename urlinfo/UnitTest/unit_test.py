import sys
import json
import unittest
import requests

class UrlUnitTest(unittest.TestCase):
    """Test
    case
    for the client methods."""

    def test_sucess_response(self):
        response = requests.get('http://127.0.0.1:5000/urlinfo/1/hacker.com:5060/var-log-')
        self.assertEqual(response.status_code, 200)

    def test_failure_response(self):
        response = requests.get('http://127.0.0.1:5000/urlinfo/1/hacker.com:5060/var-log')
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()