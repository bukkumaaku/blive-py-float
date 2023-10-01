cd "$(dirname "$0")"
$live=13233348
if [ -d "./venv/" ]; then
    echo "虚拟环境存在"
    source venv/bin/activate
    python main.py $live
else
   echo "虚拟环境不存在"
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   echo "安装环境结束"
   python main.py $live
fi