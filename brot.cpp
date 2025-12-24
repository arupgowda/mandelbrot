#include <chrono>
#include <iostream>
#include <stdio.h>
#include <math.h>

class Mandelbrot {
    const int MAX_ITER = 2048;
    const int LINEARITY = 8;

    const double offset = log(LINEARITY);
    const double scale = 255.9/(log(MAX_ITER + LINEARITY) - offset);

    //
    // returns 0 if inside the mandelbrot set and the number of iterations until
    // divergence is detected otherwise
    //
    int brot_iters(double x, double y)
    {
       //
       // z[i] = z[i-1]*z[i-1] + (x,y), z[0] = (0,0)
       //
       // compute z[1] = (0,0)*(0,0) + (x,y)
       //
       double zr = x, zi = y;

       for ( int i=1; i<MAX_ITER; ++i )
       {
          // compute z[i+1], but first, is | z[i] | > 2?
          double a = zr*zr;
          double b = zi*zi;
          if ( a+b>4.0 ) return i;
          zi = 2.0*zr*zi + y;
          zr = a - b + x;
       }
       return 0;
    }

public:
    void line_of_brot(double x, double y, double pitch, int samples,
                      int columns, unsigned char *buffer)
    {
       double color_scale = 1.0/(samples*samples);
       double delta = pitch/samples;
       double y0 = y - 0.5*(pitch - delta);
       double x0, x1, y1, r, g, b;
       int i, j, k;
       for ( i=0; i<columns; ++i)
       {
          x0 = x + i*pitch - 0.5*(pitch - delta);
          r = g = b = 0.0;
          for ( j = 0, y1 = y0; j<samples; ++j, y1 += delta )
          {
             for ( k = 0, x1 = x0; k<samples; ++k, x1 += delta )
             {
                int n = brot_iters(x1,y1);
                if ( n > 0 )
                {  double Y = (log(n + LINEARITY)-offset) * scale;
                   r += Y;
                   g += Y;
                   b += 128.0 + 0.5*Y;
                }
             }
          }
          r *= color_scale;
          g *= color_scale;
          b *= color_scale;
          *buffer++ = (r<0? 0 : r >255.0? 255 : (unsigned char)r);
          *buffer++ = (g<0? 0 : g >255.0? 255 : (unsigned char)g);
          *buffer++ = (b<0? 0 : b >255.0? 255 : (unsigned char)b);
       }
    }
};

extern "C" {
    Mandelbrot* brot_new() {
        return new Mandelbrot();
    }

    void generate(
            Mandelbrot* brot,
            double x, double y,
            double pitch,
            int samples,
            int columns,
            unsigned char *buffer) {
        brot->line_of_brot(x, y, pitch, samples, columns, buffer);
    }

    void brot_delete(Mandelbrot* brot) {
        delete brot;
    }
}

const int WID  = 1024;
const int HGT  = 1024;
const int SAMPLES = 4;

const double X_MIN = -0.60;
const double Y_MIN =  0.48;
const double PITCH =  (0.15)/WID;

unsigned char buffer[HGT][3*WID];

int main(int argc, char *argv[])
{
    Mandelbrot* brot = brot_new();
    
    using std::chrono::steady_clock;
    using std::chrono::seconds;
    using std::chrono::duration_cast;

    const auto start = steady_clock::now();
    for ( int j=0; j<HGT; ++j)
    {
        brot->line_of_brot(X_MIN, Y_MIN + j*PITCH, PITCH, SAMPLES, WID, buffer[j]);
    }
    const auto end = steady_clock::now();
    const auto elapsed = duration_cast<seconds>(end - start);
    std::cout << "C++ execution took " << elapsed.count() << " seconds\n";

    FILE *ppm = fopen(argc>1? argv[1]:"brot.ppm","w");
    if ( ppm == NULL ) ppm = stdout;

    fprintf(ppm,"P6\n#Mandelbrot set\n%d %d\n255\n",WID,HGT);

    for ( int j=HGT-1; j>=0; --j )
    {
        fwrite(buffer[j],3,WID,ppm);
    }

    fclose(ppm);
}
