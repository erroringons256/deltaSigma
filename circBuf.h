#include <stdlib.h>
typedef struct rBuf
{
    double* content;
    unsigned int size;
    unsigned int offset;
} rBuffer;

void initRBuffer(rBuffer* rBuf, unsigned int bufferSize, double initialValue)
{
    rBuf->content = (double *)malloc(bufferSize * sizeof(double));
    rBuf->size = bufferSize;
    rBuf->offset = 0;
    for(int i = 0; i < bufferSize; i++)
    {
        rBuf->content[i] = initialValue;
    }
}

void rollRBuffer(rBuffer* rBuf)
{
    rBuf->offset = (rBuf->offset + 1) % rBuf->size;
}

double getRBufferElFromStart(rBuffer* rBuf, unsigned int i)
{
    return rBuf->content[(i + rBuf->offset) % rBuf->size];
}

double getRBufferElFromEnd(rBuffer* rBuf, unsigned int i)
{
    return rBuf->content[(rBuf->size - 1 - i + rBuf->offset) % rBuf->size];
}

void setRBufferElFromStart(rBuffer* rBuf, unsigned int i, double el)
{
    rBuf->content[(i + rBuf->offset) % rBuf->size] = el;
}

void setRBufferElFromEnd(rBuffer* rBuf, unsigned int i, double el)
{
    rBuf->content[(rBuf->size - 1 - i + rBuf->offset) % rBuf->size] = el;
}