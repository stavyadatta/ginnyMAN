#!/usr/bin/env python
"""Display the Monash logo on Pepper's chest tablet and wave continuously.

The logo lives on the robot at /home/nao/monash_logo_color_white_bg.png.
This script (run from a dev machine like pepper_middleware/pepper.py):

  1. SSH-copies the logo into a folder served by Pepper's internal web
     server, so the tablet's browser can fetch it.
  2. Connects to NAOqi over the network.
  3. Calls ALTabletService.showImage() with the resulting URL.
  4. Loops the standard "Hey_1" wave animation in a background thread
     while the logo stays on screen.

Press Ctrl+C to stop waving, clear the tablet and exit.
"""

import argparse
import random
import subprocess
import time
from threading import Event, Thread

import qi

REMOTE_IMAGE = "/home/nao/monash_logo_color_white_bg.png"
# boot-config ships with every Pepper; its html/ folder is served at
# http://198.18.0.1/apps/boot-config/ from the tablet's perspective.
REMOTE_APP_DIR = "/home/nao/.local/share/PackageManager/apps/boot-config/html"
REMOTE_TARGET = "monash_logo.png"
TABLET_URL = "http://198.18.0.1/apps/boot-config/" + REMOTE_TARGET

WAVE_ANIMATION = "animations/Stand/Gestures/Hey_1"
WAVE_GAP_SECONDS = 2.0
GREETING_PHRASES = [
    "Welcome to Monash Robotics",
    "So great to have you here",
]


def stage_image_on_robot(robot_ip, ssh_user):
    remote_cmd = "mkdir -p {dir} && cp {src} {dir}/{dst}".format(
        dir=REMOTE_APP_DIR, src=REMOTE_IMAGE, dst=REMOTE_TARGET)
    subprocess.check_call(
        ["ssh", "{}@{}".format(ssh_user, robot_ip), remote_cmd])


def wave_loop(animation_service, tts_service, stop_event):
    """Wave + greet on repeat until stop_event is set.

    Each cycle: pick a random greeting, kick off the wave and speech in
    parallel via NAOqi's _async=True futures, wait for *both* to finish,
    then pause for WAVE_GAP_SECONDS before the next cycle.
    """
    while not stop_event.is_set():
        phrase = random.choice(GREETING_PHRASES)
        print("Greeting: {!r}".format(phrase))
        try:
            anim_future = animation_service.run(WAVE_ANIMATION, _async=True)
            tts_future = tts_service.say(phrase, _async=True)
            anim_future.wait()
            tts_future.wait()
        except Exception as e:
            print("Wave/speech cycle failed: {}".format(e))
        stop_event.wait(WAVE_GAP_SECONDS)


def main():
    parser = argparse.ArgumentParser(
        description="Display the Monash logo on Pepper's tablet and wave")
    parser.add_argument("--ip", default="192.168.0.52",
                        help="Pepper IP address")
    parser.add_argument("--port", type=int, default=9559,
                        help="NAOqi port")
    parser.add_argument("--ssh-user", default="nao",
                        help="SSH user used to stage the image on the robot")
    parser.add_argument("--skip-stage", action="store_true",
                        help="Skip the SSH copy (image already in place)")
    parser.add_argument("--no-wave", action="store_true",
                        help="Only show the logo, don't run the wave loop")
    args = parser.parse_args()

    if not args.skip_stage:
        print("Staging logo on {} -> {}".format(args.ip, REMOTE_APP_DIR))
        stage_image_on_robot(args.ip, args.ssh_user)

    app = qi.Application(
        ["MonashLogoDisplay",
         "--qi-url=tcp://{}:{}".format(args.ip, args.port)])
    app.start()
    session = app.session
    print("Connected to Pepper at {}:{}".format(args.ip, args.port))

    tablet = session.service("ALTabletService")
    animation_service = session.service("ALAnimationPlayer")
    motion_service = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")
    audio_device = session.service("ALAudioDevice")
    try:
        audio_device.setOutputVolume(70)
    except Exception as e:
        print("Could not set master volume: {}".format(e))

    try:
        tablet.hideImage()
    except Exception:
        pass
    try:
        tablet.cleanCache()
    except Exception:
        pass

    # Cache-bust: tablet WebKit keys cached images by URL, so a stable
    # URL keeps serving the old PNG even after we restage the file.
    cache_busted_url = "{}?t={}".format(TABLET_URL, int(time.time()))
    tablet.preLoadImage(cache_busted_url)
    tablet.showImage(cache_busted_url)
    print("Showing Monash logo: {}".format(cache_busted_url))

    print("Waking up the robot...")
    motion_service.wakeUp()

    stop_event = Event()
    wave_thread = None
    if not args.no_wave:
        wave_thread = Thread(target=wave_loop,
                             args=(animation_service, tts_service, stop_event))
        wave_thread.daemon = True
        wave_thread.start()
        print("Waving '{}' + greeting on loop.".format(WAVE_ANIMATION))

    print("Press Ctrl+C to stop and clear the tablet.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping wave, resting robot and hiding image...")
        stop_event.set()
        if wave_thread is not None:
            wave_thread.join(timeout=5)
        try:
            tablet.hideImage()
        except Exception as e:
            print("hideImage failed: {}".format(e))
        try:
            motion_service.rest()
        except Exception as e:
            print("rest() failed: {}".format(e))
        try:
            session.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
