#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <string>
#include "Song.h"

using namespace std;

vector<Song> load_datafile(){
    vector<Song> v;
    ifstream file("data.csv");
    if(!file.is_open()){
        cout<<"error"<<endl;
        return v;
    }
    string line;
    getline(file,line);
    while(getline(file,line)){
        Song temp;
        string s="";
        vector<string> t;
        bool quotes=false;
        for(int i=0;i<line.length();i++){
            if(line[i]=='"'){
                quotes=!quotes;
            }else if(line[i]==',' && !quotes){
                t.push_back(s);
                s="";
            }else{
                s+=line[i];
            }
        }
        if(t.size()<12){
            continue;
        }
        t.push_back(s);
        temp.name=t[1];
        temp.artist=t[2];
        temp.year=stoi(t[5]);
        temp.danceability=stof(t[7]);
        temp.energy=stof(t[8]);
        temp.loudness=stof(t[11]);
        v.push_back(temp);
    }
    return v;
}


int partition_danceability(vector<Song>& v,int h,int l){
    int middle=l+(h-l)/2;
    swap(v[middle],v[h]);
    Song p=v[h];
    int right=h-1;
    int left=l;
    while(true){
        while(left<=right && v[left].danceability<p.danceability){
            left+=1;
        }
        while(right>=left && v[right].danceability>p.danceability){
            right-=1;
        }
        if(left>=right){
            break;
        }
        swap(v[left],v[right]);
        left+=1;
        right-=1;
    }
    swap(v[left],v[h]);
    return left;
}

int partition_energy(vector<Song>& v,int h,int l){
    int middle=l+(h-l)/2;
    swap(v[middle],v[h]);
    Song p=v[h];
    int right=h-1;
    int left=l;
    while(true){
        while(left<=right && v[left].energy<p.energy){
            left+=1;
        }
        while(right>=left && v[right].energy>p.energy){
            right-=1;
        }
        if(left>=right){
            break;
        }
        swap(v[left],v[right]);
        left+=1;
        right-=1;
    }
    swap(v[left],v[h]);
    return left;
}

int partition_loudness(vector<Song>& v,int h,int l){
    int middle=l+(h-l)/2;
    swap(v[middle],v[h]);
    Song p=v[h];
    int right=h-1;
    int left=l;
    while(true){
        while(left<=right && v[left].loudness<p.loudness){
            left+=1;
        }
        while(right>=left && v[right].loudness>p.loudness){
            right-=1;
        }
        if(left>=right){
            break;
        }
        swap(v[left],v[right]);
        left+=1;
        right-=1;
    }
    swap(v[left],v[h]);
    return left;
}


void quickSort(vector<Song>& v,string d,int h,int l){
    if(l<h){
        int partidx;
        if(d=="danceability"){
            partidx=partition_danceability(v,h,l);
        }else if(d=="energy"){
            partidx=partition_energy(v,h,l);
        }else{
            partidx=partition_loudness(v,h,l);
        }
        quickSort(v,d,partidx-1,l);
        quickSort(v,d,h,partidx+1);
    }
}

//add pragma once to song or move song.h to this file
int main(){
    vector<Song> v=load_datafile();
    auto start=chrono::high_resolution_clock::now();
    quickSort(v,s,v.size()-1,0);
    auto stop=chrono::high_resolution_clock::now();
    auto time=chrono::duration_cast<chrono::milliseconds>(stop-start);
    cout<<"Time elapsed: "<<time.count()<<" ms"<<endl;
    return 0;
}
