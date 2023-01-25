# Polish Wikipedia Dataset

Based on [PlainTextWikipedia](https://github.com/daveshap/PlainTextWikipedia)

### Requirements
System-wide:
- wget
- bash
- bzip2
- python >= 3.7 with venv module

On Debian: `sudo apt install wget bash bzip2 python3 python3-venv`

### Usage
After installing dependencies, do:
```shell
./dl_dataset.sh           # This will download around 2-3 GB of data and decompress it
./prepare_venv.sh         # This will prepare python venv for you
./extract_dataset.sh      # This will chop Wikipedia's data into articles and print it into output directory
```