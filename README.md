# GBXT2B
GBXT2B, for **GBX** **T**ext **To** **B**inary, is a tool that converts the text-formatted GBX files to a binary format so they can be used with other parsing libraries.

Unfortunately, due to very inconsistent formatting by Nadeo when making text GBX files, there's not really a way to automatically convert without a fair bit of hardcoding, so if you get an error, please [open an issue](https://github.com/LinUwUxCat/GBXT2B/issues/new/choose) with your file.
### Usage
Run `python3 main.py Path/To/Your/File.Gbx`. The resulting file will be at Path/To/Your/B_File.Gbx ( __/!\\__ It will overwrite any existing file)
### Known working files
Not every format is fully implemented, so it's hard to provide a list.\
Here is a small list of files I could get to work:
|      File Name     |        Notes        |
|--------------------|---------------------|
| MainBody.Solid.Gbx | From TMS Opel Demo  |