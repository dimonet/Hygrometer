import logging
import ssl
import datetime
import telebot
import toml
from Hygrometer import Hygrometer
from DataStorage.Amendments1 import Amendment1
from DataStorage.HumidityTable1 import HumidityTable1
from DataStorage.Amendments2 import Amendment2
from DataStorage.HumidityTable2 import HumidityTable2
from aiohttp import web

# reading configuration from Conf file
config = toml.load('Config.toml')
API_TOKEN = config.get('Telegram').get('API_TOKEN')
WEBHOOK_HOST = config.get('ENVIRONMENT').get('WEBHOOK_HOST')
WEBHOOK_PORT = config.get('ENVIRONMENT').get('WEBHOOK_PORT')
WEBHOOK_LISTEN = config.get('ENVIRONMENT').get('WEBHOOK_LISTEN')
WEBHOOK_SSL_CERT = config.get('KEY_PATH').get('WEBHOOK_SSL_CERT')  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = config.get('KEY_PATH').get('WEBHOOK_SSL_PRIV')  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)


print(str(datetime.datetime.now()), "Telegram bot (v1.3) has started")

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
   keyboard = telebot.types.InlineKeyboardMarkup()
   callback_VIT1 = telebot.types.InlineKeyboardButton(text="VIT1", callback_data="vit1")
   callback_VIT2 = telebot.types.InlineKeyboardButton(text="VIT2", callback_data="vit2")
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
         if _model == 1:
            Hygrom = Hygrometer(Amendment1, HumidityTable1)
         else:
            Hygrom = Hygrometer(Amendment2, HumidityTable2)
         errorMsg = []
         RelativeHumidity = Hygrom.GetRelativeHumidity(_dryTemp, _wetTemp, errorMsg)  
         if len(errorMsg) != 0:
            bot.send_message(message.from_user.id, errorMsg[0])  
            print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Error:", errorMsg[0])
            any_msg(message)
         else:            
            bot.send_message(message.from_user.id, 'Relative Humidity is:  '+ str(RelativeHumidity) + '%')  
            print(str(datetime.datetime.now()), " ", str(message.message_id),"  ", "Relative Humidity is", str(RelativeHumidity), '%')         
      except Exception as e:
         print(str(datetime.datetime.now()), "  ", "EXCEPTION: error during RelativeHumidity calculating")


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)