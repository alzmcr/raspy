import termios, sys, os

'''
    # TODO: integration with key press and release?
    # is this even feasible via SSH?
    def terminator(*args): pass
    import signal
    signal.signal(signal.SIGALRM, terminator)
    TIMEOUT = .35
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT, TIMEOUT)
    c = mapping(getkey())
'''

EXIT_CHAR = '\n'

def getkey():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    c = None
    try:
        c = os.read(fd, 1)
    except:
        return c
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    return c


def keypad(obj, mapping):
    while True:
        # get command and make it lower case
        c = getkey().lower()
        if c == EXIT_CHAR:
            # exit function
            break

        try:
            # map command
            c = mapping[c]
            # execute command
            if c is not None:
                eval('obj.%s()' % c)
        except KeyError:
            # unmapped command
            print 'command unknown'
        except Exception as e:
            print e, e.message

    return -1

