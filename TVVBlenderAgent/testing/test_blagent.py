import os
from unittest import TestCase
from flask import request

class TVVTestCase(TestCase):
    PORT = 8081
    TEST_AGENT = None
    def _setUp(self, setupClass):
        setup = setupClass()
        setup.setUp()
        return setup

class TestBlagent(TVVTestCase):
    def setUp(self):
        pass
    def test_frame_start(self):
        url = 'http://localhost:{port}/getstartframe'.format(port=self.PORT)
        response = request.get(url)
        self.assertTrue(response.ok)

