#!/usr/bin/env python3
"""
Pluto-Clean Ollama集成测试脚本
使用 modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest 模型
测试修复后的类型注解是否影响程序正常运行
"""

import json
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径，确保可以导入pluto模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pluto.data_engine import DataEngine, EngineArguments
from pluto.topic_tree import TopicTree, TopicTreeArguments
from pluto.types import APIProvider


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("测试 1: 基本功能测试")
    print("=" * 60)
    
    try:
        # 测试类初始化
        args = EngineArguments(
            instructions="生成关于Python编程的问答对话",
            system_prompt="你是一个专业的Python编程导师，擅长解答编程问题。"
        )
        engine = DataEngine(args)
        print("✓ DataEngine 初始化成功")
        
        # 测试基本参数验证
        assert args.instructions is not None
        assert args.system_prompt is not None
        print("✓ 参数验证通过")
        
        return True
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False


def test_ollama_connection():
    """测试Ollama连接"""
    print("\n" + "=" * 60)
    print("测试 2: Ollama连接测试")
    print("=" * 60)
    
    model_name = "modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest"
    
    try:
        import requests
        
        # 测试Ollama服务是否可用
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if model_name in model_names:
                print(f"✓ 目标模型 {model_name} 可用")
                return True
            else:
                print(f"✗ 目标模型 {model_name} 不在可用模型列表中")
                print(f"可用模型: {model_names}")
                return False
        else:
            print(f"✗ Ollama API 响应错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Ollama连接测试失败: {e}")
        return False


