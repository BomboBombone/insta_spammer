import eel,multiprocessing,sys,copy,psutil,os,threading,codecs,random
from script.bot import bot_driver
from script.license_tracker import licenseTracker
from config import *
from tkinter import filedialog
from tkinter import *
from datetime import datetime


is_bot_opened = False


@eel.expose
def get_file_path():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_selected = filedialog.askopenfilename()
    print(file_selected)
    return file_selected

########################################################
#~~~~~~~~~~~~~~~~~~~~~ EEL FUNTION js/python ~~~~~~~~~~~~~~~~~~~#
########################################################

@eel.expose
def get_connected_devices():
    return DEVICES

@eel.expose
def get_running_processes():
    alive_processes = []
    for running_process in RUNNING_PROCESSES:
        if running_process.is_alive() or 1:
            alive_processes.append(running_process.name)
    return alive_processes

@eel.expose
def is_process_already_running(process_name):
    processes = get_running_processes()
    for process in processes:
        if process == process_name:
            return True
    return False

def isSingleThreadAccountRunning():
    processes = get_running_processes()
    for process in processes:
        if ":single_thread" in process:
            return True
    return False

@eel.expose
def get_all_accounts():
    return read_json_object_from_txt_file(accounts_file_path)


def get_all_users_actions():
    return read_json_object_from_txt_file(actions_file_path)

def get_users_actions(username):
    all_user_actions = get_all_users_actions()
    for user_action_data in all_user_actions:
        if user_action_data.get('username') == username:
            return user_action_data
    return None

@eel.expose
def add_new_account(username,password,proxy=None):
    accounts = read_json_object_from_txt_file(accounts_file_path)
    for account in accounts:
        if account.get('username') == username:
            return False
    accounts.append({
        'username':username,
        'password':password,
        'proxy':proxy
    })
    write_jsons_to_txt_file(accounts_file_path,accounts)
    save_user_prefs(username,{
        'username':username,
        'target_hashtags':'',
        'target_usernames':'',
        "target_locations":'',
        "want_to_like":True,
        "want_to_follow":True,
        "want_to_comment":True,
        "want_to_dms":True,
        "want_to_unfollow":True,
        "want_to_welcome_dms":True,
        "like_per_hour":25,
        "follow_per_hour":25,
        "comment_per_hour":25,
        "dm_per_hour":25,
        "unfollow_per_hour":25,
        "welcome_dm_per_hour":40,
        "unfollow_after_x_days":2,
        'scheduled_posts': []
    })
    return True

@eel.expose
def is_account_limit_exceed():
    if len(get_all_accounts())>=ACCOUNTS_LIMIT:
        return True
    else:
        return False

@eel.expose
def delete_account(account_json_obj):
    accounts = get_all_accounts()
    try:
        accounts.remove(account_json_obj)
        write_jsons_to_txt_file(accounts_file_path,accounts)
        return True
    except:
        return False

@eel.expose
def get_user_prefs(username):
    all_prefs = read_json_object_from_txt_file(prefs_file_path)
    for pref in all_prefs:
        if pref.get('username') == username:
            return pref
    return None

@eel.expose
def get_all_account_prefs():
    return read_json_object_from_txt_file(prefs_file_path)

@eel.expose
def save_user_prefs(username,prefs_json):
    if username == 'all':
        try:
            all_prefs = read_json_object_from_txt_file(prefs_file_path)
            found = False
            for i in range(len(all_prefs)):
                currentUsername = all_prefs[i].get('username')
                # if all_prefs[i].get('username') == username:
                # found = True
                prefs_json['total_activity_hours'] = all_prefs[i]['total_activity_hours']
                prefs_json['scheduled_posts'] = all_prefs[i].get('scheduled_posts') if bool(all_prefs[i].get('scheduled_posts')) else []
                all_prefs[i] = copy.deepcopy(prefs_json)
                all_prefs[i]['username'] = currentUsername
            if not found:
                prefs_json['total_activity_hours'] = ""
                prefs_json['scheduled_posts'] = []
                all_prefs.append(prefs_json)
            write_jsons_to_txt_file(prefs_file_path,all_prefs)
            return True
        except:
            return False
    else:
        try:
            all_prefs = read_json_object_from_txt_file(prefs_file_path)
            found = False
            for i in range(len(all_prefs)):
                if all_prefs[i].get('username') == username:
                    found = True
                    prefs_json['total_activity_hours'] = all_prefs[i]['total_activity_hours']
                    prefs_json['scheduled_posts'] = all_prefs[i].get('scheduled_posts') if bool(all_prefs[i].get('scheduled_posts')) else []
                    all_prefs[i] = copy.deepcopy(prefs_json)
            if not found:
                prefs_json['total_activity_hours'] = ""
                prefs_json['scheduled_posts'] = []
                all_prefs.append(prefs_json)
            write_jsons_to_txt_file(prefs_file_path,all_prefs)
            return True
        except:
            return False

