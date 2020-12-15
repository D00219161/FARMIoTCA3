#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <ESP8266WebServerSecure.h>
#include <EEPROM.h>
#include "DHT.h"
#include "PubSubClient.h" // Connect and publish to the MQTT broker
// @TODO Add reset button to allow rest of EEPROM
const char* apSSID = "HOMESAFE_SETUP";
const char* apPASS = "Xntk8862";
String ssidList;
const IPAddress apIP(192, 168, 1, 1);
boolean settingMode;

// WiFi
String ssid           = "";         // The SSID (name) of the Wi-Fi network you want to connect to
String wifi_password  = "";         // The password of the Wi-Fi network
String room           = "";

BearSSL::ESP8266WebServerSecure server(443);
ESP8266WebServer serverHTTP(80);

// Sensor
#define DHTPIN 14
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQTT
IPAddress mqtt_server(192, 168, 178, 25);
const char* humidity_topic    = "home/livingroom/humidity";
const char* temperature_topic = "home/livingroom/temperature";
const char* mqtt_username     = "finbar"; // MQTT username // @TODO Have these be changeable
const char* mqtt_password     = "finbar"; // MQTT password
char* clientID                = "client_";//livingroom"; // MQTT client ID // @TODO Be able to append room to ID

// Initialize the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
PubSubClient client(mqtt_server, 1883, wifiClient);

static const char serverCert[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIC6jCCAlOgAwIBAgIUHlDnCnd2yJ6JCDWg2Ba0sIYAnOkwDQYJKoZIhvcNAQEL
BQAwejELMAkGA1UEBhMCUk8xCjAIBgNVBAgMAUIxEjAQBgNVBAcMCUJ1Y2hhcmVz
dDEbMBkGA1UECgwST25lVHJhbnNpc3RvciBbUk9dMRYwFAYDVQQLDA1PbmVUcmFu
c2lzdG9yMRYwFAYDVQQDDA1lc3A4MjY2LmxvY2FsMB4XDTIwMTIwODIzMDcwOFoX
DTIxMTIwODIzMDcwOFowejELMAkGA1UEBhMCUk8xCjAIBgNVBAgMAUIxEjAQBgNV
BAcMCUJ1Y2hhcmVzdDEbMBkGA1UECgwST25lVHJhbnNpc3RvciBbUk9dMRYwFAYD
VQQLDA1PbmVUcmFuc2lzdG9yMRYwFAYDVQQDDA1lc3A4MjY2LmxvY2FsMIGfMA0G
CSqGSIb3DQEBAQUAA4GNADCBiQKBgQDCzsn+N+pT5PcKgHTHrAdBbk2E2BioxSDk
CbdI1UbcUAwXqpO/ta95dubJdFw/gbxmGwZEnKBOw6iz3tjGz8ZiMLm30YykMiSs
t6bdQlqYZBi/Avl6skJposRLpMB6GplUoLQJbIR1xq1vo3cg/j0txhzdj7fhcICO
Ofe5WTS7nwIDAQABo20wazAdBgNVHQ4EFgQUstZ3FJM+mYY2wyKbG8XeQU8V5Ycw
HwYDVR0jBBgwFoAUstZ3FJM+mYY2wyKbG8XeQU8V5YcwDwYDVR0TAQH/BAUwAwEB
/zAYBgNVHREEETAPgg1lc3A4MjY2LmxvY2FsMA0GCSqGSIb3DQEBCwUAA4GBAHGz
hqqRogkvzB+zrfs7GSOb47hYhSRYqxtqy9WVyA/b8mQw60YTYT6hpAsTcH/EqiJj
oFIWXnUIJE/TLcKc8krgYFJMgtYSj6ElsB5E4TI5u+xFYAnaesbdynfAsT/O7uRs
JOWt+talVwc7J0qHLNU6+uwUw5SKPEvy96UdQyJr
-----END CERTIFICATE-----
)EOF";

