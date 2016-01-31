#ifndef __HISTORGRAM__H
#define __HISTORGRAM__H

#include <stdio.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>

#include "rdjpeg.h"


typedef struct {        /* image couleur         */
  unsigned int k;
  unsigned int img_size;
  float* cube;
} HISTOGRAM;

void helloWorld();
int read_img(HISTOGRAM * hist, char url[]);
void init_histogram(unsigned int, HISTOGRAM*);
void fill_histogram(HISTOGRAM*, CIMAGE*);
void free_histogram(HISTOGRAM*);
void print_histogram(const HISTOGRAM*);
void print_histogram_libsvm(FILE* file, const HISTOGRAM* hist, int concept);

#endif
