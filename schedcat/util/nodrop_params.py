from schedcat.model.consumers import create_consumers
from schedcat.sched.rta_nodrop import is_schedulable_with_nodrop

def find_optimal_qk_ratio(original_tasks, num_processors, delta, alpha, beta, max_iter=20):
    # 初始搜索范围[low, high]
    low = 1
    high = 1  # 初始上限为 1，逐步扩展
    
    # 先尝试扩展上限直到找到不可调度的点
    while high <= 1024:
        consumers = create_consumers(original_tasks, alpha, beta, qk_ratio=high)
        full_system = original_tasks + consumers
        if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
            high *= 2  # 继续扩大上限
        else:
            break
    
    # 若 high=1 时已不可调度，直接返回 None
    if high == 1 and not is_schedulable_with_nodrop(
        create_consumers(original_tasks, alpha, beta, qk_ratio=high) + original_tasks,
        num_processors, delta, alpha, beta
    ):
        return None
    
    # 二分搜索区间 [low, high]
    optimal = None
    for _ in range(max_iter):
        if low > high:
            break
        mid = (low + high) // 2  # 整数中间值
        consumers = create_consumers(original_tasks, alpha, beta, qk_ratio=mid)
        full_system = original_tasks + consumers
        schedulable = is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta)
        
        if schedulable:
            optimal = mid
            high = mid - 1  # 尝试更小的 qk_ratio
        else:
            low = mid + 1   # 需要更大的 qk_ratio
    
    return optimal

def calculate_delta_alpha_beta():
    return 0.1, 0.1, 0.05