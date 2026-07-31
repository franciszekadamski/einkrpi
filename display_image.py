#!/usr/bin/python

import sys
import os
import argparse
import logging
import time
from PIL import Image
import mss
import traceback

import epd7in5_V2


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(description="Display an image on a Waveshare 7.5inch e-Paper V2 screen.")
    parser.add_argument("image_path", help="Path to the image file (BMP, PNG, JPG, etc.)")
    parser.add_argument("--clear", action="store_true", help="Clear the screen before displaying the image")
    parser.add_argument("--verbose", action="store_true", help="Logging for debugging")
    parser.add_argument("--capture", action="store_true", help="Whether to capture image from running xserver session")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        logging.error(f"Image not found: {args.image_path}")
        sys.exit(1)

    try:
        if args.verbose:
            logging.info("Initializing e-Paper display...")
        epd = epd7in5_V2.EPD()
        epd.init()

        if args.clear:
            logging.info("Clearing screen...")
            epd.Clear()
        
        if args.verbose:
            logging.info(f"Processing image: {args.image_path}")
        if args.capture:
            user_image = capture_x11_frame()
        else:
            user_image = Image.open(args.image_path)
 
        if args.verbose:
            logging.info(f"Image size: {user_image.size}")
        bg_image = process_image(epd, args, user_image)

        # Push to display
        if args.verbose:
            logging.info("Rendering image to display...")
        epd.display(epd.getbuffer(bg_image))
        
        # Small delay to let the screen update physically before sleeping
        time.sleep(1) 

        if args.verbose:
            logging.info("Putting display into deep sleep mode...")
        epd.sleep()
        
    except IOError as e:
        logging.error(f"Hardware/IO Error: {e}")
    except KeyboardInterrupt:    
        logging.info("Exiting via Ctrl+C, cleaning up GPIO pins...")
        epd7in5_V2.epdconfig.module_exit(cleanup=True)
        sys.exit(0)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        traceback.print_exc()


def process_image(epd, args, user_image):
        
    # Resize image to match screen dimensions (800x480 for 7.5" V2) while maintaining aspect ratio
    if args.verbose:
        logging.info(f'Screen dimensions: {epd.width}x{epd.height}')
        
    # Create a blank white background matching exact screen dimensions
    bg_image = Image.new('1', (epd.width, epd.height), 255) 
        
    # Scale image down to fit inside the screen boundaries if it's too large
    user_image.thumbnail((epd.width, epd.height), Image.Resampling.LANCZOS)
        
    # Center the image onto the white background
    paste_x = (epd.width - user_image.size[0]) // 2
    paste_y = (epd.height - user_image.size[1]) // 2
        
    # Ensure image is in 1-bit mode before pasting onto 1-bit background
    user_image = user_image.convert('1')
    bg_image.paste(user_image, (paste_x, paste_y))

    return bg_image


def capture_x11_frame(display_name: str = ':0'):
    os.environ['DISPLAY'] = display_name
    if 'XAUTHORITY' not in os.environ:
        os.environ['XAUTHORITY'] = f'{os.environ["HOME"]}/.Xauthority' 
    with mss.mss() as screen:
        monitor = screen.monitors[1]
        image_bytes = screen.grab(monitor)
        return Image.frombytes('RGB', image_bytes.size, image_bytes.bgra, 'raw', 'BGRX')



if __name__ == '__main__':
    main()

