# pushUrl.py 测试指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r test_requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
python3 -m pytest test_pushUrl.py -v

# 运行测试并生成覆盖率报告
python3 -m pytest test_pushUrl.py -v --cov=pushUrl --cov-report=term-missing --cov-report=html

# 运行特定测试类
python3 -m pytest test_pushUrl.py::TestParseSitemap -v

# 运行特定测试
python3 -m pytest test_pushUrl.py::TestParseSitemap::test_parse_sitemap_success -v
```

### 3. 查看覆盖率报告

测试运行后，会在 `htmlcov/` 目录生成HTML格式的覆盖率报告：

```bash
# 打开覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 测试分类

### 按功能分类运行

```bash
# 单元测试 - parse_stiemap
python3 -m pytest test_pushUrl.py::TestParseSitemap -v

# 单元测试 - push_to_bing
python3 -m pytest test_pushUrl.py::TestPushToBing -v

# 单元测试 - push_to_baidu
python3 -m pytest test_pushUrl.py::TestPushToBaidu -v

# 边界条件测试
python3 -m pytest test_pushUrl.py::TestEdgeCases -v

# 错误处理测试
python3 -m pytest test_pushUrl.py::TestErrorHandling -v

# 性能测试
python3 -m pytest test_pushUrl.py::TestPerformance -v

# 集成测试
python3 -m pytest test_pushUrl.py::TestIntegration -v
```

## 测试选项

```bash
# 详细输出
python3 -m pytest test_pushUrl.py -v

# 显示打印输出
python3 -m pytest test_pushUrl.py -v -s

# 只运行失败的测试
python3 -m pytest test_pushUrl.py --lf

# 停止在第一个失败
python3 -m pytest test_pushUrl.py -x

# 并行运行测试（需要安装pytest-xdist）
pip install pytest-xdist
python3 -m pytest test_pushUrl.py -n auto
```

## 测试文件结构

```
.
├── pushUrl.py              # 被测试的源文件
├── test_pushUrl.py         # 测试文件
├── pytest.ini              # pytest配置
├── test_requirements.txt   # 测试依赖
├── TEST_REPORT.md          # 测试报告
├── TESTING.md              # 本文件
└── htmlcov/                # 覆盖率报告目录（运行后生成）
```

## 依赖说明

- **pytest**: 测试框架
- **pytest-cov**: 覆盖率插件
- **pytest-mock**: Mock对象插件
- **requests-mock**: HTTP请求Mock
- **coverage**: 覆盖率工具

## 测试覆盖内容

✅ **功能测试**
- sitemap解析
- Bing推送
- 百度推送

✅ **异常处理**
- 网络错误
- 超时
- SSL错误
- JSON解析错误
- HTTP错误响应

✅ **边界条件**
- 空数据
- 大量数据
- 特殊字符
- Unicode字符

✅ **性能测试**
- 大批量处理
- 并发推送

## 持续集成

可以将测试集成到CI/CD流程中：

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r test_requirements.txt
    
    - name: Run tests
      run: |
        python3 -m pytest test_pushUrl.py -v --cov=pushUrl --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 常见问题

### Q: 如何添加新的测试用例？

在 `test_pushUrl.py` 中添加新的测试方法：

```python
def test_your_new_test(self):
    """测试描述"""
    # 测试代码
    assert True
```

### Q: 如何Mock外部API调用？

使用 `unittest.mock.patch`:

```python
with patch('requests.get', return_value=mock_response):
    result = pushUrl.parse_stiemap('https://example.com')
```

### Q: 测试失败时如何调试？

```bash
# 显示详细的错误信息
python3 -m pytest test_pushUrl.py -vv

# 进入调试器
python3 -m pytest test_pushUrl.py --pdb
```

## 贡献指南

添加新功能时，请：
1. 编写相应的测试用例
2. 确保所有测试通过
3. 保持代码覆盖率 ≥ 70%
4. 更新测试文档

## 联系方式

如有问题，请提交Issue或Pull Request。
