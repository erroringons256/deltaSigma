#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "circBuf.h"

#define FLOAT_SIZE sizeof(float)
#define CHANNELS 2
#define BLOCK_SIZE 262144
#define NOISE_FACTOR 2 / (double)(RAND_MAX)
// #define GAIN 0.505134 // 6 dB
#define GAIN 0.71
#define CLIP_BUF 4096.0

void deltaSigmaEncode(unsigned int, float*, char*, rBuffer*, rBuffer*, rBuffer*, rBuffer*);
double randFloat();
double clip(double, double);

/*
Psychoacoustically shaped 16x oversampling filter
double const x1Filter[6] = {0.6746, -3.07505182, 5.650604334847973, -5.2260953627290405, 2.4302826697122626, -0.45401489672137707};
double const y1Filter[6] = {5.8906, -14.50786442,19.122358320896, -14.226543299142167, 5.664459499781069, -0.9430107575337243};
*/
/*
Another psychoacoustically shaped 16x oversampling filter with exact DC reproduction
double const x1Filter[5] = {0.808, -2.849516, 3.831211344, -2.325031307912, 0.538834905385377};
double const y1Filter[5] = {4.882, -9.557026, 9.37729012, -4.611588786, 0.909324666};
*/

/* Psychoacoustically shaped 32x oversampling filter with exact DC reproduction
double const x1Filter[7] = {0.75, -4.1914, 9.7942615, -12.248500635, 8.6462927029, -3.266966849567, 0.5163307393563};
double const y1Filter[7] = {6.95, -20.70815, 34.290483, -34.080448795, 20.3299481085, -6.739731837525, 0.957899524025};
*/

/* //(Better psychoacoustic target) psychocacoustically shaped 8x oversampling filter with exact DC reproduction
double const x1Filter[3] = {0.875, -1.377294, 0.611110102};
double const y1Filter[3] = {2.93, -2.887146, 0.957146};
*/

/*
double const x1Filter[5] = {0.804, -2.84829, 3.845593832, -2.3426989048, 0.54459049718};
double const y1Filter[5] = {4.898, -9.620994, 9.473967272, -4.677073074, 0.926099802};
*/

//double const x1Filter[3] = {0.82, -1.3064, 0.552466};
//double const y1Filter[3] = {2.96, -2.9285, 0.9685};
//double const x1Filter[5] = {0.79, -2.80495, 3.769196, -2.26857528, 0.515496112};
//double const y1Filter[5] = {4.93, -9.73265, 9.617532, -4.7571438, 0.9422618};
//double const x2Filter[1] = {1};
//double const y2Filter[1] = {0};

// double const x1Filter[3] = {0.88656641037206, -1.526248466712514, 0.66072590621561};
// double const y1Filter[3] = {2.39, -1.9204, 0.51821};
// double const x2Filter[3] = {0.88656641037206, -1.669880967980196, 0.815070533533027};
// double const y2Filter[2] = {1.81, -0.864821};


double const x1Filter[4] = {1.12766, -2.7674304173, 2.313785317517516, -0.657061676419315};
double const y1Filter[4] = {2.72698, -2.8368428018, 1.328058170445298, -0.235324196346487};
double const x2Filter[1] = {1};
double const y2Filter[1] = {0};

