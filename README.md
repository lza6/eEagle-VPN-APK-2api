# eEagle VPN → 2API 逆向报告与服务器收割

> 目标 APK：`eEagle VPN v2.12.9 b132 (Premium By ElaMods)`（`com.eeaglevpn.vpn`）
> 结论：**协议层已完全打穿** —— 无需账号即可枚举全部节点（free + premium 无服务端校验差异）并按需获取含完整凭证的连接配置。

## 1. APK 概览

| 项 | 值 |
|---|---|
| 包名 | `com.eeaglevpn.vpn` |
| 版本 | 2.12.9 (b132)，ElaMods 去广告破解版 |
| 技术栈 | Kotlin + Retrofit2 + OkHttp + Room + WireGuard(官方 Go 后端) + OpenVPN(ICS OpenVPN) + AmneziaWG 混淆 |
| 壳 | 无壳，未加固（对比 Zyro 系的 luoyesiqiu 壳，此包直接静态可解） |
| 内嵌资产 | `assets/autoLogin.ovpn`（完整 OpenVPN 配置+证书）、`assets/faisal_mac.conf`（完整 WireGuard 私钥配置） |

## 2. 后端 API

- Base：`https://prod-api.eeaglevpn.com/`（开发环境 `https://dev-api.eeaglevpn.com/`）

### 2.1 认证（关键发现）

Retrofit OkHttp 双拦截器（`di/NetworkModule.kt`）：

```kotlin
// ApiKeyInterceptor — 硬编码 API key
request.newBuilder().addHeader("x-api-key", "svhhdbhweuydhscwhbduy7823ouyewebdhvhhas").build()
// UUIDInterceptor — 本地生成、服务端不校验
request.newBuilder().addHeader("x-user-id", <random UUID>).build()
```

即：**任意 UUID 即可代表一个"设备身份"**，无签名、无时间戳、无设备指纹校验。

### 2.2 端点全表（从 VPNApiService 注解还原）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/location` | 国家/城市层级列表 |
| GET | `/server` | **节点全表**（free + premium，含 IP、协议、分类） |
| GET | `/configuration_file?id=<locationId>&type=<protocol>` | **下发完整连接配置**（含私钥） |
| GET | `/current_location` | 当前出口 IP 信息 |
| GET | `/package/?platform=android` | 订阅套餐列表 |
| GET | `/user-package` | 用户订阅详情（需真实 token） |
| POST | `/request/location/` | 请求某国家节点（`{"country":"USA","email":""}`） |
| POST | `/login` | 设备登录（provider 仅 `google`/`apple`） |
| GET | `/user-time` | 连接时长上报 |
| GET | `/user/marketing` | 激活营销回调 |

> ⚠️ 坑：配置下发参数名是 **`type`** 不是 `protocol`。传 `protocol=wireguard` 会 405 `Protocol not found`。

### 2.3 服务器清单（实测 2026-10-28）

14 台全量（free 与 premium 完全重叠，服务端未做订阅校验）：

| 层级 | 国家 | 城市 | IP | 协议 |
|---|---|---|---|---|
| free | United States | Seattle | 85.239.232.81 | wireguard,ovpn,ikev2,ipsec,amneziawg |
| free | United States | Orangeburg | 86.48.26.225 | 同上 |
| free | India | Mumbai | 185.193.19.75 | 同上 |
| free | India | Mumbai | 94.136.191.138 | 同上 |
| free | Singapore | Singapore | 84.247.146.240 | 同上 |
| free | France | Lauterbourg | 207.180.215.107 | 同上 |
| free | Japan | Tokyo | 46.250.254.104 | 同上 |
| free | United Kingdom | Portsmouth | 185.219.142.21 | 同上 |
| premium | US/FR/IN/UK/SG 共 7 台 | — | 见 `SERVERS.md` | 同上 |

TCP 全封闭属正常——纯 UDP 隧道（WG :51820），无效握手静默丢弃。

### 2.4 配置下发

每次调用 `/configuration_file` 服务端**新签一对 WireGuard keypair + PSK**，conf 形如：

```ini
[Interface]
PrivateKey = <fresh-key>          # 每次不同 → 凭证可无限轮换
Address = 10.8.0.143/16
DNS = 8.8.8.8, 8.8.4.4

[Peer]
PublicKey = GeZQPMGNgo0dBD4RU5ikxWcqlY3i0M09kyNHLoBi4VI=
PresharedKey = <fresh-psk>
Endpoint = 85.239.232.81:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

OpenVPN conf 为完整内联（CA/cert/key, AES-128-GCM, auth SHA256, udp 1194）。

## 3. 使用

### 工具（不落任何凭证进 git）

```bash
# 一键拉取全部节点 + 配置
pip install requests
python tools/harvest.py --out ./harvest
```

### Demo server

```bash
python demo_server.py            # 默认 :8902
# 打开 http://localhost:8902/ → 节点地图 + 一键拉取配置 + conf 预览
```

Demo 提供只读 API：`GET /api/servers`、`GET /api/config?tier=free&country=...&city=...&type=wireguard`（实时向上游新签，不缓存凭证）。

## 4. 代理池接入路径

这些是 VPN 隧道服务器而非 HTTP/SOCKS 代理，接入 `TRYINGOPEN_PROXY_FILE` 代理池需二跳：

```
harvest conf → wireguard-go / sing-box outbound (每节点一个) → 本地 SOCKS5 :1080x → 代理池
```

优点：WG 私钥按需新签 = 凭证永不过期；节点由上游统一维护，长期稳定。

## 5. 合规说明

本仓库仅用于协议研究与自己拥有合法使用权的账号/设备的互操作分析。所含工具不内置任何密钥；demo 不缓存、不分发凭证。

## 6. 目录

```
├── README.md            # 本报告
├── SERVERS.md           # 节点清单
├── demo_server.py       # demo（只读 API + 网页）
├── demo.html            # 前端页
├── tools/harvest.py     # 采集脚本（x-api-key 由运行方提供/自带）
```
