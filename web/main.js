var current_account_obj = {}


function isMacintosh() {
    return navigator.platform.indexOf('Mac') > -1
}
  
function isWindows() {
    return navigator.platform.indexOf('Win') > -1
}

$(document).ready(function() {
    remove_all_screens() // remove all screens
    addHover()           // add hover lintener
    show_screen("add_account_screen")
    startLogger()
})

function startLogger(){
    eel.start_logger()
}

function readFile(file){
    var reader = new FileReader();
    reader.onload = (e)=>{
        fileContent = e.target.result;
        return fileContent;
    }
    reader.onerror = (e)=>{
        return e.target.error.name;
    }
    reader.readAsText(file)
}

function remove_all_screens() {
    top_tray_buttons = document.getElementsByClassName('top_btns_tray')[0].getElementsByTagName('button')
    document.getElementById("dashboard_screen").style.display = "none"
    document.getElementById("add_account_screen").style.display = 'none'
    document.getElementById("account_manager_screen").style.display = 'none'
    document.getElementById("start_screen").style.display = 'none'
    document.getElementById("schedular_screen").style.display = 'none'
    document.getElementById("track_activities").style.display = 'none'

    for(let i=0;i<top_tray_buttons.length;i++){
        top_tray_buttons[i].style.background="#F06292"
        top_tray_buttons[i].style.color="white"
        top_tray_buttons[i].style.transform =  ''
    }
}

function show_screen(SCREEN_ID) {
    clear()
    remove_all_screens()
    ID = "#" + SCREEN_ID

    $(ID).hide().slideDown(500)

    change_settings_for_ui(SCREEN_ID)
    if(SCREEN_ID == 'dashboard_screen'){
        top_tray_buttons[0].style.background="white"
        top_tray_buttons[0].style.color="black"
        top_tray_buttons[0].style.transform =  'scale(1)'
        render_dashboard_html()
    }else if(SCREEN_ID == 'add_account_screen'){
        top_tray_buttons[1].style.background="white"
        top_tray_buttons[1].style.color="black"
        top_tray_buttons[1].style.transform =  'scale(1)'
    }else if(SCREEN_ID == 'account_manager_screen'){
        top_tray_buttons[2].style.background="white"
        top_tray_buttons[2].style.color="black"
        top_tray_buttons[2].style.transform =  'scale(1)'
        render_manage_accounts_cards()
    }else if(SCREEN_ID == 'start_screen'){
        top_tray_buttons[3].style.background="white"
        top_tray_buttons[3].style.color="black"
        top_tray_buttons[3].style.transform =  'scale(1)'
        render_select_account_element(SCREEN_ID)
    }else if(SCREEN_ID == 'schedular_screen'){
        top_tray_buttons[4].style.background="white"
        top_tray_buttons[4].style.color="black"
        top_tray_buttons[4].style.transform =  'scale(1)'
        // render_schedular_accounts_cards()
        render_select_account_element(SCREEN_ID)
    }
    else if(SCREEN_ID == 'track_activities'){
        top_tray_buttons[5].style.background="white"
        top_tray_buttons[5].style.color="black"
        top_tray_buttons[5].style.transform =  'scale(1)'
        track_activities_click()
    }
}

eel.expose(show_error);
function show_error(message,callBackFunc=false,str_data=false){
    swal({
        icon: "error",
        text:message,
        // closeOnClickOutside: false
    }).then(()=>{
        if(callBackFunc && str_data){
            console.log(callBackFunc)
            console.log(str_data)
            callBackFunc(str_data)
        }else if(callBackFunc){
            callBackFunc()
        }else if(str_data){
            $("#"+str_data.split(":")[1]).modal(str_data.split(":")[0])
        }
    })
}

eel.expose(show_warning);
function show_warning(message,callBackFunc=false,str_data=false){
    swal({
        icon: "warning",
        text:message,
        // closeOnClickOutside: false
    }).then(()=>{
        if(callBackFunc && str_data){
            callBackFunc(str_data)
        }else if(callBackFunc){
            callBackFunc()
        }
    })
}

eel.expose(show_success);
function show_success(message,callBackFunc=false,str_data=false){
    swal({
        icon: "success",
        text:message,
        // closeOnClickOutside: false
    }).then(()=>{
        if(callBackFunc && str_data){
            callBackFunc(str_data)
        }else if(callBackFunc){
            callBackFunc()
        }
    })
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// DASHBOARD SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function render_dashboard_html(){
    target = document.getElementById("dashboard_container").getElementsByTagName('tbody')[0]
    target.innerHTML = ""
    eel.get_dms_count_of_all_emaulator()(function(data){
        for(let i=0; i<data.length; i++){
            target.innerHTML += `
            <tr>
                <td>${i+1}</td>
                <td>${data[i].device}</td>
                <td>${data[i].date}</td>
                <td>${data[i].total}</td>
            </tr>
            `
        }
    })
    
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// ADD NEW ACCOUNT SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function add_new_account(){
    eel.is_account_limit_exceed()(function(res){
        if(res){
            show_error("Accounts Limit Reached!")
        }else{
            username = document.getElementById('new_account_username').value
            password = document.getElementById('new_account_password').value
            // account_device = document.getElementById('device_selector_for_new_account').value
            proxy = document.getElementById('new_account_proxy').value
            if(!Boolean(proxy)){
                proxy = null
            }
            // password = 'temp'
            // proxy = null
            if (!Boolean(username)){
                show_error(message="Username is missing")
            }else if (!Boolean(password)){
                show_error(message="password is missing")
            }

            else{
                eel.add_new_account(username,password,proxy)(function(res){
                    if(res){
                        show_success(message="Account Added Successfully!",callBackFunc=clear)
                    }else{
                        show_error("account already in Db")
                        // show_error(message="Error Reasons:\n* Account Already Present in Db!\n* Emulator '" + account_device + "' Reached maximum accounts limit!")
                    }
                })
            }
        }
    })
    

}


// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// MANAGE ACCOUNTs SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function delete_account(el){

    account_json_obj = JSON.parse(el.parentElement.parentElement.parentElement.getElementsByTagName('input')[0].value)

    swal("Are you sure to delete ?", {
        icon: "warning",
        dangerMode: true,
        buttons: ["No", "Yes"]

    }).then((isConfirm) => {
        if (isConfirm) {
            eel.delete_account(account_json_obj)(function(res){
                if(res){
                    show_success("Account Deleted Successfully!")
                    render_manage_accounts_cards()
                }else{
                    show_error("Account Deleted Failed")
                }
            })
        }
    });

    

}

function render_manage_accounts_cards(){
    target_div = document.getElementById('account_manager_screen')
    target_div.innerHTML = `
        <h3 style="color: grey;"><strong>Manage Accounts</strong></h3>
        <hr>
    `

    eel.get_all_accounts()(function(accounts){
        if(accounts.length>0){
            var card_row_element = null;
            for(let a = 0; a<accounts.length; a++){
                if(a%3==0){
                    if(card_row_element){
                        target_div.appendChild(card_row_element);
                        card_row_element = null;
                    }
                    
                    // create row 
                    card_row_element = document.createElement("div")
                    card_row_element.className = "card-row"
                }
                card_row_element.innerHTML += `
                    <div class="card" >
                        <input style='display:none' value=${JSON.stringify(accounts[a])}  />
                        <div style="text-align: center;margin-top: 5%;">
                            <br>
                            <h4><strong>Account: </strong><span>${accounts[a].username}</span> </h4>
                            <h4><strong>Password: </strong><span>${accounts[a].password}</span> </h4>
                            <h4 style='display:none'><strong>Device: </strong><span></span> </h4>
                            <div style="display: flex; justify-content: center;margin-top: 15%;">
                                <button style="font: 26px;margin: 1%;" class="btn btn-outline-light btn-lg" onclick='delete_account(this)'>Delete</button>
                            </div>
                        </div>
                    </div>
                `
            }
            target_div.appendChild(card_row_element);
            addHover()
        }
    })
}


// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// START SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



//  //  //  //  //  //  //  //  //  //  
//  //  //  //  //  //  //  //  //  //   POST REPOSTING FUNCTIONS
//  //  //  //  //  //  //  //  //  //  

function set_reposter(el){
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    Swal.fire({
        title:"Reposter",
        html:`
            <br>
            <div>
                <div style='width:80%;margin: 0 auto;text-align:left'>
                    <label><strong>Target Hashtags<strong></label>
                    <input id='target_hashtags_for_repost' style='font-size:18px' class='form-control' value="${el.getAttribute('h')}" placeholder='hashtag1, hashtag2' type='text'/>
                </div>
                <br>
                <div style='width:80%;margin: 0 auto;text-align:left'>
                    <label><strong>Total Posts Per Day<strong></label>
                    <input id='total_posts' style='font-size:18px' class='form-control' placeholder='1' value="${el.getAttribute('p')}" min='1' max='3' type='number'/>
                </div>
                <br>
            </div>
        `
    }).then((res)=>{
        if(res.value){
            target_hashtags_for_repost = document.getElementById("target_hashtags_for_repost").value
            total_posts = Number(document.getElementById("total_posts").value)
            if(!Boolean(target_hashtags)){
                show_error("target hashtags not provided")
                return
            }
            if(!Boolean(total_posts)){
                total_posts = 1
            }
            el.setAttribute("h",target_hashtags_for_repost)
            el.setAttribute("p",total_posts)

        }else{

        }
    })
}


//  //  //  //  //  //  //  //  //  //  
//  //  //  //  //  //  //  //  //  //   POST SCHEDULING FUNCTIONS
//  //  //  //  //  //  //  //  //  //  

function set_post_image(el) {
    eel.get_file_path()(function(file_path) {
        if (file_path) {
            el.innerHTML = file_path
        } else {
            show_err("No Image selected.")
        }
    })
}

function schedule_new_post(){
    if(!Boolean(current_account_obj.username)){
        alert("username is not selected.")
        return
    }

    html = document.createElement('div')
    html.innerHTML = `
    <br>
    <div style="text-align: center">
        <h2 for="select_img"><strong>SELECT IMAGE</strong></h2>
        <button align="center" style="width: 50%;height: 60px;text-align: center;margin: 0 auto;overflow: hidden" type="button" id='select_img' onclick="set_post_image(this)" class="btn btn-outline-dark btn-block">SET POSTS IMAGE</button>
    </div>

    <br>
    <div style="text-align: center">
        <h2 for="caption_area"><strong>SET CAPTION</strong></h2>
        <textarea name="" id="caption_area" cols="40" rows="10"></textarea>
    </div>
    <br>
    <div style="text-align: center;display:flex;justify-content:center ">
        <div style="margin: 1%;">
            <h2 for="select_date"><strong>Set Date</strong></h2>
            <input style="text-align: center;height: 50px;margin: 0 auto;" id='select_date' class="form-control" type="date">
        </div>
    </div>
    <br>
    `
    Swal.fire({
        title:"NEW POST MENU",
        html:html, 
        onBeforeOpen: ()=>{
            html.parentElement.parentElement.parentElement.style = "width:30%"
        }
    }).then((res)=>{
        if(res.value){
            post_path = document.getElementById("select_img").innerHTML
            caption = document.getElementById("caption_area").value
            date = document.getElementById("select_date").value
            if(post_path == 'SET POSTS IMAGE' || !Boolean(date)){
                show_error("Image or Date is not selected !",schedule_new_post)
            }else{
                eel.save_post_scheduling_data(current_account_obj.username,post_path,caption,date)(function(res){
                    if(res){
                        show_success("Post Scheduled Successfully",set_values_to_schedular_screen)
                    }else{
                        show_error("Operation Failed !", set_values_to_schedular_screen)
                    }
                })
            }
        }else{
            schedule_post(null)
        }
    })


}

