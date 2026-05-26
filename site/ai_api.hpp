#include "client_https.hpp"
#include <iostream>
#include <string>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <atomic>

using namespace std;

string get_env_safe(const char* name) {
    const char* val = getenv(name);
    if (!val) {
        cerr << "[FATAL] Environment variable " << name << " is not set!" << endl;
        exit(1);
    }
    return string(val);
}

string api_key = get_env_safe("TOKEN_AI");

const int AI_TIMEOUT_SECONDS = 10;

string extract_content_from_json1(const string& raw_response) {
    string target = "\"content\":\"";
    size_t start_pos = raw_response.find(target);
    if (start_pos == string::npos) {
        return "";
    }
    
    start_pos += target.length();
    size_t end_pos = raw_response.find("\"", start_pos);
    if (end_pos == string::npos) {
        return "";
    }
    
    string content = raw_response.substr(start_pos, end_pos - start_pos);
    
    size_t nl_pos = 0;
    while ((nl_pos = content.find("\\n", nl_pos)) != string::npos) {
        content.replace(nl_pos, 2, "\n");
        nl_pos += 1;
    }
    
    return content;
}

string ask_ai1(const string& user_message) {
    string hostname = "openrouter.ai";
    
    client_net client(443, hostname);
    if (client.sock < 0) {
        cerr << "[AI Error]: Failed to connect to " << hostname << endl;
        return "";
    }

    string json_payload = "{"
        "\"model\": \"openrouter/owl-alpha\","
        "\"messages\": [{"
            "\"role\": \"user\","
            "\"content\": \"" + user_message + "\""
        "}]"
    "}";

    string http_request = 
        "POST /api/v1/chat/completions HTTP/1.1\r\n"
        "Host: " + hostname + "\r\n"
        "Authorization: Bearer " + api_key + "\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: " + to_string(json_payload.length()) + "\r\n"
        "Connection: close\r\n\r\n" + 
        json_payload;

    if (client.send(http_request) <= 0) {
        cerr << "[AI Error]: Failed to send data over SSL" << endl;
        return "";
    }

    auto start_time = chrono::steady_clock::now();
    string raw_response;
    
    while (true) {
        auto elapsed = chrono::steady_clock::now() - start_time;
        if (chrono::duration_cast<chrono::seconds>(elapsed).count() >= AI_TIMEOUT_SECONDS) {
            cerr << "[AI Timeout]: Response took too long (>" << AI_TIMEOUT_SECONDS << "s)" << endl;
            return "";
        }
        
        string chunk = client.get(4096);
        if (chunk.empty()) break;
        raw_response += chunk;
        
        if (raw_response.find("\r\n\r\n") != string::npos) {
            break;
        }
    }
    
    if (raw_response.find("HTTP/1.1 200 OK") == string::npos) {
        cerr << "[AI Error]: Non-200 response from server" << endl;
        cout<<"ERROR LOG:"<<raw_response<<endl;
        return "";
    }

    size_t body_start = raw_response.find("\r\n\r\n");
    if (body_start == string::npos) {
        return "";
    }
    string json_body = raw_response.substr(body_start + 4);

    return extract_content_from_json1(json_body);
}

string ask_ai(string a){
    return "right now ai not work";
}
