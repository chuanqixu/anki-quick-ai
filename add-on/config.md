Double click "Tools->Add-ons->Anki Quick AI", and a config page with json data format will show. Some of the parameters may be effective after restart Anki.

1. ai_config:
   1. api_key: API key for OpenAI.
   2. model: OpenAI model to be used in this addon.
2. query: Query used to search for notes. The query grammar is the same as Anki browse, which can be found in the (manual)(https://docs.ankiweb.net/searching.html).
3. note_field: The field whose values will be used to replace {response} placeholder in `prompt_list`. The note field can be found in "Browse->Note Types".
4. prompt_list: A list of prompts that will be sent to OpenAI. In the prompt, you can use custom placeholders, which are sandwiched with `#`, e.x., `#language#`. Placeholders will be replaced before sending to OpenAI. It is designed for you to quickly change the prompt.
   1. `#response#`: **This is a keyword**. In the first prompt, this will be replaced with a list of strings, which are values of the `note_field` in notes searched by `query`. In other prompts, this will be replaced with the previous response from OpenAI.
   2. `#language#`: **This is a keyword**. This will be replaced with `language_list` in the settings. See below.
   3. `#name#`: This will be replaced with the value you set in `placeholder`, see below. **Do not specify "response" or "language" as the name, since it has its special usage.**
5. placeholder: A dict contains customized placeholders. The key is the name of the placeholder. The value is another dict, whose key is the index of the prompt that will be replaced, and the value is the string to replace the placeholder. **You cannot and do not need to specify "response" or "language".**

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

6. language_list: A list of language corresponding to the sound for each response. Also, it will be used to replaced with the placeholder `#language#` in the prompt.
7. play_sound: Whether to use [edge-tts](https://github.com/rany2/edge-tts) to generate the sound of the response from OpenAI.
8.  automatic_display: Whether to automatic show the window choosing whether to run the addon when changing to the main page.
9.  shortcut: Shortcut to run the add-on. Do not be conflict with other shortcuts.