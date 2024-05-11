import yaml
import os
import json
from collections import defaultdict
import requests
import sys

with open('config.yaml', 'rb') as f:
  data = yaml.safe_load(f)
  messagesLanguage = data['messagesLanguage']
  languages = data['languages'] or []
  outputFile = data['outputFile']
  osEnvAPIKey = data['osEnvAPIKey']
  cacheFile = data['cacheFile']
  for root, dirs, files in os.walk('.'):
      if root == '.':
        for file in files:
          if file.endswith('yaml') and file != 'config.yaml':
              with open(file, 'rb') as f:
                data = yaml.safe_load(f)
                if data:
                  targetDir = data['targetDir']
                  simpleMsg = data['simpleMsg'] or []
                  indexedMsg = data['indexedMsg'] or []
                  specialCaseMsg = data['specialCaseMsg'] or []

                  apiKey = sys.argv[1] if len(sys.argv) == 2 else os.environ[osEnvAPIKey]

                  cached = defaultdict() # key = language__message, value = translation
                  def getCachedKey(language,message):
                      return f'{language}__{message}'
                  if os.path.exists(cacheFile):
                    with open(cacheFile, 'r') as f:
                        cached = json.load(f)

                  res = defaultdict(lambda: defaultdict())

                  messages = [x for x in simpleMsg] + [v for k, v in indexedMsg]

                  for language_config in languages:
                      language = language_config['code']
                      languageDir = language_config['dir']

                      requestIndices,requestMessages = set(),[]

                      for i,message in enumerate(messages):
                        cacheKey = getCachedKey(language,message)
                        if cacheKey not in cached:
                            requestMessages += [message]
                            requestIndices.add(i)

                      if requestMessages:
                        response = requests.post('https://translation.googleapis.com/language/translate/v2',
                                                params={
                                                    'q': requestMessages,
                                                    'target': language,
                                                    'source': messagesLanguage,
                                                    'key': apiKey
                                                })

                        jsonRes = response.json()
                        print(f'translation to {language} for {requestMessages}: {jsonRes}')

                      j = 0
                      for i, message in enumerate(messages):
                          cachedKey = getCachedKey(language,message)
                          if i in requestIndices:
                              translation = jsonRes['data']['translations'][j]['translatedText']
                              cached[getCachedKey(language,message)] = translation
                              j += 1
                          else:
                              # skip cached
                              translation = cached[cachedKey]
                          # print(message,translation)
                          if i < len(simpleMsg):
                              key = simpleMsg[i].replace(' ','_')
                              desc = simpleMsg[i]

                              upcase, lowercase = key[0].upper(
                              ) + key[1:], key[0].lower() + key[1:]
                              for _key in set([upcase, lowercase, key]):
                                  res[languageDir][_key] = {
                                      'message': translation,
                                      'desc': desc,
                                  }
                                  res[messagesLanguage][_key] = {
                                      'message': _key,
                                      'desc': desc,
                                  }
                          else:
                              i -= len(simpleMsg)
                              key = indexedMsg[i][0].replace(' ','_')
                              desc = indexedMsg[i][1]

                              res[languageDir][key] = {
                                  'message': translation,
                                  'desc': desc,
                              }
                              res[messagesLanguage][key] = {
                                  'message': desc,
                                  'desc': desc,
                              }
                  for key, v in specialCaseMsg:
                      for language, translate in v.items():
                          res[language][key] = {
                              'message': translate,
                              'desc': key
                          }

                  for languageDir, messages in res.items():
                      outputFilePath = f'{targetDir}/{languageDir}/{outputFile}'
                      os.makedirs(os.path.dirname(outputFilePath), exist_ok=True)
                      with open(outputFilePath, 'w') as f:
                          json.dump(messages, f, indent=4)

                  with open(cacheFile,'w') as f:
                      json.dump(cached,f,indent=1)