@eel.expose
def save_schedular_inputs(pref_json_list):
    try:
        write_jsons_to_txt_file(prefs_file_path,pref_json_list)
        return True
    except:
        return False

@eel.expose
def save_post_scheduling_data(username,post_path,caption,date):    # SCHEDULE POSTS TO UPLAOD ON INSTAGRAM
    if not caption:caption = ""
    all_prefs = get_all_account_prefs()
    for pref in all_prefs:
        if pref.get('username') == username:
            try:
                pref['scheduled_posts'].append({
                    "dated":date,
                    "image_path": post_path,
                    "caption":caption
                })
            except:
                pref['scheduled_posts'] = [{
                    "dated":date,
                    "image_path": post_path,
                    "caption":caption
                }]
    write_jsons_to_txt_file(prefs_file_path,all_prefs)
    return True

@eel.expose
def delete_post_scheduling_data(username,scheduled_post_entry):
    all_prefs = get_all_account_prefs()
    for pref in all_prefs:
        if pref.get('username') == username:
            try:
                pref['scheduled_posts'].remove(scheduled_post_entry)
            except:
                pass
    write_jsons_to_txt_file(prefs_file_path,all_prefs)
    return True


################################################################################################################
############################################### RUNNER / LAUNCHER / STOPPER ####################################
################################################################################################################



def is_action_are_done(username):
    actionsData = get_users_actions(username)
    if actionsData:
        for oneActionData in actionsData.get('data'):
            if datetime.strptime(oneActionData.get('date'),'%d-%m-%Y').date() == datetime.now().date():
                return False if len(oneActionData.get('users'))>0 else True
    return False

@eel.expose
def STOP_ACCOUNT(processName):
    global RUNNING_PROCESSES
    is_process_killed = False
    target_process = None
    for process in RUNNING_PROCESSES:
        try:
            if process.name == processName :
                # and process.is_alive()
                target_process = process
                # kill_process_by_extension(process.name)
                par_p = psutil.Process(process.pid)
                for child in par_p.children(recursive=True):child.kill()
                par_p.kill()
                # process.terminate()
                is_process_killed = True
                break
        except Exception as e:
            print("[!] Exception while killing process on line -> 202 "+str(e))
    if is_process_killed or 1:
        RUNNING_PROCESSES.pop(RUNNING_PROCESSES.index(target_process))
        print_me("[+] Killing Process => "+processName+" Succeed")
        return True
    else:
        print_me("[+] Prcess {} not found.".format(processName))
        return False


@eel.expose
def launch_one_account(username):
    prefs_json = get_user_prefs(username)
    process_name = prefs_json.get('username')+":single_thread"
    if is_process_already_running(process_name):
        eel.show_error("Account Already Running")
        return

    # check for comments/dms/welcome_dms 
    comment_file = os.path.join(comments_folder_path,username.replace('@','').replace('.','')+"_COMMENTS.txt") 
    dms_file = os.path.join(dms_folder_path,username.replace('@','').replace('.','')+"_DMS.txt") 
    welcome_dms_file = os.path.join(welcome_dms_folder_path,username.replace('@','').replace('.','')+"_WELCOME_DMS.txt") 
    if prefs_json.get('want_to_comment') and not bool(readFile(comment_file)):
        eel.show_error("'want to comment' Option is On, But The Comment List is Empty")
    elif prefs_json.get('want_to_dms') and not bool(readFile(dms_file)):
        eel.show_error("'want to dms' Option is On, But The Dms List is Empty")
    elif prefs_json.get('want_to_welcome_dms') and not bool(readFile(welcome_dms_file)):
        eel.show_error("'want to welcome dms' Option is On, But The welcome dms List is Empty")
    else:   #start account
        p = multiprocessing.Process(target=bot_driver,args=(prefs_json,),name=process_name)
        p.start()
        RUNNING_PROCESSES.append(p)
        eel.show_success("Account Up Successfully !")

