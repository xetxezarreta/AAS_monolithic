# Running Monolithic application using vagrant and docker-compose
* Go to your vagrant basic folder: (e.g.)
```cmd
cd C:\Users\flarrinaga\Dropbox (MGEP)\flarrinaga\ACADEMIA\Master\Infrastructure\PI\resources\basic 
```
* Launch vagrant (basic):
```cmd
vagrant up dev
```
* Connect to vagrant:
```cmd
vagrant ssh dev
```
* Create aas folder and clone repository from GitLab:
```bash
mkdir aas
cd aas
git clone https://gitlab.danz.eus/macc/aas/monolithic.git
cd monolithic
```
* Copy enviroment variables to .env file:
```bash
cp dot_env_example .env
```
* Launch monolithic application using docker-compose:
```bash
docker-compose up
```
## Help on docker commands
* Launch docker-compose:
```bash
docker-compose -f "file" up
```
or (if there is a docker-compose.yml file in the current folder)
```bash
docker-compose up
```
* View running containers:
```bash
docker container ps
```
* Stop docker-compose:
```bash
docker-compose -f "file" down
```
or (if there is a docker-compose.yml file in the current folder)
```bash
docker-compose down
```

# Running application using PyCharm IDE
(*View **Deploy Monolithic PyCharm.pdf** if you need the images.*)

* Create a new *Pure Python* project in PyCharm
  * **WARNING!** Remember to add a name in the location, otherwise *unamed* will be called).
  
* Enable Version Control Integration:
  1. ```VCS > Enable Version Control Integration...```
  1. Select **Git**
  1. OK
* Use the GitLab Monolithic project as the origin repository:
  1. Right click on the project.
  1. ```Git > Respsitory > Remotes...```
  1. Add (+) *https://gitlab.danz.eus/macc/aas/monolithic.git*
* Pull Repository:
  1. Right click on the project.
  1. ```Git > Repository > Pull...```
  1. Select ```origin/master```.
  1. Click on *Pull*.
* If you don't see the code:
  1. Right click on the project.
  1. ```Synchronize 'Project name'```
* Copy environment variables to needed folder:
  1. Right click on ```dot_env_exam``` file.
  1. Paste it inside ```flask_app > monolithic``` and name it as ```.env```.
* Install dependencies:
  1. Go to the terminal (inside PyCharm)
```bash
cd flask_app/monolithic
pip install -r requirements.txt
```
* Run/Debug application:
  1. Right click on ```flask_app > monolithic > app.py```
  1. ```Run 'app'``` or ```Debig 'app'```

# Understanding this repository
## Docker files
* **```docker-compose.yml```**: indicates the images/containers the application has, which port to use...
* **```dot_env_example```**: it has to be copied (and renamed to *.env*) to the needed path for the application to know
enviroment variables
* **```flask_app > Dockerfile```**: it has the docker commands to create the image with our Flask application and needed
Dependencies. I also defines that when the container is run, ```gunicorn``` has to be executed.

## Monolithic (```flask_app > monolithic```)
* **```app.py```**: the main function that will initiate the Flask application.
* **```requirements.txt```**: The dependencies that are needed to execute the application. 
The Dockerfile will execute ```pip install requirements.txt``` to install them when we build the image.

## Application (```flask_app > monolithic > application```)
* **```__init__.py```**: app.py will invoke this to create the flask app and the database.
* **```config.py```**: the object that will load environment variables (database options).
* **```machine.py```**: This is the thread that will simulate the manufacturing of the pieces by the machine.
It includes functions to manage pieces and a queue of pieces to manufacture.
* **```models.py```**: this file contains the mapping between Python Objects and database tables.
* **```routes.py```**: this file contains the REST API definition for the application (GET, POST, DELETE...)

# REST API Methods
We recommend to install an application to test the REST APIs. e.g.:
* [Postman](https://www.getpostman.com/) (Free, you can program environment variables)
* [Insomnia](https://insomnia.rest/) (Free and OpenSource + PRO Version)
* [SOAP UI](https://www.soapui.org/) (Free and OpenSource + PRO Version)

The following methods can be extracted from ```flask_app > monolithic > application > router.py``` annotations.

For the examples we will imagine that the IP of the vagrant machine is 10.100.199.200.
If you execute the app in your IDE, the host will be *localhost*.

## Create an order [POST]
* URL: *http://10.100.199.200:13000/order*
* Body:
```json
{
  "description": "New order created from REST API",
  "number_of_pieces": 5
}
```
## View an Order [GET]:
You can get the ID when you create the order.
* URL: *http://10.100.199.200:13000/order/{id}*
## Remove an Order [DELETE]:
You can get the ID when you create the order.
* URL: *http://10.100.199.200:13000/order/{id}*

The order will be deleted and the unmanufactured pices will be removed from the machine queue.
All the unmanufactured pieces of the order will appear as *"Cancelled"* and the orderid will be *null*.

## View all Orders [GET]:
* URL: *http://10.100.199.200:13000/order* or *http://10.100.199.200:13000/orders*
## View Machine Status [GET]:
You can see the queue, the status of the machine and the piece that is being manufactured.
* URL: *http://10.100.199.200:13000/machine/status*
## View a Piece [GET]:
You can get the ID when you create the order.
* URL: *http://10.100.199.200:13000/piece/{id}*

## View all Pieces [GET]:
* URL: *http://10.100.199.200:13000/piece* or *http://10.100.199.200:13000/pieces*

