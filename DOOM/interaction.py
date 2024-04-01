from math import sin, cos, atan2

from numba import njit
from numba.typed.typeddict import Dict as NumbaDict

from drawing import Drawing
from map import world_map
from player import Player
from ray_casting import mapping
from sprites import Sprites
from utilities import *


@njit(fastmath=True, cache=True)
def ray_casting_npc_player(npc_x: float, npc_y: float, _world_map: NumbaDict, player_position: Position) -> bool:
	ox, oy = player_position
	xm, ym = mapping(ox, oy)
	delta_x, delta_y = ox - npc_x, oy - npc_y
	current_angle: float = atan2(delta_y, delta_x) + pi

	sin_a, cos_a = sin(current_angle), cos(current_angle)

	# Verticals
	x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)

	for i in range(0, int(abs(delta_x)) // TILE):
		depth_v: float = (x - ox) / cos_a
		yv: float = oy + depth_v * sin_a
		tile_v: Position = mapping(x + dx, yv)

		if tile_v in _world_map:
			return False

		x += dx * TILE

	# Horizontals
	y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)

	for i in range(0, int(abs(delta_y)) // TILE):
		depth_h: float = (y - oy) / sin_a
		xh: float = ox + depth_h * cos_a
		tile_h: Position = mapping(xh, y + dy)

		if tile_h in _world_map:
			return False

		y += dy * TILE

	return True


class Interaction:
	def __init__(self, player: Player, sprites: Sprites, drawing: Drawing) -> None:
		self.player = player
		self.sprites = sprites
		self.drawing = drawing

	def interaction_objects(self) -> None:
		if self.player.shot and self.drawing.shot_animation_trigger:
			for sprite in sorted(self.sprites.list_of_objects, key=lambda x: x.distance_to_sprite):
				if sprite.is_on_fire[1]:
					if sprite.death_type != DeathType.IMMORTAL and not sprite.is_dead:
						if ray_casting_npc_player(sprite.x, sprite.y, world_map, self.player.position):
							sprite.is_dead = DeathType.TRUE
							sprite.is_blocked = None
							self.drawing.shot_animation_trigger = False
					break