def test_topic_tree_generation():
    """测试主题树生成功能"""
    print("\n" + "=" * 60)
    print("测试 3: TopicTree 生成测试")
    print("=" * 60)
    
    model_name = "modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest"
    
    try:
        # 创建主题树参数 - 使用较小的参数减少测试时间
        tree_args = TopicTreeArguments(
            root_prompt="Python编程基础",
            model_system_prompt="你是一个编程教育专家，擅长将复杂概念分解为易懂的子主题。",
            tree_degree=3,  # 每个节点3个子主题
            tree_depth=2,   # 深度2层
            api_provider=APIProvider.OLLAMA,
            api_base="http://localhost:11434"
        )
        
        print(f"正在使用模型: {model_name}")
        print("构建主题树中...")
        
        # 创建并构建主题树
        tree = TopicTree(tree_args)
        tree.build_tree(model_name)
        
        # 验证结果
        if tree.tree_paths and len(tree.tree_paths) > 0:
            print(f"✓ 主题树构建成功，生成了 {len(tree.tree_paths)} 个主题路径")
            
            # 显示前几个主题路径
            print("\n生成的主题路径示例:")
            for i, path in enumerate(tree.tree_paths[:3]):
                print(f"  {i+1}. {' -> '.join(path)}")
            
            # 保存主题树
            tree_filename = f"test_topic_tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            tree.save(tree_filename)
            print(f"✓ 主题树已保存到: {tree_filename}")
            
            return tree
        else:
            print("✗ 主题树构建失败: 未生成任何主题路径")
            return None
            
    except Exception as e:
        print(f"✗ 主题树生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_data_generation_simple():
    """测试简单数据生成功能"""
    print("\n" + "=" * 60)
    print("测试 4: 简单数据生成测试")
    print("=" * 60)
    
    model_name = "modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest"
    
    try:
        # 创建引擎参数
        args = EngineArguments(
            instructions="生成关于Python基础概念的问答对话，包括变量、函数、循环等主题。",
            system_prompt="你是一个经验丰富的Python编程导师。"
        )
        
        # 创建数据引擎
        engine = DataEngine(args)
        
        print(f"正在使用模型: {model_name}")
        print("生成数据中...")
        
        # 生成数据 - 使用较小的参数
        dataset = engine.create_data(
            model_name=model_name,
            num_steps=2,  # 只生成2步
            batch_size=2,  # 每步2个样本
            api_provider=APIProvider.OLLAMA,
            api_base="http://localhost:11434"
        )
        
        # 验证结果
        if dataset and dataset.samples and len(dataset.samples) > 0:
            print(f"✓ 数据生成成功，生成了 {len(dataset.samples)} 个样本")
            
            # 验证数据格式
            sample = dataset.samples[0]
            if validate_sample_format(sample):
                print("✓ 数据格式验证通过")
            else:
                print("✗ 数据格式验证失败")
                return None
            
            # 保存数据集
            dataset_filename = f"test_dataset_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            dataset.save(dataset_filename)
            print(f"✓ 数据集已保存到: {dataset_filename}")
            
            # 显示第一个样本
            print("\n生成的样本示例:")
            print_sample(sample)
            
            return dataset
        else:
            print("✗ 数据生成失败: 未生成任何样本")
            return None
            
    except Exception as e:
        print(f"✗ 简单数据生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_data_generation_with_topic_tree(topic_tree):
    """测试使用主题树的数据生成功能"""
    print("\n" + "=" * 60)
    print("测试 5: 使用TopicTree的数据生成测试")
    print("=" * 60)
    
    if topic_tree is None:
        print("✗ 跳过此测试: 主题树不可用")
        return None
    
    model_name = "modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest"
    
    try:
        # 创建引擎参数
        args = EngineArguments(
            instructions="根据给定的主题路径，生成高质量的Python编程问答对话。",
            system_prompt="你是一个专业的Python编程导师，能够针对特定主题生成教学对话。"
        )
        
        # 创建数据引擎
        engine = DataEngine(args)
        
        print(f"正在使用模型: {model_name}")
        print("使用主题树生成数据中...")
        
        # 使用主题树生成数据
        dataset = engine.create_data(
            model_name=model_name,
            num_steps=2,  # 只生成2步
            batch_size=2,  # 每步2个样本
            topic_tree=topic_tree,
            api_provider=APIProvider.OLLAMA,
            api_base="http://localhost:11434"
        )
        
        # 验证结果
        if dataset and dataset.samples and len(dataset.samples) > 0:
            print(f"✓ 使用主题树的数据生成成功，生成了 {len(dataset.samples)} 个样本")
            
            # 保存数据集
            dataset_filename = f"test_dataset_with_tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            dataset.save(dataset_filename)
            print(f"✓ 数据集已保存到: {dataset_filename}")
            
            # 显示第一个样本
            print("\n生成的样本示例:")
            print_sample(dataset.samples[0])
            
            return dataset
        else:
            print("✗ 使用主题树的数据生成失败: 未生成任何样本")
            return None
            
    except Exception as e:
        print(f"✗ 使用主题树的数据生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_sample_format(sample):
    """验证样本格式是否符合OpenAI标准"""
    try:
        # 检查基本结构
        if not isinstance(sample, dict):
            print(f"✗ 样本不是字典格式: {type(sample)}")
            return False
        
        if 'messages' not in sample:
            print("✗ 样本缺少 'messages' 字段")
            return False
        
        messages = sample['messages']
        if not isinstance(messages, list):
            print(f"✗ messages 不是列表格式: {type(messages)}")
            return False
        
        # 检查消息格式
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                print(f"✗ 消息 {i} 不是字典格式")
                return False
            
            if 'role' not in message or 'content' not in message:
                print(f"✗ 消息 {i} 缺少 'role' 或 'content' 字段")
                return False
            
            if message['role'] not in ['system', 'user', 'assistant']:
                print(f"✗ 消息 {i} 的role无效: {message['role']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 样本格式验证错误: {e}")
        return False


def print_sample(sample):
    """打印样本内容"""
    try:
        for i, message in enumerate(sample['messages']):
            role = message['role']
            content = message['content']
            # 限制内容长度以便显示
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"  {role}: {content}")
    except Exception as e:
        print(f"✗ 打印样本失败: {e}")


def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 Pluto-Clean Ollama集成测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模型: modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest")
    
    # 测试结果跟踪
    test_results = {}
    
    # 1. 基本功能测试
    test_results['basic'] = test_basic_functionality()
    
    # 2. Ollama连接测试
    test_results['connection'] = test_ollama_connection()
    
    if not test_results['connection']:
        print("\n⚠️ Ollama连接失败，跳过后续测试")
        return test_results
    
    # 3. 主题树生成测试
    topic_tree = test_topic_tree_generation()
    test_results['topic_tree'] = topic_tree is not None
    
    # 4. 简单数据生成测试
    simple_dataset = test_data_generation_simple()
    test_results['simple_generation'] = simple_dataset is not None
    
    # 5. 使用主题树的数据生成测试
    tree_dataset = test_data_generation_with_topic_tree(topic_tree)
    test_results['tree_generation'] = tree_dataset is not None
    
    # 测试结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复后的代码工作正常。")
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
    
    # 保存测试报告
    report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'model': 'modelscope.cn/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest',
            'results': test_results,
            'summary': f"{passed}/{total} tests passed"
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📊 测试报告已保存到: {report_filename}")
    
    return test_results


if __name__ == "__main__":
    # 设置输出编码
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    # 运行测试
    results = run_comprehensive_test()
    
    # 退出码
    sys.exit(0 if all(results.values()) else 1)