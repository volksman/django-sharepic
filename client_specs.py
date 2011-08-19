from imagekit.specs import ImageSpec 
from imagekit import processors

class ResizeAdminThumb(processors.Resize): 
    width = 150 
    height = 150 
    crop = True
    
class ResizeDisplay(processors.Resize):
    width = 640
    height = 480
    crop = True
    
class Display(ImageSpec):
    access_as = 'display'
    pre_cache = True
    increment_count = True
    processors = [ResizeDisplay]
    
class AdminThumb(ImageSpec): 
    access_as = 'admin_thumb' 
    pre_cache = True 
    processors = [ResizeAdminThumb] 