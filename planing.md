## ER Models:
#### User:
- Id(Int)(Primary Key)
- Name(String)(Required-Length(10))
- Email(String)(Required-Unique)
- Password(String)(Required)
- ProfilePicture(Bool)
- IpAddress(String)
- created_at(DateTime)
- updated_at(DateTime)

#### Role:
- Id(Int)(Primary Key)
- IsSuperAdmin(Bool)
- IsAdmin(Bool)

#### Stats:
- Id(Int)(Primary Key)
- Length(Int)
- Prompt(Int)
- LastAt(DateTime)

#### Discussion(Name,Type,Constains):
- Id(Int)(Incremental-Unique)
- Prompt(String)(Required,Length(500))
- Response(String)()
- last_at(DateTime)

#### Feedback
- Id(Int)(Incremental-Unique)
- opinion(String(300))
- sent_at(DateTime)

#### Relationships
- Each User has Discussion (One-To-One)
- Each User has multiple Feedback (One-To-Many)

----------------------------------
## Forms
#### Signup:
- Username(Length(5,10))
- Email
- Password(Length(8,30))
- confirm_password(equalto password)
- reCAPTCHA

### Login:
- Email
- Password
- reCAPTCHA

### Logout:
-     

### Feedback:
- opinion(Length(10,100))

### ModifyPicture:
- picture
        
### ModifyUsername:
- username(Length(5,10))
- password
    
### ModifyPassword:
- password
- new_password(Length(8,30))
- confirm_password(equalto password)

-------------------------------------
## DataLayer(Pipeline)
### Validations:
#### Signup:
- username.lower() should not exist in db
- email.lower() should not exist in db

#### Login:
- email.lower() should exist in db
- password should match password linked to this email in the db

#### Logout:
-  

#### Feedback:
-

#### ModifyPicture:
- picture's dims: (200 >= Height >= 180 and 200 >= Width >= 180)
- resize picture to (200,200)
- password should match password of existing user

#### ModifyUsername:
- password should match password of existing user

#### ModifyPassword:
- password should match password of existing user

---------------------------------------
## Routes Access
####  Index
        
#### Signup 

#### Login 
- only non loggedin users
    
#### Logout
- only loggedin users(redirect to login page)

#### Feedback
- only loggedin users(redirect to login page)

#### Profile
- only loggedin users(redirect to login page)