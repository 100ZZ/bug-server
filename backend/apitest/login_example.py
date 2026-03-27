"""
登录接口示例代码
演示如何处理验证码和登录流程
"""
import requests
import json
from typing import Optional, Dict, Any


class LoginClient:
    """登录客户端"""
    
    def __init__(self, base_url: str, tenant_id: str = "1"):
        """
        初始化登录客户端
        
        Args:
            base_url: 基础URL，例如 "http://192.168.100.186:8080"
            tenant_id: 租户ID，默认 "1"
        """
        self.base_url = base_url.rstrip('/')
        self.tenant_id = tenant_id
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "tenant-id": tenant_id
        })
    
    def get_captcha(self, captcha_type: str = "blockPuzzle") -> Optional[Dict[str, Any]]:
        """
        获取验证码
        
        Args:
            captcha_type: 验证码类型，"blockPuzzle"(滑块) 或 "clickWord"(点选)
            
        Returns:
            验证码数据，包含图片和token
        """
        url = f"{self.base_url}/admin-api/system/captcha/get"
        data = {"captchaType": captcha_type}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("repCode") == "0000":
                return result.get("repData")
            else:
                print(f"获取验证码失败: {result.get('repMsg')}")
                return None
        except Exception as e:
            print(f"获取验证码异常: {e}")
            return None
    
    def check_captcha(
        self, 
        token: str, 
        point_json: str, 
        captcha_type: str = "blockPuzzle"
    ) -> Optional[str]:
        """
        校验验证码
        
        Args:
            token: 验证码token
            point_json: 验证坐标（滑块验证格式：'{"x":123,"y":45}'，点选验证格式：'1,2,3'）
            captcha_type: 验证码类型
            
        Returns:
            验证成功返回captchaVerification字符串，失败返回None
        """
        url = f"{self.base_url}/admin-api/system/captcha/check"
        data = {
            "captchaType": captcha_type,
            "pointJson": point_json,
            "token": token
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("repCode") == "0000":
                # 注意：实际的前端代码会使用AES加密生成captchaVerification
                # 这里需要根据实际的加密逻辑生成
                # 简化示例：直接使用token（实际应该加密）
                return token  # 实际应该返回加密后的字符串
            else:
                print(f"验证码校验失败: {result.get('repMsg')}")
                return None
        except Exception as e:
            print(f"验证码校验异常: {e}")
            return None
    
    def login(
        self, 
        username: str, 
        password: str, 
        captcha_verification: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        登录
        
        Args:
            username: 账号
            password: 密码
            captcha_verification: 验证码验证字符串（如果为None，会尝试不传验证码）
            
        Returns:
            登录结果，包含accessToken等
        """
        url = f"{self.base_url}/admin-api/system/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        # 如果提供了验证码，添加到请求中
        if captcha_verification:
            data["captchaVerification"] = captcha_verification
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data")
            else:
                print(f"登录失败: {result.get('msg')}")
                return None
        except Exception as e:
            print(f"登录异常: {e}")
            return None
    
    def login_with_captcha(
        self, 
        username: str, 
        password: str,
        point_json: str,
        captcha_type: str = "blockPuzzle"
    ) -> Optional[Dict[str, Any]]:
        """
        完整的登录流程（包含验证码处理）
        
        Args:
            username: 账号
            password: 密码
            point_json: 验证坐标（需要用户完成验证后提供）
            captcha_type: 验证码类型
            
        Returns:
            登录结果
        """
        # 1. 获取验证码
        print("步骤1: 获取验证码...")
        captcha_data = self.get_captcha(captcha_type)
        if not captcha_data:
            return None
        
        token = captcha_data.get("token")
        print(f"获取验证码成功，token: {token}")
        
        # 2. 校验验证码
        print("步骤2: 校验验证码...")
        captcha_verification = self.check_captcha(token, point_json, captcha_type)
        if not captcha_verification:
            return None
        
        print("验证码校验成功")
        
        # 3. 登录
        print("步骤3: 执行登录...")
        login_result = self.login(username, password, captcha_verification)
        
        if login_result:
            print(f"登录成功！accessToken: {login_result.get('accessToken', '')[:30]}...")
        
        return login_result


def example_1_simple_login():
    """示例1: 简单登录（如果验证码已关闭或使用空字符串）"""
    client = LoginClient("http://192.168.100.186:8080", tenant_id="1")
    
    # 尝试不使用验证码登录（如果系统允许）
    result = client.login("admin", "admin123", captcha_verification="")
    
    if result:
        print("登录成功！")
        print(f"Token: {result.get('accessToken')}")
    else:
        print("登录失败，可能需要验证码")


def example_2_login_with_captcha():
    """示例2: 带验证码的完整登录流程"""
    client = LoginClient("http://192.168.100.186:8080", tenant_id="1")
    
    # 注意：point_json需要用户实际完成验证后提供
    # 滑块验证示例：'{"x":123,"y":45}'
    # 点选验证示例：'1,2,3'
    point_json = '{"x":123,"y":45}'  # 实际使用时需要用户操作获得
    
    result = client.login_with_captcha(
        username="admin",
        password="admin123",
        point_json=point_json,
        captcha_type="blockPuzzle"
    )
    
    if result:
        print("登录成功！")
        print(f"Token: {result.get('accessToken')}")


def example_3_get_captcha_only():
    """示例3: 仅获取验证码（用于前端显示）"""
    client = LoginClient("http://192.168.100.186:8080", tenant_id="1")
    
    captcha_data = client.get_captcha("blockPuzzle")
    
    if captcha_data:
        print("验证码获取成功")
        print(f"Token: {captcha_data.get('token')}")
        print(f"背景图片长度: {len(captcha_data.get('originalImageBase64', ''))}")
        print(f"滑块图片长度: {len(captcha_data.get('jigsawImageBase64', ''))}")
        
        # 可以保存图片用于显示
        # import base64
        # img_data = captcha_data.get('originalImageBase64', '').split(',')[1]
        # with open('captcha.png', 'wb') as f:
        #     f.write(base64.b64decode(img_data))


if __name__ == "__main__":
    print("=" * 50)
    print("登录接口示例")
    print("=" * 50)
    
    print("\n示例1: 简单登录（无验证码）")
    print("-" * 50)
    example_1_simple_login()
    
    print("\n示例2: 带验证码的完整登录流程")
    print("-" * 50)
    print("注意：需要用户实际完成验证码验证")
    # example_2_login_with_captcha()  # 取消注释以运行
    
    print("\n示例3: 仅获取验证码")
    print("-" * 50)
    example_3_get_captcha_only()

