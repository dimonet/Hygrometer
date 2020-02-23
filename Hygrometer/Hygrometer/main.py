from Hygrometer import Hygrometer
from DataStorage.Amendments import Amendment1
from DataStorage.HumidityTables import HumidityTable1


dryTemp = float(input("Enter Dry Measure ")) #24.8#25.1
wetTemp = float(input("Enter Wet Measure ")) #20.3#20.4

Hygrom1 = Hygrometer(Amendment1, HumidityTable1)
RelativeHumidity = round(Hygrom1.GetRelativeHumidity(dryTemp, wetTemp), 2)
print('Relative Humidity is: ', RelativeHumidity)