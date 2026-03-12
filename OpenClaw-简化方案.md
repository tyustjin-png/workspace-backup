# OpenClaw 整合方案（极简版）

## 🎯 一句话总结

**一个 OpenClaw，服务所有设备，复用一个 Claude Max 订阅。**

---

## 📱 三台设备

```
工作电脑（MBP）  →  家里服务器（Mac mini）  →  云服务器（OpenClaw）
   轻量化              存储 + 开发                  AI 中枢
```

---

## 🔧 怎么配置

### MBP 上的 Obsidian
装插件（Text Generator），填这三个：
```
地址：http://云服务器IP:18789/v1
密钥：fdefab2e7ed757595b49de9fd04625af275c0b05ccadd69f
模型：openclaw:main
```

### MBP 上的 VS Code  
装插件（Continue），填一样的三个参数。

---

## 💡 为什么好

- ✅ **省钱**：一个订阅($20/月)，不用重复买 API
- ✅ **轻量**：MBP 不装大模型，保持快速
- ✅ **统一**：所有 AI 调用走一个入口

---

## ⚡ 工作流

**写笔记：** Obsidian → 云服务器 → Claude Max → 返回结果  
**写代码：** VS Code → 云服务器 → Claude Max → 返回结果

---

## 📋 待办清单

- [ ] MBP Obsidian 装插件
- [ ] MBP VS Code 装插件
- [ ] 填入上面的三个参数
- [ ] 测试能不能调用

---

**就这么简单！** 🎉
