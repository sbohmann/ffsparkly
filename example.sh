#!/bin/sh

set_color() {
    foreground_color="$1"
    background_color="$2"

    printf "\e[38;5;%dm\e[48;5;%dm" "$foreground_color" "$background_color"
}

reset_color() {
    printf "\e[0m"
}

traditional_16_colors() {
    index=0
    while [ $index -lt 16 ]
    do
        if [ $index -eq 8 ]; then echo; fi
        foreground_color=15
        if [ $index -eq  7 ] || [ $index -gt 8 ]
        then
            foreground_color=0
        fi
        set_color $foreground_color $index
        printf " %2d " $index
        reset_color
        index=$((index + 1))
    done
    echo
}

rgb_colors() {
    r=0
    while [ $r -lt 6 ]
    do
        g=0
        while [ $g -lt 6 ]
        do
            b=0
            while [ $b -lt 6 ]
            do
                rgb_index=$((36 * r + 6 * g + b))
                index=$((rgb_index + 16))
                foreground_color=15
                if [ $g -gt 2 ]
                then
                  foreground_color=0
                fi
                set_color $foreground_color $index
                printf " %d %d %d %3d %3d " $r $g $b $rgb_index $index
                b=$((b + 1))
            done
            reset_color
        printf "\n"
            g=$((g + 1))
        done
        r=$((r + 1))
    done
    echo
}

additional_24_gray_tones() {
    offset=0
    while [ $offset -lt 24 ]
    do
        if [ $((offset % 8)) -eq 0 ]; then echo; fi
        index=$((offset + 232))
        foreground_color=15
        if [ $offset -ge  12 ]
        then
            foreground_color=0
        fi
        set_color $foreground_color $index
        printf " %2d %3d " $offset $index
        reset_color
        offset=$((offset + 1))
    done
    echo
}

echo "\n16 Colors. Label: absolute index \n"

traditional_16_colors

echo "\nRGB Colors. Labels: r, g, b, relative offset, absolute index\n"

rgb_colors

echo "\n24 Gray Tones. Labels: relative offset, absolute index \n"

additional_24_gray_tones

echo

echo
