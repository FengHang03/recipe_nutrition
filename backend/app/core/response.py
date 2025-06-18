from typing import Any, Optional
from datetime import datetime

def create_response(
    success: bool,
    data: Optional[Any] = None,
    message: Optional[str] = None,
    error: Optional[str] = None
) -> dict:
    """创建统一的API响应格式"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    if error:
        response["error"] = error
    
    return response