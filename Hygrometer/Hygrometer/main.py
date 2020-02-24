# Bot's name - 'Hygrometerbot' 
# User name 'hygrometerbot'
import telebot
import datetime
from Hygrometer import Hygrometer
from DataStorage.Amendments import Amendment1
from DataStorage.HumidityTables import HumidityTable1
from telebot import types
print(str(datetime.datetime.now()), "Telegram bot (v1.1) has started")
bot = telebot.TeleBot("925726841:AAEclsVk5bYXshpcMdCOflM1kCzjEpx2nbU")

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
   # Если сообщение из чата с ботом
   if call.message:
      global model      
      if call.data == "vit1":                                    
         print(str(datetime.datetime.now()), " ", str(call.message.message_id),"  ", "Model = VIT1")
         model = 1
         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please enter Dry measure of VIT1")
         bot.register_next_step_handler(call.message, SetDryTemp)
      elif call.data == "vit2":                           
         print(str(datetime.datetime.now()), " ", str(call.message.message_id),"  ", "Model = VIT2")
         model = 2
         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please enter Dry measure of VIT2")
         bot.register_next_step_handler(call.message, SetDryTemp)

def SetDryTemp(message):   
   global dryTemp
   if message.text.isnumeric() == False:
      bot.send_message(message.from_user.id, "The value is not numeric. Please enter correct Dry measure") 
      print(str(datetime.datetime.now()), " ", "Incorrect value - ", message.text)
      bot.register_next_step_handler(message, SetDryTemp)  
   else:
      dryTemp = round(float(message.text), 2)
      print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "DryTemp = ", str(dryTemp))
      bot.send_message(message.from_user.id, "Please enter Wet measure of VIT"+str(model))  
      bot.register_next_step_handler(message, SetWetTemp)  

def SetWetTemp(message):   
   global wetTemp
   global RelativeHumidity
   if message.text.isnumeric() == False:
      bot.send_message(message.from_user.id, "The value is not numeric. Please enter correct Wet measure")
      print(str(datetime.datetime.now()), " ", "Incorrect value - ", message.text)
      bot.register_next_step_handler(message, SetWetTemp)  
   else:
      wetTemp = round(float(message.text), 2)   
      print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "WetTemp = ", str(wetTemp))
      try:
         Hygrom1 = Hygrometer(Amendment1, HumidityTable1)
         RelativeHumidity = round(Hygrom1.GetRelativeHumidity(dryTemp, wetTemp), 2)     
         bot.send_message(message.from_user.id, 'Relative Humidity is:  '+ str(RelativeHumidity) + '%')  
         print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Relative Humidity is", str(RelativeHumidity), '%')
      except Exception as e:
         print(str(datetime.datetime.now()), "  ", "EXCEPTION: error during RelativeHumidity calculating")
bot.polling(none_stop = True)