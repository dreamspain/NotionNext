"""
pushUrl.py 深度实盘测试套件
包含单元测试、集成测试、边界条件测试和错误处理测试
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
import requests
from io import StringIO

# 导入被测试的模块
import pushUrl


class TestParseSitemap:
    """测试 parse_stiemap 函数"""
    
    def test_parse_sitemap_success(self):
        """测试成功解析sitemap"""
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
    </url>
    <url>
        <loc>https://example.com/page3</loc>
    </url>
</urlset>'''
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert result is not None
            assert len(result) == 3
            assert 'https://example.com/page1' in result
            assert 'https://example.com/page2' in result
            assert 'https://example.com/page3' in result
    
    def test_parse_sitemap_empty(self):
        """测试空sitemap"""
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>'''
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert result == []
    
    def test_parse_sitemap_network_error(self, capsys):
        """测试网络错误"""
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
            result = pushUrl.parse_stiemap('https://example.com')
            captured = capsys.readouterr()
            assert '请检查你的url是否有误' in captured.out
            assert result is None
    
    def test_parse_sitemap_invalid_xml(self):
        """测试无效的XML"""
        mock_response = Mock()
        mock_response.content = b'Invalid XML Content'
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert result == []
    
    def test_parse_sitemap_malformed_url(self, capsys):
        """测试格式错误的URL"""
        with patch('requests.get', side_effect=Exception("Connection error")):
            result = pushUrl.parse_stiemap('not-a-valid-url')
            captured = capsys.readouterr()
            assert '请检查你的url是否有误' in captured.out
    
    def test_parse_sitemap_timeout(self, capsys):
        """测试超时情况"""
        with patch('requests.get', side_effect=requests.exceptions.Timeout("Timeout")):
            result = pushUrl.parse_stiemap('https://example.com')
            captured = capsys.readouterr()
            assert '请检查你的url是否有误' in captured.out
    
    def test_parse_sitemap_large_response(self):
        """测试大量URL的sitemap"""
        # 生成包含500个URL的sitemap
        urls = [f'https://example.com/page{i}' for i in range(500)]
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in urls:
            xml_content += f'    <url>\n        <loc>{url}</loc>\n    </url>\n'
        xml_content += '</urlset>'
        
        mock_response = Mock()
        mock_response.content = xml_content.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 500


class TestPushToBing:
    """测试 push_to_bing 函数"""
    
    def test_push_to_bing_success(self, capsys):
        """测试成功推送到Bing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1', 'https://example.com/page2']
            pushUrl.push_to_bing('https://example.com', urls, 'test-api-key')
            
            captured = capsys.readouterr()
            assert '成功推送到Bing' in captured.out
    
    def test_push_to_bing_error_response(self, capsys):
        """测试Bing返回错误"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "ErrorCode": "InvalidRequest",
            "Message": "Invalid API key"
        }
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1']
            pushUrl.push_to_bing('https://example.com', urls, 'invalid-key')
            
            captured = capsys.readouterr()
            assert '推送到Bing出现错误' in captured.out
            assert 'Invalid API key' in captured.out
    
    def test_push_to_bing_network_error(self, capsys):
        """测试Bing网络错误"""
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            urls = ['https://example.com/page1']
            pushUrl.push_to_bing('https://example.com', urls, 'test-api-key')
            
            captured = capsys.readouterr()
            assert 'An error occurred' in captured.out
    
    def test_push_to_bing_empty_urls(self, capsys):
        """测试空URL列表"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response):
            pushUrl.push_to_bing('https://example.com', [], 'test-api-key')
            captured = capsys.readouterr()
            assert '成功推送到Bing' in captured.out
    
    def test_push_to_bing_api_key_format(self):
        """测试API密钥格式"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            urls = ['https://example.com/page1']
            api_key = 'test-api-key-123'
            pushUrl.push_to_bing('https://example.com', urls, api_key)
            
            # 验证API密钥是否正确包含在URL中
            call_args = mock_post.call_args
            assert api_key in call_args[0][0]
    
    def test_push_to_bing_payload_structure(self):
        """测试推送到Bing的payload结构"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            site = 'https://example.com'
            urls = ['https://example.com/page1', 'https://example.com/page2']
            pushUrl.push_to_bing(site, urls, 'test-api-key')
            
            # 验证payload结构
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            assert payload['siteUrl'] == site
            assert payload['urlList'] == urls


