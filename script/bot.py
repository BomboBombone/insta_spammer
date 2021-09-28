import time,random,os,sys,ast,requests,copy,multiprocessing,threading,uuid,shutil,pickle
from tqdm import tqdm
from datetime import datetime,timedelta
from config import *
from instagrapi import Client
from instagrapi.types import Media as BotMediaClass
from PIL import Image
import traceback

def get_user_prefs(username):
    all_prefs = read_json_object_from_txt_file(prefs_file_path)
    for pref in all_prefs:
        if pref.get('username') == username:
            return pref
    return None

def update_user_prefs(username,updated_scheduling_data):
    all_prefs = read_json_object_from_txt_file(prefs_file_path)
    for pref in all_prefs:
        if pref.get('username') == username:
            pref['scheduled_posts'] = copy.deepcopy(updated_scheduling_data)
            break
    write_jsons_to_txt_file(prefs_file_path,all_prefs)

def get_all_users_actions():
    return read_json_object_from_txt_file(actions_file_path)

def get_users_actions(username):
    all_user_actions = get_all_users_actions()
    for user_action_data in all_user_actions:
        if user_action_data.get('username') == username:
            return user_action_data
    return None

def get_all_done_users():
    all_users_actions = get_all_users_actions()
    done_users = []
    for one_user_action in all_users_actions:
        for data in one_user_action.get('data'):
            done_users += data.get('done')
    return done_users

def random_sleep(st=2,end=3):
    time.sleep(random.randint(st,end))

class IntreactionData:

    def __init__(self):
        self.data = []
        self.dated = datetime.now().date()
        self.actions_dict = {
            'likes': 0,
            'comments': 0,
            'follows': 0,
            'unfollows': 0,
            'dms': 0,
            'welcome_dms': 0,
            'stories': 0

        }

    def insert_media(self,mediaObj):
        self.data.append(mediaObj)
    
    def insert_user(self,userId):
        self.data.append(userId)
    
