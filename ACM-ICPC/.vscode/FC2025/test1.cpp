#include <iostream>
#include <bits/stdc++.h>
using namespace std;

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int i ;
    cin >> i;
    int a;
    int b;
    int c;
    while(cin>>a>>b>>c){
            int d = a + b + c;
            cout<< (abs(21-d) > abs(14-d)? "YES" : "NO") << '\n';    
}
return 0;
}