function see_caption(captionText){
    HTML = document.createElement("div")

    HTML.innerHTML = `
    <br>
    <textarea style='padding:3%' name="" disabled cols="40" disabled rows="10">${captionText}</textarea>
    <br>
    `
    Swal.fire({
        title: "caption",
        html:HTML,
        onBeforeOpen: ()=>{
            HTML.parentElement.parentElement.parentElement.style = "width:30%"
        }
    }).then((res)=>{

    })
}

function delete_scheduled_post(scheduled_post_entry){
    scheduled_post_entry = JSON.parse(scheduled_post_entry)
    eel.delete_post_scheduling_data(current_account_obj.username,scheduled_post_entry)(function(res){
        set_values_to_schedular_screen()
    })
}

//  //  //  //  //  //  //  //  //  //  
//  //  //  //  //  //  //  //  //  //   SAVE PREFERENCES FUNCTIONS
//  //  //  //  //  //  //  //  //  //  

function change_settings_for_ui(current_screen_id){
    if(current_screen_id == 'add_account_screen'){
        document.getElementsByClassName('mid_right')[0].style.display = 'block'
        document.getElementsByClassName('mid_left')[0].style.width = '70%'
    }else if(current_screen_id == 'account_manager_screen'){
        document.getElementsByClassName('mid_right')[0].style.display = 'block'
        document.getElementsByClassName('mid_left')[0].style.width = '70%'
    }else if(current_screen_id == 'start_screen'){
        document.getElementsByClassName('mid_right')[0].style.display = 'none'
        document.getElementsByClassName('mid_left')[0].style.width = '95%'
    }else if(current_screen_id == 'schedular_screen'){
        document.getElementsByClassName('mid_right')[0].style.display = 'block'
        document.getElementsByClassName('mid_left')[0].style.width = '70%'
    }
    else if(current_screen_id == 'track_activities'){
        document.getElementsByClassName('mid_right')[0].style.display = 'block'
        document.getElementsByClassName('mid_left')[0].style.width = '70%'
    }
    
}

function render_select_account_element(screen_id){
    target_ele = document.getElementById(screen_id).getElementsByTagName('select')[0]
    target_ele.innerHTML = `
        <option value="set_account"><strong>Select Account</strong></option>
    `
    eel.get_all_accounts()(function(accounts){
        for(let a=0;a<accounts.length;a++){
            target_ele.innerHTML+=`
                <option value='${JSON.stringify(accounts[a])}'>
                    <strong>${accounts[a].username}</strong>
                </option>
            `
        }
        if(screen_id == 'schedular_screen'){
            document.getElementById('newPostCreator').style.display = "none"
        }
    })
}

function set_values_to_schedular_screen(){

    eel.get_user_prefs(current_account_obj.username)(function(pref){
        if(pref){
            console.log(pref)
            targetTable = document.getElementById('schedular_screen').getElementsByTagName('tbody')[0]
            targetTable.innerHTML = ""
            for(let t=0;t<pref.scheduled_posts.length; t++){
                strFor = JSON.stringify(pref.scheduled_posts[t])
                targetTable.innerHTML += `
                    <tr value='${JSON.stringify(pref.scheduled_posts[t])}'>
                        <td>${pref.scheduled_posts[t].image_path}</td>
                        <td>
                            <button onclick="see_caption('${pref.scheduled_posts[t].caption}')" class='btn btn-outline-info'>See caption</button>
                        </td>
                        <td>${pref.scheduled_posts[t].dated}</td>
                        <td>
                            <button onclick="delete_scheduled_post(strFor)" class='btn btn-outline-danger'>Delete post</button>
                        </td>
                    </tr>
                `
            }

        }
        else{
            targetTable = document.getElementById('schedular_screen').getElementsByTagName('tbody')[0]
            targetTable.innerHTML = ""
        }
    })
}

function set_values_to_start_screen(){
    console.log(current_account_obj.username)
    eel.get_user_prefs(current_account_obj.username)(function(pref){
        if(pref){
            console.log(pref)
            // setting 1
            document.getElementById('target_hashtags').value = pref.target_hashtags
            document.getElementById('target_usernames').value = pref.target_usernames
            document.getElementById('target_locations').value = pref.target_locations
            
            // setting 2
            if(pref.want_to_like){
                $('#want_to_like').bootstrapToggle('on');
            }else{
                $('#want_to_like').bootstrapToggle('off');
            }

            if(pref.want_to_follow){
                $('#want_to_follow').bootstrapToggle('on');
            }else{
                $('#want_to_follow').bootstrapToggle('off');
            }

            if(false){
                $('#want_to_comment').bootstrapToggle('on');
            }else{
                $('#want_to_comment').bootstrapToggle('off');
            }

            if(false){
                $('#want_to_dms').bootstrapToggle('on');
            }else{
                $('#want_to_dms').bootstrapToggle('off');
            }

            if(pref.want_to_unfollow){
                $('#want_to_unfollow').bootstrapToggle('on');
            }else{
                $('#want_to_unfollow').bootstrapToggle('off');
            }

            if(false){
                $('#want_to_welcome_dms').bootstrapToggle('on');
            }else{
                $('#want_to_welcome_dms').bootstrapToggle('off');
            }
            if(false){
                $('#want_to_upload_scheduled_posts').bootstrapToggle('on');
            }else{
                $('#want_to_upload_scheduled_posts').bootstrapToggle('off');
            }
            if(pref.want_to_watch_stories){
                $('#want_to_watch_stories').bootstrapToggle('on');
            }else{
                $('#want_to_watch_stories').bootstrapToggle('off');
            }


            document.getElementById('like_per_hour').value = pref.like_per_hour
            document.getElementById('follow_per_hour').value = pref.follow_per_hour
            document.getElementById('comment_per_hour').value = pref.comment_per_hour
            document.getElementById('unfollow_per_hour').value = pref.unfollow_per_hour
            document.getElementById('dm_per_hour').value = pref.dm_per_hour
            document.getElementById('stories_per_hour').value = pref.stories_per_hour
            document.getElementById('welcome_dm_per_hour').value = pref.welcome_dm_per_hour

            // setting 3
            document.getElementById('unfollow_after_x_days').value = pref.unfollow_after_x_days

        }
        else{
            // setting 1
            document.getElementById('target_hashtags').value = ''
            document.getElementById('target_usernames').value = ''
            document.getElementById('target_locations').value = ''
            
            // setting 2
            $('#want_to_like').bootstrapToggle('on');
            $('#want_to_follow').bootstrapToggle('on');
            $('#want_to_comment').bootstrapToggle('off');
            $('#want_to_dms').bootstrapToggle('off');
            $('#want_to_unfollow').bootstrapToggle('on');
            $('#want_to_welcome_dms').bootstrapToggle('off');
            $('#want_to_watch_stories').bootstrapToggle('on');
            $('#want_to_upload_scheduled_posts').bootstrapToggle('off');

            document.getElementById('like_per_hour').value = ''
            document.getElementById('follow_per_hour').value = ''
            document.getElementById('comment_per_hour').value = ''
            document.getElementById('unfollow_per_hour').value = ''
            document.getElementById('dm_per_hour').value = ''
            document.getElementById('welcome_dm_per_hour').value = ''
            document.getElementById('stories_per_hour').value = ''

            // setting 3
            document.getElementById('unfollow_after_x_days').value = ''
        }
    })
}

