"""
フリックキーボード(受信側)
PC用
"""
import sys
import time
import socket
import pyautogui
import pyperclip
import threading

def type_text(text):
    # 与えた文字を入力（クリップボードにコピー＆ペースト）
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    return True

def type_backspace():
    pyautogui.typewrite(["backspace"])
    return True

def type_enter():
    pyautogui.typewrite(["enter"])
    return True

class Receiver():
    def __init__(self, port, ipaddr=None, set_daemon=True):
        """
        受信側

        Parameters
        ----------
        port : int
            使用するポート番号
        ipaddr : None or str
            受信側PCのIPアドレス．Noneで自動取得．
        set_daemon : bool
            スレッドをデーモン化するか．受信部スレッド終了を待たずにメインスレッドを停止させる．
        """
        if(ipaddr is None):
            host = socket.gethostname()
            ipaddr = socket.gethostbyname(host)
        self.ipaddr = ipaddr
        self.port = port
        self.set_daemon = set_daemon
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.loopflag = False
        print("ip:{0} port:{1}".format(self.ipaddr, self.port))
    
    def loop(self):
        self.sock.settimeout(0.5)
        self.sock.bind((self.ipaddr, self.port))
        self.sock.listen(1)
        print("start listening...")
        while(self.loopflag):
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            print("accepted")
            with conn:
                while(self.loopflag):
                    # print("waiting...")
                    data = conn.recv(1024)
                    if(not data):
                        break
                    if(data[:1]==b"\x08"):  # 連続してbackspaceを押すと，複数個同時に送られてくる（例：b"\x08\x08\x08）ことがあるため，先頭8バイトのみチェック
                        print("> BS")
                        type_backspace()
                    elif(data==b"\x0a"):
                        print("> Enter")
                        type_enter()
                    elif(data==b"\x00"):
                        print("STOP CLIENT")
                        break
                    else:
                        text = data.decode("utf-8")
                        print(">", text)
                        type_text(text)

    def start_loop(self):
        self.loopflag = True
        self.thread = threading.Thread(target=self.loop)
        if(self.set_daemon):
            self.thread.setDaemon(True)
        self.thread.start()
        print("start_thread")
    
    def stop_loop(self):
        print("stop loop")
        self.loopflag = False
        time.sleep(0.6)  # socketがtimeoutするまで待つ
        if(not self.set_daemon):
            print("waiting to stop client...")  # 送信側が停止するのを待つ
            self.thread.join()
        print("stop_thread")
    
    def close_sock(self):
        self.sock.close()
        print("socket closed")

def main():
    """
    ポート番号を設定し，送信（スマホ）側と合わせる
    実行中，コンソールに"s"を入力し，Enterを押すと受信（PC）側を停止できる．
    """

    # コマンドライン引数
    ipaddr = None
    args = sys.argv
    if(len(args)<=1):
        print("Usage: flick_kb_receiver [PORT] [IP (optional)]")
        sys.exit()
    elif(len(args)==2):
        port = int(args[1])
    else:
        port = int(args[1])
        ipaddr = args[2]

    # メイン処理
    receiver = Receiver(port=port, ipaddr=ipaddr)
    receiver.start_loop()
    while True:
        stopper = input()
        if(stopper=="s"):
            receiver.stop_loop()
            break
    receiver.close_sock()

if __name__=="__main__":
    main()