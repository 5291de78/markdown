#include <iostream>
#include <math.h>
#include <vector>
using namespace std;

int gcd(int a, int b) {
    while(b) {
        a %= b;
        swap(a,b);
    }
    return a;
}


int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    vector<int> abc(3,0);
    vector<int> xyz(3,0);
    bool yn =false;
    while(T--){
        yn = true;
        abc.clear();
        xyz.clear();
        for(int x = 0 ; x < 3 ; x ++){cin >> abc[x];}
        for(int x = 0 ; x < 3 ; x ++){cin >> xyz[x];}
        for(int x = 0 ; x < 3 ; x ++){
            if(gcd(abc[x] , xyz[x]) != abc[x]){yn = false;}
        }
        if(!yn){cout<<"YES"<<"\n";}
        else{cout<<"No"<<"\n";}
    }
}