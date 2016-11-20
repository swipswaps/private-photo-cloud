# Features specification

This document explains features specification, specified as user stories.


## Upload

* User may upload files dropping them anywhere on the page
* User may manually select files to upload using OS-specific files picker
* All provided files are automatically uploaded without user confirmation
* [TODO] User may drop or select folders, then all contained files would be uploaded
    * [BLOCKER] There is no relevant web standard for this
    * Update: Chrome and Firefox has it <https://developer.mozilla.org/en-US/Firefox/Releases/50#Files_and_directories>
* User may select HUGE number (10K) of files for upload
* [TODO] User may upload HUGE files (~ 8Gb)
* [TODO] User may resume upload that was interrupted before
* Most relevant files are uploaded first (smallest; images, videos, other files)
* User may upload any file, not just image or video
* User sees the progress of upload batch
* User sees the result of upload batch (e.g. thumbnails of images and videos)
* Upload consumes as much bandwidth as possible
* Upload guarantees that files were not corrupt or altered during transfer from user
* Upload takes as much metadata as provided by user browser (file name, modification time, etc.)
* User may provide files that were already uploaded before. That must give the same results but much faster.
  * Already uploaded files must not be uploaded (e.g. to be checked whether it is a duplicate)
* User may provide duplicate files in the same upload batch. That must give about the same result but without duplicates.
  * Only one version of duplicate file in upload batch must be uploaded
* [TODO] User may adjust results of upload batch (e.g. rotate, add a comment, change date, group photos) on the same page

## De-duplication

* Binary identical (i.e. by content) files are treated as duplicates
* Within given user -- storing duplicates is technically not possible
  * Different users could have the same file
* [ABSTRACT] Different versions of the same image are treated as different "media" for the same "shot"
  * They may have slightly different resolution and shot date
  * [TODO] JPEG and RAW images are treated as the same "shot" but different "media"
  * [TODO] SDR/LDR and HDR images are treated as the same "shot" but different "media"
  * [TODO] Burst are treated as the same "shot" but different "media"
* Files without metadata are excluded from duplication check
  * [FUTURE] Extraction of binary part of the image makes some sense for duplication while some applications strip metadata without re-compression (e.g. iOS)
  * [FUTURE] Comparison of images by content is a complex topic and might be implemented in future