class BOT:

    def __init__(
                    self,username,password,proxy=None,
                    target_usernames=[],target_locations=[],target_hashtags=[],
                    want_to_like_post=False,want_to_comment_on_post=False,want_to_follow_user=False,want_to_unfollow_user=False,want_to_send_dm=False,want_to_send_welcome_dm=True,want_to_restart_session=False,want_to_upload_scheduled_posts=False,want_to_watch_stories=False,
                    skip_private_accounts=False,skip_users_with_no_profile_pic=False,skip_business_account=False,
                    DMS=[],COMMENTS=[],WELCOME_DMS=[],
                    server_host='127.0.0.1',server_port=5037,
                    sleep_time_after_like=random.randint(5,10),
                    sleep_time_after_comment=random.randint(10,15),
                    sleep_time_after_dm=random.randint(10,15),
                    sleep_time_after_follow=random.randint(5,10),
                    sleep_time_after_unfollow=random.randint(5,10),
                    my_followers_file=None,following_file_path=None,notified_user_file_path=None,user_info_file_path=None,
                    session_file_path=None,
                    likes_per_hour=20,comments_per_hour=20,follows_per_hour=20,unfollows_per_hour=20,dms_per_hour=20,welcome_dms_per_hour=20,stories_per_hour=20,
                    unfollow_after_x_days=2,restart_session_after_x_hours=2,
                    repost_hashtags=[],total_posts_to_reposts=1,
                    post_scheduling_data=[]
                ):
        self.username = username
        self.password = password
        self.proxy = proxy
        self.server_host = server_host
        self.server_port = server_port
        self.target_usernames = target_usernames
        self.target_locations = target_locations
        self.target_hashtags = target_hashtags
        self.want_to_like_post = want_to_like_post
        self.want_to_comment_on_post = want_to_comment_on_post
        self.want_to_upload_scheduled_posts = want_to_upload_scheduled_posts
        self.want_to_follow_user = want_to_follow_user
        self.want_to_unfollow_user = want_to_unfollow_user
        self.want_to_send_dm = want_to_send_dm
        self.want_to_watch_stories = want_to_watch_stories
        self.want_to_send_welcome_dm = want_to_send_welcome_dm
        self.want_to_restart_session=want_to_restart_session
        self.skip_private_accounts = skip_private_accounts
        self.skip_users_with_no_profile_pic = skip_users_with_no_profile_pic
        self.skip_business_account = skip_business_account
        self.DMS = DMS
        self.COMMENTS = COMMENTS
        self.WELCOME_DMS = WELCOME_DMS
        self.sleep_time_after_like = random.randint(120,180) #3600/likes_per_hour
        self.sleep_time_after_comment = random.randint(120,180) #3600/comments_per_hour
        self.sleep_time_after_dm = random.randint(180,210) #3600/dms_per_hour
        self.sleep_time_after_follow = random.randint(120,180) #3600/follows_per_hour
        self.sleep_time_after_unfollow = random.randint(120,180) #3600/unfollows_per_hour
        self.sleep_time_after_welcome_dm = random.randint(180,210) #3600/welcome_dms_per_hour
        self.my_followers_file = my_followers_file
        self.following_file_path = following_file_path
        self.notified_user_file_path = notified_user_file_path
        self.user_info_file_path=user_info_file_path
        self.session_file_path = session_file_path
        self.my_id = None
        self.unfollow_after_x_days=unfollow_after_x_days
        self.likes_per_hour = likes_per_hour
        self.comments_per_hour = comments_per_hour
        self.follows_per_hour = follows_per_hour
        self.unfollows_per_hour = unfollows_per_hour
        self.dms_per_hour = dms_per_hour
        self.stories_per_hour = stories_per_hour
        self.welcome_dms_per_hour = welcome_dms_per_hour
        self.my_followers = []
        self.restart_session_after_x_hours = restart_session_after_x_hours
        # self.bot_2 = request_bot(username,password)
        self.CURRENT_USERS_FOR_ACTIONS = []
        self.target_user_followers_done = 0
        self.target_user_followers_limit = random.randint(50,80)
        self.repost_hashtags=repost_hashtags
        self.total_posts_to_reposts=total_posts_to_reposts
        self.post_scheduling_data = post_scheduling_data
        self.client = None
        self.is_login = False
        self.interaction_data = None
        self.operations = 0
        self.total_operations = random.randint(100,150)

    def print_me(self,msg):
        msg = "[*{}*] : {}".format(self.username,msg)
        print_me(msg)
        # print(msg)

    def do_sleep(self,action,customSleep=0):
        
        if customSleep != 0:
            self.print_me("** Sleep for {}".format(customSleep))
            time.sleep(customSleep)
            return

        # self.open_home_screen_of_insta_app()
        if action == 'like':
            time.sleep(self.sleep_time_after_like)
        elif action == 'comment':
            time.sleep(self.sleep_time_after_comment)
        elif action == 'dm':
            time.sleep(self.sleep_time_after_dm)
        elif action == 'follow':
            time.sleep(self.sleep_time_after_follow)
        elif action == 'unfollow':
            time.sleep(self.sleep_time_after_unfollow)
        elif action == 'welcome_dm':
            time.sleep(self.sleep_time_after_welcome_dm)
        else:
            time.sleep(random.randint(20,25))

    ################## DM / COMMENT / MSG

    def get_random_dm(self):
        return self.DMS[random.randint(0,len(self.DMS)-1)]

    def get_random_comment(self):
        return self.COMMENTS[random.randint(0,len(self.COMMENTS)-1)]

    def get_random_welcome_dm(self):
        return self.WELCOME_DMS[random.randint(0,len(self.WELCOME_DMS)-1)]

    ################## GET HASHTAG USERS /  LOCATION USERS / USER FOLLOWERS

    def do_login(self):
        self.print_me("Login with account ->  "+self.username)

        if self.proxy:
            self.print_me("Login with proxy ->  "+self.proxy)
            self.client = Client(proxy=self.proxy)
        else:
            self.print_me("Login without proxy ")
            self.client = Client()
        try:
            if os.path.exists(self.session_file_path):
                self.client.load_settings(self.session_file_path)
                self.is_login = self.client.login(self.username, self.password)
                self.my_id = self.client.user_id_from_username(self.username)
            else:
                self.is_login = self.client.login(self.username, self.password)
                self.client.dump_settings(self.session_file_path)
                self.my_id = self.client.user_id_from_username(self.username)
            self.client.request_timeout = 30
            self.print_me("** Login Successfullt !")
        except Exception as e:
            print(e)
            self.print_me("Error While Login, " + str(e))

    ######################## 
    ######################## Getters
    ######################## 

    def get_my_followers(self):
        followers = []
        try:
            file = open(self.my_followers_file,'r')
            for line in file.readlines():
                try:
                    if not line.strip():continue
                    followers.append(line.strip())
                except:pass
        except:
            open(self.my_followers_file,'w').close()
        if not bool(followers):
            self.print_me(" ~~~ > Fetching Followers from Api ......." )
            if not self.my_id:
                self.my_id = self.client.user_id_from_username(self.username)

            # self.client.user_followers_v1()
            # self.client.user_followers()
            followers = self.client.user_followers_v1(self.my_id)
            file = open(self.my_followers_file,'w')
            for foll in followers:
                file.write( str(foll.pk) + "\n" )
            file.close()
        else:
            self.print_me(" ~~~ > Fetching Followers from file ......." )
            info_dict = self.client.user_info_by_username(self.username).dict()
            now_followers_count,now_following_count = info_dict.get('follower_count'),info_dict.get('following_count')
            if len(followers) < now_followers_count:
                self.print_me("==> checking and fetching new 100's")
                first_100 = self.client.user_followers_v1(self.my_id,amount=100)
                try:
                    first_100 = [f.pk for f in first_100]
                except:
                    pass
                followers = list(set(first_100) - set(followers))
                # followers = list(set(followers) | set(first_100))
                file = open(self.my_followers_file,'w')
                for foll in followers:
                    file.write(str(foll)+"\n")
                file.close()
        return followers

    def get_top_hashtag_medias(self,hashtag,amount=100):
        hashtag = hashtag.replace('#','')
        medias = self.client.hashtag_medias_v1(hashtag,amount=amount,tab_key='top')
        return medias

    def get_most_recent_hashtag_medias(self,hashtag,amount=100):
        hashtag = hashtag.replace('#','')
        medias = self.client.hashtag_medias_v1(hashtag,amount=amount,tab_key='recent')
        return medias
    
    def get_top_location_medias(self,hashtag,amount=100):
        hashtag = hashtag.replace('#','')
        # medias = self.client.hashtag_medias_top(location,amount=amount)
        # return medias

    def get_most_recent_location_medias(self,location,amount=100):
        hashtag = hashtag.replace('#','')
        # medias = self.client.hashtag_medias_recent(hashtag,amount=amount)
        # return medias
    
    def get_user_medias(self,user_id,amount=0):
        if amount == 0: #fetch all
            medias = self.client.user_medias(user_id)
        else:
            medias = self.client.user_medias(user_id,amount=amount)
        return medias

    def get_user_followers(self,user_id,amount=0):
        if amount == 0:
            target_user_followers = self.client.user_followers_v1(user_id)
        else:
            target_user_followers = self.client.user_followers_v1(user_id,amount=amount)
        return target_user_followers


    ######################## ######################## 
    ######################## ######################## 
    ######################## ######################## 

    def read_following_with_dates(self):
        try:
            file = open(self.following_file_path,'r')
        except:
            file = open(self.following_file_path,'w')
            file.close()
            return []
        my_following = []
        for line in file.readlines():
            my_following.append(ast.literal_eval(line.strip()))
        return my_following

    def get_intruder_followings(self):
        following = self.read_following_with_dates()
        if not following:return []
        intruders_folowing = []
        date_format = "%d/%m/%Y"
        today_date = datetime.strptime(datetime.today().strftime('%d/%m/%Y'), date_format)
        for foll in following:
            foll_date = foll['date']
            user_id = foll['user_id']
            foll_date = datetime.strptime(foll_date, date_format)
            delta = today_date - foll_date
            diff = delta.days
            print(diff,self.unfollow_after_x_days)
            if diff>=self.unfollow_after_x_days:
                intruders_folowing.append(user_id)
        return intruders_folowing

    def update_following_file(self,foll_users):
        all_foll = self.read_following_with_dates()
        try:
            file = open(self.following_file_path,'w')
            for foll in all_foll:
                if foll['user_id'] in foll_users:
                    continue
                else:
                    data = str(foll)
                    file.write(data+"\n")
            file.close()
        except Exception as e:
            self.print_me(str(e))

    def save_this_user_to_following_file(self,user_id):
        today_date = datetime.today().strftime('%d/%m/%Y')
        one_data = {'user_id':user_id,'date':today_date}
        try:
            file = open(self.following_file_path,'a')
        except Exception as e:
            file = open(self.following_file_path,'w')
        data = str(one_data)
        file.write(data+"\n")
        file.close()


    ########################################################################################################
    ###############################################   ACTIONS     ##########################################
    ########################################################################################################

    def send_dm(self,dmText,user_id):
        res = self.client.direct_send(dmText,[user_id])
        return res

    def do_follow(self,user_id,update_file=True):
        res = self.client.user_follow(user_id)
        if res and update_file:
            self.save_this_user_to_following_file(user_id)
        return res
    
    def do_unfollow_user(self,user_id,update_file=True):
        res = self.client.user_unfollow(user_id)
        if res and update_file:
            self.update_following_file([user_id])
        return res

    def do_like(self,media_id):
        res = self.client.media_like(media_id)
        return res

    def do_comment(self,commentText,media_id):
        res = self.client.media_comment(media_id,commentText)
        return res

    def watch_story(self,user_id):
        try:
            userStories = self.client.user_stories_v1(user_id)
            if not userStories:
                self.print_me("User has no stories.")
                return False
            return self.client.story_seen([s.pk for s in userStories])
        except Exception as e:
            print(e)
        return False


    ########################################################################################################
    ########################################################################################################

    def update_interaction_file(self,popedObj,success_dict):
        interactionsFilePath = os.path.join(interactions_files_folder_path, "{}_{}.pkl".format(self.username.replace('.',''),datetime.now().date().strftime('%d-%m-%Y') ))
        if success_dict.get('like'): self.interaction_data.actions_dict['likes'] += 1
        if success_dict.get('comment'): self.interaction_data.actions_dict['comments'] += 1
        if success_dict.get('dm'): self.interaction_data.actions_dict['dms'] += 1
        if success_dict.get('unfollow'): self.interaction_data.actions_dict['unfollows'] += 1
        if success_dict.get('follow'): self.interaction_data.actions_dict['follows'] += 1
        if success_dict.get('welcome_dm'): self.interaction_data.actions_dict['welcome_dms'] += 1
        if success_dict.get('story'): self.interaction_data.actions_dict['stories'] += 1

        with open(interactionsFilePath,'wb') as f:
            pickle.dump(self.interaction_data,f)
        print("[{}] Interactions file updated.".format(self.username))

    def today_posts_are_done(self,posts_per_day):
        # medias = self.my_bot.get_user_medias(self.my_id,filtration=False)
        medias = self.bot_2.get_user_medias(self.username,self.total_posts_to_reposts)
        try:
            medias = medias[:posts_per_day]
        except:
            return False
        if len(medias)<posts_per_day:
            return False
        today_date = datetime.now().date()
        all_done = True
        p_ind = 0
        for post in medias:
            # info = self.my_bot.get_media_info(post)[0]
            try:
                tym = post['caption']['created_at']
            except:
                tym = post['taken_at']
            post_date = datetime.fromtimestamp(tym).date()
            if p_ind == 0 and post_date == today_date and posts_per_day == 1:
                return True
            if post_date != today_date:
                all_done = False
                break
            p_ind += 1
        return all_done

    def get_image_name(self,media_info):

        rawImgLink = media_info.get('image_versions2').get('candidates')[0].get('url')
        postCode = media_info.get('code')
        owner_id = media_info.get('user').get('pk')
        owner_username = media_info.get('user').get('username')

        return os.path.join(get_app_path(),'config','posts', postCode+".png"),rawImgLink,owner_id,owner_username

    def DownloadSingleFile(self,postLink,file_path):
        self.print_me('Downloading image...')
        response = requests.get(postLink, stream=True)
        out_file = open(file_path, 'wb')
        shutil.copyfileobj(response.raw, out_file)
        self.print_me('[+] Done. Image saved to "posts" folder as ' + file_path)

    def get_photo(self,hashtags):
        # hashtags = hashtags.split(",")
        ALL_MEDIAS = []
        for i in range(10):random.shuffle(hashtags)
        if len(hashtags)>=1:
            hashtags = random.sample(hashtags,1)
        for hashtag in hashtags:
            ALL_MEDIAS+=self.bot_2.get_hashtag_medias(hashtag,30)
            # ALL_MEDIAS+=self.my_bot.get_hashtag_medias(hashtag.replace('#',''),filtration=False)

        folder = os.path.join(get_app_path(),'config','posts')
        try:
            media = ALL_MEDIAS[random.randint(0,len(ALL_MEDIAS)-1)]
            localPostPath,postRawLink,owner_id,owner_username = self.get_image_name(media)        
            self.DownloadSingleFile(postRawLink,localPostPath)
        except:
            localPostPath = "asdqjdhqkjwehqkwhekqjwe"

        while not os.path.exists(localPostPath):
            try:
                media = ALL_MEDIAS[random.randint(0,len(ALL_MEDIAS)-1)]
                localPostPath,postRawLink,owner_id,owner_username = self.get_image_name(media)
                # link = self.my_bot.get_link_from_media_id(media)
                self.print_me("[+] Downloading Image '{}' in 'posts' folder. ".format(localPostPath))
                self.DownloadSingleFile(postRawLink,localPostPath)
            except Exception as e:
                print(e)
        post_name = os.path.basename(localPostPath)
        androidPostPath = "./sdcard/Download/"+post_name
        _ = os.system("adb -s localhost:5555 push {} {}".format(localPostPath,androidPostPath))
        return localPostPath,androidPostPath,media,owner_id,owner_username

    def uploadPost(self,androidPostPath,caption):
        self.print_me("[+] Uploading Post -> "+androidPostPath)
        try:
            post_name = os.path.basename(androidPostPath)
            campatible_path =  "file:///storage/emulated/0/Download/" + post_name
            res = self.my_device.shell("am start -a android.intent.action.SEND -t image/png  --eu android.intent.extra.STREAM '{}' com.instagram.android/com.instagram.share.handleractivity.ShareHandlerActivity".format(campatible_path))
            time.sleep(5)
            self.my_device(resourceId="com.instagram.android:id/save").click()
            time.sleep(2)
            self.my_device(resourceId="com.instagram.android:id/next_button_imageview").click()
            time.sleep(1)
            self.my_device(resourceId="com.instagram.android:id/caption_text_view").set_text(caption)
            time.sleep(1)
            self.my_device(resourceId="com.instagram.android:id/next_button_imageview").click()
            time.sleep(5)
            self.my_device.shell("rm -rf {}".format(androidPostPath))
            return True
        except Exception as e:
            self.print_me(str(e))
            return False

    def do_repost(self):
        iter = 0
        while not self.today_posts_are_done(self.total_posts_to_reposts):
            if iter > 5: break
            try:
                local_post_path,androidPostPath,media_info_dict,owner_id,owner_username = self.get_photo(self.repost_hashtags)
                if local_post_path:
                    self.print_me("[+] SELECTED PHOTO {} FOR POST UPLOAD".format(local_post_path))
                    caption = "\nPc: @{}".format(owner_username)
                    res = self.uploadPost(androidPostPath,caption)
                    if res:
                        self.print_me("[+] POST UPLOADED SUCCESSFULLY ")
                        os.remove(local_post_path)
                        time.sleep(random.randint(8,15))
                    else:
                        os.remove(local_post_path)
                        self.print_me("[+] POST UPLOADED FAILED ")
                    time.sleep(random.randint(8,15))
                else:
                    self.print_me("[+] NO .png IMAGE FOUND IN POST FOLDER ")
            except Exception as e:
                self.print_me(str(e))
                time.sleep(random.randint(8,15))
            iter += 1

    def resize(self,image_pil):
        '''
        Resize PIL image keeping ratio and using white background.
        '''
        image_pil = (Image.open(image_pil, 'r')) #Usar a diretoria como stuff
        width = 1000
        height = 1000
        ratio_w = width / image_pil.width
        ratio_h = height / image_pil.height
        if ratio_w < ratio_h:
        # It must be fixed by width
            resize_width = width
            resize_height = round(ratio_w * image_pil.height)
        else:
        # Fixed by height
            resize_width = round(ratio_h * image_pil.width)
            resize_height = height
        image_resize = image_pil.resize((resize_width, resize_height), Image.ANTIALIAS)
        background = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        offset = (round((width - resize_width) / 2), round((height - resize_height) / 2))
        background.paste(image_resize, offset)
        return background.convert('RGB')

    def upload_scheduled_post(self):
        self.post_scheduling_data = get_user_prefs(self.username).get('scheduled_posts')
        _ = self.client.get_timeline_feed()

        for post in self.post_scheduling_data:
            localPostPath = post.get('image_path')
            caption = post.get('caption')
            if not caption:caption = ""
            postDate = datetime.strptime(post.get('dated'),'%Y-%m-%d').date()
            current_date = datetime.now().date()

            if postDate == current_date:
                try:
                    res = self.client.photo_upload(localPostPath,caption=caption)
                except:
                    _ = self.resize(localPostPath)
                    _.save(localPostPath)
                    res = self.client.photo_upload(localPostPath,caption=caption)
                if res:
                    self.post_scheduling_data.remove(post)
                    update_user_prefs(self.username,self.post_scheduling_data)
                    os.remove(localPostPath)
                    self.print_me("[+] POST UPLOADED SUCCESSFULLY ")
                    self.operations += 1
                    time.sleep(2*60)
                    return
                else:
                    self.print_me("[+] POST UPLOADED FAILED ")

                time.sleep(random.randint(8,15))

    def is_limit_reached_for_action(self, actionName):
        today_date_string_format = datetime.now().date().strftime("%d-%m-%Y")
        actions = get_users_actions(self.username)
        limit_reached = False
        if actions:
            for data in actions.get('data'):
                if data.get('date') == today_date_string_format:
                    if actionName == "follow":
                        return data.get('actions_history').get(actionName) >= self.follows_per_day
                    elif actionName == "unfollow":
                        return data.get('actions_history').get(actionName) >= self.unfollows_per_day
                    elif actionName == "like":
                        return data.get('actions_history').get(actionName) >= self.likes_per_day
                    elif actionName == "comment":
                        return data.get('actions_history').get(actionName) >= self.comments_per_day
                    elif actionName == "dm":
                        return data.get('actions_history').get(actionName) >= self.dms_per_day

    ########################################################################################################
    ########################################################################################################

    def do_actions_on_current_users(self,do_like=False,do_comment=False,do_dm=False,do_follow=False,do_unfollow=False,do_welcome_dm=False,do_watch_story=False):

        while self.interaction_data.data:

            if self.operations >=self.total_operations:break

            if self.operations !=0 and self.operations % 30 == 0:
                break

            popedObj = self.interaction_data.data.pop()

            if isinstance(popedObj,int):
                self.print_me("** Object is User id.")
                user_id = popedObj
                user_info = self.client.user_info(user_id).dict()       # .username .is_private .media_count .follower_count .following_count 
            elif isinstance(popedObj,BotMediaClass):
                self.print_me("** Object is MediaObj.")
                user_media = popedObj
                user_id = user_media.user.pk
                user_info = self.client.user_info(user_id).dict()       # .username .is_private .media_count .follower_count .following_count 
            else:
                self.print_me("** Object Type is story")
                user_id = popedObj.pk
                user_info = self.client.user_info(user_id).dict()       # .username .is_private .media_count .follower_count .following_count 
                

            if do_like or do_comment :
                try:
                    user_media = self.get_user_medias(user_id,amount=1)[0]
                except:
                    user_media = None
            else:
                user_media = None



            user_name = user_info.get('username')
            is_private = user_info.get('is_private')
            total_posts = user_info.get('media_count')
            follower_count = user_info.get('follower_count')
            following_count = user_info.get('following_count')

            self.print_me("Performing Actions On User -> @"+str(user_name))

            success_dict = {
                'like': False,
                'comment': False,
                'dm': False,
                'unfollow': False,
                'follow': False,
                'welcome_dm': False,
                'story': False
            }

            if self.skip_private_accounts and is_private:
                self.print_me("Skipping User '{}' cause of Privavte account".format(user_name))
                time.sleep(2)
                continue

            if do_watch_story:
                self.print_me("** Watching Stories of User -> "+user_name)
                random_sleep()
                res = self.watch_story(user_id)
                if res:
                    self.print_me("** Story Watched Successfully.")
                    success_dict['story'] = True
                    self.do_sleep('',customSleep=random.randint(15,25))
                else:
                    self.print_me("** Story operation not fulfilled.")
                    self.do_sleep('',customSleep=random.randint(5,10))

            if do_follow :
                self.print_me("** Following User -> "+user_name)
                random_sleep()
                res = self.do_follow(user_id)
                if res:
                    self.print_me("** User followed successfully.")
                    success_dict['follow'] = True
                    self.do_sleep('',customSleep=random.randint(120,180))
                else:
                    self.print_me("** follow operation not fulfilled.")
                    self.do_sleep('',customSleep=random.randint(10,30))

                
            if do_like and not is_private and user_media :
                self.print_me("Liking User '{}' Post".format(user_name))
                random_sleep()
                res = self.do_like(user_media.pk)
                if res:
                    self.print_me("** User Post Liked Successfuly!")
                    success_dict['like'] = True
                    self.do_sleep('',customSleep=random.randint(120,180))
                else:
                    self.print_me("** Like operation not fulfilled.")
                    self.do_sleep('',customSleep=random.randint(10,30))


            # if do_dm:
            #     self.print_me("Sending Dm to User '{}'.".format(user_name))
            #     random_sleep()
            #     dmText = self.get_random_dm()
            #     res = self.send_dm(dmText,user_id)
            #     if res:
            #         self.print_me("** Dm Sent Successfuly!")
            #         success_dict['dm'] = True
            #         self.do_sleep('',customSleep=random.randint(180,210))
            #     else:
            #         self.print_me("** Dm operation not fulfilled.")
            #         self.do_sleep('',customSleep=random.randint(10,30))


            # if do_comment and not is_private and user_media:
            #     self.print_me("Commenting on User '{}' post.".format(user_name))
            #     random_sleep()
            #     commentText = self.get_random_comment()
            #     res = self.do_comment(commentText,user_media.pk)
            #     if res:
            #         self.print_me("** Comment Sent Successfuly!")
            #         success_dict['comment'] = True
            #         self.do_sleep('',customSleep=random.randint(130,180))
            #     else:
            #         self.print_me("** Comment operation not fulfilled.")
            #         self.do_sleep('',customSleep=random.randint(10,20))

            if any(success_dict.values()) or 1:self.update_interaction_file(popedObj,success_dict)

            self.operations += 1

            # if self.operations % 10 == 0 and self.operations != 0:
                # self.upload_scheduled_post()

            random_sleep()

    def unfollow_non_followers(self):
        self.print_me("Initiating Unfollow non followers")
        intruderUsers = self.get_intruder_followings()
        for intruderUser in intruderUsers:
            self.print_me("** Unfollowing user -> {}.".format(intruderUser))
            res = self.do_unfollow_user(intruderUser)
            if res:
                self.print_me("User unfollowed successfully.")
                self.do_sleep('',customSleep=random.randint(120,180))
            else:
                self.print_me("Unfollow Operation failed.")
                self.do_sleep('',customSleep=random.randint(10,30))

    def send_welcome_dms(self):
        if not self.my_followers:self.my_followers = self.get_my_followers()
        self.print_me("Lets Check New Followers, and Do them Welcome DM.")
        time.sleep(3)
        all_followers = [foll for foll in self.my_followers]
        notified_users = readFile(self.notified_user_file_path)
        if not notified_users:
            write_to_file(all_followers,self.notified_user_file_path)
            self.print_me((
                            "[info] All followers saved in file {users_path}.\n"
                            "In a next time, for all new followers "
                            "script will send messages."
                            ).format(
                                users_path=self.notified_user_file_path
                        )
                    )
            time.sleep(4)
        else:
            self.print_me("[info] Read saved list of notified users. Count: {count}".format(count=len(notified_users)))
            time.sleep(3)
            self.print_me("[info] Amount of all followers is {count}".format(count=len(all_followers)))
            time.sleep(3)
            new_followers = set(all_followers) - set(notified_users)
            if not new_followers:
                self.print_me("[info] No New followers found")
            else:
                self.print_me("[info] Found new followers. Count: {count}".format(count=len(new_followers)))
                time.sleep(5)
                for follower in new_followers:
                    # self.print_me("Sending welcome dm to User -> "+str(follower))
                    time.sleep(3)
                    dm = self.get_random_welcome_dm()
                    self.print_me("Sending Welcome Dm to User '{}'".format(follower))
                    res = self.send_dm(dm,follower)
                    if res.id:
                        self.print_me("Welcome Dm Sent Successfully.")
                        notified_users.append(follower)
                        write_to_file(notified_users,self.notified_user_file_path)
                    else:
                        print(res)

                    self.do_sleep('welcome_dm')


    ########################################################################################################
    ########################################################################################################

    def load_interactions(self):
        interactionsFilePath = os.path.join(interactions_files_folder_path, "{}_{}.pkl".format(self.username.replace('.',''),datetime.now().date().strftime('%d-%m-%Y') ))
        if os.path.exists(interactionsFilePath):
            self.print_me("** interaction file found for today. Lets load it.")
            with open(interactionsFilePath,'rb') as f:
                self.interaction_data =  pickle.load(f)
        else:
            self.print_me("** interaction file not found for today. Lets fetch and create it.")
            self.interaction_data = IntreactionData()
            # 1 fetch users from target user followers
            if len(self.target_usernames)>2:
                targetUsers = random.sample(self.target_usernames,2)
            else:
                targetUsers = copy.copy(self.target_usernames)
            for user in targetUsers:
                self.print_me("** Fetching followers of {} ".format(user))
                user = user.replace('@','')
                user_id = self.client.user_id_from_username(user)
                target_user_followers = self.get_user_followers(user_id,amount=int(100/len(targetUsers)) )
                # target_user_followers = self.client.user_followers(user_id,amount=int(100/len(targetUsers)))
                for user_id in target_user_followers:self.interaction_data.insert_user(user_id)
            
            # 2 fetch users from target hashtags
            if len(self.target_hashtags)>2:
                targetHashtags = random.sample(self.target_hashtags,2)
            else:
                targetHashtags = copy.copy(self.target_hashtags)
            for hashtag in targetHashtags:
                self.print_me("** Fetching medias from hashtag {} ".format(hashtag))
                target_hashtag_data = self.get_most_recent_hashtag_medias(hashtag,amount=int(100/len(targetHashtags)))
                print(len(target_hashtag_data))
                for mediaObj in target_hashtag_data:self.interaction_data.insert_media(mediaObj)
            
            ## 3 fetch users from target locations
            # if len(self.target_locations)>2:
            #     targetLocations = random.sample(self.target_locations,2)
            # else:
            #     targetLocations = copy.copy(self.target_locations)
            # for location in targetLocations:
            #     target_location_users = self.bot_2.get_location_users(location,total=200,excluded_users=get_all_done_users())
            #     data_for_action += target_location_users
            with open(interactionsFilePath,'wb') as f:
                pickle.dump(self.interaction_data,f)

    def update_actions_file(self,user,success_dict):
        today_date = datetime.now().date()
        today_date_string_format = today_date.strftime("%d-%m-%Y")

        all_users_actions_data = get_all_users_actions()
        for i in range(len(all_users_actions_data)):
            if all_users_actions_data[i].get('username') == self.username:
                for j in range(len(all_users_actions_data[i].get('data'))):
                    if all_users_actions_data[i]['data'][j].get('date') == today_date_string_format:
                        all_users_actions_data[i]['data'][j]['users'].remove(user)
                        all_users_actions_data[i]['data'][j]['done'].append(user)
                        if success_dict['like']: all_users_actions_data[i]['data'][j]['actions_history']['likes'] += 1
                        if success_dict['comment']: all_users_actions_data[i]['data'][j]['actions_history']['comments'] += 1
                        if success_dict['dm']: all_users_actions_data[i]['data'][j]['actions_history']['dms'] += 1
                        if success_dict['welcome_dm']: all_users_actions_data[i]['data'][j]['actions_history']['welcome_dms'] += 1
                        if success_dict['follow']: all_users_actions_data[i]['data'][j]['actions_history']['follows'] += 1
                        if success_dict['unfollow']: all_users_actions_data[i]['data'][j]['actions_history']['unfollows'] += 1
                        break
                break
        write_jsons_to_txt_file(actions_file_path,all_users_actions_data)

    def runner(self):

        if not bool(self.my_followers):self.my_followers = self.get_my_followers()

        # if self.want_to_send_welcome_dm:self.send_welcome_dms()

        if self.want_to_unfollow_user:self.unfollow_non_followers()
  
        if self.want_to_like_post or self.want_to_comment_on_post or self.want_to_follow_user or self.want_to_send_dm or self.want_to_watch_stories:
            while 1:
                try:
                    if not self.interaction_data:self.load_interactions()
                    print(len(self.interaction_data.data))
                    self.do_actions_on_current_users(
                                                        do_like=self.want_to_like_post,do_comment=self.want_to_comment_on_post,
                                                        do_follow=self.want_to_follow_user,do_dm=self.want_to_send_dm,
                                                        do_watch_story=self.want_to_watch_stories
                                                    )
                    break
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    self.print_me("Error occur during inner loop.")
        else:
            pass

    def driver(self):

        self.do_login()

        if not self.is_login:
            self.print_me("** Bot not able to proceed. Exiting...")
            return

        while 1:

            self.runner()

            if self.operations >=self.total_operations:break

            randomTime = random.randint(30,45)
            self.print_me("** Sleepf for {} minutes.".format(randomTime))
            time.sleep(randomTime * 60)
            self.operations += 1


        self.print_me(" ******* Session End ******* ")