@eel.expose
def launch():
    global RUNNING_PROCESSES
    # if os.name == 'nt':
    #     devices = ['localhost:5555','emulator-5554']
    #     # devices = ['localhost:5555','emulator-5554','emulator-5564','emulator-5574','emulator-5584']
    # else:
    #     devices = ['localhost:5555']

    # for device in devices:
    #     processname = device + " : process"
    #     if is_process_already_running(processname):
    #         print_me("'{}' already running.".format(processname))
    #         continue
    #     process = multiprocessing.Process(target=one_device_controller,args=(device,),name=processname)
    #     process.start()
    #     RUNNING_PROCESSES.append(process)


################################################################################################################
############################################### LOGGER ##########################################################
################################################################################################################

def log_shower():
    temporary_logs_file = os.path.join(get_app_path(),'config','files','cores','data','temporary_logs.log')
    while 1:
        lines = readFile(temporary_logs_file)
        # lines = readLinesFromFile(temporary_logs_file)
        if not bool(lines):continue
        linesText = '<br>'.join(lines)
        eel.print(linesText)
        open(temporary_logs_file,'w').close()
        time.sleep(4)

@eel.expose
def start_logger():
    t = threading.Thread(target=log_shower)
    t.daemon = True
    t.start()


# #########################################################################################################################################
# ###################################################### COMMENTS / DMS / WELCOMD DMS SETTER ##############################################
# #########################################################################################################################################

@eel.expose
def get_all_comments(user):
    comment_file_path = os.path.join(comments_folder_path,user.replace('@','').replace('.','') +'_COMMENTS.txt')
    try:
        file = codecs.open(comment_file_path,'r','utf-8-sig')
    except:
        file = codecs.open(comment_file_path,'w','utf-8-sig')
        file.close()
        return []
    DMS = []
    for line in file.readlines():
        DMS.append(line.strip())
    file.close()
    return DMS

@eel.expose
def add_new_comment(text,user):
    text = text.replace("\n","\\n")
    comment_file_path = os.path.join(comments_folder_path,user.replace('@','').replace('.','')+'_COMMENTS.txt')
    try:
        try:
            file = codecs.open(comment_file_path,'a','utf-8-sig')
        except:
            file = codecs.open(comment_file_path,'w','utf-8-sig')
        file.write(text+'\n')
        file.close()
        return True
    except:
        return False

@eel.expose
def delete_comment(dm,user):
    comment_file_path = os.path.join(comments_folder_path,user.replace('@','').replace('.','')+'_COMMENTS.txt')
    try:
        dms = get_all_comments(user)
        file = codecs.open(comment_file_path,'w','utf-8-sig')
        for DM in dms:
            if DM.lower() == dm.lower():
                continue 
            file.write(DM+"\n")
        file.close()
        return True
    except:
        return False

##############################


@eel.expose
def get_all_dms(user):
    dm_file_path = os.path.join(dms_folder_path,user.replace('@','').replace('.','')+'_DMS.txt')
    try:
        file = codecs.open(dm_file_path,'r','utf-8-sig',errors='replace')
    except:
        file = codecs.open(dm_file_path,'w','utf-8-sig')
        file.close()
        return []
    DMS = []
    for line in file.readlines():
        DMS.append(line.strip())
    file.close()
    return DMS

@eel.expose
def save_these_dms_for_all_accounts(username):
    dms = get_all_dms(username)
    for account in get_all_accounts():
        user_name = account.get('username')
        dm_file_path = os.path.join(dms_folder_path,user_name.replace('@','').replace('.','')+'_DMS.txt')
        write_jsons_to_txt_file(dm_file_path,dms)
    return True

@eel.expose
def add_new_dm(text,user):
    text = text.replace("\n","\\n")
    dm_file_path = os.path.join(dms_folder_path,user.replace('@','').replace('.','')+'_DMS.txt')
    try:
        try:
            file = codecs.open(dm_file_path,'a','utf-8-sig')
        except:
            file = codecs.open(dm_file_path,'w','utf-8-sig')
        file.write(text+'\n')
        file.close()
        return True
    except:
        return False

