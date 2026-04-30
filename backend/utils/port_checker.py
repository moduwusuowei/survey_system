import os
import sys
import socket
import subprocess
import time

def kill_process_on_port(port=9999):
    """
    检测端口是否被占用，如果被占用则强制杀死进程
    """
    # 1. 检查端口是否被占用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect_ex 返回 0 表示连接成功，即端口已被占用
        if s.connect_ex(('localhost', port)) != 0:
            print(f"✅ 端口 {port} 空闲，可以直接使用。")
            return True

    print(f"⚠️ 端口 {port} 已被占用，正在尝试释放...")
    
    # 2. 查找占用端口的 PID (仅支持 Windows，因为报错 [Errno 10048] 是典型的 Windows 错误)
    try:
        # 使用 netstat -ano 查找特定端口的 PID
        # findstr 用于过滤出包含端口号的行
        cmd = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        
        if output:
            # 解析输出结果，通常格式为: TCP 0.0.0.0:9999 ... LISTENING 12345
            lines = output.strip().split('\n')
            for line in lines:
                if line:
                    parts = line.split()
                    pid = parts[-1] # PID 通常是最后一列
                    print(f"🔍 发现占用进程 PID: {pid}")
                    
                    # 3. 强制杀死进程
                    kill_cmd = f'taskkill /PID {pid} /F'
                    subprocess.run(kill_cmd, shell=True)
                    print(f"💥 已强制终止进程 {pid}")
            
            # 稍微等待一下系统释放资源
            time.sleep(1) 
            return True
        else:
            print("❌ 未找到占用该端口的进程信息，可能是系统保留端口。")
            return False
            
    except subprocess.CalledProcessError:
        print(f"ℹ️ 端口 {port} 实际上未被占用或无法获取进程信息。")
        return True
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return False



if __name__ == '__main__':
    kill_process_on_port(8888)
