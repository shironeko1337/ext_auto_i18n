### Auto i18n using Google Cloud Translation
This util helps generating `message.json` for chrome extensions.

### Usage
- Config os environment variable, variable name is configured in config.yaml, default is `osEnvAPIKey`
- Config yaml for your app, see example below.
- Run `python i18Gen.py`

### Example
This yaml file
```
targetDir: myExt\src\i18n
simpleMsg:
  - hello
  - world
indexedMsg:
  - - americanSayHello
    - Welcome to the United States of America, have a nice day!
specialCaseMsg:
  - - ms
    - en: ms
      zh_TW: 毫秒
```
Would generate two folders each with a `message.json` under `myExt\src\i18n`,
one is `myExt\src\en\messages.json`, another is `myExt\src\i18n\zh_TW\messages.json`.


- `simpleMsg` would be translated directly, the key is the message itself.
- `indexedMsg` have a data structure of `[key,value]`, value would be
translated, key is for index.
- `specialCaseMsg` would not be translated, translated text is directly configured. data structure is ['key',{'targetLanguage','targetTranslation'}]
