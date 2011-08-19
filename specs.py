from imagekit.specs import ImageSpec 
from imagekit import processors 


class ResizeDesktopLarge(processors.Resize):
    width = 1600
    height = 1200
    crop = True
    
class ResizeDesktopLargeWide(processors.Resize):
    width = 1680
    height = 1050
    crop = True
    
class ResizeDesktopMedium(processors.Resize):
    width = 1280
    height = 1024
    crop = True
    
class ResizeAvatar(processors.Resize):
    width = 150
    height = 150
    crop = True

class ResizeAdminThumb(processors.Resize): 
    width = 150 
    height = 150 
    crop = True

class ResizeDisplay(processors.Resize):
    width = 640
    height = 480
    crop = True

class AdminThumb(ImageSpec): 
    access_as = 'admin_thumb' 
    pre_cache = True 
    processors = [ResizeAdminThumb] 

class Display(ImageSpec):
    access_as = 'display'
    pre_cache = True
    increment_count = True
    processors = [ResizeDisplay]

class DesktopLarge (ImageSpec):
    access_as = 'desktop_large'
    processors = [ResizeDesktopLarge]
    
class ResizeDesktopLargeWide (ImageSpec):
    access_as = 'desktop_large_wide'
    processors = [ResizeDesktopLargeWide]
    
class ResizeDesktopMedium (ImageSpec):
    access_as = 'desktop_medium'
    processors = [ResizeDesktopMedium]
    
class ResizeAvatar (ImageSpec):
    access_as = 'avatar'
    processors = [ResizeAvatar]