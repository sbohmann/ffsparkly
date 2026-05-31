#!/usr/bin/env python3
import colorsys
import math
import os
import sys
import termios
import tty


ALT_SCREEN_ON = "\x1b[?1049h"
ALT_SCREEN_OFF = "\x1b[?1049l"
CURSOR_HIDE = "\x1b[?25l"
CURSOR_SHOW = "\x1b[?25h"
RESET = "\x1b[0m"
HOME = "\x1b[H"
CLEAR = "\x1b[2J"
PROMPT = " Press any key to exit "


def terminal_size() -> tuple[int, int]:
    try:
        size = os.get_terminal_size(sys.stdout.fileno())
    except OSError:
        return 80, 24

    return max(size.columns, 1), max(size.lines, 1)


def foreground_rgb(red: int, green: int, blue: int) -> str:
    return f"\x1b[38;5;{16 + 36 * red + 6 * green + blue}m"

def background_rgb(red: int, green: int, blue: int) -> str:
    return f"\x1b[48;5;{16 + 36 * red + 6 * green + blue}m"


def rainbow_plus_grid(width: int, height: int) -> str:
    lines = []

    for y in range(height):
        line = []
        for x in range(width):
            hue = ((x * 2.0) / max(width, 1) + (y * 3.0) / max(height, 1)) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            print(red, green, blue)
            line.append(
                f"{background_rgb(int(red * 5 + 0.5) % 6, int(green * 5 + 0.5) % 6, int(blue * 5 +0.5) % 6)} "
            )
        lines.append("".join(line))

    return "\n".join(lines)


def centered_prompt(width: int, height: int) -> str:
    row = max(1, height // 2 + 1)
    col = max(1, (width - len(PROMPT)) // 2 + 1)
    return f"\x1b[{row};{col}H\x1b[1;30;47m{PROMPT}{RESET}"


def draw() -> None:
    width, height = terminal_size()
    sys.stdout.write(HOME + CLEAR)
    sys.stdout.write(rainbow_plus_grid(width, height))
    sys.stdout.write(centered_prompt(width, height))
    sys.stdout.flush()


def wait_for_keypress() -> None:
    sys.stdin.read(1)


def main() -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("ffsparkly needs an interactive ANSI terminal.", file=sys.stderr)
        return 1

    original_terminal_settings = termios.tcgetattr(sys.stdin.fileno())

    try:
        tty.setcbreak(sys.stdin.fileno())
        sys.stdout.write(ALT_SCREEN_ON + CURSOR_HIDE)
        draw()
        wait_for_keypress()
    finally:
        termios.tcsetattr(
            sys.stdin.fileno(), termios.TCSADRAIN, original_terminal_settings
        )
        sys.stdout.write(RESET + CURSOR_SHOW + ALT_SCREEN_OFF)
        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
