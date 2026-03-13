# 🖥️ Ubuntu Desktop 24.04 安装指南

> 目标：把你的 EPYC 服务器变成超级本地工作站

---

## 📋 准备清单

在开始前，准备好：

- [ ] **U 盘**（8GB 以上，会被格式化）
- [ ] **显示器 + 键盘**（安装时需要，装好后可以远程）
- [ ] **网线**（接路由器，自动获取 IP）
- [ ] **另一台电脑**（下载 ISO、制作启动盘）

---

## 第一步：下载 Ubuntu Desktop ISO

### 1.1 下载地址

官网下载（推荐）：
```
https://ubuntu.com/download/desktop
```

选择：**Ubuntu 24.04.1 LTS**（约 6GB）

或者用国内镜像更快：
```
https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/24.04/ubuntu-24.04.1-desktop-amd64.iso
```

### 1.2 下载完成后

记住文件保存位置，下一步要用。

---

## 第二步：制作启动 U 盘

### Mac 用户

**推荐用 balenaEtcher**（免费）：

1. 下载安装：https://etcher.balena.io/
2. 打开 Etcher
3. 选择下载的 ISO 文件
4. 选择 U 盘
5. 点击 Flash
6. 等待完成（约 5-10 分钟）

### Windows 用户

**推荐用 Rufus**（免费）：

1. 下载：https://rufus.ie/
2. 打开 Rufus
3. 设备：选择 U 盘
4. 引导类型：选择 ISO 文件
5. 分区类型：**GPT**
6. 目标系统：**UEFI**
7. 点击开始

---

## 第三步：服务器 BIOS 设置

### 3.1 接好线

- 显示器接服务器（HDMI 或 DP）
- 键盘接服务器（USB）
- U 盘插上
- 网线接上

### 3.2 开机进 BIOS

1. 开机，看屏幕提示按键（通常是 **DEL** 或 **F2**）
2. 进入 BIOS 设置

### 3.3 关键设置

在 BIOS 里找这几项：

```
✅ Boot Mode: UEFI（不是 Legacy）
✅ Secure Boot: Disabled（关闭）
✅ Boot Order: USB 设备排第一
```

### 3.4 保存退出

按 **F10** 保存并重启，会从 U 盘启动。

---

## 第四步：安装 Ubuntu

### 4.1 启动界面

看到 Ubuntu 启动菜单，选择：
```
Try or Install Ubuntu
```

### 4.2 安装向导

按顺序操作：

| 步骤 | 选择 |
|-----|------|
| 语言 | **中文（简体）** |
| 键盘布局 | 中文 / English (US) 都行 |
| 连接网络 | 应该自动连上了，跳过也行 |
| 安装类型 | **正常安装** |
| 安装选项 | ✅ 安装第三方软件（勾上） |

### 4.3 磁盘分区（重要！）

选择：**清除整个磁盘并安装 Ubuntu**

⚠️ 这会格掉 ESXi 和所有数据，确认没问题再继续。

> 高级选项：如果你想手动分区（比如单独设置 /home），可以选「其他选项」，但默认自动分区就够用。

### 4.4 设置用户

| 项目 | 建议填写 |
|-----|---------|
| 你的名字 | Jin（或你喜欢的） |
| 计算机名 | **homeserver**（方便识别） |
| 用户名 | **jin**（小写，登录用） |
| 密码 | 设一个强密码，**记住它！** |
| 登录选项 | 需要密码登录 |

### 4.5 等待安装

大约 10-20 分钟，完成后会提示重启。

**重启前拔掉 U 盘！**

---

## 第五步：首次启动配置

### 5.1 登录桌面

用刚才设置的用户名密码登录。

### 5.2 跳过初始设置

首次登录会有一些向导（在线账户、隐私等），全部跳过就行。

### 5.3 打开终端

按 `Ctrl + Alt + T` 打开终端。

### 5.4 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

等待完成（可能要几分钟）。

### 5.5 安装 SSH 服务（关键！）

```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

### 5.6 查看 IP 地址

```bash
ip addr | grep inet
```

找到类似 `192.168.x.x` 的地址，**记下来**，这是你服务器的 IP。

### 5.7 安装远程桌面

```bash
# 安装 xrdp（Windows/Mac 都能连）
sudo apt install -y xrdp
sudo systemctl enable xrdp
sudo systemctl start xrdp
```

---

## 第六步：测试远程连接

### 从 Mac 连接

**SSH 测试：**
```bash
ssh jin@192.168.x.x  # 替换成你的 IP
```

**远程桌面：**
1. 打开「Microsoft Remote Desktop」（App Store 下载）
2. 添加电脑：输入 IP 地址
3. 用户名密码：jin / 你的密码
4. 连接！

### 从 Windows 连接

**远程桌面：**
1. 按 Win+R，输入 `mstsc`
2. 输入 IP 地址
3. 登录

---

## 第七步：告诉我，我来接管

完成以上步骤后，给我发：

```
✅ IP 地址：192.168.x.x
✅ 用户名：jin
✅ SSH 可连接确认
```

### 或者配对 OpenClaw 节点

在终端运行：
```bash
curl -fsSL https://get.openclaw.ai | bash
openclaw node pair
```

把配对码发给我，我直接接管。

---

## 🤖 我接管后自动完成

- [ ] 系统优化
- [ ] Docker 安装
- [ ] FFmpeg + 视频处理环境
- [ ] 中文字体完善
- [ ] Ollama 本地 LLM
- [ ] Book-Video-Pipeline 部署
- [ ] 监控和自动化脚本

---

## ❓ 常见问题

### Q: 启动后黑屏？
→ 显卡兼容问题，开机选「Safe Graphics」模式

### Q: 看不到 U 盘启动选项？
→ 检查 BIOS 的 Secure Boot 是否关闭

### Q: 安装超级慢？
→ 正常，23TB 硬盘格式化需要时间

### Q: 忘记密码？
→ 重装吧，反正快 😂

---

## 📞 需要帮助？

安装过程中遇到问题，截图发给我，实时指导。

Let's go! 🚀
