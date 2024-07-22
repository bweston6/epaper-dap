import queue
import threading

from PIL import Image

from TP_lib import epd2in13_V3


class Frame:
    def __init__(self, image, update_mode):
        self.image = image
        self.update_mode = update_mode


class Display:

    def __init__(self, rotate=0):
        self.rotate = rotate
        if self.rotate in [0, 180]:
            self.width = epd2in13_V3.EPD_WIDTH
            self.height = epd2in13_V3.EPD_HEIGHT
        if self.rotate in [90, 270]:
            self.width = epd2in13_V3.EPD_HEIGHT
            self.height = epd2in13_V3.EPD_WIDTH

        self.current_mode = None
        self.first_refresh_flag = True
        self.sleep_flag = True
        self.worker_flag = True

        self.frame_queue = queue.Queue()
        self.epd = epd2in13_V3.EPD()
        self.FULL_UPDATE = self.epd.FULL_UPDATE
        self.PARTIAL_UPDATE = self.epd.PART_UPDATE

        self.worker = threading.Thread(
            target=self._worker,
        ).start()

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, other):
        self._rotate = other % 360

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close_resources()

    def __del__(self):
        self._close_resources()

    def _close_resources(self):
        self.frame_queue.join()
        self.worker_flag = False
        self.worker.join()
        self.epd.sleep()
        self.epd.Dev_exit()

    def sleep(self):
        self.epd.sleep()
        self.sleep_flag = True

    def display(self, image, update_mode, blocking=True):
        if self.rotate == 90:
            image = image.transpose(method=Image.Transpose.ROTATE_270)
        if self.rotate == 180:
            image = image.transpose(method=Image.Transpose.ROTATE_180)
        if self.rotate == 270:
            image = image.transpose(method=Image.Transpose.ROTATE_90)

        self.frame_queue.put(Frame(image, update_mode))

        if blocking:
            self.frame_queue.join()

    def _worker(self):
        while self.worker_flag:
            # wait until frame is in the queue
            frame = self.frame_queue.get(block=True)

            if self.first_refresh_flag:
                frame.update_mode = self.FULL_UPDATE
                self.first_refresh_flag = False

            if frame.update_mode == self.FULL_UPDATE:
                print("full update")
                if self.sleep_flag or self.current_mode != self.FULL_UPDATE:
                    self.epd.init(self.FULL_UPDATE)
                    self.current_mode = self.FULL_UPDATE
                    self.sleep_flag = False
                self.epd.displayPartBaseImage(self.epd.getbuffer(frame.image))
            elif frame.update_mode == self.PARTIAL_UPDATE:
                print("partial update")
                if self.sleep_flag or self.current_mode != self.PARTIAL_UPDATE:
                    self.epd.init(self.PARTIAL_UPDATE)
                    self.current_mode = self.PARTIAL_UPDATE
                    self.sleep_flag = False
                self.epd.displayPartial_Wait(self.epd.getbuffer(frame.image))

            self.frame_queue.task_done()