static const char serverKey[] PROGMEM =  R"EOF(
-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAMLOyf436lPk9wqA
dMesB0FuTYTYGKjFIOQJt0jVRtxQDBeqk7+1r3l25sl0XD+BvGYbBkScoE7DqLPe
2MbPxmIwubfRjKQyJKy3pt1CWphkGL8C+XqyQmmixEukwHoamVSgtAlshHXGrW+j
dyD+PS3GHN2Pt+FwgI4597lZNLufAgMBAAECgYAracQQGEvrSFJZj8j2mnq/dSJn
YXUVX2D2EMg8vfLdtCUNvSDSD148lmfWK01HhdUDeDBMaA89nlLhSt9KZxFRemvQ
B/GVjBHwc/V3Mlh+9WZl9KvaUSq0pw5I404iHBO+dLL5IcFyxyUmAVxv3dZdHafm
R0F9YwHn8nS/V6HbwQJBAPhSX+sv1mDVXKIobn7ts+pTNAkha5tPbbEMqWybj51p
TlcJQne4MQCVpe8IugL93thf3M+c7xavRDhY02TLBqECQQDI1NEcp3u0L9cojGrg
G2F9KnbaMPrcmORj8zIUrydp20QjHW6wUosNOUydRMlGZ4TYXwAHbocRvHveKpoV
+do/AkEAk6x5OmYieUepZQ3iWD2IJyv/4AYt9hjQROAgyWPhjl0Xp47sJkI1cgGM
wpBP/oN3SPoJWLYdQUJNsayxWlmawQJAMuJhHU5+NFhOvpJdXezyFYGV3ZC9bvk6
HOz4im8aoGKS8Aa8DebMHoyfEdXk3XbLHPttCXUCuga0p8TJh7nnhwI/KLr0ODak
bXoPzoh35B6e5HMWPNLMIkepSsGhA19SH3qTVBv6+yo3p5GqbZqfG+OTIXOImHV6
RBsJfheBbAEL
-----END PRIVATE KEY-----
)EOF";

// Custom function to connect to the MQTT broker via WiFi
void connect_MQTT(){

  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.hostname(clientID);
  WiFi.begin(ssid, wifi_password);

  // Wait until the connection has been confirmed before continuing
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Debugging - Output the IP Address of the ESP8266
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to MQTT Broker
  // client.connect returns a boolean value to let us know if the connection was successful.
  // If the connection is failing, make sure you are using the correct MQTT Username and Password (Setup Earlier in the Instructable)
  if (client.connect(clientID, mqtt_username, mqtt_password)) {
    Serial.println("Connected to MQTT Broker!");
  }
  else {
    Serial.println("Connection to MQTT Broker failed...");
  }
}

bool startAP() {
  byte timeout = 50;
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  int n = WiFi.scanNetworks();
  delay(100);
  Serial.println("");
  for (int i = 0; i < n; ++i) {
    ssidList += "<option value=\"";
    ssidList += WiFi.SSID(i);
    ssidList += "\">";
    ssidList += WiFi.SSID(i);
    ssidList += "</option>";
  }
  delay(100);
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(apSSID, apPASS);

  Serial.print("Waiting for a connection ");
  for (int i = 0; i < timeout; i++) {
    if (WiFi.softAPgetStationNum() > 0) { //WiFi.status() == WL_CONNECTED) {
      Serial.print("Connection to AP made.\n");
      Serial.print("Server can be accessed at https://");
      Serial.print(apIP);
      return true;
    }
    delay(5000);
    Serial.print(".");
  }

  Serial.println("\nNo connection to AP found.");
  return false;
}

