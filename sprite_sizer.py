import pygame
import os

# Initialize Pygame
pygame.init()

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the assets directory
assets_dir = os.path.join(script_dir, 'assets')

# List to store the sizes of each sprite
sprite_sizes = []

# Walk through all files in the assets directory and subdirectories
for root, dirs, files in os.walk(assets_dir):
    for filename in files:
        if filename.endswith('.png'):  # You can add other extensions if needed
            image_path = os.path.join(root, filename)

            # Load the sprite image
            sprite_image = pygame.image.load(image_path)

            # Get the size of the sprite
            sprite_rect = sprite_image.get_rect()
            width, height = sprite_rect.width, sprite_rect.height

            # Store the size and filename
            relative_path = os.path.relpath(image_path, script_dir)
            sprite_sizes.append((relative_path, width, height))

# Print the sizes of all sprites
for sprite in sprite_sizes:
    print(f'Image: {sprite[0]}, Width: {sprite[1]}, Height: {sprite[2]}')

# Quit Pygame
pygame.quit()
