# Django Project Management API

This is a web API designed to manage projects, assign user roles, and enable collaboration through comments. It supports **creating, updating, and deleting projects** while ensuring **role-based access control**.

## **Setting up the project**

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/dunfred/pma-assessment.git
$ cd pma-assessment
```

### **1️⃣ Create a `.env` file**
Before running the project, create a `.env` file in the **project directory** (where `manage.py` is located) and add the following:

```ini
SECRET_KEY='random_secret_goes_here'
DEBUG=1
ALLOWED_HOSTS='*'
```

If you plan to use **AWS S3 for static files**, you can also add these:

```ini
AWS_ACCESS_KEY_ID=''
AWS_SECRET_ACCESS_KEY=''
AWS_STORAGE_BUCKET_NAME=''
AWS_STORAGE_REGION=''
AWS_DEFAULT_ACL=''
```

---

### **2️⃣ Create & Activate Virtual Environment**
This project uses **`virtualenv`** and requires **Python 3.12.9**.  

```sh
# If you don't have virtualenv installed, install it first
$ pip install virtualenv

# Create a virtual environment using Python 3.12
$ virtualenv -p python3.12 pma-env

# Activate the virtual environment
$ source pma-env/bin/activate  # On Windows: env\Scripts\activate
```

Then install the dependencies:

```sh
(pma-env)$ pip install -r requirements.txt
```

---

### **3️⃣ Apply Migrations & Create a Superuser**
By default, the project uses **SQLite3** as the database. Run migrations:

```sh
(pma-env)$ python manage.py migrate
```

Then, **create an admin (superuser) account** so you can manage everything:

```sh
(pma-env)$ python manage.py createsuperuser
```

Follow the prompts to enter an **email, username, and password** for the admin account.

---

### **4️⃣ Start Server & Access the Admin Panel**
Run the server:

```sh
(pma-env)$ python manage.py runserver
```

- **Django Admin Panel:** `http://127.0.0.1:8000/backroom/`  
  Here, you can **manage users, projects, and roles** through an easy-to-use UI.  

---

### **5️⃣ Using AWS S3 for Static Files (Optional)**
If you have **valid AWS S3 credentials** in your `.env` file, you can collect static files by running:

```sh
(pma-env)$ python manage.py collectstatic
```

Make sure your **AWS IAM user** has the necessary permissions for **S3 access** before running this.

---

## **Running Tests**

Run the test suite with:

```sh
(pma-env)$ pytest
```

After the tests finish, you can check the **coverage report**:

```sh
(pma-env)$ open htmlcov/index.html  # On Windows: start htmlcov\index.html
```

This will display **test coverage** in an interactive format.

---

## **API Documentation**

The API is fully documented. Start the server and visit to check the various endpoints available:

- **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://127.0.0.1:8000/api/schema/redoc/`

---
### Author
- [Fred Dunyo](https://github.com/dunfred)

---