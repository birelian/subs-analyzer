# subs-analyzer

A simple Python script that analyzes CSV data exported from NINA and filters bad subs according to certain parameters.

There are beautiful tools for this purpose. This is just my own implementation of the workflow I follow.

## Motivation

There are some common patterns that lead me to a discarded sub. Some of them are:

- High HFR.
- Bad RMS. 
- Clouds.
- Others.

Before checking visually each individual sub, I usually open the NINA exported CSV and discard bad ones according to:

 - HFR
 - RMS
 - Median
 - Number of stars

Later on this document I explain how I use those values (and I may be mistaken!) in order to discard bad subs.

## Prerequisites

- Python 3
- A CSV exported from NINA containing all subs metadata

## How to run it

```shell
$ python3 subs-analyzer.py 
```

## How it works

When the script starts, it will load the CSV, read the subs metadata, and select the best one.

With the current implementation, the best sub is the one that has the higher number of stars, but is also below a RMS threshold given by the user.

Once the best sub has been selected, the rest of them will be compared to it, and discarded according the following rules:

### By HFR

Subs with higher HFR than the HFR limit will be discarded.

### By median

The median of the best sub will be taken as a reference. When discarding by median, two values must be supplied:

- Upper thershold
- Lower threshold

Those thresholds are multipliers that define what median values to keep. For example given these parameters:

- Reference median value: `1000`
- Upper threshold: `1.10`
- Lower threshold: `0.95`

All median values between 950 `(1000 * 0.95)` and 1100 `(1000 * 1.10)` will be kept.

### By RMS

When discarding by RMS, the following algorithm is applied:

- Subs with a RMS lower than a given threshold will not be analyzed.
- Subs with a RMS higher than the RMS limit will be discarded.
- Subs with RMS below those two thresholds will be analyzed for eccentricity.

For example, given these parameters:

- RMS no check threshold: `1.0`
- RMS discard threshold: `2.0`
- RMS RA/Dec ratio threshold: `2.0`

We may have this cases:

- A sub with a RMS value of `0.90` will be kept.
- A sub with a RMS value of `2.05` will be discarded.

If RMS is between the two threshold values, eccentricity will be analyzed. In this case, ratio between RA and Dec RMS must not be greater than `2.0`

- A sub with RA RMS of `0.9` and Dec RMS of `1.3` will be kept because ratio is `1.3 / 0.9 = 1.44`.
- A sub with RA RMS of `0.9` and Dec RMS of `1.9` will be discarded  because ratio is `1.9 / 0.9 = 2.11`.

### By number of stars

When discarding by stars, number of stars of each sub is compared to the number of stars of the reference sub. If that amount is below a certain threshold, the sub is discarded. For example:

- Number of stars of the reference sub: `1000`
- Threshold: `0.8`

All subs with less than 800 stars will be discarded bacause `1000 * 0.8 = 800`.

## Parameters

Parameters are optional. They all have default values.

- `--help`: Prints help.
- `--csv-file`: Path to the CSV file, with the filaname included. Default value: `example.csv`.
- `--subs-folder`: Folder where the subs are stored. Default is the current working directory.
- `--move-discarded`: If true, discarded subs will be moved to another folder. Default value: `False`. 
- `--discarded-folder`: Folder where discarded subs should be moved. Default value: `./delete`.
- `--exposure-time`: If set, the script will only process subs that matches the given exposure time.
- `--hfr-limit`: Subs with values higher than this threshold will be discarded. Default value: `3.0`.
- `--median-lower-threshold`: Lower threshold when discarding by median. Default value: `0.8`.
- `--median-upper-threshold`: Upper threshold when discarding by median. Default value: `1.05`.
- `--rms-no-check-threshold`: Subs with RMS lower than this threshold won't be analyzed. Default value: `1.0`.
- `--rms-limit`: Subs with RMS higher than this threshold will be discarded. Default value: `1.5`.
- `--rms-ra-dec-ratio-threshold`: Max RA/Dec RMS ratio. Default value `2.2`.
- `--star-count-ratio-threshold`: Star count ratio threshold. Default value is `0.75`.
- `--reference-sub-rms-limit`: RMS limit for the reference sub. Default value is `0,8`.

## Recommendations

When shooting with different exposure times / filters, it is recommended to run the script for every filter / exposure time. This is because thresholds may change from one combination to another, and running altogether would lead to false positives when discarding subs.

## Example of execution

```shell
$ python3 subs-analyzer.py 
```