$('#want_to_like').change(function(){
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;
})
$('#want_to_follow').change(function(){
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;

})
$('#want_to_unfollow').change(function(){
    document.getElementById('unfollow_after_x_days').disabled = !this.checked
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;
})
$('#want_to_comment').change(function(){
    document.getElementById('set_comments_btn').disabled = !this.checked
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;
})
$('#want_to_dms').change(function(){
    document.getElementById('set_dms_btn').disabled = !this.checked
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;
})
$('#want_to_welcome_dms').change(function(){
    document.getElementById('set_welcome_dms_btn').disabled = !this.checked
    this.parentElement.parentElement.getElementsByTagName('input')[1].disabled = !this.checked;
})

// $('#account_selecter_element').change(whenAccountSelectorChange())

// document.getElementById('start_screen').getElementsByTagName('select')[0].addEventListener('change',whenAccountSelectorChangeforStartScreen(document.getElementById('start_screen').getElementsByTagName('select')[0]))
// document.getElementById('schedular_screen').getElementsByTagName('select')[0].addEventListener('change',whenAccountSelectorChangeforSchedularScreen(document.getElementById('schedular_screen').getElementsByTagName('select')[0]))


function whenAccountSelectorChangeforStartScreen(el){
    try {
        account_obj = JSON.parse(el.value)
        current_account_obj = account_obj
        set_values_to_start_screen()
    } catch (error) {
        console.log(error)
        current_account_obj = {}
        set_values_to_start_screen()
    }

}
function whenAccountSelectorChangeforSchedularScreen(el){
    try {
        account_obj = JSON.parse(el.value)
        current_account_obj = account_obj
        document.getElementById('newPostCreator').style.display = "block"
        set_values_to_schedular_screen()
    } catch (error) {
        document.getElementById('newPostCreator').style.display = "none"
        current_account_obj = {}
        set_values_to_schedular_screen()
    }

}


function save_settings(){
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    // setting 1
    var target_hashtags = document.getElementById('target_hashtags').value
    var target_usernames = document.getElementById('target_usernames').value
    var target_locations = document.getElementById('target_locations').value
    
    // setting 2
    var want_to_like = document.getElementById('want_to_like').checked
    var want_to_follow = document.getElementById('want_to_follow').checked
    var want_to_comment = false
    var want_to_dms = false
    var want_to_unfollow = document.getElementById('want_to_unfollow').checked
    var want_to_welcome_dms = false
    var want_to_watch_stories = document.getElementById("want_to_watch_stories").checked
    var want_to_upload_scheduled_posts = false
    
    var like_per_hour = Number(document.getElementById('like_per_hour').value)
    var follow_per_hour = Number(document.getElementById('follow_per_hour').value)
    var comment_per_hour = Number(document.getElementById('comment_per_hour').value)
    var dm_per_hour = Number(document.getElementById('dm_per_hour').value)
    var unfollow_per_hour = Number(document.getElementById('unfollow_per_hour').value)
    var welcome_dm_per_hour = Number(document.getElementById('welcome_dm_per_hour').value)
    var stories_per_hour = Number(document.getElementById("stories_per_hour").value)
    // var restart_session_after_x_hours = Number(document.getElementById("restart_session_after_x_hours").value)
    if(!Boolean(like_per_hour)){like_per_hour = 20}
    if(!Boolean(follow_per_hour)){follow_per_hour = 20}
    if(!Boolean(comment_per_hour)){comment_per_hour = 20}
    if(!Boolean(dm_per_hour)){dm_per_hour = 20}
    if(!Boolean(unfollow_per_hour)){unfollow_per_hour = 20}
    if(!Boolean(welcome_dm_per_hour)){welcome_dm_per_hour = 20}
    if(!Boolean(stories_per_hour)){stories_per_hour = 20}
    // if(!Boolean(restart_session_after_x_hours)){restart_session_after_x_hours = 2}

    repost_hashtags = ''
    total_posts_to_reposts = 1

    if (!Boolean(total_posts_to_reposts)){
        total_posts_to_reposts = 1
    }
    if (!Boolean(repost_hashtags) || repost_hashtags == "undefined"){
        repost_hashtags = ""
    }

    // setting 3
    var unfollow_after_x_days = Number(document.getElementById('unfollow_after_x_days').value) 
    if(!Boolean(unfollow_after_x_days)){
        unfollow_after_x_days = 2
    }

    if(!Boolean(target_hashtags) && !Boolean(target_usernames) && !Boolean(target_locations)){
        show_error("Cannot Proceed Without Target Selected, Please Enter Target hashtags / Target usernames / Target Locations First.")
        return
    }



    json_data = {
        username:username,
        target_hashtags:target_hashtags,
        target_usernames:target_usernames,
        target_locations:target_locations,
        want_to_like:want_to_like,
        want_to_follow:want_to_follow,
        want_to_comment:want_to_comment,
        want_to_dms:want_to_dms,
        want_to_unfollow:want_to_unfollow,
        want_to_watch_stories:want_to_watch_stories,
        want_to_welcome_dms:want_to_welcome_dms,
        like_per_hour:like_per_hour,
        follow_per_hour:follow_per_hour,
        comment_per_hour:comment_per_hour,
        stories_per_hour:stories_per_hour,
        dm_per_hour:dm_per_hour,
        unfollow_per_hour:unfollow_per_hour,
        welcome_dm_per_hour:welcome_dm_per_hour,
        unfollow_after_x_days:unfollow_after_x_days,
        want_to_upload_scheduled_posts:want_to_upload_scheduled_posts,
        repost_hashtags:repost_hashtags,
        total_posts_to_reposts:total_posts_to_reposts
    }
    eel.save_user_prefs(username,json_data)(function(res){
        if(res){
            show_success("Preferences Save Successfully")
        }else{
            show_error("Preferences Not Saved")
        }
    })
}

