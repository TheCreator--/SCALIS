import pygame
from pygame.locals import *
import time

import marching_cubes
import ConvolutionSurface

WIDTH = 150
HEIGHT = 150
SCALING = 1

class Gamestate:
	screen = None
	
	mouse_down = None
	mouse_pos = None
	mouse_clicked = False
	mouse_pressed = False
	scroll = 0
	
	shift_pressed = False
	space_pressed = False
	delete_pressed = False
	
	default_radius = 5
	bone_radius = []
	bones = []
	selected_bones = []
	bone_segments = []
	bone_triangles = []
	bone_selected = None
	bone_selected_offset = None

def reset_user_input(gs):
	gs.mouse_clicked = False
	gs.scroll = 0

def handle_user_input(gs):
	global SCALING

	reset_user_input(gs)

	for event in pygame.event.get():
		if event.type == QUIT:
			gs.done = True
		elif event.type == pygame.VIDEORESIZE:
			# Get the min dimension change to keep the screen square
			min_dim = event.w if event.w < event.h else event.h
			
			SCALING = 1 - int((WIDTH - min_dim) / WIDTH)
		
			gs.screen = pygame.display.set_mode((SCALING * WIDTH, SCALING * WIDTH), pygame.RESIZABLE)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			# If left mouse button
			if event.button == 1:
				gs.mouse_pressed = True
				gs.mouse_down_pos = (pygame.mouse.get_pos()[0] // SCALING, pygame.mouse.get_pos()[1] // SCALING)
			elif event.button == 4:
				gs.scroll = 1
			elif event.button == 5:
				gs.scroll = -1
		elif event.type == pygame.MOUSEMOTION:
			gs.mouse_pos = (pygame.mouse.get_pos()[0] // SCALING, pygame.mouse.get_pos()[1] // SCALING)
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				pos = (pygame.mouse.get_pos()[0] // SCALING, pygame.mouse.get_pos()[1] // SCALING)
				
				# If the mouse was pressed down in the same place, this is a click.
				if pos == gs.mouse_down_pos:
					gs.mouse_clicked = pos
				
				gs.mouse_pressed = False
				gs.mouse_down_pos = None
		elif event.type == pygame.KEYDOWN:
			if event.key == K_LSHIFT:
				gs.shift_pressed = True
			elif event.key == K_SPACE:
				gs.space_pressed = True
			elif event.key == K_DELETE:
				gs.delete_pressed = True
		elif event.type == pygame.KEYUP:
			if event.key == K_LSHIFT:
				gs.shift_pressed = False
			elif event.key == K_SPACE:
				gs.space_pressed = False
			elif event.key == K_DELETE:
				gs.delete_pressed = False
			
def update_game_state(gs):
	if gs.mouse_clicked:
		# If we clicked on an existing bone, select it
		for i in range(len(gs.bones)):
			bone = gs.bones[i]
			
			if bone is not None:
				x = gs.mouse_pos[0]
				y = gs.mouse_pos[1]
				
				if x >= bone[0] - gs.bone_radius[i] and \
						x <= bone[0] + gs.bone_radius[i] and \
						y >= bone[1] - gs.bone_radius[i] and \
						y <= bone[1] + gs.bone_radius[i]:
						
					# If this bone is already selected, deselect it.
					if i in gs.selected_bones:
						gs.selected_bones.remove(i)
					else:
						# If the shift key is pressed add this bone to the selection, otherwise make this bone the selection.
						if gs.shift_pressed:				
							# If we already have 3 points, replace the last one.
							if len(gs.selected_bones) == 3:
								gs.selected_bones[2] = i
							else:
								gs.selected_bones.append(i)
						else:
							gs.selected_bones = [i]
					break
		# We haven't found any bones. Create a new one.
		else:
			gs.bones.append(gs.mouse_pos)
			gs.bone_radius.append(gs.default_radius)
	
	# If the space key is pressed, combine all of the selected bones into either a segment or a triangle.
	if gs.space_pressed:
		if len(gs.selected_bones) == 2:
			gs.bone_segments.append((gs.selected_bones[0], gs.selected_bones[1]))
			gs.selected_bones = []
		elif len(gs.selected_bones) == 3:
			gs.bone_triangles.append((gs.selected_bones[0], gs.selected_bones[1], gs.selected_bones[2]))
			gs.selected_bones = []
			
	# If the delete key is pressed, remove all of the selected bones.
	if gs.delete_pressed:
		# Remove the actual bones that are selected
		for selected in gs.selected_bones:
			gs.bones[selected] = None
			# Remove the segments and triangles made from these bones.
			for segment in list(gs.bone_segments):
				if selected in segment:
					gs.bone_segments.remove(segment)
			for triangle in list(gs.bone_triangles):
				if selected in triangle:
					gs.bone_triangles.remove(triangle)
		# We are no longer selecting any bones (they are all removed)
		gs.selected_bones = []
	
	# If the mouse is pressed, and we have moved it from the starting position (i.e. not a click) move the bone if present.
	if gs.mouse_pressed:
		# If we have not selected any bone, find a bone that we clicked on.
		if gs.bone_selected is None:
			for i in range(len(gs.bones)):
				bone = gs.bones[i]
				
				if bone is not None:
					x = gs.mouse_pos[0]
					y = gs.mouse_pos[1]
					
					tolerance = gs.bone_radius[i] if gs.bone_radius[i] > 2 else 2
					
					if x >= bone[0] - tolerance and \
							x <= bone[0] + tolerance and \
							y >= bone[1] - tolerance and \
							y <= bone[1] + tolerance:
						
						gs.bone_selected = i
						gs.bone_selected_offset = [bone[0] - x, bone[1] - y]
						
						break
			else:
				# We haven't found any bones, meaning no bone is selected.
				gs.bone_selected = None
				
		# If the mouse moved, move the bone with it
		elif gs.mouse_down_pos != gs.mouse_pos:
			gs.bones[gs.bone_selected] = [gs.mouse_pos[0] + gs.bone_selected_offset[0], gs.mouse_pos[1] + gs.bone_selected_offset[1]]
	else:
		gs.bone_selected = None
		
	# If the scroll wheel was moved, change the radius of the bone we are on top of.
	if gs.scroll != 0:
		for i in range(len(gs.bones)):
			bone = gs.bones[i]
			
			if bone is not None:
				x = gs.mouse_pos[0]
				y = gs.mouse_pos[1]
				
				tolerance = gs.bone_radius[i] if gs.bone_radius[i] > 2 else 2
				
				if x >= bone[0] - tolerance and \
						x <= bone[0] + tolerance and \
						y >= bone[1] - tolerance and \
						y <= bone[1] + tolerance:
						
					gs.bone_radius[i] += gs.scroll
					if gs.bone_radius[i] < 0: gs.bone_radius[i] = 0
					
					break
		

def render_field(gs, field):
	for x in range(0, WIDTH-1):
		for y in range(0, HEIGHT-1):
			cell = [(x*SCALING,y*SCALING+1*SCALING), (x*SCALING+1*SCALING,y*SCALING+1*SCALING), (x*SCALING+1*SCALING,y*SCALING), (x*SCALING,y*SCALING)]
			values = [field[x//SCALING+y//SCALING*WIDTH] for x,y in cell]
			
			edges = marching_cubes.polygonize(cell, values, 1)
			for ex, ey in edges:
				pygame.draw.line(gs.screen, (255, 0, 0), ex, ey)

def render(gs):
	# Reset window to blank color.
	gs.screen.fill((255,255,255))
	
	# Draw the game state.
	# Draw the integral field left by each bone.
	field = [0] * HEIGHT * WIDTH
	for a, b in gs.bone_segments:
		ConvolutionSurface.add_to_field(gs.bones[a], gs.bone_radius[a], gs.bones[b], gs.bone_radius[b], WIDTH, HEIGHT, field)
	render_field(gs, field)
				
	
	# Draw all the bones
	for i in range(len(gs.bones)):
		if gs.bones[i] is not None:
			if i in gs.selected_bones:
				color = (255, 255, 0)
			else:
				color = (0, 0, 255)
			
			if gs.bone_radius[i] >= 1:
				pygame.draw.circle(gs.screen, color, (gs.bones[i][0]*SCALING, gs.bones[i][1]*SCALING), gs.bone_radius[i] * SCALING, 1)
	
	# Draw the bone triangles.
	#for x, y, z in gs.bone_triangles:
	#	pygame.draw.polygon(gs.screen, (100, 100, 100), (gs.bones[x], gs.bones[y], gs.bones[z]))
	
	# Draw the bone segments.
	for x, y in gs.bone_segments:
		pygame.draw.line(gs.screen, (0, 0, 0), (gs.bones[x][0]*SCALING, gs.bones[x][1]*SCALING), (gs.bones[y][0]*SCALING, gs.bones[y][1]*SCALING))
	
			
	# Show new frame.
	pygame.display.flip()


def main():
	# Create game window.
	gs = Gamestate()
	pygame.init()
	gs.screen = pygame.display.set_mode((WIDTH*SCALING, HEIGHT*SCALING), pygame.RESIZABLE)
	
	# Game loop
	gs.done = False
	elapsed_time = 0
	frame_counter = 0
	prev_time = time.time()
	while not gs.done:
		curr_time = time.time()
		dt = curr_time - prev_time
		elapsed_time += dt
		frame_counter += 1
				
		if elapsed_time >= 1:
			print(frame_counter / elapsed_time)
			elapsed_time %= 1
			frame_counter = 0
		
		handle_user_input(gs)
		update_game_state(gs)
		render(gs)
		
		prev_time = curr_time

	pygame.quit()

if __name__ == "__main__":
	main()
	