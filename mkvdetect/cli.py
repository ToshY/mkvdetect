import json

import click
from loguru import logger  # noqa

from mkvdetect.args import InputPathChecker
from mkvdetect.exception import StreamTypeMissingError, StreamOrderError
from mkvdetect.helper import (
    split_list_of_dicts_by_key,
    combine_arguments_by_batch,
)
from mkvdetect.process import ProcessCommand


def validate_stream_order(mkvmerge_identify_result, file_details):
    """
    Check the stream order in the given mkvmerge result.

    Parameters:
        mkvmerge_identify_result (dict): A dictionary containing the mkvmerge result.
            The keys are the stream types (e.g., 'video', 'audio', 'subtitles') and the values
            are dictionaries with the following keys:
            - 'count' (int): The number of streams of that type.
        file_details (dict): A dictionary containing the file name and batch name.

    Raises:
        StreamOrderError: If the stream order does not follow convention video - audio - subtitles.
    """

    required_streams_order = ["video", "audio", "subtitles"]
    for idx, (stream_type, stream_info) in enumerate(mkvmerge_identify_result.items()):
        if required_streams_order[idx] == stream_type:
            continue

        raise StreamOrderError(
            required_streams_order[idx], idx, stream_type, file_details
        )


def validate_stream_count(mkvmerge_identify_result, file_details):
    """
    Validates the stream count in the given mkvmerge result.

    Parameters:
        mkvmerge_identify_result (dict): A dictionary containing the mkvmerge result.
            The keys are the stream types (e.g., 'video', 'audio', 'subtitles') and the values
            are dictionaries with the following keys:
            - 'count' (int): The number of streams of that type.
        file_details (dict): A dictionary containing the file name and batch name.

    Raises:
        StreamTypeMissingError: If a required stream type is missing in the mkvmerge result.
    """

    required_streams_types = ["video", "audio", "subtitles"]
    for required_stream_type in required_streams_types:
        if required_stream_type in mkvmerge_identify_result:
            continue
        raise StreamTypeMissingError(required_stream_type, file_details)


def mkvmerge_identify_streams(
    input_file, total_items, item_index, batch_index, batch_name
):
    """
    Identifies the streams in an MKV file using MKVmerge and returns a dictionary of streams sorted by codec type.

    Args:
        input_file (str): The path to the MKV file to identify.
        total_items (int): The total number of items in the batch.
        item_index (int): The index of the current item in the batch.
        batch_index (int): The index of the current batch.
        batch_name (str): The name of the current batch.

    Returns:
        dict: A dictionary of streams sorted by codec type, with the following structure:
            - The keys are the codec types ("video", "audio", "subtitles").
            - The values are dictionaries with two keys:
                - "streams": A dictionary of individual streams, with the following structure:
                    - The keys are the stream IDs.
                    - The values are dictionaries with the stream information.
                - "count": The number of streams of the given codec type.
    """

    if item_index == 0:
        logger.info(
            f"MKVmerge identify batch `{batch_index}` for `{batch_name}` started."
        )

    mkvmerge_identify_command = [
        "mkvmerge",
        "--identify",
        "--identification-format",
        "json",
        str(input_file),
    ]

    process = ProcessCommand(logger)
    result = process.run("MKVmerge identify", mkvmerge_identify_command)

    mkvmerge_identify_output = json.loads(result.stdout)

    # Split by codec_type
    split_streams, split_keys = split_list_of_dicts_by_key(
        mkvmerge_identify_output["tracks"], "type"
    )

    # Rebuild streams & count per codec type
    streams = {k: {"streams": {}, "count": 0} for k in split_keys}
    for x, s in enumerate(split_keys):
        streams[s]["streams"] = split_streams[x]
        streams[s]["count"] = len(streams[s]["streams"])

    file_details = {"file_name": input_file, "batch_name": batch_name}

    validate_stream_count(streams, file_details)
    validate_stream_order(streams, file_details)

    if item_index == total_items - 1:
        logger.info(
            f"MKVmerge identify batch `{batch_index}` for `{batch_name}` completed."
        )


@logger.catch
@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Repository: https://github.com/ToshY/mkvdetect",
)
@click.option(
    "--input-path",
    "-i",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, resolve_path=True),
    required=False,
    multiple=True,
    callback=InputPathChecker(),
    show_default=True,
    default=["./input"],
    help="Path to input file or directory",
)
def cli(input_path):
    combined_result = combine_arguments_by_batch(input_path)

    # Identify track order
    for item in combined_result:
        current_batch = item.get("batch")
        current_input_original_batch_name = item.get("input").get("given")
        current_input_files = item.get("input").get("resolved")
        total_current_input_files = len(current_input_files)

        for current_file_path_index, current_file_path in enumerate(
            current_input_files
        ):
            mkvmerge_identify_streams(
                current_file_path,
                total_current_input_files,
                current_file_path_index,
                current_batch,
                current_input_original_batch_name,
            )
