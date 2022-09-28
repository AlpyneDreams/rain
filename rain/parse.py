import sys, re, time, json
from os import path as Path
from clang.cindex import Index, Diagnostic, CompilationDatabase, TranslationUnit, TranslationUnitLoadError

from util import Colors, command_output, print_diagnostic 
from traverse import traverse_file

ARGS = [
    '-xc++', # allows inspecting headers
    '-std=c++20',
    '-Wno-deprecated-volatile',
    #'-stdlib=libc++' # TODO: support parsing with libc++?
]

# Linux: Add GCC or Clang headers
if sys.platform.startswith('linux'):
    #version_gcc = command_output('gcc', '-dumpversion')
    #includes_gcc = command_output('gcc', '--print-file-name=include')
    includes_clang = command_output('clang', '--print-file-name=include')
    
    ARGS += [ f'-I{includes_clang}' ]       # /usr/lib/clang/<version>/include, provides stddef.h
    #ARGS += [ f'-I{includes_gcc}' ]        # /usr/lib/gcc/x86_64-pc-linux-gnu/<version>/include
    #ARGS += [ f'-I{includes_gcc}-fixed' ]  # provides limits.h
    #ARGS += [ f'-I/usr/include/c++/v1' ]               # libc++
    #ARGS += [ f'-I/usr/include/c++/{version_gcc}' ]    # libstdc++


def parse_files(src_root, stale_files):
    start_time = time.perf_counter()

    compile_commands_json = []

    all_includes = set()

    # Quickly parse compile_commands.json
    with open('compile_commands.json') as compdb:
        compile_commands_json = json.load(compdb)

    # Create index (takes ~5 ms)
    index = Index.create(excludeDecls=True)    
    
    # Read compile_commands.json (10x slower than reading the json file directly)
    #compile_commands: CompilationDatabase = CompilationDatabase.fromDirectory('.')
    
    i = 0
    count = len(stale_files)
    for file in stale_files:
        i += 1
        print(f'[{i}/{count}] ' + Path.basename(file))

        # Get compile commands for this specific file
        args = []
        for cmd in compile_commands_json:
            if cmd['file'] == file:
                args = cmd['command'].split() + ARGS
                break
        #cmd = compile_commands.getCompileCommands(file)[0]

        meta = parse_file(index, file, args)

        with open(stale_files[file], 'w') as f:
            f.write(json.dumps(meta, indent='\t')) 
    
    end_time = time.perf_counter()
    print(Colors.PURPLE + f"Parsed all files in {round((end_time - start_time) * 1000)} ms" + Colors.END)

def parse_file(index, file, cmd_args):
    # Get include dirs & defines
    args = [arg for arg in cmd_args if arg.lstrip('"').startswith('-I') or arg.lstrip('"').startswith('-D')]

    # Strip and unescape quotes
    for i, arg in enumerate(args):
        if arg[0] == '"' and arg[-1] == '"':
            args[i] = arg[1:-1].replace('\\"', '"')

    # Add default args
    args += ARGS

    # Parse translation unit (the slowest step)
    options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
    tu: TranslationUnit = index.parse(file, args, options=options)

    # Print diagnostics
    for msg in tu.diagnostics:
        print_diagnostic(msg)
        if msg.severity == Diagnostic.Fatal:
            exit(1)
    
    # Traverse the AST and produce RTTI data
    print(Colors.DIM, end='')
    meta = traverse_file(tu, file)
    print(f"Reflected {len(meta['classes'])} classes and {len(meta['enums'])} enums.")
    print(Colors.NO_DIM, end='')
    
    return meta