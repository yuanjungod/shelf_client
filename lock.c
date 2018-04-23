#include "lock.h"


#define DEVICE "/dev/parport0"
#define BASEADDR 0x378
#define STATUSADDR 0x379

int lock_init(void)
{
        int fd;
        unsigned char data;

        if ((fd=open(DEVICE, O_RDWR)) < 0) {
                fprintf(stderr, "can not open %s\n", DEVICE);
                return -1;
        }
        if (ioctl(fd, PPCLAIM)) {
                perror("PPCLAIM");
                close(fd);
                return -2;
        }

        int mode = IEEE1284_MODE_ECP;
        int res = ioctl(fd, PPSETMODE, &mode);
        //setto output direction
        data = 0;
        res = ioctl(fd, PPDATADIR, data);
        return fd;
}

int lock_deinit(int fd)
{
        if(ioctl(fd, PPRELEASE)) {
                perror("PPCLAIM");
                close(fd);
                return -2;
        }
        close(fd);
        return 0;
}

int open_door(int fd)
{
        unsigned char data = 0x01;
        //write_data(fd, 0x01);
        return (ioctl(fd, PPWDATA, &data));
}

int close_door(int fd)
{
        unsigned char data = 0x00;
        //write_data(fd, 0x00);
        return (ioctl(fd, PPWDATA, &data));
}

bool getLockState(int fd)
{
        int val;

        ioctl(fd, PPRSTATUS, &val);
        return ((val & PARPORT_STATUS_SELECT)==PARPORT_STATUS_SELECT) ? false : true;
}

bool getDoorState(int fd)
{
        int val;

        ioctl(fd, PPRSTATUS, &val);
        return ((val & PARPORT_STATUS_PAPEROUT)==PARPORT_STATUS_PAPEROUT) ? false : true;
}

///////////////////////////////////////////////////unused//////////////////////////////////////////
/* example how to write data */
int write_data(int fd, unsigned char data)
{
        return (ioctl(fd, PPWDATA, &data));
}

/* example how to read 8 bit from the data lines */
int read_data(int fd)
{
        unsigned char data;

        int mode = IEEE1284_MODE_ECP;
        int res=ioctl(fd, PPSETMODE, &mode);    /* ready to read ? */
        mode=255;
        res=ioctl(fd, PPDATADIR, &mode);        /* switch output driver off */
        printf("ready to read data !\n");
        fflush(stdout);
        sleep(10);
        res=ioctl(fd, PPRDATA, &data);  /* now fetch the data! */
        printf("data=%02x\n", data);
        fflush(stdout);
        sleep(10);
        data=0;
        res=ioctl(fd, PPDATADIR, data);
        return 0;
}

/* example how to read the status lines. */
int status_pins(int fd)
{
        int val;

        ioctl(fd, PPRSTATUS, &val);
        val^=PARPORT_STATUS_BUSY; /* /BUSY needs to get inverted */
        printf("/BUSY  = %s\n",
                ((val & PARPORT_STATUS_BUSY)==PARPORT_STATUS_BUSY)?"HI":"LO");
        printf("ERROR  = %s\n",
                ((val & PARPORT_STATUS_ERROR)==PARPORT_STATUS_ERROR)?"HI":"LO");
        printf("SELECT = %s\n",
                ((val & PARPORT_STATUS_SELECT)==PARPORT_STATUS_SELECT)?"HI":"LO");
        printf("PAPEROUT = %s\n",
                ((val & PARPORT_STATUS_PAPEROUT)==PARPORT_STATUS_PAPEROUT)?"HI":"LO");
        printf("ACK = %s\n",
                ((val & PARPORT_STATUS_ACK)==PARPORT_STATUS_ACK)?"HI":"LO");
        return 0;
}