int main()
{
    srand(time(0));
    float* inBuffer = malloc(BLOCK_SIZE * FLOAT_SIZE * CHANNELS); // Allocate input and output buffers for reading/writing on heap.
    char* outBuffer = malloc(BLOCK_SIZE * CHANNELS);
    rBuffer x1Buffer[CHANNELS]; // Allocate and initialise quantitisation error buffers for noise shaping filter. The filter even in a worst case scenario should not exceed ~100 samples, and as such, this can be allocated on the stack.
    rBuffer x2Buffer[CHANNELS];
    rBuffer y1Buffer[CHANNELS];
    rBuffer y2Buffer[CHANNELS];
    for(unsigned int i = 0; i < CHANNELS; i++)
    {
        initRBuffer(x1Buffer + i, 4, 0.0);
        initRBuffer(x2Buffer + i, 1, 0.0);
        initRBuffer(y1Buffer + i, 4, 0.0);
        initRBuffer(y2Buffer + i, 1, 0.0);
    }
    FILE* fileHandle = fopen("/home/user/004.raw", "rb");
    if(fileHandle == 0)
    {
        printf("Could not open input file!\n");
        return(1);
    }
    FILE* fileHandle2 = fopen("/home/user/004_copy.raw", "wb");
    if(fileHandle2 == 0)
    {
        printf("Could not open output file!\n");
        return(1);
    }
    unsigned int samplesRead = 0; // Quantitise audio file chunk by chunk, with handling for the last chunk being of a different size.
    do
    {
        samplesRead = fread(inBuffer, FLOAT_SIZE * CHANNELS, BLOCK_SIZE, fileHandle);
        deltaSigmaEncode(samplesRead, inBuffer, outBuffer, x1Buffer, y1Buffer, x2Buffer, y2Buffer);
        fwrite(outBuffer, samplesRead * CHANNELS, 1, fileHandle2);
    } while (samplesRead == BLOCK_SIZE);
    fclose(fileHandle);
    fclose(fileHandle2);
    return(0);
}

inline void deltaSigmaEncode(unsigned int blockSize, float* inBuffer, char* outBuffer, rBuffer* x1Buffer, rBuffer* y1Buffer, rBuffer* x2Buffer, rBuffer* y2Buffer) // This is where the noise shaping magic happens.
{
    char q = 0; // Temporary buffer variable to store quantitised state before further encoding into output file type.
    double u = 0; // Temporary buffer variable to store difference between input signal and filter output
    double buf; //Temporary buffer variable to store temporary output of filter sum.
    for(unsigned int offset = 0; offset < blockSize; offset++)
    {
        for(unsigned int channel = 0; channel < CHANNELS; channel++)
        {
            buf = 0.0;
            inBuffer[CHANNELS * offset + channel] = GAIN * (inBuffer[CHANNELS * offset + channel]);
            u = inBuffer[CHANNELS * offset + channel] - getRBufferElFromEnd(y2Buffer + channel, 0);
            q = (char)(u + 0.1 * randFloat() >= 0.0f); 
            outBuffer[CHANNELS * offset + channel] = 254 * q + 1;

            setRBufferElFromStart(x1Buffer + channel, 0, 2 * (double)q - 1 - u + 0.01 * randFloat());
            rollRBuffer(x1Buffer + channel);

            for(int i = 0; i < 4; i++)
            {
                buf += x1Filter[i] * getRBufferElFromEnd(x1Buffer + channel, i);
            }
            for(int i = 0; i < 4; i++)
            {
                buf += y1Filter[i] * getRBufferElFromEnd(y1Buffer + channel, i);
            }

            setRBufferElFromStart(y1Buffer + channel, 0, buf);
            rollRBuffer(y1Buffer + channel);            
            setRBufferElFromStart(x2Buffer + channel, 0, buf);
            rollRBuffer(x2Buffer + channel);
            buf = 0.0;

            for(int i = 0; i < 1; i++)
            {
                buf += x2Filter[i] * getRBufferElFromEnd(x2Buffer + channel, i);
            }
            for(int i = 0; i < 1; i++)
            {
                buf += y2Filter[i] * getRBufferElFromEnd(y2Buffer + channel, i);
            }

            setRBufferElFromStart(y2Buffer + channel, 0, buf);
            rollRBuffer(y2Buffer + channel);
        }
    }
}

inline double randFloat() // Simply a convenience function to return a random float value between -1 and 1.
{
    return NOISE_FACTOR * (double)(rand()) - 1;
}

inline double clip(double x, double lim)
{
    return (lim <= x) * lim - (-lim >= x) * lim + (lim > x && -lim < x) * x;
}