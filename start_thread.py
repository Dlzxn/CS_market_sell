import subprocess, sys, time, os

from src.db.CRUD import user_database


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

ENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")

def start():
    if not os.path.exists(ENV_PYTHON):
        print(f"❌ Ошибка: Интерпретатор не найден по пути: {ENV_PYTHON}", file=sys.stderr)
        print("Убедитесь, что виртуальное окружение (.venv) создано и активировано.", file=sys.stderr)
        sys.exit(1)


    all_id = user_database.get_all_id()
    proc_list = []
    for user_id, _ in all_id:
        check_file = open(f"data/app_check_{user_id}.log", 'w', encoding='utf-8')
        del_file = open(f"data/app_del_{user_id}.log", 'w', encoding='utf-8')
        proc_check = subprocess.Popen([ENV_PYTHON, "app_check.py", str(user_id)],
                         stdout=check_file,
                         stderr=check_file,)
        proc_del = subprocess.Popen([ENV_PYTHON, "app_del.py", str(user_id)],
                         stdout=del_file,
                         stderr=del_file
                         )
        proc_list.append((proc_check, proc_del))
    print(len(proc_list))
    time.sleep(5)
    for proc_check, proc_del in proc_list:
        proc_check.terminate()
        proc_del.terminate()
    start()

start()
