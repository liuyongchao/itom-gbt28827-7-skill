# 公开发布记录

本包发布到 [https://github.com/liuyongchao/itom-gbt28827-7-skill](https://github.com/liuyongchao/itom-gbt28827-7-skill)。技能目录为 [skills/itom-cost-gbt28827-7](skills/itom-cost-gbt28827-7/SKILL.md)。用户已明确授权与此前NESMA相同的公开发布。

- 原技能运行目录26文件及独立ZIP逐字节一致，包含完整14卡、6项资源、4项辅助reference、入口和编译清单。
- 保留使用说明、标准精华、测试报告、源Bundle和有用测试证据。没有上传原PDF、图像或OCR全文、原始候选工作稿、临时执行脚本及重复评分答案。
- 公开证据中的本机工作目录前缀已转换为相对路径；JSON为可移植格式重新序列化，原测试输入、数值、行为判断和失败记录没有改写。见audit/publication-preflight.json。
- 原来的文件交付版仍保存在本地。公开整理不改变已测执行规则，亦不解除N01—N06。
- 已匿名下载公开文档和ZIP，使用skill-installer从技能URL安装到临时工作目录；26个文件哈希全部与已测版本一致。完整费用示例得到12088元；缺少其他费用时保留partial及11088元已知小计，没有虚构总额。见[远程安装验证](audit/remote-install-verification.json)。
- 验证时间：2026-10-08T14:54:02.641730+00:00。没有安装到发布者的实际用户技能目录。

复现脚本检查：在仓库根目录运行 `python tests/calculator/run_regression.py`。计算器仅使用Python标准库；重新编译source-bundle才依赖cangjie-skill/PyYAML。
