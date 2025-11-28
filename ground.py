# ground.py
import pygame
from OpenGL.GL import *


class TexturedGround:
    """
    Simple textured ground plane - just 1 quad with a tiled grass texture.
    Way faster than loading a 16K polygon grass model!
    """
    
    def __init__(self, texture_path, size=1000, tile_repeat=10):
        """
        Args:
            texture_path: Path to the grass texture image (jpg/png)
            size: Half-size of the ground plane (total will be size*2 x size*2)
            tile_repeat: How many times to tile the texture across the ground
        """
        self.size = size
        self.tile_repeat = tile_repeat
        self.texture_id = None
        self.display_list = None
        
        # Load texture
        self._load_texture(texture_path)
        
        # Generate display list for even faster rendering
        self._generate_display_list()
    
    def _load_texture(self, texture_path):
        """Load and configure the grass texture"""
        try:
            # Load image with pygame
            surf = pygame.image.load(texture_path)
            image_data = pygame.image.tostring(surf, 'RGB', True)
            width, height = surf.get_rect().size
            
            # Generate OpenGL texture
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            
            # Texture parameters for tiling
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload texture data
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                        GL_RGB, GL_UNSIGNED_BYTE, image_data)
            
            # Generate mipmaps for better quality at distance
            glGenerateMipmap(GL_TEXTURE_2D)
            
            print(f"✓ Grass texture loaded: {texture_path} ({width}x{height})")
            
        except Exception as e:
            print(f"✗ Failed to load grass texture: {e}")
            self.texture_id = None
    
    def _generate_display_list(self):
        """Pre-compile the ground quad into a display list"""
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        s = self.size
        t = self.tile_repeat  # UV coordinate for tiling
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Normal pointing up
        
        # Four corners with tiled UV coordinates
        glTexCoord2f(0, 0)
        glVertex3f(-s, 0, -s)
        
        glTexCoord2f(t, 0)
        glVertex3f(s, 0, -s)
        
        glTexCoord2f(t, t)
        glVertex3f(s, 0, s)
        
        glTexCoord2f(0, t)
        glVertex3f(-s, 0, s)
        
        glEnd()
        
        glEndList()
    
    def render(self):
        """Render the textured ground"""
        if self.texture_id is None:
            # Fallback: render green quad without texture
            glDisable(GL_TEXTURE_2D)
            glColor3f(0.2, 0.6, 0.2)
            glCallList(self.display_list)
            return
        
        # Save current state
        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT | GL_CURRENT_BIT)
        
        # Enable texturing
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Set color to white so texture shows properly
        glColor3f(1.0, 1.0, 1.0)
        
        # Render the quad
        glCallList(self.display_list)
        
        # Restore previous state - this prevents texture bleeding to other objects
        glPopAttrib()
        
        # Explicitly unbind texture and disable texturing
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
    
    def free(self):
        """Clean up OpenGL resources"""
        if self.texture_id:
            glDeleteTextures([self.texture_id])
        if self.display_list:
            glDeleteLists(self.display_list, 1)