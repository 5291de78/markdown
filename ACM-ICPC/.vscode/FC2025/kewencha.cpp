#include<iostream>
#include<vector>
#include<algorithm>
#include<map>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    int D;
    int Q;
    int ans;
    int p;
    int p2;
    map<int , int>ans_map;
    vector<int> x(D,0);
    vector<int> z(Q,0);
    while(T -- ){
        D = 0;
        Q = 0;
        ans = 0;
        cin >> D >> Q; 
        p = 0;
        for(int y = 0;y<D;y++){
            cin >> p;
            ans += p;
            x[y] += p;
        }
        for(int y = 0;y<D;y++){
            cin >> p;
            x[y] += p;
        }
        sort(x.begin() , x.end());
        for(int y = 0; y < Q ; y ++ ){
            cin >> z[y];
        }
        /*
        while(Q--){
            int p2 = 0;
            cin >> p;
            for(int y = 0; y < p ;y++){
                p2 -= x[y];
            }
            cout << ans + p2 << '\n';
        }
        */

        
    }
}