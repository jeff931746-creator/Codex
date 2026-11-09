# Windows 使用说明

## 启动工作台

1. 安装 Python 3：<https://www.python.org/downloads/windows/>，安装时勾选 `Add Python to PATH`。
2. 双击 `run-windows.bat`。首次运行会安装一个 HTTPS 证书依赖，然后打开 `http://127.0.0.1:8765/`。
3. 命令窗口必须保持打开；关闭窗口会停止本地服务，但不会删除数据库。

## 安装 Chrome 扩展

1. Chrome 地址栏打开 `chrome://extensions/`。
2. 开启右上角“开发者模式”。
3. 点击“加载已解压的扩展程序”，选择本目录中的 `chrome-extension` 文件夹。
4. 登录藏宝阁，打开全服搜索结果页，再通过扩展同步或启用定时采集。

## 数据位置

当前行情、角色详情、任务和估价记录均在 `data/market.sqlite3`。迁移数据时先关闭工作台命令窗口，再复制该文件。

登录状态、Cookie、Token 和账号密码不包含在压缩包中，需要在 Windows Chrome 重新登录。
