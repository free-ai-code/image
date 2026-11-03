#!/bin/sh
gcc img_view.c -o img-view `sdl2-config --cflags --libs` -lm
