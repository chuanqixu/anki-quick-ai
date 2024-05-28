# CHANGELOG

**This add-on is actively developing. Configuration parameters may be changed when the add-on was updated, but Anki does not automatically change the old configuration.**

**Please go to the add-on configuration page and click "Restore Defaults". Sorry for the inconvenience!**

### Version **1.0.9** 2024-04-28

(In this update, changes have been made to the structure of the configuration file)

Added

* Option to select AI Provider: Now you can choose between OpenAI or Groq API for inference.
* Browser Note Selection: Your query will dynamically update based on the cards you select.
* Enhanced Browser Menu: Introducing an additional "Anki Quick Ai" option in the context menu of browser cards.
* Agentic Behavior: Cards can be updated using AI output resulting in a dedicated thread per note along with its fields.
* New Placeholder #json_fields#: Representing an expected JSON string returned by the AI model, intended to be managed by the agent.

### Version **1.0.8** 2024-01-15

Changed

* Update to the latest version of OpenAI library

Fixed

* Fixed the bugs when deleting prompts due to the issues when Anki updates to PyQt 6.6

### Version **1.0.7** 2024-01-14

Changed

* Thanks for @quinn-p-mchugh. Models are now not hardcoded.

### Version **1.0.6** 2023-11-29

Fixed

* Thanks for @marquiswang. It is now ported to Anki 23.10.


### Version **1.0.5** 2023-06-16

Added

* System prompt.
* Note field configurations for note types.

Changed

* Now model is drop down menu.
* Remove note field and replace it with note field configuration.
* Now prompt configuration dialog is scrollable.

### Version **1.0.4** 2023-06-12

Added

* Interaction with OpenAI in the response dialog.

Changed

* Move audio widget below each response widget.

### Version **1.0.3** 2023-06-07

Added

* Add configuration GUI. Now configuration is more clear and straightforward!
* Support multiple predefined prompt.
* Run again button to generate new response.
* Sliders for audio.
* Specify edge-tts voice.

Changed

* Now can quickly change prompt and placeholder before running.

Fixed

* Sometimes it does not have permission to override the sound file.


### Version **1.0.2** 2023-05-30
 
Added

* Now support streamed and real-time response.
* Add buttons to save texts and audio files at the end of the dialog.

Changed

* Replace `#field_value#` as the placeholder for field values. Previously, `#response#` is used for this in the first prompt and nothing will be used in the following prompts.
* Disabled HTML representation in the dialog.

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

First Version.