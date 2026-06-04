#!/usr/bin/env python3
import asyncio
import colorsys
import contextlib
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
START_FRAME = "\x1b[?2026h"
END_FRAME = "\x1b[?2026l"
PROMPT = " Press any key to exit "
FRAME_SECONDS = 0.1


def terminal_size() -> tuple[int, int]:
    try:
        size = os.get_terminal_size(sys.stdout.fileno())
    except OSError:
        return 80, 24

    return max(size.columns, 1), max(size.lines, 1)


def foreground_color(color: int) -> str:
    return f"\x1b[38;5;{color}m"


def background_color(color: int) -> str:
    return f"\x1b[48;5;{color}m"


def rgb(red: int, green: int, blue: int) -> int:
    return 16 + 36 * red + 6 * green + blue


def rainbow_plus_grid(width: int, height: int, frame: int) -> str:
    lines = []
    scroll = frame * 0.08

    for y in range(height):
        line = []
        for x in range(width):
            hue = (
                ((x * 2.0) / max(width, 1))
                + ((y * 3.0) / max(height, 1))
                + scroll
            ) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            color = (
                int(red * 5 + 0.5) % 6,
                int(green * 5 + 0.5) % 6,
                int(blue * 5 + 0.5) % 6,
            )
            line.append(
                f"{background_color(rgb(*color))}{foreground_color(rgb(5, 5, 5))} "
            )
        lines.append("".join(line))

    return "\n".join(lines)


def centered_prompt(width: int, height: int) -> str:
    row = max(1, height // 2)
    col = max(1, (width - len(PROMPT)) // 2 + 1)
    return f"{background_color(rgb(0, 0, 0))}{foreground_color(rgb(5, 5, 5))}\x1b[{row};{col}H{PROMPT}{RESET}"


def draw(frame: int) -> None:
    width, height = terminal_size()
    sys.stdout.write(START_FRAME +
                     HOME +
                     rainbow_plus_grid(width, height, frame) +
                     centered_prompt(width, height) +
                     END_FRAME)
    sys.stdout.flush()


async def animate() -> None:
    frame = 0
    while True:
        draw(frame)
        frame += 1
        await asyncio.sleep(FRAME_SECONDS)


async def wait_for_keypress() -> None:
    loop = asyncio.get_running_loop()
    keypress = loop.create_future()

    def on_keypress() -> None:
        if not keypress.done():
            sys.stdin.read(1)
            keypress.set_result(None)

    loop.add_reader(sys.stdin.fileno(), on_keypress)
    try:
        await keypress
    finally:
        loop.remove_reader(sys.stdin.fileno())


async def animate_until_keypress() -> None:
    animation = asyncio.create_task(animate())
    try:
        await wait_for_keypress()
    finally:
        animation.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await animation


def main() -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("ffsparkly needs an interactive ANSI terminal.", file=sys.stderr)
        return 1

    original_terminal_settings = termios.tcgetattr(sys.stdin.fileno())

    try:
        tty.setcbreak(sys.stdin.fileno())
        sys.stdout.write(ALT_SCREEN_ON + CURSOR_HIDE + CLEAR)
        asyncio.run(animate_until_keypress())
    finally:
        termios.tcsetattr(
            sys.stdin.fileno(), termios.TCSADRAIN, original_terminal_settings
        )
        sys.stdout.write(RESET + CURSOR_SHOW + ALT_SCREEN_OFF)
        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
