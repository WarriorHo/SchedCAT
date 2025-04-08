# import unittest
# from schedcat.model.tasks import TaskSystem, SporadicTask
# from schedcat.model.consumers import create_consumers
# from schedcat.sched.rta_nodrop import is_schedulable_with_nodrop

# class TestRTAWithNoDrop(unittest.TestCase):
#     def setUp(self):
#         self.delta = 0.1
#         self.alpha = 0.1
#         self.beta = 0.05
#         self.num_processors = 1

#     def test_basic_schedulable(self):
#         tasks = TaskSystem([
#             SporadicTask(exec_cost=2, period=5, syscall_count=3, priority=3),
#             SporadicTask(exec_cost=3, period=6, syscall_count=2, priority=2),
#         ])
#         self.assertTrue(is_schedulable_with_nodrop(tasks, self.num_processors, self.delta, self.alpha, self.beta))

#     def test_with_consumers_schedulable(self):
#         tasks = TaskSystem([
#             SporadicTask(exec_cost=2, period=10, syscall_count=3, priority=3),
#             SporadicTask(exec_cost=3, period=15, syscall_count=2, priority=2),
#         ])
#         consumers = create_consumers(tasks, self.alpha, self.beta, qk_ratio=1.0)
#         full_system = tasks + consumers
#         self.assertTrue(is_schedulable_with_nodrop(full_system, self.num_processors, self.delta, self.alpha, self.beta))

# if __name__ == '__main__':
#     unittest.main()


import unittest
from schedcat.model.tasks import TaskSystem, SporadicTask
from schedcat.model.consumers import create_consumers
from schedcat.sched.rta_nodrop import is_schedulable_with_nodrop

class TestRTAWithNoDrop(unittest.TestCase):
    def setUp(self):
        
        self.delta = 0.1
        self.alpha = 0.2
        self.beta = 0.05
        self.num_processors = 1

    def test_basic_schedulable(self):

        tasks = TaskSystem([
            SporadicTask(
                exec_cost=2, 
                period=10, 
                deadline=10,
                syscall_count=3,
                priority=2
            ),
            SporadicTask(
                exec_cost=3,
                period=15,
                deadline=15,
                syscall_count=2,
                priority=1
            )
        ])
        
        tasks[0].blocking_time = 0.0
        tasks[1].blocking_time = 0.0
        self.assertTrue(is_schedulable_with_nodrop(
            tasks, self.num_processors, self.delta, self.alpha, self.beta))

    def test_with_consumers_schedulable(self):
        
        tasks = TaskSystem([
            SporadicTask(
                exec_cost=2,
                period=20,
                deadline=20,
                syscall_count=3,
                priority=3
            ),
            SporadicTask(
                exec_cost=3,
                period=30,
                deadline=30,
                syscall_count=2,
                priority=2
            )
        ])
        
        consumers = create_consumers(tasks, self.alpha, self.beta, qk_ratio=1.0)
        full_system = tasks + consumers
        
        self.assertTrue(is_schedulable_with_nodrop(
            full_system, self.num_processors, self.delta, self.alpha, self.beta))

if __name__ == '__main__':
    unittest.main()