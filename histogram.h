#ifndef __HISTORGRAM__H
#define __HISTORGRAM__H

#include "rdjpeg.h"

#include <stdlib.h>

typedef struct {        /* image couleur         */
  unsigned int k;
  unsigned int img_size;
  float* cube;
} HISTOGRAM;

void init_histogram(unsigned int, HISTOGRAM*);
void fill_histogram(HISTOGRAM*, CIMAGE*);
void free_histogram(HISTOGRAM*);
void print_histogram(const HISTOGRAM*);
void print_histogram_libsvm(const HISTOGRAM*, int concept);
#endif
