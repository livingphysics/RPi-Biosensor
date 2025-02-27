import time
from typing import Tuple
from bioreactor import Bioreactor

# Ring light scheduler
def ring_light_scheduler(t: float) -> Tuple[int, int, int]:
    """Calculate RGB values for ring light based on time.
    
    Args:
        t: Time in seconds
        
    Returns:
        Tuple of RGB values (0-255) for red, green, blue
    """
    # One hour period = 3600 seconds
    # Map time to position in color wheel (0-360 degrees)
    angle = (t % 3600) * (360 / 3600)
    
    # Convert angle to RGB using HSV->RGB conversion
    # Hue = angle, Saturation = 1, Value = 1
    h = angle / 60  # Convert to 0-6 range
    c = 255  # Chroma = Value * Saturation * 255
    x = int(c * (1 - abs((h % 2) - 1)))
    
    if 0 <= h < 1:
        return (c, x, 0)
    elif 1 <= h < 2:
        return (x, c, 0)
    elif 2 <= h < 3:
        return (0, c, x)
    elif 3 <= h < 4:
        return (0, x, c)
    elif 4 <= h < 5:
        return (x, 0, c)
    else:  # 5 <= h < 6
        return (c, 0, x)

def ring_light_thread(bioreactor: Bioreactor, start: float) -> None:
    """Thread for updating the ring light"""
    while True:
        bioreactor.change_ring_light(ring_light_scheduler(time.time()-start))
        time.sleep(10)
