import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./app/prepdocs/.env')

cognitive_search_url = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
api_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY')

skill_name = os.getenv('LINE_BOT_NAME') + os.getenv('SKILLSET_NAME')

request_body = {
  "description": "",
  "skills":
  [
    {
      "@odata.type": "#Microsoft.Skills.Text.V3.EntityRecognitionSkill",
      "context": "/document/merged_content",
      "categories": [
        "URL",
        "Event",
        "IPAddress",
        "Person",
        "Organization",
        "Skill",
        "Quantity",
        "Product",
        "DateTime",
        "Email",
        "Address",
        "PhoneNumber",
        "Location",
        "PersonType"
      ],
      "defaultLanguageCode": "ja",
      "minimumPrecision": 0.8,
      "inputs": [
        { "name": "text", "source": "/document/merged_content" },
        { "name": "languageCode", "source": "/document/language" }
      ],
      "outputs": [
        { "name": "persons", "targetName": "people" },
        { "name": "organizations", "targetName": "organizations" },
        { "name": "locations", "targetName": "locations" }
      ]
    },
    {
    "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
      "context": "/document/merged_content",
      "defaultLanguageCode": "ja",
      "maxKeyPhraseCount": 20,
      "inputs": [
        { "name": "text", "source": "/document/merget_content" },
        { "name":"languageCode", "source": "/document/language" }
      ],
      "outputs": [
        { "name": "keyPhrases", "targetName": "keyPhrases" }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
      "context": "/document",
      "inputs": [
        { "name": "text", "source": "/document/merged_content" }
      ],
      "outputs": [
        { "name": "languageCode", "targetName": "language" }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
      "context": "/document",
      "insertPreTag": " ",
      "insertPostTag": " ",
      "inputs": [
        { "name": "text", "source": "/document/content" },
        { "name": "itemsToInsert", "source": "/document/normalized_images/*/text" },
        { "name": "offsets", "source": "/document/normalized_images/*/contentOffset" }
      ],
      "outputs": [
        { "name": "mergedText", "targetName": "merged_content" }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
      "context": "/document/normalized_images/*",
      "lineEnding": "Space",
      "defaultLanguageCode": "ja",
      "detectOrientation": True,
      "inputs": [
        { "name": "image", "source": "/document/normalized_images/*" }
      ],
      "outputs": [
        { "name": "text", "targetName": "text" },
        { "name": "layoutText", "targetName": "layoutText" }
      ]
    },
    {
      "@odata.type": "#Microsoft.Skills.Vision.ImageAnalysisSkill",
      "context": "/document/normalized_images/*",
      "defaultLanguageCode": "ja",
      "visualFeatures": [
        "tags",
        "description"
      ],
      "inputs": [
        { "name": "image", "source": "/document/normalized_images/*" }
      ],
      "outputs": [
        { "name": "tags", "targetName": "imageTags" },
        { "name": "description", "targetName": "imageCaption" }
      ]
    }
  ],
  # "cognitiveServices": {
  #   "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
  #   # "key":"<Your-Cognitive-Services-Multiservice-Key>"
  #   "key":"146433e88e624c3484d93fbe53f4b1e0"
  # }
}

headers = { "api-key " : api_key, "Content-Type" : "application/json" }
ret = requests.put(cognitive_search_url + f"/skillsets/{skill_name}?api-version=2020-06-30", headers=headers, data=json.dumps(request_body))

print(ret)
