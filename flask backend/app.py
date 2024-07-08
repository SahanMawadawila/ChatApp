from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

#download the necessary resources for tokenization and lemmatization
nltk.download('punkt')
nltk.download('wordnet')
app = Flask(__name__)
CORS(app)

def greet():
    return "Hello! I am your assistant. What's your name?"


#potential negative responses
negative_responses = ("no", "nope", "nah", "naw", "sorry")
  #keywords for exiting the conversation
exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later","thank","thanks","stop","done")
  #random starter questions
random_questions = (
        "How can I assist you today?\n",
        "What can I do for you today?\n",
        "What are you looking for today?\n",
        "How can I help you today?\n",
        "What do you need help with today?\n",
        "what are things are you going to buy today?\n"
    )

wordDictionary = {
  "searching_shelf_number": r"shel(f|ves)\b",  # Corrected to match "shelf" and "shelves"
  "searching_price": r"price(?:s)?\b",  # Matches "price" and "prices"
  "searching_quantity": r"quantit(y|ies)?\b"  # Correctly matches "quantity" and "quantities"
}

def find_item_details(words, detail_type):
  item_with_shelf_number ={}
  #open txt file which contains the details in the supermarket
  with open("itemLists.txt", "r") as file:
    for line in file:
      # Split the line by comma
        item_name, shelf_number, price, quantity = line.strip().split(',')
       # iterate through the words
        for word in words:
          # Check if the word is in the line
          if word == item_name:
            if detail_type == "shelf_number":
              item_with_shelf_number[item_name] = shelf_number
            elif detail_type == "price":
              item_with_shelf_number[item_name] = price
            elif detail_type == "quantity":
              item_with_shelf_number[item_name] = quantity
  return item_with_shelf_number

def preprocess_text(text):
  #tokenize the reply
    tokens = word_tokenize(text)

    #convert plural words to singular ( lemmatization)
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens

#remove punctuation from string
def remove_punctuation(text):
  return text.translate(str.maketrans("", "", string.punctuation))

def match_reply(reply):
  for key, value in wordDictionary.items():
      intent = key
      regex = value
      found = re.search(regex, reply)
      if found:
          if intent == "searching_shelf_number":
              return search_shelf_number(reply)
          elif intent == "searching_price":
              return search_price(reply)
          elif intent == "searching_quantity":
              return search_quantity(reply)
  # If no matches were found in the loop, then return no match intent
  return no_match_intent()

def search_shelf_number(reply):
  response = (
    "Do you want to know more details?\n",
    "I can assist you with that. Do you want to know more details?\n",)

  lemmatized_tokens = preprocess_text(reply)
  #search for shelf number
  item_with_shelf_number = find_item_details(lemmatized_tokens, "shelf_number")

  response1 =""
  if(len(item_with_shelf_number) == 0):
    return "Sorry, I couldn't find the item you are looking for. Do you want to search for something else?\n"
  for item, shelf_number in item_with_shelf_number.items():
    response1 += f"*{item} is available in shelf number {shelf_number}\n"
  
  return response1 + random.choice(response)

def search_price(reply):
  response = (
    "If you have any other questions, feel free to ask.\n",
    "I'm happy to help. Do you have any other questions?\n",
    "If you need more information, feel free to ask.\n")
  
  lemmatized_tokens = preprocess_text(reply)
  #search for price
  item_with_price = find_item_details(lemmatized_tokens, "price")

  if(len(item_with_price) == 0):
    return "Sorry, I couldn't find the item you are looking for. Do you want to know about price of another item?\n"
  response1 =""
  for item, price in item_with_price.items():
    response1 += f"*{item} is available at Rs.{price} per item\n"

  return response1 + random.choice(response)

def search_quantity(reply):
  response = (
    "need my help with anything else?\n",
    "Do you clarify anything else?\n",
  )
  lemmatized_tokens = preprocess_text(reply)
  #search for quantity
  item_with_quantity = find_item_details(lemmatized_tokens, "quantity")

  if(len(item_with_quantity) == 0):
    return "Sorry, I'm unable to find the item you are looking for. Do you want to know about quantity of another item?\n"
  response1 =""
  for item, quantity in item_with_quantity.items():
    response1 += f"*{item} is available in quantity {quantity}\n"
  
  return response1 + random.choice(response)
  
def no_match_intent():
  response =(
    "plesase tell me more\n",
    "I am not sure what you are looking for. Can you tell me more?\n",
    "Could you provide more details?\n",
    "I'm sorry, I don't understand. Can you provide more details?\n"
  )
  return random.choice(response) 
    

@app.route('/api/message', methods=['POST'])
def message():
    data = request.json
    user_message = remove_punctuation(data.get('message').lower())
    counter = data.get('counter')
    is_question = data.get('isQuestion')
    if counter == 0:
        return jsonify({'response': greet()})
    elif counter == 1:
      return jsonify({'response': "Hello, " + user_message + "! Are you here for shopping today?"})
    
    else :
        if any(word in negative_responses for word in user_message.split()):
            return jsonify({'response': "Okay, have a great day!","counter": True})
        elif any(word in exit_commands for word in user_message.split()):
            return jsonify({'response': "Thank you for shopping with us! Have a great day!", "counter": True})
        
        else:
            if(is_question == False):
              return jsonify({'response': random.choice(random_questions), 'question': True})
            else:
                return jsonify({'response': match_reply(user_message), 'question': True})
                
            
              
if __name__ == '__main__':
    app.run(port=5000)