def bot_driver(user_prefs):



    # username
    username = user_prefs.get('username')

    username,password,proxy = get_account_json(username).values()


    session_file_path = os.path.join(session_folder_path,username+'_session.json')

    # related files paths
    my_followers_file = os.path.join(followers_folder_path,username+'_followers.txt')
    following_file_path = os.path.join(followings_folder_path,username+'_followings.txt')
    notified_user_file_path = os.path.join(user_notified_folder_path,username+'_notified_users.txt')
    user_info_file_path = os.path.join(db_folder,username+'_info.txt')
    dm_file_path = os.path.join(dms_folder_path,username.replace('@','').replace('.','')+'_DMS.txt')
    welcome_dm_file_path = os.path.join(welcome_dms_folder_path,username.replace('@','').replace('.','')+'_WELCOME_DMS.txt')
    comment_file_path = os.path.join(comments_folder_path,username.replace('@','').replace('.','')+'_COMMENTS.txt')

    # targets
    TARGET_USERS = [t.strip() for t in user_prefs.get('target_usernames').split(',') if bool(t.strip())]
    TARGET_HASHTAGS = [t.strip() for t in user_prefs.get('target_hashtags').split(',') if bool(t.strip())]
    TARGET_LOCATIONS = [t.strip() for t in user_prefs.get('target_locations').split(',') if bool(t.strip())]

    # want to do some Action
    want_to_like = user_prefs.get('want_to_like')
    want_to_follow = user_prefs.get('want_to_follow')
    want_to_comment = user_prefs.get('want_to_comment')
    want_to_dms = user_prefs.get('want_to_dms')
    want_to_unfollow = user_prefs.get('want_to_unfollow')
    want_to_welcome_dms = user_prefs.get('want_to_welcome_dms')
    want_to_watch_stories = user_prefs.get('want_to_watch_stories')
    want_to_restart_session = user_prefs.get('want_to_restart_session')

    # per hour things
    like_per_hour = user_prefs.get('like_per_hour')
    follow_per_hour = user_prefs.get('follow_per_hour')
    comment_per_hour = user_prefs.get('comment_per_hour')
    dm_per_hour = user_prefs.get('dm_per_hour')
    unfollow_per_hour = user_prefs.get('unfollow_per_hour')
    stories_per_hour = user_prefs.get('stories_per_hour')
    welcome_dm_per_hour = user_prefs.get('welcome_dm_per_hour')

    want_to_upload_scheduled_posts = user_prefs.get('want_to_upload_scheduled_posts')

    repost_hashtags = [] #[t.strip() for t in user_prefs.get("repost_hashtags").split(',') if bool(t.strip())]
    total_posts_to_reposts = 1 #user_prefs.get("total_posts_to_reposts")

    post_scheduling_data = user_prefs.get("scheduled_posts")

    # unfollwo after x days
    unfollow_after_x_days = user_prefs.get('unfollow_after_x_days')

    # dms / comments / welcome dms
    t_dms = readFile(dm_file_path)
    DMS = [dm.replace('\\n','\n').replace('\ufeff','').replace('ï»¿','') for dm in t_dms]

    t_COMMENTS = readFile(comment_file_path)
    COMMENTS = [comm.replace('\\n','\n').replace('\ufeff','').replace('ï»¿','') for comm in t_COMMENTS]

    t_WELCOME_DMS = readFile(welcome_dm_file_path)
    WELCOME_DMS = [w_dm.replace('\\n','\n').replace('\ufeff','').replace('ï»¿','') for w_dm in t_WELCOME_DMS]

    if proxy is not None:
        if not proxy.startswith('http'):
            proxy = 'http://' + proxy.replace('https://').replace('http://')


    bot = BOT(
                username,password,proxy=proxy,

                target_usernames=TARGET_USERS,target_hashtags=TARGET_HASHTAGS,target_locations=TARGET_LOCATIONS,
                
                want_to_follow_user=want_to_follow,want_to_like_post=want_to_like,want_to_comment_on_post=want_to_comment,want_to_send_dm=want_to_dms,want_to_restart_session=want_to_restart_session,
                
                want_to_unfollow_user=want_to_unfollow,want_to_send_welcome_dm=want_to_welcome_dms,want_to_upload_scheduled_posts=want_to_upload_scheduled_posts,want_to_watch_stories=want_to_watch_stories,

                skip_business_account=False,
                
                DMS=DMS,COMMENTS=COMMENTS,WELCOME_DMS=WELCOME_DMS,
                
                my_followers_file=my_followers_file,following_file_path=following_file_path,notified_user_file_path=notified_user_file_path,user_info_file_path=user_info_file_path,

                session_file_path=session_file_path,
                
                likes_per_hour=like_per_hour,comments_per_hour=comment_per_hour,follows_per_hour=follow_per_hour,unfollows_per_hour=unfollow_per_hour,dms_per_hour=dm_per_hour,welcome_dms_per_hour=welcome_dm_per_hour,stories_per_hour=stories_per_hour,
                
                unfollow_after_x_days=unfollow_after_x_days,

                repost_hashtags=repost_hashtags,total_posts_to_reposts=total_posts_to_reposts,

                post_scheduling_data=post_scheduling_data
            )

    bot.driver()
