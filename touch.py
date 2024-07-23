import copy
import threading
import time

from TP_lib import epd2in13_V3
from TP_lib import gt1151

from shapes import Point, Rectangle


class TouchEvent:
    def __init__(
        self,
        touch_points=[],
        touch_areas=[],
        timestamp_start=None,
        timestamp_end=None,
    ):
        if timestamp_start is None:
            self.timestamp_start = time.time()
        else:
            self.timestamp_start = timestamp_start
        self.timestamp_end = timestamp_end
        self.touch_points = touch_points
        self.touch_areas = touch_areas


class Touch:
    WATCHDOG_TIMEOUT = 0.05  # seconds (worst-case 40 int/s allow 2x margin)

    def __init__(
        self,
        rotate=0,
        new_touch_point_callback=None,
        touch_event_start_callback=None,
        touch_event_end_callback=None,
        touch_event_gesture_end_callback=None,
        touch_event_tap_end_callback=None,
    ):
        self.current_touch_event = None
        self.current_touch_event_watchdog = None
        self.new_touch_point_callback = new_touch_point_callback
        self.new_touch_point_event = threading.Event()
        self.rotate = rotate
        self.touch_event_end_callback = touch_event_end_callback
        self.touch_event_gesture_end_callback = touch_event_gesture_end_callback
        self.touch_event_lock = threading.Lock()
        self.touch_event_start_callback = touch_event_start_callback
        self.touch_event_tap_end_callback = touch_event_tap_end_callback

        epd2in13_V3.EPD().reset()
        self.gt = gt1151.GT1151()
        self.gt.GT_Init()
        self.gt_touch = gt1151.GT_Development()

        # touch interrupt handler
        self.interrupt_handler = threading.Thread(
            target=self._interrupt_handler,
            daemon=True,
        )
        self.interrupt_handler.start()

        # touch event update watchdog
        self.current_touch_event_worker = threading.Thread(
            target=self._current_touch_event_worker,
            daemon=True,
        )
        self.current_touch_event_worker.start()

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, other):
        self._rotate = other % 360

    def _current_touch_event_worker(self):
        while True:
            # wait for new touch_point
            self.new_touch_point_event.wait()
            self.new_touch_point_event.clear()

            if len(self.current_touch_event.touch_points) == 1:
                threading.Thread(
                    target=self.touch_event_start_callback,
                    args=(copy.deepcopy(self.current_touch_event),),
                ).start()

            threading.Thread(
                target=self.new_touch_point_callback,
                args=(copy.deepcopy(self.current_touch_event),),
            ).start()

    def _current_touch_event_watchdog(self):
        self.touch_event_lock.acquire()
        self.current_touch_event.timestamp_end = time.time()

        # call generic TouchEvent end callback
        threading.Thread(
            target=self.touch_event_end_callback,
            args=(copy.deepcopy(self.current_touch_event),),
        ).start()

        # call gesture/tap TouchEvent end callback
        if is_gesture(self.current_touch_event):
            threading.Thread(
                target=self.touch_event_gesture_end_callback,
                args=(copy.deepcopy(self.current_touch_event),),
            ).start()
        else:
            threading.Thread(
                target=self.touch_event_tap_end_callback,
                args=(copy.deepcopy(self.current_touch_event),),
            ).start()

        self.current_touch_event = None
        self.touch_event_lock.release()

    def _interrupt_handler(self):
        while True:
            # wait for interrupt
            self.gt.GPIO_INT.wait_for_release()

            self.gt.GT_Scan(self.gt_touch)
            if not (self.gt_touch.X and self.gt_touch.Y):
                continue

            # cancel watchdog so that the touch_point gets added to the
            # current_touch_event
            if self.current_touch_event_watchdog:
                self.current_touch_event_watchdog.cancel()

            x = self.gt_touch.X[0]
            y = self.gt_touch.Y[0]
            s = self.gt_touch.S[0]
            half_s = s / 2

            touch_point = transpose_point(Point(x, y), self.rotate)
            touch_area = Rectangle(
                Point(touch_point.x - half_s, touch_point.y - half_s),
                Point(touch_point.x + half_s, touch_point.y + half_s),
            )

            # lock touch event for r/w
            self.touch_event_lock.acquire()
            if self.current_touch_event is None:
                self.current_touch_event = TouchEvent(
                    touch_points=[touch_point],
                    touch_areas=[touch_area],
                )
            else:
                self.current_touch_event.touch_points.append(touch_point)
                self.current_touch_event.touch_areas.append(touch_area)
            self.touch_event_lock.release()

            # register new touch_point and restart watchdog
            self.new_touch_point_event.set()
            self.current_touch_event_watchdog = threading.Timer(
                self.WATCHDOG_TIMEOUT, self._current_touch_event_watchdog
            )
            self.current_touch_event_watchdog.start()


def is_gesture(touch_event):
    """
    A TouchEvent is a gesture if the centre of any touchpoint leaves the
    touch_area of the first touchpoint.
    """
    assert isinstance(touch_event, TouchEvent)

    for touch_point in touch_event.touch_points:
        if not touch_event.touch_areas[0].contains_point(touch_point):
            return True
    return False


def transpose_point(point, deg):
    """
    Rotate a point in 90 degree increments based on the display dimensions

    The touch matrix is upside down relative to the native display orientation
    """
    match deg:
        case 0:
            return Point(
                epd2in13_V3.EPD_WIDTH - point.x,
                epd2in13_V3.EPD_HEIGHT - point.y,
            )
        case 90:
            return Point(
                epd2in13_V3.EPD_HEIGHT - point.y,
                point.x,
            )
        case 180:
            return point
        case 270:
            return Point(
                point.y,
                epd2in13_V3.EPD_WIDTH - point.x,
            )
        case _:
            raise Exception(
                "Invalid rotation, only increments of 90 deg are permitted",
            )
