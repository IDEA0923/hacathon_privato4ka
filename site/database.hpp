#pragma once
#include <iostream>
#include <libpq-fe.h>
#include <vector>
#include <random>
#include <ctime>
using namespace std;

string config_to_pg = "host=db port=5432 dbname="+string(getenv("POSTGRES_DB"))+" user="+string(getenv("POSTGRES_USER"))+" password="+string(getenv("POSTGRES_PASSWORD"));

class db{
    public:
    PGconn *conn;
    bool ok = true;
    db(string config = config_to_pg ){
        conn = PQconnectdb(config.c_str());
        if(PQstatus(conn) != CONNECTION_OK){
            ok = false;
            PQfinish(conn);
            return;
        }

    }
    //db(const db&) = delete;
    //db& operator=(const db&) = delete;

    vector<vector<string>> req_with_ans(string req ,vector<string> prms ){
        const char* params[prms.size()] ;
        for(int i = 0;i <prms.size();i++){
            params[i]= prms[i].c_str();
        }
        PGresult* res = PQexecParams(this->conn , req.c_str() ,prms.size() , NULL , params , NULL , NULL , 0 );
        if(PQresultStatus(res) != PGRES_TUPLES_OK && PQresultStatus(res) != PGRES_COMMAND_OK ){
            PQclear(res);
            return {};
        }
        vector<vector<string>> ans;
        int rows = PQntuples(res);
        int fields = PQnfields(res);
        char * bufff;
        for(int i1 = 0;i1<rows;i1+=1){
            vector<string> buff;
            for(int i2 = 0;i2<fields;i2+=1){
                bufff = PQgetvalue(res , i1 , i2);
                buff.push_back(bufff ? bufff : "");
            }
            ans.push_back(buff);
        }
        PQclear(res);
        return ans;
    }

    ~db(){
        if(conn){
            PQfinish(conn);
            conn = nullptr;
        }
        
    }
};



// void delete_all_other_sesssion_uuid(string uid , db* db1){
//     vector<vector<string>>fdb = db1->req_with_ans("DELETE FROM ssid_u WHERE user_id = $1 ;" , {uid});
// }
// void add_data(int data_type , string data , string uuid, db* db1){
//     vector<vector<string>>fdb = db1->req_with_ans("INSERT INTO device_data"+to_string(data_type)+" (uuid , dt) VALUES ($1 , $2)" , {uuid , data});
// }
// bool check_cooldown(int data_type , string uuid, db* db1){
//     return db1->req_with_ans("SELECT uuid FROM device_data"+to_string(data_type)+" WHERE uuid = $1 AND added > NOW() - INTERVAL '30 seconds';" , {uuid}).size() > 0;
// }
// string count_devices(int uid ,db *db1){
//     return (db1->req_with_ans("SELECT COUNT(*) FROM devices WHERE user_id = $1" , {to_string(uid)})[0][0]);
// }
int id_valid_data(string tg_id ,db* db1 ){
    vector<vector<string>>fdb = db1->req_with_ans("SELECT id FROM users WHERE tg_id" , {tg_id});
    if(fdb.size() == 0){
        return -1;
    }
    return stoi(fdb[0][0]);
}
string generate_UUID(){
    srand(time(0));
    string buff = "0123456789abcdef";
    string ans = "";
    for(int i = 0 ; i<8;i++){
        ans+=buff[rand()%16];
    }
    ans+="-";
    for(int i = 0 ; i<4;i++){
        ans+=buff[rand()%16];
    }
    ans+="-4";
    for(int i = 0 ; i<3;i++){
        ans+=buff[rand()%16];
    }
    ans+="-a";
    for(int i = 0 ; i<3;i++){
        ans+=buff[rand()%16];
    }
    ans+="-";
    for(int i = 0 ; i<12;i++){
        ans+=buff[rand()%16];
    }
    return ans;
}

