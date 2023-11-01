#!/bin/python3

import csv
import shutil
import argparse
import json
import sys

# Default file values
DEFAULT_CSV_FILENAME = "example.csv"
DEFAULT_SUBS_FOLDER = "."
DEFAULT_MOVE_DISCARDED = False
DEFAULT_DISCARDED_FOLDER = "./delete"

# Default image values and thresholds
DEFAULT_HFR_LIMIT = 3.0
DEFAULT_MEDIAN_LOWER_THRESHOLD = 0.8
DEFAULT_MEDIAN_UPPER_THRESHOLD = 1.05
DEFAULT_RMS_NO_CHECK_THRESHOLD = 1.0
DEFAULT_RMS_LIMIT = 1.5
DEFAULT_RMS_RA_DEC_RATIO_THRESHOLD = 2.2
DEFAULT_STAR_COUNT_RATIO_THRESHOLD = 0.75
DEFAULT_REFERENCE_SUB_RMS_LIMIT = 0.8

# CSV constants
CSV_ID_ROW_POSITION = 0
CSV_FILENAME_ROW_POSITION = 5
CSV_EXPOSURE_TIME_POSITION = 8
CSV_HFR_ROW_POSITION = 10
CSV_MEDIAN_ROW_POSITION = 12
CSV_RMS_RA_PIXELS_POSITION = 17
CSV_RMS_DEC_PIXELS_POSITION = 18
CSV_RMS_TOT_PIXELS_POSITION = 19
CSV_SCALE_POSITION = 20
CSV_STARS_ROW_POSITION = 11

# Config constants
CSV_FILE = "csv-file"
SUBS_FOLDER = "subs-folder"
MOVE_DISCARDED = "move-discarded"
DISCARDED_FOLDER = "discarded-folder"
EXPOSURE_TIME = "exposure-time"

HFR_LIMIT = "hfr-limit"
MEDIAN_LOWER_THRESHOLD = "median-lower-threshold"
MEDIAN_UPPER_THRESHOLD = "median-upper-thershold"
RMS_NO_CHECK_THRESHOLD = "rms-no-check-threshold"
RMS_LIMIT = "rms-limit"
RMS_RA_DEC_RATIO_THRESHOLD = "rms-ra-dec-ratio-threshold"
STAR_COUNT_RATIO_THRESHOLD = "star-count-ratio-threshold"
REFERENCE_SUB_RMS_LIMIT = "reference-sub-rms-limit"


# Sub constants
SUB_ID = "id"
SUB_FILENAME = "filename"
SUB_EXPOSURE_TIME = "exposure-time"
SUB_HFR = "hfr"
SUB_MEDIAN = "median"
SUB_RMS = "rms"
SUB_RMS_RA = "rms-ra"
SUB_RMS_DEC = "rms-dec"
SUB_STARS = "stars"


# Other constants
JSON_INDENTATION = 2


def print_separator():
    print("-----------------------------------------------------------")


def beauty_print(content):
    print(json.dumps(content, indent=JSON_INDENTATION))


def press_enter_to_contiune():
    print("\nPlease press enter to contiunue:\n")
    sys.stdin.read(1)


