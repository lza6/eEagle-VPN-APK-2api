# eEagle VPN 服务器清单（从 APK v2.12.9 逆向）

| 层级 | 国家 | 城市 | IP | 协议 | 类别 |
|---|---|---|---|---|---|
| free | United States | Seattle | 85.239.232.81 | wireguard,ovpn,ikev2,ipsec,amneziawg | streaming |
| free | United States | Orangeburg | 86.48.26.225 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| free | India | Mumbai | 185.193.19.75 | wireguard,ovpn,ikev2,ipsec,amneziawg | gaming |
| free | India | Mumbai | 94.136.191.138 | wireguard,ovpn,ikev2,ipsec,amneziawg | streaming |
| free | Singapore | Singapore | 84.247.146.240 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| free | France | Lauterbourg | 207.180.215.107 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| free | Japan | Tokyo | 46.250.254.104 | wireguard,ovpn,ikev2,ipsec,amneziawg | streaming |
| free | United Kingdom | Portsmouth | 185.219.142.21 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| premium | United States | Orangeburg | 217.216.89.179 | wireguard,ovpn,ikev2,ipsec,amneziawg | gaming |
| premium | United States | Orangeburg | 85.239.230.206 | wireguard,ovpn,ikev2,ipsec,amneziawg | gaming |
| premium | France | Lauterbourg | 176.57.188.9 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| premium | India | Mumbai | 147.93.153.199 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |
| premium | India | Mumbai | 94.136.188.135 | wireguard,ovpn,ikev2,ipsec,amneziawg | gaming |
| premium | Singapore | Singapore | 46.250.224.104 | wireguard,ovpn,ikev2,ipsec,amneziawg | - |

共 14 台。配置文件（含 WG 私钥/PSK）在 configs/，48 份（wireguard/ovpn/ipsec/amneziawg）。

## 代理池接入说明
- WireGuard: UDP 51820，单机 conf 就绪，可用 wireguard-go / sing-box outbound 直接拨号
- OpenVPN: conf 就绪 (AES-128-GCM, auth SHA256)
- 这些不是 HTTP/SOCKS 代理，需经隧道客户端转成本地 SOCKS5 后接入 TRYINGOPEN_PROXY_FILE
