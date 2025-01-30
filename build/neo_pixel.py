import board
import neopixel
import RPi.GPIO as IO
import time

# IO.setmode(IO.BCM)  # Set the GPIO mode to BOARD numbering
# LED_Pin = 18  # Define the pin number for the LED
# IO.setup(LED_Pin, IO.OUT) 

# IO.output(LED_Pin, 1)
# time.sleep(5)
# IO.output(LED_Pin, 0)

pixels = neopixel.NeoPixel(board.D10 ,32, brightness=0.2, auto_write=False)
pixels[0] = (255,0,0)

pixels.fill((0,255,0))	
pixels.show()
time.sleep(2) 
pixels.fill((255,0,0))	
pixels.show()
time.sleep(2)
pixels.fill((0,0,255))	
pixels.show()
time.sleep(2)
pixels.fill((125,125,125))	
pixels.show()
time.sleep(2)
pixels.fill((0,0,0))	
pixels.show()

	
