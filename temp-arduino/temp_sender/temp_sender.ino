#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

//#define DHTPIN 2
#define DHTTYPE DHT11
const int DHTPIN = D1;

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "FreeWifi";
const char* password = "Passw0rd";

String serverUrl =
"http://192.168.1.67:3000/api/data";

void setup()
{
  Serial.begin(115200);

  WiFi.begin(ssid,password);

  while(WiFi.status()!=WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi ühendatud");

  dht.begin();
}

void loop()
{
  float temp = dht.readTemperature() - 10;
  float hum  = dht.readHumidity();


  if(isnan(temp)||isnan(hum))
  {
    Serial.println("Anduri viga");
    delay(5000);
    return;
  }

  if(WiFi.status()==WL_CONNECTED)
  {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverUrl);
    http.addHeader("Content-Type","application/json");

    String json =
      "{\"temperature\":" + String(temp) +
      ",\"humidity\":" + String(hum) +
      ",\"device\":\"ESP8266-D1\"}";

    int code = http.POST(json);

    Serial.println(code);

    http.end();
  }

  delay(150000); //2,5min
}