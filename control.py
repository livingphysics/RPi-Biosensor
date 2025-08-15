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
    # 12 hour period = 43200 seconds (12 * 3600)
    # Check if we're in the first 12 hours (on) or second 12 hours (off)
    cycle_position = t % 43200
    
    if cycle_position < 43200 / 2:  # First 12 hours - white light on
        return (255, 255, 255)  # White illumination
    else:  # Second 12 hours - lights off
        return (0, 0, 0)  # All lights off

def ring_light_thread(bioreactor: Bioreactor, start: float) -> None:
    """Thread for updating the ring light"""
    while True:
        # Check if override is active
        if bioreactor.ring_light_override:
            # Use override color
            bioreactor.change_ring_light(bioreactor.ring_light_override_color)
        else:
            # Use normal scheduler
            color = ring_light_scheduler(time.time()-start)
            bioreactor.change_ring_light(color)
            # Update the state based on whether lights are on or off
            bioreactor.set_ring_light_state(color != (0, 0, 0))
        time.sleep(10)
