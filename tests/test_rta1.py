import unittest
from schedcat.model.tasks import TaskSystem, SporadicTask
from schedcat.model.consumers import create_consumers
from schedcat.sched.rta_nodrop import is_schedulable_with_nodrop

class TestRTAWithNoDrop(unittest.TestCase):
    def setUp(self):
        # 公共参数（delta, alpha, beta 来自实际测量）
        self.delta = 0.1
        self.alpha = 0.1
        self.beta = 0.05

    def test_overload_due_to_consumers(self):
        """测试因 Consumer 干扰导致的不可调度"""
        tasks = TaskSystem([
            SporadicTask(execution_time=4, period=5, syscall_count=10, priority=3),  # 高 syscall_count 增加干扰
            SporadicTask(execution_time=3, period=6, syscall_count=2, priority=2),
        ])
        consumers = create_consumers(tasks, self.alpha, self.beta, qk_ratio=1.0)
        full_system = tasks + consumers
        self.assertFalse(is_schedulable_with_nodrop(full_system, self.num_processors, self.delta, self.alpha, self.beta))

    def test_qk_ratio_impact(self):
        """测试不同 qk_ratio 对可调度性的影响"""
        tasks = TaskSystem([
            SporadicTask(execution_time=2, period=10, syscall_count=5, priority=3),
        ])
        # qk_ratio 过小（Consumer 高频触发）导致不可调度
        consumers = create_consumers(tasks, self.alpha, self.beta, qk_ratio=0.2)
        full_system = tasks + consumers
        self.assertFalse(is_schedulable_with_nodrop(full_system, self.num_processors, self.delta, self.alpha, self.beta))
        
        # qk_ratio 较大时可调度
        consumers = create_consumers(tasks, self.alpha, self.beta, qk_ratio=0.8)
        full_system = tasks + consumers
        self.assertTrue(is_schedulable_with_nodrop(full_system, self.num_processors, self.delta, self.alpha, self.beta))
        
    def test_consumer_period_impact(self):
        """验证消费者任务周期 q_k 对干扰的影响"""
        # 原始任务
        tasks = TaskSystem([
            SporadicTask(execution_time=2, period=10, syscall_count=3, priority=3),
        ])
    
        # 创建两种 Consumer 配置：
        # Case 1: qk_ratio=0.5（高频触发，预期不可调度）
        consumers_case1 = create_consumers(tasks, self.alpha, self.beta, qk_ratio=0.5)
        full_system_case1 = tasks + consumers_case1
        self.assertFalse(is_schedulable_with_nodrop(full_system_case1, self.num_processors, self.delta, self.alpha, self.beta))
        
        # Case 2: qk_ratio=2.0（低频触发，预期可调度）
        consumers_case2 = create_consumers(tasks, self.alpha, self.beta, qk_ratio=2.0)
        full_system_case2 = tasks + consumers_case2
        self.assertTrue(is_schedulable_with_nodrop(full_system_case2, self.num_processors, self.delta, self.alpha, self.beta))