The script will start and will print the configuration that will be used
```shell
Using the following configuration:
{
  "csv-file": "example.csv",
  "subs-folder": ".",
  "move-discarded": false,
  "discarded-folder": "./delete",
  "exposure-time": null,
  "hfr-limit": 3.0,
  "median-upper-thershold": 1.05,
  "median-lower-threshold": 0.8,
  "rms-no-check-threshold": 1.0,
  "rms-limit": 1.5,
  "rms-ra-dec-ratio-threshold": 2.2,
  "star-count-ratio-threshold": 0.75,
  "reference-sub-rms-limit": 0.8
}

Please press enter to contiunue:
```

After hitting enter, info about the reference sub will be printed

```shell
Reference sub:

{
  "id": "123",
  "filename": "0080_120.00s_2023-10-14_01-43-51_ L2_-5.30.fits",
  "exposure-time": "120",
  "stars": 1313,
  "hfr": 2.3706684313829847,
  "median": 2460.0,
  "rms-ra": 0.5402998428317651,
  "rms-dec": 0.36499104439216884,
  "rms": 0.6520294338835604
}

Please press enter to contiunue:
```

Then, the script will analyze and discard the bad subs. Summary will be printed

```shell
Discarded by stars:

0194_120.00s_2023-10-14_06-08-23_ L2_-4.90.fits - Stars: 983
0195_120.00s_2023-10-14_06-11-26_ L2_-5.30.fits - Stars: 847
0196_120.00s_2023-10-14_06-13-28_ L2_-4.90.fits - Stars: 622
0197_120.00s_2023-10-14_06-15-29_ L2_-5.30.fits - Stars: 859
0198_120.00s_2023-10-14_06-19-32_ L2_-4.90.fits - Stars: 952
0199_120.00s_2023-10-14_06-21-33_ L2_-4.90.fits - Stars: 962
0200_120.00s_2023-10-14_06-24-18_ L2_-5.30.fits - Stars: 935


Discarded by median:

0000_120.00s_2023-10-13_22-49-01_ L2_-5.30.fits - Median: 2680.0
0001_120.00s_2023-10-13_22-51-03_ L2_-4.90.fits - Median: 2672.0
0002_120.00s_2023-10-13_22-53-04_ L2_-4.90.fits - Median: 2668.0
0003_120.00s_2023-10-13_22-55-06_ L2_-4.90.fits - Median: 2664.0
0004_120.00s_2023-10-13_22-57-07_ L2_-4.90.fits - Median: 2660.0
0005_120.00s_2023-10-13_22-59-26_ L2_-4.90.fits - Median: 2652.0
0006_120.00s_2023-10-13_23-01-27_ L2_-4.90.fits - Median: 2652.0
0007_120.00s_2023-10-13_23-03-28_ L2_-4.90.fits - Median: 2648.0
0008_120.00s_2023-10-13_23-05-30_ L2_-5.30.fits - Median: 2636.0
0009_120.00s_2023-10-13_23-07-31_ L2_-4.90.fits - Median: 2632.0
0010_120.00s_2023-10-13_23-10-06_ L2_-5.30.fits - Median: 2628.0
0011_120.00s_2023-10-13_23-12-08_ L2_-4.90.fits - Median: 2624.0
0012_120.00s_2023-10-13_23-14-09_ L2_-5.30.fits - Median: 2600.0
0013_120.00s_2023-10-13_23-16-10_ L2_-4.90.fits - Median: 2600.0
0014_120.00s_2023-10-13_23-18-12_ L2_-4.90.fits - Median: 2600.0
0015_120.00s_2023-10-13_23-20-27_ L2_-5.30.fits - Median: 2600.0
0016_120.00s_2023-10-13_23-22-29_ L2_-4.90.fits - Median: 2596.0
0017_120.00s_2023-10-13_23-24-30_ L2_-4.90.fits - Median: 2592.0
0018_120.00s_2023-10-13_23-26-32_ L2_-4.90.fits - Median: 2584.0
0178_120.00s_2023-10-14_05-32-31_ L2_-4.90.fits - Median: 2592.0
0179_120.00s_2023-10-14_05-34-32_ L2_-5.30.fits - Median: 2596.0
0180_120.00s_2023-10-14_05-37-38_ L2_-5.30.fits - Median: 2608.0
0181_120.00s_2023-10-14_05-39-39_ L2_-4.90.fits - Median: 2616.0
0182_120.00s_2023-10-14_05-41-40_ L2_-4.90.fits - Median: 2624.0
0183_120.00s_2023-10-14_05-45-13_ L2_-4.90.fits - Median: 2644.0
0184_120.00s_2023-10-14_05-47-14_ L2_-4.90.fits - Median: 2656.0
0185_120.00s_2023-10-14_05-49-55_ L2_-4.90.fits - Median: 2668.0
0186_120.00s_2023-10-14_05-51-56_ L2_-4.90.fits - Median: 2680.0
0187_120.00s_2023-10-14_05-53-58_ L2_-4.90.fits - Median: 2688.0
0188_120.00s_2023-10-14_05-55-59_ L2_-5.30.fits - Median: 2696.0
0189_120.00s_2023-10-14_05-58-00_ L2_-5.30.fits - Median: 2704.0
0190_120.00s_2023-10-14_06-00-17_ L2_-5.30.fits - Median: 2716.0
0191_120.00s_2023-10-14_06-02-19_ L2_-4.90.fits - Median: 2724.0
0192_120.00s_2023-10-14_06-04-20_ L2_-4.90.fits - Median: 2736.0
0193_120.00s_2023-10-14_06-06-21_ L2_-4.90.fits - Median: 2748.0


Discarded by rms:

0022_120.00s_2023-10-13_23-35-18_ L2_-5.30.fits - Total RMS: 2.73 - RA RMS: 2.66 - Dec RMS: 0.63
0085_120.00s_2023-10-14_01-54-23_ L2_-5.30.fits - Total RMS: 3.20 - RA RMS: 0.71 - Dec RMS: 3.12
0095_120.00s_2023-10-14_02-25-25_ L2_-5.30.fits - Total RMS: 2.53 - RA RMS: 0.53 - Dec RMS: 2.48
0098_120.00s_2023-10-14_02-31-29_ L2_-4.90.fits - Total RMS: 1.56 - RA RMS: 0.84 - Dec RMS: 1.31
0105_120.00s_2023-10-14_02-47-05_ L2_-4.90.fits - Total RMS: 3.47 - RA RMS: 0.85 - Dec RMS: 3.37
0112_120.00s_2023-10-14_03-02-18_ L2_-5.30.fits - Total RMS: 1.70 - RA RMS: 0.73 - Dec RMS: 1.53
0122_120.00s_2023-10-14_03-26-04_ L2_-5.30.fits - Total RMS: 1.45 - RA RMS: 0.59 - Dec RMS: 1.33
0125_120.00s_2023-10-14_03-33-11_ L2_-5.30.fits - Total RMS: 2.22 - RA RMS: 0.67 - Dec RMS: 2.12
0130_120.00s_2023-10-14_03-44-21_ L2_-5.30.fits - Total RMS: 2.79 - RA RMS: 0.79 - Dec RMS: 2.67
0132_120.00s_2023-10-14_03-48-24_ L2_-4.90.fits - Total RMS: 1.79 - RA RMS: 0.66 - Dec RMS: 1.66
0157_120.00s_2023-10-14_04-44-39_ L2_-4.90.fits - Total RMS: 1.59 - RA RMS: 0.70 - Dec RMS: 1.43
0160_120.00s_2023-10-14_04-51-45_ L2_-5.30.fits - Total RMS: 2.60 - RA RMS: 0.68 - Dec RMS: 2.51
0162_120.00s_2023-10-14_04-55-48_ L2_-4.90.fits - Total RMS: 2.41 - RA RMS: 0.76 - Dec RMS: 2.29
0165_120.00s_2023-10-14_05-02-53_ L2_-5.30.fits - Total RMS: 2.94 - RA RMS: 0.55 - Dec RMS: 2.89
0167_120.00s_2023-10-14_05-06-55_ L2_-4.90.fits - Total RMS: 1.83 - RA RMS: 0.67 - Dec RMS: 1.70
0175_120.00s_2023-10-14_05-26-27_ L2_-4.90.fits - Total RMS: 1.56 - RA RMS: 0.75 - Dec RMS: 1.37
0177_120.00s_2023-10-14_05-30-30_ L2_-5.30.fits - Total RMS: 2.34 - RA RMS: 0.66 - Dec RMS: 2.25

Number of subs: 201
Number correct subs: 142
Number of discarded subs: 59
Normalized success ratio: 0.7064676616915423

Discarded subs by stars: 7
Discarded subs by median: 35
Discarded subs by RMS: 17
```

## License

This script is free, open source, and under GPLv3. More details in `LICENSE`.