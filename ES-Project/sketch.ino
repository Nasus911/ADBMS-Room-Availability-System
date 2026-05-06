#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <ElegantOTA.h>
#include <WebSerial.h>
#include "HX711.h"
#include "web_page.h"

// ===================== USER SETTINGS =====================
const char* AP_SSID = "ESP32-Lab";   // AP name kapag walang WiFi
const char* AP_PASS = "";            // blank = open AP

const char* WIFI_SSID = "";          // optional: lagay SSID dito
const char* WIFI_PASS = "";          // optional: lagay password dito

// HX711 calibration factor (easy edit)
float CALIBRATION_FACTOR = -7050.0f; // palitan after calibration

// Pins
constexpr int PIN_HX711_DT  = 16;
constexpr int PIN_HX711_SCK = 4;

constexpr int PIN_TRIG = 5;
constexpr int PIN_ECHO = 18;

constexpr int PIN_LED = 2;           // built-in LED

// Timing
constexpr uint32_t SENSOR_INTERVAL_MS = 250;
// ==========================================================

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
HX711 scale;

volatile float g_weight = 0.0f;
volatile float g_distance = 0.0f;

uint32_t lastSensorMs = 0;
uint32_t bootMs = 0;

// ===================== HELPERS =====================
void logLine(const String& msg){
  Serial.println(msg);
  WebSerial.println(msg);
}

float readWeightGrams(){
  if (!scale.is_ready()) return g_weight;
  return scale.get_units(3) * 1.0f;
}

float readDistanceCm(){
  // mabilis na pulse, walang delay() sa loop
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 25000); // 25ms timeout
  if (duration == 0) return g_distance;
  return duration * 0.0343f / 2.0f;
}

void broadcastData(){
  String metaStr = "WiFi RSSI: " + String(WiFi.RSSI()) + " dBm | Uptime: " +
                   String((millis()-bootMs)/1000) + "s | Heap: " + String(ESP.getFreeHeap());

  float w = g_weight;
  float d = g_distance;
  float wPct = constrain((w / 5000.0f) * 100.0f, 0.0f, 100.0f);
  float dPct = constrain((d / 200.0f) * 100.0f, 0.0f, 100.0f);

  String payload = "{";
  payload += "\"weight\":" + String(w,1) + ",";
  payload += "\"distance\":" + String(d,1) + ",";
  payload += "\"wbar\":" + String((int)wPct) + ",";
  payload += "\"dbar\":" + String((int)dPct) + ",";
  payload += "\"meta\":\"" + metaStr + "\"";
  payload += "}";
  ws.textAll(payload);
}

void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
               void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    logLine("WS client connected");
  } else if (type == WS_EVT_DISCONNECT) {
    logLine("WS client disconnected");
  } else if (type == WS_EVT_DATA) {
    AwsFrameInfo *info = (AwsFrameInfo*)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      data[len] = 0;
      String msg = (char*)data;

      if (msg.indexOf("tare") >= 0) {
        // Tare: i-zero ang scale
        scale.tare();
        logLine("Tare done");
      } else if (msg.indexOf("calibrate") >= 0) {
        // Calibration helper: ilagay known weight, then read raw
        long reading = scale.get_value(10);
        logLine("Raw reading: " + String(reading));
        logLine("Set CALIBRATION_FACTOR = raw/known_weight");
      } else if (msg.indexOf("ping") >= 0) {
        g_distance = readDistanceCm();
        logLine("Ping distance: " + String(g_distance,1) + " cm");
      }
    }
  }
}

// ===================== SETUP =====================
void setup() {
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);

  Serial.begin(115200);
  bootMs = millis();
  logLine("Booting...");

  // HX711 init
  scale.begin(PIN_HX711_DT, PIN_HX711_SCK);
  scale.set_scale(CALIBRATION_FACTOR);
  scale.tare();

  // WiFi: auto-connect saved or AP mode
  WiFi.mode(WIFI_STA);
  if (String(WIFI_SSID).length() > 0) {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
  } else {
    WiFi.begin();
  }

  uint32_t startMs = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startMs < 8000) {
    digitalWrite(PIN_LED, !digitalRead(PIN_LED));
    delay(200);
  }

  if (WiFi.status() == WL_CONNECTED) {
    logLine("WiFi connected: " + WiFi.localIP().toString());
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    logLine("AP mode: " + String(AP_SSID));
    logLine("AP IP: " + WiFi.softAPIP().toString());
  }

  // Web server
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", INDEX_HTML);
  });

  server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request){
    String json = "{";
    json += "\"weight\":" + String(g_weight,1) + ",";
    json += "\"distance\":" + String(g_distance,1);
    json += "}";
    request->send(200, "application/json", json);
  });

  WebSerial.begin(&server);
  ElegantOTA.begin(&server);

  server.begin();
  logLine("Server started");
}

// ===================== LOOP =====================
void loop() {
  uint32_t now = millis();
  if (now - lastSensorMs >= SENSOR_INTERVAL_MS) {
    lastSensorMs = now;
    g_weight = readWeightGrams();
    g_distance = readDistanceCm();
    broadcastData();
  }

  // heartbeat LED
  digitalWrite(PIN_LED, (now / 500) % 2);
}
