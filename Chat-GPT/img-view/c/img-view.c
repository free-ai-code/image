// img_view.c
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include <SDL2/SDL.h>
#include <stdio.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s imagefile\n", argv[0]);
        return 1;
    }

    int w, h, n;
    unsigned char *pixels = stbi_load(argv[1], &w, &h, &n, 4);
    if (!pixels) {
        fprintf(stderr, "failed to load image: %s\n", stbi_failure_reason());
        return 1;
    }

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        stbi_image_free(pixels);
        return 1;
    }

    SDL_Window *win = SDL_CreateWindow(
        "img-view",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        w, h,
        SDL_WINDOW_RESIZABLE
    );

    if (!win) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
        stbi_image_free(pixels);
        SDL_Quit();
        return 1;
    }

    SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!ren) {
        fprintf(stderr, "SDL_CreateRenderer failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        stbi_image_free(pixels);
        SDL_Quit();
        return 1;
    }

    SDL_Surface *surf = SDL_CreateRGBSurfaceWithFormatFrom(
        pixels, w, h, 32, w * 4, SDL_PIXELFORMAT_RGBA32
    );

    SDL_Texture *tex = SDL_CreateTextureFromSurface(ren, surf);
    SDL_FreeSurface(surf);

    if (!tex) {
        fprintf(stderr, "SDL_CreateTextureFromSurface failed: %s\n", SDL_GetError());
        SDL_DestroyRenderer(ren);
        SDL_DestroyWindow(win);
        stbi_image_free(pixels);
        SDL_Quit();
        return 1;
    }

    int running = 1;
    SDL_Event e;

    while (running) {
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) running = 0;
            if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) running = 0;
        }

        int win_w, win_h;
        SDL_GetWindowSize(win, &win_w, &win_h);

        SDL_RenderClear(ren);
        SDL_Rect dst = {0, 0, win_w, win_h};
        SDL_RenderCopy(ren, tex, NULL, &dst);
        SDL_RenderPresent(ren);

        SDL_Delay(16);
    }

    SDL_DestroyTexture(tex);
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    stbi_image_free(pixels);
    SDL_Quit();
    return 0;
}
