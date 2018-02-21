consent_list = [
# First test class
  {
    "user_id": "user1@mail.com",
    "description": "This policy was created for test purposes. The policy url is linked to Chino.io policy.",
    "policy_url": "https://www.chino.io/legal/privacy-policy",
    "policy_version": "test",
    "collection_mode": "none",
    "data_controller": {
      "company" : "Chino.io",
      "contact" : "controller",
      "address" : "Via S.G. Bosco 27, 38068 Rovereto",
      "email" : "controller@mail.com",
      "VAT" : "n/d",
      "on_behalf" : true
    },
    "purposes": [
      {
          "authorized": true,
          "purpose": "testing",
          "description" : "Testing class api.ChinoAPIConsents"
      },
      {
          "authorized": false,
          "purpose": "testing",
          "description" : "Testing class objects.Consent"
      }
    ]
  },

# Second test class
  {
    "user_id": "user2@mail.com",
    "description": "This policy was created for test purposes. The policy url is linked to Chino.io policy.",
    "policy_url": "https://www.chino.io/legal/privacy-policy",
    "policy_version": "test",
    "collection_mode": "none",
    "data_controller": {
      "company" : "Chino.io",
      "contact" : "controller",
      "address" : "Via S.G. Bosco 27, 38068 Rovereto",
      "email" : "controller@mail.com",
      "VAT" : "n/d",
      "on_behalf" : true
    },
    "purposes": [
      {
          "authorized": true,
          "purpose": "testing",
          "description" : "Testing class api.ChinoAPIConsents"
      },
      {
          "authorized": false,
          "purpose": "testing",
          "description" : "Testing class objects.Consent"
      }
    ]
  }
]
