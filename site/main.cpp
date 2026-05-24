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
#include "net.hpp"
#include "funcs.hpp"
using namespace std;

string response_200_text[] = {
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/plain; charset=utf-8\r\n"
    "Content-Length: " , "\r\n"
    "Connection: close\r\n"
    "\r\n" };
string response_200_html[] = {
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=utf-8\r\n"
    "Content-Length: " , "\r\n"
    "Connection: close\r\n"
    "\r\n" };

string nf404 = ("HTTP/1.1 404 Not Found\r\n\r\n404 Not Found");
map<string , string > st_sites;

void err(string error){
    cout<<"[-]ERROR : "<<error<<endl;
}


void init_st_sites(string dir , string main_file , map <string ,string>* w){
    ifstream a = ifstream((dir + main_file).c_str());
    ifstream f;
    string bff;
    
    while(a>>bff){
        f = ifstream((dir + bff).c_str());
        if(!f.is_open()){err("file " +bff+" !f.is_open()");continue;}
        cout<<"[+]loading :"<<bff<<endl;
        string bff1((istreambuf_iterator<char>(f)) , (istreambuf_iterator<char>()));
        (*w)[bff]=bff1;
        f.close();
    }
    a.close();
}

string linux_commad(string commmand , int bf= 1){
    char bff[bf];
    string ans;

    FILE * p = popen(commmand.c_str() ,"r");
    if(!p){return ans;}
    while(fgets(bff , sizeof(bff) , p) != NULL){
        ans+=((string)bff);
    }
    return ans;
}


void main1(net nt){
    
    string message = nt.recv_http_3(1024);
    cout<<"client message :\n"<<message<<"\n------"<<endl;
    string path = get_arg1(&message, " ", " ");
    cout << "DEBUG: Path is -> [" << path << "]" << endl;

    string methot = message.substr(0, message.find(" "));
    cout<<"methot : "<<methot<<endl;
    if(path == "/"){
        string  bff = st_sites["index.html"];
            nt.send(response_200_html[0]+to_string(bff.size())+response_200_html[1]+bff);
            cout<<"SENDED: "<<path<<endl;
            close(nt.socket);
            return;
    }else if(path != ""){
        if(st_sites.count(path.substr(1))){
            string  bff = st_sites[path.substr(1)];
            nt.send(response_200_html[0]+to_string(bff.size())+response_200_html[1]+bff);
            cout<<"SENDED: "<<path<<endl;
            close(nt.socket);
            return;
        }
    }
    nt.send(nf404);
    cout<<"SENDED: 404 Not Found"<<endl;
    close(nt.socket);
}

int main(int arg , char * args[]){
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
    cout<<"[+] init complite "<<endl;
    //init end
    socklen_t cli_len = sizeof(sockaddr);
    while((nw_sock = accept(sock  , (sockaddr * )& client  , &cli_len))){
        cout<<"new client"<<endl;
        net buff = net(nw_sock);
        thread t(main1 , buff);
        t.detach();
    }
    close(sock);
}