#!/usr/bin/env python3
"""
验证中间件 - 强制所有数据处理经过验证
最高优先级：坚决与AI幻觉作斗争
"""
import json
import requests
from datetime import datetime
from functools import wraps

class VerificationMiddleware:
    """验证中间件 - 所有数据必须经过验证"""
    
    def __init__(self):
        self.validation_log = []
        self.strict_mode = True  # 严格模式，不通过验证的数据将被拒绝
    
    def validate_required(self, func):
        """装饰器：强制验证装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 强制验证
            if isinstance(result, dict):
                validation_result = self.verify_data(result)
                
                if not validation_result['passed']:
                    if self.strict_mode:
                        raise ValueError(
                            f"数据验证失败: {validation_result['errors']}\n"
                            f"数据: {json.dumps(result, ensure_ascii=False)[:200]}"
                        )
                    else:
                        # 标记为待验证
                        result['_verification'] = {
                            'status': 'PENDING',
                            'errors': validation_result['errors'],
                            'timestamp': datetime.now().isoformat()
                        }
                else:
                    # 标记为已验证
                    result['_verification'] = {
                        'status': 'VERIFIED',
                        'level': validation_result['level'],
                        'timestamp': datetime.now().isoformat()
                    }
            
            return result
        return wrapper
    
    def verify_data(self, data):
        """验证数据"""
        errors = []
        warnings = []
        
        # 1. 检查AI幻觉迹象
        hallucination_checks = self._check_hallucination(data)
        errors.extend(hallucination_checks['errors'])
        warnings.extend(hallucination_checks['warnings'])
        
        # 2. 检查必填字段
        if 'name' in data or 'title' in data:
            field_checks = self._check_required_fields(data)
            errors.extend(field_checks['errors'])
            warnings.extend(field_checks['warnings'])
        
        # 3. 检查来源
        source_checks = self._check_sources(data)
        errors.extend(source_checks['errors'])
        warnings.extend(source_checks['warnings'])
        
        # 确定验证级别
        if errors:
            level = 'REJECTED'
        elif warnings:
            level = 'CONDITIONAL'
        else:
            level = 'A'
        
        return {
            'passed': len(errors) == 0,
            'level': level,
            'errors': errors,
            'warnings': warnings
        }
    
    def _check_hallucination(self, data):
        """检查AI幻觉迹象"""
        errors = []
        warnings = []
        
        # 检查模板化名称
        name = data.get('name', data.get('title', ''))
        template_patterns = [
            '文创品牌', '文旅综合体', '非遗活化', '数字文创', '文创街区',
            '{city}', '{region}', '某', '示例', '测试'
        ]
        
        for pattern in template_patterns:
            if pattern in name:
                errors.append(f"疑似AI生成/模板数据: 包含'{pattern}'")
        
        # 检查模糊表述
        vague_words = ['可能', '大概', '也许', '估计', '应该', '据说']
        data_str = json.dumps(data, ensure_ascii=False)
        for word in vague_words:
            if word in data_str:
                warnings.append(f"包含模糊表述: '{word}'")
        
        # 检查是否缺少具体数据
        if 'kpi' in data:
            kpi = data['kpi']
            if isinstance(kpi, dict):
                for key, value in kpi.items():
                    if isinstance(value, str) and ('万' in value or '亿' in value):
                        if '来源' not in data_str and 'source' not in data_str:
                            warnings.append(f"KPI数据'{key}'缺少来源标注")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _check_required_fields(self, data):
        """检查必填字段"""
        errors = []
        warnings = []
        
        # 品牌案例必填字段
        if 'category' in data:
            required = ['name', 'region', 'category']
            for field in required:
                if not data.get(field):
                    errors.append(f"缺少必填字段: {field}")
        
        # 政策文件必填字段
        if 'title' in data and '政策' in data.get('category', ''):
            if not data.get('doc_number') and not data.get('source_url'):
                errors.append("政策文件必须提供文号或来源链接")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _check_sources(self, data):
        """检查数据来源"""
        errors = []
        warnings = []
        
        # 检查是否有来源信息
        has_source = any([
            data.get('source_url'),
            data.get('sources'),
            data.get('type') == 'real_brand',
            data.get('verified')
        ])
        
        if not has_source:
            warnings.append("缺少数据来源信息")
        
        # 检查来源URL格式
        source_url = data.get('source_url', '')
        if source_url:
            if not source_url.startswith(('http://', 'https://')):
                errors.append("来源URL格式错误")
        
        return {'errors': errors, 'warnings': warnings}


# 全局验证中间件实例
verification_middleware = VerificationMiddleware()


def require_verification(func):
    """快捷装饰器"""
    return verification_middleware.validate_required(func)


# 验证报告生成
class VerificationReporter:
    """验证报告生成器"""
    
    def __init__(self):
        self.reports = []
    
    def add_report(self, data, result):
        """添加验证报告"""
        self.reports.append({
            'timestamp': datetime.now().isoformat(),
            'data_summary': str(data)[:100],
            'result': result
        })
    
    def generate_summary(self):
        """生成汇总报告"""
        total = len(self.reports)
        passed = sum(1 for r in self.reports if r['result']['passed'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': f"{passed/total*100:.1f}%" if total > 0 else "0%",
            'timestamp': datetime.now().isoformat()
        }


# 使用示例
if __name__ == '__main__':
    print("=" * 70)
    print("🔒 验证中间件 - 最高优先级")
    print("   坚决与AI幻觉作斗争")
    print("=" * 70)
    print()
    
    # 测试数据
    test_cases = [
        {
            'name': '故宫淘宝',
            'region': '北京市',
            'category': '博物馆文创',
            'type': 'real_brand',
            'source_url': 'https://gugong.tmall.com'
        },
        {
            'name': '北京文创品牌',  # 模板数据
            'region': '北京市',
            'category': '文创IP'
        },
        {
            'name': '泡泡玛特',
            'region': '北京市',
            'category': '潮玩盲盒',
            'kpi': {'revenue': '10亿+'},  # 缺少来源
            'type': 'real_brand'
        }
    ]
    
    middleware = VerificationMiddleware()
    middleware.strict_mode = False  # 测试模式，不抛出异常
    
    print("验证测试:")
    for case in test_cases:
        result = middleware.verify_data(case)
        status = "✅ 通过" if result['passed'] else "❌ 失败"
        print(f"\n{status} {case.get('name', '')}")
        if result['errors']:
            print(f"  错误: {result['errors']}")
        if result['warnings']:
            print(f"  警告: {result['warnings']}")
