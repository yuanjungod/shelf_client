#ifndef _LOCK_H
#define _LOCK_H

#include <stdio.h>
#include <fcntl.h>              /* open() */
#include <sys/types.h>          /* open() */
#include <sys/stat.h>           /* open() */
#include <asm/ioctl.h>
#include <linux/parport.h>
#include <linux/ppdev.h>

#include <stdbool.h>
#include <sys/io.h>
#include <unistd.h>//sleep
#include <sys/ioctl.h>


int lock_init(void);

int lock_deinit(int fd);

int open_door(int fd);

int close_door(int fd);

bool getLockState(int fd);

bool getDoorState(int fd);

#endif //_LOCK_H