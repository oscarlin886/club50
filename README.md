# README
## How to Compile and Configure CLUB50
First, download the zip file from the applicable source. Then, extract the zip file to a new folder of your choosing, taking care to name it something recognizable. Then, drag and drop or upload the new folder into VScode or some code editor. Then **cd** into the appropriate folder in the code editor and execute **$ flask run** into the terminal. Within the folder, you may also execute **sqlite3 clubs.db** and then **.schema** in order to review the structure of the various SQL tables.

*If you have cleared the club.db database, it is imperative that you register an Admin account with an id = 1 in order to allow for that account to access the admin options within CLUB50 (This can be done simply by being the first registered account after emptying the database).*

## Using CLUB50
1. As a normal User
    a. Normal users can simply register for an account by clicking on "Register" in the top right hand navbar. They are then prompted for a Club Name of which they are able to type whatever they'd like. Then, they will be prompted for a username and password and a confirmation of their password. There, they must type exactly what they had typed previously for their password.
    b. After registration, they will be redirected to their index/portfolio page where their requests are displayed. If there are none, then none will be displayed. At this point, they are able to navigate to the Request tab of the navbar (which is not avaible to admins) in which they are able to enter the reason for their request and argue for the grant inn a text box as well as enter the amount of the request. Then, they have to press the submit button or press enter. They will be redirected to their portfolio and the grant request will be submitted. 
    c. Users are also able to click on the comments tab in the navbar in order to submit a comment to be posted for everyone to see. They can also add an email through which anyone can contact them within the posted comment (defaults to no email given if none is given when written manually into the database)
    d. They are able to log out by clicking on the logout tab in the top rght corner. The name of the club can also be updated by clicking on the Profile tab in the top left hand corner of the navbar.
    e. Finally, they are able to Change their Passwords by clicking in thetop right of the navbar next to Log Out (it says Change Password) and there, the user must enter their old password and their new passwords in order to change it.
2. As an Admin
    a. An admin account is the first account that is registered into the clubs.db database. The first account tht is already wtihin the database should have a username of **admin1** and password of **123**. 
    b. Instead of a normal request or portfolio (they cannot utilize request) they have an admin page. Any attempt to got the index by an admin will redirect them to the Admin page. This page can also be access with the navbar Admin button in the top right. Within the Admin Page, admins are able to check checkboxes. Checking a *Pending* grant will *Approved*, checking an *Approved* grant will *Denied* it. Checking a *Denied* grant will *Approved* it. It is important to save the changes by submitting. 
    c. Admins may also comment into the Comments page like any normal User. They are also able to Change their password and their clubname, although for their case, this simply changes their display name when in the Comments tab.

*After receiving an error, the user can simply navigate to another tab using the navbar or simply go back to the previous page*
