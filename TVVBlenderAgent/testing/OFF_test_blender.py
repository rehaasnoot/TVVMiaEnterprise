from unittest import TestCase
from blender import TVVBlender

class TVVTestCase(TestCase):
    TEST_AGENT = None
    def _setUp(self, setupClass):
        setup = setupClass()
        setup.setUp()
        return setup

class TestFrames(TVVTestCase):
    def setUp(self):
        self.TEST_AGENT = TVVBlender()
    def test_this(self):
        frame_end = self.TEST_AGENT.getFrameEnd()
        self.assertEqual(frame_end, 250, self)
        
class TestFrames(TVVTestCase):
    def setUp(self):
        self.TEST_AGENT = TVVBlender()
    def test_armature(self):
        arm_list = self.TEST_AGENT.getArmatureNameList()
        self.assertEqual(arm_list[0], "Armature.001", self)
        self.assertEqual(arm_list[1], "Armature.020", self)
        