// $$$$$$$$$$$$$$$$$$$$  RUN ACCOUNT

function launch_account(){
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    swal("Are you sure ? By Doing so all account will start working !", {
        icon: "warning",
        dangerMode: true,
        buttons: ["No", "Yes"]

    }).then((isConfirm) => {
        if (isConfirm) {
            eel.launch_one_account(username)
            // eel.launch()
            setTimeout(()=>{
                show_screen('track_activities')
            },2000)
        }
    });

    
    // setTimeout(()=>{
    //     show_screen('track_activities')
    // },2000)


    // username = current_account_obj.username
    // if(!username){
    //     show_error('Account Not Selected')
    //     return
    // }


    // // setting 1
    // var target_hashtags = document.getElementById('target_hashtags').value
    // var target_usernames = document.getElementById('target_usernames').value
    // var target_locations = document.getElementById('target_locations').value
    
    // // setting 2
    // var want_to_like = false
    // var want_to_follow = false
    // var want_to_comment = false
    // var want_to_dms = document.getElementById('want_to_dms').checked
    // var want_to_unfollow = false
    // var want_to_welcome_dms = false
    // var want_to_restart_session = false

    // var like_per_hour = Number(document.getElementById('like_per_hour').value)
    // var follow_per_hour = Number(document.getElementById('follow_per_hour').value)
    // var comment_per_hour = Number(document.getElementById('comment_per_hour').value)
    // var dm_per_hour = Number(document.getElementById('dm_per_hour').value)
    // var unfollow_per_hour = Number(document.getElementById('unfollow_per_hour').value)
    // var welcome_dm_per_hour = Number(document.getElementById('welcome_dm_per_hour').value)
    // var restart_session_after_x_hours = Number(document.getElementById("restart_session_after_x_hours").value)
    // if(!Boolean(like_per_hour)){like_per_hour = 30}
    // if(!Boolean(follow_per_hour)){follow_per_hour = 30}
    // if(!Boolean(comment_per_hour)){comment_per_hour = 30}
    // if(!Boolean(dm_per_hour)){dm_per_hour = 30}
    // if(!Boolean(unfollow_per_hour)){unfollow_per_hour = 30}
    // if(!Boolean(welcome_dm_per_hour)){welcome_dm_per_hour = 30}
    // if(!Boolean(restart_session_after_x_hours)){restart_session_after_x_hours = 2}

    // repost_hashtags = document.getElementById("reposter_btn").getAttribute("h")
    // total_posts_to_reposts = Number(document.getElementById("reposter_btn").getAttribute("p"))

    // if (!Boolean(total_posts_to_reposts)){
    //     total_posts_to_reposts = 1
    // }
    // if (!Boolean(repost_hashtags) || repost_hashtags == "undefined"){
    //     repost_hashtags = ""
    // }

    // // setting 3
    // var unfollow_after_x_days = Number(document.getElementById('unfollow_after_x_days').value) 
    // if(!Boolean(unfollow_after_x_days)){
    //     unfollow_after_x_days = 2
    // }

    // if(!Boolean(target_hashtags) && !Boolean(target_usernames) && !Boolean(target_locations)){
    //     show_error("Cannot Proceed Without Target Selected, Please Enter Target hashtags / Target usernames / Target Locations First.")
    //     return
    // }

    // json_data = {
    //     username:username,
    //     target_hashtags:target_hashtags,
    //     target_usernames:target_usernames,
    //     target_locations:target_locations,
    //     want_to_like:want_to_like,
    //     want_to_follow:want_to_follow,
    //     want_to_comment:want_to_comment,
    //     want_to_dms:want_to_dms,
    //     want_to_unfollow:want_to_unfollow,
    //     want_to_welcome_dms:want_to_welcome_dms,
    //     like_per_hour:like_per_hour,
    //     follow_per_hour:follow_per_hour,
    //     comment_per_hour:comment_per_hour,
    //     dm_per_hour:dm_per_hour,
    //     unfollow_per_hour:unfollow_per_hour,
    //     welcome_dm_per_hour:welcome_dm_per_hour,
    //     unfollow_after_x_days:unfollow_after_x_days,
    //     want_to_restart_session:want_to_restart_session,
    //     restart_session_after_x_hours:restart_session_after_x_hours,
    //     repost_hashtags:repost_hashtags,
    //     total_posts_to_reposts:total_posts_to_reposts
    // }
    // eel.save_user_prefs(username,json_data)(function(res){
    //     if(res){
    //         eel.launch(username)
    //         setTimeout(()=>{
    //             show_screen('track_activities')
    //         },2000)
    //     }else{
    //         show_error("Operation Abort !")
    //     }
    // })


    
}


// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// SCHEDULAR SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function edit_ativity_time(el){
    my_html = document.createElement('div')
    my_html.innerHTML = `
        <div style='width:80%;margin:0 auto'>
            <div style='width:80%;margin:0 auto;font-size:20px'>
                <label for='activity_start_from'><strong>Activity Start From</strong></label>
                <input style='font-size:20px' type="time" name="" id="activity_start_from" class="form-control">
            </div >
            <br>
            <div style='width:80%;margin:0 auto;font-size:20px'>
                <label for='activity_start_to'><strong>Activity Start To</strong></label>
                <input style='font-size:20px' type="time" name="" id="activity_start_to" class="form-control">
            </div>
        </div>
    
    `
    swal({
        title:"Time Input",
        content:my_html
    }).then((result)=>{
        if(result){
            active_from = document.getElementById('activity_start_from').value
            active_to = document.getElementById('activity_start_to').value
            if(active_from>active_to){
                show_error("'Active Start From' Time Must Be Greater then 'Active Start To' Time ")
            }else{

            }
        }

    })
}

function render_schedular_accounts_cards(){
    target_div = document.getElementById('schedular_screen').getElementsByTagName('div')[0]
    target_div.innerHTML = `
        <table class="table" >
            <thead >
                <tr style='font-weight: bold;'>
                    <td>Account</td>
                    <td>Total Activity Hours</td>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    `

    target_table = document.getElementById('schedular_screen').getElementsByTagName('table')[0].getElementsByTagName('tbody')[0]

    eel.get_all_account_prefs()(function(prefs){

        for(let p=0;p<prefs.length;p++){
        
            var new_row = target_table.insertRow()
            new_row.value = JSON.stringify(prefs[p])
        
            // name
            new_row.insertCell().appendChild(
                document.createTextNode(prefs[p].username)
            )

            // total activity time hours
            new_row.insertCell().innerHTML = `
                <div style='display:flex;margin:0 auto;justify-content:center'>
                    <input type='number' style='width:25%;height:50px;text-align:center;font-size:22px' min='0' value=${prefs[p].total_activity_hours}  placeholder='5' class='form-control' onchange='sort_scheduling_table(this)'/>
                    <p style='margin:1%'>(in hour)</p>
                </div>
            `

        }
    })
}

function sort_scheduling_table(el){
    if (el.value<0){
        el.value = 0
    }
    row = el.parentElement.parentElement.parentElement
    pref_json = JSON.parse(row.value)
    pref_json.total_activity_hours = Number(el.value)
    row.value = JSON.stringify(pref_json)
}

function save_schedular_inputs(){
    all_prefs = []
    rows = document.getElementById('schedular_screen').getElementsByTagName('tbody')[0].rows
    for (let r=0;r<rows.length;r++ ){
        json = JSON.parse(rows[r].value)
        if(!Boolean(json.total_activity_hours) || json.total_activity_hours<0){
            json.total_activity_hours = 0
        }
        all_prefs.push(json)
    }
    eel.save_schedular_inputs(all_prefs)(function(res){
        if(res){
            show_success("Scheduling Inputs Are Saved")
        }else{
            show_error("Scheduling Inputs Are Not Saved :(")
        }
    })
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// SCHEDULAR SCREEN ////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


function stop_family(el){
    var processName = el.value
    // var USERNAME = el.value.split(':')[0]
    swal("Are you sure ?", {
        icon: "warning",
        dangerMode: true,
        buttons: ["No", "Yes"]

    }).then((isConfirm) => {
        if (isConfirm) {
            eel.STOP_ACCOUNT(processName)(function(res){
                if(res){
                    show_success("Process Kill Successfully !",track_activities_click)
                }else{
                    show_error("Operation Failed !",track_activities_click)
                }
            })
        }
    });
}

// activity tracker click
function track_activities_click(){
    eel.get_running_processes()(function(running_processes){
        console.log(running_processes)
        target_div = document.getElementById("track_activities")
        target_div.innerHTML = ""
        if (running_processes.length == 0){
            show_warning("No Activty is Pending.",callBackFunc=show_screen,str_data='start_screen')
            return
        }
        for(let i=0;i<running_processes.length;i++){
            if(running_processes[i].split(':').length > 2){
                var username = running_processes[i].split(':')[0] +":"+  running_processes[i].split(':')[1]
            }else{
                var username = running_processes[i].split(':')[0]
            }
            html_for_one_process = `
            <div class="track_activity_div" onmouseover="this.style.background='#BCAAA4';this.style.color='white';this.getElementsByTagName('button')[0].className='btn btn-outline-light btn-block'" onmouseout="this.style.background='#EEEEEE';this.style.color='darkslategrey';this.getElementsByTagName('button')[0].className='btn btn-outline-danger btn-block'">
                <h3 >Account Name: <span>${username}</span></h3>
                <button type="button" style='overflow:auto;font-size:26px;height:50px' value="${running_processes[i]}" onclick="stop_family(this)" class="btn btn-outline-danger btn-block"> <img src="./images/kill.png" alt=""> KILL ME</button>
            </div>
            `
            target_div.innerHTML+=html_for_one_process
        }

    })
}

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// //////////////////////////////////////////////// EXTRA METHOD  /////////////////////////////////////////////////////////
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function clear(){

    // clear add account screen 
    document.getElementById('new_account_username').value = ''
    document.getElementById('new_account_password').value = ''
    document.getElementById("new_account_proxy").value = ''

    for (let t = 0; t < 10; t++) {
        try {
            var rows = document.getElementById("comments_add_see_modal").getElementsByTagName('table')[0].getElementsByTagName("tr")
            for (let i = 1; i < rows.length; i++) {
                console.log(i)
                rows[i].remove()
            }
        } catch (error) {
            // console.log(error)
        }

        try {
            var rows = document.getElementById("dm_add_see_modal").getElementsByTagName('table')[0].getElementsByTagName("tr")
            for (let i = 1; i < rows.length; i++) {
                console.log(i)
                rows[i].remove()
            }
        } catch (error) {

        }
        try {
            var rows = document.getElementById("welcome_dm_add_see_modal").getElementsByTagName('table')[0].getElementsByTagName("tr")
            for (let i = 1; i < rows.length; i++) {
                console.log(i)
                rows[i].remove()
            }
        } catch (error) {

        }

    }

}

eel.expose(print);
function print(msg) {
    var target_div = document.getElementById("logs_div")
    target_div.innerHTML += msg +" <br>";
    target_div.scrollTo(0,target_div.scrollHeight);
}

function addHover(){
    all_cards = document.getElementsByClassName('card')
    for(let card = 0; card<all_cards.length; card++){
        all_cards[card].addEventListener("mouseover",function(){
            all_cards[card].style.background="#FEF5E7"
            // all_cards[card].style.background="#EC7063"
            all_cards[card].getElementsByTagName("h4")[0].style.color="black"
            all_cards[card].getElementsByTagName("h4")[1].style.color="black"
            all_cards[card].getElementsByTagName("h4")[2].style.color="black"
            all_cards[card].getElementsByTagName('button')[0].className = 'btn btn-outline-danger btn-lg'
        })
        all_cards[card].addEventListener("mouseout",function(){
            all_cards[card].style.background="#F06292"
            all_cards[card].getElementsByTagName("h4")[0].style.color="white"
            all_cards[card].getElementsByTagName("h4")[1].style.color="white"
            all_cards[card].getElementsByTagName("h4")[2].style.color="white"
            all_cards[card].getElementsByTagName('button')[0].className = 'btn btn-outline-light btn-lg'
        })
    }

}

function exit_program() {
    swal("Are you sure ?", {
        icon: "warning",
        dangerMode: true,
        buttons: ["No", "Yes"]
    }).then((isConfirm) => {
        if (isConfirm) {
            window.close()
        }
    });
}


// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////

async function add_comment() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }

    // $("#comments_add_see_modal").modal('hide')

    const { value: formValues } = await Swal.fire({
        title: 'Enter Comment Below',
        html: '<textarea id="swal-input1" row=100 col=10 style="height:300px" class="swal2-input"></textarea>',
        // '<input id="swal-input1" class="swal2-input"></input>',
        focusConfirm: false,
        preConfirm: () => {
            return [
                document.getElementById('swal-input1').value
            ]
        }
    })

    if (Boolean(formValues[0])) {
        eel.add_new_comment(formValues[0], username)(function(res) {
            if (res) {
                set_comments()
            }
        })
    }
}

