## 连锁反应——Polygon 搜索者的 nonce 碰撞

MEV-X 中继缓存了一批搜索者（searcher）的竞价签名。为了抢 FastLane 密封竞价
的 250ms 窗口，这些钱包为了省时间复用了同一批 nonce，于是多个钱包的签名之间
出现了线性关系。

服务给你的东西：

- `sig[i].{message,hash,r,s}`：一批签名记录，来自多个钱包，**顺序已打乱**；
- `vault_wallet_pubkey`：其中一个钱包的公钥；
- `vault_op.{message,hash,r,s}`：该钱包签发的一条转账指令。

你需要恢复这个钱包的私钥，提交后取得凭证（Flag）。

### 提示

- 中继**不会**告诉你一共有几个钱包、哪个签名属于哪个钱包、哪些 nonce 被共享。
- 记录里混有若干条来自无关临时钱包的**噪音签名**，它们不参与任何碰撞。
- 每个签名都满足 `s·k ≡ e + r·d (mod n)`。把不同的 nonce 与私钥都当成未知数，
  就得到一个线性方程组。

### 连接方式

正式环境请使用题目页面显示的 `nc <host> <port>` 命令连接。服务给出全部数据后
会提示 `vault_private_key_hex>`，每会话最多尝试 5 次。

### 本地调试

附件中的 `server.py` 与容器内服务相同：

```bash
YL_DYFLAG='YulinSec{local_only}' PORT=20000 python3 server.py
nc 127.0.0.1 20000
```

附件中不含正式 Flag；容器启动时由平台通过 `YL_DYFLAG` 注入。

### 参考论文

Y. Madhwal, A. Seoev, R. Della Pietra, A. Smirnova, Y. Yanovich,
*Chain Reactions: How Nonce Collisions in ECDSA Compromise Polygon MEV Searchers*,
arXiv:2605.21498 (2026)，第 IV-C 节（跨钱包 nonce 碰撞）。