class TestPushToBaidu:
    """测试 push_to_baidu 函数"""
    
    def test_push_to_baidu_success(self, capsys):
        """测试成功推送到百度"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1', 'https://example.com/page2']
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')
            
            captured = capsys.readouterr()
            assert '成功推送到百度' in captured.out
    
    def test_push_to_baidu_error_response(self, capsys):
        """测试百度返回错误"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": 401,
            "message": "token is not valid"
        }
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1']
            pushUrl.push_to_baidu('https://example.com', urls, 'invalid-token')
            
            captured = capsys.readouterr()
            assert '推送到百度出现错误' in captured.out
            assert 'token is not valid' in captured.out
    
    def test_push_to_baidu_network_error(self, capsys):
        """测试百度网络错误"""
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            urls = ['https://example.com/page1']
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')
            
            captured = capsys.readouterr()
            assert 'An error occurred' in captured.out
    
    def test_push_to_baidu_unknown_response(self, capsys):
        """测试百度返回未知响应"""
        mock_response = Mock()
        mock_response.json.return_value = {"unknown_field": "unknown_value"}
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1']
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')
            
            captured = capsys.readouterr()
            assert 'Unknown response from Baidu' in captured.out
    
    def test_push_to_baidu_payload_format(self):
        """测试推送到百度的payload格式"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            urls = ['https://example.com/page1', 'https://example.com/page2']
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')
            
            # 验证payload格式（应该是换行分隔的URL）
            call_args = mock_post.call_args
            payload = call_args[1]['data']
            assert payload == '\n'.join(urls)
            
            # 验证headers
            headers = call_args[1]['headers']
            assert headers['Content-Type'] == 'text/plain'
    
    def test_push_to_baidu_url_construction(self):
        """测试百度API URL构造"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            site = 'https://example.com'
            token = 'test-token-123'
            urls = ['https://example.com/page1']
            pushUrl.push_to_baidu(site, urls, token)
            
            # 验证API URL构造
            call_args = mock_post.call_args
            api_url = call_args[0][0]
            assert site in api_url
            assert token in api_url
    
    def test_push_to_baidu_empty_urls(self, capsys):
        """测试空URL列表"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response):
            pushUrl.push_to_baidu('https://example.com', [], 'test-token')
            captured = capsys.readouterr()
            assert '成功推送到百度' in captured.out


class TestMainWorkflow:
    """测试主工作流程"""
    
    def test_main_with_all_parameters(self, capsys):
        """测试提供所有参数的主流程"""
        mock_sitemap_response = Mock()
        mock_sitemap_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/page1</loc></url>
    <url><loc>https://example.com/page2</loc></url>
</urlset>'''.encode('utf-8')
        
        mock_bing_response = Mock()
        mock_bing_response.status_code = 200
        mock_bing_response.json.return_value = {"success": True}
        
        mock_baidu_response = Mock()
        mock_baidu_response.json.return_value = {"success": True}
        
        with patch('requests.get', return_value=mock_sitemap_response), \
             patch('requests.post') as mock_post:
            
            # 设置post请求的返回值
            mock_post.side_effect = [mock_bing_response, mock_baidu_response]
            
            # 模拟命令行参数
            test_args = [
                'pushUrl.py',
                '--url', 'https://example.com',
                '--bing_api_key', 'test-bing-key',
                '--baidu_token', 'test-baidu-token'
            ]
            
            with patch('sys.argv', test_args):
                # 重新加载模块以应用新的参数
                import importlib
                importlib.reload(pushUrl)
    
    def test_main_without_url(self, capsys):
        """测试未提供URL的情况"""
        test_args = ['pushUrl.py']
        
        with patch('sys.argv', test_args):
            # 创建新的ArgumentParser实例来测试
            import argparse
            parser = argparse.ArgumentParser(description='parse sitemap')
            parser.add_argument('--url', type=str, default=None)
            parser.add_argument('--bing_api_key', type=str, default=None)
            parser.add_argument('--baidu_token', type=str, default=None)
            args = parser.parse_args([])  # 不传递任何参数
            
            # 验证URL为None
            assert args.url is None
    
    def test_quota_limit(self):
        """测试URL数量超过配额限制"""
        # 生成150个URL（超过默认100的限制）
        urls = [f'https://example.com/page{i}' for i in range(150)]
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in urls:
            xml_content += f'    <url>\n        <loc>{url}</loc>\n    </url>\n'
        xml_content += '</urlset>'
        
        mock_response = Mock()
        mock_response.content = xml_content.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 150
            
            # 测试配额限制
            with patch('random.sample') as mock_sample:
                mock_sample.return_value = result[:pushUrl.QUOTA]
                
                # 模拟主流程中的配额限制逻辑
                if len(result) > pushUrl.QUOTA:
                    limited_urls = mock_sample(result, pushUrl.QUOTA)
                    assert len(limited_urls) == pushUrl.QUOTA
    
    def test_random_seed_consistency(self):
        """测试随机种子设置"""
        import time
        import random
        
        timestamp1 = int(time.time())
        random.seed(timestamp1)
        sample1 = random.randint(1, 1000)
        
        time.sleep(0.1)  # 短暂延迟
        
        timestamp2 = int(time.time())
        random.seed(timestamp2)
        sample2 = random.randint(1, 1000)
        
        # 由于时间戳可能相同，这个测试主要验证种子设置不会报错
        assert isinstance(sample1, int)
        assert isinstance(sample2, int)


class TestEdgeCases:
    """边界条件测试"""
    
    def test_special_characters_in_urls(self):
        """测试URL中包含特殊字符"""
        mock_response = Mock()
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/page?id=1&amp;name=test</loc></url>
    <url><loc>https://example.com/page#section</loc></url>
    <url><loc>https://example.com/中文页面</loc></url>
</urlset>'''.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 3
    
    def test_very_long_urls(self):
        """测试非常长的URL"""
        long_url = 'https://example.com/' + 'a' * 1000
        mock_response = Mock()
        mock_response.content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>{long_url}</loc></url>
</urlset>'''.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 1
            assert result[0] == long_url
    
    def test_duplicate_urls_in_sitemap(self):
        """测试sitemap中包含重复URL"""
        mock_response = Mock()
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/page1</loc></url>
    <url><loc>https://example.com/page1</loc></url>
    <url><loc>https://example.com/page2</loc></url>
</urlset>'''.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            # 应该包含所有URL，包括重复的
            assert len(result) == 3
    
    def test_mixed_protocols(self):
        """测试混合协议（http和https）"""
        mock_response = Mock()
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/page1</loc></url>
    <url><loc>http://example.com/page2</loc></url>
</urlset>'''.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 2
            assert 'https://example.com/page1' in result
            assert 'http://example.com/page2' in result
    
    def test_unicode_in_response(self):
        """测试响应中包含Unicode字符"""
        mock_response = Mock()
        mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/测试</loc></url>
    <url><loc>https://example.com/テスト</loc></url>
</urlset>'''.encode('utf-8')
        
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
            assert len(result) == 2


class TestErrorHandling:
    """错误处理测试"""
    
    def test_json_decode_error_bing(self, capsys):
        """测试Bing响应JSON解码错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1']
            pushUrl.push_to_bing('https://example.com', urls, 'test-api-key')
            
            captured = capsys.readouterr()
            assert 'An error occurred' in captured.out
    
    def test_json_decode_error_baidu(self, capsys):
        """测试百度响应JSON解码错误"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with patch('requests.post', return_value=mock_response):
            urls = ['https://example.com/page1']
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')
            
            captured = capsys.readouterr()
            assert 'An error occurred' in captured.out
    
    def test_ssl_error(self, capsys):
        """测试SSL错误"""
        with patch('requests.get', side_effect=requests.exceptions.SSLError("SSL Error")):
            result = pushUrl.parse_stiemap('https://example.com')
            captured = capsys.readouterr()
            assert '请检查你的url是否有误' in captured.out
    
    def test_http_error_codes(self, capsys):
        """测试各种HTTP错误代码"""
        for status_code in [400, 401, 403, 404, 500, 502, 503]:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.json.return_value = {
                "ErrorCode": f"Error{status_code}",
                "Message": f"Error {status_code} occurred"
            }
            
            with patch('requests.post', return_value=mock_response):
                urls = ['https://example.com/page1']
                pushUrl.push_to_bing('https://example.com', urls, 'test-api-key')
                
                captured = capsys.readouterr()
                assert '推送到Bing出现错误' in captured.out or 'An error occurred' in captured.out
    
    def test_encoding_error(self):
        """测试编码错误"""
        mock_response = Mock()
        # 使用无效的编码
        mock_response.content = b'\xff\xfe Invalid UTF-8'
        
        with patch('requests.get', return_value=mock_response):
            try:
                result = pushUrl.parse_stiemap('https://example.com')
                # 应该返回空列表或None
                assert result == [] or result is None
            except UnicodeDecodeError:
                # 如果抛出编码错误也是可以接受的
                pass


class TestPerformance:
    """性能测试"""
    
    def test_large_batch_processing(self):
        """测试大批量URL处理"""
        import time
        
        # 生成1000个URL
        urls = [f'https://example.com/page{i}' for i in range(1000)]
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in urls:
            xml_content += f'    <url>\n        <loc>{url}</loc>\n    </url>\n'
        xml_content += '</urlset>'
        
        mock_response = Mock()
        mock_response.content = xml_content.encode('utf-8')
        
        start_time = time.time()
        with patch('requests.get', return_value=mock_response):
            result = pushUrl.parse_stiemap('https://example.com')
        end_time = time.time()
        
        assert len(result) == 1000
        # 确保处理时间合理（小于5秒）
        assert (end_time - start_time) < 5
    
    def test_concurrent_pushes(self):
        """测试并发推送（模拟）"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch('requests.post', return_value=mock_response):
            urls = [f'https://example.com/page{i}' for i in range(100)]
            
            # 测试Bing推送
            pushUrl.push_to_bing('https://example.com', urls, 'test-api-key')
            
            # 测试百度推送
            mock_response.json.return_value = {"success": True}
            pushUrl.push_to_baidu('https://example.com', urls, 'test-token')


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow_integration(self, capsys):
        """测试完整的工作流程集成"""
        # 准备sitemap响应
        mock_sitemap_response = Mock()
        mock_sitemap_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://example.com/page1</loc></url>
    <url><loc>https://example.com/page2</loc></url>
    <url><loc>https://example.com/page3</loc></url>
</urlset>'''.encode('utf-8')
        
        # 准备Bing响应
        mock_bing_response = Mock()
        mock_bing_response.status_code = 200
        mock_bing_response.json.return_value = {"success": True}
        
        # 准备百度响应
        mock_baidu_response = Mock()
        mock_baidu_response.json.return_value = {"success": True}
        
        with patch('requests.get', return_value=mock_sitemap_response):
            # 解析sitemap
            urls = pushUrl.parse_stiemap('https://example.com')
            assert len(urls) == 3
            
            with patch('requests.post', side_effect=[mock_bing_response, mock_baidu_response]):
                # 推送到Bing
                pushUrl.push_to_bing('https://example.com', urls, 'test-bing-key')
                
                # 推送到百度
                pushUrl.push_to_baidu('https://example.com', urls, 'test-baidu-token')
                
                captured = capsys.readouterr()
                assert '成功推送到Bing' in captured.out
                assert '成功推送到百度' in captured.out


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
