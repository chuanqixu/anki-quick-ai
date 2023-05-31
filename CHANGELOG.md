# CHANGELOG

**This add-on is actively developing. Configuration parameters may be changed when the add-on was updated, but Anki does not automatically change the old configuration.**

**Please go to the add-on configuration page and click "Restore Defaults". Sorry for the inconvenience!**


### Version **1.0.2** 2023-05-31

Added

* Now support streamed and real time response!

Changed

* Replace `#field_value#` as the placeholder for field values. Previously, `#response#` is used for this in the first prompt and nothing will be used in the following prompts.


Fixed

* No directory of sound files if 'play_sound' is set to false.

### Version **1.0.1** 2023-05-27

Added

* Support quickly change query and note_field in the pop-up window. This will not change the default configuration.
* Add a "Quick AI" button to the browse window to quickly click when checking the browse query, the query will be the current input query in the browse window.
* Add a shortcut to run it quickly in the main window.
* Support adding customized placeholders in prompts.
* Support HTML tags in response.

Changed

* Remove the progress bar of interacting with OpenAI so Anki is not blocked.
* Change configuration files.
* Change the response window. Now the texts can be copied.

Fixed

* Sometimes it does not have permission to override the sound file.

### Version **1.0.0** -- 2023-05-22

First Version