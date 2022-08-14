import os, os.path, sys, json, time

infiles = sys.argv[1:-1]
outfile = sys.argv[-1]

start_time = time.time()

includes = set()
classes = {}
enums = {}

for filename in infiles:
    filename = os.path.splitext(filename)[0] + '.json'
    if not os.path.exists(filename):
        continue
    with open(filename) as file:
        meta = json.load(file)
        classes.update(meta['classes'])
        enums.update(meta['enums'])
        for inc in meta['includes']:
            includes.add(inc)

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
write('#pragma GCC diagnostic ignored "-Winvalid-offsetof"')

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
