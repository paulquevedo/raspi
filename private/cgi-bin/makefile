TARGET = server

C_PIECES = server

C_FLAGS = -g -Wall -Wno-format -O1
LIBS = -lfcgi

CC = gcc
LD = ld
C_FILES = $(C_PIECES:%=%.c)
O_FILES = $(C_FILES:%.c=%.o)

TARGET_DIR = ../../public/cgi-bin/

all: $(TARGET).fcgi
	@echo
	$(CC) $(C_FLAGS) $(C_FILES) $(LIBS) -o $(TARGET).fcgi
	cp $(TARGET).fcgi $(TARGET_DIR)
	@$(CC) --version

restart:
	@echo
	@echo Restarting LightTPD...
	@echo
	sudo /etc/init.d/lighttpd restart

clean:
	@echo
	@echo Cleaning up...
	@echo
	rm $(TARGET).fcgi
