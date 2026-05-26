#pragma once
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>


using namespace std;

const struct timeval tv={5 , 5}; //rcv , snd
void https_init(){
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();
}

void configure_context(SSL_CTX *ctx , string crt , string key) {
    // Ожидаем файлы server.crt и server.key в папке с программой
    if (SSL_CTX_use_certificate_file(ctx, crt.c_str(), SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    if (SSL_CTX_use_PrivateKey_file(ctx, key.c_str(), SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }
}
class net{
    public:
    struct sockaddr_in cli;
    SSL_CTX *ctx;
    SSL* ssl;
    int socket;
    net(int s ,sockaddr_in client ,SSL_CTX *ctx ):socket(s) , cli(client) , ctx(ctx){}

    void dnet(){
        if(ssl){
            SSL_free(ssl);
            SSL_shutdown(ssl);
        }
        close(socket);
    }

    bool init(){
        ssl = SSL_new(ctx);
        if (!ssl) {
                cout<<"[-]ERROR SSL";
                close(socket);
                return 1;
        }
        setsockopt(socket , SOL_PACKET , SO_RCVTIMEO ,(const void*)&tv , sizeof(tv));
        setsockopt(socket , SOL_PACKET , SO_SNDTIMEO , (const void*)&tv , sizeof(tv));
        SSL_set_fd(ssl, socket);
        if (SSL_accept(ssl) <= 0) {
                //ERR_print_errors_fp(stderr);
                return 1; // Если не договорились о шифровании, выходим
        }
        return 0;
    }
    int send(string message){
        return SSL_write(ssl , message.c_str() , message.size());
    }
    string recv_bare(int sbuff = 1024){
        char buff[sbuff] = {0};
        int n;
        string ans;
        while((n = SSL_read(ssl , buff , sbuff)) > 0){
            for(int n1 = 0;n1<n;n1++){
                ans+=buff[n1];
            }
        }
        return ans;
    }
    string recv(int sbuff = 1){

        char buff[sbuff] ;
        int n;
        string ans;
        while((n = SSL_read(ssl , buff ,sbuff )) > 0){
            ans.append(buff , n);
            //cout<<buff<<endl;
            if(ans.find("\r\n\r\n") != string::npos){
                return ans;
            }
        }
        return ans;
    }
    string recv2(int sbuff = 1){
        char buff[sbuff] ;
        int n , n1 , n2, n3;
        string ans;
        while((n = SSL_read(ssl , buff ,sbuff )) > 0){
            ans.append(buff , n);
            //cout<<buff<<endl;
            if((n1 =ans.find("\r\n\r\n")) != string::npos){
                if((n2 = ans.find("Content-Length: ")) != string::npos){
                    n2+=16;
                    if((n3 =ans.find("\r\n" , n2)) != string::npos){
                        int content_length = stoi(ans.substr(n2 , n3 - n2));
                        int body_received = ans.size() - (n1 + 4);
                        while(body_received < content_length && (n = SSL_read(ssl , buff ,sbuff )) > 0){
                            ans.append(buff , n);
                            body_received += n;
                        }
                    }
                }
                return ans;
            }
        }
        return ans;
    }

    string recv_http_1(int sbuff = 1){
        char buff[sbuff] = {0};
        int n , n1;
        //int endl = 0;
        string ans;
        while((n = (::recv(socket ,buff , sbuff , 0 ))) > 0){
            n1 = n;
            while(n > 0){
                ans+=buff[n1-n];
                n-=1;
            }
            if(ans.size() >= 4){
                int bf = ans.size();
                if(ans[bf -4] == '\r' && ans[bf-3] =='\n' &&ans[bf -2] == '\r' && ans[bf-1] =='\n'){
                    return ans;
                }
            }
        }
        return ans;
    }
    string recv_http_2(int sbuff = 1){
        char buff[sbuff] ;
        int n;
        string ans;
        while((n = (::recv(socket ,buff , sbuff , 0 ))) > 0){
            ans.append(buff , n);
            cout<<buff<<endl;
            if(ans.size() >= 4){
                int bf = ans.size();
                if(ans[bf -4] == '\r' && ans[bf-3] =='\n' &&ans[bf -2] == '\r' && ans[bf-1] =='\n'){
                    return ans;
                }
            }
        }
        return ans;
    }

};