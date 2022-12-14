import os, os.path, sys, json, time

from util import Colors
from parse import parse_files

# Usage: rtti.py <meta files...> <rtti.cpp> <src folder>

infiles = sys.argv[1:-2]
outfile = sys.argv[-2]
src_root = sys.argv[-1]

start_time = time.time()

includes = set()
classes = {}
enums = {}

stale_files = {}

print(Colors.CYAN)
print(f'==================== Rain RTTI ====================')
print(Colors.END, end='')

# Load reflection information from .meta.json file
def load_meta(filename):
    global stale_files
    filename = os.path.splitext(filename)[0] + '.json'
    if not os.path.exists(filename):
        print(Colors.YELLOW + f"Can't find meta file: {filename}" + Colors.END)
        return
    with open(filename) as file:
        meta = json.load(file)
        if "stale" in meta and meta["stale"]:
            stale_files[meta["filename"]] = filename
            return
        classes.update(meta['classes'])
        enums.update(meta['enums'])
        for inc in meta['includes']:
            includes.add(inc)

for filename in infiles:
    load_meta(filename)

# If there's any stale meta files, regenerate them
if len(stale_files) > 0:
    print(Colors.PURPLE + f"Regenerating RTTI for {len(stale_files)} files..." + Colors.END)

    # Reparse stale files
    parse_files(src_root, stale_files)
    
    for file in stale_files:
        load_meta(stale_files[file])
    print(f"Generating '{outfile}'")
else:
    print(f"Up to date! Generating '{outfile}'")

output = open(outfile, 'w')
global_indent = 0
write = lambda *args, indent=0: output.write((' ' * (indent+global_indent) * 4) + ''.join([*args]) + '\n')

write('// Autogenerated by rain/rtti.py')
write('#include <rain/rain.h>')
write()
for inc in includes:
    write(f'#include "{inc}"')

# Suppress offsetof warnings (for non-standard layout structs)
# TODO: This seems to work but is not guaranteed to
write()
write('#ifdef __GNUC__')
write('#pragma GCC diagnostic ignored "-Winvalid-offsetof"')
write('#endif')

# Begin RTTI namesapce
write()
write('namespace rain::rtti')
write('{')
global_indent += 1

# Initialize registries
write('// One Definition Rule: Ensure registries are initialized first.')
write('static const auto& _class = Registry<Class>::registry;')
write('static const auto& _enums = Registry<Enum>::registry;')
write()

# Write classes
for spelling, data in classes.items():
    write(f'// {data["location"]}')
    write('template <>')
    write(f'Class& ClassDef<{spelling}> = Class::Register(Class {{')

    # Write name, size
    write(f'.name = "{data["name"]}",', indent=1)
    write(f'.displayName = "{data["displayName"]}",', indent=1)
    write(f'.type = {data["type"]},', indent=1)
    write(f'.size = {data["size"]},', indent=1)

    fields = data['fields']
    # Write fields
    if len(fields) > 0:
        write('.fields = {', indent=1)
        for n in fields:
            write(f'{{ "{n["name"]}", "{n["displayName"]}", {n["type"]}, {n["offset"]} }},', indent=2)
        write('},', indent=1)

    methods = data['methods']
    # Write methods
    if len(methods) > 0:
        write('.methods = {', indent=1)
        for n in methods:
            if n["name"].startswith('operator'):
                continue
            argtypes = ', '.join(n["args"])
            args = ', '.join(f'TypeID<{arg}>' for arg in n["args"])
            write(f'Method {{ "{n["name"]}", "{n["displayName"]}", MEMBER_FUNCTION({n["pointer"]}), TypeID<{n["result"]}>, {{{args}}} }},', indent=2)
        write('},', indent=1)

    # Write base classes
    bases = data['bases']
    if len(bases) > 0:
        write(f'.bases = {{ {", ".join([f"TypeHash<{n}>" for n in bases])} }},', indent=1)

    # Write subclasses
    derived = data['derived']
    if len(derived) > 0:
        write(f'.derived = {{ {", ".join([f"TypeHash<{n}>" for n in derived])} }},', indent=1)

    
    # End class RTTI
    write('});\n')

# Write enums
for spelling, data in enums.items():
    write(f'// {data["location"]}')
    write('template <>')
    write(f'Enum& EnumDef<{spelling}> = Enum::Register(Enum {{')

    # Write name, size
    write(f'.name = "{data["name"]}",', indent=1)
    write(f'.displayName = "{data["displayName"]}",', indent=1)
    write(f'.type = {data["type"]},', indent=1)
    write(f'.size = {data["size"]},', indent=1)
    write(f'.underlyingType = {data["underlyingType"]},', indent=1)
    write(f'.scoped = {"true" if data["scoped"] else "false"},', indent=1)

    write(f'.values = {{', indent=1)
    values = data['values']
    for name in values:
        write(f'{{ "{name}", uintmax({spelling}::{name}) }},', indent=2)
    write('},', indent=1)

    write(f'.names = {{', indent=1)
    for name, value in values.items():
        write(f'{{ uintmax({spelling}::{name}), "{name}" }},', indent=2)
    write('}', indent=1)
    
    # End class RTTI
    write('});\n')


# End RTTI namespace
global_indent -= 1
write('}')

output.close()

print(Colors.CYAN, end='')
print(f'===================================================')
print(Colors.END)
