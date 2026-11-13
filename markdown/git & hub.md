# git & hub

```
cd 绝对路径
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin 仓库地址
git pull origin main --allow-unrelated-histories
git push -u origin main
```

User uploaded an image and asks for a comprehensive explanation of git commands, fork, branches, GitHub usage. Let me look at the image first.

User has a GitHub repo MCM-ICM （建模比赛的学习笔记） and wants a comprehensive git tutorial: commands, fork, branches, how to use GitHub. Give a thorough but structured explanation in Chinese.
看到你的仓库了（MCM-ICM，建模比赛学习笔记）。下面系统讲一遍，按「概念 → 本地操作 → 远程协作 → GitHub 流程」的顺序。

---

## 一、核心概念（先懂这个，命令才有意义）

Git 管的是**三个区域**：

```
工作区(你写的代码) --git add--> 暂存区 --git commit--> 本地仓库 --git push--> 远程仓库(GitHub)
```

- **commit（提交）**：一次快照，记录了"谁、什么时候、改了什么"
- **分支（branch）**：一条独立的开发线。`main` 是主分支，你可以开新分支做实验，不弄坏主线
- **远程（remote）**：GitHub 上的仓库，默认叫 `origin`

---

## 二、本地常用命令

### 1. 起步

```bash
git init                      # 把当前文件夹变成 git 仓库
git clone <url>               # 把 GitHub 仓库整个下载到本地
git config --global user.name "你的名字"    # 首次使用要配置身份
git config --global user.email "邮箱"
```

### 2. 日常三连（90% 时间在用）

```bash
git status                    # 看当前状态：哪些文件改了、哪些没跟踪
git add .                     # 把所有改动放进暂存区（git add 文件名 = 只加某个）
git commit -m "说明这次改了什么"
git push                      # 推送到 GitHub
```

### 3. 查看历史

```bash
git log --oneline             # 简洁版提交历史
git diff                      # 看还没 add 的改动具体改了什么
git diff --staged             # 看已 add 的改动
```

### 4. 后悔药

```bash
git restore 文件名             # 丢弃工作区的修改（还没 add）
git restore --staged 文件名    # 从暂存区撤出来（add 错了）
git reset --soft HEAD~1       # 撤销上一次 commit，改动保留
git reset --hard HEAD~1       # 撤销上一次 commit，改动全删（危险！）
git revert <commit的id>       # 安全地"反向提交"抵消某次 commit（已 push 的用这个）
```

---

## 三、分支（branch）——重点

**为什么需要分支**：比如你想给笔记仓库加个"2026 美赛真题"模块，写一半发现写错了，如果直接在 main 上改，仓库就乱了。开分支 = 复制一条线随便折腾，满意了再合并回 main。

```bash
git branch                    # 看有哪些分支（* 号是当前所在）
git branch 新分支名            # 创建分支
git switch 分支名              # 切换过去（老命令是 git checkout）
git switch -c 新分支名         # 创建并切换（一步到位）

# 在新分支上正常 add / commit ...

git switch main               # 回主分支
git merge 新分支名             # 把新分支的内容合并进 main
git branch -d 新分支名         # 合并完删掉它
```

**合并冲突（conflict）**：如果 main 和分支改了同一文件的同一行，git 会问你要哪个。打开文件会看到：

```
<<<<<<< HEAD
main 的内容
=======
分支的内容
>>>>>>> 分支名
```

手动改成想要的样子，删掉标记行，然后 `git add .` + `git commit` 就解决了。

---

## 四、远程操作

```bash
git remote -v                 # 看远程仓库地址
git pull                      # 把 GitHub 上的新内容拉下来合并（= fetch + merge）
git fetch                     # 只拉下来看看，不合并
git push                      # 推上去
git push -u origin main       # 第一次推送时建立关联，之后直接 git push
```

**pull vs clone**：clone 是第一次整个下载；pull 是之后每次同步更新。

---

## 五、Fork 是什么

