import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyDxAl_LSB7CiI48qMjYchuo3H90bfaT0SQ",
  "authDomain": "resume-builder-69ce7.firebaseapp.com",
  "projectId": "resume-builder-69ce7",
  "storageBucket": "resume-builder-69ce7.appspot.com",
  "messagingSenderId": "872884368036",
  "appId": "1:872884368036:web:7f2f9af6b65488c7da6c31",
  "databaseURL":"https://resume-builder-69ce7-default-rtdb.firebaseio.com/",
};


firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()