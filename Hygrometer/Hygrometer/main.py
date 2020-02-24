# Bot's name - 'Hygrometerbot' 
# User name 'hygrometerbot'
import telebot
import datetime
from Hygrometer import Hygrometer
from DataStorage.Amendments import Amendment1
from DataStorage.HumidityTables import HumidityTable1
from telebot import types
print(str(datetime.datetime.now()), "Telegram bot (v1.0) has started")
bot = telebot.TeleBot("925726841:AAEclsVk5bYXshpcMdCOflM1kCzjEpx2nbU")

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def ValidateInputedValues(telebot, message, strDryTemp, strWetTemp = "0"):
   if isFloat(strDryTemp) == False:
      telebot.send_message(message.from_user.id, "The value is not numeric. Please enter correct Dry measure") 
      print(str(datetime.datetime.now()), " ", "Error: Incorrect Dry value - ", strDryTemp)
      bot.register_next_step_handler(message, SetDryTemp)  
      return False
   elif isFloat(strWetTemp) == False:
      telebot.send_message(message.from_user.id, "The value is not numeric. Please enter correct Wet measure") 
      print(str(datetime.datetime.now()), " ", "Error: Incorrect Wet value - ", strWetTemp)
      bot.register_next_step_handler(message, SetWetTemp)  
      return False
   elif float(strWetTemp) >= float(strDryTemp):
      telebot.send_message(message.from_user.id, "The Wet measure should be less than Dry measure. Please enter correct Wet measure") 
      print(str(datetime.datetime.now()), " ", "Error: Wet value more or equally then Dry - ", strWetTemp)
      bot.register_next_step_handler(message, SetWetTemp)  
      return False
   return True

@bot.message_handler(content_types=["text"])
def any_msg(message):
   print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Session has started")
   keyboard = types.InlineKeyboardMarkup()
   callback_VIT1 = types.InlineKeyboardButton(text="VIT1", callback_data="vit1")
   callback_VIT2 = types.InlineKeyboardButton(text="VIT2", callback_data="vit2")
   keyboard.add(callback_VIT1)
   keyboard.add(callback_VIT2)
   bot.send_message(message.chat.id, "Please select model", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
   if call.message:
          
      if call.data == "vit1":                                    
         SetModel(call.message, model = 1)         
      elif call.data == "vit2":                           
         SetModel(call.message, model = 2)        

def SetModel(message, model):
   global _model  
   _model = model
   print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Model = ", _model)
   bot.edit_message_text(chat_id = message.chat.id, message_id = message.message_id, text = "Please enter Dry measure of VIT" + str(_model))
   bot.register_next_step_handler(message, SetDryTemp)

def SetDryTemp(message):   
   global _dryTemp
   if ValidateInputedValues(telebot = bot, message = message, strDryTemp = message.text) == True:
      _dryTemp = round(float(message.text), 2)
      print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "DryTemp = ", str(_dryTemp))
      bot.send_message(message.from_user.id, "Please enter Wet measure of VIT"+str(_model))  
      bot.register_next_step_handler(message, SetWetTemp)  

def SetWetTemp(message):   
   global _wetTemp
   global RelativeHumidity
   if ValidateInputedValues(telebot = bot, message = message, strDryTemp = str(_dryTemp), strWetTemp = message.text) == True: 
      try:
         _wetTemp = round(float(message.text), 2)   
         print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "WetTemp = ", str(_wetTemp))
         Hygrom1 = Hygrometer(Amendment1, HumidityTable1)
         errorMsg = []
         RelativeHumidity = Hygrom1.GetRelativeHumidity(_dryTemp, _wetTemp, errorMsg)  
         if len(errorMsg) != 0:
            bot.send_message(message.from_user.id, errorMsg[0])  
            print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Error:", errorMsg[0])            
            return
         bot.send_message(message.from_user.id, 'Relative Humidity is:  '+ str(RelativeHumidity) + '%')  
         print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Relative Humidity is", str(RelativeHumidity), '%')
      except Exception as e:
         print(str(datetime.datetime.now()), "  ", "EXCEPTION: error during RelativeHumidity calculating")

bot.polling(none_stop = True)