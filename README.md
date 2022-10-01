# Rain: Automatic Reflection for C++

## Requirements

You will need Python 3.10 and the `libclang` pip package. 

## Examples

### Setup: Meson

This process will likely change.

Add rain as a subproject. Assume you have all your `.cpp` files in `proj_src`.
You want to generate a `.meta.json` file for each, and then combine them into
an `rtti.cpp` file that you can link normally.

```meson
rain     = subproject('rain')
rain_dep = rain.get_variable('rain_dep')

...

python = import('python').find_installation('python3')

# Build meta files
proj_meta = []
foreach file : proj_src
    fs = import('fs')
    proj_meta += custom_target(
        fs.name(file) + '.meta.json',
        output: fs.name(file) + '.meta.json',
        input: [rain.get_variable('rain_update_py'), file],
        command: [python, '@INPUT@', '@OUTPUT@'],
        console: true
    )
endforeach

# Build rtti.cpp
proj_rtti = custom_target(
    'rtti.cpp',
    output: 'rtti.cpp',
    input: [rain.get_variable('rain_rtti_py'), proj_meta],
    command: [python, '@INPUT@', '@OUTPUT@', '@CURRENT_SOURCE_DIR@],
    console: true
)

...

proj_exe = executable(files(proj_src), proj_rtti, 
    ...
    link_with: [rain_dep, ...]
)

```

## Structure

The Python scripts are as follows:
- `update.py` - simply marks a given meta file as stale
- `rtti.py` - generates a `rtti.cpp` file from a list of meta files
  - `parse.py` - actual libclang parsing logic - regenerates stale meta files
    - `traverse.py` - traverses the AST to produce type info
