# FHDS Trigger Effects

> Steam Deck 游戏模式下 Forza Horizon 的 DualSense 扳机震动插件

[English version below](#english)

---

## 简介

FHDS Trigger Effects 是一个 Decky Loader 插件，将 [Forza-Horizon-DualSense-Python](https://github.com/HamzaYslmn/Forza-Horizon-DualSense-Python) 的扳机震动功能带入 Steam Deck 的游戏模式。无需桌面模式，无需手动启动脚本——直接在游戏模式中通过 Decky 插件商店安装，即开即用。

当你在 Forza Horizon 中驾驶时，DualSense 手柄的扳机会根据游戏遥测数据产生真实的物理反馈：

- **刹车（左扳机）**：踩下时有渐进阻力，轮胎抱死时 ABS 高频弹跳
- **油门（右扳机）**：踩下时有渐进阻力，换挡瞬间有冲击感，接近红线转速限制器震动
- **手刹**：额外的大阻力反馈

所有效果与 Steam 原生手柄震动共存，互不干扰。

## 功能

- 双扳机震动效果，基于 Forza Horizon UDP 遥测数据
- Decky 插件 UI 实时调节参数（力度、曲线、开关）
- 随 Steam Deck 系统语言自动切换中英文
- 一键启停总开关，关闭后 Steam 震动不受任何影响
- 设置自动持久化，休眠/重启不丢失

## 安装

### 方式一：Decky 插件商店

提交至 [decky-plugin-database](https://github.com/SteamDeckHomebrew/decky-plugin-database) 后即可在 Decky 内置商店搜索安装。

### 方式二：手动安装

1. 从 [Releases](https://github.com/Sci-fi-Borg/fhds-in-decky-loader/releases) 下载 `fhds-decky-v*.zip`
2. 解压到 `~/homebrew/plugins/`
3. Decky 中重载插件

## 使用

1. 在 Decky 中打开 FHDS Trigger Effects 设置面板
2. 根据手感调整刹车/油门的最大力度和曲线
3. 进入 Forza Horizon，在 **设置 → HUD 和游戏玩法** 中开启 Data Out：
   - Data Out：**开**
   - Data Out IP 地址：`127.0.0.1`
   - Data Out IP 端口：`5300`
4. 开始驾驶，感受扳机震动

## 开发

```bash
git clone https://github.com/Sci-fi-Borg/fhds-in-decky-loader.git
cd fhds-in-decky-loader
pnpm install
pnpm run build
python package_plugin.py
```

## 参考项目

- [Forza-Horizon-DualSense-Python](https://github.com/HamzaYslmn/Forza-Horizon-DualSense-Python) — HamzaYslmn 的原项目，提供了 DualSense HID 通信和 Forza UDP 协议解析
- [decky-loader](https://github.com/SteamDeckHomebrew/decky-loader) — Steam Deck Homebrew 的插件加载框架
- [decky-plugin-template](https://github.com/SteamDeckHomebrew/decky-plugin-template) — Decky 插件模板

## 注意事项

- 首次使用建议通过 USB 连接 DualSense，蓝牙模式未经充分测试
- 如果扳机效果消失，在 Decky 中关闭再打开总开关即可重置
- 不要在 Forza Horizon 中同时运行桌面版的 Forza-Horizon-DualSense-Python，会端口冲突
- 插件写入 HID 报告时使用 `valid_flag0=0x0C`（仅扳机），并通过 200ms 限流保护 Steam 震动的完整性

## 许可

BSD-3-Clause © 2026 tau

---

## English

### About

FHDS Trigger Effects brings the [Forza-Horizon-DualSense-Python](https://github.com/HamzaYslmn/Forza-Horizon-DualSense-Python) experience to Steam Deck's gaming mode via Decky Loader. No desktop mode required — install it from the Decky plugin store and it runs automatically.

Your DualSense triggers react to Forza Horizon telemetry in real time:

- **Brake (L2)**: Progressive resistance, ABS pulse on tire lockup
- **Throttle (R2)**: Progressive resistance, gear shift thump, rev limiter buzz
- **Handbrake**: Maximum resistance override

All effects coexist with Steam's native controller rumble.

### Features

- DualSense trigger effects driven by Forza Horizon UDP telemetry
- Real-time parameter adjustments via Decky UI (force, curve, toggles)
- Auto language switch (Chinese / English) based on system locale
- One-click master switch — Steam rumble untouched when disabled
- Persistent settings across sleep and reboot

### Installation

1. Install from Decky Plugin Store (search "FHDS")
2. Or download from [Releases](https://github.com/Sci-fi-Borg/fhds-in-decky-loader/releases) and extract to `~/homebrew/plugins/`

### In-Game Setup

Forza Horizon → Settings → HUD and Gameplay:
- Data Out: **ON**
- Data Out IP: `127.0.0.1`
- Data Out Port: `5300`

### Credits

- [Forza-Horizon-DualSense-Python](https://github.com/HamzaYslmn/Forza-Horizon-DualSense-Python) — Original DualSense HID and UDP implementation
- [decky-loader](https://github.com/SteamDeckHomebrew/decky-loader) — Plugin framework
- [decky-plugin-template](https://github.com/SteamDeckHomebrew/decky-plugin-template) — Plugin scaffold

### Notes

- USB connection recommended for initial testing; Bluetooth not fully validated
- Toggle the master switch off/on to reset trigger state if effects stop
- Do not run the desktop version of Forza-Horizon-DualSense-Python simultaneously — port conflict
- HID reports use `valid_flag0=0x0C` (triggers only) with a 200ms rate limit to preserve Steam rumble

### License

BSD-3-Clause © 2026 tau
