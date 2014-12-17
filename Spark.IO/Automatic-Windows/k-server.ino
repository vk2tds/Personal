/* Web_HelloWorld.pde - very simple Webduino example */

#include "WebServer/WebServer.h"

/* This creates an instance of the webserver.  By specifying a prefix
 * of "", all pages will be at the root of the server. */
#define PREFIX ""
WebServer webserver(PREFIX, 80);

// no-cost stream operator as described at 
// http://sundial.org/arduino/?page_id=119
template<class T>
inline Print &operator <<(Print &obj, T arg)
{ obj.print(arg); return obj; }

void o (int led)
{
  digitalWrite(led, HIGH);   // Turn ON the LED
  delay(1000);               // Wait for 1000mS = 1 second
  digitalWrite(led, LOW);    // Turn OFF the LED
  delay(250);
  digitalWrite(D5, HIGH);    // Turn OFF the LED
  delay(1000);               // Wait for 1000mS = 1 second
  digitalWrite(D5, LOW);    // Turn OFF the LED

}

void c (int led)
{
  digitalWrite(led, HIGH);   // Turn ON the LED
  delay(1000);               // Wait for 1000mS = 1 second
  digitalWrite(led, LOW);    // Turn OFF the LED
  delay(250);
  digitalWrite(D4, HIGH);    // Turn OFF the LED
  delay(1000);               // Wait for 1000mS = 1 second
  digitalWrite(D4, LOW);    // Turn OFF the LED

}



void formCmd(WebServer &server, WebServer::ConnectionType type, char *url_tail, bool tail_complete)
{
    char name[16], value[16];

      URLPARAM_RESULT rc;
    if (strlen(url_tail))
    {
    while (strlen(url_tail))
      {
      rc = server.nextURLparam(&url_tail, name, 16, value, 16);
      if (rc == URLPARAM_EOS)
        server.printP("");
       else
        {
      if (name[0] != 0 && value[0] != 0){
          if (name[0] == 'O') {
            if(value[0] == '0') {o(D6); }
            if(value[0] == '1') {o(D7); }
            if(value[0] == '2') {o(D2); }
            if(value[0] == '3') {o(D3); }
          }
          if (name[0] == 'C') {
            if(value[0] == '0') {c(D6); }
            if(value[0] == '1') {c(D7); }
            if(value[0] == '2') {c(D2); }
            if(value[0] == '3') {c(D3); }
          }
      }  
        }
      }
      server.httpSuccess();
      return;
    }
      server.httpSuccess();
    
  //else
//      outputPins(server, type, true);
}


/* commands are functions that get called by the webserver framework
 * they can read any posted data from client, and they output to the
 * server to send data back to the web browser. */
void helloCmd(WebServer &server, WebServer::ConnectionType type, char *, bool)
{
  /* this line sends the standard "we're all OK" headers back to the
     browser */
  server.httpSuccess();

  /* if we're handling a GET or POST, we can output our data here.
     For a HEAD request, we just stop after outputting headers. */
  if (type != WebServer::HEAD)
  {
    /* this defines some HTML text in read-only memory aka PROGMEM.
     * This is needed to avoid having the string copied to our limited
     * amount of RAM. */
    P(helloMsg) = "<h1>http://192.168.1.158/form?O=0 or http://192.168.1.158/form?C=4</h1>";

    /* this is a special form of print that outputs from PROGMEM */
    server.printP(helloMsg);
  }
}

void setup()
{
    
    pinMode (D0, OUTPUT);
    pinMode (D1, OUTPUT);
    pinMode (D2, OUTPUT);
    pinMode (D3, OUTPUT);
    pinMode (D4, OUTPUT);
    pinMode (D5, OUTPUT);
    pinMode (D6, OUTPUT);
    pinMode (D7, OUTPUT);
  /* setup our default command that will be run when the user accesses
   * the root page on the server */
  webserver.setDefaultCommand(&helloCmd);

  /* run the same command if you try to load /index.html, a common
   * default page name */
  webserver.addCommand("index.html", &helloCmd);
  webserver.addCommand("form", &formCmd);

  /* start the webserver */
  webserver.begin();
  //o(D6);
}

void loop()
{
  char buff[64];
  int len = 64;

  /* process incoming connections one at a time forever */
  webserver.processConnection(buff, &len);
}






