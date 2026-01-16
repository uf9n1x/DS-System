# GitHub 推送指南

## 步骤 1：在 GitHub 上创建仓库

1. 登录您的 GitHub 账户
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库名称（建议使用与项目相关的名称，如 "python-webtools"）
4. 选择仓库的可见性（公开或私有）
5. **不要勾选** "Initialize this repository with a README"，因为我们已经有了自己的文件
6. 点击 "Create repository"

## 步骤 2：获取远程仓库 URL

创建完成后，您将看到一个带有远程仓库 URL 的页面。URL 格式如下：
- HTTPS: `https://github.com/your-username/repository-name.git`
- SSH: `git@github.com:your-username/repository-name.git`

## 步骤 3：添加远程仓库地址

请将以下命令中的 `REMOTE_URL` 替换为您在步骤 2 中获取的 URL，然后在终端中执行：

```bash
git remote add origin REMOTE_URL
```

## 步骤 4：推送到 GitHub

执行以下命令将本地代码推送到 GitHub：

```bash
git push -u origin master
```

## 步骤 5：验证推送结果

在 GitHub 仓库页面刷新，您应该能看到所有已提交的文件。

## 可能遇到的问题及解决方案

1. **SSH 密钥问题**：如果使用 SSH URL 推送时遇到权限问题，请确保您的 SSH 密钥已添加到 GitHub 账户。
2. **分支名称问题**：如果 GitHub 默认分支名称为 `main` 而不是 `master`，请执行以下命令：
   ```bash
   git branch -M main
   git push -u origin main
   ```
3. **认证失败**：如果使用 HTTPS URL 推送时遇到认证失败，请尝试使用 SSH URL 或更新您的 GitHub 凭证。

## 后续操作建议

1. **创建 README.md 文件**：为项目添加详细的说明文档
2. **添加 LICENSE 文件**：选择合适的开源许可证
3. **创建 .env.example 文件**：提供环境变量示例，不包含敏感信息
4. **设置 CI/CD 工作流**：使用 GitHub Actions 自动化测试和部署
5. **添加分支保护规则**：保护主分支，防止未经审查的代码合并

## 注意事项

1. 确保 `.gitignore` 文件已正确配置，避免将敏感信息或不必要的文件推送到 GitHub
2. 不要在代码中硬编码密码、API 密钥等敏感信息
3. 定期更新依赖，确保项目安全
4. 遵循良好的提交规范，使用清晰、有意义的提交信息