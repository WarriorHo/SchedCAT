# from schedcat.model.tasks import SporadicTask

# def create_consumers(original_tasks, alpha, beta, qk_ratio=1.0, priority_offset=None):
    
#     if priority_offset is None:
#         max_original_priority = max(t.priority for t in original_tasks) if original_tasks else 0
#         priority_offset = max_original_priority + 1

#     sorted_tasks = sorted(original_tasks, key=lambda x: x.priority, reverse=True)
    
#     consumers = []
#     for idx, task in enumerate(sorted_tasks):

#         C_consumer = alpha + task.syscall_count * beta

#         q_k = qk_ratio * task.period
#         deadline = q_k
        
#         consumer_priority = priority_offset + idx
        
#         consumer = SporadicTask(
#             exec_cost=C_consumer,
#             period=q_k,
#             deadline=deadline,
#         )
#         consumer.priority = consumer_priority
#         consumer.is_consumer = True
#         consumer.syscall_count = task.syscall_count
#         consumers.append(consumer)
    
#     return sorted(consumers, key=lambda x: x.priority, reverse=True)

from schedcat.model.tasks import SporadicTask

def create_consumers(original_tasks, alpha, beta, qk_ratio=1.0, priority_offset=None):
    
    if priority_offset is None:
        max_original_priority = max(t.priority for t in original_tasks) if original_tasks else 0
        priority_offset = max_original_priority + 1

    sorted_tasks = sorted(original_tasks, key=lambda x: x.priority, reverse=True)
    
    consumers = []
    for idx, task in enumerate(sorted_tasks):
        C_consumer = alpha + task.syscall_count * beta
        q_k = qk_ratio * task.period
        
        consumer_id = "consumer_{0}".format(task.id) if task.id else None
        
        consumer = SporadicTask(
            exec_cost=C_consumer,
            period=q_k,
            deadline=q_k,
            syscall_count=0,
            priority=priority_offset + idx,
            # id=f"consumer_{task.id}"
            id=consumer_id
        )
        consumer.is_consumer = True
        consumers.append(consumer)
    
    return sorted(consumers, key=lambda x: x.priority, reverse=True)