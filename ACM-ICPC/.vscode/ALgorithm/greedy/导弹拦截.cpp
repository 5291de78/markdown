#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    vector<int> a;
    int x;
    while (cin >> x) a.push_back(x);   // 读一行到 EOF
    int n = a.size();

    // 第一问：最长不上升子序列（a[j] >= a[i] 才能接上）
    vector<int> dp1(n, 1);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < i; j++)
            if (a[j] >= a[i]) dp1[i] = max(dp1[i], dp1[j] + 1);

    // 第二问：最长严格上升子序列（a[j] < a[i]）
    vector<int> dp2(n, 1);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < i; j++)
            if (a[j] < a[i]) dp2[i] = max(dp2[i], dp2[j] + 1);

    cout << *max_element(dp1.begin(), dp1.end()) << '\n'
         << *max_element(dp2.begin(), dp2.end()) << '\n';
    return 0;
}