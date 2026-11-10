# engineering-project-bootstrap

Codex + DSH 的工程项目启动 Skill，组合三个已有开发工作流。仓库包含入口、可选工作流依赖、安装检查和回退工具、隔离复验脚本。

克隆仓库后进入目录，或从 Releases 下载 ZIP 并解压。私有仓库需使用获准的 GitHub 账号。

```sh
git clone https://github.com/GongZhengxin/engineering-project-bootstrap.git
cd engineering-project-bootstrap
```

在目标项目根目录打开 Codex，说：

> 接管这个项目，按我的标准软件工程工作流准备开发。

要依据某个外观重建，再指定那张图、录屏或参考界面。Codex 会找现有源码、适用的目录规范、依赖及锁、原任务源、构建与测试入口，运行可安全隔离的最小基线。你收到的是路由理由、可复跑命令、已有改动、缺口和下一项验法。空目录没有需求时，先补一项用户动作与成功结果。

## 安装一次

从交付包根运行，Python 3.9+。Windows 可用 `python` 或 `py -3`，Linux 通常用 `python3`。先查当前 Codex 会话的 Skills 列表，只选一个用户级目录。以下演示使用 `~/.codex/skills`；也可使用官方文档列出的 `~/.agents/skills`。自定义 CODEX_HOME 时用实际已发现的目录。引号中的 `~` 由脚本展开。不要在两个根重复装同名 Skill。[OpenAI Skills 文档](https://learn.chatgpt.com/docs/build-skills)

```sh
python skill_files.py plan --skills-dir "~/.codex/skills" --with-workflows
```

`ADD` 列出将新增的文件，`REUSE` 表示逐文件字节相同，`CONFLICT` 表示应先审阅两版。此命令只读。

确认差异并获得该工位的安装授权后，再运行以下两条。把回执放在目录外，选一个尚不存在的文件名。`install` 遇冲突会停止，保留已有版本；`check` 会核对文件集合与内容。若三个工作流已在另一发现根中就绪，省略 `--with-workflows`，只装入口 Skill。

```sh
python skill_files.py install --skills-dir "~/.codex/skills" --with-workflows --record install-01.json
python skill_files.py check --skills-dir "~/.codex/skills" --with-workflows
```

在 Codex 的 Skill 选择器核对四个名称，然后在项目中使用上面的一句话。若目录有新文件而选择器尚未刷新，重启 Codex 再查；也可以显式输入 `$engineering-project-bootstrap`。三个工程工作流沿用已有发布包，入口 Skill 按名称加载。安装器不会设置模型、联网、安装包管理器或修改目标项目。

回退时带同一回执、目录和选项。工具先逐文件核对，随后将本次新增目录移入回执旁的 `install-01.json.disabled/`。本次复用的 Skill 保留；遇安装后变更时停下供人工核对。卸载后可用选择器确认。

```sh
python skill_files.py rollback --skills-dir "~/.codex/skills" --with-workflows --record install-01.json
```

## 能直接继承什么

| 归属 | 保存内容 | 换项目或机器时的动作 |
|---|---|---|
| 用户级 Skills | 启动发现、三类任务路由、保留脏工作树、定向验证、同版接收、异常接续方法 | 安装一次。非空仓库新增未定义能力可组合需求与增量流程；参考优先级由本次要求决定 |
| 项目 Git 与原任务系统 | 仓库入口及子目录规则、可执行构建与测试脚本、锁文件、CI、验收样例、数据或图像契约及出处 | 找项目已有权威来源。逐项目确认执行目录、依赖版本、用户场景、异常、可写范围、验收人。已有外部看板只链接；按需给缺入口的项目提最小差异 |
| 本机 DSH ACP 与授权控制器 | 可执行文件、实际 Profile、角色及工具权限、模型/推理映射、provider、凭据引用、会话存储、记账与截止 | 每台机器配置一次。每项实际委托绑定项目、原任务、候选、写域及材料许可。密钥、会话库和持权资料留在本机 |

Codex 执行本地检查、设计判断、集成和签收。DeepSeek 的普通开发角色只取得隔离候选所需的写域；Gemini 的独立视觉角色取得批准的图像和只读权限。两者使用项目批准的 DSH 路线。不可用时，接管仍能给出本地基线和该角色的具体缺项。

## 在新机器开通 DSH

1. 先验证独立于 DSH 的本地接手。核操作系统/架构、实际 shell、Git、项目运行时和包管理器版本，按项目锁文件选择环境。确认当前工作目录、大小写、空格或非 ASCII 路径、行尾、可执行位及临时输出权限。Windows 的盘符、PowerShell、Job Object 与 Linux 挂载点、shell、进程组或 cgroup 分别验证。用目标系统的锁定构建和测试命令复跑，核输入与工作树。
2. 需要模型协作时，在新机通过已批准的安装渠道取得 DSH，确认对应平台有可运行的 ACP 入口、协议能力和角色 Profile。将 DSH 可执行路径、工作区、临时目录、开发和视觉 Profile、路由标识及凭据引用设为本机参数。通过本机受支持方式登录或注入凭据。各项目声明可派角色、可出站内容和验收；真实授权由受信控制器核实。
3. 在一次获准的微型工单上验通。用本地哨兵实测开发写域、审阅只读及越界拒绝；比对实际出站模型、effort 与返回值。DeepSeek 交候选与红绿测试；Gemini 取得授权图像的字节摘要和可核查的具体观察。Codex 独立核同版结果。
4. 核上游前计数、绝对截止、内部重试计数、取消及所属子进程退出。用同任务、角色、原会话、候选、额度恢复一次，再试一次预算耗尽或错目录的拒绝。把结果留在该工位。请求数、时间、token、金额分别记录实际能执行的限制。Linux 和新 provider 均需实际测试，缺保护时相应角色保持待准入。

## 复验本包

```sh
python -B -X utf8 checks/trial.py smoke
python -B -X utf8 checks/catalog.py
```

第一条使用 Git、Node 22+ 和 Python 创建临时的空目录及已有仓库，执行真实构建、测试和安装回退；第二条需要提供 `codex debug prompt-input` 的 Codex CLI，使用临时 CODEX_HOME 验证可发现性。两者都在包内新建临时目录，需解压到可写位置。要手动重放三种接手，先用 `checks/trial.py prepare --trial replay-01` 建夹具，再按[复验说明](VALIDATION.md)的三条输入操作，最后运行 `checks/trial.py check --trial replay-01`。该试验目录可保留复查。

本方法沿用官方示例中的只读发现、权威来源定位和按规模选择最小交付物；Skill 描述承担触发，细节在选择后加载。[OpenAI harness-author 工作流](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) · [Codex Skills](https://learn.chatgpt.com/docs/build-skills)
