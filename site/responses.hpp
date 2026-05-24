#pragma once
#include <string>
using namespace std;

string response_200_text[] = {
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/plain; charset=utf-8\r\n"
    "Content-Length: " , "\r\n"
    "Connection: close\r\n"
    "\r\n" };
string response_200_json_with_uuid[]={
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: ",
    "\r\n"
    "Set-Cookie: session_id=" ,
    "; Path=/; HttpOnly; SameSite=Strict\r\n"
    "Connection: close\r\n"
    "\r\n"
};
string response_200_json[]={
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: ",
    "\r\n"
    "Connection: close\r\n"
    "\r\n"
};
string response_200_html[] = {
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=utf-8\r\n"
    "Content-Length: " , "\r\n"
    "Connection: close\r\n"
    "\r\n" };

string nf404 = ("HTTP/1.1 404 Not Found\r\n\r\n404 Not Found");
