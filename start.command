cd "$(dirname "$0")"
room_id=7777
if [ -d "./venv/" ]; then
    echo "虚拟环境存在"
    source venv/bin/activate
    python main.py $room_id
else
   echo "虚拟环境不存在"
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   echo "安装环境结束"
   python main.py $room_id
fi