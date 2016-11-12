# Private Photo Cloud

Web application to provide you with private photo cloud. You could think about it as a self-hosted Apple Photo solution.

With this application you would be able to:

* Upload you photos and videos to the server
* Access you media using a web browser
* Download source files binary the same as they were uploaded

## Features

* Advanced upload capabilities:
  * Check for duplicates before upload (full content hashing)
  * Handle dozents of file (worked with 10.000 files)
  * Multi-thread upload (3 uploads in parallel)
  * [PLANNED] Upload files by chunks with resume feature
* Automatic processing and classification during upload:
  * Automatic metadata extraction from images and videos
  * Automatic generation of image and video thumbnail
  * Automatic image and video rotation according to metadata
  * [PLANNED] Automatic classification by shoot date
  * [PLANNED] Automatic grouping of RAW and JPEG images
* TODO

## Status

Currently project is in early development state.

Many features are not implemented yet, existing ones are implemented as bare minimum BUT should work.
