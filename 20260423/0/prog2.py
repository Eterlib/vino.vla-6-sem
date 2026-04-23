import muiltiprocessing, unittest, socket, time

class TestProg(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls. proc = mulriprocessing.Process(target=sqroo.serve)
		cls.proc.start()
		time.sleep(1)
	@classmethod
	def tearDownClass(cls):
		cls.proc.terminate()
		cls.proc.join()
		
	def tearDown(self):
		self.sock.close()
