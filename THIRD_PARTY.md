# 工作流依赖来源

入口 Skill 按名称复用以下三个工作流。可选依赖归档保持原字节，安装器校验 SHA-256：

`f9a2602dccd2350849c26899558fa68b45bad54e13e6b31b848132eaac189897`

- build-from-requirements
- change-existing-software
- rebuild-from-reference

归档中的 manifest.json 记录文件哈希，upstream.json 记录引用资源来源。参考材料附带的许可证保留在各工作流的 references 目录。

引用资源包括 Spec Kit v1.3.2 的规格模板、Superpowers v7.0.2 的完成前验证材料，以及 OpenSpec 的探索材料。对应原始 URL 与哈希以归档内 upstream.json 为准。

方法设计参考 [OpenAI harness-author 示例](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) 与 [Codex Skills 文档](https://learn.chatgpt.com/docs/build-skills)。