void showWebpage() {
  String content = "<!DOCTYPE html><html>";
  content +=  "<head><title>";
  content +=  apSSID;
  content +=  "</title>";
  content +=  "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">";
  /*******************************************
   *            CSS Style 
   *******************************************/
  content +=  "<style>input[type=text], input[type=password], select {";
  content +=    "width: 100%; padding: 12px 20px; margin: 8px 0;";
  content +=    "display: inline-block; border: 1px solid #ccc;";
  content +=    "border-radius: 4px; box-sizing: border-box;}";
  content +=  "input[type=submit] {width: 100%; background-color: #4CAF50;";
  content +=    "color: white; padding: 14px 20px; margin: 8px 0;";
  content +=    "border: none; border-radius: 4px; cursor: pointer;}";
  content +=  "input[type=submit]:hover {background-color: #45a049;}";
  content +=  "div {margin: 0 auto; max-width: 500px; border-radius: 5px;";
  content +=    "background-color: #f2f2f2; padding: 20px;}";
  content +=  "h1, h5 {text-align: center;text-color: #808080;}</style>";
  /*******************************************
   *            Script
   *******************************************/
  content +=  "<script>\n";
  content +=    "function showPassword() {";
  content +=      "var x = document.getElementById(\"pass\");";
  content +=      "if (x.type === \"password\"){ x.type = \"text\";";
  content +=      "} else {x.type = \"password\";}}";
  content +=  "</script>";
  content +=  "</head><body>";
  /*******************************************
   *            Body
   *******************************************/
  content +=  "<div><h1>";
  content +=  apSSID;
  content +=  "</h1><p>";
  content +=  "<form method=\"get\" action=\"setup\">";
  content +=  "<label for=\"ssid\">SSID</label>";
  content +=  "<select id=\"ssid\" name=\"ssid\">";
  content +=  ssidList;
  content +=  "</select>";
  content +=  "<label for=\"pass\">Password</label>";
  content +=  "<input type=\"password\" id=\"pass\" name=\"pass\" placeholder=\"Your WiFi password..\" maxlength=\"64\">";
  content +=  "<input type=\"checkbox\" onclick=\"showPassword()\">Show Password<br><br>";
  content +=  "<label for=\"room\">Room</label>";
  content +=  "<input type=\"text\" id=\"room\" name=\"room\" placeholder=\"Front Room\" maxLength=\"32\">";
  content +=  "<h5>Please use a unique room name for each device.</h5>";
  content +=  "<input type=\"submit\" value=\"Submit\">";
  content +=  "</form></div>";
  content +=  "</body></html>";
  server.send(200, "text/html", content);

  server.on("/setup", []() {
      ssid = urlDecode(server.arg("ssid"));
      Serial.print("SSID: ");
      Serial.println(ssid);
      wifi_password = urlDecode(server.arg("pass"));
      Serial.print("Password: ");
      Serial.println(wifi_password);
      room = urlDecode(server.arg("room"));
      Serial.print("Room: ");
      Serial.println(room);
      /**********************************
       *    EEPROM WRITE 
       *********************************/
      Serial.println("Writing SSID to EEPROM...");
      for (int i = 0; i < ssid.length(); ++i) {
        EEPROM.write(i, ssid[i]);
      }
      Serial.println("Writing Password to EEPROM...");
      for (int i = 0; i < wifi_password.length(); ++i) {
        EEPROM.write(32 + i, wifi_password[i]);
      }
      Serial.println("Writing Room to EEPROM...");
      for (int i = 0; i < room.length(); ++i) {
        EEPROM.write(96 + i, room[i]);
      }
      EEPROM.commit();
      Serial.println("Write EEPROM done! (Restart in 5 seconds ...)");
      delay(5000);
      ESP.restart();   
  });
}

// Redirect HTTP requests to the HTTPS site.
void secureRedirect() {
  serverHTTP.sendHeader("Location", String("https://192.168.1.1"), true);
  serverHTTP.send(301, "text/plain", "");
}

boolean restoreConfig() {
  Serial.println("Reading EEPROM...");
  if (EEPROM.read(0) != '\0') {
    for (int i = 0; i < 32; ++i) {
      ssid += char(EEPROM.read(i));
    }
    Serial.print("SSID: ");
    Serial.println(ssid);
    for (int i = 32; i < 96; ++i) {
      wifi_password += char(EEPROM.read(i));
    }
    Serial.print("Password: ");
    Serial.println(wifi_password);
    for (int i = 96; i < 128; ++i) {
      room += char(EEPROM.read(i));
    }
    /*
    for (int i = 0; i < room.length(); ++i) {
      clientID++;
      *clientID = room[i];  
    }
    */
    
    WiFi.begin(ssid.c_str(), wifi_password.c_str());
    return true;
  }
  else {
    Serial.println("Config not found.");
    return false;
  }
}

