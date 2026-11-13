#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    ll n, c, p, q;
    scanf("%lld %lld %lld %lld", &n, &c, &p, &q);
    static char s[500010];
    scanf("%s", s + 1);

    vector<ll> pre(n + 1, 0);
    for (int i = 1; i <= n; i++)
        pre[i] = pre[i - 1] + (s[i] == '1' ? q : -p);

    deque<int> dq;      
    int last = 0, ans = 0;

    for (int r = 1; r <= n; r++) {
        int j = r - (int)c;                 
        if (j >= 0) {
            while (!dq.empty() && pre[dq.back()] >= pre[j]) dq.pop_back();
            dq.push_back(j);
        }
        while (!dq.empty() && dq.front() < last) dq.pop_front();  

        if (!dq.empty() && pre[r] >= pre[dq.front()]) {          
            ans++;
            last = r;                       
            dq.clear();
        }
    }
    printf("%d\n", ans);
    return 0;
}