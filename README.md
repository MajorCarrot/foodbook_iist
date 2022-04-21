# foodbook

## Runnning the code
To run the code:

1. Download the repository as a zip file (on the top RHS of the github page)
   and unzip the folder.
1. Modify the `Booking_Prefs.yml` file based on your preferences. - *Only once*
1. Install any version of `python` above 3.3 for windows from the microsoft
   store (it is included in linux by default). - *Only once*
1. Install pyyaml (`python -m pip install PyYaml`) - *Only once*
1. Open the command line and navigate to the location of the unzipped folder.
1. Run `python book.py -c "Booking_Prefs.yml" -i <Your SC Code here> -p <Your
   Password here>` - whenever you want to book (2 weeks by default)


## Configuring Preferences
You can configure your booking preferences in the `Booking_Prefs.yml` file
inside this repository.

- For the odd week modify preferences under `Week1` key of the yaml file and
  for the even week modify those under `Week2`
- `all_days` represents the preferences for all days of that particular week.
  You can mention your general preferences here (marking non-veg dishes as
  `false` for vegetarians, marking everything under `Dinner` as `false` if you
  don't have dinner from the mess etc.)
- Under the preferences for each day, you can mention the meals you want to
  skip for that day (following the same pattern as `all_days`)


## Booking or skipping for a particular period
There are options to book or skip particular days. These can be found by
running `python book.py -h`

```
usage: foodbook [-h] [-s SKIP_DATES [SKIP_DATES ...]] [--skip_from SKIP_FROM] [--skip_till SKIP_TILL] [-b BOOK_DATES [BOOK_DATES ...]]
                [--book_from BOOK_FROM] [--book_till BOOK_TILL] -c CONFIG -p PIN -i ID [-v]

IIST food booking tool

optional arguments:
  -h, --help            show this help message and exit
  -s SKIP_DATES [SKIP_DATES ...], --skip_dates SKIP_DATES [SKIP_DATES ...]
                        Dates to skip
  --skip_from SKIP_FROM
                        Starting date for days to skip (--skip_till is required while using this)
  --skip_till SKIP_TILL
                        Ending date for days to skip (--skip_from is required while using this)
  -b BOOK_DATES [BOOK_DATES ...], --book_dates BOOK_DATES [BOOK_DATES ...]
                        Dates to book
  --book_from BOOK_FROM
                        Starting date for days to book (--book_till is required while using this)
  --book_till BOOK_TILL
                        Ending date for days to book (--book_from is required while using this)
  -c CONFIG, --config CONFIG
                        Config file
  -p PIN, --pin PIN     PIN
  -i ID, --id ID        ID
  -v, --version         show program's version number and exit
```

<b>
Note: The format assumed for dates is `YYYY-MM-DD`. Follow that while passing
the option.

Also note that `--skip_dates` takes multiple dates as argument and so does
`--book_dates`. These can be directly specified `DATE1 DATE2` or specified with
a square bracket around it `[DATE1 DATE2]`
</b>


## Licensing
This project is distributed under the [LGPL v2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html), see [LICENSE](https://github.com/MajorCarrot/foodbook_iist/blob/main/LICENSE) for more information.
