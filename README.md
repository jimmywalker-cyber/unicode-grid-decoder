# Unicode Grid Decoder

A Python command-line tool that retrieves coordinate-based Unicode data from a published Google Doc and reconstructs the hidden message in a two-dimensional grid.

## Features

- Retrieves a published document directly from its URL
- Parses HTML tables without third-party packages
- Detects the x-coordinate, character, and y-coordinate columns
- Fills unspecified grid positions with spaces
- Supports arbitrarily sized non-negative coordinates
- Includes validation and network-error messages

## Expected Document Format

| x-coordinate | Character | y-coordinate |
| ---: | :---: | ---: |
| 0 | █ | 0 |
| 0 | █ | 1 |
| 1 | ▀ | 1 |

## Running the Project

Python 3.9 or newer is recommended. No external packages are required.

```bash
python3 unicode_grid_decoder.py
```

When prompted, paste the URL of a published Google Doc:

```text
Published Google Doc URL: https://docs.google.com/document/d/e/.../pub
```

The decoded grid will be printed in the terminal.

## How It Works

1. Downloads the published document’s HTML.
2. Locates the table headers and coordinate rows.
3. Stores each Unicode character by its x and y coordinates.
4. Builds the grid from the highest y-coordinate to zero.
5. Inserts spaces wherever no character is specified.

## Skills Demonstrated

Python, HTML parsing, Unicode handling, coordinate mapping, input validation, network requests, error handling, and command-line application design.

## Author

[Jimmy Walker](https://github.com/jimmywalker-cyber)