function delete_comment(comment) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_comment(comment, username)(function(res) {
        if (res) {
            set_comments()
        }
    })
}

function edit_comment(comment) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_comment(comment, username)(function(res) {
        if (res) {
            comment = comment.split("\\n").join('\n')
            // $("#comments_add_see_modal").modal('hide')
            add_comment()
            document.getElementsByTagName('textarea')[0].value = comment

        }
    })
}

function set_comments() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }

    eel.get_all_comments(username)(function(comments){
        HTML = document.createElement('div')
        // HTML.style = "height:500px;overflow:auto"
        HTML.innerHTML = `
        <br>

        <div style="text-align: center;">
            <button align="center" type="button" class='btn btn-outline-primary btn-lg' onclick='add_comment()'>ADD COMMENT + </button>
        </div>
        <br>
        <br>
        <div style ='height:500px;overflow:auto'>
            <table class="table" id='comments_table'  style="width: 100%;font-size: 22px;">
                <thead class="thead-light">
                    <tr>
                        <th scope="col">Sr #</th>
                        <th scope="col">Old Comments</th>
                        <th scope="col"> --- </th>
                        <th scope="col"> --- </th>
                    </tr>
                </thead>
            </table>
        </div>
        <br>
        
        `

        table = HTML.getElementsByTagName('table')[0]
        var rows = table.getElementsByTagName("tr").length
        for(let c=0; c<comments.length; c++){
            var row = table.insertRow(rows);
            row.insertCell(0).innerHTML = c + 1;
            
            cell_1 = row.insertCell(1)
            cell_1.innerHTML = comments[c];
            cell_1.style = "width:50%"

            // add delete button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "D E L E T E"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { delete_comment(comments[c]) })
            row.insertCell(2).appendChild(btn);

            // add edit button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "E D I T"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { edit_comment(comments[c]) })
            row.insertCell(3).appendChild(btn);
            row = row + 1
        }

        Swal.fire({
            title:"Comment Menu",
            html:HTML, 
            onBeforeOpen: ()=>{
                HTML.getElementsByTagName('table')[0].parentElement.parentElement.parentElement.parentElement.parentElement.style = "width:45%"
            }
        })

    })

    // $("#comments_add_see_modal").modal('show')
    // clear()
    // eel.get_all_comments(username)(function(comments) {
    //         if (comments) {
    //             var table = document.getElementById("comments_add_see_modal").getElementsByTagName('table')[0]
    //             var rows = table.getElementsByTagName("tr").length
    //             for (let i = 0; i < comments.length; i++) {
    //                 var row = table.insertRow(rows);
    //                 let e = 1
    //                 row.insertCell(0).innerHTML = i + 1;
    //                 row.insertCell(1).innerHTML = comments[i];
    //                 // add delete button
    //                 var btn = document.createElement('button');
    //                 btn.type = "button";
    //                 btn.innerHTML = "D E L E T E"
    //                 btn.className = "btn btn-outline-success";
    //                 btn.onclick = (function(entry) { delete_comment(comments[i]) })
    //                 row.insertCell(2).appendChild(btn);

    //                 // add edit button
    //                 var btn = document.createElement('button');
    //                 btn.type = "button";
    //                 btn.innerHTML = "E D I T"
    //                 btn.className = "btn btn-outline-success";
    //                 btn.onclick = (function(entry) { edit_comment(comments[i]) })
    //                 row.insertCell(3).appendChild(btn);

    //                 rows = rows + 1
    //             }
    //         }
    //     })
        // eel.open_comment_file()
}

// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////

async function add_dm() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    // $("#dm_add_see_modal").modal('hide')
    const { value: text } = await Swal.fire({
        title: 'Enter Dm Below',
        html: '<textarea id="swal-input1" style="height:300px" class="swal2-input"></textarea>',
        // '<input id="swal-input1" class="swal2-input"></input>',
        focusConfirm: false,
        preConfirm: () => {
            return document.getElementById('swal-input1').value

        }
    })
    if (Boolean(text)) {
        eel.add_new_dm(text, username)(function(res) {
            if (res) {
                set_dms()
            }
        })
    }
    else{
        set_dms()
    }
}

