import unittest
import prog1

class TestPeog(unittest.TestCase):
	def test_TwoInt3(self):
		self.assertEqual(prog1.func(1, 2, 1), 1)
	def test_TwoInt1(self):
		self.assertEqual(prog1.func(1, -5, 6), 2)
	def test_TwoInt2(self):
		self.assertEqual(prog1.func(1, 1, 1), 0)
	def test_IntStr(self):
		with self.assertRaises(ValueError):
			prog1.func(0, 1, 2)
