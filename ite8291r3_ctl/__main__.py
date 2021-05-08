import argparse
import sys
import math

from ite8291r3_ctl import ite8291r3

color_name_to_rgb = {
	"black":   (0, 0, 0),
	"white":   (255, 255, 255),
	"red":     (255, 0, 0),
	"green":   (0, 255, 0),
	"blue":    (0, 0, 255),
	"yellow":  (255 , 119, 0),
	"aqua":    (0, 255, 255),
	"purple":  (255, 0, 255),
	"silver":  (192, 192, 192),
	"gray":    (192, 192, 192),
	"maroon":  (128, 128, 0),
	"teal":    (0, 128, 128),
	"orange":  (255, 28, 0),
}

def screen_mode(handle, offset_x=None, offset_y=None, width=None, height=None):
	from Xlib import display, X
	from PIL import Image
	import time

	disp = display.Display()
	root = disp.screen().root
	geom = root.get_geometry()

	if offset_x is None:
		offset_x = 0

	if offset_y is None:
		offset_y = 0

	if width is None:
		width = geom.width

	if height is None:
		height = geom.height

	handle.enable_user_mode()

	last_draw = 0

	while True:

		raw = root.get_image(offset_x, offset_y, width, height, X.ZPixmap, 0xFFFFFFFF)

		im = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX")

		im = im.resize((16, 6), resample=Image.BOX)

		color_map = {}

		for row in range(6):
			for col in range(16):
				color_map[(row, col)] = im.getpixel((col, 5-row))

		handle.set_key_colors(color_map, enable_user_mode=False)

		now = time.monotonic()

		if now-last_draw <= 0.1:
			time.sleep(now-last_draw)

		last_draw = now

