# 公开发布记录

本包发布到 [https://github.com/liuyongchao/itom-gbt28827-7-skill](https://github.com/liuyongchao/itom-gbt28827-7-skill)。技能目录为 [skills/itom-cost-gbt28827-7](skills/itom-cost-gbt28827-7/SKILL.md)。用户已明确授权与此前NESMA相同的公开发布。

- 原技能运行目录26文件及独立ZIP逐字节一致，包含完整14卡、6项资源、4项辅助reference、入口和编译清单。
- 保留使用说明、标准精华、测试报告、源Bundle和有用测试证据。没有上传原PDF、图像或OCR全文、原始候选工作稿、临时执行脚本及重复评分答案。
- 公开证据中的本机工作目录前缀已转换为相对路径；JSON为可移植格式重新序列化，原测试输入、数值、行为判断和失败记录没有改写。见audit/publication-preflight.json。
- 原来的文件交付版仍保存在本地。公开整理不改变已测执行规则，亦不解除N01—N06。
- 远程下载、临时目录安装及计算器实测：待完成后在此更新。

复现脚本检查：在仓库根目录运行 `python tests/calculator/run_regression.py`。计算器仅使用Python标准库；重新编译source-bundle才依赖cangjie-skill/PyYAML。
