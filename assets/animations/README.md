# Animation file format
An animation file is a plain text file, every line of which contains a single instruction. The main thing to keep in mind is the "color map", which stores *position <-> color* mappings.
Commands:
* `pos R C r,g,b` - set the color of (row `R`, column `C`) to `r,g,b` in the color map
* `apply` - actually set the keyboard backlighting according to the current color map
* `clear` - clear the color map
* `wait N` - wait `N` seconds (`N` may be floating point)
* `brightness B` - set the backlight brightness to `B` (it must be an integer between 0 and 50)
* `shift Rdiff Cdiff` - add `Rdiff` (int) to the y-coordinate (row), and `Cdiff` to the x-coordinate (column) of every entry in the color map 

*Note:* On the XMG Fusion 15, there are 16x6 actually available positions that can be colored. All animations have been created for that size.

*Note:* `shift 0 -1` shifts everything to the left by one, for example.

*Note:* Lines that begin with `#` are ignored. If a line starts with `/*`, then a comment block begins; if a line starts with `*/`, a comment block ends. Comment blocks may be nested. Look in the folder `assets/animations` to see more examples.

*Note:* `(row 0, col 0)` is the bottom left corner.

# Examples in this directory

## gaming_mode
This animation colors the WASD keys and the arrows red. (Similar to the *Gaming mode* in the XMG Control Center.)

## xmg_f15
This animation shows the text `XMG F15`.

## sine_wave.py
This animation generates a sine wave. You need to pipe the output of this script into `ite8291r3-ctl` as follows:
```
python sine_wave.py | ite8291r3-ctl anim
```
