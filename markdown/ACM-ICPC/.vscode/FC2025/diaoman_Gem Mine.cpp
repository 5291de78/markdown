#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        int n, x;
        ll d;
        cin >> n >> x >> d;
        vector<ll> w(n + 1), c(n + 1);
        for (int i = 1; i <= n; i++) cin >> w[i];
        for (int i = 1; i <= n; i++) cin >> c[i];   // c[1] 是 dummy，读进来不用

        ll C = 0, W = 0, ans = -1;
        for (int L = 1; L <= n; L++) {
            W = max(W, w[L]);          // W = max(w1..wL)
            if (L >= 2) C += c[L];     // C = c2+...+cL
            if (C > d) break;          // c_i ≥ 1，C 单调增，后面更不可能
            if (L >= x) ans = max(ans, (d - C) * W);
        }
        cout << ans << '\n';
    }
}
