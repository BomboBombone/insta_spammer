import gspread,os,shutil,json
from oauth2client.service_account import ServiceAccountCredentials
from config import get_app_path,get_mac
from datetime import datetime,timedelta



class licenseTracker:

    def __init__(self):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        self.SHEET = None
        self.credential_file_path = os.path.join(get_app_path(),'config','files','cores','creds.json')
        self.dic = {
            "type": "service_account",
            "project_id": "empyrean-box-299916",
            "private_key_id": "6911e0e4f63582ceb51906b72a3b46f12074a033",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDvvHN6KlMHLp+Y\n1nrLfzHh8k2AEoSrgMDja4KVsRoVHZF67keXEQFdWBW/bsuxEeTmdR6XaOhZtzc9\naWYmMG1zjEls/aUQ1yBGik33DV0YtH2tVyo+dfFj5lsnxcbrzBYfv/duooJxSNbP\nPBe+80eUwkXfIQ4KZ80M5sibxj2Ipar4xjz+ZGNS0bhsNujR79JiIU2DbZaRakVY\ndqYaGwvlN0SRDoCWdVAFPdV1/4r5qNThctGjnnT4fZXAgZLnhdNk2+A4naxFeb8J\nC3uice5GwINIze1xBNdWqnvEZ85y8gfbWytLiKh0E+5/AIj7L3sEg/39fArjREIg\nvD+dyEVTAgMBAAECggEABiplF+e9weoHjcE6YEBxsntuVdRkGBsUGuU5cwsefhuI\nEc7OBYsY62MoEAfT8kZhCjJJ6p/2ldQZ9hjfWS0Wq4mYm9Z8J844lMfa0HdGBSwj\nLVGYEwoqfqS+hGvYPVk+2msv/GbujuZOK/9CJxWPqjpC3MW3XDomMmY/E46KJ5j6\naeiLwuEQeiasLxMei3LVstH854xEWmHTIkk8nBWR6/RNeoSJzCOEOWfgAt0gTjeu\nAY8gANQ2VsIr0Ctc0eG7uwfDpykNtiytCLH8jTA94pNs1f49SkWEUDWPevNwCChm\nHhG+eQOZ96vlCJBp+WsYUI61LSm3hpv7pmlUihxgHQKBgQD57g+V7g9RDYSSLjsl\nfIGpMsiCG3gaikz8B/vNAHPUkAxejKMywi4dk8DAs2+kg4WVn3VSPFCFUTx0J/Ob\n8L8sL7oChjrJ1SYTcv2erI7gRJWGr63zIMQ6e1orhrJEEAJURcFxc8I2eskDe9An\nHky2oUV1d1+njGvxeXGXF+iTrQKBgQD1jwKlBlWf8gvdTOXfplOihDi2hEJaSXXo\neL+qzYg7IEcouLPbSDGTDZwnZ8ps+m4+YtpnL2DlZ9doxxSJCfswFzZEOtKJ2x5A\nYDVQvsjX9y9nnNWp469Ss/65HXJCOiqDvu8UBcjgzrXQIqMMdCbGkRwYmu9m2+TO\nWnEEMZdc/wKBgHapvOSmnscQ7/ynzpVBxB4dam27tQ6E04BmGft/V3941SafB202\nHMcWO9JCX6NwfqBHkWB2GpTxuQ49WcCUUXAdSOeh64+gj+90DU6lB0EbzxKfnqts\nxz4tCubXkRQXtcNlSy8ekvti2MW6p12rWSjs8RmQj+3xEd8YlgHy7A4RAoGAUSNz\nFUJVkqcxAmvBXTghVIbqEmz7W8gAPNOBSZfmVtsgiDUXwPJG5zdNDLw/5+iL+vNB\nBW1jUAoS5F07zNhOdqKE3OCu5rxPb6galdakmK/lqw/ojd1c9i/hkBtJwNZla+jw\nKKaMrLPA4chAJgJPObeDGCJBzrQEE6dQxrj4MdMCgYAV+06c1/ZX0D5jTCTmBIyV\nj1WIb2IzzdOB7ldtqsPhHTCvOQAZ/IOX+LwIMgqu/LdurW/Ehy7gzuB90CC1JMEh\nw4s6SLTJQes/esY0ayhbd2gj4qgDdr7ig6YzspTEpyyGb1Oytu5kvbgoE+sW1xsY\ntviTC2yxnMRS+0Fqq5EpYg==\n-----END PRIVATE KEY-----\n",
            "client_email": "pire-wise@empyrean-box-299916.iam.gserviceaccount.com",
            "client_id": "107813617179301962595",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pire-wise%40empyrean-box-299916.iam.gserviceaccount.com"
        }

    def load_cres_json_file(self):
        if not os.path.exists(self.credential_file_path):
            file = open(self.credential_file_path,'w')
            json_dumps_str = json.dumps(self.dic, indent=4)
            file.write(json_dumps_str)

    def delete_creds_json_file(self):
        try:
            os.remove(self.credential_file_path)
        except:
            pass

    def load_sheet(self):
        # print("[+] Loading .... ..")
        self.load_cres_json_file()
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credential_file_path, self.scope)
        client = gspread.authorize(creds)
        self.SHEET = client.open("License Tracker (Pire)").sheet1
        self.delete_creds_json_file()
        # print("[+] Loading Done -")

    def check_and_load_sheet(self):
        if not self.SHEET:self.load_sheet()

    def get_all_sheet_data(self):
        self.check_and_load_sheet()
        data = self.SHEET.get_all_records()  # Get a list of all records
        return data

    def is_user_is_new(self,username,project_name):
        self.check_and_load_sheet()
        all_data = self.get_all_sheet_data()
        current_mac_address = get_mac()
        user_is_new = True
        for data in all_data:
            if data.get('Buyer').lower() == username.lower() and data.get('Project Name').lower() == project_name.lower():
                user_is_new = False
                break
        if user_is_new:
            for data in all_data:
                if data.get('Project Name').lower() == project_name.lower() and data.get('Machine Address').lower() == current_mac_address.lower():
                    # print("[Error] Same Project is Already Allocated to Device.")
                    return False 
        return user_is_new

    def what_datetime_now(self):
        return datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    def get_user_index(self,username,project_name):
        all_data = self.get_all_sheet_data()
        for i in range(len(all_data)):
            if all_data[i].get('Buyer').lower() == username.lower() and all_data[i].get('Project Name').lower() == project_name.lower():
                return i+2
        return -1

    def add_user(self,username,project_name):
        # print("[->] Adding New User '{}' to db ".format(username))
        
        # give 30 days pkg
        activated_from = datetime.now()
        activated_to = (activated_from+timedelta(days=+30)).strftime('%d-%m-%Y')
        activated_from = activated_from.strftime('%d-%m-%Y')
        
        new_data = [username,get_mac(),project_name,activated_from,activated_to,self.what_datetime_now(),"ON"]
        self.SHEET.append_row(new_data)
        # print("[info] Person Added Succeed.")

    def update_data(self,username,project_name):
        # print("[->] Updating User '{}'.. ".format(username))
        all_data = self.get_all_sheet_data()
        for i in range(len(all_data)):
            if all_data[i].get('Buyer').lower() == username.lower() and all_data[i].get('Project Name').lower() == project_name.lower():
                self.SHEET.update_cell(i+2,6, self.what_datetime_now())  # Update cell number 6 value which is date
                break
        # print("[+] User Updated.")

    def authenticate_user(self,username,project_name):
        print("[+] Authenticating incomming orders....")
        self.check_and_load_sheet()

        # check if user is new
        isNewUser = self.is_user_is_new(username, project_name)
        if True:
            self.add_user(username,project_name)
            print("[+] Authentication Succeed.")
            return True
