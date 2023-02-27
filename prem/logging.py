import logging
import inspect

from rich.theme import Theme
from rich.logging import RichHandler
from rich.console import Console

from logging import LogRecord, Logger
from rich.traceback import Traceback
from rich._null_file import NullFile

custom_logging_theme = Theme({
    "debug": 'green',
    "info" : 'none',
    "note": "magenta",
    "warn": "bold yellow",
    "warning": "bold yellow",
    "error": "bold red",
    "critical": "bold red reverse"
})

shell_console = Console(theme = custom_logging_theme)


class CustomHandler(RichHandler):

    def emit(self, record: LogRecord) -> None:
        """Invoked by logging."""
        message = self.format(record)
        traceback = None
        if (
            self.rich_tracebacks
            and record.exc_info
            and record.exc_info != (None, None, None)
        ):
            exc_type, exc_value, exc_traceback = record.exc_info
            assert exc_type is not None
            assert exc_value is not None
            traceback = Traceback.from_exception(
                exc_type,
                exc_value,
                exc_traceback,
                width=self.tracebacks_width,
                extra_lines=self.tracebacks_extra_lines,
                theme=self.tracebacks_theme,
                word_wrap=self.tracebacks_word_wrap,
                show_locals=self.tracebacks_show_locals,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                suppress=self.tracebacks_suppress,
            )
            message = record.getMessage()
            if self.formatter:
                record.message = record.getMessage()
                formatter = self.formatter
                if hasattr(formatter, "usesTime") and formatter.usesTime():
                    record.asctime = formatter.formatTime(record, formatter.datefmt)
                message = formatter.formatMessage(record)

        message_renderable = self.render_message(record, message)
        log_renderable = self.render(
            record=record, traceback=traceback, message_renderable=message_renderable
        )
        if isinstance(self.console.file, NullFile):
            # Handles pythonw, where stdout/stderr are null, and we return NullFile
            # instance from Console.file. In this case, we still want to make a log record
            # even though we won't be writing anything to a file.
            self.handleError(record)
        else:
            try:
                self.console.print(log_renderable, style=record.__dict__['style'])
            except Exception:
                self.handleError(record)

# the handler determines where the logs go: stdout/file
shell_handler = CustomHandler(
        markup=True,
        console=shell_console,
        show_time=False,
        show_level=False,
        show_path=False,
        )
shell_handler.setLevel(logging.INFO)
fmt_shell = '%(message)s'
shell_formatter = logging.Formatter(fmt_shell)
shell_handler.setFormatter(shell_formatter)

# the handler determines where the logs go: stdout/file
log_filename = "prem.log"
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
fmt_file = '%(levelname)s [%(asctime)s] %(message)s'
file_formatter = logging.Formatter(fmt_file)
file_handler.setFormatter(file_formatter)

class CustomLogger(Logger):
    def __init__(self, name, level=logging.NOTSET):
        """
        Initialize the logger with a name and an optional level.
        """
        super().__init__(name, level)
        self.addHandler(shell_handler)
        self.addHandler(file_handler)

    # Override _log() to modify message with indent_str
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1, **kwargs):

        indent_level = kwargs.get('indent_level', log_default_indent_level)
        indent_step = kwargs.get('indent_step', log_default_indent_step)
        indent_caret = kwargs.get('indent_caret', log_default_indent_caret)
        indent_str = get_indent_string(indent_level, indent_step, indent_caret)
        if indent_str:
            msg = f"{indent_str} {msg}"

        if extra is None:
            extra = {}
        extra['style'] = logging._levelToName[level].lower()

        super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)


class BufferedLogger(CustomLogger):
    def __init__(self, name, level=logging.NOTSET):
        """
        Initialize the logger with a name and an optional level.
        """
        super().__init__(name, level)
        self.log_data = []

    # Override _log() to modify message with indent_str
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1, **kwargs):

        indent_level = kwargs.get('indent_level', log_default_indent_level)
        indent_step = kwargs.get('indent_step', log_default_indent_step)
        indent_caret = kwargs.get('indent_caret', log_default_indent_caret)
        indent_str = get_indent_string(indent_level, indent_step, indent_caret)
        if indent_str:
            msg = f"{indent_str} {msg}"

        if extra is None:
            extra = {}
        extra['style'] = logging._levelToName[level].lower()
        self.log_data.append((level, msg, args, exc_info, extra, stack_info, stacklevel))

    def flush(self, lock):
        lock.acquire()
        for level, msg, args, exc_info, extra, stack_info, stacklevel in self.log_data:
            super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)
        lock.release()

# logging.setLoggerClass(CustomLogger)

# defaultLogger = logging.getLogger(__name__)
defaultLogger = CustomLogger('default')
logger_methods = dict(inspect.getmembers(defaultLogger, predicate=inspect.ismethod))
defaultLogger.setLevel(logging.INFO)

defaultLogger.addHandler(shell_handler)
defaultLogger.addHandler(file_handler)

log_default_indent_level = 0
log_default_indent_step = 2
log_default_indent_caret = '>'

def get_indent_string(indent_level=log_default_indent_level, indent_step=log_default_indent_step, indent_caret=log_default_indent_caret):
    total_indent = indent_level * indent_step
    indent_caret = indent_caret if total_indent > 0 else ''
    return ' ' * total_indent + indent_caret

def log(msg, *args, level='info', indent_level=log_default_indent_level, indent_step=log_default_indent_step, indent_caret=log_default_indent_caret, **kwargs):
    indent_str = get_indent_string(indent_level, indent_step, indent_caret)
    if indent_str:
        msg = f"{indent_str} {msg}"

    logger = kwargs.get('logger', defaultLogger)
    logger_methods = dict(inspect.getmembers(logger, predicate=inspect.ismethod))
    logger_methods[level](msg, *args)


def debug(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    defaultLogger.debug(msg, *args,
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

def info(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    log(msg, *args,
        level='info',
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

def warning(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    log(msg, *args,
        level='warning',
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

def warn(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    log(msg, *args,
        level='warning',
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

def error(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    log(msg, *args,
        level='error',
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

def critical(msg, *args, indent_level=0, indent_step=2, indent_caret='>'):
    log(msg, *args,
        level='critical',
        indent_level=indent_level,
        indent_step=indent_step,
        indent_caret=indent_caret,
        )

if __name__ == "__main__":
    debug("debug text 123")
    info("info text 123")
    warning("warn text 123")
    error("error text 123")
    critical("critical text 123")
    info("[bold magenta]filename 123[/bold magenta] more text")
