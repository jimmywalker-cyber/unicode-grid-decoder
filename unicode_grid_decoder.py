"""Reconstruct a Unicode message from coordinates in a published Google Doc."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class _TableParser(HTMLParser):
    """Collect table rows and cells from an HTML document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None
        self._ignored_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        tag = tag.lower()

        if tag in {"script", "style"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return

        if tag == "tr":
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []
        elif tag == "br" and self._current_cell is not None:
            self._current_cell.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and self._current_cell is not None:
            self._current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in {"script", "style"}:
            self._ignored_depth = max(0, self._ignored_depth - 1)
            return
        if self._ignored_depth:
            return

        if tag in {"td", "th"} and self._current_cell is not None:
            value = " ".join("".join(self._current_cell).replace("\xa0", " ").split())
            if self._current_row is not None:
                self._current_row.append(value)
            self._current_cell = None
        elif tag == "tr" and self._current_row is not None:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = None


def _fetch_document(url: str) -> str:
    if not url.startswith(("https://", "http://")):
        raise ValueError("Enter a complete published Google Doc URL.")

    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _find_columns(rows: list[list[str]]) -> tuple[int, int, int, int]:
    for row_number, row in enumerate(rows):
        headers = [_normalize_header(value) for value in row]

        x_column = next(
            (i for i, value in enumerate(headers) if value in {"x", "xcoord", "xcoordinate"}),
            None,
        )
        y_column = next(
            (i for i, value in enumerate(headers) if value in {"y", "ycoord", "ycoordinate"}),
            None,
        )
        character_column = next(
            (
                i
                for i, value in enumerate(headers)
                if value in {"char", "character", "symbol", "unicodecharacter"}
            ),
            None,
        )

        if x_column is not None and y_column is not None and character_column is not None:
            return row_number, x_column, character_column, y_column

    raise ValueError(
        "Could not find x-coordinate, Character, and y-coordinate columns."
    )


def _extract_points(html: str) -> dict[tuple[int, int], str]:
    parser = _TableParser()
    parser.feed(html)

    header_row, x_column, character_column, y_column = _find_columns(parser.rows)
    required_column = max(x_column, character_column, y_column)
    points: dict[tuple[int, int], str] = {}

    for row in parser.rows[header_row + 1 :]:
        if len(row) <= required_column:
            continue

        try:
            x = int(row[x_column])
            y = int(row[y_column])
        except ValueError:
            continue

        if x < 0 or y < 0:
            raise ValueError("Coordinates must be zero or greater.")

        character = row[character_column]
        if character:
            points[(x, y)] = character

    if not points:
        raise ValueError("The document did not contain any valid coordinate rows.")

    return points


def _render_grid(points: dict[tuple[int, int], str]) -> str:
    max_x = max(x for x, _ in points)
    max_y = max(y for _, y in points)

    lines = []
    for y in range(max_y, -1, -1):
        line = "".join(points.get((x, y), " ") for x in range(max_x + 1))
        lines.append(line)

    return "\n".join(lines)


def decode_secret_message(document_url: str) -> str:
    """Retrieve a published Google Doc, print its Unicode grid, and return it."""

    html = _fetch_document(document_url)
    grid = _render_grid(_extract_points(html))
    print(grid)
    return grid


def main() -> None:
    document_url = input("Published Google Doc URL: ").strip()
    try:
        decode_secret_message(document_url)
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Unable to retrieve the document: {error}")
    except ValueError as error:
        print(f"Unable to decode the document: {error}")


if __name__ == "__main__":
    main()
