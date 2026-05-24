#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>

using namespace std;

class net{
    public:
    int socket;
    net(int s):socket(s){

    }
    int send(string message){
        return ::send(socket , message.c_str() , message.size(), 0);
    }

    string recv(int sbuff = 1024){
        char buff[sbuff] = {0};
        int n;
        string ans;
        while((n == (::recv(socket ,buff , sbuff , 0 ))) > 0){
            ans+=buff;
        }
        return "a";
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
    string recv_http_3(int sbuff = 1){
        char buff[sbuff] ;
        int n;
        string ans;
        while((n = (::recv(socket ,buff , sbuff , 0 ))) > 0){
            ans.append(buff , n);
            cout<<buff<<endl;
            if(ans.find("\r\n\r\n")){
                return buff;
            }
        }
        return ans;
    }
};