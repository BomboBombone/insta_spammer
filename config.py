import sys,os,time,random,subprocess,ast,codecs
import logging


LOGS_LINES = []
permanent_logger = None
temporary_logger = None
RUNNING_PROCESSES = []
ACCOUNTS_LIMIT = 3

def get_app_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        running_mode = 'Frozen/executable'
    else:
        try:
            application_path = os.path.realpath(__file__)
            application_path = os.path.dirname(application_path)
            running_mode = "Non-interactive (e.g. 'python myapp.py')"
        except NameError:
            application_path = application_path
            running_mode = 'Interactive'
    # application_path = os.path.join(application_path,'..')
    return application_path

def check_and_make():
    if not os.path.exists(os.path.join(get_app_path(),'config')):
        os.mkdir(os.path.join(get_app_path(),'config'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files')):
        os.mkdir(os.path.join(get_app_path(),'config','files'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','db')):
        os.mkdir(os.path.join(get_app_path(),'config','files','db'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','cores')):
        os.mkdir(os.path.join(get_app_path(),'config','files','cores'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','cores','data')):
        os.mkdir(os.path.join(get_app_path(),'config','files','cores','data'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','cores','user_notified_dir')):
        os.mkdir(os.path.join(get_app_path(),'config','files','cores','user_notified_dir'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','cores','followings_dir')):
        os.mkdir(os.path.join(get_app_path(),'config','files','cores','followings_dir'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','cores','followers_dir')):
        os.mkdir(os.path.join(get_app_path(),'config','files','cores','followers_dir'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','DMS')):
        os.mkdir(os.path.join(get_app_path(),'config','files','DMS'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','WELCOME_DMS')):
        os.mkdir(os.path.join(get_app_path(),'config','files','WELCOME_DMS'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','COMMENTS')):
        os.mkdir(os.path.join(get_app_path(),'config','files','COMMENTS'))
    # if not os.path.exists(os.path.join(get_app_path(),'config','logs')):
    #     os.mkdir(os.path.join(get_app_path(),'config','logs'))
    # if not os.path.exists(os.path.join(get_app_path(),'config','logs','log')):
    #     os.mkdir(os.path.join(get_app_path(),'config','logs','log'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','sessions')):
        os.mkdir(os.path.join(get_app_path(),'config','files','sessions'))
    if not os.path.exists(os.path.join(get_app_path(),'config','files','interactions')):
        os.mkdir(os.path.join(get_app_path(),'config','files','interactions'))

    
    if os.name == 'nt':
        path = os.path.join(os.path.expanduser(os.getenv('USERPROFILE')),'config')
        if not os.path.exists(path):
            os.mkdir(path)
    else:
        path = os.path.join(os.path.expanduser('~'),'config')
        if not os.path.exists(path):
            os.mkdir(path)

def readFile(file_path):
    data = []
    try:
        file = codecs.open(file_path,'r',encoding='utf-8-sig')
        for line in file.readlines():
            if bool(line.strip()):data.append(line.strip())
        file.close()
    except:
        codecs.open(file_path,'w',encoding='utf-8-sig').close()
    return data

def write_to_file(list_of_lines,file_path):
    file = codecs.open(file_path,'w',encoding='utf-8-sig')
    for line in list_of_lines:
        file.write(str(line)+"\n")
    file.close()

def random_sleep():
    time.sleep(random.randint(5,10))

def get_mac():
    if os.name == 'nt':
        cmd = 'wmic csproduct get uuid'
        uuid = str(subprocess.check_output(cmd))
        pos1 = uuid.find("\\n")+2
        uuid = uuid[pos1:-15]
        return uuid
    else:
        cmd = ['system_profiler', 'SPHardwareDataType', '|', 'awk', '/UUID/ {print $3}']
        uuid = str(subprocess.check_output(cmd))
        uuid = uuid[uuid.index("Hardware UUID: "):]
        uuid = uuid.replace("Hardware UUID: ",'').replace("\\n",'').replace("'",'')
        uuid = uuid.split(' ')[0].strip()
        return uuid.strip()

def read_json_object_from_txt_file(path):
    json_objs = []
    try:
        file = open(path,'r')
        for line in file.readlines():
            if bool(line.strip()): json_objs.append(ast.literal_eval(line.strip()))
        file.close()
        return json_objs
    except Exception as e:
        open(path,'w').close()
        return json_objs

def write_jsons_to_txt_file(path,json_objs):
    file = open(path,'w')
    for json_obj in json_objs:
        file.write(str(json_obj)+"\n")
    file.close()
    
def get_account_json(username):
    all_accounts = read_json_object_from_txt_file(accounts_file_path)
    for account in all_accounts:
        if account.get('username') == username:return account
    return None

def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter("* %(asctime)s - %(message)s","%Y-%m-%d %H:%M:%S")
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def print_me(msg):
    if '[+]' in msg:msg = msg.replace('[+]','')
    global permanent_logger,temporary_logger
    if not permanent_logger:
        permanent_logger = setup_logger('permanent_logger',os.path.join(get_app_path(),'config','files','cores','data','permanent_logs.log'))
    if not temporary_logger:
        temporary_logger = setup_logger('temporary_logs',os.path.join(get_app_path(),'config','files','cores','data','temporary_logs.log'))
    print(msg)
    permanent_logger.info(msg)
    temporary_logger.info(msg)

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print("")
    print("")

db_folder = os.path.join(get_app_path(),'config','files','db')
accounts_file_path = os.path.join(db_folder,'accounts.txt')
prefs_file_path = os.path.join(db_folder,'preferences.txt')
dms_folder_path = os.path.join(get_app_path(),'config','files','DMS')
welcome_dms_folder_path = os.path.join(get_app_path(),'config','files','WELCOME_DMS')
comments_folder_path = os.path.join(get_app_path(),'config','files','COMMENTS')
cores_folder_path = os.path.join(get_app_path(),'config','files','cores')
followings_folder_path = os.path.join(get_app_path(),'config','files','cores','followings_dir')
followers_folder_path = os.path.join(get_app_path(),'config','files','cores','followers_dir')
user_notified_folder_path = os.path.join(get_app_path(),'config','files','cores','user_notified_dir')
actions_file_path = os.path.join(get_app_path(),'config','files','db','actions.txt')
session_folder_path = os.path.join(get_app_path(),'config','files','sessions')
interactions_files_folder_path = os.path.join(get_app_path(),'config','files','interactions')





