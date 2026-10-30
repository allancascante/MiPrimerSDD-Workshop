import os
from io import StringIO
from pathlib import Path
import subprocess
import sys
import signal
import time
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


class StartupTests(unittest.TestCase):
    def test_known_cursorless_terminal_rejected_before_app_start(self):
        from curso_pswe_07.__main__ import main

        with TemporaryDirectory() as home, \
             patch.dict(os.environ, {"TERM": "dumb", "HOME": home, "USERPROFILE": home}), \
             patch("sys.stdin.isatty", return_value=True), \
             patch("sys.stdout.isatty", return_value=True), \
             patch("sys.stderr", new_callable=StringIO) as stderr, \
             patch("curso_pswe_07.__main__.TaskApp") as app:
            app.return_value.return_code = 0
            self.assertEqual(main(), 2)
            self.assertIn("cursor", stderr.getvalue())
            app.assert_not_called()
            self.assertFalse((Path(home) / ".curso-pswe-07").exists())

    def test_redirected_startup_rejected_without_file_creation(self):
        with TemporaryDirectory() as home:
            result = subprocess.run(
                [sys.executable, "-m", "curso_pswe_07"],
                input="", capture_output=True, text=True,
                env={**os.environ, "HOME": home, "USERPROFILE": home}, timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("interactive terminal", result.stderr)
            self.assertFalse((Path(home) / ".curso-pswe-07").exists())


@unittest.skipUnless(os.name == "posix", "POSIX PTY restoration is unavailable on Windows")
class TerminalLifecycleTests(unittest.TestCase):
    def run_terminal(self, home, interrupt=None, create=False, expected_title=None, fault=False):
        import fcntl
        import pty
        import select
        import struct
        import termios

        master, slave = pty.openpty()
        before = termios.tcgetattr(slave)
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
        command = [sys.executable, "-m", "curso_pswe_07"]
        if fault:
            command = [sys.executable, "-c", (
                "from unittest.mock import patch\n"
                "from curso_pswe_07.__main__ import main\n"
                "with patch('curso_pswe_07.tui.TaskView.compose', "
                "side_effect=RuntimeError('terminal fault probe')):\n"
                "    raise SystemExit(main())\n"
            )]
        process = subprocess.Popen(
            command, stdin=slave, stdout=slave, stderr=slave,
            env={**os.environ, "HOME": home, "USERPROFILE": home, "TERM": "xterm-256color"},
            start_new_session=True,
        )
        output = bytearray()

        def wait_for(needle):
            deadline = time.monotonic() + 12
            while needle not in output and time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    output.extend(os.read(master, 65536))
                if process.poll() is not None:
                    break
            self.assertTrue(needle in output, output[-2000:].decode(errors="replace"))

        try:
            wait_for(b"terminal fault probe" if fault else b"Add task")
            if expected_title:
                wait_for(expected_title.encode())
            if create:
                os.write(master, b"\r")
                wait_for(b"Description")
                os.write(master, b"Persisted from PTY\t\t\r")
                wait_for(b"Saved.")
            if fault:
                pass
            elif interrupt == "signal":
                process.send_signal(signal.SIGINT)
            else:
                os.write(master, b"\x03" if interrupt == "key" else b"\x11")
            deadline = time.monotonic() + 12
            while process.poll() is None and time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    output.extend(os.read(master, 65536))
            process.wait(timeout=1)
            while select.select([master], [], [], 0.1)[0]:
                output.extend(os.read(master, 65536))
            self.assertEqual(process.returncode, 1 if fault else 130 if interrupt else 0)
            self.assertEqual(termios.tcgetattr(slave), before)
            self.assertIn(b"\x1b[?25h", output)
            self.assertIn(b"\x1b[?1049l", output)
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            os.close(master)
            os.close(slave)

    def test_exit_and_interrupt_restore_terminal(self):
        for interrupt in (None, "key", "signal"):
            with self.subTest(interrupt=interrupt), TemporaryDirectory() as home:
                self.run_terminal(home, interrupt)
                self.assertFalse((Path(home) / ".curso-pswe-07" / "tasks.json").exists())

    def test_two_process_save_and_reopen(self):
        with TemporaryDirectory() as home:
            self.run_terminal(home, create=True)
            self.run_terminal(home, expected_title="Persisted from PTY")

    def test_unexpected_fault_is_visible_nonzero_and_restores_terminal(self):
        with TemporaryDirectory() as home:
            self.run_terminal(home, fault=True)
