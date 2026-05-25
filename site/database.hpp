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

// int id_valid_data(string tg_id ,db* db1 ){
//     vector<vector<string>>fdb = db1->req_with_ans("SELECT id FROM users WHERE tg_id = $1" , {tg_id});
//     if(fdb.size() == 0){
//         return -1;
//     }
//     return stoi(fdb[0][0]);
// }
// vector<string> count_devices(string tg_id ,db *db1){
//     vector<vector<string>>fdb = db1->req_with_ans("SELECT tg_id , subjects , class , region FROM  users WHERE tg_id = $1" , {tg_id});
//     return fdb[0];
// }
// Пофиксил синтаксис SQL (не было = $1)
int id_valid_data(string tg_id, db* db1){
    vector<vector<string>> fdb = db1->req_with_ans("SELECT id FROM users WHERE tg_id = $1", {tg_id});
    if(fdb.empty()){
        return -1;
    }
    return stoi(fdb[0][0]);
}

vector<string> get_user_info(string tg_id, db *db1){
    vector<vector<string>> fdb = db1->req_with_ans("SELECT tg_id, subjects, class, region FROM users WHERE tg_id = $1", {tg_id});
    if(fdb.empty()) return {};
    return fdb[0];
}

vector<string> get_suitable_olimps(string tg_id, db* db1) {
    vector<string> u_data = get_user_info(tg_id, db1);
    if(u_data.empty()) return {};
    string subjects = u_data[1];
    string cls = u_data[2];
    // string region = u_data[3]; // Если в olimps добавишь регион, раскомментируй и добавь в запрос
    
    string q = "SELECT id FROM olimps WHERE class_start <= $1 AND class_end >= $1 AND subjects = $2 AND date_start BETWEEN NOW() AND NOW() + INTERVAL '1 month'";
    vector<vector<string>> o_data = db1->req_with_ans(q, {cls, subjects});
    
    vector<string> res;
    for(auto& row : o_data) res.push_back(row[0]);
    return res;
}
vector<string> get_suitable_olimps1(string tg_id, db* db1) {
    // 1. Получаем инфо о юзере (tg_id, subjects, class, region)
    vector<string> u_data = get_user_info(tg_id, db1);
    if(u_data.empty()) return {};
    
    string subjects = u_data[1]; // Например "МФ" (Математика, Физика)
    string cls = u_data[2];      // Класс, например "9"
    string region = u_data[3];   // Регион, например "77"
    
    // 2. Пишем правильный SQL-запрос к таблице events
    // - Проверяем класс: class_start <= класс_юзера <= class_end
    // - Проверяем регион: region олимпиады равен региону юзера
    // - Проверяем дату: начнется в будущем (date_start >= NOW())
    // - Проверяем предметы: предмет олимпиады есть в строке предметов юзера
    string q = "SELECT id FROM events WHERE "
               "class_start <= $1 AND class_end >= $1 "
               "AND region = $2 "
               "AND date_start >= NOW() "
               "AND POSITION(subjects IN $3) > 0 "
               "ORDER BY date_start ASC"; // Сначала те, что "скоро"
               
    vector<vector<string>> o_data = db1->req_with_ans(q, {cls, region, subjects});
    
    vector<string> res;
    for(auto& row : o_data) {
        res.push_back(row[0]);
    }
    return res;
}

vector<string> get_olimp_info(string id, db *db1){
    string q = "SELECT id, name_1, date_start, date_end, class_start, class_end, lvl, frm, lnk, subjects, description_1 FROM olimps WHERE id = $1";
    vector<vector<string>> fdb = db1->req_with_ans(q, {id});
    if(fdb.empty()) return {};
    return fdb[0];
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