void resetEEPROM() {
  Serial.println("BEGIN EEPROM RESET");
  for (int i = 0; i < 128; ++i) {
    EEPROM.write(i, '\0');
  }
  EEPROM.commit();
  Serial.println("EEPROM RESET ENDED");
}

void sendSensorData() {
  delay(100);
  connect_MQTT();
  Serial.setTimeout(6000);
  
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.println(" %");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println(" *C");

  // MQTT can only transmit strings
  String hs="Hum: "+String((float)h)+" % ";
  String ts="Temp: "+String((float)t)+" C ";

  // PUBLISH to the MQTT Broker (topic = Temperature, defined at the beginning)
  if (client.publish(temperature_topic, String(t).c_str())) {
    Serial.println("Temperature sent!");
  }
  else {
    Serial.println("Temperature failed to send. Reconnecting to MQTT Broker and trying again");
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(10); // This delay ensures that client.publish doesn't clash with the client.connect call
    client.publish(temperature_topic, String(t).c_str());
  }

  // PUBLISH to the MQTT Broker (topic = Humidity, defined at the beginning)
  if (client.publish(humidity_topic, String(h).c_str())) {
    Serial.println("Humidity sent!");
  }
  else {
    Serial.println("Humidity failed to send. Reconnecting to MQTT Broker and trying again");
    client.connect(clientID, mqtt_username, mqtt_password);
    delay(10); // This delay ensures that client.publish doesn't clash with the client.connect call
    client.publish(humidity_topic, String(h).c_str());
  }
  client.disconnect();  // disconnect from the MQTT broker
  delay(1000*60);       // print new values every 1 Minute

}

void setup() {
  
  Serial.begin(115200);
  delay(100);
  EEPROM.begin(512);
  delay(100);
  //resetEEPROM();
  dht.begin();
  Serial.println('\n');
  if (restoreConfig()) {
    settingMode = false;
  } else {
    settingMode = true;
    
    if (!startAP()) {
      delay(60000);
      ESP.restart();
    }
    serverHTTP.on("/", secureRedirect);
    serverHTTP.begin();

    server.getServer().setRSACert(new BearSSL::X509List(serverCert), new BearSSL::PrivateKey(serverKey));
    server.on("/", showWebpage);
    server.begin();
  
    Serial.println("\nAP is ready");
  }
}

void loop() {
  if (settingMode) {
    serverHTTP.handleClient();
    server.handleClient();
  } else {
    sendSensorData();
  }
}

String urlDecode(String input) {
  String s = input;
  s.replace("%20", " ");
  s.replace("+", " ");
  s.replace("%21", "!");
  s.replace("%22", "\"");
  s.replace("%23", "#");
  s.replace("%24", "$");
  s.replace("%25", "%");
  s.replace("%26", "&");
  s.replace("%27", "\'");
  s.replace("%28", "(");
  s.replace("%29", ")");
  s.replace("%30", "*");
  s.replace("%31", "+");
  s.replace("%2C", ",");
  s.replace("%2E", ".");
  s.replace("%2F", "/");
  s.replace("%2C", ",");
  s.replace("%3A", ":");
  s.replace("%3A", ";");
  s.replace("%3C", "<");
  s.replace("%3D", "=");
  s.replace("%3E", ">");
  s.replace("%3F", "?");
  s.replace("%40", "@");
  s.replace("%5B", "[");
  s.replace("%5C", "\\");
  s.replace("%5D", "]");
  s.replace("%5E", "^");
  s.replace("%5F", "-");
  s.replace("%60", "`");
  return s;
}
