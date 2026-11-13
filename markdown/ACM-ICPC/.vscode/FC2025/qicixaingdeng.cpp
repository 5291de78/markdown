#include<iostream>
#include<vector>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T = 0;
    int n = 0;
    int x = 0;
    float adx = 0;
    vector<int> a1;
    vector<int> a2;
    cin >> T;
    for(int i = 0; i < T ; i ++){
        a1.clear();         //每轮循环记得清理memory
        a2.clear();
        cin >> n;
        for(int j = 0 ; j < n ; j ++){
            cin >> x;
            a1.push_back(x);
        }
        for(int j = 0 ; j < n ; j ++){
            cin >> x;
            a2.push_back(x);
        }
        adx = 0;
        int len = 0;
        for(int i = 0;adx != 0 && i < n ; i++){
            if(a1[i] * a2[i] != 0){
                len = i;               
            }
        }
        if(a1[len] >= a2[len]){
            adx = a1[0] / a2[0];
            for(int j = len; j < n ; j++){
               if((adx - a1[j] / a2[j]) <1e-8){cout<<"NO"<<"\n";break;}  
            }
            cout<<"YES"<<"\n";
        }else{
            adx = a2[len] / a1[len];
            for(int j = len; j < n ; j++){
               if((adx - a2[j] / a1[j]) <1e-8 ){cout<<"NO"<<"\n";break;}  
            }
            cout<<"YES"<<"\n";
        }
    }    
    
}
/*
 
3
3
2 4 5
-4 -8 -10
3
0 0 1
0 0 -4
3
0 1 1
0 2 -2

*/