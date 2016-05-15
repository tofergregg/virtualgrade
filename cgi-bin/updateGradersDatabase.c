// updateGradersDatabase.c
// This program will update the .htgroup.dbase file
// one directory up from where it is run

#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int addUser(char *userId);
int removeUser(char *userId);
char *loadUsers(long *filelen);

const char* database = "../.htgroup.dbase";

int main(int argc, char *argv[])
{
        // usage: ./updateGradersDatabase remote_user [add|remove] userid
        if (argc != 4) {
                return -1;
        }

        char *remote_user = argv[1];
        char *operation = argv[2];
        char *userid = argv[3];

        const char* env_remote_user = getenv("REMOTE_USER");
        if (strcmp(remote_user,env_remote_user) != 0){
                // not the right user
                printf("incorrect user\n");
                return -1;
        }

        // sanity check so we don't remove "graders:"
        if (strcmp("graders:",userid) == 0) {
                return -1;
        }

        if (strcmp("add",operation) == 0) {
                return addUser(userid);
        }
        else if (strcmp("remove",operation) == 0) {
                return removeUser(userid);
        }
}

int addUser(char *userId)
{
        long origLen;
        char *origFile = loadUsers(&origLen);
        int userIdLen = strlen(userId);
        // check to see if the last two characters are two newlines
        // If they aren't, we will fail
        if (*(origFile+origLen-2) == '\n'
                        && *(origFile+origLen-2) == '\n') {

                // create a buffer big enough to hold the whole id string
                char *idBuf = malloc(sizeof(char) * (userIdLen + strlen(" \\\n") + 1));
                strcpy(idBuf,userId); // copy original
                strcat(idBuf," \\\n");

                // search for old so we don't add twice
                char *userIdPtr = strstr(origFile,idBuf);

                if (userIdPtr == NULL) { // not present
                        // write back updated file
                        FILE *fp = fopen(database, "w");
                        if (fp != NULL) {
                                // write all but the last newline
                                for (long i=0;i<origLen-1;i++){
                                        fprintf(fp,"%c",*(origFile+i));
                                }
                                fprintf(fp,"%s",idBuf);
                                fprintf(fp,"\n"); // final newline
                                fclose(fp);
                        }
                }
        }
        else {
                free(origFile);
                return -1;
        }
        free(origFile);
        return 0;
}

int removeUser(char *userId)
{
        long origLen;
        int userIdLen = strlen(userId);
        char *origFile = loadUsers(&origLen);
        
        // we will be searching for the userId plus
        // a space,backslash,newline 
      
        // create a buffer big enough to hold the whole id string
        char *idBuf = malloc(sizeof(char) * (userIdLen + strlen(" \\\n") + 1));
        strcpy(idBuf,userId); // copy original
        strcat(idBuf," \\\n");
      
        // locate the original string 
        char *userIdPtr = strstr(origFile,idBuf);   
        if (userIdPtr != NULL) { // found it
                // put a null terminator at that location
                // so we can print both parts of the string,
                // skipping the userId
                *(userIdPtr) = '\0';
                
                // write back updated file
                FILE *fp = fopen(database, "w");
                if (fp != NULL) {
                        fprintf(fp,"%s",origFile);
                        fprintf(fp,"%s",userIdPtr+strlen(idBuf));
                        fclose(fp);
                }
        }

        free(idBuf); 
        free(origFile);
        return 0;
}

// much of this function is from:
// http://stackoverflow.com/a/2029227/561677
char *loadUsers(long *filelen)
{
        char *source = NULL;
        FILE *fp = fopen(database, "r");
        if (fp != NULL) {
            /* Go to the end of the file. */
            if (fseek(fp, 0L, SEEK_END) == 0) {
                /* Get the size of the file. */
                long bufsize = ftell(fp);
                if (bufsize == -1) { /* Error */ }
                *filelen = bufsize;

                /* Allocate our buffer to that size. */
                source = malloc(sizeof(char) * (bufsize + 1));

                /* Go back to the start of the file. */
                if (fseek(fp, 0L, SEEK_SET) != 0) { /* Error */ }

                /* Read the entire file into memory. */
                size_t newLen = fread(source, sizeof(char), bufsize, fp);
                if (newLen == 0) {
                    fputs("Error reading file", stderr);
                } else {
                    source[newLen++] = '\0'; /* Just to be safe. */
                }
            }
            fclose(fp);
        }
        return source;
        //free(source); /* Don't forget to call free() later! */
}