def main():
	handle = None

	def valid_rgb(x):
		try:
			value = tuple(map(int, x.strip().split(',')))
		except Exception as e:
			raise argparse.ArgumentTypeError("must have exactly three integers separated by comma (',')")

		if len(value) != 3:
			raise argparse.ArgumentTypeError("must have exactly three integers")

		return value

	def valid_intrange(lo, hi=math.inf):

		def f(x):
			try:
				value = int(x)
			except ValueError as e:
				raise argparse.ArgumentTypeError("must be an integer")

			if not (lo <= value <= hi):
				raise argparse.ArgumentTypeError(f"must be between {lo} and {hi} (inclusive)")

			return value

		return f

	def valid_devid(devid):
		try:
			(bus, addr) = (int(x) for x in devid.split('/'))

			if bus < 0 or addr < 0:
				raise argparse.ArgumentTypeError("bus and address id must be non-negative")

			return (bus, addr)
		except ValueError:
			raise argparse.ArgumentTypeError("two integers expected in device id")

	def handle_off_args(args):
		handle.turn_off()

	def handle_brightness_args(args):
		handle.set_brightness(args.brightness)

	def handle_test_pattern_args(args):
		import time

		b = handle.get_brightness()

		for i in range(6):
			handle.test_pattern(i, 50 - i * 10)

			if i != 5:
				time.sleep(2)

		handle.set_key_colors({}, b)

	def handle_freeze_args(args):
		handle.freeze()

	def handle_effect_args(args):
		effect = ite8291r3.effects.get(args.effect_name)

		assert effect is not None

		data = {}

		if args.speed is not None:
			data["speed"] = args.speed

		if args.brightness is not None:
			data["brightness"] = args.brightness

		if args.color  is not None:
			data["color"] = ite8291r3.colors[ args.color ]

		if args.direction  is not None:
			data["direction"] = ite8291r3.directions[ args.direction ]

		if args.reactive:
			data["reactive"] = 1

		if args.save:
			data["save"] = 1

		handle.set_effect(effect(**data))

	def handle_monocolor_args(args):
		if args.name:
			handle.set_color(color_name_to_rgb[args.name], args.brightness)
		elif args.rgb:
			handle.set_color(args.rgb, args.brightness)

	def handle_palette_args(args):
		if args.set_color:
			color_idx = int(args.set_color[0])
			color = valid_rgb(args.set_color[1])

			handle.set_palette_color(color_idx, color)

		if args.restore:
			handle.restore_default_palette()

		if args.random:
			from random import randint

			for i in range(7):
				handle.set_palette_color(i+1, [randint(0, 255) for _ in range(3)])

	def handle_mode_args(args):
		if args.screen is not None:
			try:
				if args.screen == "fullscreen":
					data = (None, ) * 4
				else:
					data = map(int, args.screen.strip().split(','))

				screen_mode(handle, *data)
			except KeyboardInterrupt:
				pass

	def handle_anim_args(args):
		import time

		def do_shift(color_map, rowdiff=0, coldiff=0):
			new_map = {}

			for ((row, col), color) in color_map.items():
				if (0 <= row+rowdiff <= 5) and (0 <= col+coldiff <= 15):
					new_map[ (row+rowdiff, col+coldiff) ] = color

			return new_map

		def do_animation():
			i = 0

			# do not store lines if no looping is needed
			if args.loop == 1:
				line_source = filter(lambda x: x != "", map(lambda x: x.strip(), args.file))
			else:
				line_source = list(filter(lambda x: x != "", [x.strip() for x in args.file]))

			while args.loop is True or i < args.loop:

				color_map = {}

				comment = 0

				for line in line_source:

					if line.startswith('#'):
						continue

					if line.startswith('/*'):
						comment += 1
						continue

					if line.startswith('*/'):
						comment -= 1
						continue

					if comment != 0:
						continue

					if line.startswith('pos'):
						_, row, col, rgb = line.split()
						color_map[(int(row), int(col))] = valid_rgb(rgb)

					elif line.startswith('apply'):
						handle.set_key_colors(color_map)

					elif line.startswith('wait'):
						_, t = line.split()
						time.sleep(float(t))

					elif line.startswith('clear'):
						color_map.clear()

					elif line.startswith('brightness'):
						_, b = line.split()
						handle.set_brightness(int(b))

					elif line.startswith('shift'):
						_, rowdiff, coldiff = line.split()

						color_map = do_shift(color_map, int(rowdiff), int(coldiff))

				i += 1

		try:
			do_animation()
		except KeyboardInterrupt:
			pass

	def handle_query_args(args):
		if args.fw_version:
			print("{}.{}.{}.{}".format(*handle.get_fw_version()))

		if args.brightness:
			print(handle.get_brightness())

		if args.state:
			print("off" if handle.is_off() else "on")

		if args.devices:
			for dev in ite8291r3.get_all():
				print(f"{dev.idVendor:04x}:{dev.idProduct:04x} "
				      f"bus {dev.bus} "
				      f"addr {dev.address} "
				      f"rev {dev.bcdDevice >> 8:x}.{dev.bcdDevice & 0xFF:02x} "
				      f"product '{dev.product}' "
				      f"manufacturer '{dev.manufacturer}'")

	parser = argparse.ArgumentParser(description='ITE8291 (rev 0.03) RGB keyboard backlight controller driver.')

	parser.add_argument('--debug', action='store_true', help='print traffic between the device and this program to stderr')
	parser.add_argument('--device', type=valid_devid, help='bus/addr of the device to control.')

	subparsers = parser.add_subparsers(help='Subcommands.')

	parser_off = subparsers.add_parser('off', help='Turn keyboard backlight off.')
	parser_off.set_defaults(func=handle_off_args)

	parser_brightness = subparsers.add_parser('brightness', help='Change keyboard backlight brightness.')
	parser_brightness.add_argument('brightness', type=valid_intrange(0, 50), help='Keyboard backlight brightness.')
	parser_brightness.set_defaults(func=handle_brightness_args)

	parser_test_pattern = subparsers.add_parser('test-pattern', help='Show the test pattern.')
	parser_test_pattern.set_defaults(func=handle_test_pattern_args)

	parser_freeze = subparsers.add_parser('freeze', help='Stop the running animation. [possibly unsafe]')
	parser_freeze.set_defaults(func=handle_freeze_args)

	parser_effect = subparsers.add_parser('effect', help='Change keyboard backlight effect.')
	parser_effect.add_argument('effect_name', choices=ite8291r3.effects.keys())
	parser_effect.add_argument('-s', '--speed', type=valid_intrange(0, 10), help='Speed of the effect.')
	parser_effect.add_argument('-b', '--brightness', type=valid_intrange(0, 50), help='Brightness of the effect.')
	parser_effect.add_argument('-c', '--color', choices=ite8291r3.colors.keys(), help='Color of the effect.')
	parser_effect.add_argument('--save', action='store_true', help='Instruct the controller to save the settings.')
	parser_effect.set_defaults(func=handle_effect_args)

	group = parser_effect.add_mutually_exclusive_group()
	group.add_argument('-d', '--direction', choices=ite8291r3.directions.keys(), help='Direction of the effect.')
	group.add_argument('-r', '--reactive', action='store_true', help='Specify if you want the effect to be reactive.')

	parser_monocolor = subparsers.add_parser('monocolor', help='Change keyboard backlight color.')
	parser_monocolor.add_argument('-b', '--brightness', type=valid_intrange(0, 50), help='Brightness of the color.')
	group = parser_monocolor.add_mutually_exclusive_group()
	group.add_argument('--name', choices=color_name_to_rgb.keys(), help='Specify color by name.')
	group.add_argument('--rgb', type=valid_rgb, metavar='red,green,blue', help='Specify color by RGB code.')
	parser_monocolor.set_defaults(func=handle_monocolor_args)

	parser_palette = subparsers.add_parser('palette', help='Change keyboard color palette.')
	group = parser_palette.add_mutually_exclusive_group()
	group.add_argument('--set-color', nargs=2, help='Change the given color of the palette to an arbitrary color.')
	group.add_argument('--restore', action='store_true', help='Restore palette to default values.')
	group.add_argument('--random', action='store_true', help='Set a random palette.')
	parser_palette.set_defaults(func=handle_palette_args)

	parser_mode = subparsers.add_parser('mode', help='Enable interactive modes.')
	group = parser_mode.add_mutually_exclusive_group()
	group.add_argument('--screen', metavar='offset_x,offset_y,width,height', nargs='?', const='fullscreen', help='Color the keyboard according to what is on the screen in the given region.')
	parser_mode.set_defaults(func=handle_mode_args)

	parser_anim = subparsers.add_parser('anim', help='Play animation.')
	parser_anim.add_argument('--file', type=argparse.FileType('r', bufsize=1), default=sys.stdin, help='Read animation from file. If not specified, stdin is used.')
	parser_anim.add_argument('--loop', nargs='?', const=True, default=1, type=valid_intrange(1), help='Repeat the animation this number of times. Omit the argument to repeat indefinitely.')
	parser_anim.set_defaults(func=handle_anim_args)

	parser_query = subparsers.add_parser('query', help='Query the controller.')
	parser_query.add_argument('--fw-version', action='store_true', help='Get the controller firmware version.')
	parser_query.add_argument('--brightness', action='store_true', help='Get the current brightness.')
	parser_query.add_argument('--state', action='store_true', help='Get the current state of the keyboard backlight.')
	parser_query.add_argument('--devices', action='store_true', help='List available devices that may be controlled.')
	parser_query.set_defaults(func=handle_query_args)

	args = parser.parse_args()

	if args.debug:
		ite8291r3.DEBUG = True

	try:
		handle = ite8291r3.get(args.device)
	except FileNotFoundError as e:
		print(f"device handle could not be acquired: {e}")
		return 1

	assert handle

	try:
		if "func" in args:
			args.func(args)

	except Exception as e:
		print(f"failed to carry out operation: {e}", file=sys.stderr)
		return 1

	return 0

if __name__ == "__main__":
	sys.exit(main())
