#include <iostream>
#include <vector>
#include <math.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    vector<int> t = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97};
    vector<int> p(20,1);
    int y = 0;
    int g = 0;
    for(int x = 0;x < 20 ; x++){
        y = t[x];
        g = 0;
        cout << "? " << y << "\n";
        cout.flush();
        cin>>g;
        if(g == 1){p[0] = y;}
    }
    int z =1;
    for(int x : p){
        z *= x;
    }
    cout<<"! " << z << "\n";
}