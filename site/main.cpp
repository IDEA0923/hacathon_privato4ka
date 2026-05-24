#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <fstream>
#include <iostream>
#include <thread>
#include <map>

#include <cstdlib> //std::getenv("postgress_login");

#include <arpa/inet.h> //inet_ntoa
#include "ai_api.hpp"
#include <libpq-fe.h>

#include "net_https.hpp"
#include "funcs.h"
#include "database.hpp"

#include "responses.hpp"

using namespace std;

map<string , string > st_sites;



void main1(net nt){
    
    if(nt.init()){nt.dnet();return;}
    string message = nt.recv2(1024);
    cout<<"[+]new client ip :"<<inet_ntoa(nt.cli.sin_addr);
    cout<<"client message :\n"<<message<<"\n------"<<endl;
    string path = get_arg1(&message, " ", " ");
    cout << "DEBUG: Path is -> [" << path << "]" << endl;
    
    string methot = message.substr(0, message.find(" "));
    cout<<"methot : "<<methot<<endl;
    cout<<"ask ai"<<ask_ai("ку ")<<endl;
    if(methot == "GET"){
        if(path == "/"){
            string rsp = response_200_html[0]+to_string(st_sites["index1.html"].size())+response_200_html[1]+st_sites["index.html"];
            nt.send(rsp);
            cout<<"SENDED: index.html"<<endl;
            nt.dnet();
            return;
        }else if("/api/" == path.substr(0, 5)){
            if("profile" == path.substr(5, 7) ){
                if(1)
                nt.dnet();
                return;
            }
            
        }
    }else if(methot == "POST"){
        db db1 = db();
        
        // 1. Профиль
        if("/profile/" == path.substr(0, 9)){
            string tg_id = path.substr(9);
            if(id_valid_data(tg_id, &db1) != -1){
                vector<string> u_data = get_user_info(tg_id, &db1);
                if(!u_data.empty()){
                    // Собираем CSV через запятую
                    string rsp_body = u_data[0] + "," + u_data[1] + "," + u_data[2] + "," + u_data[3];
                    string rsp = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: " + to_string(rsp_body.size()) + "\r\n\r\n" + rsp_body;
                    nt.send(rsp);
                    cout << "SENDED: /profile/" << tg_id << endl;
                    nt.dnet();
                    return;
                }
            }
        }
        // 2. Олимпиады за месяц (id шники)
        else if("/api/olimps/" == path.substr(0, 12)){
            string tg_id = path.substr(12);
            if(id_valid_data(tg_id, &db1) != -1){
                vector<string> ids = get_suitable_olimps(tg_id, &db1);
                
                string rsp_body = "{ \"ids\": [";
                for(size_t i = 0; i < ids.size(); i++){
                    rsp_body += ids[i];
                    if(i != ids.size() - 1) rsp_body += ", ";
                }
                rsp_body += "] }";
                
                string rsp = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + to_string(rsp_body.size()) + "\r\n\r\n" + rsp_body;
                nt.send(rsp);
                cout << "SENDED: /api/olimps/" << tg_id << endl;
                nt.dnet();
                return;
            }
        }
        // 3. Конкретная олимпиада + ИИ поинт
        else if("/api/olimp:" == path.substr(0, 11)){
            size_t slash_pos = path.find('/', 11);
            if(slash_pos != string::npos){
                string olimp_id = path.substr(11, slash_pos - 11);
                string tg_id = path.substr(slash_pos + 1);
                
                if(id_valid_data(tg_id, &db1) != -1){
                    vector<string> ol_data = get_olimp_info(olimp_id, &db1);
                    vector<string> u_data = get_user_info(tg_id, &db1);
                    
                    if(!ol_data.empty() && !u_data.empty()){
                        // Запрос к AI
                        string ai_req = "Коротко в 1 предложение объясни почему олимпиада " + ol_data[1] + " (" + ol_data[9] + ") подходит ученику " + u_data[2] + " класса. Описание: " + ol_data[10];
                        string point = ask_ai(ai_req);
                        
                        // Экранируем кавычки для валидного JSON (базовая очистка)
                        size_t pos = 0;
                        while((pos = point.find("\"", pos)) != string::npos) { point.replace(pos, 1, "\\\""); pos += 2; }
                        while((pos = point.find("\n", pos)) != string::npos) { point.replace(pos, 1, " "); pos += 1; }

                        // Формируем JSON руками
                        string rsp_body = "{\n";
                        rsp_body += "\"id\": " + ol_data[0] + ",\n";
                        rsp_body += "\"name_1\": \"" + ol_data[1] + "\",\n";
                        rsp_body += "\"date_start\": \"" + ol_data[2] + "\",\n";
                        rsp_body += "\"date_end\": \"" + ol_data[3] + "\",\n";
                        rsp_body += "\"class_start\": " + ol_data[4] + ",\n";
                        rsp_body += "\"class_end\": " + ol_data[5] + ",\n";
                        rsp_body += "\"lvl\": \"" + ol_data[6] + "\",\n";
                        rsp_body += "\"frm\": \"" + ol_data[7] + "\",\n";
                        rsp_body += "\"lnk\": \"" + ol_data[8] + "\",\n";
                        rsp_body += "\"subjects\": \"" + ol_data[9] + "\",\n";
                        rsp_body += "\"description_1\": \"" + ol_data[10] + "\",\n";
                        rsp_body += "\"point\": \"" + point + "\"\n";
                        rsp_body += "}";

                        string rsp = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + to_string(rsp_body.size()) + "\r\n\r\n" + rsp_body;
                        nt.send(rsp);
                        cout << "SENDED: /api/olimp:" << olimp_id << "/" << tg_id << endl;
                        nt.dnet();
                        return;
                    }
                }
            }
        }
    }
    // if(methot == "POST"){
    //     if("/profile/" == path.substr(0 , 9)){
    //         db db1 = db();
    //         string tg_id = path.substr(9);
    //         if(id_valid_data(tg_id , &db1) != -1){
    //             nt.send(nf404);
    //             cout<<"SENDED: 404 Not Found"<<endl;
    //             nt.dnet();
    //         }

    //     }
    // }
    nt.send(nf404);
    cout<<"SENDED: 404 Not Found"<<endl;
    nt.dnet();
}

