import math
class Hygrometer(object):
   def __init__(self, amendments, wetTable):    
      self.amendments = amendments
      self.wetTable = wetTable
  
   def GetRelativeHumidity(self, dryTemp, wetTemp):        
      CalibDryTemp = self.__GetAmendment(dryTemp, self.amendments['dry'])
      CalibWetTemp = self.__GetAmendment(wetTemp, self.amendments['wet'])
      diff = round((CalibDryTemp - CalibWetTemp), 1)
      HumidityAmount = self.__GetHumidityAmount(CalibDryTemp, diff, self.wetTable)
      dryTempDecimal = round((CalibDryTemp%1),1)  # берем десятичную часть с температуры 25.5 -> 0.5
      diffDecimal =  round(diff - self.__RoundByDecimal(diff, 0.5), 1)  # берем десятичную часть с разници          
      return HumidityAmount+(dryTempDecimal * 2) - ((diffDecimal * 4)/0.5)
  
   def __GetHumidityAmount(self, dryTemp, diff, wetTable):
      RoundDryTemp = math.floor(dryTemp)            # округление до низа
      RoundDiff = self.__RoundByDecimal(diff, 0.5)  # округляем разницу до ближащего десятичного значения 0.5
      return wetTable[RoundDryTemp][RoundDiff]
  
   def __GetAmendment(self, tempAmount, amendments):
      valueList = list(amendments.values())
      keyList = list(amendments.keys())
      pos = 0
      for i in amendments:    
         if pos < len(valueList) - 1:          
            if round(tempAmount) >= int(keyList[pos]) and round(tempAmount) < int(keyList[pos + 1]):
               return round((tempAmount+valueList[pos]),1)
         else:
            if round(tempAmount) >= int(keyList[pos]):
               return round((tempAmount+valueList[pos]),1)     
         pos+=1

   #Utilities
   def __RoundByDecimal(self, number, byDec):
      return round(number - round((number%byDec),1),2)   
