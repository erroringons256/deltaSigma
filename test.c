#include <stdio.h>
#include <stdlib.h>
#include <time.h>


int main()
{
    srand(time(0));
    char byte[131072];
    unsigned int midpoint = RAND_MAX / 2;
    char randBit[1048576];
    for(int i = 0; i < 1048576; i++)
    {
        randBit[i] = (char)(rand() > midpoint);
    }
    printf("Filled random bytes, starting test 1...\n");
    for(int i = 0; i < 16384; i++)
    {
        for(int j = 0; j < 1048576; j++)
        {
            k = j << 3;
            byte = (randBit[j] << 7) | (randBit[j + 1] << 6) | (randBit[j + 2] << 5) | (randBit[j + 3] << 4) | (randBit[j + 4] << 3) | (randBit[j + 5] << 2) | (randBit[j + 6] << 1) | randBit[j + 7];
            
        }
    }
    printf("%u\n", byte + 128);
    printf("Finished test 1! Starting test 2...\n");
    for(int i = 0; i < 16384; i++)
    {
        for(int j = 0; j < 1048576; j += 8)
        {
            byte = (((((((randBit[j] << 1 | randBit[j + 1]) << 1 | randBit[j + 2]) << 1 | randBit[j + 3]) << 1 | randBit[j + 4]) << 1 | randBit[j + 5]) << 1 | randBit[j + 6]) << 1 | randBit[j+7]);
        }
    }
    printf("%u\n", byte + 128);
    printf("Finished test 2!\n");
    return 0;
}