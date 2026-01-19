"""权限控制模块"""
from fastapi import HTTPException
from typing import List

# 权限规则定义
PERMISSIONS = {
    'admin': {
        'projects': ['read', 'create', 'update', 'delete'],
        'users': ['read', 'create', 'update', 'delete'],
        'bugs': ['read', 'create', 'update', 'delete'],
        'testcases': ['read', 'create', 'update', 'delete'],
        'comments': ['read', 'create', 'update', 'delete'],
        'statistics': ['read'],
        'models': ['read', 'create', 'update', 'delete'],
        'apitest': ['read', 'create', 'update', 'delete', 'execute']  # admin拥有所有apitest权限
    },
    'product': {
        'projects': ['read'],  # 只有管理员可以创建、更新、删除项目
        'users': ['read'],  # 只能查看用户，不能修改
        'bugs': ['read', 'create', 'update', 'delete'],
        'testcases': ['read', 'create', 'update', 'delete'],
        'comments': ['read', 'create', 'update', 'delete'],
        'statistics': ['read'],
        'models': ['read'],
        'apitest': ['read', 'create', 'update', 'delete', 'execute']
    },
    'developer': {
        'projects': ['read'],  # 只有管理员可以创建、更新、删除项目
        'users': ['read'],  # 只能查看用户，不能修改
        'bugs': ['read', 'create', 'update', 'delete'],
        'testcases': ['read', 'create', 'update', 'delete'],
        'comments': ['read', 'create', 'update', 'delete'],
        'statistics': ['read'],
        'models': ['read'],
        'apitest': ['read', 'create', 'update', 'delete', 'execute']
    },
    'tester': {
        'projects': ['read'],  # 只有管理员可以创建、更新、删除项目
        'users': ['read'],  # 只能查看用户，不能修改
        'bugs': ['read', 'create', 'update', 'delete'],
        'testcases': ['read', 'create', 'update', 'delete'],
        'comments': ['read', 'create', 'update', 'delete'],
        'statistics': ['read'],
        'models': ['read'],
        'apitest': ['read', 'create', 'update', 'delete', 'execute']
    },
    'guest': {
        'projects': ['read'],  # 游客只能查看
        'users': ['read'],
        'bugs': ['read'],
        'testcases': ['read'],
        'comments': ['read'],
        'statistics': ['read'],
        'models': ['read'],
        'apitest': ['read']  # 游客只能查看
    }
}


def check_permission(user_role: str, resource: str, action: str) -> bool:
    """
    检查用户是否有权限执行指定操作
    
    Args:
        user_role: 用户角色 (admin, product, developer, tester, guest)
        resource: 资源类型 (projects, users, bugs, comments, statistics)
        action: 操作类型 (read, create, update, delete)
    
    Returns:
        bool: 是否有权限
    """
    if user_role not in PERMISSIONS:
        return False
    
    if resource not in PERMISSIONS[user_role]:
        return False
    
    return action in PERMISSIONS[user_role][resource]


def require_permission(user_role: str, resource: str, action: str):
    """
    权限检查装饰器辅助函数，如果没有权限则抛出异常
    
    Args:
        user_role: 用户角色
        resource: 资源类型
        action: 操作类型
    
    Raises:
        HTTPException: 403 Forbidden
    """
    if not check_permission(user_role, resource, action):
        raise HTTPException(
            status_code=403,
            detail=f"权限不足: {user_role} 角色无法对 {resource} 执行 {action} 操作"
        )


def get_user_permissions(user_role: str) -> dict:
    """
    获取用户的所有权限
    
    Args:
        user_role: 用户角色
    
    Returns:
        dict: 权限字典
    """
    return PERMISSIONS.get(user_role, {})


# 角色显示名称映射
ROLE_NAMES = {
    'admin': '管理员',
    'product': '产品',
    'developer': '开发',
    'tester': '测试',
    'guest': '游客'
}


def get_role_name(role: str) -> str:
    """获取角色显示名称"""
    return ROLE_NAMES.get(role, role)

