#include "lock.h"

int main(int argc, char **argv)
{
        int fd;
        int i = 0;

        fd = lock_init();
        printf("fd=%d\n", fd);
        if(fd < 0)
        {
                printf("初始化锁失败\n");
                return fd;
        }

        while(1) {
                open_door(fd);
                printf("-----------开锁----------\n");
                i = 0;
                while(i < 10) {
                        printf("锁芯状态:       %s\n", getLockState(fd) ? "开" : "关");
                        printf("门状态:         %s\n", getDoorState(fd) ? "开" : "关");
                        sleep(1);
                        i++;
                }
                close_door(fd);
                printf("-----------关锁----------\n");
                i = 0;
                while(i < 10) {
                        printf("锁芯状态:       %s\n", getLockState(fd) ? "开" : "关");
                        printf("门状态:         %s\n", getDoorState(fd) ? "开" : "关");
                        sleep(1);
                        i++;
                }
        }
        lock_deinit(fd);
        return 0;
}

