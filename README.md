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
  * Multi-threaded upload (3 uploads in parallel)
  * [PLANNED] Upload files by chunks with resume feature
* Automatic processing and classification during upload:
  * Automatic metadata extraction from images and videos
  * Automatic generation of image (also RAW) and video thumbnail
  * Automatic image and video rotation according to metadata
  * [PLANNED] Automatic classification by shoot date
* De-duplicating capabilities:
  * Binary duplicates are not possible (check full content hash)
  * [PLANNED] Automatic grouping of RAW and JPEG images as a single photo
  * [PLANNED] Automatic grouping of images shot at the same time as a single shot
  * [PLANNED] Automatic grouping of images shot as about the same tim as a single shot-burst
* TODO

See [Ideas list](IDEAS.md)

## Ideal use case

* Plug camera + open web site / run mobile app
* Upload all photos and videos
* Go to "Memories" list
* Group memories, fine-tune them
* See memories on mobile (app), desktop (browser) or TV
* Print memories as photos or album

## Why

* Web-based
* Self-hosted
* Better import (speed, number of files handled)
* Built-in de-duplicating
* Built-in grouping of media into shots / shot bursts

## Status

Currently project is in early development state.

Many features are not implemented yet, existing ones are implemented as bare minimum BUT should work.

### De-duplication strategy

Application tries to handle common duplication cases:

* Same image shoot as JPEG and RAW
  * Has the same device
  * Taken at the same time
* TODO
