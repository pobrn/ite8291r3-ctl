import sys

import usb.core
import usb.util


DEBUG = False

VENDOR_ID   = 0x048D
PRODUCT_IDS = [0x6004, 0x6006, 0xCE00]
REV_NUMBER  = 0x0003 # 0.03

NUM_ROWS = 6
NUM_COLS = 21

ROW_BUFFER_LEN = 3 * NUM_COLS + 2

ROW_RED_OFFSET   = 1 + 2 * NUM_COLS
ROW_GREEN_OFFSET = 1 + 1 * NUM_COLS
ROW_BLUE_OFFSET  = 1 + 0 * NUM_COLS

class commands:
	SET_EFFECT        =   8
	SET_BRIGHTNESS    =   9
	SET_PALETTE_COLOR =  20
	SET_ROW_INDEX     =  22
	GET_FW_VERSION    = 128
	GET_EFFECT        = 136

colors = {
	"none" :  0,
	"red":    1,
	"orange": 2,
	"yellow": 3,
	"green":  4,
	"blue":   5,
	"teal":   6,
	"purple": 7,
	"random": 8,
}

directions = {
	"none":  0,
	"right": 1,
	"left":  2,
	"up":    3,
	"down":  4,
}

class effect_attrs:
	EFFECT     = 0
	SPEED      = 1
	BRIGHTNESS = 2
	COLOR      = 3
	DIRECTION  = 4
	REACTIVE   = 4
	SAVE       = 5

def effect(effect_id, args={}):

	max_arg_idx = max(map(lambda x: x[0], args.values()))

	def f(**kwargs):

		res = [0] * (max_arg_idx+1)
		for (k, (idx, default)) in args.items():
			res[ idx ] = default

		for (k, v) in kwargs.items():
			if k not in args:
				raise ValueError(f"'{k}' attr is not needed by effect")

			res[ args[k][0] ] = v

		res[effect_attrs.EFFECT] = effect_id
		return res

	return f

