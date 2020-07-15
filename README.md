# What is it?
`ite8291r3-ctl` is a userspace driver for the ITE 8291 (rev 0.03) RGB keyboard backlight controller. 


# Disclaimer
**This software is in early stages of developement. Futhermore, to quote GPL: Everything is provided as is. There is no warranty for the program, to the extent permitted by applicable law.**

**This software is licensed under the GNU General Public License v2.0**


# Compatibility
It has only been tested on Linux so far, but the core functionalities should work where `pyusb` is available. It has only been tried on an XMG Fusion 15 device so far, but it should work on other devices that have this particular ITE controller. So if [`aucc`](https://github.com/rodgomesc/avell-unofficial-control-center) works, this should work as well.

You can use `lsusb -d 048d:ce00` to determine if you have the suitable device. If it shows something like
```
Bus 001 Device 002: ID 048d:ce00 Integrated Technology Express, Inc. ITE Device(8291)
```
then you have an ITE 8291 controller, now the question is the revision number. If `lsusb -d 048d:ce00 -v | grep bcdDevice` shows
```
  bcdDevice            0.03
```
then the device is the correct revision and the program should work flawlessly.


# Dependencies
### Required
* [`Python 3.6`](https://python.org) or above
* [`pyusb`](https://github.com/pyusb/pyusb) *(and thus one of the backend that it supports, e.g. [`libusb`](https://libusb.info))*
### Optional
#### for the `screen` mode
* [`python-xlib`](https://pypi.org/project/python-xlib) Python package
* [`Pillow`](https://pypi.org/project/Pillow) Python package


# Features
## Current
* Support for built-in effects
* Monocolor mode
* Color palette management
* Per-key RGB colors
* Animations
* Coloring the keyboard according to what is on screen **[exprimental, Linux+Xorg only]**
* Querying parts of the controller state

## TO-DO
* User interface for instructing the controller to save changes
* Modify timeout
* A more sane way of assigning colors to specific keys
* Possibly a GUI
* Coloring the keyboard based on audio


# How to install
## Using PIP
The simplest way to install is to use `pip`:
```
pip install ite8291r3-ctl
```
*Note:* This will not download anything from the `assets` directory, it only installs the program. You will have to download them manually if you want to try them out.
*Note:* If you want to install for all users, run `pip` as root.

## Manually
### Downloading
If you have `git` installed:
```
git clone https://github.com/pobrn/ite8291r3-ctl
```

If you don't, then you can download it [here](https://github.com/pobrn/ite8291r3-ctl/archive/master.zip).

### Installing
After downloading the files, open the directory in a terminal, and run `pip install .` (or `pip install .[mode-screen]` if you want the optional dependencies for the `screen` mode). If you have multiple Python versions installed, specify one that satisfies the requirements.


# How to use
## Running it without installation
It is possible to run the utility without installation. Open the directory in a terminal, then run `python -m ite8291r3_ctl`. In this case you need to install the dependencies manually. `pip install -r requirements.txt` to install the required `pyusb` package. If you want to try the `screen` mode, you need to install the optional dependencies as well.

## Accessing the USB device
By default you need *root* privileges if you want to use this utility. As noted [here](https://github.com/rodgomesc/avell-unofficial-control-center/issues/45) and [here](https://aur.archlinux.org/cgit/aur.git/tree/10-ite-backlight.rules?h=ite-backlight), you can create a `udev` rule to allow everyone on your system to access this particular USB device, and thus you won't need to run the program as `root`.

If you want to do that, create a file `/etc/udev/rules.d/99-ite8291.rules`:
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="ce00", MODE:="0666"
```

or you can make it accessible only for a given group if you don't want anyone to have access to it:
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="ce00", GROUP="name_of_the_group", MODE:="0660"
```

after creating the file, run `sudo udevadm control --reload`, then `sudo udevadm trigger`. Or reboot.

## Subcommands
Use `ite8291r3-ctl -h` to get a list of subcommands. Use `ite8291r3 <subcommand> -h` to get the help for a given subcommand.
### off
Turns off the keyboard backlight.

*Example:*
```
ite8291r3-ctl off
```
___
### brightness
Changes the keyboard backlight brightness. The argument must be an integer between 0 and 50 (inclusive). Zero is no backlight, 50 is the brightest.

*Example:*
```
ite8291r3-ctl brightness 33
```
___
### test-pattern
```
ite8291r3-ctl test-pattern
```
**[for testing]** Shows a test pattern. It takes 10 seconds to run. It will turn off all key backlighting once it is finished.

___
### freeze
**[for testing, potentially unsafe]** Changes the speed of the current effect to 11 (one above the maximum). This appears to stop the effect (which are animated).

*Example:*
```
ite8291r3-ctl freeze
```

___
### effect
Changes the current effect. You can specify the following properties for effects:
| property   | possible values       | note                               | default |
|------------|-----------------------|------------------------------------|---------|
| speed      | integer from 0 to 10  | 0 is fastest, 10 is slowest        | 5       |
| brightness | integer from 0 to 50  | 0 is no backlight, 50 is brightest | 25      |
| color      | *see help*            | -                                  | random  |
| direction  | left, right, up, down | -                                  | left    |
| reactive   | -                     | -                                  | no      |

*Example:*
```
ite8291r3-ctl effect wave -s 0 -d up
// enable 'wave' effect with speed 0 (fastest) and bottom-up direction

ite8291r3-ctl effect rainbow -b 50
// enable rainbow effect with brightness 50 (max)

ite8291r3-ctl effect aurora -s 2 -c red -r
// enable reactive 'aurora' effect with speed 2 and color red
```

*Help*:
```
positional arguments:
  {breathing,wave,random,rainbow,ripple,marquee,raindrop,aurora,fireworks}

optional arguments:
  -h, --help            show this help message and exit
  -s, --speed SPEED
                        Speed of the effect.
  -b, --brightness BRIGHTNESS
                        Brightness of the effect.
  -c, --color {none,red,orange,yellow,green,blue,teal,purple,random}
                        Color of the effect.
  -d, --direction {none,right,left,up,down}
                        Direction of the effect.
  -r, --reactive        Specify if you want the effect to be reactive.
```
*Note:* If you specify `random` for color value, then all colors in the palette will be used in some fashion (depending on the effect).
*Note:* Do **not** use `none` for *direction* or *color*, because nothing will show up.
*Note:* Not all effects support all properties. You will get an error message if you try to use an unsupported property. See the *Effect property support matrix* section for more info.
*Note:* The color names might be misleading. `red` actually refers to the first color in the palette, `orange` to the second, and so on. If you modify the palette, and then set the color for an effect, you might not get what you expect.
*Note:* Enabling an effect will change the brightness. If not specified, the default value (25) will be applied.

___
### monocolor
Changes the color of the keyboard to a single color which may be specified as an RGB code or a predefined name. For the list of color names see `ite8291r3-ctl monocolor -h`.

*Example:*
```
ite8291r3-ctl monocolor -b 5 --name white
// set the backlight color to white and the brightness to 5 (very low)

ite8291r3-ctl monocolor --rgb 255,45,23
// change the backlight to color (255, 45, 23)
```
*Note:* If you don't specify the brightness, it will not be changed.
*Note:* No whitespaces are allowed in the RGB color code. `--rgb 255, 45, 23` is invalid and will be rejected.

___
### palette
Manages the color palette on the device.

*Example:*
```
ite8291r3-ctl palette --restore
// restores the palette to the default values

ite8291r3-ctl palette --set-color 3 255,13,14
// sets the 3rd color of the palette to (255, 13, 14)

ite8291r3-ctl palette --random
// sets all color to something randomly generated
```
*Note:* The index specified for `--set-color` must lie between 1 and 7 (inclusive).

___
### mode
**[experimental]** Enables one of the interactive modes. There is only a single mode available at the moment: `screen`, and it only works on Linux, with Xorg. You also need to install `python-xlib` and `Pillow` Python pacakges. You can install them by installing the utility with `pip install ite8291r3_ctl[mode-screen]`.

The `screen` mode takes a screenshot every 0.2 seconds of your screen, downsizes it to 16x6, and lights up the backlight LEDs according to the colors on the picture. [This video](https://www.youtube.com/watch?v=3VZthcTSBrI) is perfect for trying it out. The colors are not cleared after exiting, so I guess this is also a way to set the desired colors if you don't want to spend time with the more robust way described in the following section.

*Example:*
```
ite8291r3-ctl mode --screen
// take screenshots of the whole screen and color according to that

ite8291r3-ctl mode --screen 1000,1000,200,300
// take screenshots of the rectangle whose top left corner is at (1000, 1000) and has a width of 200 and height of 300
```
*Note:* You can exit by pressing `Ctrl+C` (or seding `SIGINT` to the process).

___
### anim
Plays an animation from a file. The name might be a bit misleading, because this is actually the facility of the program that allows you to set the color values on a per key basis. Read the README file in `assets/animatins` to see how animations may be made. It is a bit cumbersome, I am aware, however, a better way has yet to be found. The animation may be read from the standard input, so you can programatically generate it.

*Example:*
```
ite8291r3-ctl anim --file test_anim_file --loop 3
// read animation from 'anin_test_file' and loop it three times

ite8291r3-ctl anim --loop
// read animation from the standard input and loop it indefinitely
```
*Note:* If looping is required, then the whole file must be read into memory.

___
### query
Queries the controller.

*Example:*
```
ite8291r3-ctl query --fw-version
// prints the controller firmware version as X.Y.Z.W

ite8291r3-ctl query --brightness
// prints the current brightness

ite8291r3-ctl query --state
// prints the current state of the keyboard backlight: "on" or "off"
```
*Note:* This information may be useful if you want to use it in a script.


# Effect property support matrix
This matrix shows which effects support which properties.

| effect    | speed | color | direction | reactivity |
|-----------|-------|-------|-----------|------------|
| breathing | yes   | yes   | -         | -          |
| wave      | yes   | -     | yes       | -          | 
| random    | yes   | yes   | -         | yes        |
| rainbow   | -     | -     | -         | -          |
| ripple    | yes   | yes   | -         | yes        |
| marquee   | yes   | -     | -         | -          |
| raindrop  | yes   | yes   | -         | -          |
| aurora    | yes   | yes   | -         | yes        |
| fireworks | yes   | yes   | -         | yes        |

*Note:* brightness may be specified for all currently supported effects.


# Contribution
All contribution is welcome. If you find a bug, typo, or have a feature request, do not hestitate to report it on the [*Issues*](https://github.com/pobrn/ite8291r3-ctl/issues) page (but please do a search first, maybe someone has already reported it). If you have an addition to the software and you want it to be inclueded, open a [*pull request*](https://github.com/pobrn/ite8291r3-ctl/pulls).


# Acknowledgements
[`aucc`](https://github.com/rodgomesc/avell-unofficial-control-center), [`ite-backlight`](https://github.com/hexagonal-sun/ite-backlight), and [*Project Starbeat*](https://github.com/kirainmoe/tongfang-hackintosh-utility) have been incredily useful in gaining insight into how this controller works, without them, this program would not have been created.

