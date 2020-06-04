"""
フリックキーボード（スマホ側）
テキスト送信部
"""
import socket

class Sender():
    def __init__(self, port, ipaddr, timeout=5.0):
        """
        送信側
        Parameters
        ----------
        port : int
            通信するポート番号
        ipaddr : str
            相手のIPアドレス
        timeout : float
            タイムアウトの時間
        """
        self.port = port
        self.ipaddr = ipaddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
    
#    def __del__(self):
#        self.sock.close()

    def connect(self):
        self.sock.connect((self.ipaddr, self.port))            
    
    def send(self, text, enc="utf-8"):
        """
        データを送信する
        
        Parameters
        ----------
        text : str
            送信するテキスト
        enc : str
            エンコードのタイプ。Noneでエンコードなし
        """
        if(enc is not None):
            text_ = text.encode(enc)
        else:
            text_ = text
        self.sock.sendall(text_)
    
    def close(self):
        #self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
