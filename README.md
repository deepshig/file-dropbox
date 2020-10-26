# 2020_group_12_s3993914_s4091221_s4199456

## Problem Statement
There is a requirement for a system which allows clients to connect to a pool on a hosted system to upload files and periodically receive async updates after some time. Multiple pools can be running simultaneously that require some Identity and Access Management. A client pool may consist of 2 to thousands of client applications. Each client application performs some task that produces a file that is required by a hosted server. Each client in the pool generates these files asynchronously (some clients may even be listeners and provide no updates) and sends them to our project system through an API for processing, there is a user defined update frequency from minutes to days required. Some clients may not be able to send updates immediately and will cache local updates until a batched update can be sent with multiple timestamps contained.

The file size(s) being sent are 100’s of Kbs to 10’s of Mbs. Although sending updates asynchronously, it is required that batches from similar timestamps are grouped, this can be through the range on the timestamp, or otherwise. A server, external to this system, will request a group's files at a given trigger event. The external server will then perform some operation for roughly 2 minutes. On completion the external server will return to our project system a single file intended to be shared back down to the entire client pool.

## Architecture

![Architecture7](Architecture/Architecture-7.png)

The above image summarizes the architecture followed in the project. The whole system is designed with microservice architecture. Every module is an independent microservice. Different microservices interact with each other via synchronous or ansynchronous mechanisms, as per the need. Let us look at each module in detail.

### Front-end Client

This module is a dummy web client which provides the following features :
* Create a new user
* Login
* Logout
* Upload a new file
* Allow admin to view files for all users

It calls the Authentication Service APIs to create a new user, login and logout.

It connects to the socket gateway to allow the user to upload file, and to allow them to view their previously uploaded files.

### Socket Gateway

It provides an interface for asynchronous communication between front-end client and the backend servers. It exposes following web-socket connection APIs :
* Initiate Connection : `connect`
* Start Uploading a file : `start-transfer`
* File Upload : `write-chunk`
* Completing the Upload : `complete-upload`
* View user history : `get-history`
* Keeping Connection Alive : `alive`

Initiate Connection API allows user to connect to the back-end system. User has to provide their `access_token`. Connection is established only if this `access_token` is valid. If it is not, user has to login and get a new `access_token`.

Start Uploading a file lets the user to select the file to be uploaded. If it is one of the forbidden types, upload is rejected. Else, a unique file_id is created to store this file in a temporary storage. It also records user details and receives file metadata from the user.

File Upload actually uplaods the file against the unique `file_id` created in the previous API. This is the actual movement of the file from client to server.

Completing the upload determines when the file is completely uplaoded. It verifies it against the user details and metadata recorded while starting the upload. If verification proceeds successfully, it internally calls the `File Upload` API of the file uploader service to allow further processing.

View User History internally calls the `View User History` API of the File Service Manager to fetch details about all the files uploaded by the user.

Keeping connection alive provides mechanism for the client to keep the connection alive even if they are not using for its actual feature.

In addition, the gateway also runs a queue consumer in a parallel thread. This consumer consumes messages from the user notification queues and publishes them to the client via the established socket connection. This mechanism is implemented to asynchronously update the user about the status of the file they attempted to upload.

### Authentication Service
This module is reponsible for authorising users to use the whole system. It exposes the following HTTP REST APIs:
* Create new user : `POST /auth/signup`
* Login existing user : `PUT /auth/login/<string:user_name>`
* Logout user : `PUT /auth/logout/<string:user_name>`
* Authenticate user : `GET /auth/validate`

A user entitiy is defined by :
* User ID : System Generated [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)
* User Name : Defined by the user during sign up. Needs to be unique.
* Role : `admin` or `user`

Each user is assigned an `access_token` generated by the system at the time of user creation. This is used to authenticate the user for further requests. A user, immediately after creation is logged in by default.

Access Token is valid for a logged in user. If the user logs out, the access token becomes invalid. User needs to login again to generate a fresh access token in this case.

