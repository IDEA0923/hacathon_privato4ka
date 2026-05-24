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

#include <libpq-fe.h>

#include "net_https.hpp"
#include "funcs.h"
#include "database.hpp"

#include "responses.hpp"

using namespace std;

map<string , string > st_sites;

map<string , string > makets_sites;


void main1(net nt){
    if(nt.init()){nt.dnet();return;}
    string message = nt.recv2(1024);
    cout<<"[+]new client ip :"<<inet_ntoa(nt.cli.sin_addr);
    cout<<"client message :\n"<<message<<"\n------"<<endl;
    string path = get_arg1(&message, " ", " ");
    cout << "DEBUG: Path is -> [" << path << "]" << endl;

    string methot = message.substr(0, message.find(" "));
    cout<<"methot : "<<methot<<endl;
    if(methot == "GET"){
        if(path == "/"){
            string rsp = response_200_html[0]+to_string(st_sites["index.html"].size())+response_200_html[1]+st_sites["index.html"];
            nt.send(rsp);
            cout<<"SENDED: index.html"<<endl;
            nt.dnet();
            return;
        }
    }
    if(methot == "POST"){
        
    }
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
    init_st_sites("catalog_static/" , "makets.txt" , &makets_sites);
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