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


import math

def is_schedulable_with_nodrop(task_system, num_processors, delta, alpha, beta):

    normal_tasks = [t for t in task_system if not getattr(t, 'is_consumer', False)]
    consumer_tasks = [t for t in task_system if getattr(t, 'is_consumer', False)]

    all_tasks = sorted(normal_tasks, key=lambda x: x.priority, reverse=True)

    for task in all_tasks:

        E_i = task.exec_cost + task.syscall_count * delta
        
        r_i = E_i + task.blocking_time
        prev_r_i = 0
        iteration = 0
        max_iterations = 100
        
        while iteration < max_iterations and abs(r_i - prev_r_i) > 1e-6:
            prev_r_i = r_i
            total_interference = 0
            
            for hp_task in normal_tasks:
                if hp_task.priority > task.priority:
                    E_k = hp_task.exec_cost + hp_task.syscall_count * delta
                    interference = math.ceil(r_i / hp_task.period) * E_k
                    total_interference += interference

            for consumer in consumer_tasks:
                if consumer.priority > task.priority:
                    interference = math.ceil(r_i / consumer.period) * consumer.exec_cost
                    total_interference += interference
            
            r_i = E_i + task.blocking_time + total_interference
            
            if r_i > task.deadline:
                return False
            
            iteration += 1
        
        if r_i > task.deadline:
            return False
    
    return True