function delete_dm(dm) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_dm(dm, username)(function(res) {
        if (res) {
            set_dms()
        }
    })
}

function edit_dm(dm) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_dm(dm, username)(function(res) {
        if (res) {
            dm = dm.split("\\n").join('\n')
            // $("#dm_add_see_modal").modal('hide')
            add_dm()
            document.getElementsByTagName('textarea')[0].value = dm

        }
    })
}

function save_these_dms_for_all_accounts(){
    username = current_account_obj.username
    eel.save_these_dms_for_all_accounts(username)(function(res){
        if(res){
            show_success("Dms Saved for all accounts successfully !")
        }else{
            show_error("Dms Saved for all accounts Failed !")
        }
    })
}


function set_dms() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.get_all_dms(username)(function(dms){
        HTML = document.createElement('div')
        // HTML.style = "height:500px;overflow:auto"
        HTML.innerHTML = `
        <br>

        <div style="text-align: center;display:flex;margin:0 auto;justify-content:center">
            <button align="center" style='margin:1%' type="button" class='btn btn-outline-primary btn-lg' onclick='add_dm()'>ADD NEW DM + </button>
        </div>
        <br>
        <br>
        <div style ='height:500px;overflow:auto'>
            <table class="table" id='dms_table'  style="width: 100%;font-size: 22px;">
                <thead class="thead-light">
                    <tr>
                        <th scope="col">Sr #</th>
                        <th scope="col">Old DMS</th>
                        <th scope="col"> --- </th>
                        <th scope="col"> --- </th>
                    </tr>
                </thead>
            </table>
        </div>
        <br>
        
        `

        table = HTML.getElementsByTagName('table')[0]
        var rows = table.getElementsByTagName("tr").length
        for(let c=0; c<dms.length; c++){
            var row = table.insertRow(rows);
            row.insertCell(0).innerHTML = c + 1;
            
            cell_1 = row.insertCell(1)
            cell_1.innerHTML = dms[c];
            cell_1.style = "width:50%"

            // add delete button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "D E L E T E"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { delete_dm(dms[c]) })
            row.insertCell(2).appendChild(btn);

            // add edit button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "E D I T"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { edit_dm(dms[c]) })
            row.insertCell(3).appendChild(btn);

            row = row + 1
        }

        Swal.fire({
            title:"Dms Menu",
            html:HTML, 
            onBeforeOpen: ()=>{
                HTML.getElementsByTagName('table')[0].parentElement.parentElement.parentElement.parentElement.parentElement.style = "width:45%"
            }
        })

    })
}


// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////


async function add_welcome_dm() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    $("#welcome_dm_add_see_modal").modal('hide')
    const { value: text } = await Swal.fire({
        title: 'Enter Welcome Dm Below',
        html: '<textarea id="swal-input1" style="height:300px" class="swal2-input"></textarea>',
        // '<input id="swal-input1" class="swal2-input"></input>',
        focusConfirm: false,
        preConfirm: () => {
            return document.getElementById('swal-input1').value

        }
    })
    if (Boolean(text)) {
        eel.add_new_welcome_dm(text, username)(function(res) {
            if (res) {
                set_welcome_dms()
            }
        })
    }
}

async function delete_welcome_dm(dm) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_welcome_dm(dm, username)(function(res) {
        if (res) {
            set_welcome_dms()
        }
    })
}

function edit_welcome_dm(dm) {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.delete_welcome_dm(dm, username)(function(res) {
        if (res) {
            dm = dm.split("\\n").join('\n')
            $("#welcome_dm_add_see_modal").modal('hide')
            add_welcome_dm()
            document.getElementsByTagName('textarea')[0].value = dm

        }
    })
}

function set_welcome_dms() {
    username = current_account_obj.username
    if(!username){
        show_error('Account Not Selected')
        return
    }
    eel.get_all_welcome_dms(username)(function(dms){
        HTML = document.createElement('div')
        // HTML.style = "height:500px;overflow:auto"
        HTML.innerHTML = `
        <br>
        <div style="text-align: center;">
            <button align="center" type="button" class='btn btn-outline-primary btn-lg' onclick='add_welcome_dm()'>ADD WELCOME DM + </button>
        </div>
        <br>
        <br>
        <div style ='height:500px;overflow:auto'>
            <table class="table" id='welcome_dms_table'  style="width: 100%;font-size: 22px;">
                <thead class="thead-light">
                    <tr>
                        <th scope="col">Sr #</th>
                        <th scope="col">Old DMS</th>
                        <th scope="col"> --- </th>
                        <th scope="col"> --- </th>
                    </tr>
                </thead>
            </table>
        </div>
        <br>
        `

        table = HTML.getElementsByTagName('table')[0]
        var rows = table.getElementsByTagName("tr").length
        for(let c=0; c<dms.length; c++){
            var row = table.insertRow(rows);
            row.insertCell(0).innerHTML = c + 1;
            
            cell_1 = row.insertCell(1)
            cell_1.innerHTML = dms[c];
            cell_1.style = "width:50%"

            // add delete button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "D E L E T E"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { delete_welcome_dm(dms[c]) })
            row.insertCell(2).appendChild(btn);

            // add edit button
            var btn = document.createElement('button');
            btn.type = "button";
            btn.innerHTML = "E D I T"
            btn.className = "btn btn-outline-success";
            btn.onclick = (function(entry) { edit_welcome_dm(dms[c]) })
            row.insertCell(3).appendChild(btn);
            row = row + 1
        }

        Swal.fire({
            title:"Welcome Dms Menu",
            html:HTML, 
            onBeforeOpen: ()=>{
                HTML.getElementsByTagName('table')[0].parentElement.parentElement.parentElement.parentElement.parentElement.style = "width:45%"
            }
        })

    })
}


// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////



