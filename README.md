# 中国人民大学形势与政策半自动化抢课脚本

本项目基于https://github.com/panjd123/RUC-CourseSelectionTool

适用：自动化抢形势与政策讲座和研讨课，支持选择讲座或研讨，支持抢课速度调整

## Simple Usage

```bash
pip install ruclogin
ruclogin                # only need to run once
python main.py
```


- 关于 ruclogin 这个包，你可以查看 [ruclogin](https://github.com/panjd123/ruclogin) 的具体文档。  
- 注意,需要安装适合自己浏览器的 webdriver 并在 ruclogin 时配置相应路径
- 抢课结果将会打印到本地的 result.txt 文件中，同时也会在控制台输出
- 可通过setting.json文件调整抢课速度和选择讲座或研讨课


