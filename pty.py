import os
import pty
import select
import sys
import termios
import tty


def run_terminal():
    # 1. Fork a child process with a pseudo-terminal (PTY)
    pid, fd = pty.fork()

    if pid == 0:
        # --- CHILD PROCESS ---
        # Replace the child process with a shell (e.g., bash)
        shell = os.environ.get("SHELL", "/bin/bash")
        os.execlp(shell, shell)
    else:
        # --- PARENT PROCESS ---
        # Put the host terminal into raw mode so keypresses pass directly
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())

            while True:
                # Watch both stdin (user keyboard) and fd (shell output)
                r, _, _ = select.select([sys.stdin, fd], [], [])

                if sys.stdin in r:
                    # User typed something -> send to shell
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    os.write(fd, data)

                if fd in r:
                    # Shell output something -> draw to screen
                    try:
                        data = os.read(fd, 1024)
                        if not data:
                            break
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        break
        finally:
            # Restore host terminal settings on exit
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    print("Starting Python Terminal Emulator... (Type 'exit' to quit)")
    run_terminal()

