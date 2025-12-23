# Task Management System – Development Assessment

## 🚀 How to Run

### ✅ Prerequisites
- **Node.js** v14 or higher  
- **Python** 3.12+  
- **PostgreSQL** running locally
  

## 🔧 Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd server

2. python3 -m venv fastenv
3. . source venv/bin/activate
4. pip install -r requirements.txt
5. Create a .env file in the backend directory with the following content:

 SECRET_KEY=secret_key 

ALGORITHM=HS256 

ACCESS_TOKEN_EXPIRE_MINUTES=30 

SQLALCHEMY_DATABASE_URL=postgresql://username:password@localhost:5432/database_name 

7.  start the fastapi server
  
 uvicorn app.main:app --reload

 
   ## Frontend Setup 

  1. cd client
  2. npm install 
  3. npm run dev