def get_config():
    parser = argparse.ArgumentParser(
        prog="subs-analyzer.py",
        description="A simple script that analyzes CSV data \
            exported from NINA and filters bad subs according to certain parameters",
        epilog="Clear skyies!",
    )

    parser.add_argument(
        "--csv-file",
        help="CSV file",
        required=False,
        default=DEFAULT_CSV_FILENAME,
        type=str,
    )

    parser.add_argument(
        "--subs-folder",
        help="Folder where the subs are stored",
        required=False,
        default=DEFAULT_SUBS_FOLDER,
        type=str,
    )

    parser.add_argument(
        "--move-discarded",
        help="Move discarded subs",
        required=False,
        default=DEFAULT_MOVE_DISCARDED,
        type=bool,
    )

    parser.add_argument(
        "--discarded-folder",
        help="Discarded subs folder. Folder must exist.",
        required=False,
        default=DEFAULT_DISCARDED_FOLDER,
        type=str,
    )

    parser.add_argument(
        "--exposure-time",
        help="Only process subs that have this exposure time",
        required=False,
        default=None,
        type=int,
    )
    parser.add_argument(
        "--hfr-limit",
        help="Subs with HFR higher than this value will be discarded",
        required=False,
        default=DEFAULT_HFR_LIMIT,
        type=float,
    )

    parser.add_argument(
        "--median-lower-threshold",
        help="Upper threshold used to discard by lower median value",
        required=False,
        default=DEFAULT_MEDIAN_LOWER_THRESHOLD,
        type=float,
    )
    parser.add_argument(
        "--median-upper-threshold",
        help="Upper threshold used to discard by upper median value",
        required=False,
        default=DEFAULT_MEDIAN_UPPER_THRESHOLD,
        type=float,
    )
    parser.add_argument(
        "--rms-no-check-threshold",
        help="Subs with RMS lower than this value will not be checked for RA/DEC RMS ratio",
        required=False,
        default=DEFAULT_RMS_NO_CHECK_THRESHOLD,
        type=float,
    )
    parser.add_argument(
        "--rms-limit",
        help="Subs with RMS higher than this value will be discarded",
        required=False,
        default=DEFAULT_RMS_LIMIT,
        type=float,
    )
    parser.add_argument(
        "--rms-ra-dec-ratio-threshold",
        help="Max RA/Dec RMS ratio. Upper values will be discarded",
        required=False,
        default=DEFAULT_RMS_RA_DEC_RATIO_THRESHOLD,
        type=float,
    )
    parser.add_argument(
        "--star-count-ratio-threshold",
        help="Ratio used for discarding by star count",
        required=False,
        default=DEFAULT_STAR_COUNT_RATIO_THRESHOLD,
        type=float,
    )

    parser.add_argument(
        "--reference-sub-rms-limit",
        help="Max RMS value of the reference sub",
        required=False,
        default=DEFAULT_REFERENCE_SUB_RMS_LIMIT,
        type=float,
    )

    args = parser.parse_args()

    config = {
        CSV_FILE: args.csv_file,
        SUBS_FOLDER: args.subs_folder,
        MOVE_DISCARDED: args.move_discarded,
        DISCARDED_FOLDER: args.discarded_folder,
        EXPOSURE_TIME: args.exposure_time,
        HFR_LIMIT: args.hfr_limit,
        MEDIAN_UPPER_THRESHOLD: args.median_upper_threshold,
        MEDIAN_LOWER_THRESHOLD: args.median_lower_threshold,
        RMS_NO_CHECK_THRESHOLD: args.rms_no_check_threshold,
        RMS_LIMIT: args.rms_limit,
        RMS_RA_DEC_RATIO_THRESHOLD: args.rms_ra_dec_ratio_threshold,
        STAR_COUNT_RATIO_THRESHOLD: args.star_count_ratio_threshold,
        REFERENCE_SUB_RMS_LIMIT: args.reference_sub_rms_limit,
    }

    print_separator()
    print("\nUsing the following configuration:\n")
    beauty_print(config)
    press_enter_to_contiune()

    return config


