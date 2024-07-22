import time

from touch import Touch
from TP_lib import epd2in13_V3
epd = epd2in13_V3.EPD()
epd.reset()


def new_touch_point_callback(touch_event):
    print(f"New touchpoint: {str(touch_event.touch_points[-1])}")


def touch_event_start_callback(touch_event):
    print(f"TouchEvent start at: {touch_event.timestamp_start}")


def touch_event_end_callback(touch_event):
    print(f"TouchEvent end at: {touch_event.timestamp_start}")
    print(f"{len(touch_event.touch_points)/(touch_event.timestamp_end - touch_event.timestamp_start)} tp/ms")


def touch_event_gesture_end_callback(touch_event):
    print("It was a gesture")


def touch_event_tap_end_callback(touch_event):
    print("It was a tap")


touch = Touch(
    0,
    new_touch_point_callback,
    touch_event_start_callback,
    touch_event_end_callback,
    touch_event_gesture_end_callback,
    touch_event_tap_end_callback,
)

time.sleep(60 * 60)
