#include "client_https.hpp"
#include <iostream>
#include <string>
#include <cstdlib>

using namespace std;

string api_key = string(getenv("TOKEN_AI"));
    

string extract_content_from_json1(const string& raw_response) {
    // Ищем маркер начала текста ответа ассистента
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
    
    // Обработка экранированных символов переноса строки, если они есть
    size_t nl_pos = 0;
    while ((nl_pos = content.find("\\n", nl_pos)) != string::npos) {
        content.replace(nl_pos, 2, "\n");
        nl_pos += 1;
    }
    
    return content;
}

string ask_ai1(const string& user_message) {
    string hostname = "openrouter.ai";
    
    // 2. Инициализируем сетевое TLS-подключение
    client_net client(443, hostname);
    if (client.sock < 0) {
        cerr << "[AI Error]: Failed to connect to " << hostname << endl;
        return "";
    }

    // 3. Формируем чистый JSON payload (поддерживает кириллицу напрямую в UTF-8)
    string json_payload = "{"
        "\"model\": \"openrouter/owl-alpha\"," // Используем полностью бесплатную модель
        "\"messages\": [{"
            "\"role\": \"user\","
            "\"content\": \"" + user_message + "\""
        "}]"
    "}";

    // 4. Собираем сырой HTTP-запрос (Важно: Connection: close)
    string http_request = 
        "POST /api/v1/chat/completions HTTP/1.1\r\n"
        "Host: " + hostname + "\r\n"
        "Authorization: Bearer " + api_key + "\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: " + to_string(json_payload.length()) + "\r\n"
        "Connection: close\r\n\r\n" + 
        json_payload;

    // 5. Отправляем запрос через SSL-сокет
    if (client.send(http_request) <= 0) {
        cerr << "[AI Error]: Failed to send data over SSL" << endl;
        return "";
    }

    // 6. Читаем ответ от сервера до закрытия соединения
    string raw_response = client.get(4096);
    //cout<<raw_response<<endl;
    // 7. Проверяем HTTP статус-код (должен быть 200 OK)
    if (raw_response.find("HTTP/1.1 200 OK") == string::npos) {
        cerr << "[AI Error]: Non-200 response from server" << endl;
        // Если хотите увидеть ошибку (например 402), можно раскомментировать строку ниже:
        // cerr << raw_response << endl;
        return "";
    }

    // 8. Отсекаем HTTP заголовки, оставляя только JSON тело
    size_t body_start = raw_response.find("\r\n\r\n");
    if (body_start == string::npos) {
        return "";
    }
    string json_body = raw_response.substr(body_start + 4);

    // 9. Извлекаем текст ответа нейросети
    return extract_content_from_json1(json_body);
}

string ask_ai(string a){
    return "right now ai not work";
}