#!/usr/bin/env python3
"""
文创产品分析师 - 模板生成器
根据模板和数据自动生成分析报告页面
"""

import re
import json
import base64
import requests
from datetime import datetime

class WCFXReportGenerator:
    """文创分析师报告生成器"""
    
    def __init__(self, template_path='wcfx-template.html'):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def generate(self, data, output_path=None):
        """
        生成报告
        
        Args:
            data: 产品数据字典
            output_path: 输出文件路径
        
        Returns:
            生成的HTML字符串
        """
        html = self.template
        
        # 替换所有 {{变量}}
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            html = html.replace(placeholder, str(value))
        
        # 保存文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'✅ 报告已生成: {output_path}')
        
        return html
    
    def validate(self, data):
        """验证数据完整性"""
        required_fields = [
            'PRODUCT_NAME', 'BRAND', 'CATEGORY', 'SUBCATEGORY',
            'SALES_VOLUME', 'PRICE', 'REVENUE', 'CONVERSION', 'REPURCHASE',
            'MANUFACTURER', 'LAUNCH_DATE', 'POSITIONING', 'MATERIAL', 'SELLING_POINT',
            'USER_AGE', 'USER_GENDER', 'USER_CITY', 'USER_INCOME', 'USER_TAGS',
            'CAROUSEL_SLIDES', 'CAROUSEL_DOTS', 'CHANNELS',
            'WORD_CLOUD', 'CHALLENGES', 'OPPORTUNITIES'
        ]
        
        missing = [f for f in required_fields if f not in data]
        
        # 检查标签字数
        if 'USER_TAGS' in data:
            # 提取标签文字
            tags_text = re.sub(r'<[^>]+?>', '', data['USER_TAGS'])
            if len(tags_text) > 18:
                print(f'⚠️ 警告: 标签总字数 {len(tags_text)} 超过18字限制')
        
        if missing:
            print(f'❌ 缺少字段: {missing}')
            return False
        
        print('✅ 数据验证通过')
        return True


def create_carousel_slides(images):
    """
    创建轮播图HTML
    
    Args:
        images: [(url, caption), ...]
    
    Returns:
        (slides_html, dots_html)
    """
    slides = []
    dots = []
    
    for i, (url, caption) in enumerate(images):
        active = 'active' if i == 0 else ''
        slides.append(f'''<div class="carousel-slide {active}">
    <img src="{url}" alt="{caption}">
    <div class="carousel-caption">{caption}</div>
</div>''')
        dots.append(f'<span class="carousel-dot {active}" onclick="goToSlide({i})"></span>')
    
    return '\n'.join(slides), '\n'.join(dots)


def create_channels(channels_data):
    """
    创建销售渠道HTML
    
    Args:
        channels_data: [(icon, name, account, value, role), ...]
    
    Returns:
        HTML字符串
    """
    channels = []
    for icon, name, account, value, role in channels_data:
        channels.append(f'''<div class="channel-item">
    <div class="channel-icon">{icon}</div>
    <div class="channel-name">{name}</div>
    <div class="channel-account">{account}</div>
    <div class="channel-value">{value}</div>
    <div class="channel-role">{role}</div>
</div>''')
    return '\n'.join(channels)


def create_word_cloud(words):
    """
    创建词云HTML
    
    Args:
        words: [(text, size, left, top, delay), ...]
    
    Returns:
        HTML字符串
    """
    word_spans = []
    for text, size, left, top, delay in words:
        color = 'var(--primary)' if len(word_spans) % 2 == 0 else 'var(--gold)'
        word_spans.append(f'<span class="word" style="font-size: {size}px; color: {color}; left: {left}%; top: {top}%; animation-delay: {delay}s;">{text}</span>')
    return '\n'.join(word_spans)


def create_co_words(items, is_challenge=True):
    """
    创建挑战/机遇词云HTML
    
    Args:
        items: [(text, size, left, top, delay), ...] 6个
        is_challenge: True=挑战(红色), False=机遇(绿色)
    
    Returns:
        HTML字符串
    """
    words = []
    for text, size, left, top, delay in items:
        if is_challenge:
            color = 'var(--primary)' if len(words) % 2 == 0 else '#A03030'
        else:
            color = 'var(--green)' if len(words) % 2 == 0 else '#3D7A6A'
        words.append(f'<span class="co-word" style="font-size: {size}px; color: {color}; left: {left}%; top: {top}%; animation-delay: {delay}s;">{text}</span>')
    return '\n'.join(words)


