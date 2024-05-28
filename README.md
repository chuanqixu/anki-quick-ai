# Anki Quick AI

**This add-on is actively developing. Configuration parameters may be changed when the add-on was updated, but Anki does not automatically change the old configuration.**

**After updating the add-on, please go to the add-on configuration page and click "Restore Defaults". Sorry for the inconvenience!**

The Anki Quick AI Addon is a powerful tool that lets you interact with OpenAI in Anki. It allows you to quickly collect field values from notes, interact with OpenAI using customized prompts in multiple languages, and show and play audio responses.

Features:

1. Find & collect field values from Anki's notes.

2. Interact with OpenAI using custom prompts. Multiple interactions are supported.

3. Show & play audio of responses from OpenAI.



## Example Usage

1. Words story: Retrieve words studied today in Anki, and send them to OpenAI to ask it to make a story using these words. Print the story and generate the audio files.

https://github.com/chuanqixu/anki-quick-ai/assets/33219261/5e71caba-b20f-41a1-beaa-63bf90f5a95a

## Install

It has been submitted to Anki add-ons [Anki Quick AI](https://ankiweb.net/shared/info/547821970). The code is **547821970**.

To install it, click "Tools->Add-ons->Get Add-ons". In the Code section, input **547821970**, and then click OK.


## Usage

**Please configure the add-on before the first time you use it.**

There are several ways to run the add-on:

1. Click the `Tools` button on the menu bar in the main Anki window, and then click `Anki Quick AI`. Wait for seconds for AI generation and transmission between OpenAI and your local machine. If you also generate the sound, then it may take other seconds for sound generation.

2. In the Browse window, click the `Anki Quick AI` button on the menu bar.

3. If `shortcut` is set, you can use it to run the add-on. The default shortcut is `Alt+A`.

4. If `automatic_display` is set to be `true`, then the add-on will automatically run if you change to the main deck window. For example, when you finish one deck, or when you change to the deck window from the study window.

## Settings

Double click "Tools->Add-ons->Anki Quick AI", and a config page will show. Some of the parameters may be effective after restarting Anki. You should add "api_key" and "model" in the "AI" tag of the config page.

Hover your mouse for tooltips of parameters in the configuration window.

For usage, you should create your default prompt settings in the "prompt" tag of the config page. The settings are the following:

1. Prompt Name: A name for this prompt configuration.
2. Default Browse Query: Query used to search for notes. The query grammar is the same as Anki browse, which can be found in the [official manual](https://docs.ankiweb.net/searching.html).
3. Note Field Configuration: Only note values with the specified fields will be selected. "Other Note Type" will be used for unspecified note types.
4. Prompt: A list of prompts that will be sent to OpenAI. In the prompt, you can use custom placeholders, which are sandwiched with `#`, e.x., `#language#`. Placeholders will be replaced before sending to OpenAI. It is designed for you to quickly change the prompt.
   1. `#field_value#`: **This is a keyword**. This will be replaced with a list of strings, which are values of the `note_field` in notes searched by `query`.
   2. `#response#`: **This is a keyword**. This will be replaced with the previous response from OpenAI.
   3. `#language#`: **This is a keyword**. This will be replaced with `language_list` in the settings. See below.
   4. `#custom#`: You can specify your custom placeholder. This will be replaced with the value you set in `placeholder`, see below. **Do not specify "field_value", "response", or "language" as the name, since they have their special usage.**
5. placeholder: A dict contains customized placeholders. The key is the name of the placeholder. The value is another dict, whose key is the index of the prompt that will be replaced, and the value is the string to replace the placeholder. **You cannot and do not need to specify "field_value", "response", or "language".**
6.language: Languages for the generated audio.

## Custom API Provider

1. Provider API (Directory `add-on/ai/provider`):
    1. Create a new provider in the directory by name `provider_{provider_name}.py`
    2. Add to the beginning: `from .provider import Provider`
    3. Define the class `Provider{provider_name}` and inherit from `Provider`
    4. Implement: 1. `get_client()`; 2. `__call__()`; 3. `get_avail_chat_model_list()`. Please see example of [provider_openai.py](./add-on/ai/provider/provider_openai.py)
    5. Add arguments for the provider in `meta.json: ai_config` in the directory`add-on`
2. Provider setting and configure GUI (Directory `add-on/gui/provider`)
    1. Create a new config layout for a provider in the directory by name `ai_config_layout_{provider_name}.py`
    2. Add to the beginning: `from .ai_config_layout import AIConfigLayout`
    3. Define the class `AIConfigLayout{provider_name}` and inherit from `AIConfigLayout`
    4. Implement: `advanced()` if needed
    5. Add arguments for the provider `in meta.json: ai_config`

## Setup (Optional)

[add-on/lib](add-on/lib/) contains third-party libraries that are not supported by Anki. Currently, Anki add-ons require third-party libraries to be bundled with the source code.

Update third-party libraries:
```bash
cd add-on
pip install -r requirements.txt --target lib
```

## Change Log

Please find in [CHANGELOG.md](./CHANGELOG.md).

## Local Usage (Deprecated)

It also provides a local Python program for this in [src](./src/), but this is not maintained anymore. The latest version is to use the Anki add-on.


## License

This repository is under [AGPL 3.0](./LICENSE) required by AnkiWeb for Anki Add-on.

## Acknowledgement

Thanks for the inspiration and code in [yihong0618/duolingo_remember](https://github.com/yihong0618/duolingo_remember) and [yihong0618/shanbay_remember](https://github.com/yihong0618/shanbay_remember).

Thanks for [BlueGreenMagick/ankiaddonconfig](https://github.com/BlueGreenMagick/ankiaddonconfig) for configuration window.

Thanks for @marquiswang. It is now ported to Anki 23.10.
