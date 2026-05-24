#pragma once 

#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>

//for the HTTPS
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <iostream>

using namespace std;

class client_net{
    public:
    int sock;
    sockaddr_in server;
    SSL_CTX * ctx;
    SSL * ssl ;
    client_net(string ip , int port = 443 , string hostname = ""){
        sock= socket(AF_INET , SOCK_STREAM , 0);
        server.sin_family = AF_INET;
        server.sin_port = htons(port);
        server.sin_addr.s_addr = inet_addr(ip.c_str());
        if(connect(sock , (struct sockaddr * ) &server , sizeof(server)) < 0){
            return;
        }
        SSL_library_init();
        SSL_load_error_strings();
        const SSL_METHOD* method = TLS_client_method();
        ctx = SSL_CTX_new(method);
        ssl =  SSL_new(ctx);
        SSL_set_fd(ssl  , sock);

        SSL_set_tlsext_host_name(ssl, hostname.c_str());
    }
    client_net(int port = 443 , string hostname = ""){
        struct addrinfo hints, *res;
    
        memset(&hints, 0, sizeof(hints));
        hints.ai_family = AF_INET;       
        hints.ai_socktype = SOCK_STREAM; 


        if (getaddrinfo(hostname.c_str(), NULL, &hints, &res) != 0) {
            sock = -1;
            return;
        }


        sock= socket(AF_INET , SOCK_STREAM , 0);
        server.sin_family = AF_INET;
        server.sin_port = htons(port);
        server.sin_addr = ((struct sockaddr_in *)res->ai_addr)->sin_addr;
        freeaddrinfo(res);

        if(connect(sock , (struct sockaddr * ) &server , sizeof(server)) < 0){
            close(sock);
            return;
        }
        SSL_library_init();
        SSL_load_error_strings();
        const SSL_METHOD* method = TLS_client_method();
        ctx = SSL_CTX_new(method);
        ssl =  SSL_new(ctx);
        SSL_set_fd(ssl  , sock);
        SSL_set_tlsext_host_name(ssl, hostname.c_str());
        if (SSL_connect(ssl) <= 0) {
            close(sock);
            sock = -1;
            return;
        }
    }
    string get(int sbuff = 1024){
        char buff[sbuff];
        string ans = "";
        int a;
        while((a = SSL_read(ssl , buff , sbuff)) > 0){
            ans.append(buff , a);
        }
        return ans;
    }
    int send(string message){
        return SSL_write(ssl , message.c_str() , message.length());
    }
};