# 汉字拼音批量注音工具

## 项目简介
本项目用于自动为汉字文本批量添加拼音（拼音在汉字上方，HTML ruby 格式），支持网页可视化、HTML/Word文档导出，并可打包为exe独立运行。

## 主要功能
- 自动为汉字添加拼音（拼音在上方，ruby标签）
- 生成带拼音的HTML文件
- 一键下载带拼音的Word文档（需本机安装 Microsoft Word 或 WPS Office）
- 可打包为exe，无需Python环境

## 使用方法
1. 运行 `app.py` 或打包后的 `app.exe`
   - ⚠️ 打包后的 exe 运行后，需要手动在浏览器打开 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 进行操作。
2. 浏览器访问 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
3. 在网页输入或粘贴汉字文本
4. 点击“生成拼音”可在线预览拼音效果
5. 点击“生成HTML文档”可下载带拼音的HTML文件
6. 点击“生成Word文档”可下载docx文件（需本机安装Word/WPS，且仅在Windows下支持自动化，不好用，还是建议手动转换）

## 打包说明
- 使用 PyInstaller 打包：
  ```bash
  D:/python/python.exe -m PyInstaller app.py --add-data "templates;templates" --hidden-import=win32com --hidden-import=pythoncom --onefile
  ```
- 打包后 exe 可直接运行，无需 Python 环境

## 依赖环境
- Python 3.6 及以上
- Flask
- pypinyin
- python-docx
- pywin32
- Windows 系统，需本机安装 Microsoft Word 或 WPS Office

## 注意事项
- 生成的 docx 文件，若需“拼音在上方”效果，**请用 WPS Office 手动打开生成的 HTML 文件，再另存为 docx 格式。**
- 自动化转换（Word/WPS）有时与手动操作效果不同，手动另存为可获得最佳拼音排版。

---
如有问题请联系开发者。 