int main(int arg , char * args[]){
    https_init();
    const SSL_METHOD *method = TLS_server_method();
    SSL_CTX *ctx = SSL_CTX_new(method);
    if (!ctx) { perror("Unable to create SSL context"); exit(EXIT_FAILURE); }
    configure_context(ctx , "server.crt" , "server.key");
    cout<<"[+]SSL INIT COMPLITE"<<endl;
    cout<<"[/]starting server on port:"<<args[1]<<" for "<<args[2]<<" sessions"<<endl;
    ///init start
    int sock =  socket(AF_INET , SOCK_STREAM , 0);
    struct sockaddr_in serv , client;
    
    if(sock < 0){
        err("sock");
        return 1;
    }
    serv.sin_addr.s_addr = INADDR_ANY;
    serv.sin_family = AF_INET;
    serv.sin_port = htons(atoi(args[1]));
    if(bind(sock , (struct sockaddr * ) &serv , sizeof(serv)) < 0){
        err("bind");
        close(sock);
        return 1;
    }
    if(listen(sock , atoi(args[2])) < 0){
        err("listen");
        close(sock);
        return 1;
    }
    int nw_sock;
    init_st_sites("catalog_static/" , "ctg.txt" , &st_sites);
    //init_st_sites("catalog_static/" , "makets.txt" , &makets_sites);
    cout<<"[+] init complite "<<endl;
    //init end
    socklen_t cli_len = sizeof(sockaddr);
    while((nw_sock = accept(sock  , (sockaddr * )& client  , &cli_len))){
        cout<<"new client"<<endl;
        net buff =net(nw_sock  , client , ctx);
        thread t(main1 , buff);
        t.detach();
    }
    close(sock);
}