effects = {
	"breathing": effect(0x02, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"wave": effect(0x03, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"direction":  (effect_attrs.DIRECTION, directions.get("right")),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"random": effect(0x04, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"reactive":   (effect_attrs.REACTIVE, 0),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"rainbow": effect(0x05, {
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"ripple": effect(0x06, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"reactive":   (effect_attrs.REACTIVE, 0),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"marquee": effect(0x09, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"raindrop": effect(0x0A, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"aurora": effect(0x0E, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"reactive":   (effect_attrs.REACTIVE, 0),
		"save":       (effect_attrs.SAVE, 0),
	}),

	"fireworks": effect(0x11, {
		"speed":      (effect_attrs.SPEED, 5),
		"brightness": (effect_attrs.BRIGHTNESS, 25),
		"color":      (effect_attrs.COLOR, colors.get("random")),
		"reactive":   (effect_attrs.REACTIVE, 0),
		"save":       (effect_attrs.SAVE, 0),
	}),
}

class ite8291r3:
	def __init__(self, channel):
		self.channel = channel

	def __send_data(self, payload):
		if DEBUG:
			print(f"sending data ({len(payload)} bytes) to device: {payload}", file=sys.stderr)

		return self.channel.write(payload)

	def __send_ctrl(self, *payload):
		if len(payload) < 8:
			payload += (0, ) * (8 - len(payload))

		if DEBUG:
			print(f"sending ctrl device: {payload}", file=sys.stderr)

		# https://github.com/libusb/hidapi/blob/533dd9229a846d6ab00c4dced1cbddf66b576258/libusb/hid.c#L1180
		self.channel.ctrl_transfer(
			usb.util.build_request_type(usb.util.CTRL_OUT,
						    usb.util.CTRL_TYPE_CLASS,
						    usb.util.CTRL_RECIPIENT_INTERFACE), # bmRequestType
			0x009, # bRequest (HID set_report)
			0x300, # wValue (HID feature)
			0x001, # wIndex
			payload)

	def __get_ctrl(self, length):

		# https://github.com/libusb/hidapi/blob/533dd9229a846d6ab00c4dced1cbddf66b576258/libusb/hid.c#L1210
		data = self.channel.ctrl_transfer(
			usb.util.build_request_type(usb.util.CTRL_IN,
						    usb.util.CTRL_TYPE_CLASS,
						    usb.util.CTRL_RECIPIENT_INTERFACE), # bmRequestType
			0x001, # bRequest (HID get_report)
			0x300, # wValue (HID feature)
			0x001, # wIndex
			length)

		if DEBUG:
			print(f"received ctrl from device: {data}", file=sys.stderr)

		return data

	def get_fw_version(self):
		self.__send_ctrl(commands.GET_FW_VERSION)
		buf = self.__get_ctrl(8)

		return (buf[1], buf[2], buf[3], buf[4]) # high.low.test.customer

	def get_effect(self):
		self.__send_ctrl(commands.GET_EFFECT)
		return list(self.__get_ctrl(8)[2:]) # skip command id and control code

	def __set_row_index(self, row_idx):
		self.__send_ctrl(commands.SET_ROW_INDEX, 0x00, row_idx)

	def __set_effect_impl(self, control, effect=0x00, speed=0x00, brightness=0x00, color=0x00, direction_or_reactive=0x00, save=0x00):
		self.__send_ctrl(commands.SET_EFFECT, control, effect, speed, brightness, color, direction_or_reactive, save)

	def set_effect(self, effect_data):
		self.__set_effect_impl(0x02, *effect_data)

	def set_brightness(self, brightness):
		if not (0 <= brightness <= 50):
			raise ValueError("brightness must be between 0 and 50 inclusive")

		self.__send_ctrl(commands.SET_BRIGHTNESS, 0x02, brightness)

	def freeze(self):
		effect = self.get_effect()
		effect[effect_attrs.SPEED] = 11 # change speed to 11 (that stops the "animation" - empirical evidence)
		self.set_effect(effect)

	def turn_off(self):
		self.__set_effect_impl(control=0x01)

	def is_off(self):
		self.__send_ctrl(commands.GET_EFFECT)
		return self.__get_ctrl(8)[1] == 0x01

	def get_brightness(self):
		return self.get_effect()[effect_attrs.BRIGHTNESS]

	def enable_user_mode(self, brightness=None, save=False):
		if brightness is None:
			brightness = self.get_brightness()

		self.set_effect((51, 0, brightness, 0, 0, 1 if save else 0))

	def set_color(self, color, brightness=None, save=False):
		self.enable_user_mode(brightness, save)

		for row in range(NUM_ROWS):

			arr = [0] * ROW_BUFFER_LEN

			for i in range(NUM_COLS):
				arr[ROW_RED_OFFSET + i], arr[ROW_GREEN_OFFSET + i], arr[ROW_BLUE_OFFSET + i] = color

			self.__set_row_index(row)
			self.__send_data(bytearray(arr))

	def set_palette_color(self, idx, color):
		if not (1 <= idx <= 7):
			raise ValueError("palette color index must be between 1 and 7 (inclusive)")

		self.__send_ctrl(commands.SET_PALETTE_COLOR, 0, idx, *color)

	def restore_default_palette(self):
		self.set_palette_color(1, (255,   0,   0) ) # red
		self.set_palette_color(2, (255,  28,   0) ) # orange
		self.set_palette_color(3, (255, 119,   0) ) # yellow
		self.set_palette_color(4, (  0, 255,   0) ) # green
		self.set_palette_color(5, (  0,   0, 255) ) # blue
		self.set_palette_color(6, (  0, 255, 255) ) # teal
		self.set_palette_color(7, (255,   0, 255) ) # purple

	def test_pattern(self, shift=0, brightness=None, save=False):
		self.enable_user_mode(brightness, save)

		c = [
			(255, 0, 0),
			(0, 255, 0),
			(0, 0, 255),
		]

		for row in range(NUM_ROWS):

			arr = [0] * ROW_BUFFER_LEN

			for i in range(0, NUM_COLS, 3):
				for j in range(3):
					arr[ROW_RED_OFFSET + i + j], arr[ROW_GREEN_OFFSET + i + j], arr[ROW_BLUE_OFFSET + i + j] = c[(j + row + shift) % 3]

			self.__set_row_index(row)
			self.__send_data(bytearray(arr))

	def set_key_colors(self, color_map={}, brightness=None, save=False, enable_user_mode=True):
		arr = [ [0] * ROW_BUFFER_LEN for _ in range(NUM_ROWS) ]

		for ((row, col), color) in color_map.items():
			arr[row][ROW_RED_OFFSET + col], arr[row][ROW_GREEN_OFFSET + col], arr[row][ROW_BLUE_OFFSET + col] = color

		if enable_user_mode or save:
			self.enable_user_mode(brightness, save)

		for row in range(NUM_ROWS):
			self.__set_row_index(row)
			self.__send_data(bytearray(arr[row]))

class usb_channel:
	def __init__(self, dev, fd_out):
		self.dev = dev
		self.fd_out = fd_out

	def ctrl_transfer(self, *args, **kwargs):
		return self.dev.ctrl_transfer(*args, **kwargs)

	def write(self, payload):
		return self.dev.write(self.fd_out, payload)

def get(loc=None):
	if loc:
		(bus, addr) = loc
		dev = usb.core.find(bus=bus, address=addr)
	else:
		dev = usb.core.find(idVendor=VENDOR_ID, custom_match=lambda d: d.idProduct in PRODUCT_IDS and d.bcdDevice == REV_NUMBER)

	if not dev:
		raise FileNotFoundError("no suitable device found")

	if dev.is_kernel_driver_active(1):
		dev.detach_kernel_driver(1)

	cfg = dev.get_active_configuration()

	fd_out = usb.util.find_descriptor(cfg[(1, 0)], custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

	return ite8291r3(usb_channel(dev, fd_out))

def get_all():
	return usb.core.find(find_all=True,
			     idVendor=VENDOR_ID,
			     custom_match=lambda d: d.idProduct in PRODUCT_IDS and d.bcdDevice == REV_NUMBER)
