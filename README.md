# Anki Quick AI

The Anki Quick AI Addon is a powerful tool that lets you interact with OpenAI in Anki. It allows you to find and collect field values from notes, interact with OpenAI using customized prompts in multiple languages, and generate and play audio responses.

The process is:
1. Find & collect field values from Anki's notes.
2. Interact with OpenAI using custom prompts. Multiple interactions & languages supported.
3. Generate & play audio responses from OpenAI.



## Example Usage

1. Words story: Retrieve words studied today in Anki, and send them to OpenAI to asks it make a story using these words. Print the story and generate the audio files.

https://github.com/chuanqixu/anki-quick-ai/assets/33219261/a383cd74-e915-489c-adcb-a770cf8dd2ba

## Install

It has been submitted to Anki add-ons [Anki Quick AI](https://ankiweb.net/shared/info/547821970). The code is **547821970**.

To install it, click "Tools->Add-ons->Get Add-ons". In the Code section, input **547821970**, and then click OK.

## Settings

Double click "Tools->Add-ons->Anki Quick AI", and a config page with json data format will show.

1. api_key: API key for OpenAI.
2. model: OpenAI model to be used in this addon.
3. query: Query used to search for notes. The query grammar is the same as Anki browse, which can be found in the (manual)(https://docs.ankiweb.net/searching.html).
4. note_field: The field whose values will be used to replace {response} placeholder in `prompt_list`. The note field can be found in "Browse->Note Types".
5. prompt_list: A list of prompts that will be sent to OpenAI. In the prompt, you can use custom placeholders, which are sandwiched with `#`, e.x., `#language#`. Placeholders will be replaced before sending to OpenAI. It is designed for you to quickly change the prompt.
   1. `#response#`: **This is a keyword**. In the first prompt, this will be replaced with a list of strings, which are values of the `note_field` in notes searched by `query`. In other prompts, this will be replaced with the previous response from OpenAI.
   2. `#name#`: This will be replaced with the value you set in `placeholder`, see below. **Do not specify "response" as the name, since it has its special usage.**
6. placeholder: A dict contains customized placeholders. The key is the name of the placeholder. The value is another dict, whose key is the index of the prompt that will be replaced, and the value is the string to replace the placeholder. **You cannot and do not need to specify "response".**

   For example:
   ```json
   "prompt_list": [
      "My first name is #my_name#",
      "My last name is #my_name#"
   ],
   "placeholder": {
      "my_name": {
         "0": "Hello",
         "1": "World"
      }
   }
   ```
   The placeholder means in the 0th prompt, `#my_name#` will be replaced with `Hello`, and in the 1st prompt, `#my_name#` will be replaced with `World`.

7. sound_language_list: A list of language corresponding to the sound for each response.
8. play_sound: Whether to use [edge-tts](https://github.com/rany2/edge-tts) to generate the sound of the response from OpenAI.
9. automatic_display: Whether to automatic show the window choosing whether to run the addon when changing to the main page.


## Usage

Click the `Tools->` button on the menu bar in the main Anki window, and then click `AI Quick AI`. Wait for seconds for AI generation and transmission between OpenAI and your local machine. If you also generate the sound, then it may take another seconds for sound generation.


## Setup (Optional)

[add-on/lib](add-on/lib/) contains third-party libraries that are not supported by Anki. Currently, Anki add-ons require third-party libraries to be bundled with the source code.

Update third-party libraries:
```bash
cd add-on
pip install -r requirements.txt --target lib
```

## Change Log

Please find in [CHANGELOG.md](./CHANGELOG.md).



## License

This repository is under [AGPL 3.0](./LICENSE) required by AnkiWeb for Anki Add-on.

## Acknowledgement

Thanks for the inspiration and code in [yihong0618/duolingo_remember](https://github.com/yihong0618/duolingo_remember) and [yihong0618/shanbay_remember](https://github.com/yihong0618/shanbay_remember).

