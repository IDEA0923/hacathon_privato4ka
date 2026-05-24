#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

using namespace std;

string get_arg(string * text , string find , string stop = "\r\n"){

    int ind = 0;
    int i = 0;
    bool finded = false;
    string ans;
    while(i < text->size()){
    while(i < text->size() &&text->at(i) != find[0]){
            i++;
    }
    ind = 0;
    while((i + ind) < text->size() && ind < find.size()&&text->at(i+ind) == find[ind]  ){
        ind +=1;
    }
    if((i + ind) < text->size() && ind+1 == find.size() && text->at(i+ind) == find[ind]){
        i+=ind;
        //finded
        while(i < text->size()){
            while(i < text->size() &&text->at(i) != stop[0] ){
                ans+=text->at(i);
                i+=1;
            }
            ind = 0;
            while((i + ind) < text->size() && ind < stop.size()&&text->at(i+ind) == stop[ind]  ){
                ind +=1;
            }
            if((i + ind) < text->size() && ind+1 == stop.size() && text->at(i+ind) == stop[ind]){
                return ans;
            }
            if(i < text->size()){
                ans+=text->at(i);
                i+=1;
            }
        }
        return ans;
    }
    }
    return "";
}

string get_arg1(string * text , string find , string stop = "\r\n"){
    int ind = text->find(find );
    if(ind<0){return "";}
    ind+=find.size();
    int i2 = text->find(stop , ind);
    
    if(i2 <0){
        return text->substr(ind  );
    }else{
        cout<<"---++=-"<<((i2) - (ind))<<endl;
        return text->substr(ind, ((i2) - (ind)));
    }
    return "";
}