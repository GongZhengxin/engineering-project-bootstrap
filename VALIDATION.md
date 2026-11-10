# 复验

包使用 Python 标准库。运行安装/回退试验还需 Git 与 Node 22+；目录发现试验需支持 `codex debug prompt-input` 的 Codex CLI。

```sh
python -B -X utf8 checks/trial.py smoke
python -B -X utf8 checks/catalog.py
```

手动重放时先创建夹具：

```sh
python -B -X utf8 checks/trial.py prepare --trial replay-01
```

在生成的 blank 目录输入“接管这个项目，按我的标准软件工程工作流准备开发。”，应选择 build-from-requirements，记录缺少需求与可运行入口。

在 ledger 目录输入同一句话，应选择 change-existing-software，从根及 web 的约定追到任务、组件脚本与用例。构建和测试从 web 目录执行。目录中存在的参考图只有在用户明确指定“以 samples/card.svg 为界面参考”时才触发 rebuild-from-reference，并组合增量流程。静态参考的交互仍需实现后验收。

完成后核文件、HEAD、索引和状态：

```sh
python -B -X utf8 checks/trial.py check --trial replay-01
```

发布前在 Windows 使用 Python 3.12.3、Git 2.44.0、Node v24.22.1 运行。本地测试覆盖空项目、含已暂存/未暂存/未跟踪内容的 Git 项目、实际构建及测试、四个 Skill 的安装与复用、冲突拒绝和按回执回退。Codex CLI 目录试验核对临时安装四个 Skill 后可见、回退后消失。

此前独立 Codex 接手演练已覆盖上述三种输入。角色正反例验证了准备阶段本地检查、获准后的 DeepSeek 隔离实现与 Gemini 只读审阅，以及额度耗尽后的停止判断。新机实际 DSH 调用、权限和预算保护需在当地入口实测。Linux 运行兼容性仍待目标机确认。
