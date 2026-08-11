# EinkRPI

Project aims at creating a framework, that will allow turn a RPI SBC and connected Waveshare eink screen into a e-book reader and portable computer.

It uses two files provided by Waveshare: `epdconfig.py` and `epdconfig.pyc`.

The screen used is 7.5 black and white eink screen.

# Installation

For now there are some issues with install script. Make sure to do the things inside by yourself if some are not done.
Moreover, remember to edit lightdm.conf file in your etc directory, and change rpc-lab to dwm as it is not included in the installation script.

If you want to use xdotool, first export DISPLAY variable with `:0` value (`export DISPLAY=:0`) in your ssh session that you want to use xdotool from.

You will probably need to create or edit your `.xinitrc` file with content: `exec dwm`.

It is good practice to edit your .bashrc to give it aliases:
- `z` for zathura,
- `f` for feh,
- `b` for `xdotool key alt+b` to conveniently hide or show the bar,
- `k` for `xdotool key alt+k` to move windows in the pane up,
- `j` for `xdotool key alt+j` to move windows in the pane down,
- `x` for `xdotool_interactive` script located in your `$HOME/.local/share/einkrpi/` directory.

# License

Project is available under open source license specifiedd in [LICENSE.md].

