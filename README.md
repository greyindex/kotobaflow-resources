# KotobaFlow 学习资源

[网站](https://kotobaflow.lol) · [Web 源码](https://github.com/greyindex/kotobaflow-web) · [Android 源码](https://github.com/greyindex/kotobaflow-android) · [Android 0.4.2 下载](https://download.kotobaflow.lol/android/kotobaflow-0.4.2-public-8d85707591da.apk)

这里保存 KotobaFlow 的数据母版、处理结果与音图资源。词表序列和语法索引基于公开资料，本项目的课程、释义扩展、元数据、格式化与内容处理由维护者和 AI agent 协作完成。项目自有资源以 **CC0 1.0** 提供，可以自由使用、修改、再分发与商用，无需单独申请。来自第三方的内容继续保留原署名和许可，见 [第三方声明](THIRD_PARTY_NOTICES.md)。

资源或版权问题请联系 [wsxedcrfzh@gmail.com](mailto:wsxedcrfzh@gmail.com)，附上相关文件路径和来源信息。

## 内容

- 12,528 条主词表及词性、语域、语体、及物性等元数据，保留完整母版与运行分片。
- 739 条语法详情、索引、辅助课文和运行分片。
- KotobaFlow 四册、77 课、6,518 条课程词汇，含正文、词块、词汇补充审核与构建母版。
- 76 张单元插图、假名点读、词汇配音、课程朗读与会话。
- 35,491 条实际使用的例句配音，保存在 80 个按字节范围播放的 OGG 包中；当前公开数据不再引用的 6,336 条片段不打包。
- 古典拓展阅读六部、152 个分部，原文、现代日语／中文 AI 试译与两段完整朗读；作品索引保留来源与质量说明。

**新编日语的全部专用资源均不提供**：不含其正文、课程目录、教材词表、语法标注、插图、朗读、会话、旧修订台账和私有 Git 历史。历史词音目录中仅保留 KotobaFlow 直接引用的 4,791 条通用孤立单词配音，这是维护者明确确认的共享资源；不包含旧教材词表或其余专用词音。

## 两个资源版本

| 版本 | 对应程序 | 用途 |
| --- | --- | --- |
| `web-2026-10-31` | Web `cef1c7f` | 当前公开网页的数据与母版；例句包按公开内容精简 |
| `android-0.4.2` | 外层 `5b39065`、网页 `c704ecf` | 已发行 Android 0.4.2 的包内内容及其对应母版 |

JSON、JSONL 和逐文件清单位于 `profiles/<版本>/files/`，保留应用的原相对路径。音频与插图去重后放在同仓库的 [Release 媒体包](https://github.com/greyindex/kotobaflow-resources/releases/download/resources-2026-10-31/kotobaflow-media-2026-10-31.zip)（约 796 MB）；不需要 Git LFS。两个版本共同使用一个媒体包，安装器按清单恢复对应路径并验证大小与 SHA-256。

媒体包 SHA-256：`0d419eddd4ada091a39d0ef7bac51a73882e06e9136421f4d26514382e3df608`。完整描述见 [media-release.json](media-release.json)。

## 安装到源码目录

需要 Python 3.12+。先克隆本资源仓库和对应程序仓库，再在资源仓库执行：

```powershell
# Web：将资源放入网页源码根目录
python install_resources.py --profile web-2026-10-31 --target C:\path\to\kotobaflow-web

# Android：将资源放入独立网页源码子目录
python install_resources.py --profile android-0.4.2 --target C:\path\to\kotobaflow-android\web-source-backup
```

安装器默认下载并缓存媒体包；已有文件时可加 `--media-archive C:\path\to\kotobaflow-media-2026-10-31.zip`，只安装 JSON 等数据可加 `--metadata-only`。`--verify-only` 仅检查资源，不修改目标。相同文件会跳过；目标已有不同版本时停止，建议安装到新克隆的源码目录。

资源不会复制进源码仓库的 Git 历史，两个程序仓库会忽略这些本机依赖。公开源码默认只提供 KotobaFlow 四册；普通启动与公开版组包不需要新编教材。不可公开文本的检查边界只保存 SHA-256 指纹，不包含课文原文。

母版和运行闭包均已保留，便于研究数据清理、标注、身份关联、分片、元数据与音频区间处理。原开发仓库针对八册数据的全量维护检查仍含新编专用步骤；本资源仓库没有用空白教材或伪造资源绕过它们。

## 校验

```powershell
python -m unittest test_install_resources.py
python install_resources.py --profile web-2026-10-31 --verify-only --media-archive C:\path\to\kotobaflow-media-2026-10-31.zip
python install_resources.py --profile android-0.4.2 --verify-only --media-archive C:\path\to\kotobaflow-media-2026-10-31.zip
```

许可范围见 [LICENSE](LICENSE) 与 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。资源许可不自动改变两个程序仓库的源码许可。