场景：你看到别人的仓库（比如一个建模模板库）想改，但你**没有它的写权限**。

- **Fork** = 把别人的仓库**复制一份到你自己的 GitHub 账号下**，这份随便你改
- 改完后可以发 **Pull Request（PR）**，请求原作者把你的改动合并回他的仓库
- 开源协作的标准流程：**Fork → clone 到本地 → 改 → push 到自己的 fork → 发 PR**

对自己的仓库不需要 fork，直接 clone 就行。

**Star**：收藏/点赞。**Watch**：订阅更新通知。**Issues**：提 bug / 讨论区。

---

## 六、GitHub 日常使用流程（结合你的仓库）

**个人项目（你现在的情况）**：

```bash
git clone https://github.com/5291de78/MCM-ICM.git   # 第一次下载
cd MCM-ICM
# ...写笔记/代码...
git add .
git commit -m "添加线性规划笔记"
git push
```

换电脑了先 `git pull` 再开始写，避免冲突。

**给别人协作（比如队友）**：仓库页面 Settings → Collaborators → 加队友，队友 clone 后同样 add/commit/push。两个人同时改同一文件才容易冲突，养成**先 pull 再 push** 的习惯。

**GitHub 网页上也能直接改**：你截图里的 `Add file` 可以上传/新建文件，文件可以点进去直接在线编辑，适合改 README 这种小改动。但代码建议本地改完再 push。

---

## 七、容易踩的坑

1. **大文件**：GitHub 单文件限 100MB，数据集别直接传，用 `.gitignore` 排除
2. **`.gitignore`**：仓库根目录建这个文件，写上不想跟踪的（如 `__pycache__/`、`.idea/`、`.env`）
3. **密码不能用了**：现在 push 要用 Personal Access Token 或 SSH key，不能直接用账号密码
4. **commit message 写清楚**：`"update"` 这种三个月后你自己都看不懂

---

建议的最小上手路径：先练熟 `add → commit → push` 三连 + `pull`，然后试着开个分支合并一次，这两步会了，GitHub 日常就通了。想针对哪部分展开（比如 SSH 配置、PR 流程、gitignore 模板）直接说。



## git --help

```
C:\Program Files\Microsoft Visual Studio\18\Community>git --help
usage: git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--no-lazy-fetch]
           [--no-optional-locks] [--no-advice] [--bare] [--git-dir=<path>]
           [--work-tree=<path>] [--namespace=<name>] [--config-env=<name>=<envvar>]
           <command> [<args>]

These are common Git commands used in various situations:

start a working area (see also: git help tutorial)
   clone      Clone a repository into a new directory
   init       Create an empty Git repository or reinitialize an existing one

work on the current change (see also: git help everyday)
   add        Add file contents to the index
   mv         Move or rename a file, a directory, or a symlink
   restore    Restore working tree files
   rm         Remove files from the working tree and from the index

examine the history and state (see also: git help revisions)
   bisect     Use binary search to find the commit that introduced a bug
   diff       Show changes between commits, commit and working tree, etc
   grep       Print lines matching a pattern
   log        Show commit logs
   show       Show various types of objects
   status     Show the working tree status

grow, mark and tweak your common history
   backfill   Download missing objects in a partial clone
   branch     List, create, or delete branches
   commit     Record changes to the repository
   history    EXPERIMENTAL: Rewrite history
   merge      Join two or more development histories together
   rebase     Reapply commits on top of another base tip
   reset      Set `HEAD` or the index to a known state
   switch     Switch branches
   tag        Create, list, delete or verify tags

collaborate (see also: git help workflows)
   fetch      Download objects and refs from another repository
   pull       Fetch from and integrate with another repository or a local branch
   push       Update remote refs along with associated objects

'git help -a' and 'git help -g' list available subcommands and some
concept guides. See 'git help <command>' or 'git help <concept>'
to read about a specific subcommand or concept.
See 'git help git' for an overview of the system.
```