# 示例数据
EXAMPLE_DATA = {
    'PRODUCT_NAME': '泡泡玛特星星人怦然星动毛绒挂件盲盒',
    'BRAND': '泡泡玛特国际集团',
    'CATEGORY': '潮玩盲盒',
    'SUBCATEGORY': '毛绒挂件盲盒',
    
    'SALES_VOLUME': '10万+',
    'PRICE': '¥149',
    'REVENUE': '1490万',
    'CONVERSION': '4.5%',
    'REPURCHASE': '32%',
    
    'MANUFACTURER': '泡泡玛特国际集团',
    'LAUNCH_DATE': '2025-01',
    'POSITIONING': '毛绒挂件盲盒',
    'MATERIAL': '聚酯纤维/ABS/金属配件',
    'SELLING_POINT': '明星IP联名，盲盒惊喜体验',
    
    'USER_AGE': '18-30岁',
    'USER_GENDER': '女性70% · 男性30%',
    'USER_CITY': '上海 · 北京 · 深圳',
    'USER_INCOME': '中高收入',
    'USER_TAGS': '<span class="tag">潮玩</span><span class="tag">盲盒</span><span class="tag">IP运营</span><span class="tag">收藏</span><span class="tag">社交</span><span class="tag">送礼</span>',
}


def main():
    """示例用法"""
    generator = WCFXReportGenerator()
    
    # 创建轮播图
    images = [
        ('https://raw.githubusercontent.com/alandan97/wenchang-site/main/images/baidu_search.png', '泡泡玛特星星人怦然星动系列 - 百度图片'),
        ('https://raw.githubusercontent.com/alandan97/wenchang-site/main/images/baidu_search2.png', '泡泡玛特盲盒毛绒系列 - 百度图片'),
        ('https://raw.githubusercontent.com/alandan97/wenchang-site/main/images/baidu_search3.png', 'Pop Mart Star Man Plush - 百度图片'),
    ]
    slides, dots = create_carousel_slides(images)
    EXAMPLE_DATA['CAROUSEL_SLIDES'] = slides
    EXAMPLE_DATA['CAROUSEL_DOTS'] = dots
    
    # 创建销售渠道
    channels = [
        ('抖', '抖音', '@泡泡玛特官方', '35%', '直播带货主阵地'),
        ('天', '天猫', '@泡泡玛特旗舰店', '30%', '官方主渠道'),
        ('小', '小红书', '@泡泡玛特', '20%', '种草引流'),
        ('线', '线下店', '泡泡玛特门店', '15%', '体验消费'),
    ]
    EXAMPLE_DATA['CHANNELS'] = create_channels(channels)
    
    # 创建词云
    words = [
        ('太可爱了', 19, 20, 24, 1.9),
        ('抽到了隐藏款', 13, 58, 22, 0.2),
        ('停不下来', 17, 20, 44, 0.8),
        ('送朋友很喜欢', 14, 57, 56, 0.5),
        ('质量很好', 14, 28, 64, 1.6),
    ]
    EXAMPLE_DATA['WORD_CLOUD'] = create_word_cloud(words)
    
    # 创建挑战
    challenges = [
        ('二手市场炒作', 18, 15, 25, 0.4),
        ('同质化竞争', 16, 55, 20, 0.8),
        ('IP生命周期短', 20, 60, 45, 1.2),
        ('盲盒成瘾争议', 15, 10, 50, 0.6),
        ('供应链成本上升', 17, 35, 70, 1.0),
        ('盗版仿品泛滥', 14, 65, 75, 1.4),
    ]
    EXAMPLE_DATA['CHALLENGES'] = create_co_words(challenges, True)
    
    # 创建机遇
    opportunities = [
        ('影视联名合作', 20, 10, 22, 0.5),
        ('出海东南亚', 18, 55, 28, 0.9),
        ('虚拟潮玩NFT', 16, 20, 48, 1.3),
        ('主题乐园布局', 19, 50, 52, 0.7),
        ('数字化藏品', 15, 15, 72, 1.1),
        ('跨界品牌联名', 17, 60, 78, 1.5),
    ]
    EXAMPLE_DATA['OPPORTUNITIES'] = create_co_words(opportunities, False)
    
    # 验证并生成
    if generator.validate(EXAMPLE_DATA):
        generator.generate(EXAMPLE_DATA, 'wcfx-popmart-star.html')


if __name__ == '__main__':
    main()
