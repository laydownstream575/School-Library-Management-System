"""Background workers for long operations using QRunnable + QThreadPool.

Usage::

    from ui.workers import run_worker

    def on_done(result):
        theme.show_success(self, f"Exported to {result}")

    def on_error(msg):
        theme.show_error(self, msg)

    run_worker(self, excel_service.export_rows, on_done, on_error,
               columns, rows, filename)
"""

import logging
import traceback
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as exc:
            logger.exception("Worker failed: %s", exc)
            self.signals.error.emit(str(exc))


def run_worker(parent, fn, on_finished, on_error, *args, **kwargs):
    """Run a callable in a background thread.

    Parameters
    ----------
    parent : QWidget
        The widget that owns the operation (for cursor + button control).
    fn : callable
        The function to run in the background.
    on_finished : callable
        Called on the main thread with the return value of fn.
    on_error : callable
        Called on the main thread with the error message string.
    *args, **kwargs
        Passed to fn.
    """
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    QApplication.setOverrideCursor(Qt.WaitCursor)
    parent.setEnabled(False)

    worker = Worker(fn, *args, **kwargs)
    pool = QThreadPool.globalInstance()

    def _done(result):
        parent.setEnabled(True)
        QApplication.restoreOverrideCursor()
        on_finished(result)

    def _error(msg):
        parent.setEnabled(True)
        QApplication.restoreOverrideCursor()
        on_error(msg)

    worker.signals.finished.connect(_done)
    worker.signals.error.connect(_error)
    pool.start(worker)
