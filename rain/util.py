from clang.cindex import Diagnostic

# https://ansi.gabebanks.net/
class Colors:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    PURPLE  = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    DEFAULT = '\033[39m'

    DIM     = '\033[2m'
    BOLD    = '\033[1m'
    NO_DIM  = '\033[22m'
    END     = '\033[0m'
    RESET   = '\033[0m'

def print_diagnostic(msg: Diagnostic):
    text = msg.format()
    #for child in msg.children:
    #    text += '\n    ' + Colors.DIM + child.format() + Colors.NO_DIM
    match msg.severity:
        case Diagnostic.Note | Diagnostic.Ignored:
            print(Colors.DIM + text + Colors.END)
        case Diagnostic.Warning:
            print(Colors.YELLOW + text + Colors.END)
        case Diagnostic.Error:
            print(Colors.RED + text + Colors.END)
        case Diagnostic.Fatal:
            print(Colors.RED + Colors.BOLD + text + Colors.END)

def command_output(*args):
    import subprocess
    return subprocess.check_output(args, encoding='utf-8').strip()