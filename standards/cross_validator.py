#!/usr/bin/env python3
"""
交叉验证工具
验证数据是否有多个独立来源支持
"""
import requests
import json
from urllib.parse import urlparse

class CrossValidator:
    """交叉验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'brand': {
                'min_sources': 2,
                'required_source_types': ['official', 'media'],
                'forbidden_patterns': ['文创品牌', '文旅综合体', '非遗活化']
            },
            'product': {
                'min_sources': 2,
                'required_source_types': ['ecommerce', 'official'],
                'image_validation': True
            },
            'policy': {
                'min_sources': 1,
                'required_fields': ['doc_number', 'source_url'],
                'source_priority': ['gov.cn', 'gov.cn']
            }
        }
    
    def check_source_independence(self, sources):
        """检查来源是否独立"""
        domains = []
        for source in sources:
            url = source.get('url', '')
            domain = urlparse(url).netloc
            domains.append(domain)
        
        # 检查是否有重复域名
        unique_domains = set(domains)
        
        return {
            'is_independent': len(unique_domains) >= 2,
            'unique_domains': list(unique_domains),
            'total_sources': len(sources)
        }
    
    def check_source_credibility(self, url):
        """检查来源可信度"""
        domain = urlparse(url).netloc.lower()
        
        # 可信度评级
        credibility_levels = {
            'A': [
                'tmall.com', 'jd.com',  # 电商官方
                'gov.cn',  # 政府网站
            ],
            'B': [
                '36kr.com', 'huxiu.com',  # 科技媒体
                'sina.com.cn', 'qq.com',  # 门户
            ],
            'C': [
                'xiaohongshu.com', 'douyin.com',  # 社交
                'zhihu.com',  # 问答
            ]
        }
        
        for level, domains in credibility_levels.items():
            if any(d in domain for d in domains):
                return level
        
        return 'D'  # 未知来源
    
    def validate_brand_cross(self, brand_name, sources):
        """品牌交叉验证"""
        result = {
            'brand': brand_name,
            'is_valid': False,
            'checks': {}
        }
        
        # 1. 检查来源数量
        result['checks']['source_count'] = len(sources) >= 2
        
        # 2. 检查来源独立性
        independence = self.check_source_independence(sources)
        result['checks']['independence'] = independence['is_independent']
        result['domain_analysis'] = independence
        
        # 3. 检查来源可信度
        credibility_scores = []
        for source in sources:
            score = self.check_source_credibility(source.get('url', ''))
            credibility_scores.append(score)
        
        result['checks']['has_credible_source'] = any(s in ['A', 'B'] for s in credibility_scores)
        result['credibility_scores'] = credibility_scores
        
        # 4. 检查是否为模板
        template_patterns = self.validation_rules['brand']['forbidden_patterns']
        result['checks']['not_template'] = not any(p in brand_name for p in template_patterns)
        
        # 综合判断
        result['is_valid'] = all(result['checks'].values())
        
        return result
    
    def validate_policy_cross(self, policy_data):
        """政策交叉验证"""
        result = {
            'title': policy_data.get('title', '')[:40],
            'is_valid': False,
            'checks': {}
        }
        
        # 1. 检查文号
        doc_number = policy_data.get('doc_number', '')
        result['checks']['has_doc_number'] = bool(doc_number)
        
        # 2. 检查来源链接
        source_url = policy_data.get('source_url', '')
        result['checks']['has_source_url'] = bool(source_url)
        
        # 3. 检查来源是否为政府网站
        if source_url:
            is_gov = 'gov.cn' in source_url.lower()
            result['checks']['is_gov_source'] = is_gov
        else:
            result['checks']['is_gov_source'] = False
        
        # 4. 检查标题是否为模板
        template_patterns = ['关于促进', '关于加快', '关于推动', '关于支持']
        title = policy_data.get('title', '')
        result['checks']['not_template'] = not all(p in title for p in template_patterns[:2])
        
        # 综合判断
        # 政策至少需要有文号或政府来源
        result['is_valid'] = result['checks']['has_doc_number'] or result['checks']['is_gov_source']
        
        return result


def generate_validation_report(items, data_type='brand'):
    """生成验证报告"""
    validator = CrossValidator()
    
    report = {
        'data_type': data_type,
        'total': len(items),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    for item in items:
        if data_type == 'brand':
            result = validator.validate_brand_cross(
                item.get('name', ''),
                item.get('sources', [])
            )
        elif data_type == 'policy':
            result = validator.validate_policy_cross(item)
        else:
            continue
        
        if result['is_valid']:
            report['passed'] += 1
        else:
            report['failed'] += 1
        
        report['details'].append(result)
    
    return report


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("🔍 交叉验证工具")
    print("=" * 70)
    print()
    
    # 示例：验证品牌
    test_brands = [
        {
            'name': '故宫淘宝',
            'sources': [
                {'url': 'https://gugong.tmall.com', 'type': 'ecommerce'},
                {'url': 'https://www.dpm.org.cn', 'type': 'official'}
            ]
        },
        {
            'name': '北京文创品牌',
            'sources': [
                {'url': 'https://example.com/1', 'type': 'unknown'},
            ]
        }
    ]
    
    validator = CrossValidator()
    
    print("品牌验证示例:")
    for brand in test_brands:
        result = validator.validate_brand_cross(brand['name'], brand['sources'])
        status = "✅ 通过" if result['is_valid'] else "❌ 失败"
        print(f"\n{status} {brand['name']}")
        print(f"  检查项: {result['checks']}")
