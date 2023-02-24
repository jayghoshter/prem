
from rich import print as rprint
from rich.console import Console
from rich.theme import Theme
import datetime

custom_logging_theme = Theme({
    "print": 'none',
    "info" : 'bold green',
    "note": "bold magenta",
    "warn": "bold yellow",
    "error": "bold red"
})
log_console = Console(theme = custom_logging_theme)

log_out_all = []
log_err_all = []
log_timestamp = "." + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

logfilename = 'out'

def log_get_indent_string(indent_level=0, indent_step=2, indent_caret='>'):
    total_indent = indent_level * indent_step
    indent_caret = indent_caret if total_indent > 0 else ''
    return ' ' * total_indent + indent_caret

def rule(*message):
    log_console.rule(*message)

def generic_log(*message, indent_level=0, indent_step=2, style='info', err=False, prefix=False):

    if err:
        write = write_err
        log_arr = log_err_all
    else:
        write = write_out
        log_arr = log_out_all

    if prefix:
        message = [ f"{style.upper()}:" ] + list(message)

    indent_str = log_get_indent_string(indent_level, indent_step)
    if indent_str:
        message = [ indent_str ] + list(message)

    log_arr.append(" ".join(message))
    log_console.print(*message, style=style or 'info')
    write(logfilename, ' '.join(message))

def print(*message, indent_level=0, indent_step=2, prefix=False):
    """
    Write to stdout
    """
    generic_log(*message, indent_level=indent_level, indent_step=indent_step, style='print', prefix=prefix)

def info(*message, indent_level=0, indent_step=2, prefix=False):
    """
    Write to stdout
    """
    generic_log(*message, indent_level=indent_level, indent_step=indent_step, style='info', prefix=prefix)

def err(*message, indent_level=0, indent_step=2, prefix=True):
    """
    Write to "stderr"
    """
    generic_log(*message, indent_level=indent_level, indent_step=indent_step, style='error', prefix=prefix)

def warn(*message, indent_level=0, indent_step=2, prefix=False):
    """
    Write to stderr
    """
    generic_log(*message, indent_level=indent_level, indent_step=indent_step, style='warn', prefix=prefix)

def note(*message, indent_level=0, indent_step=2, prefix=False):
    """
    Write to stdout
    """
    generic_log(*message, indent_level=indent_level, indent_step=indent_step, style='note', prefix=prefix)

def die(*message, exception=RuntimeError):
    """
    Write to stderr, and die
    """
    err(*message)
    raise(exception(*message))


def write_out(fname, message_str, timestamp=False):
    """
    write to output file
    """
    ts = log_timestamp if timestamp else ''
    with open(fname + ts + '.stdout.log', 'a') as outfile:
        outfile.write(message_str + '\n')

def write_err(fname, messsage_str, timestamp=False):
    """
    write to output file
    """
    ts = log_timestamp if timestamp else ''
    with open(fname + ts + '.stderr.log', 'a') as errfile:
        errfile.write(messsage_str + '\n')

def write_all(fname, timestamp=False):
    """
    write to files
    """
    ts = log_timestamp if timestamp else ''
    with open(fname + ts + '.stdout.log', 'w') as outfile:
        outfile.write("\n".join(log_out_all))
    with open(fname + ts + '.stderr.log', 'w') as errfile:
        errfile.write("\n".join(log_err_all))