def parse_csv(config):
    with open(config.get(CSV_FILE), newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        next(reader, None)  # Skip the headers

        subs = []
        for row in reader:
            # Add the sub when exposure time is not set or when exposure time is set and is the same as the sub
            if config.get(EXPOSURE_TIME) is None or config.get(EXPOSURE_TIME) == int(
                row[CSV_EXPOSURE_TIME_POSITION]
            ):
                subs.append(
                    {
                        SUB_ID: row[CSV_ID_ROW_POSITION],
                        SUB_FILENAME: row[CSV_FILENAME_ROW_POSITION],
                        SUB_EXPOSURE_TIME: row[CSV_EXPOSURE_TIME_POSITION],
                        SUB_STARS: int(row[CSV_STARS_ROW_POSITION]),
                        SUB_HFR: float(row[CSV_HFR_ROW_POSITION]),
                        SUB_MEDIAN: float(row[CSV_MEDIAN_ROW_POSITION]),
                        SUB_RMS_RA: float(row[CSV_RMS_RA_PIXELS_POSITION])
                        * float(row[CSV_SCALE_POSITION]),
                        SUB_RMS_DEC: float(row[CSV_RMS_DEC_PIXELS_POSITION])
                        * float(row[CSV_SCALE_POSITION]),
                        SUB_RMS: float(row[CSV_RMS_TOT_PIXELS_POSITION])
                        * float(row[CSV_SCALE_POSITION]),
                    }
                )

        # Order by stars desc
        subs.sort(key=lambda sub: sub[SUB_STARS], reverse=True)

        return subs


def get_refecence_sub(config, subs):
    reference_sub = next(
        sub for sub in subs if sub.get(SUB_RMS) < config.get(REFERENCE_SUB_RMS_LIMIT)
    )

    print("\nReference sub:\n")
    beauty_print(reference_sub)
    press_enter_to_contiune()

    return reference_sub


def discard_by_stars(config, reference_sub, sub):
    return sub.get(SUB_STARS) < reference_sub.get(SUB_STARS) * config.get(
        STAR_COUNT_RATIO_THRESHOLD
    )


def discard_by_median(config, reference_sub, sub):
    return sub.get(SUB_MEDIAN) > reference_sub.get(SUB_MEDIAN) * config.get(
        MEDIAN_UPPER_THRESHOLD
    ) or sub.get(SUB_MEDIAN) < reference_sub.get(SUB_MEDIAN) * config.get(
        MEDIAN_LOWER_THRESHOLD
    )


def discard_by_rms(config, sub):
    if sub.get(SUB_RMS) < config.get(RMS_NO_CHECK_THRESHOLD):
        return False

    elif sub.get(SUB_RMS) > config.get(RMS_LIMIT):
        return True

    ratio = (
        sub.get(SUB_RMS_RA) / sub.get(SUB_RMS_DEC)
        if sub.get(SUB_RMS_RA) > sub.get(SUB_RMS_DEC)
        else sub.get(SUB_RMS_DEC) / sub.get(SUB_RMS_RA)
    )

    return ratio > config.get(RMS_RA_DEC_RATIO_THRESHOLD)


def print_discarded_by_stars(discarded_by_stars):
    print("\n\nDiscarded by stars:\n")
    for sub in discarded_by_stars:
        print(f"{sub.get(SUB_FILENAME)} - Stars: {sub.get(SUB_STARS)}")


def print_discarded_by_median(discarded_by_median):
    print("\n\nDiscarded by median:\n")
    for sub in discarded_by_median:
        print(f"{sub.get(SUB_FILENAME)} - Median: {sub.get(SUB_MEDIAN)}")


def print_discarded_by_rms(discarded_by_rms):
    print("\n\nDiscarded by rms:\n")
    for sub in discarded_by_rms:
        print(
            f"{sub.get(SUB_FILENAME)} - Total RMS: {sub.get(SUB_RMS):.2f} - RA RMS: {sub.get(SUB_RMS_RA):.2f} - Dec RMS: {sub.get(SUB_RMS_DEC):.2f}"
        )


def print_statistics(subs, discarded_by_stars, discarded_by_median, discarded_by_rms):
    discarded_subs = (
        len(discarded_by_stars) + len(discarded_by_median) + len(discarded_by_rms)
    )

    print(f"\nNumber of subs: {len(subs)}")
    print(f"Number correct subs: {len(subs) - discarded_subs}")
    print(f"Number of discarded subs: {discarded_subs}")
    print(f"Normalized success ratio: {1 - discarded_subs / len(subs)}")

    print(f"\nDiscarded subs by stars: {len(discarded_by_stars)}")
    print(f"Discarded subs by median: {len(discarded_by_median)}")
    print(f"Discarded subs by RMS: {len(discarded_by_rms)}")


# ------------------------------------

config = get_config()

# Get subs ordered by stars
subs = parse_csv(config)

reference_sub = get_refecence_sub(config, subs)

discarded_by_stars = []
discarded_by_median = []
discarded_by_rms = []

for sub in subs:
    sub_discarded = False
    if discard_by_stars(config, reference_sub, sub):
        discarded_by_stars.append(sub)
        sub_discarded = True

    elif discard_by_median(config, reference_sub, sub):
        discarded_by_median.append(sub)
        sub_discarded = True

    elif discard_by_rms(config, sub):
        discarded_by_rms.append(sub)
        sub_discarded = True

    if sub_discarded is True and config.get(MOVE_DISCARDED) is True:
        shutil.move(
            config.get(SUBS_FOLDER) + "/" + sub.get(SUB_FILENAME),
            config.get(DISCARDED_FOLDER) + "/" + sub.get(SUB_FILENAME),
        )

discarded_by_stars.sort(key=lambda sub: sub[SUB_FILENAME])
discarded_by_median.sort(key=lambda sub: sub[SUB_FILENAME])
discarded_by_rms.sort(key=lambda sub: sub[SUB_FILENAME])

print_discarded_by_stars(discarded_by_stars)
print_discarded_by_median(discarded_by_median)
print_discarded_by_rms(discarded_by_rms)


print_statistics(subs, discarded_by_stars, discarded_by_median, discarded_by_rms)
