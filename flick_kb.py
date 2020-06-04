"""
フリックキーボード（スマホ側）
iOSのPytoアプリ上で動作
"""
import sys
import socket
import pyto_ui as ui
import text_client as myclient

class MySender(myclient.Sender):
    """
    送信関係
    イベント関数を含む
    """
    def __init__(self, port, ipaddr, timeout=5.0):
        print(port, ipaddr)
        super().__init__(port, ipaddr, timeout)
        self.editflag = False
    
    def connect(self):
        try:
            super().connect()
            self.editflag = True
            print("connection")
        except socket.timeout:
            print("timed out")
            super().close()
            sys.exit()
    
    def send_text(self, text):
        self.send(text)
#        print(">", text)
    
    def send_end_flag(self):
        # アプリ終了をPCに伝えるフラグを送信
        if(self.editflag):
            self.send(b"\x00", enc=None)
            self.editflag = False
            
    def close(self):
        self.send_end_flag()
        super().close()
    
    def did_end_editing(self, sender):
        if(self.editflag):
            if sender.text == " ":
                self.send(b"\x0a", enc=None)  # enter
                sender.text = " "
            elif sender.text == "":
                self.send(b"\x08", enc=None)  # backspace
            else:
                self.send_text(sender.text[1:])  # 前のスペースを省いてテキスト送信
                sender.text = " "
    
        sender.superview["text_field1"].become_first_responder()  # テキストボックスからフォーカスが外れないようにする
    
    def did_change_text(self, sender):
        if sender.text == "":
            sender.text = " "  # バックスペース検知用
            self.send(b"\x08", enc=None)  # backspace       

def main():
    args = sys.argv
    if(len(args)<=2):
        print("Input arguments. [PORT] [IP Address]")
        sys.exit()
    else:
        port = int(args[1])
        ipaddr = args[2]
    
    # 送信部
    print("start connection...")
    mysender = MySender(port=port, ipaddr=ipaddr, timeout=5.0)
    mysender.connect()
    
    # GUI部
    view = ui.View()
    view.background_color = ui.COLOR_SYSTEM_BACKGROUND
    
    text_field = ui.TextField(placeholder="Back Space")
    text_field.name = "text_field1"
    text_field.text = " "
    text_field.become_first_responder()
    text_field.action = mysender.did_change_text
    text_field.did_end_editing = mysender.did_end_editing
    text_field.return_key_type = ui.RETURN_KEY_TYPE_DONE
    text_field.width = 300
    text_field.center = (view.width/2, view.height/2)
    text_field.flex = [
        ui.FLEXIBLE_BOTTOM_MARGIN,
        ui.FLEXIBLE_TOP_MARGIN,
        ui.FLEXIBLE_LEFT_MARGIN,
        ui.FLEXIBLE_RIGHT_MARGIN
    ]
    view.add_subview(text_field)
    
    ui.show_view(view, ui.PRESENTATION_MODE_SHEET)
    
    # 終了処理
    mysender.close()
    print("end")

if __name__=="__main__":
    main()