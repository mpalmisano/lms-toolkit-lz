# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import sys

from dotenv import load_dotenv
from errorhandler import ErrorHandler  # type: ignore
from sqlalchemy.engine.base import Engine

from edfi_lms_extractor_lib.helpers.decorators import catch_exceptions
from helpers.argparser import MainArguments, parse_main_arguments  # type: ignore

logger: logging.Logger


@catch_exceptions
def _configure_logging(arguments: MainArguments) -> None:
    global logger

    logger = logging.getLogger(__name__)

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=arguments.log_level,
    )


@catch_exceptions
def _run(arguments: MainArguments) -> None:
    global logger
    engine: Engine = arguments.get_db_engine()

    with engine.connect().execution_options(autocommit=True) as connection:
        logger.info("Harmonizing Canvas LMS Users.")
        connection.execute("EXEC lms.harmonize_lmsuser_canvas;")

        logger.info("Harmonizing Google Classroom LMS Users.")
        connection.execute("EXEC lms.harmonize_lmsuser_google_classroom;")

        logger.info("Harmonizing Schoology LMS Users.")
        connection.execute("EXEC lms.harmonize_lmsuser_schoology;")


def main() -> None:
    load_dotenv()
    arguments = parse_main_arguments(sys.argv[1:])
    _configure_logging(arguments)
    error_tracker: ErrorHandler = ErrorHandler()

    _run(arguments)

    if error_tracker.fired:
        print(
            "A fatal error occurred, please review the log output for more information.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
