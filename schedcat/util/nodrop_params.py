from schedcat.model.consumers import create_consumers
from schedcat.sched.rta_nodrop import is_schedulable_with_nodrop
from schedcat.model.consumers import create_consumers_per_task

def find_per_task_qk_candidates(original_tasks, num_processors, delta, alpha, beta,
                                max_qk=1024, top_k=3):
    """
    对每个任务，找出可调度的若干个 qk_ratio 候选值（整数）。
    优先按照任务优先级从高到低排序，处理完再按原顺序返回结果。

    返回：
        List[List[int]]，每个任务对应一个 qk_ratio 候选整数列表。
    """
    # 记录原始索引，用于最终结果恢复顺序
    indexed_tasks = list(enumerate(original_tasks))
    # 根据优先级从高到低排序（即 priority 数值小的优先级高）
    sorted_indexed_tasks = sorted(indexed_tasks, key=lambda x: x[1].priority)

    candidates_all_sorted = []

    for _, task in sorted_indexed_tasks:
        qk = 1
        min_schedulable_qk = None

        # 指数扩展
        while True:
            consumers = create_consumers([task], alpha, beta, qk_ratio=qk)
            full_system = [task] + consumers
            if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
                break
            qk *= 2
            if qk > max_qk:
                break

        if qk > max_qk:
            candidates_all_sorted.append([])  # 无法调度
            continue

        # 二分回扫
        low = max(1, qk // 2)
        high = qk
        while low <= high:
            mid = (low + high) // 2
            consumers = create_consumers([task], alpha, beta, qk_ratio=mid)
            full_system = [task] + consumers
            if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
                min_schedulable_qk = mid
                high = mid - 1
            else:
                low = mid + 1

        if min_schedulable_qk is None:
            candidates_all_sorted.append([])
            continue

        # 向上枚举 top_k 个可行值
        valid_qks = []
        for qk_val in range(min_schedulable_qk, min_schedulable_qk + top_k):
            consumers = create_consumers([task], alpha, beta, qk_ratio=qk_val)
            full_system = [task] + consumers
            if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
                valid_qks.append(qk_val)
        candidates_all_sorted.append(valid_qks)

    # 将候选列表映射回原顺序
    # 结果是：按原任务顺序排列，每个元素是对应任务的候选 qk_ratio 列表
    final_candidates_all = [None] * len(original_tasks)
    for (orig_idx, _), qks in zip(sorted_indexed_tasks, candidates_all_sorted):
        final_candidates_all[orig_idx] = qks

    return final_candidates_all



def calculate_delta_alpha_beta():
    return 0.1, 0.1, 0.05


def optimized_greedy_backtrack_qk_search(original_tasks, num_processors, delta, alpha, beta,
                                         qk_candidates_per_task):
    best_qk_config = None
    best_cost = float('inf')
    num_tasks = len(original_tasks)

    # 按优先级从高到低排序任务和候选qk值
    task_qk_pairs = list(zip(original_tasks, qk_candidates_per_task))
    task_qk_pairs.sort(key=lambda pair: pair[0].priority)

    sorted_tasks = [pair[0] for pair in task_qk_pairs]
    sorted_qk_candidates = [pair[1] for pair in task_qk_pairs]

    # 预先计算每个任务的最小停留时间，用于估价剪枝
    min_stay_times = [t.period * min(qks) for t, qks in zip(sorted_tasks, sorted_qk_candidates)]

    def dfs(idx, current_qk_list, current_cost):
        nonlocal best_qk_config, best_cost

        if idx == num_tasks:
            # 所有任务已选完 qk_ratio，提前保证可调度
            consumers = create_consumers_per_task(sorted_tasks, alpha, beta, current_qk_list)
            full_system = sorted_tasks + consumers
            if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_qk_config = current_qk_list[:]
            return

        # 估计最小可能成本，提前剪枝
        remaining_min_cost = sum(min_stay_times[i] for i in range(idx, num_tasks))
        if current_cost + remaining_min_cost >= best_cost:
            return

        for qk in sorted(sorted_qk_candidates[idx]):
            new_cost = current_cost + sorted_tasks[idx].period * qk
            if new_cost >= best_cost:
                continue

            current_qk_list.append(qk)

            # 构建当前系统以判断调度性
            consumers = create_consumers_per_task(sorted_tasks[:idx+1], alpha, beta, current_qk_list)
            full_system = sorted_tasks[:idx+1] + consumers
            if is_schedulable_with_nodrop(full_system, num_processors, delta, alpha, beta):
                dfs(idx + 1, current_qk_list, new_cost)

            current_qk_list.pop()

    dfs(0, [], 0)

    # 映射回原始任务顺序
    if best_qk_config is not None:
        id_map = {id(task): i for i, task in enumerate(original_tasks)}
        qk_result = [0] * num_tasks
        for sorted_task, qk in zip(sorted_tasks, best_qk_config):
            qk_result[id_map[id(sorted_task)]] = qk
        return qk_result
    else:
        return None






