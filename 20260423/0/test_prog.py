import unittest
import prog

class TestPeog(unittest.TestCase):
	def test_TwoInt(self):
		self.assertEqual(prog.func(1, 2), 4)
	def test_IntStr(self):
		with self.assertRaises(TypeError):
			prog.func(1, '2')
			
