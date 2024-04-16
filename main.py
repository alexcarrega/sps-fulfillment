import csv
import json
import sys
from typing import Any, Dict, TextIO

import requests
from cloup import Choice, Path, command, option, option_group
from cloup.constraints import mutually_exclusive
from dict2xml import dict2xml

FORMAT_CSV = "csv"
FORMAT_JSON = "json"
ACCEPTED_FORMAT = (FORMAT_CSV, FORMAT_JSON)
ACCEPTED_SOURCE = ("file", "api", "stdin")


def read_data(
    format: str, api_input: str, filename_input: str, stdin: str
) -> Dict[str, Any]:
    data = []
    if filename_input is not None:
        with open(filename_input, "r") as file:
            match format.lower():
                case "json":
                    return json.load(file)
                case "csv":
                    return parse_csv(file)
    if api_input is not None:
        source = requests.get(api_input)
        match format.lower():
            case "json":
                return json.loads(source.json())
            case "csv":
                return parse_csv(source.json().splitlines())
    elif stdin:
        match format.lower():
            case "json":
                return json.load(sys.stdin)
            case "csv":
                return parse_csv(sys.stdin)
    return data


def parse_csv(input: str | TextIO) -> Dict[str, Any]:
    data = []
    reader = csv.DictReader(input)
    for row in reader:
        data.append(row)
    return data


def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    processed = []
    for item in data:
        processed.append(
            dict(
                id=item["id"],
                nome=item["nome"],
                prezzo_totale=float(item["prezzo"]) * int(item["quantità"]),
            )
        )
    return processed


def write_data(
    data: Dict[str, Any], api_output: str, filename_output: str, stdout: bool
) -> None:
    output = dict2xml(data, wrap="prodotti", indent="   ")
    if filename_output is not None:
        with open(filename_output, "w") as file:
            file.write(output)
    elif api_output is not None:
        requests.post(api_output, output)
    elif stdout:
        print(output)


@command()
@option(
    "-f",
    "--format",
    type=Choice(ACCEPTED_FORMAT, case_sensitive=False),
    help="Format of the input data file",
    required=True,
)
@option_group(
    "Input options",
    option(
        "-r",
        "--api-input",
        type=str,
        default=None,
        help="API endpoint to request the data",
    ),
    option(
        "-l",
        "--filename-input",
        type=Path(exists=True),
        default=None,
        help="Input data filename",
    ),
    option(
        "-i",
        "--stdin",
        is_flag=True,
        default=False,
        help="Read data from standard input",
    ),
    constraint=mutually_exclusive,
)
@option_group(
    "Output options",
    option(
        "-p",
        "--api-output",
        type=str,
        default=None,
        help="API endpoint to send the data",
    ),
    option(
        "-e",
        "--filename-output",
        type=Path(),
        default=None,
        help="Input data filename",
    ),
    option(
        "-u",
        "--stdout",
        is_flag=True,
        default=False,
        help="Write data to standard output",
    ),
    constraint=mutually_exclusive,
)
def start(
    format: str,
    api_input: str,
    filename_input: str,
    stdin: bool,
    api_output: str,
    filename_output: str,
    stdout: bool,
) -> None:
    data = read_data(format, api_input, filename_input, stdin)
    processed = process_data(data)
    write_data(processed, api_output, filename_output, stdout)


if __name__ == "__main__":
    start()