Access Token information in both the above stated scenarios is shared with the user via [JSON Web Token](https://jwt.io/)

Authentication API checks if the given `access_token` is valid for the given `user_id`. It returns error if the user is not authenticated or not authorised.

User data is maintained in relational form in a PostgreSQL Database.

We do not have password based authentication yet, because this module is not the focus point of the project. A simple to use authentication system is created, but it provides a window for future development into complex authentication mechanism.

### File Uploader Service

This module is responsible for receiving file from the user, validating it, and caching it until it is stored in a permanent storage. It exposes the following HTTP REST APIs:
* Upload File : `POST /file/upload`
* Update File Status : `PUT /file/update/status`

Upload File API recieves the file along with user details and some metadata. It validates the file against `EMPTY_FILE` checks. It generates a `file_id` for this file, and then stores the file, as well as the associated details in cache. It then publishes a queue event with the file details and user details for facilitating its permanenet storage. It also publishes another queue event for the notifying the user (and the admin as well) that file has been successfully cached.

Update File Status API is hit by the File Service Manager to update the status of the file : `uploaded_successfully` or `upload_failed`.

In case of `uploaded_successfully`, file is deleted from the cache, its index is updated with its successfully uplaoded status, and an event is published in the queue to notify the user (and the admin as well) the file has been uploaded successfully.

However, in case of `upload_failed`, an event to the file upload queue is published again for facilitating the retry of upload flow. Index of the file in the cache is updated to have information about the retry. A file is retried for uplaod two times (If counting the original uplaod attempt, we have total 3 attempts for a single file). If upload is still not successful, it deletes the file from the cache. Index of the file is marked as failed to upload, and an event in the user notification queue is published to notify the user of the failure.

We use Redis for in-memory caching requirements, and RabbitMQ for event queueing mechanisms.

### File Service Manager

This module is responsible for storing the cached files in permanent storage, and providing an interface to view and download them.

It consumes the file upload queue events which contain the file details and associated user details. It first tries to fetch the file from the cache, and then uploads it in a permanent storage database. It then creates an index entry for the file in the database. This entry is marked against the user who owns the file. Once all of this is done, it informs the File Uploader service about the status of the file via the `Update File Status` API.

The file index entity stored in MongoDB has the following fields:
* `clientName` : User name provided by user during registration
* `clientId`  : User ID (UUID) generated by authentication service
* `fileName`  : File ID (UUID) generated by file uploader service during caching
* `activity`  : Enum value to specify the file status in the system
* `gridFs_id` : ID of the file in GridFS DB
* `meta_data` : File metadata as provided by user
* `created`   : Timestamp of creation of this entry in DB

Alongside this queue consumer, this module also runs a server instance. It exposes the following HTTP REST API :
* View User History `GET /client/history/<client_id>`
* Download File `GET /file/<filename>`

The View User History API fetches the indexing details of all the files uploaded by the given user.

The Download File API allows user to download their file using the `file_id` generated during upload.

Here, we use GridFS as permanent File Storage and MongoDB for storing the file index information. Caching and queueing mechaninsms are the same as instantiated by File Uploader Service.


## Dependencies

The project uses the following technological stack:

* [Python 3.8](https://docs.python.org/3/whatsnew/3.8.html) : We chose Python as our working language because it provides easy to use and readily available libraries for all the other dependencies, with detailed documentation.
* [React JS Redux State Management](https://react-redux.js.org/) : We use this for developing the web client.
* [Redis](https://redis.io/) : We chose Redis to serve as in-memory cache store for caching file, as well as its associated indexing details.
* [RabbitMQ](https://www.rabbitmq.com/) : We need to have asynchronous communication between file uploader service and file service manager once the file is cached. Also, file uplaoder service needs to notify the socket gateway about file status. We chose event queuing mechanism provided by RabbitmQ for this. We have used management plugin because it provides web UI for monitoring.
* [PostgreSQL](https://www.postgresql.org/docs/12/index.html) : We used PostgreSQL to maintain the user authentication data in authentication service. It is a relational database with indexing over `user_id` and `user_name`. Thus, we chose PostgreSQL.
* [GridFS](https://docs.mongodb.com/manual/core/gridfs/) : We chose this as a permananent storage for our files. It divides the file into chunks, and stores each of them separately. This gives us better scalability when larger files is considered.
* [MongoDB](https://www.mongodb.com/) : MongoDB is used as a file indexing store in File Service Manager. We chose this because it provides an option for high availability.
* [Web Sockets](https://en.wikipedia.org/wiki/WebSocket#:~:text=WebSocket%20is%20a%20computer%20communications,being%20standardized%20by%20the%20W3C.) : We use this for asynchronous communication between backend and web client.
* [Elastic Search](https://www.elastic.co/) : We use this to dump application logs and display them on a Kibana dashboard.
* [Kibana](https://www.elastic.co/kibana) : We use Kibana as a monitoring engine for application logs.
* [Docker](https://www.docker.com/) : In order to maintain the uniformity of deployment, we use docker as deployment engine.
* [Portainer](https://www.portainer.io/) : We provision a portainer dashboard to be able to monitor the health of infrastructure when running the system locally.
* [Kubernetes](https://kubernetes.io/) : We use Kubernetes to deploy the application on [Google Cloud Project](https://cloud.google.com/)

## Running the program

* To run the tests : `cd back_end/tests && py.test -v && cd ../../`
* To run the application locally : `docker-compose up` (Note: in some instance rabbitmq may be delayed in startup: fsm, file_uploader, and socket-gateway may need restarts)
* To run in detached mode : `docker-compose up -d`
* To see the logs of a specific, container, first find the container name by running `docker ps -a`, then run : `docker container logs <container_name>`
* To clean up : `docker-compose down -v --rmi all --remove-orphans`
* We can run separate container by : `docker-compose up <container_name>` where `container_name` is one of the service names from the docker-compose.yml.
* We can access the web-client on http://localhost:3000. Here, we can create a user, login, logout, and upload file.
* While the containers are running, we can monitor the RabbitMQ queue on the dashboard http://localhost:15672/ with `[Username/Password]` as `[guest/guest]`.
* We can view PostgreSQL using Adminer Dashboard on http://localhost:8080/, where we can login with `[System/Server/Username/Password/Database]` as`[PostgreSQl/postgresdb/postgres/postgres/user_auth]`
* We can access the redis on localhost port `6379` using `redis-cli -p 6379`. We can run redis monitor using the command `redis-cli -p 6379 monitor`
* We can access application logs in Kibana using http://localhost:5601/
* We have set up a portainer instance to be able to monitor the high level status of all the containers. We can access the Web UI for the same on http://localhost:10001/ while the portainer container is running. Use `[Username/Password]` as `[admin/admin123]`.

### Kubernetes

* To run the system in kubernetes a node cluster pool of minimum 4 nodes (without replicas) is required `gcloud container node-pools create default-pool --cluster=project --machine-type=n2-standard-2  --num-nodes=4`
* 
* Run the following commands from the `kubernetes/` directory
* An Nginx Ingress instance is required on the cluster `kubectl apply -f .\nginx-deploy.yaml` _Important: Wait until the endpoints have been assigned before continuing_
* Now start the Nginx Load balancer `kubectl apply -f .\nginx-ingress.yaml`
* Note the host IP for the Nginx loadbalancer will need to be configured in `front_end/.env`for new deployments. This change will need to be built and pushed to docker hub. `cd front-end`, `docker build . -f .\Dockerfile.prod -t diarmuidk/wacc:front-end`, `docker push diarmuidk/wacc:front-end`
* Once the previous steps are complete start the following database deployments: logstash, mongodb, postgresdb, rabbitmq, redis using the following command
`kubectl apply -f .\logstash-deployment.yaml,.\logstash-service.yaml,.\mongodb-deployment.yaml,.\mongodb-service.yaml,.\postgresdb-deployment.yaml,.\postgresdb-service.yaml,.\rabbitmq-deployment.yaml,.\rabbitmq-service.yaml,.\redis-deployment.yaml,.\redis-service.yaml`

* Next start the following services: adminer, auth, elastic-search, file-uploader, front-end, fsm, kibana, socket-gateway using:
`kubectl apply -f .\adminer-deployment.yaml,.\adminer-service.yaml,.\auth-deployment.yaml,.\auth-service.yaml,.\elasticsearch-deployment.yaml,.\elasticsearch-service.yaml,.\file-uploader-deployment.yaml,.\file-uploader-service.yaml,.\front-end-deployment.yaml,.\front-end-service.yaml,.\fsm-deployment.yaml,.\fsm-service.yaml,.\kibana-deployment.yaml,.\kibana-service.yaml,.\socket-gateway-deployment.yaml,.\socket-gateway-service.yaml`

