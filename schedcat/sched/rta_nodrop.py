# V1.0 #
# import math
# def is_schedulable_with_nodrop(task_system, num_processors, delta, alpha, beta):
#     normal_tasks = [t for t in task_system if not getattr(t, 'is_consumer', False)]
#     consumer_tasks = [t for t in task_system if getattr(t, 'is_consumer', False)]
#     all_tasks_sorted = sorted(task_system, key=lambda x: x.priority, reverse=True)
#     for task in normal_tasks:
#         E_i = task.exec_cost + task.syscall_count * delta    
#         r_i = E_i
#         prev_r_i = 0        
#         iteration = 0
#         max_iterations = 100        
#         while iteration < max_iterations and abs(r_i - prev_r_i) > 1e-6:
#             prev_r_i = r_i
#             total_interference = 0            
#             for hp_task in normal_tasks:
#                 if hp_task.priority > task.priority:
#                     E_k = hp_task.exec_cost + hp_task.syscall_count * delta
#                     interference = math.ceil(r_i / hp_task.period) * E_k
#                     total_interference += interference
#             for consumer in consumer_tasks:
#                 if consumer.priority > task.priority:
#                     C_consumer = alpha + consumer.syscall_count * beta
#                     q_k = consumer.period
#                     interference = math.ceil(r_i / q_k) * C_consumer
#                     total_interference += interference            
#             r_i = E_i + task.blocking_time + total_interference            
#             if r_i > task.deadline:
#                 return False            
#             iteration += 1        
#         if r_i > task.deadline:
#             return False    
#     return True

# V2.0 #
# import math
# def is_schedulable_with_nodrop(task_system, num_processors, delta, alpha, beta):
#     normal_tasks = [t for t in task_system if not getattr(t, 'is_consumer', False)]
#     consumer_tasks = [t for t in task_system if getattr(t, 'is_consumer', False)]
#     all_tasks = sorted(normal_tasks, key=lambda x: x.priority, reverse=True)
#     for task in all_tasks:
#         E_i = task.exec_cost + task.syscall_count * delta        
#         r_i = E_i + task.blocking_time
#         prev_r_i = 0
#         iteration = 0
#         max_iterations = 100        
#         while iteration < max_iterations and abs(r_i - prev_r_i) > 1e-6:
#             prev_r_i = r_i
#             total_interference = 0            
#             for hp_task in normal_tasks:
#                 if hp_task.priority > task.priority:
#                     E_k = hp_task.exec_cost + hp_task.syscall_count * delta
#                     interference = math.ceil(r_i / hp_task.period) * E_k
#                     total_interference += interference
#             for consumer in consumer_tasks:
#                 if consumer.priority > task.priority:
#                     interference = math.ceil(r_i / consumer.period) * consumer.exec_cost
#                     total_interference += interference            
#             r_i = E_i + task.blocking_time + total_interference            
#             if r_i > task.deadline:
#                 return False            
#             iteration += 1        
#         if r_i > task.deadline:
#             return False    
#     return True

# V3.0 #
from __future__ import division
from math import ceil

def get_blocked(task):
    return task.__dict__.get('blocked', 0)

def get_jitter(task):
    return task.__dict__.get('jitter', 0)

def get_suspended(task):
    return task.__dict__.get('suspended', 0)

def get_prio_inversion(task):
    return task.__dict__.get('prio_inversion', 0)

def suspension_jitter(task):
    if get_suspended(task) > 0:
        return task.response_time - task.exec_cost
    else:
        return get_jitter(task)

def _nodrop_rta(task, own_demand, higher_prio_tasks, hp_jitter, delta, alpha, beta):

    max_iterations = 100
    tolerance = 1e-6
    
    normal_hp_tasks = [t for t in higher_prio_tasks if not getattr(t, 'is_consumer', False)]
    consumer_hp_tasks = [t for t in higher_prio_tasks if getattr(t, 'is_consumer', False)]

    r_i = own_demand + task.blocking_time
    prev_r_i = 0
    iteration = 0

    while iteration < max_iterations and abs(r_i - prev_r_i) > tolerance:
        prev_r_i = r_i
        total_interference = 0

        for hp in normal_hp_tasks:
            E_k = hp.exec_cost + hp.syscall_count * delta
            releases = ceil((r_i + hp_jitter(hp)) / hp.period)
            total_interference += releases * E_k

        for consumer in consumer_hp_tasks:
            C_consumer = alpha + consumer.syscall_count * beta
            releases = ceil((r_i + hp_jitter(consumer)) / consumer.period)
            total_interference += releases * C_consumer

        new_r_i = own_demand + task.blocking_time + total_interference
        
        if new_r_i > task.deadline:
            return False
        if new_r_i == r_i:
            break
            
        r_i = new_r_i
        iteration += 1

    task.response_time = r_i + get_jitter(task)
    return r_i <= task.deadline

def bound_response_times_with_nodrop(no_cpus, taskset, delta, alpha, beta):

    consumers = [t for t in taskset if getattr(t, 'is_consumer', False)]
    normal_tasks = [t for t in taskset if not getattr(t, 'is_consumer', False)]
    
    sorted_tasks = sorted(normal_tasks, key=lambda x: x.priority, reverse=True)
    
    for idx, task in enumerate(sorted_tasks):

        own_demand = (task.exec_cost + 
                     task.syscall_count * delta + 
                     get_prio_inversion(task))
        
        higher_prio = sorted_tasks[0:idx] + consumers
        
        if not _nodrop_rta(task, own_demand, higher_prio, get_jitter, delta, alpha, beta):
            return False
    return True

is_schedulable_with_nodrop = lambda ts, np, d, a, b: bound_response_times_with_nodrop(np, ts, d, a, b)