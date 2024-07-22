from . import epdconfig

MAX_INPUTS = 5


class GT_Development:
    def __init__(self):
        self.TouchpointFlag = 0
        self.TouchCount = 0
        self.Touchkeytrackid = []
        self.X = []
        self.Y = []
        self.S = []


class GT1151:
    def __init__(self):
        # e-Paper
        self.ERST = epdconfig.EPD_RST_PIN
        self.DC = epdconfig.EPD_DC_PIN
        self.CS = epdconfig.EPD_CS_PIN
        self.BUSY = epdconfig.EPD_BUSY_PIN
        # TP
        self.TRST = epdconfig.TRST
        self.INT = epdconfig.INT
        self.GPIO_INT = epdconfig.GPIO_INT

    def digital_read(self, pin):
        return epdconfig.digital_read(pin)

    def digital_callback(self, pin, callback):
        return epdconfig.digital_callback(pin, callback)

    def GT_Reset(self):
        epdconfig.digital_write(self.TRST, 1)
        epdconfig.delay_ms(100)
        epdconfig.digital_write(self.TRST, 0)
        epdconfig.delay_ms(100)
        epdconfig.digital_write(self.TRST, 1)
        epdconfig.delay_ms(100)

    def GT_Write(self, Reg, Data):
        epdconfig.i2c_writebyte(Reg, Data)

    def GT_Read(self, Reg, len):
        return epdconfig.i2c_readbyte(Reg, len)

    def GT_ReadVersion(self):
        buf = self.GT_Read(0x8140, 4)
        print(f"gt1151 version: {buf}")

    def GT_Init(self):
        if epdconfig.module_init() != 0:
            return -1
        self.GT_Reset()
        self.GT_ReadVersion()

    def GT_Scan(self, GT_Dev):
        buf = []
        mask = 0x00

        buf = self.GT_Read(0x814E, 1)

        if buf[0] & 0x80 == 0x00:
            self.GT_Write(0x814E, mask)
        else:
            GT_Dev.TouchpointFlag = buf[0] & 0x80
            GT_Dev.TouchCount = buf[0] & 0x0F

            if GT_Dev.TouchCount > 5 or GT_Dev.TouchCount < 1:
                self.GT_Write(0x814E, mask)
                return

            buf = self.GT_Read(0x814F, GT_Dev.TouchCount * 8)
            self.GT_Write(0x814E, mask)

            GT_Dev.X = []
            GT_Dev.Y = []
            GT_Dev.S = []

            for i in range(GT_Dev.TouchCount):
                GT_Dev.Touchkeytrackid.append(buf[0 + 8 * i])
                GT_Dev.X.append((buf[2 + 8 * i] << 8) + buf[1 + 8 * i])
                GT_Dev.Y.append((buf[4 + 8 * i] << 8) + buf[3 + 8 * i])
                GT_Dev.S.append((buf[6 + 8 * i] << 8) + buf[5 + 8 * i])
