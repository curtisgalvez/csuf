#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/stat.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define DATE_MAX_CHARS 25
#define NUMBER_OF_MESSAGES 5
#define MAX_NUMBER_OF_FILES 5
#define MAX_MESSAGE_LENGTH 250

char *fileName[MAX_NUMBER_OF_FILES];
char messageArray[NUMBER_OF_MESSAGES][MAX_MESSAGE_LENGTH];
int delay = 0;
int totalFiles = 0;
int errors[MAX_NUMBER_OF_FILES] = {};
int warnings[MAX_NUMBER_OF_FILES] = {};
int totalMsg[2] = {};
pthread_mutex_t msgMutex;
pthread_mutex_t countMutex;
void *reader(void *i);
void *report(void *i);
void *formatMsg(int index, int error, int warning, int displayMsg);
void *dirtyHack(char msg[]);

/*
compile: gcc logmon.c -lpthread
sources:
    date format: genlog.c
        provided by professor avery
    pthread:
        http://stackoverflow.com/questions/1662909/undefined-reference-to-pthread-create-in-linux
        http://stackoverflow.com/questions/19232957/pthread-create-passing-an-integer-as-the-last-argument
        http://stackoverflow.com/questions/18756836/how-to-keep-a-thread-alive-after-the-main-process-exited
        https://computing.llnl.gov/tutorials/pthreads/
        Operating System Concepts book
    file size and time modified:
        http://linux.die.net/man/2/stat
        http://stackoverflow.com/questions/5283120/date-comparison-to-find-which-is-bigger-in-c
    reading files and comparing strings:
        http://www.zentut.com/c-tutorial/c-read-text-file/
        http://www.cplusplus.com/reference/cstdio/fseek/
        http://www.cplusplus.com/reference/cstring/strstr/
*/

int main(int argc, char *argv[])
{
    int index = 0;
    pthread_t tid;
    pthread_attr_t attr;

    if (argc < 3)
    {
        printf("error: arg! not enough args.\n");
        printf("logmon will monitor up to 5 files\n");
        printf("usage: ./logmon [NUM] [FILE(S)]\n");
        return 1;
    }
    else if (argc > 7)
    {
        printf("error: hold up, i can only monitor up to five files!\n");
        return 1;
    }
    else
    {
        delay = atoi(argv[1]);
        //argc index starts at ./logmon
        //all the files that need to be read
        for (index=0; index < argc-2; index++)
        {
            fileName[index] = argv[index+2];
            totalFiles++;
            //thanks SO!
            int *arg = malloc(sizeof(*arg));
            *arg = index;
            pthread_attr_init(&attr);
            pthread_create(&tid, &attr, reader, arg);
        }
    }
    //watch all the things
    pthread_create(&tid, &attr, report, argv[0]);
    //wake me up before you go-go
    pthread_join(tid, NULL);

    return 0;
}

void *dirtyHack(char msg[])
{
    int index = 0, msgAdded = 0;
    if (strlen(messageArray[NUMBER_OF_MESSAGES-1]) == 0)
    {
        while (index < NUMBER_OF_MESSAGES && msgAdded == 0)
        {
            if (strlen(messageArray[index]) == 0)
            {
                strcpy(messageArray[index], msg);
                msgAdded = 1;
            }
            index++;
        }
    }
    else
    {
        for (index=0; index < NUMBER_OF_MESSAGES; index++)
        {
            if (strlen(messageArray[index]) != 0 && strlen(messageArray[index+1]) != 0)
            {
                strcpy(messageArray[index], messageArray[index+1]);
            }
        }
        strcpy(messageArray[NUMBER_OF_MESSAGES-1], msg);
    }
    return 0;
}

void *reader(void *i)
{
    FILE * fp;
    int index = *(int *)i;
    free(i);
    double seconds;
    char str[MAX_MESSAGE_LENGTH];
    char msg[MAX_MESSAGE_LENGTH];
    struct stat s;
    time_t modifiedTime;
    off_t fileSize = 0, currentSize = 0, seekPos;

    fp = fopen(fileName[index], "r");
    if (fp == NULL)
        printf("error: %s", fileName[index]);

    //get modified time of file
    stat(fileName[index], &s);
    modifiedTime = s.st_mtime;
    //wait at EOF for new changes ^.~
    fseek(fp, s.st_size, SEEK_SET);
    setbuf(stdout, NULL);
    for (;;)
    {
        //if the file has been modified check it before sleeping
        stat(fileName[index], &s);
        seconds = difftime(s.st_mtime, modifiedTime);
        if (seconds > 0) // || fileSize == 0)
        {
            modifiedTime = s.st_mtime;
            fileSize = s.st_size;
            seekPos = currentSize - fileSize;
            fseek(fp, seekPos, SEEK_SET);
            while (fgets(str, MAX_MESSAGE_LENGTH, fp) != NULL)
            {
                sprintf(msg, "%s: %s", fileName[index], str);
                pthread_mutex_lock(&msgMutex);
                dirtyHack(msg);
                pthread_mutex_unlock(&msgMutex);
                if (strstr(str, "ERROR"))
                {
                    pthread_mutex_lock(&countMutex);
                    totalMsg[0] += 1;
                    errors[index] += 1;
                    pthread_mutex_unlock(&countMutex);
                }
                else if (strstr(str, "WARNING"))
                {
                    pthread_mutex_lock(&countMutex);
                    totalMsg[1] += 1;
                    warnings[index] += 1;
                    pthread_mutex_unlock(&countMutex);
                }
            }
        }
        modifiedTime = s.st_mtime;
        currentSize = s.st_size;
        sleep(1);
    }
    fclose(fp);
    pthread_exit(0);
}

void *report(void *i)
{
    char date[DATE_MAX_CHARS];
    int index;
    struct tm *timestamp;
    time_t currentTime;

    printf("I always feel like somebody's watching me...\n");
    sleep(delay);
    for (;;)
    {
        currentTime = time(NULL);
        timestamp = localtime(&currentTime);
        strftime(date, DATE_MAX_CHARS, "%F %T", timestamp);
        printf("\n\n%s\n", date);
        for (index=0; index < totalFiles; index++)
        {
            //print count for individual file
            formatMsg(index, errors[index], warnings[index], 0);
        }
        //print total count
        formatMsg(index, totalMsg[0], totalMsg[1], 1);
        printf("\nRecent activity\n");
        if (strlen(messageArray[0]) == 0)
            printf("Nothing to see here...\n");
        else
        {
            for (index=0; index < NUMBER_OF_MESSAGES; index++)
            {
                if (strlen(messageArray[index]) != 0)
                    printf("%s", messageArray[index]);
            }
        }
        sleep(delay);
    }
    pthread_exit(0);
}

//use this to make messages pretty with error/errors/etc based on count
void *formatMsg(int index, int error, int warning, int displayMsg)
{
    char errorMsg[7];
    char warningMsg[8];
    if (error > 1 || error == 0)
        strcpy(errorMsg, "errors");
    else
        strcpy(errorMsg, "error");
    if (warning > 1 || warning == 0)
        strcpy(warningMsg, "warnings");
    else
        strcpy(warningMsg, "warning");
    if (displayMsg == 0)
        printf("%s: %d %s, %d %s\n", fileName[index], errors[index], errorMsg, warnings[index], warningMsg);
    else
        printf("Total: %d %s, %d %s\n", totalMsg[0], errorMsg, totalMsg[1], warningMsg);
    return 0;
}