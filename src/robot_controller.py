import ai2thor.controller

class Controller:

	moves = {'trai': 'MoveLeft', 'tien': 'MoveAhead', 'phai': 'MoveRight', 'lui': 'MoveBack'}
	rotates = {'quaytrai': -90, 'quayphai': 90}
	looks = {'nhinlen': -15, 'nhinxuong': 15}

	def __init__(self, _screen_size=400):
		self.screen_size = _screen_size
		self.rotation = 0
		self.horizon = 0

		self.controller = ai2thor.controller.Controller()
		self.event = None

	def start(self):
		self.controller.start(player_screen_width=self.screen_size,
				player_screen_height=self.screen_size)
		self.controller.reset('FloorPlan201')
		self.event = self.controller.step(dict(action='Initialize',
                            gridSize=0.5,
                            rotation=self.rotation,
                            horizon=self.horizon,
                            renderClassImage=True,
                            renderObjectImage=True))


	def stop(self):
		self.controller.stop()

	def apply(self, action):
		if action in self.moves:
			event = self.controller.step(dict(action=self.moves[action]))

		elif action in self.rotates:
			self.rotation += self.rotates[action]
			event = self.controller.step(dict(action='Rotate', rotation=self.rotation))

		elif action in self.looks:
			self.horizon += self.looks[action]
			event = self.controller.step(dict(action='Look', horizon=self.horizon))

if __name__ == '__main__':
	controller = Controller()

	import time
	controller.start()
	while True:
		controller.apply('quaytrai')
		time.sleep(0.1)
	controller.stop()