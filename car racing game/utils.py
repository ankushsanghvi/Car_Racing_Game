import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def blit_text_center(win, font, text, color=(255, 255, 255), shadow=True):
    if shadow:
        # Render shadow
        shadow_render = font.render(text, 1, (0, 0, 0))
        shadow_x = win.get_width()/2 - shadow_render.get_width()/2 + 2
        shadow_y = win.get_height()/2 - shadow_render.get_height()/2 + 2
        win.blit(shadow_render, (shadow_x, shadow_y))

    # Render main text
    render = font.render(text, 1, color)
    win.blit(render, (win.get_width()/2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2))

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Create a gradient surface from color1 to color2"""
    surface = pygame.Surface((width, height))

    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))

    return surface