@eel.expose
def delete_dm(dm,user):
    dm_file_path = os.path.join(dms_folder_path,user.replace('@','').replace('.','')+'_DMS.txt')
    try:
        dms = get_all_dms(user)
        file = codecs.open(dm_file_path,'w','utf-8-sig')
        for DM in dms:
            if DM.lower() == dm.lower():
                continue 
            file.write(DM+"\n")
        file.close()
        return True
    except:
        return False

##############################


@eel.expose
def get_all_welcome_dms(user):
    welcome_dm_file_path = os.path.join(welcome_dms_folder_path,user.replace('@','').replace('.','')+'_WELCOME_DMS.txt')
    # dm_file_path = os.path.join(dms_folder_path,user+'_DMS.txt')
    try:
        file = codecs.open(welcome_dm_file_path,'r','utf-8-sig')
    except:
        file = codecs.open(welcome_dm_file_path,'w','utf-8-sig')
        file.close()
        return []
    DMS = []
    for line in file.readlines():
        DMS.append(line.strip())
    file.close()
    return DMS

@eel.expose
def add_new_welcome_dm(text,user):
    text = text.replace("\n","\\n")
    welcome_dm_file_path = os.path.join(welcome_dms_folder_path,user.replace('@','').replace('.','')+'_WELCOME_DMS.txt')
    try:
        try:
            file = codecs.open(welcome_dm_file_path,'a','utf-8-sig')
        except:
            file = codecs.open(welcome_dm_file_path,'w','utf-8-sig')
        file.write(text+'\n')
        file.close()
        return True
    except:
        return False

@eel.expose
def delete_welcome_dm(dm,user):
    welcome_dm_file_path = os.path.join(welcome_dms_folder_path,user.replace('@','').replace('.','')+'_WELCOME_DMS.txt')
    try:
        dms = get_all_welcome_dms(user)
        file = codecs.open(welcome_dm_file_path,'w','utf-8-sig')
        for DM in dms:
            if DM.lower() == dm.lower():
                continue 
            file.write(DM+"\n")
        file.close()
        return True
    except:
        return False


########################################################
#~~~~~~~~~~~~~~~~~~~~~ INDEX PAGE ~~~~~~~~~~~~~~~~~~~#
########################################################

def on_exit(x,y):
    pass

def open_bot():
    eel.init('web')
    # eel.start('index.html',size=(900, 1000),close_callback=on_exit(1,2))
    eel.start('index.html',size=(2000, 2000),close_callback=on_exit(1,2))
    while True:eel.sleep(20)

def show_expired_page():
    eel.init('web')
    eel.start('expired.html',size=(2000, 2000),close_callback=on_exit(1,2))
    while True:eel.sleep(20)

########################################################
#~~~~~~~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~~~~~#
########################################################

def read_special_user():
    name = ''
    filePath = os.path.join(get_app_path(),'config','files','cores','special_user.txt')
    try:
        file = open(filePath,'r')
        name = file.read().strip()
        file.close()
    except:
        open(filePath,'w').close()
    return name

if __name__ == "__main__":

    if os.name !='nt': os.system("source ~/.bash_profile")

    clear_screen()

    # some conf
    multiprocessing.freeze_support()
    if sys.platform == 'darwin':multiprocessing.set_start_method('spawn')

    # read special user
    # name = 'Drcasie_1_win_umer_tariq'
    name = 'haezel99_umer_tariq'
    if not name:
        print("\n\n[Error] Name Of User is not allocated.\n\n")
    else:
        # auth user
        license_tracker = licenseTracker()
        try:
            if license_tracker.authenticate_user(name,'New Insta Bot'): # if succeed then run the bot
                is_bot_opened = True
                check_and_make()
                open_bot()
            else:                                                        # Else Show error
                show_expired_page()
        except:
            if not is_bot_opened:
                print("Internet issue occur, please check your internet and try again.")
                if os.path.exists(os.path.join(get_app_path(),'config','files','cores','creds.json')): 
                    os.remove(os.path.join(get_app_path(),'config','files','cores','creds.json'))
                exit(1)

