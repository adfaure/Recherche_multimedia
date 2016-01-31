#include "histogram.h"

void init_histogram(unsigned int k, HISTOGRAM* histogram)
{
  histogram->k = k;
  histogram->img_size = 0;
  histogram->cube = malloc(sizeof(float) * k * k * k);
  for(int i = 0 ; i <  k * k * k; i++)
  {
    histogram->cube[i] = 0.0;
  }
}

void fill_histogram(HISTOGRAM* hist, CIMAGE* img)
{
  hist->img_size = img->ny * img->nx;
  float section = 256.0 /  hist->k;
  for (int j = 0; j < img->ny; j++)
  {
    for (int i = 0; i < img->nx; i++)
    {
      unsigned int x = img->r[i][j] / section;
      unsigned int y = img->g[i][j] / section;
      unsigned int z = img->b[i][j] / section;
      hist->cube[x + (y * hist->k) + (z * hist->k * hist->k)]++;
    }
  }

  for(int i = 0 ; i <  hist->k * hist->k * hist->k; i++) {
    hist->cube[i] = hist->cube[i] / (hist->img_size);
  }
}

void print_histogram(const HISTOGRAM *hist)
{
  for(int b = 0 ; b < hist->k; b++)
  {
    for(int g = 0 ; g < hist->k; g++)
    {
      for(int r = 0 ; r < hist->k; r++)
      {
        printf("%lf ", hist->cube[r + (hist->k*g) +  (hist->k * hist->k * b) ]);
      }
      printf("\n");
    }
    printf("\n");
  }
}

void print_histogram_libsvm(FILE * file, const HISTOGRAM* hist, int concept) {
  fprintf(file, "%d ", concept);
  for(int b = 0 ; b < hist->k; b++)
  {
    for(int g = 0 ; g < hist->k; g++)
    {
      for(int r = 0 ; r < hist->k; r++)
      {
        unsigned int indice = r + (hist->k*g) +  (hist->k * hist->k * b);
        if(hist->cube[indice] != 0) {
          fprintf(file, "%d:%lf ", indice ,hist->cube[indice]);
        }
      }
    }
  }
  fprintf(file, "\n");
}

void free_histogram(HISTOGRAM *hist) {
  hist->k = 0;
  free(hist->cube);
}

int read_img(HISTOGRAM * hist, char url[])
{
  int i,j,n,nx,ny,nb;
  CIMAGE cim;
  read_cimage(url,&cim);
  init_histogram(4, hist);
  fill_histogram(hist, &cim);
  free_cimage(0,&cim);
  return 1;
}

void helloWorld() {
    printf("hello world");
}
