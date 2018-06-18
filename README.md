# [![GeoLoRacja](https://image.ibb.co/g2e2jc/logo_small.png)](https://github.com/KG5321/geoloracja_server) GeoLoRacja Server

Server created for team project called "GeoLoRacja"

## Frameworks:

- Flask
- Bootstrap
- SQLAlchemy

## Database:

- PostrgreSQL

## Authors

- **Dominik Hofman**
- **Konrad Gebler**

## Instalation

###### Step 1 - Installing all needed packages.

To install all packages, run:

`$ pip install -r requirements.txt`

###### Step 2 - Training classifier.

Go to folder `machine_learning` by typing `$ cd machine_learning` then run:

`$ python train.py`

###### Step 3 - Installing PostrgreSQL and configuring database.

1. Install PostrgreSQL for Your operating system, You can download it from this link:

 [Download PostrgreSQL](https://www.postgresql.org/download/)

2. Create user:

 `$ sudo -u postgres createuser loradb`

3. Create database:

 `$ sudo -u postgres createdb loradb`

4. Give new created user a password:

 ```
 $ sudo -u postgres psql
 psql=# alter user loradb with encrypted password 'GeoLoracja2018!';
 ```

5. Grant privileges on database:

 `psql=# grant all privileges on database loradb to loradb;`

###### Step 4 - Initialize database.
In project folder start python console by typing:

`$ python`

In python console run:

`>>> from server import db`

Next create all tables by typing:

`>>> db.create_all()`

Exit python console:

`>>> exit()`

## Usage

After finishing all steps in Installation, in project folder run command:

`$ python server.py`

If everything was properly configured You should see this:

```
Starting Lora thread
Uplink listener is running...
 * Running on http://0.0.0.0:5000/
```

Now You can start browser and go to:

`https://localhost:5000`

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
