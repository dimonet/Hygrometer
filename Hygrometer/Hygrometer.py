import math


class Hygrometer(object):
    def __init__(self, amendments, HumidityTable):
        self.amendments = amendments
        self.HumidityTable = HumidityTable

    def GetRelativeHumidity(self, dryTemp, wetTemp, errorMsg):
        CalibDryTemp = self.__GetAmendment(dryTemp, self.amendments['dry'])
        if CalibDryTemp == None:
            errorMsg.append(
                "Inputted Dry temperature is incorrect for this model. Please check the inputted Dry temperature or try to select another model")
            return
        CalibWetTemp = self.__GetAmendment(wetTemp, self.amendments['wet'])
        if CalibWetTemp == None:
            errorMsg.append(
                "Inputted Wet temperature is incorrect for this model. Please check the inputted Wet temperature or try to select another model")
            return
        diff = round((CalibDryTemp - CalibWetTemp), 1)
        HumidityAmount = self.__GetHumidityAmount(CalibDryTemp, diff, self.HumidityTable, errorMsg)
        if HumidityAmount is None:
            return
        dryTempDecimal = round((CalibDryTemp % 1), 1)  # берем десятичную часть с температуры 25.5 -> 0.5
        diffDecimal = round(diff - self.__RoundByDecimal(diff, 0.5), 1)  # берем десятичную часть с разници
        return round(HumidityAmount + (dryTempDecimal * 2) - ((diffDecimal * 4) / 0.5), 2)

    def __GetHumidityAmount(self, dryTemp, diff, HumidityTable, errorMsg):
        RoundDryTemp = math.floor(dryTemp)  # округление до низа
        RoundDiff = self.__RoundByDecimal(diff, 0.5)  # округляем разницу до ближащего десятичного значения 0.5
        try:
            return HumidityTable[RoundDryTemp][RoundDiff]
        except:
            errorMsg.append(
                "The relative humidity can not be calculated regarding to these temperatures. Please check the inputted temperatures or try to select another model")

    def __GetAmendment(self, tempAmount, amendments):
        valueList = list(amendments.values())
        keyList = list(amendments.keys())
        pos = 0
        for i in amendments:
            if pos < len(valueList) - 1:
                if round(tempAmount) >= int(keyList[pos]) and round(tempAmount) < int(keyList[pos + 1]):
                    return round((tempAmount + valueList[pos]), 1)
            elif round(tempAmount) >= int(keyList[pos]):
                return round((tempAmount + valueList[pos]), 1)
            pos += 1

    # Utilities
    def __RoundByDecimal(self, number, byDec):
        return round(number - round((number % byDec), 1), 2)
